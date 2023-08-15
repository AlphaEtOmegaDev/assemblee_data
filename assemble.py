# importing required modules
import json
from enum import Enum
import os
from os import listdir
from os.path import isfile, join
import pickle


class VoteType(Enum):
    POUR = 1
    CONTRE = 2
    ABSTENTION = 3

GP_CONST = {
                "PO800496": "Socialistes et apparentés - NUPES (SOC)",
                "PO793087": "Non Inscrit (NI)",
                "PO800508": "Les Républicains (LR)",
                "PO800538": "Renaissance (REN)",
                "PO800532": "Libertés, Indépendants, Outre-mer et Territoires (LIOT)",
                "PO800514": "Horizons et apparentés (HOR)",
                "PO800502": "Gauche Démocrate et Républicaine - NUPES (GDR)",
                "PO800484": "Démocrate (MODEM)",
                "PO800526": "Écologiste - NUPES (ECO)",
                "PO800490": "La France Insoumise - NUPES (LFI)",
                "PO800520": "Rassemblement National (RN)"
            }
#
# "PA..." : [pours,absentions,contres]
#
acteurs = {}

def acteursExist(acteurID):
    acteur = acteurs.get(acteurID)
    if acteurs.get(acteurID) == None:
        acteurs.update({acteurID: {"pours": 0, "abstentions": 0, "contres": 0}})
        acteur = acteurs.get(acteurID)
    return acteur

# Permet d'ajouter un vote pour un député
def append(acteurID, voteType):
    acteur = acteursExist(acteurID)
    if voteType is VoteType.POUR:
        acteur.update({"pours": acteur.get("pours")+1})
    if voteType is VoteType.ABSTENTION:
        acteur.update({"abstentions": acteur.get("abstentions")+1})
    if voteType is VoteType.CONTRE:
        acteur.update({"contres": acteur.get("contres")+1})

# Récupère les votes des députés.
def compute(data1,voteType,dataList):
    if isinstance(data1['votant'],list):
        for j in data1['votant'] :
            append(j['acteurRef'],voteType)
            dataList.append(j['acteurRef'])
    else:
        append(data1['votant']['acteurRef'],voteType)
        dataList.append(data1['votant']['acteurRef'])
        
# ON récupère l'identité d'un député
def getActeurName(name):
    file = open("acteurs/"+name+".json", "r")
    d = json.load(file)
    return d['acteur']['etatCivil']['ident']['nom'],d['acteur']['etatCivil']['ident']['prenom']


def listToName(datalist):
    nameList = []
    for id in datalist:
        nom,prenom = getActeurName(id)
        nameList.append(nom + " " + prenom)
    return nameList

def dictToName(dataDict):
    nameDict = {}
    for id in dataDict:
        nom,prenom = getActeurName(id)
        nameDict[nom + " " + prenom] = dataDict.get(id)
    return nameDict


# On lance le calcul des data
def computeFile(name):
    f_json = open(name, "r")
    data = json.load(f_json)
    data = data['scrutin']['ventilationVotes']['organe']['groupes']['groupe'] # on est au max là
    
    pours = []
    contres = []
    abstentions = []
    groupes = {}
        
    for i in data:
        votes = i['vote']['decompteNominatif']['pours']
        if i['vote']['decompteNominatif']['pours'] != None:
            compute(i['vote']['decompteNominatif']['pours'],VoteType.POUR,pours)
        if i['vote']['decompteNominatif']['abstentions'] != None:
            compute(i['vote']['decompteNominatif']['abstentions'],VoteType.ABSTENTION,abstentions)
        if i['vote']['decompteNominatif']['contres'] != None:
            compute(i['vote']['decompteNominatif']['contres'],VoteType.CONTRE,contres)

    data = {"pours":pours, "contres":contres, "abstentions":abstentions}
    analysePath = 'analyses/vote/f/' if name.split("/")[1] == "faveurMajorite"  else 'analyses/vote/c/'

    os.makedirs(analysePath + name.split("/")[2].split(".")[0] +'/', exist_ok=True)
    with open(analysePath + name.split("/")[2].split(".")[0] +'/scrutins.dat', 'wb') as f:
        pickle.dump(data, f)

    f_json.close()
    
def main():
    faveur = [("resultat/faveurMajorite/"+f) for f in listdir("resultat/faveurMajorite/") if isfile(join("resultat/faveurMajorite/", f))]
    faveur.extend([("resultat/contreMajorite/"+f) for f in listdir("resultat/contreMajorite/") if isfile(join("resultat/contreMajorite/", f))])
    
    for f in faveur:
        computeFile(f)
    
    with open('analyses/acteurs.dat', 'wb') as f:
        pickle.dump(acteurs, f)
    with open('analyses/acteurs_revealed.dat', 'wb') as f:
        pickle.dump(dictToName(acteurs), f)
main()

# Permet de déserialiser les fichiers DAT
def deserialize(name):
    with open(name, 'rb') as f:
        data = pickle.load(f)
        print((data, type(data)))

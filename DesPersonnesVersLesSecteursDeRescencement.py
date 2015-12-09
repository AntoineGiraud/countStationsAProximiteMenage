import lib.toolbox as toolbox
import time
import csv
import math
import os
import json
import copy
from collections import OrderedDict


def parseValue(mapping, field, value):
    try:
        fieldMapping = mapping[field]
        if fieldMapping == "int":
            return int(value)
        elif fieldMapping == "float":
            return float(value)
        elif fieldMapping == "json":
            return json.loads(value)
        else:
            return value
    except Exception:
        return value


def loadFile(fileName, nbLignes, idPrincipale, mapping, separator):
    tStart = time.clock()
    stops = {}
    labels = []

    isGtfsStm = 'stm' in fileName or 'STM' in fileName or 'Stm' in fileName

    i = -1
    for line in open(fileName, encoding="utf8"):  # , encoding="utf8"
        ligne = line.replace("\n", "").split(separator)
        # name;lon;lat;coordsLatLon;capacity;region
        if i < 0:
            labels = ligne
            i += 1
            continue
        elif i >= 2000000:
            break  # On veut que 500 tapIn mais ... on ne veut pas couper les tap in d'une carte !

        ligneJson = OrderedDict()
        j = 0
        try:
            for field in labels:
                ligneJson[field] = parseValue(mapping, field, ligne[j])
                j += 1
        except Exception:
            print(labels)
            print(ligne)

        stops[ligneJson[idPrincipale]] = ligneJson

        toolbox.progressBar(i, nbLignes)
        i += 1

    toolbox.hideProgressBar()
    print(i+1, "entrées lues en", toolbox.tempsCalulString(tStart), "pour", fileName)

    return stops, labels


def getSridu(sridu, sridus):
    SR = sridu + ".00" if len(sridu) == 7 else sridu
    try:
        return sridus[SR]
    except Exception:
        avg = {'sommePonderee': 0, 'quotient': 0}
        sriduRetour = OrderedDict([
            ('SRIDU', SR),
            ('1kmCountBIXIstops', copy.copy(avg)),
            ('500mCountBIXIstops', copy.copy(avg)),
            ('1kmCountBIXIcapacity', copy.copy(avg)),
            ('500mCountBIXIcapacity', copy.copy(avg)),
            ('1kmCountAMTstops', copy.copy(avg)),
            ('500mCountAMTstops', copy.copy(avg)),
            ('1kmCountAMTcountStopTimes', copy.copy(avg)),
            ('500mCountAMTcountStopTimes', copy.copy(avg)),
            ('1kmCountSTMstops', copy.copy(avg)),
            ('500mCountSTMstops', copy.copy(avg)),
            ('1kmCountSTMcountStopTimes', copy.copy(avg)),
            ('500mCountSTMcountStopTimes', copy.copy(avg)),
            ('1kmCountSTMcountStopTimesSemaine', copy.copy(avg)),
            ('500mCountSTMcountStopTimesSemaine', copy.copy(avg)),
            ('1kmCountSTMcountStopTimesSamedi', copy.copy(avg)),
            ('500mCountSTMcountStopTimesSamedi', copy.copy(avg)),
            ('1kmCountSTMcountStopTimesDimanche', copy.copy(avg)),
            ('500mCountSTMcountStopTimesDimanche', copy.copy(avg)),
            # ('nbPersLogi', copy.copy(avg)),
            ('age', copy.copy(avg)),
            ('permis', copy.copy(avg)),
            ('pop', 0),
            ('hommes', 0),
            ('femmes', 0),
            ('statut_1', 0),
            ('statut_2', 0),
            ('statut_3', 0),
            ('statut_4', 0),
            ('statut_5', 0),
            ('statut_6', 0),
            ('statut_7', 0),
            ('statut_8', 0)
        ])
        sridus[SR] = sriduRetour
        return sriduRetour


def updateAvg(value, facteur, avgObject):
    avgObject['sommePonderee'] += value * facteur
    avgObject['quotient'] += facteur


def aggregateTowardsSridu(menages, personnes, nbLignes):
    tStart = time.clock()
    sridus = {}
    sridu_labels = list(getSridu('sridu', sridus).keys())
    sridus = {}

    i = 0
    for pers in personnes.values():
        factPers = pers['facteurPersonne']
        menage = menages[pers['idFeuillet']]
        sridu = getSridu(pers['SRIDU'], sridus)
        if not sridu['SRIDU']:
            print(pers)

        updateAvg(menage['1kmCountBIXIstops'], factPers, sridu['1kmCountBIXIstops'])
        updateAvg(menage['500mCountBIXIstops'], factPers, sridu['500mCountBIXIstops'])
        updateAvg(menage['1kmCountBIXIcapacity'], factPers, sridu['1kmCountBIXIcapacity'])
        updateAvg(menage['500mCountBIXIcapacity'], factPers, sridu['500mCountBIXIcapacity'])
        updateAvg(menage['1kmCountAMTstops'], factPers, sridu['1kmCountAMTstops'])
        updateAvg(menage['500mCountAMTstops'], factPers, sridu['500mCountAMTstops'])
        updateAvg(menage['1kmCountAMTcountStopTimes'], factPers, sridu['1kmCountAMTcountStopTimes'])
        updateAvg(menage['500mCountAMTcountStopTimes'], factPers, sridu['500mCountAMTcountStopTimes'])
        updateAvg(menage['1kmCountSTMstops'], factPers, sridu['1kmCountSTMstops'])
        updateAvg(menage['500mCountSTMstops'], factPers, sridu['500mCountSTMstops'])
        updateAvg(menage['1kmCountSTMcountStopTimes'], factPers, sridu['1kmCountSTMcountStopTimes'])
        updateAvg(menage['500mCountSTMcountStopTimes'], factPers, sridu['500mCountSTMcountStopTimes'])
        updateAvg(menage['1kmCountSTMcountStopTimesSemaine'], factPers, sridu['1kmCountSTMcountStopTimesSemaine'])
        updateAvg(menage['500mCountSTMcountStopTimesSemaine'], factPers, sridu['500mCountSTMcountStopTimesSemaine'])
        updateAvg(menage['1kmCountSTMcountStopTimesSamedi'], factPers, sridu['1kmCountSTMcountStopTimesSamedi'])
        updateAvg(menage['500mCountSTMcountStopTimesSamedi'], factPers, sridu['500mCountSTMcountStopTimesSamedi'])
        updateAvg(menage['1kmCountSTMcountStopTimesDimanche'], factPers, sridu['1kmCountSTMcountStopTimesDimanche'])
        updateAvg(menage['500mCountSTMcountStopTimesDimanche'], factPers, sridu['500mCountSTMcountStopTimesDimanche'])
        updateAvg(pers['age'], factPers, sridu['age'])
        valPermis = pers['permis'] if pers['permis'] <= 2 else 1
        updateAvg(valPermis-1, factPers, sridu['permis'])
        sridu['pop'] += factPers
        if pers['sexe'] == 1:
            sridu['hommes'] += factPers
        elif pers['sexe'] == 2:
            sridu['femmes'] += factPers
        statutTitle = 'statut_'+str(pers['statut'])
        sridu[statutTitle] += factPers

        toolbox.progressBar(i, nbLignes)
        i += 1

    for sridu in sridus.values():
        sridu['1kmCountBIXIstops'] = round(sridu['1kmCountBIXIstops']['sommePonderee'] / sridu['1kmCountBIXIstops']['quotient'], 1)
        sridu['500mCountBIXIstops'] = round(sridu['500mCountBIXIstops']['sommePonderee'] / sridu['500mCountBIXIstops']['quotient'], 1)
        sridu['1kmCountBIXIcapacity'] = round(sridu['1kmCountBIXIcapacity']['sommePonderee'] / sridu['1kmCountBIXIcapacity']['quotient'], 1)
        sridu['500mCountBIXIcapacity'] = round(sridu['500mCountBIXIcapacity']['sommePonderee'] / sridu['500mCountBIXIcapacity']['quotient'], 1)
        sridu['1kmCountAMTstops'] = round(sridu['1kmCountAMTstops']['sommePonderee'] / sridu['1kmCountAMTstops']['quotient'], 1)
        sridu['500mCountAMTstops'] = round(sridu['500mCountAMTstops']['sommePonderee'] / sridu['500mCountAMTstops']['quotient'], 1)
        sridu['1kmCountAMTcountStopTimes'] = round(sridu['1kmCountAMTcountStopTimes']['sommePonderee'] / sridu['1kmCountAMTcountStopTimes']['quotient'], 1)
        sridu['500mCountAMTcountStopTimes'] = round(sridu['500mCountAMTcountStopTimes']['sommePonderee'] / sridu['500mCountAMTcountStopTimes']['quotient'], 1)
        sridu['1kmCountSTMstops'] = round(sridu['1kmCountSTMstops']['sommePonderee'] / sridu['1kmCountSTMstops']['quotient'], 1)
        sridu['500mCountSTMstops'] = round(sridu['500mCountSTMstops']['sommePonderee'] / sridu['500mCountSTMstops']['quotient'], 1)
        sridu['1kmCountSTMcountStopTimes'] = round(sridu['1kmCountSTMcountStopTimes']['sommePonderee'] / sridu['1kmCountSTMcountStopTimes']['quotient'], 1)
        sridu['500mCountSTMcountStopTimes'] = round(sridu['500mCountSTMcountStopTimes']['sommePonderee'] / sridu['500mCountSTMcountStopTimes']['quotient'], 1)
        sridu['1kmCountSTMcountStopTimesSemaine'] = round(sridu['1kmCountSTMcountStopTimesSemaine']['sommePonderee'] / sridu['1kmCountSTMcountStopTimesSemaine']['quotient'], 1)
        sridu['500mCountSTMcountStopTimesSemaine'] = round(sridu['500mCountSTMcountStopTimesSemaine']['sommePonderee'] / sridu['500mCountSTMcountStopTimesSemaine']['quotient'], 1)
        sridu['1kmCountSTMcountStopTimesSamedi'] = round(sridu['1kmCountSTMcountStopTimesSamedi']['sommePonderee'] / sridu['1kmCountSTMcountStopTimesSamedi']['quotient'], 1)
        sridu['500mCountSTMcountStopTimesSamedi'] = round(sridu['500mCountSTMcountStopTimesSamedi']['sommePonderee'] / sridu['500mCountSTMcountStopTimesSamedi']['quotient'], 1)
        sridu['1kmCountSTMcountStopTimesDimanche'] = round(sridu['1kmCountSTMcountStopTimesDimanche']['sommePonderee'] / sridu['1kmCountSTMcountStopTimesDimanche']['quotient'], 1)
        sridu['500mCountSTMcountStopTimesDimanche'] = round(sridu['500mCountSTMcountStopTimesDimanche']['sommePonderee'] / sridu['500mCountSTMcountStopTimesDimanche']['quotient'], 1)
        sridu['age'] = round(sridu['age']['sommePonderee'] / sridu['age']['quotient'], 1)
        sridu['permis'] = round(sridu['permis']['sommePonderee'] / sridu['permis']['quotient'], 3)

    toolbox.hideProgressBar()
    print(len(personnes), 'personnes affectés aux', len(sridus), "Secteurs de Rescencement en", toolbox.tempsCalulString(tStart), "s")

    return sridus, sridu_labels

print("----- Lecture des fichiers ménages & personnes ------")
mapping = {
    'mtmx': 'float',
    'mtmy': 'float',
    'lat': 'float',
    'lng': 'float',
    'popLogi': 'int',
    'facteurLogement': 'float',
    'popPonderee': 'float',
    'countStopTimes': 'int',
    'countStopTimesSemaine': 'int',
    'countStopTimesSamedi': 'int',
    'countStopTimesDimanche': 'int',
    'capacity': 'int',
    '1kmCountBIXIstops': 'int',
    '500mCountBIXIstops': 'int',
    '1kmCountBIXIcapacity': 'int',
    '500mCountBIXIcapacity': 'int',
    '1kmCountAMTstops': 'int',
    '500mCountAMTstops': 'int',
    '1kmCountAMTcountStopTimes': 'int',
    '500mCountAMTcountStopTimes': 'int',
    '1kmCountSTMstops': 'int',
    '500mCountSTMstops': 'int',
    '1kmCountSTMcountStopTimes': 'int',
    '500mCountSTMcountStopTimes': 'int',
    '1kmCountSTMcountStopTimesSemaine': 'int',
    '500mCountSTMcountStopTimesSemaine': 'int',
    '1kmCountSTMcountStopTimesSamedi': 'int',
    '500mCountSTMcountStopTimesSamedi': 'int',
    '1kmCountSTMcountStopTimesDimanche': 'int',
    '500mCountSTMcountStopTimesDimanche': 'int',
    'nbPersLogi': 'int',
    'facteurPersonne': 'float',
    'facteurLogement': 'float',
    'age': 'int',
    'permis': 'int',
    'statut': 'int',
    'sexe': 'int'
}

menages, menages_label = loadFile('input/menages_withCountStopTimes.csv', 17749, 'idFeuillet', mapping, ';')
personnes, personnes_label = loadFile('input/personnes_OD2008.csv', 37576, 'idPersonne', mapping, ';')

print("----- aggrégation vers les SRIDU ------")

sridus, sridu_label = aggregateTowardsSridu(menages, personnes, 37576)

with open('output/sridus.csv', 'w', newline='') as csvfile:
    outputFile = csv.writer(csvfile, delimiter=';', quotechar='"', quoting=csv.QUOTE_MINIMAL)
    outputFile.writerow(sridu_label)
    for row in sridus.values():
        outputFile.writerow(list(row.values()))

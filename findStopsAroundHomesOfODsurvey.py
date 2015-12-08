import lib.toolbox as toolbox
import time
import csv
import math
import os
import json
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


def loadFile(fileName, nbLignes, idPrincipale, mapping):
    tStart = time.clock()
    stops = {}
    labels = []

    isGtfsStm = 'stm' in fileName or 'STM' in fileName or 'Stm' in fileName

    i = -1
    for line in open(fileName, encoding="utf8"):  # , encoding="utf8"
        ligne = line.replace("\n", "").split(",")
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


def getDistance(ptA, ptB):
    return math.sqrt(math.pow(ptB[0]-ptA[0], 2) + math.pow(ptB[1]-ptA[1], 2))


def countStopTimesPerStop(menages, menages_label, nbLignes, stopsToCheck, name, newCounter):
    tStart = time.clock()
    menages_label.append('1kmCount'+name+'stops')
    menages_label.append('500mCount'+name+'stops')
    for c in newCounter:
        menages_label.append('1kmCount'+name+c)
        menages_label.append('500mCount'+name+c)

    i = 0
    for menage in menages.values():
        menage['1kmCount'+name+'stops'] = 0
        menage['500mCount'+name+'stops'] = 0
        for c in newCounter:
            menage['1kmCount'+name+c] = 0
            menage['500mCount'+name+c] = 0
        ptA = [menage['mtmx'], menage['mtmy']]
        for stop in stopsToCheck.values():
            ptB = [stop['mtmx'], stop['mtmy']]
            distance = getDistance(ptA, ptB)
            if distance < 500:
                menage['500mCount'+name+'stops'] += 1
                for c in newCounter:
                    menage['500mCount'+name+c] += stop[c]
            if distance < 1000:
                menage['1kmCount'+name+'stops'] += 1
                for c in newCounter:
                    menage['1kmCount'+name+c] += stop[c]

        toolbox.progressBar(i, nbLignes)
        i += 1

    toolbox.hideProgressBar()
    print(len(stopsToCheck), 'stops affectés aux', i, "ménages en", toolbox.tempsCalulString(tStart), "pour les stops", name)

print("----- Lecture des fichiers stops consolidés & ménages ------")
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
    'capacity': 'int'
}
stopsAMT, stopsAMT_label = loadFile('input/stationsAmtSous1kmMenagesOD08_mtm8_wgs64_avecSRIDU.csv', 123, 'stop_id', mapping)
stopsBixi, stopsBixi_label = loadFile('input/stationsBixi_mtm8_wgs64_avecSRIDU.csv', 463, 'stop_id', mapping)
stopsSTM, stopsSTM_label = loadFile('input/stationsStmSous1kmMenagesOD08_mtm8_wgs64_avecSRIDU.csv', 8995, 'stop_id', mapping)

menages, menages_label = loadFile('input/menages_OD08_mtm8_pop_wgs64_mtm8.csv', 17749, 'idFeuillet', mapping)

print("----- Comptage stops autour des ménages ------")

countStopTimesPerStop(menages, menages_label, 17749, stopsBixi, 'BIXI', ['capacity'])
countStopTimesPerStop(menages, menages_label, 17749, stopsAMT, 'AMT', ['countStopTimes'])
countStopTimesPerStop(menages, menages_label, 17749, stopsSTM, 'STM', ['countStopTimes', 'countStopTimesSemaine', 'countStopTimesSamedi', 'countStopTimesDimanche'])

with open('output/menages_withCountStopTimes.csv', 'w', newline='') as csvfile:
    outputFile = csv.writer(csvfile, delimiter=';', quotechar='"', quoting=csv.QUOTE_MINIMAL)
    outputFile.writerow(menages_label)
    for row in menages.values():
        outputFile.writerow(list(row.values()))

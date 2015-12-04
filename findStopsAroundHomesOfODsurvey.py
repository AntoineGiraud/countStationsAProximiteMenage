import lib.toolbox as toolbox
import time
import csv
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


def countStopTimesPerStop(fileName, nbLignes, idPrincipale, mapping, stops):
    tStart = time.clock()
    labels = []

    stopIdPos = 3
    tripIdPos = 0
    isGtfsStm = 'stm' in fileName or 'STM' in fileName or 'Stm' in fileName

    i = -1
    for line in open(fileName, encoding="utf8"):  # , encoding="utf8"
        ligne = line.replace("\n", "").split(",")
        # name;lon;lat;coordsLatLon;capacity;region
        if i < 0:
            labels = ligne
            stopIdPos = labels.index(idPrincipale)
            tripIdPos = labels.index('trip_id')
            i += 1
            continue
        elif i >= 20000000:
            break  # On veut que 500 tapIn mais ... on ne veut pas couper les tap in d'une carte !

        try:
            stops[ligne[stopIdPos]]['countStopTimes'] += 1
            if isGtfsStm:
                tripId = ligne[tripIdPos]
                if '_S_' in tripId:
                    stops[ligne[stopIdPos]]['countStopTimesSemaine'] += 1
                elif '_A_' in tripId:
                    stops[ligne[stopIdPos]]['countStopTimesSamedi'] += 1
                elif '_I_' in tripId:
                    stops[ligne[stopIdPos]]['countStopTimesDimanche'] += 1
        except Exception:
            print(ligne[stopIdPos], 'inconu dans les stops du GTFS O.o,', stopIdPos)

        toolbox.progressBar(i, nbLignes)
        i += 1

    toolbox.hideProgressBar()
    print(i, "stopTimes lus en", toolbox.tempsCalulString(tStart), "et affectés aux stops pour", fileName)

print("----- Lecture des fichiers stops & stops_time AMT ------")
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
stopsAMT = loadFile('input/stationsAmtSous1kmMenagesOD08_mtm8_wgs64_avecSRIDU.csv', 123, 'stop_id', mapping)
stopsBixi = loadFile('input/stationsBixi_mtm8_wgs64_avecSRIDU.csv', 463, 'stop_id', mapping)
stopsSTM = loadFile('input/stationsStmSous1kmMenagesOD08_mtm8_wgs64_avecSRIDU.csv', 8995, 'stop_id', mapping)

menages = loadFile('input/menages_OD08_mtm8_pop_wgs64_mtm8.csv', 17749, 'idFeuillet', mapping)

# print("----- Lecture des fichiers stops & stops_time STM ------")

# countStopTimesPerStop('input/GTFS/stop_times_stm.txt', 5136728, {}, stopsSTM)

# with open('output/stops_stm_withCountStopTimes.csv', 'w', newline='') as csvfile:
#     outputFile = csv.writer(csvfile, delimiter=';', quotechar='"', quoting=csv.QUOTE_MINIMAL)
#     outputFile.writerow(labelsAMT)
#     for id, row in stopsSTM.items():
#         outputFile.writerow(list(row.values()))

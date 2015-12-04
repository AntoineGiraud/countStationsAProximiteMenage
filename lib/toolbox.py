from math import *
import sys
import time
import datetime


def tempsCalul(startTime):
    ''' @return float: temps passé entre startTime et maintenant '''
    return time.clock() - startTime


def tempsCalulString(startTime):
    ''' @return String: temps passé entre startTime et maintenant, formaté en: {0:.5f}s'''
    return '{0:.5f}s'.format(time.clock() - startTime)


def export(data, path="output/export-" + datetime.datetime.now().isoformat('_') + ".txt"):
    ''' Exporter n'importe quel tableau vers un ficher donné:

    On fait pour chaque ligne du tableau un : print (row, file = fw2)

    '''
    fw2 = open(path, "w")
    for row in data:
        print(row, file=fw2)


def progressBar(curPos, totalToDo, tailleProgressBar=20):
    step = 1
    if len(str(totalToDo)) > 2:
        step = 10**(len(str(totalToDo))-3)
    if curPos % step == 0:
        percent = float(curPos) / totalToDo
        hashes = '#' * int(round(percent * tailleProgressBar))
        spaces = ' ' * (tailleProgressBar - len(hashes))
        sys.stdout.write("\rProgression: [{0}] {1}%".format(hashes + spaces, int(round(percent * 100))))
        sys.stdout.flush()


def hideProgressBar():
    sys.stdout.write('\r')
    sys.stdout.flush()


def baseEncode(number, newBase):
    """Converts an integer to a given base string."""

    alphabet = '0123456789abcdefghijklmnopqrstuvwxyz'
    if not isinstance(number, (int)):
        raise TypeError('number must be an integer')

    output = ''
    sign = ''

    if number < 0:
        sign = '-'
        number = -number

    if 0 <= number < newBase:
        return sign + alphabet[number]

    while number != 0:
        number, i = divmod(number, newBase)
        output = alphabet[i] + output

    return sign + output


def base36encode(number):
    return baseEncode(number, 36)


def toBase10(number, base):
    return int(number, base)

#!/usr/bin/python

"""
compress pitches of a piece of music
grammar size for Fugue #10 in paper is 217
"""

import time
import sys
import re
from glob import glob
from smallgram import *
import music21

# read in a music file
if len(sys.argv) > 1:
    s = music21.converter.parse(sys.argv[1])
else:
    s = music21.converter.parse('bf10i.krn')
if len(sys.argv) > 2:
    voice = int(sys.argv[2])
else:
    voice = None



inputNotes = []
inputRules = []
firstNotes = []
descriptors = []
for j, part in enumerate(s.parts):
    prevNote = None
    intervals = []
    voiceNotes = part.flat.notes
    firstNotes.append(voiceNotes[0])
    descriptors.append('{}, voice {}'.format(s.metadata.title, j))
    for i, n in enumerate(voiceNotes):
        if type(n) == music21.note.Note:
            if prevNote is None:
                prevNote = n
            else:
                intervals.append(
                    music21.interval.notesToGeneric(prevNote, n).simpleDirected
                )
                prevNote = n
    inputNotes.append(voiceNotes)
    inputRules += [Separator('S{}'.format(j))] + intervals

# run the compression algorithm
t0 = time.time()
rules, log = compressGrammar(inputRules, 1)

print '\nTime to compute grammar: {} seconds\n'.format(time.time() - t0)
print 'Grammar length: {}\n\nProduction rules:'.format(len(rules))

# format as a dictionary
gramDict = listToDict(rules)
numRE = re.compile('[\d]+')
gramList = sorted(
    gramDict.items(),
    key=lambda x: int(numRE.findall(x[0])[0])
)
for k, v in gramList:
    print '{} ->'.format(k),
    for s in v:
        print '{}'.format(s),
    print


# re-generate the original input string, minus accidentals
def expand(rule):
    rhs = rule
    generated = []
    for sym in rhs:
        if isinstance(sym, int):
            generated.append(sym)
        else:
            generated += ['<{}'.format(sym)] + expand(gramDict[sym]) + ['{}>'.format(sym)]
    return generated

for i in range(len(firstNotes)):
    generatedIntervals = expand(gramList[i][1])
    noteStream = music21.stream.Stream()
    noteStream.append(firstNotes[i])
    genNotes = [firstNotes[i]]
    genOut = [firstNotes[i].pitch.name]
    for sym in generatedIntervals:
        if type(sym) is str:
            genOut.append(sym)
        else:
            n = deepcopy(genNotes[-1])
            noteStream.append(n)
            n.transpose(music21.interval.GenericInterval(sym), inPlace=True)
            genNotes.append(n)
            genOut.append(n.pitch.name)

    # print the string and its derivation
    genStr = []
    print '\n{}:'.format(descriptors[i])
    for n in genOut:
        if n.isalpha():
            print n,
            genStr.append(n)

    print '\n\nDerivation:'
    color = 7
    for n in genOut:
        if type(n) is str:
            if n[0] == '<':
                color += 1
            c = (color + 1) % 7 + 30 + 1
            print "\033[1;" + str(c) + ";48m" + n,
            if n[-1] == '>':
                color -= 1
        else:
            print n.pitch.name,

    # check for errors in the grammar
    for k in range(len(inputNotes)):
        if inputNotes[i][k].pitch.step != genStr[k]:
            print 'Error reproducing pitch #{}.'.format(k)
            print '\tDerived: {}\tExpected: {}'.format(genStr[k], inputNotes[i][k].pitch.step)

    print "\033[1;37;48m\n"

# print "\033[1;37;48m\n\nlog:"
# print log

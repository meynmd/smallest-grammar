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
# if len(sys.argv) > 1:
#     s = music21.converter.parse(sys.argv[1])
# else:
#     s = music21.converter.parse('bf10i.krn')
if len(sys.argv) > 1:
    path = sys.argv[1]
else:
    path = None
if len(sys.argv) > 2:
    voice = int(sys.argv[2])
else:
    voice = None

inputs = []
descriptors = []
if path is None:
    for f in glob('./*.krn'):
        s = music21.converter.parse(f)
        for j, part in enumerate(s.parts):
            # inputs.append(part.flat.notes)
            inputs.append([
                n for n in part.flat.elements
                    if isinstance(n, music21.note.Note)
                    or isinstance(n, music21.chord.Chord)
            ])
            descriptors.append('{}, voice {}'.format(s.metadata.title, j))
else:
    s = music21.converter.parse(path)
    if voice is None:
        for j, part in enumerate(s.parts):
            # inputs.append(part.flat.notes)
            inputs.append([
                n for n in part.flat.elements
                    if isinstance(n, music21.note.Note)
                    or isinstance(n, music21.chord.Chord)
            ])
            descriptors.append('{}, voice {}'.format(s.metadata.title, j))
    else:
        inputs.append([
            n for n in s.parts[voice].flat.elements
                if isinstance(n, music21.note.Note)
                or isinstance(n, music21.chord.Chord)
        ])
        descriptors.append('{}, voice {}'.format(s.metadata.title, voice))

inputNotes = []
inputRules = []
firstNotes = []
for j, inp in enumerate(inputs):
    prevNote = None
    intervals = []
    firstNotes.append(inp[0])
    # descriptors.append('{}, voice {}'.format(None, j))
    for i, n in enumerate(inp):
        if type(n) == music21.note.Note:
            if prevNote is None:
                prevNote = n
            else:
                intervals.append(
                    music21.interval.notesToGeneric(prevNote, n).simpleDirected
                )
                prevNote = n
        elif type(n) == music21.chord.Chord:
            if prevNote is None:
                prevNote = n.pitches[0]
            else:
                intervals.append(
                    music21.interval.notesToGeneric(prevNote, n.pitches[0]).simpleDirected
                )
                prevNote = n.pitches[0]
    inputNotes.append(inp)
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

startRules = [r for r in gramList if 'S' in r[0]]

for i in range(len(firstNotes)):
    generatedIntervals = expand(startRules[i][1])
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
    for k in range(len(inputs[i])):
        if isinstance(inputs[i][k], music21.note.Note):
            if inputs[i][k].pitch.step != genStr[k]:
                print 'Error reproducing pitch #{}.'.format(k)
                print '\tDerived: {}\tExpected: {}'.format(genStr[k], inputs[i][k].pitch.step)

    print "\033[1;37;48m\n"

# print "\033[1;37;48m\n\nlog:"
# print log

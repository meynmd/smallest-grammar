#!/usr/bin/python

from smallgram import *
import time
import sys

# read in a music file
if len(sys.argv) > 1:
    s = music21.converter.parse('bf10i.krn')
else:
    s = music21.converter.parse('bf10i.krn')
prevNote = None
notes = []
for i, n in enumerate(s.parts[0].flat.notes):
    if type(n) == music21.note.Note:
        if prevNote is None:
            prevNote = n
        else:
            notes.append(
                music21.interval.notesToGeneric(prevNote, n).simpleDirected
            )
            prevNote = n
print 'input: {}\n'.format(notes)

# run the compression algorithm
t0 = time.time()
initRHS, rules = compressGrammar(notes, [], 0)

# format it more nicely
rules = cleanupRuleNums(rules)
print 'Time to compute grammar: {} seconds\n'.format(time.time() - t0)
print 'Grammar length: {}\n'.format(gramLength(initRHS, rules))
startRule = Production('S', 0, initRHS)
rules.insert(0, startRule)
for r in rules:
    printRule(r)

# re-generate the original input string
def expand(rule):
    rhs = rule.rhs
    generated = []
    for sym in rhs:
        if type(sym) is int or type(sym) is str:
            generated.append(sym)
        else:
            generated += ['<R{}'.format(sym.number)] + expand(sym) + ['R{}>'.format(sym.number)]
    return generated

generatedIntervals = expand(rules[0])

print
print generatedIntervals
print

firstNote = music21.note.Note('E4')
noteStream = music21.stream.Stream()
noteStream.append(music21.key.Key('e', 'minor'))
noteStream.append(firstNote)
genNotes = [firstNote]
genOut = [firstNote.pitch.name]
for sym in generatedIntervals:
    if type(sym) is str:
        genOut.append(sym)
    else:
        n = deepcopy(genNotes[-1])
        noteStream.append(n)
        n.transpose(music21.interval.GenericInterval(sym), inPlace=True)
        genNotes.append(n)
        genOut.append(n.pitch.name)

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








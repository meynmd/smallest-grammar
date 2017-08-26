from smallgram import *
import time

# read in a music file
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
print 'Grammar length: {}'.format(gramLength(initRHS, rules))
startRule = Production('S', 0, initRHS)
rules.insert(0, startRule)
for r in rules:
    printRule(r)




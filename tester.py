from smallgram import *

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

print 'input: {}'.format(notes)

initRHS, rules = compressGrammar(notes, [], 0)
rules = cleanupRuleNums(rules)


startRule = Production('S', 0, initRHS)
rules.insert(0, startRule)
for r in rules:
    printRule(r)

print 'max repeat time: {}\nreplace time: {}'.format(time_maxrepeat, time_replace)
from copy import deepcopy
from sys import argv
from collections import deque
import sys
import pickle
import music21
import reexpand

if len(argv) != 5:
    print 'usage: xp.py GRAMMAR_FILE SCORE_FILE PART_NUM START_SYM'
    exit(1)
# with open(argv[1], 'r') as fp:
#     gramDict = pickle.load(fp)

with open(argv[1], 'r') as fp:
    gramDict = reexpand.readGram(fp.readlines())

if len(argv) == 5:
    start = argv[4]
    interact = False
else:
    start = None
    interact = True

partNum = int(argv[3])

score = music21.converter.parse(argv[2])
scoreNotes = [
    n for n in score.parts[partNum].flat.elements
        if isinstance(n, music21.note.Note)
        or isinstance(n, music21.chord.Chord)
]

def expand(rule):
    rhs = rule
    generated = []
    for s in rhs:
        if isinstance(s, int):
            generated.append(s)
        else:
            generated += ['({}'.format(s)] + expand(gramDict[s]) + ['{})'.format(s)]
    return generated


def reexpand(startSym, firstNote):
    generatedIntervals = expand(gramDict[startSym])
    noteStream = music21.stream.Stream()
    noteStream.append(firstNote)
    genNotes = [firstNote]
    genOut = [firstNote.pitch.step]
    opens = deque()
    spans = []
    for sym in generatedIntervals:
        if type(sym) is str:
            genOut.append(sym)
            if sym[0] == '(':
                opens.append((len(genNotes), sym))
            elif sym[-1] == ')':
                closed = (len(genNotes), sym)
                idx, symbol = opens.pop()
                spans.append((symbol, idx, len(genNotes)))
        else:
            n = deepcopy(genNotes[-1])
            noteStream.append(n)
            n.transpose(music21.interval.GenericInterval(sym), inPlace=True)
            genNotes.append(n)
            genOut.append(n.pitch.step)

    # print the string and its derivation
    print 'Re-expanded string:'
    genStr = []
    for n in genOut:
        if n.isalpha():
            print n,
            genStr.append(n)

    print '\n\nDerivation:'
    color = 7
    for n in genOut:
        if type(n) is str:
            if n[0] == '(':
                color += 1
            c = (color + 1) % 7 + 30 + 1
            print "\033[1;" + str(c) + ";48m" + n,
            if n[-1] == ')':
                color -= 1
        else:
            print n.pitch.name,

    print "\033[1;37;48m\n"

    # display score annotated with derivation
    spans = sorted(spans, key=lambda (s, f, l): l - f)
    later = spans
    spanGroups = []


    while len(later) > 0:
        spans = later
        later = []
        last = -1
        group = []
        for span in spans:
            (s, f, l) = span
            if f >= last:
                group.append((s, f, l))
            else:
                later.append((s, f, l))
            last = l
        spanGroups.append(group)

    spanGroups.reverse()

    annotatedScore = deepcopy(score.parts[partNum])

    for j, sg in enumerate(spanGroups):
        notes = [
            n for n in annotatedScore.flat.elements
                if isinstance(n, music21.note.Note)
                or isinstance(n, music21.chord.Chord)
        ]

        for i, (s, f, l) in enumerate(sg):
            startNote = notes[f]
            endNote = notes[l - 1]
            if startNote.lyric is None:
                startNote.lyric = ''
            if endNote.lyric is None:
                endNote.lyric = ''
            startNote.lyric += '(' + s[2:]
            endNote.lyric = s[2:] + ')' + endNote.lyric

    annotatedScore.show()

    # annotatedScore = music21.stream.Score()
    # for j, sg in enumerate(spanGroups):
    #     staff = deepcopy(score.parts[partNum])
    #     staffNotes = [
    #         n for n in staff.flat.elements
    #             if isinstance(n, music21.note.Note)
    #             or isinstance(n, music21.chord.Chord)
    #     ]
    #
    #     for i, (s, f, l) in enumerate(sg):
    #         startNote = staffNotes[f - 1]
    #         endNote = staffNotes[l - 1]
    #         startNote.lyric = '<' + s[2:]
    #         endNote.lyric = s[2:] + '>'
    #
    #     annotatedScore.append(staff)
    # annotatedScore.show()

    '''
    annotatedScore = music21.stream.Score()
    label = ''
    for sym in genOut:
        if sym[0] == '<' or sym[-1] == '>':
            label += sym
        else:
            n = music21.note.Note(sym)
            n.lyric = label
            annotatedScore.append(n)
            label = ''
    annotatedScore.show()
    '''



if interact:
    while True:
        ss = raw_input('Starting Rule: ')
        if ss == '':
            exit(0)
        sn = raw_input('Starting Note: ')
        if sn == '':
            sn = deepcopy(scoreNotes[0])
        else:
            n = music21.note.Note()
            n.pitch.pitchClass = sn
        reexpand(ss, n)
else:
    ss = start
    sn = deepcopy(scoreNotes[0])
    reexpand(ss, sn)
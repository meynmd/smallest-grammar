import music21
from collections import deque
from collections import defaultdict
from copy import deepcopy


def readGram(lines):
    grammar = defaultdict(list)
    for line in lines:
        line = line.strip().split()
        rhs = line[2:]
        rhs = [s if s[0].isalpha() else int(s) for s in rhs]
        grammar[line[0]] = rhs
    return grammar


def expand(rule, gramDict):
    rhs = rule
    generated = []
    for s in rhs:
        if isinstance(s, int):
            generated.append(s)
        else:
            generated += ['({}'.format(s)] + expand(gramDict[s], gramDict) + ['{})'.format(s)]
    return generated


def reexpand(startSym, firstNote, gramDict):
    generatedIntervals = expand(gramDict[startSym], gramDict)
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
    return genOut, noteStream

from collections import defaultdict
"""
maxrepeat(s) finds all occurrences of max length repeated substring in s
"""
def maxrepeat(s):
    current, best = [], []
    occurrences = defaultdict(set)

    # split at each possible point
    for offset in range(1, len(s) - 1):
        start = 0

        # compare elements offset by this distance
        last = len(s) - offset
        for i in range(last):
            if s[i] == s[offset + i]:
                # building the substring
                current.append(s[i])
                if i < last - 1:
                    continue

            # substring has ended
            if i == last - 1:
                i += 1
            if len(current) > len(best):
                best = current
                occurrences = defaultdict(
                    set, {tuple(best) : {
                        (start, i),
                        (start + offset, i + offset)
                    }})
            elif len(current) == len(best) and len(best) > 0:
                occurrences[tuple(current)].add((start, i))
                occurrences[tuple(current)].add((start + offset, i + offset))

            start = i + 1
            current = []

    return max(occurrences.items(), key=lambda x: len(x[0]) * len(x[1]))



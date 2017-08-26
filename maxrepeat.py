import time
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
                end = i + 1
            else:
                end = i
            if len(current) > 1:
                occurrences[tuple(current)].add((start, end))
                occurrences[tuple(current)].add((start + offset, end + offset))
            start = i + 1
            current = []

    return sorted(
                  [(k, list(v)) for k, v in occurrences.items()],
                  key=lambda x: len(x[0]) * len(x[1]), reverse=True
    )


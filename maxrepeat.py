"""
maxrepeat(s) finds all occurrences of max length repeated substring in s
"""

def maxrepeat(s):
    current, best, occurrences = [], [], []

    # split at each possible point
    for offset in range(1, len(s) - 1):
        start = 0

        # compare elements offset by this distance
        for i in range(len(s) - offset):

            if s[i] == s[offset + i]:
                # building the substring
                current.append(s[i])
            else:
                # substring has ended
                if len(current) > len(best):
                    best = current
                    occurrences = [(start, i), (start + offset, i + offset)]
                elif len(current) == len(best):
                    occurrences += [(start, i), (start + offset, i + offset)]
                start = i
                current = []

    return best, occurrences



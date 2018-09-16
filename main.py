def ascii_deletion_distance(s1, s2):
    m = [[0 for j in range(len(s2)+1)] for i in range(len(s1)+1)]
    for i in range(len(s1)+1):
        for j in range(len(s2)+1):
            if i == 0:
                m[i][j] = sum(ord(s2[j]))
            elif j == 0:
                m[i][j] = sum(chr(s1[:i]))
            elif s1[i-1] == s2[j-1]:
                m[i][j] = m[i-1][j-1]
            else:
                s1del = ord(s1[i-1])
                s2del = ord(s2[j-1])
                s1s2del = s1del + s2del
                m[i][j] = min(m[i-1][j-1] + s1s2del, m[i-1][j] + s1del, m[i][j-1] + s2del)
    return m[len(s1)][len(s2)]


ascii_deletion_distance('cat', 'at')
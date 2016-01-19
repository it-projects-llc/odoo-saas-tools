__author__ = 'D.H. Bahr <dhbahr@gmail.com>'


def _levenshtein(src, tgt):
    m = len(src)
    n = len(tgt)
    d = [[0] * (m+1) for row in xrange(n+1)]

    for i in xrange(1, m+1):
        d[0][i] = i

    for j in xrange(1, n+1):
        d[j][0] = j

    for j in xrange(1, n+1):
        for i in xrange(1, m+1):
            try:
                if src[i-1] == tgt[j-1]:
                    d[j][i] = d[j - 1][i - 1]
                else:
                    d[j][i] = min(d[j-1][i]+1, d[j][i-1]+1, d[j-1][i-1]+1)
            except:
                print i, j

    return d[n][m]

def acronym(src):
    words = src.split(" ")
    return "".join([x[0] for x in words]).upper()


if __name__ == "__main__":
    print acronym("American Association Against the Abuse of Acronyms")[:3]

import csv
import re


def isnotEmpty(line):
    #print line
    foo = filter(lambda x:len(x), line)
    ch_count = reduce(lambda x,y: x+y, foo)
    if ch_count:
        return True
    else:
        return False

def removeAppend(line):
    nline = []
    print line
    for token in line:
        token = token.strip()
        if token:
            print 'Y'
            temp = re.sub('[ \n]+','', token)
            temp = re.sub('[ ,]+',' ', temp)
            nline.append(temp)
        else:
            nline.append('888')
    return nline


def clean_csv(fn):
    with open(fn, 'r') as f:
        header = f.readline()

    rf = csv.reader(open(fn))
    next(rf, None)

    res = []
    for line in rf:
        #print "choo Choo", line
        if isnotEmpty(line):

            res.append(removeAppend(line))
            
    
    with open('cleaned_{}.csv'.format(fn.split('.')[0]), 'w') as f:
        f.write(header)
        for li in res:
            for tok in li:
                f.write(tok)
                f.write(',')
            f.write('\n')


    print 'Success'


if __name__ == '__main__':
    clean_csv('Andhra Pradesh.csv')

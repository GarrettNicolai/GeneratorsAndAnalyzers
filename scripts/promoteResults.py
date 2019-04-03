import sys
import codecs
import re
import regex
import operator

fDict = codecs.open(sys.argv[1], "r", "utf-8")
fDTL = codecs.open(sys.argv[2], "r", "utf-8")
fOut = codecs.open(sys.argv[3], "w", "utf-8")

Dict = {}
DTLScores = {}

for i in fDict:
    parts = i.strip().lower().split("\t");
    Dict[parts[0]] = True

for i in fDTL:
    parts = i.replace("|", "").replace("_","").replace("#","").split("\t")
    if(len(parts) < 2):
        continue
    if(parts[3] == "-inf"):
        continue
    if parts[0] not in DTLScores:
        DTLScores[parts[0]] = {}
        DTLScores[parts[0]]["MAXIMUM"] = -1000000000
        DTLScores[parts[0]]["MINIMUM"] = 100000000
    if(parts[1] in DTLScores[parts[0]]):
            continue

    maximum = DTLScores[parts[0]]["MAXIMUM"]
    minimum = DTLScores[parts[0]]["MINIMUM"]

    DTLScores[parts[0]][parts[1]] = float(parts[3])
    if(float(parts[3]) > maximum):
        DTLScores[parts[0]]["MAXIMUM"] = float(parts[3])
    if(float(parts[3]) < minimum):
        DTLScores[parts[0]]["MINIMUM"] = float(parts[3])

normalizedScores = {}
for i in DTLScores:
    predictions = DTLScores[i]
    normalizedScores[i] = {}
    maximum = predictions["MAXIMUM"]
    minimum = predictions["MINIMUM"]
    difference = maximum - minimum
    #if(difference == 0):
    #    print(DTLScores[i])
    #    continue
    for j in predictions:
        if(j == "MAXIMUM" or j == "MINIMUM"):
            continue;
        if(difference == 0.0):
            normalizedScores[i][j] = 1.1
        else:
            normalizedScores[i][j] = ((predictions[j] - minimum) / difference) + 0.10
        analysis = re.sub(r"([A-Z])\+([A-Z])", r"\1;\2", j)
        analysisParts = analysis.split("+");
        lemma = analysisParts[0]
        if("*" in lemma):
            if(len(analysisParts) < 2):
                continue
            lemma = analysisParts[1]
        if(lemma in Dict):
            normalizedScores[i][j] += 1.1;

for i in normalizedScores:
    predictions = normalizedScores[i]
    sorted_x = sorted(predictions.items(), key=operator.itemgetter(1), reverse=True)
    count = 1;
    for j in sorted_x:
        if(float(j[1]) > 1.1):
            fOut.write(i + "\t" + j[0] + "\t" + str(count) + "\n")
            count += 1
        else:
            break
    if(count == 1):
        fOut.write(i + "\n")
        

fDict.close();
fDTL.close();
fOut.close();

import sys
import codecs
import re



fIn = codecs.open(sys.argv[1], "r", "utf-8")
fOut = codecs.open(sys.argv[2], "w", "utf-8")
affixing = sys.argv[3].lower

orig2um = {}
fConvert = ""

for i in fIn:
    if(i.strip() == ""):
        continue
    k = 0;
    i = i.strip()
    words = i.split("\t")
    surface = words[0]
    if(len(words) < 2):
        z = 0
    analysis = words[1]
    rank = words[2]
    score = words[3]
    surfaceParts = surface.strip().split("|")
    analysisParts = analysis.strip().split("|")
#    z = 0;
    tag = ""
    lemma = ""
    stem = ""
    prefix = ""
    suffix = ""
    j = 0;
    deletion = ""
    while j < len(analysisParts):
        while "_" in analysisParts[j]:
            deletion += surfaceParts[j]
            j+= 1
        if "!" in surfaceParts[j] and (affixing == 'p' or affixing == 'c'):
            tag = analysisParts[j]
            prefix += surfaceParts[j]
            j += 1 
            continue    
            
        if "#" in surfaceParts[j] and (affixing == 's' or affixing == 'c'):
            tag = analysisParts[j]
            suffix += deletion
            deletion = ""
            suffix += surfaceParts[j]
            j += 1
            continue
        if ("!" in surfaceParts[j] and affixing == 's') or ("#" in surfaceParts[j] and affixing == 'p'):
            #lemma += analysisParts[j]
            #stem += surfaceParts[j]
            tag = analysisParts[j]
            stem += deletion
            deletion = ""
            j += 1
            continue
            
        if lemma == "" and (affixing == 'p' or affixing == 'c'):
            prefix += deletion
            deletion = ""
        else:
            stem += deletion
            deletion = ""
        lemma += analysisParts[j]
        stem += surfaceParts[j]
        j += 1
        
    features = tag.strip().split(";")
    nufeatures = []
    lemma = re.sub(r"\([^A-Z;]\)\+\([^A-Z;]\)", r"\1\2", lemma)
    lemma = re.sub(r"^\++", r"", lemma)
    lemma = re.sub(r"\++$", r"", lemma)



    fOut.write(surface.strip().replace("!","").replace("#","").replace(":","").replace("|","").replace("_","") + "\t" + lemma.replace("!","").replace("#","") + "\t" + ";".join(nufeatures) + "\t" + rank + "\t" + score + "\n")
    

fIn.close();
fOut.close();


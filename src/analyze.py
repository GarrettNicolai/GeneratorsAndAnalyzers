# -*- coding: utf-8 -*-
"""
Created on Mon Mar 19 2018

@author: Garrett Nicolai

Morphological analyzer:
Usage:  python analyze.py -i inFile -o outFile -l language (-g) (-n N) (-d Dictionary)
inFile is the file to analyze
outFile is the location to print output
language is the language of the inFile
-g indicates running the script in generation mode, instead of analysis mode
-n is the number of analyses / generations to produce, while 
the Dictionary will limit output to forms observed in the list

We currently support more than 900 languages: 
Please search the file models.in for by ISO 639 code
to see which languages are supported
"""



import sys
import codecs
import re
import os
from optparse import OptionParser
from subprocess import call



#Get Options

parser = OptionParser()
parser.add_option("-i", "--in", dest="inFile",
                  help="FILE to analyze", metavar="FILE")
parser.add_option("-o", "--out", dest="outFile",
                  help="Write analyzed file to FILE", metavar="FILE")
parser.add_option("-l", "--lang", dest="language",
                  help="Language of file to be analyzed")
parser.add_option("-g", "--gen", action="store_true", dest="generate",
                  help="Run in generation mode")
parser.add_option("-n", "--nBest", dest="nBest",
                  help="Number of analysis candidates to return")
parser.add_option("-d", "--dictionary", dest="dictionary",
                  help="A dictionary of forms to limit the output")

(options,args) = parser.parse_args()

if not options.inFile or not options.outFile or not options.language:
    parser.error("Usage must be python analyze.py -i inFile -o outFile -l language -n nBest -d dictionary -g")



### Global variables ###

models = {}
lookup = {}
lookupGen = {}
languages = []
orig2um = {}
import regex



modelIn = codecs.open("models.in", "r", "utf-8")
analyzedOutput = codecs.open("analyzed.out1", "w", "utf-8")
intermediateNouns = codecs.open("nounsToAnalyze.txt", "w", "utf-8")
intermediateVerbs = codecs.open("verbsToAnalyze.txt", "w", "utf-8")
affixFile = ""

#Read in parameters from model file


for i in modelIn:
    parts = i.strip().split("\t")
    if(parts[0].lower() == options.language):
       models["Lookup"] = parts[1].strip()
       models["DTLVMA"] = parts[2].strip()
       models["DTLNAMA"] = parts[3].strip()
       models["DTLVG"] = parts[4].strip()
       models["DTLNAG"] = parts[5].strip() 
       affixFile = codecs.open(parts[6].strip(), "r", "utf-8")
    languages.append(parts[0])

modelIn.close()



if not models:
   print("Sorry, that language is not yet supported. We currently support:" )
   for i in languages:
       print(i)
   print("More to come!")
   sys.exit()

#Determine conversion method for features

fConvert = ""

tagsIn = codecs.open("tags", "r", "utf-8")
Tags = {}
Tags["verbs"] = {}
Tags["nouns"] = {}
Affixing = {}
Affixes = {}
Affixing["verbs"] = ""
Affixing["nouns"] = ""

for line in affixFile:
    parts = line.split("\t")
    Affixes[parts[0]] = {}
    Affixes[parts[0]]["VERBS"] = float(parts[1])
    Affixes[parts[0]]["NOUNS"] = float(parts[2])
    Affixes[parts[0]]["ADJS"] = float(parts[3]) 
    Affixes[parts[0]]["OTHER"] = float(parts[4])
        
        
for line in tagsIn:
    parts = line.split("\t")
    language = parts[0]
    if(language != options.language):
        continue
    for i in range(1,len(parts)):
        tag = parts[i]
        if("VB" in tag):
            Tags["verbs"][tag] = True
            if(Affixing["verbs"] == ""):
                if("++" in tag):
                    Affixing["verbs"] = "C"
                elif(tag.startswith("+")):
                    Affixing["verbs"] = "S"
                elif(tag.endswith("+")):
                    Affixing["verbs"] = "P"

        if("NN" in tag):
            Tags["nouns"][tag] = True
            if(Affixing["nouns"] == ""):
                if("++" in tag):
                    Affixing["nouns"] = "C"
                elif(tag.startswith("+")):
                    Affixing["nouns"] = "S"
                elif(tag.endswith("+")):
                    Affixing["nouns"] = "P"

    

#Read lookup table into hash, converting if necessary
try:
    lookupIn = codecs.open(models["Lookup"], "r", "utf-8")
    for line in lookupIn:
       if(line.strip() == ""):
           continue
       parts = line.split("\t")
       sf = parts[1].lower().strip()
       lemma = parts[0].lower().strip()
       if(lemma not in lookupGen):
            lookupGen[lemma] = []
       if(sf not in lookup):
            lookup[sf] = []
       features = parts[2].strip().split(";")
       nufeatures = []
       for f in features:
            try:
                nufeatures.append(f)
            except:
                pass
       lookup[sf].append(lemma + "\t" + ";".join(nufeatures))
       lookupGen[lemma].append(sf + "\t" + ";".join(nufeatures) )
    lookupIn.close()

except:
    pass
analyzeIn = codecs.open(options.inFile, "r", "utf-8")

#Process inFile.  If instance is not in hash, then pass it to intermediate file

for line in analyzeIn:
    if (not options.generate and line.strip().lower() in lookup) or (options.generate and line.strip().lower() in lookupGen):
       if(options.generate):
           analyses = lookupGen[line.lower().strip()]
       else:
           analyses = lookup[line.lower().strip()]
       for a in analyses:
           analyzedOutput.write(line.lower().strip() + "\t" + a + "\n") 
    else:
       affix = ""
       if(len(line.lower().strip()) >= 3) and Affixing["verbs"] == "P":
           affix = line.lower().strip()[0:3] + "-"
       elif(len(line.lower().strip()) >= 3) and Affixing["verbs"] == "S":
           affix = "-" + line.lower().strip()[-3:]
       elif(len(line.lower().strip()) >= 3) and Affixing["verbs"] == "C":
           affix = line.lower().strip()[0:3] + "-" + line.lower().strip()[-3:]

                   
       VScore = 0.0
       NScore = 0.0

       if(affix not in Affixes or affix == ""):
           VScore = 0.0
           NScore = 0.0
       else:
           VScore = Affixes[affix]["VERBS"]
           NScore = Affixes[affix]["NOUNS"] + Affixes[affix]["ADJS"]

       if((not options.generate and models["DTLNAMA"] != "NA" and models["DTLVMA"] != "NA")) or (options.generate and models["DTLNAG"] != "NA" and models["DTLVG"] != "NA"):
           if(options.generate):
               for tag in Tags["nouns"]:
                   if("++" in tag):
                       generationForm = tag.replace("++",":+:" + ":".join(regex.findall(r"\X", line.lower().strip(), regex.U)) + ":+:")
                   elif(tag.endswith("+")):
                       generationForm = re.sub(r"\+$", ":+:" + ":".join(regex.findall(r"\X", line.lower().strip(), regex.U)), tag)
                   elif(tag.startswith("+")):
                       generationForm = re.sub(r"^\+", ":".join(regex.findall(r"\X", line.lower().strip(), regex.U)) + ":+:", tag)
                   if(VScore < 0.5): #ie, not likely to just be a verb
                       intermediateNouns.write(generationForm + "\n")
               for tag in Tags["verbs"]:
                   if("++" in tag):
                       generationForm = tag.replace("++",":+:" + ":".join(regex.findall(r"\X", line.lower().strip(), regex.U)) + ":+:")
                   elif(tag.endswith("+")):
                       generationForm = re.sub(r"\+$", ":+:" + ":".join(regex.findall(r"\X", line.lower().strip(), regex.U)), tag)
                   elif(tag.startswith("+")):
                       generationForm = re.sub(r"^\+", ":".join(regex.findall(r"\X", line.lower().strip(), regex.U)) + ":+:", tag)
                   if(NScore < 0.5): #Not likely to just be a noun
                       intermediateVerbs.write(generationForm + "\n")
           else:
               if(VScore < 0.5):
                   if(Affixing["nouns"] == "C" or Affixing["nouns"] == "P"):
                       intermediateNouns.write("#:")
                   intermediateNouns.write(":".join(regex.findall(r"\X", line.lower().strip(), regex.U)))
                   if(Affixing["nouns"] == "C" or Affixing["nouns"] == "S"):
                       intermediateNouns.write(":!")
                   intermediateNouns.write("\n")

               if(NScore < 0.5):
                   if(Affixing["verbs"] == "C" or Affixing["verbs"] == "P"):
                       intermediateVerbs.write("#:")
                   intermediateVerbs.write(":".join(regex.findall(r"\X", line.lower().strip(), regex.U)))
                
                   if(Affixing["verbs"] == "C" or Affixing["verbs"] == "S"):
                       intermediateVerbs.write(":!")
                   intermediateVerbs.write("\n")



               #intermediateFile.write("#:" + ":".join(line.strip()).replace(" ", "!") + "@" + "\n") #DTL-specific format
       else:
           intermediateNouns.write(line + "\n") #Catch-all
           intermediateVerbs.write(line + "\n") #Catch-all



analyzeIn.close()
analyzedOutput.close()
intermediateNouns.close()
intermediateVerbs.close()

#As long as there is an NN model, then we can analyze using the NN

if (not options.generate and models["DTLNAMA"] != "NA" and models["DTLVMA"] != "NA") or (options.generate and models["DTLNAG"] != "NA" and models["DTLVG"] != "NA"):  #Do DTL Analysis
    try:
        if(not options.generate):
            nBest = 5
            if(options.nBest is not None):
                nBest = options.nBest
            call([os.environ["DTL"], "--cs", "4", "--ng", "9", "--copy", "--jointMgram", "3", "--inChar", ":", "-t","nounsToAnalyze.txt", "--nBestTest", str(nBest), "-a","analyzed.nouns.dtl.out", "--mi", models["DTLNAMA"]])     
            call(["python", "postProcessDTL.py", "analyzed.nouns.dtl.out.phraseOut", "analyzed.out2", Affixing["nouns"]])   
            call([os.environ["DTL"], "--cs", "4", "--ng", "9", "--copy", "--jointMgram", "3", "--inChar", ":", "-t","verbsToAnalyze.txt", "--nBestTest", str(nBest), "-a","analyzed.verbs.dtl.out", "--mi", models["DTLVMA"]])
            call(["python", "postProcessDTL.py", "analyzed.verbs.dtl.out.phraseOut", "analyzed.out3", Affixing["verbs"]])   
            if(options.dictionary is not None):
                call(["python", "promoteResults.py", options.dictionary, "analyzed.out2", "analyzed.out4"])   
                call(["python", "promoteResults.py", options.dictionary, "analyzed.out3", "analyzed.out5"])   
                call(["mv", "analyzed.out4", "analyzed.out2"])
                call(["mv", "analyzed.out5", "analyzed.out3"])

        else:
            nBest = 5
            if(options.nBest is not None):
                nBest = options.nBest

            call([os.environ["DTL"], "--cs", "4", "--ng", "9", "--copy", "--jointMgram", "3", "--inChar", ":", "-t","nounsToAnalyze.txt", "--nBestTest", str(nBest), "-a","analyzed.nouns.dtl.out", "--mi", models["DTLNAG"]])     
            call(["python", "postProcessDTL.py", "analyzed.nouns.dtl.out.phraseOut", "analyzed.out2", Affixing["nouns"]])   
            call([os.environ["DTL"], "--cs", "4", "--ng", "9", "--copy", "--jointMgram", "3", "--inChar", ":", "-t","verbsToAnalyze.txt", "--nBestTest", str(nBest), "-a","analyzed.verbs.dtl.out", "--mi", models["DTLVG"]])     
            call(["python", "postProcessDTL.py", "analyzed.verbs.dtl.out.phraseOut", "analyzed.out3", Affixing["verbs"]])   
            if(options.dictionary is not None):
                call(["python", "promoteResults.py", options.dictionary, "analyzed.out2", "analyzed.out4"])   
                call(["python", "promoteResults.py", options.dictionary, "analyzed.out3", "analyzed.out5"])   
                call(["mv", "analyzed.out4", "analyzed.out2"])
                call(["mv", "analyzed.out5", "analyzed.out3"])
    except:
        print("There was an error.  Is DirecTL+ installed? If not, it can be obtained at https://github.com/GarrettNicolai/DTLM")

#In the worst case, we skip the examples, and declare a miss
else:
    call(["mv", "nounsToAnalyze.txt", "analyzed.out2"]) 
    call(["mv", "verbsToAnalyze.txt", "analyzed.out3"]) 
    


#We now concatenate the lookup and analyzed forms back together.  Note, this will not follow the order of the original file.
filenames = ['analyzed.out1', 'analyzed.out2', 'analyzed.out3']
outFile = codecs.open(options.outFile, "w", "utf-8")    
for filename in filenames:
    inFile = codecs.open(filename, "r", "utf-8") 
    for line in inFile:
        parts = line.split("\t")
        if(parts[4].strip() == "0"):
            if(parts[3] == "1"):
                line = parts[0] + "\t" + parts[0] + "\n"
            else:
                continue
        if(len(parts) == 1):
            line = line.strip() + "\t" + "MISS" + "\n"; #Unanalyzed, for cases where NN and DTL are unavailable, but lookup is available
        outFile.write(line)
    inFile.close()


#Cleanup

call(["rm", "-f", "toAnalyze.txt"])
call(["rm", "-f", "analyzed.out1"])
#call(["rm", "-f", "analyzed.out2"])
#call(["rm", "-f", "analyzed.out3"])
call(["rm", "-f", "analyzed.nouns.dtl.out.phraseOut"])
call(["rm", "-f", "analyzed.verbs.dtl.out"])

outFile.close()



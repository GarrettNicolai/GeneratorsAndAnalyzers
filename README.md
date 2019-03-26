# Description 
Runnable Morphological Analysis and Generation Tools 

## Warning

This software is at an **alpha** stage. 

## Prerequisites

[DirecTL+](https://github.com/GarrettNicolai/DTLM)




## Installation
900 DTL+ models are too large to be hosted on GitHub, so we do not include them here; please contact gnicola2 AT jhu DOT edu for pre-trained models.
Uncompress DTL models into models/DTL directory.

```
tar -xvzf DTLModel.tgz
```

Set environment variables to point to required binaries.

```
export DTL=<location of DTL binary>
export CTRANSLATE=<location of ctranslate binary>
```

## Usage

```
python src/analyze.py -i input.wordlist -a output.analyses -l language -n nBest -d dictionary -g

The input list contains a list of words to either analyze, or a list of lemmas
from which to generate.  

NBest produces the n-best hypotheses for each input form; default is 5.

Dictionary is a list of acceptable types or lemmas.

-g will run the system in generation mode, as opposed to analysis mode.
```

For example:

To analyze a list of Welsh words, and to limit their lemmas to a dictionary of citation forms contained in WelshLemmas.txt:
```
python analyze.py -i Welsh.toAnalyze -a WelshLemmaPredictions.out -l cym **-d WelshLemmas**

To generate inflected forms from a list of lemmas, activate the **-g** flag.  The dictionary option can still be used, but instead of lemmas, the dictionary should now contain a list of attested forms, without frequency statistics. Note that the dictionary for the generation task can be used as an input to the analysis task, and vice versa. 

python analyze.py -i WelshLemmas -a WelshInflectionPredictions.out -l cym **-d Welsh.toAnalyze** **-g**
```

It is not necessary to provide the location of a DTL model; this information is contained in the configuration file (models.in) in the src directory.




## Supported Languages

```
We currently support more than 900 languages; to see if your language is
supported, please view the file supportedLanguages, which contains
the ISO-639 codes for each language currently supported.
```

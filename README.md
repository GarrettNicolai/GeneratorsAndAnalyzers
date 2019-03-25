# Description 
Runnable Morphological Analysis and Generation Tools 

## Warning

This software is at an **alpha** stage. 

## Prerequisites

[DirecTL+](https://github.com/GarrettNicolai/DTLM)




## Installation
Due to the size of DirecTL+ models, we do not include them here; please contact gnicola2 AT jhu DOT edu for pre-trained models.
Uncompress DTL models into models/DTL directory. See **releases** tab above to download.

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

```
python analyze.py -i Welsh.toAnalyze -a Welsh.out -l welsh
```


## Supported Languages

```
We currently support more than 900 languages; to see if your language is
supported, please view the file supportedLanguages, which contains
the ISO-639 codes for each language currently supported.
```

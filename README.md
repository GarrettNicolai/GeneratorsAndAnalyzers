# analyzers
Runnable Morphological Analysis and Generation Tools from aligned bible corpora

## Warning

This software is at an **alpha** stage. 

## Prerequisites

[DirecTL+](https://github.com/GarrettNicolai/DTL)




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

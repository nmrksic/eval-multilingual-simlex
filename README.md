# Tool for Evaluating Multilingual WS-353 and SimLex-999
Nikola Mrkšić
nm480@cam.ac.uk

Multilingual versions of WordSim-353 and SimLex-999 datasets are a valuable new resource for evaluating word vector spaces. A full description of the datasets can be found on their [webpage](http://technion.ac.il/~ira.leviant/MultilingualVSMdata.html). 

This repository provides a script to evaluate collections of word vectors with respect to the four supported languages (English, German, Italian and Russian). The script reports the SimLex-999 and WS-353 scores (and coverage), as well as the scores for the WS-353 similarity and relatedness subsets.  

###Usage

```python evaluate.py word_vector_location language```

The word vectors file should list one entry per line, with each word followed by the word vector itself. The words can either contain no language prefixes or language prefixes of the following form: en_dog, de_Hund, it_cane, ru_собака. 
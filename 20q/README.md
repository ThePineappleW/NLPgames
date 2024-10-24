# Twenty Questions

Play 20 questions against WordNet.
Most terms in WordNet are not deeper than 20 levels in the hierarchy.   
The main issue is siblings.

Note that only nouns are implemented.

The synset `cat.n.01` refers to the label `cat`, the POS `n`, and the sense ID `01`.

## Usage

To play the game:

```
python 20q.py
```



To find the path to a given synset:

```
python 20q.py -p <synset_label>
```

Where the synset label is as described above.

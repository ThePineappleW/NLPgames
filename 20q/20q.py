"""
A crude implementation of 20 Questions
Please only stick to nouns... NLTK's WordNet might contain cycles for adjectives and verbs.

Usage:
`python 20q.py <category>`
<category> is the starting WordNet Synset. By default it is `entity.n.01`. 

`python 20q.py -p <term>`
Displays the term's location in the hierarchy.

EJ  2024-10-21
"""

import nltk
from nltk.corpus import wordnet as wn
# download WordNet
try:
    nltk.data.find('corpora/wordnet.zip')
except LookupError:
    nltk.download('wordnet')


class Node:
    """
    Implementation of a tree with some extra utilities.
    Each node is a synset, and its children are any hyponyms.
    """
    def __init__(self, label: str, definition: str, children:list=()):
        self.label = label
        self.definition = definition
        self.children = children

    def name(self) -> str:
        """The nicely-formatted name of this synset."""
        return self.label.rsplit('.')[0].replace('_', ' ')

    def defn(self) -> str:
        """The definition of this synset."""
        return self.definition
    
    def count(self) -> int:
        """
        The number of nodes in this tree.
        Returns 1 if this is a leaf (no known hyponyms).
        """
        return 1 + sum([c.count() for c in self.children])
    
    def find(self, target, path):
        """
        Traces the path to a certain word.
        
        Params:
            target: The string name of the desired node
            path: A list of names representing the steps in the tree. Should be `[]` on invocation.
        """
        if self.label == target:
            return path + [self.label]
        elif len(self.children) == 0:
            return []
        else:
            for child in self.children:
                c = child.find(target, path + [self.label])
                if len(c) > 0:
                    return c
            return []


def build_tree(root: nltk.corpus.reader.wordnet.Synset) -> Node:
    """
    Construct a tree from WordNet data.
    UNSAFE for non-nouns.

    Params:
        root: The starting Synset.
    Returns:
        The fully-populated tree.
    """
    hyponyms = root.hyponyms()
    if len(hyponyms) == 0:
        return Node(root.name(), root.definition())
    else:
        return Node(root.name(), root.definition(), [build_tree(child) for child in hyponyms])

# Responses for the game input
# We use `yes!` To indicate an exact match, even if there are still further hyponyms.
POS = ('yes', 'y')
NEG = ('no', 'n')

def starting_message():
    msg = '''
        Welcome to Twenty Questions!
        Think of a secret word, then answer the questions.
        
        If your word has hyponyms (e.g. 'cat' --> 'siamese', 'tabby', etc.), 
        and it is guessed by the computer, answer 'yes!'.
        
        If you are unsure of the meaning of a word, enter '?'.
    '''
    print(msg)
    input('Press enter to begin...')
    
def play_game(root=wn.synset('entity.n.01')) -> None:
    """
    Plays a game of twenty questions.
    Think of a secret word, and then you will be prompted with a question.
    Answer either `yes` or `no`.
    If your word itself has hyponyms (e.g. 'cat' --> 'tabby', 'siamese', etc.),
    and the computer guesses it correctly, end your answer with `!`.

    Params:
        root: Starting Synset, 'entity.n.01' by default.
    """
    
    tree = build_tree(root)
    subtree_ind = 0
    
    starting_message()
    
    correct = False
    q_num = 0
    
    while not correct:
        subtrees = sorted(tree.children, key=Node.count, reverse=True)

        if len(subtrees) == 0:
            print(f'I win in {q_num} guesses! Your word is: {tree.name()}')
            return
        
        if subtree_ind >= len(subtrees):
            print('I could not guess your word :(')
            return

        current_topic = subtrees[subtree_ind]
        
        q_num += 1
        response = input(f'Question {q_num}: Is it a {current_topic.name()}? ')

        if response.endswith('!'):
            print(f'I win in {q_num} guesses! Your word is "{current_topic.name()}"!')
            return
        if response.lower() in POS:
            tree = current_topic
            subtree_ind = 0
        elif response.lower() in NEG:
            subtree_ind += 1
        else:
            print(f'\tA "{current_topic.name()}" is "{current_topic.definition}"')
            q_num -= 1

def find_path(target):
    """Prints the path to the given word"""
    tree = build_tree(wn.synset('entity.n.01'))
    path = tree.find(target, [])
    if len(path) > 0:
        for i, word in enumerate(path):
            print(f'{" "*i}{word}')
    else:
        print(f'{target} was not found in the database.')

if __name__ == '__main__':
    from sys import argv

    if len(argv) == 1:
        play_game()
    elif len(argv) == 2:
        play_game(root=wn.synset(argv[1]))
    elif argv[1] == '-p':
        find_path(argv[2])
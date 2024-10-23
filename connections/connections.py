#!/usr/bin/env python
# coding: utf-8

# # Connections using ConceptNet
# 
# The goal is to pick a term for a category, then to pick a set of terms that all share some (perhaps the same) relation with the former.

# In[1]:


import requests
import time
from random import choice, shuffle
import webbrowser
import os
import tempfile


# In[3]:


RELS = (
    'PartOf',
    'IsA',
    'DerivedFrom',
    'CapableOf',
    'HasA',
    'Causes',
    'AtLocation',
    'HasProperty',
    'Synonym',
)


# In[5]:


WORDS = [
    'time',
    'year',
    'people',
    'way',
    'day',
    'man',
    'thing',
    'woman',
    'life',
    'child',
    'world',
    'school',
    'state',
    'family',
    'student',
    'group',
    'country',
    'problem',
    'hand',
    'part',
    'place',
    'case',
    'week',
    'company',
    'system',
    'program',
    'question',
    'work',
    'government',
    'number',
    'night',
    'point',
    'home',
    'water',
    'room',
    'mother',
    'area',
    'money',
    'story',
    'fact',
    'month',
    'lot',
    'right',
    'study',
    'book',
    'eye',
    'job',
    'word',
    'business',
    'issue',
    'side',
    'kind',
    'head',
    'house',
    'service',
    'friend',
    'father',
    'power',
    'hour',
    'game',
    'line',
    'end',
    'member',
    'law',
    'car',
    'city',
    'community',
    'name',
    'president',
    'team',
    'minute',
    'idea',
    'kid',
    'body',
    'information',
    'back',
    'parent',
    'face',
    'others',
    'level',
    'office',
    'door',
    'health',
    'person',
    'art',
    'war',
    'history',
    'party',
    'result',
    'change',
    'morning',
    'reason',
    'research',
    'girl',
    'guy',
    'moment',
    'air',
    'teacher',
    'force',
    'education',
]


# In[6]:


def conceptnet(term: str, lang:str='en', all_results=True, verbose=False) -> dict:
    if verbose:
        print(f'Querying term "{term}"')
        start = time.time()
    res = requests.get(f'http://api.conceptnet.io/c/{lang}/{term}')
    if verbose:
        elapsed = time.time() - start
        print(f'Response received after {elapsed}s.')
    return res.json()

def conceptnet_query(start=None, end=None, rel=None, lang='en', verbose=False):
    base_request = 'http://api.conceptnet.io/query?'
    if start:
        base_request += f'start=/c/{lang}/{start}&'
    if end:
        base_request += f'end=/c/{lang}/{end}&'
    if rel:
        base_request += f'rel=/r/{rel}&'
    
    if verbose:
        print(f'Querying {base_request}')
        start = time.time()
    res = requests.get(base_request)
    if verbose:
        elapsed = time.time() - start
        print(f'Response received after {elapsed}s.')
    return res.json()


# In[11]:


def remove_word(word, terms):
    return [term for term in terms if word not in term][:4]
    
def random_category(word, rels=RELS, verbose=False):
    if len(rels) == 0:
        raise RuntimeError('No valid relations for' + word  + '!')
    rel = choice(list(rels))
    anchor = choice(('start', 'end'))

    if anchor == 'start':
        res = conceptnet_query(start=word, rel=rel, verbose=verbose)
        other_anchor = 'end'
    else:
        res = conceptnet_query(end=word, rel=rel, verbose=verbose)
        other_anchor = 'start'
    
    terms = [edge[other_anchor]['label'] for edge in res['edges'] if edge[other_anchor]['language'] == 'en']
    terms = remove_word(word, terms)
    if len(terms) < 4:
        return random_category(word, rels=set(rels) - set([rel]), verbose=verbose)
    else:
        shuffle(terms)
        return word, anchor, rel, terms


# In[12]:


def connections(wordlist:list=WORDS, rels=RELS, k=4, verbose=False):
    wl = wordlist.copy()
    shuffle(wl)
    cats = []
    for i in range(k):
        word = wl.pop()
        success = None
        while not success:
            try:
                success, anchor, rel, terms = random_category(word, rels, verbose=verbose)
            except RuntimeError:
                word = wl.pop()
        cats.append((word, anchor, rel, remove_word(word, terms)))
    return cats     


# In[13]:


def print_category(word, anchor, rel, terms):
    if anchor == 'start':
        print(f'{word} {rel} {terms}')
    else:
        print(f'{terms} {rel} {word}')


# In[15]:



def create_game(categories):
    """
    A category is a (label string, list of terms)
    """
    HTML = """
    <!DOCTYPE html>
    <html>
        <head>
            <title>Connections</title>
            <style>
                #game-container {
                    margin: auto;
                    text-align: center;
                }

                #game-board {
                    margin: auto;
                    width: 400px;
                }

                .tile {
                    border: 2px solid lightgray;
                    height: 100px;
                    width: 100px;
                    user-select: none;
                    cursor: pointer;
                    border-radius: 5px;
                }

                .unselected:hover {
                    background-color: #EEE;
                }

                .selected:hover {
                    background-color: #999;
                }

                .selected {
                    background-color: gray;
                }

                .unselected {
                    background-color: white;
                }

                .game-row {
                    text-align: center;
                    height: 100px;
                }

            </style>
        </head>
        <body>
            <div id="game-container">
                <table id="game-board">
                    <tr class="game-row unrevealed">
                        <td class="tile unselected" onclick="toggle(this)"></td>
                        <td class="tile unselected" onclick="toggle(this)"></td>
                        <td class="tile unselected" onclick="toggle(this)"></td>
                        <td class="tile unselected" onclick="toggle(this)"></td>
                    </tr>
                    <tr class="game-row unrevealed">
                        <td class="tile unselected" onclick="toggle(this)"></td>
                        <td class="tile unselected" onclick="toggle(this)"></td>
                        <td class="tile unselected" onclick="toggle(this)"></td>
                        <td class="tile unselected" onclick="toggle(this)"></td>
                    </tr>
                    <tr class="game-row unrevealed">
                        <td class="tile unselected" onclick="toggle(this)"></td>
                        <td class="tile unselected" onclick="toggle(this)"></td>
                        <td class="tile unselected" onclick="toggle(this)"></td>
                        <td class="tile unselected" onclick="toggle(this)"></td>
                    </tr>
                    <tr class="game-row unrevealed">
                        <td class="tile unselected" onclick="toggle(this)"></td>
                        <td class="tile unselected" onclick="toggle(this)"></td>
                        <td class="tile unselected" onclick="toggle(this)"></td>
                        <td class="tile unselected" onclick="toggle(this)"></td>
                    </tr>
                </table>
                <br>
                <br>
                <br>
                <button onclick="scoreInput()">Submit</button>
            </div>
        </body>
        <script type="text/javascript">
            class Category {
                constructor(color, name, items) {
                    this.color = color;
                    this.name = name;
                    this.items = items;
                }

                size() {
                    return this.items.size;
                }

                // How many items differ between these categories?
                difference(cat2) {
                    if (cat2 instanceof Category && this.size() == cat2.size()) {
                        let diffs = 0;
                        for (const item of this.items.values()) {
                            if (!cat2.items.has(item)) {
                                diffs += 1;
                            }
                        }
                        return diffs;
                    } else {
                        // if the categories have different sizes, the question doesn't make sense.
                        return -1;
                    }
                }

                terms() {
                    return this.items.values();
                }

                toString() {
                    return this.terms().reduce((acc, term) => acc + ", " + term, "").substring(2);
                }
            };

            function toggle(tile) {
                if (tile.className == "tile unselected") {
                    // Try to add the tile, and select it.
                    if (terms.size < 4 && !terms.has(tile.innerHTML)) {
                        terms.add(tile.innerHTML);
                        tile.className = "tile selected";
                    }

                } else if (tile.className == "tile selected") {
                    // Reset the tile
                    tile.className = "tile unselected";
                    terms.delete(tile.innerHTML);
                }
            }

            // this fails if any of the category lengths mismatch!
            function scoreInput() {
                inputCat = new Category('gray', 'input', terms);

                if (terms.size < CAT1.size()) {
                    return "Invalid input!";
                }

                scoredCats = CATS.map((cat) => [inputCat.difference(cat), cat]);

                match = scoredCats.find((x) => x[0] == 0);
                oneAway = scoredCats.find((x) => x[0] == 1);

                if (match) {
                    window.alert("Correct!");
                    revealCategory(match[1]);

                } else if (oneAway) {
                    window.alert("One away!");
                } else {
                    window.alert("Try again!");
                }
            }

            function setUp(categories) {
                // get the terms and randomize
                allTerms = categories.reduce((acc, cat) => [...acc, ...cat.terms()], [])
                allTerms = shuffle(allTerms);

                let cells = document.getElementsByClassName("tile");
                for (let i = 0; i < cells.length; i++) {
                    cells[i].insertAdjacentHTML('afterBegin', allTerms[i]);
                }
            }

            // from https://www.geeksforgeeks.org/how-to-shuffle-an-array-using-javascript/
            function shuffle(array) { 
                return array.sort(()=>seededRandom()-0.5);
            } 

            // Seeded random is to ensure that all players have an equal playing field.
            // It is necessary to change the seed for each puzzle.
            // from https://stackoverflow.com/a/19303725
            let SEED = 81
            function seededRandom() {
                var x = Math.sin(SEED++) * 10000;
                return x - Math.floor(x);
            }

            const delay = ms => new Promise(res => setTimeout(res, ms));

            function revealCategory(cat) {
                revealTerms = cat.terms();
                rows = Array.from(document.getElementsByClassName("unrevealed"));
                targetRow = rows.shift();

                resetCells();

                // swap cells
                otherCells = []
                for (row of rows) {
                    cells = Array.from(row.children);
                    otherCells = [...otherCells, ...cells]
                }

                for (const cell of Array.from(targetRow.children)) {
                    if (!cat.items.has(cell.innerHTML)) {
                        for (const other of otherCells) {
                            if (cat.items.has(other.innerHTML)) {
                                swapElements(cell, other);
                            }
                        }
                    }
                }

                placeBanner(targetRow, cat);
            }

            function swapElements(obj1, obj2) {
                // create marker element and insert it where obj1 is
                var temp = document.createElement("div");
                obj1.parentNode.insertBefore(temp, obj1);

                // move obj1 to right before obj2
                obj2.parentNode.insertBefore(obj1, obj2);

                // move obj2 to right before where obj1 used to be
                temp.parentNode.insertBefore(obj2, temp);

                // remove temporary marker node
                temp.parentNode.removeChild(temp);
            }

            function removeAllChildren(elem) {
                while (elem.hasChildNodes()) {
                    elem.removeChild(elem.firstChild);
                }
            }

            function placeBanner(row, cat) {
                let catBanner = document.createElement('td');
                catBanner.innerHTML = cat.name + "<br />" + cat.toString();
                catBanner.style.background = cat.color;
                catBanner.colSpan = "4";
                row.className = "game-row revealed";
                removeAllChildren(row)
                row.appendChild(catBanner);
            }

            function resetCells() {
                terms.clear();
                let cells = Array.from(document.getElementsByClassName("selected"));
                cells.forEach((cell) => cell.className = "tile unselected ");
            }

            const purple = "mediumpurple";
            const blue = "deepskyblue";
            const green = "springgreen"
            const yellow = "gold";

            

            const CAT1 = new Category("mediumpurple", "Tower of ____", new Set(["hanoi", "babel", "london", "terror"]));
            const CAT2 = new Category("deepskyblue", "World Capitals", new Set(["lima", "paris", "seoul", "baghdad"]));
            const CAT3 = new Category("springgreen", "Negative Emotions", new Set(["jealousy", "fury", "sadness", "angst"]));
            const CAT4 = new Category("gold", "Beans", new Set(["pinto", "fava", "kidney", "green"]));

            // const CAT1a = new Category(purple, 'bourbon', 'tang', 'ptolemaic', 'umayyad');
            // const CAT2a = new Category(green, 'zest', 'spice', 'piquancy', 'kick');
            // const CAT3a = new Category(blue, 'rum', 'scotch', 'sake', 'mead');
            // const CAT4a = new Category(yellow, 'tahoe', 'victoria', 'baikal', 'superior');

            const CAT1b = new Category(purple, "Palindromes", new Set(["Racecar", "Kayak", "Malayalam", "Xanax"]));
            const CAT2b = new Category(green, "Unconventional Transport", new Set(["Canoe", "Go-kart", "Eighteen wheeler", "Hovercraft"]) );
            const CAT3b = new Category(blue,  "Languages of India", new Set(["Odia", "Sindhi", "Urdu", "Marathi"]));
            const CAT4b = new Category(yellow, "Medication Brand Names", new Set(["Viagra", "Ritalin", "Lyrica", "Otezla"]));

            
            const terms = new Set();

            const CAT1py = new Category("mediumpurple", <REPLACE_CAT1>);
            const CAT2py = new Category("deepskyblue", <REPLACE_CAT2>)
            const CAT3py = new Category("springgreen", <REPLACE_CAT3>)
            const CAT4py = new Category("gold", <REPLACE_CAT4>)

            CATS = [CAT1py, CAT2py, CAT3py, CAT4py];

            setUp(CATS);
        </script>
    </html>
    """
    
    for i, (label, terms) in enumerate(categories):
        term_string = ', '.join([f'"{term}"' for term in terms])
        HTML = HTML.replace(f'<REPLACE_CAT{i+1}>', f'"{label}", new Set([{term_string}])')
    return HTML
    
def render_html_string(html):
    with tempfile.NamedTemporaryFile(delete=False, suffix='.html') as tmp_file:
        tmp_file.write(html.encode('utf-8'))
        tmp_file_path = tmp_file.name
    print('Launching webpage...')
    webbrowser.open(f'file://{tmp_file_path}')

def main():
    game = connections(verbose=True)
    cats = []
    for word,anchor,rel,terms in game:
        if anchor == 'start':
            cat = (f'{word} {rel} _____', terms)
        else:
            cat = (f'_____ {rel} {word}', terms)
        cats.append(cat)
    
    html = create_game(cats)
    render_html_string(html)

if __name__ == '__main__':
    main()
import os
import pickle
import random
import time

import attr
import gin
import portalocker
from flask import Flask, render_template, request

from codenamer import Codenamer
from instance import Hint, Instance

CONF_EN_GLOVE = '''
Codenamer.wordlist_file = 'wordlist-en-10000-google-no-swears.txt'
Codenamer.wordlist_minlen = 4
Codenamer.wordlist_limit = 2000
Codenamer.codenames_file = 'codenames-en-bgg.txt'
Codenamer.codenames_minlen = 4
Codenamer.codenames_limit = None
Codenamer.model_name = 'glove-twitter-100'
Codenamer.model_prefix = ''
Codenamer.name = 'en-bgg-google-glove-100'
'''

CONF_EN_CONCEPTNET = '''
Codenamer.wordlist_file = 'wordlist-en-10000-google-no-swears.txt'
Codenamer.wordlist_minlen = 4
Codenamer.wordlist_limit = 2000
Codenamer.codenames_file = 'codenames-en-bgg.txt'
Codenamer.codenames_minlen = 4
Codenamer.codenames_limit = None
Codenamer.model_name = 'conceptnet-numberbatch-17-06-300'
Codenamer.model_prefix = '/c/en/'
Codenamer.name = 'en-bgg-google-conceptnet-300'
'''

CONF_EN_EMPTY = '''
Codenamer.wordlist_file = 'wordlist-en-10000-google-no-swears.txt'
Codenamer.wordlist_minlen = 4
Codenamer.wordlist_limit = 5000
Codenamer.codenames_file = 'codenames-en-bgg.txt'
Codenamer.codenames_minlen = 3
Codenamer.codenames_limit = None
Codenamer.model_name = 'model-empty-100.txt'
Codenamer.model_prefix = ''
Codenamer.name = 'en-bgg-google-empty-100'
'''

CONF_CS_CONCEPTNET = '''
Codenamer.wordlist_file = 'wordlist-cs-syn-lemma.txt'
Codenamer.wordlist_minlen = 5
Codenamer.wordlist_limit = 3000
Codenamer.codenames_file = 'wordlist-cs-syn-lemma.txt'
Codenamer.codenames_minlen = 5
Codenamer.codenames_limit = 1000
Codenamer.model_name = 'conceptnet-numberbatch-17-06-300'
Codenamer.model_prefix = '/c/cs/'
Codenamer.name = 'cs-syn-syn-conceptnet-300'
'''

CONF_CS_CONCEPTNET_LOCAL = CONF_CS_CONCEPTNET + '''
Codenamer.model_name = 'conceptnet-numberbatch-17-06-cs-300.txt'
'''

# Nuber of hints to display
TOP = 15
TOP_GUESS = 5
# Number of words to generate (pos, neut, neg, killer)
RANDOM_COUNTS = (6, 5, 5, 1)
RANDOM_GUESS_COUNTS = (5, 4, 4, 1)

# Use given config
#gin.parse_config(CONF_CS_CONCEPTNET_LOCAL)
gin.parse_config(CONF_EN_CONCEPTNET)

CODENAMER = Codenamer()

app = Flask(__name__)

@app.route('/guess', methods=('GET', 'POST'))
def guess():
    voted = False
    if request.method == 'POST':
        inst = Instance.from_form(request.form)
        log_vote(inst)
        voted = True
    inst = Instance.gen_random(CODENAMER.wordlist, counts=RANDOM_GUESS_COUNTS)
    CODENAMER.create_hints(inst, n=TOP_GUESS)
    cols = inst.hint_cols()
    name = gin.query_parameter('Codenamer.name')
    # Shuffle columns keeping BAD first
    perm = list(range(len(cols)))
    p1 = perm[1:]
    random.shuffle(p1)
    perm[1:] = p1
    return render_template("guess.html", inst=inst, name=name, perm=perm, cols=cols, voted=voted, nick=inst.nickname)


@app.route('/', methods=('GET', 'POST'))
def hints():
    inst = Instance()
    voted = False
    if request.method == 'POST':
        inst = Instance.from_form(request.form)
        if 'b_random' in request.form:
            inst = Instance.gen_random(CODENAMER.wordlist, counts=RANDOM_COUNTS)
        if 'b_given' in request.form or 'b_random' in request.form:
            CODENAMER.create_hints(inst, n=TOP)
            inst.hints.insert(0, Hint("", 0.0))
            pass
        elif 'b_vote' in request.form:
            log_vote(inst)
            voted = True
            pass
        else:
            raise Exception('Unknown button in POST')
    cols = inst.hint_cols()
    name = gin.query_parameter('Codenamer.name')
    return render_template("hints.html", inst=inst, name=name, cols=cols, voted=voted, nick=inst.nickname)


def log_vote(instance, log_file=None, guess=False):
    if log_file is None:
        log_file = 'votes-' + gin.query_parameter('Codenamer.name') + ('-guess' if guess else '') + '.json'
    with portalocker.Lock(log_file) as f:
        f.write(instance.to_json() + "\n")
        f.flush()
        os.fsync(f.fileno())

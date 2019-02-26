import pickle
import random
import sqlite3
import time
import gin

import attr
from flask import Flask, render_template, request

from codenamer import Codenamer
from instance import Hint, Instance


CONF_TMPL = '''
Codenamer.wordlist_file = ''
Codenamer.wordlist_minlen = 4
Codenamer.wordlist_limit = 5000
Codenamer.codenames_file = ''
Codenamer.codenames_minlen = 5
Codenamer.codenames_limit = 1000
Codenamer.model_name = ''
Codenamer.model_prefix = ''
Codenamer.name = ''
'''

CONF_EN_GLOVE = '''
Codenamer.wordlist_file = 'wordlist-en-10000-google-no-swears.txt'
Codenamer.wordlist_minlen = 4
Codenamer.wordlist_limit = 5000
Codenamer.codenames_file = 'codenames-en-bgg.txt'
Codenamer.codenames_minlen = 3
Codenamer.codenames_limit = None
Codenamer.model_name = 'glove-twitter-100'
Codenamer.model_prefix = ''
Codenamer.name = 'en-bgg-google-glove-100'
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

CONF_CS_CONCEPTNET_LOCAL = '''
Codenamer.wordlist_file = 'wordlist-cs-syn-lemma.txt'
Codenamer.wordlist_minlen = 5
Codenamer.wordlist_limit = 3000
Codenamer.codenames_file = 'wordlist-cs-syn-lemma.txt'
Codenamer.codenames_minlen = 5
Codenamer.codenames_limit = 1000
Codenamer.model_name = 'conceptnet-numberbatch-17-06-cs-300.txt'
Codenamer.model_prefix = '/c/cs/'
Codenamer.name = 'cs-syn-syn-conceptnet-300'
'''

CONF_CS_EMPTY = '''
Codenamer.wordlist_file = 'wordlist-cs-syn-lemma.txt'
Codenamer.wordlist_minlen = 5
Codenamer.wordlist_limit = 3000
Codenamer.codenames_file = 'wordlist-cs-syn-lemma.txt'
Codenamer.codenames_minlen = 5
Codenamer.codenames_limit = 1000
Codenamer.model_name = 'model-empty-100.txt'
Codenamer.model_prefix = ''
Codenamer.name = 'cs-syn-syn-empty-100'
'''

TOP = 15
gin.parse_config(CONF_CS_CONCEPTNET_LOCAL)

CODENAMER = Codenamer()

app = Flask(__name__)

@app.route('/guess', methods=('GET', 'POST'))
def guess():
    voted = False
    nick = ""
    if request.method == 'POST':
        inst = Instance.from_form(request.form)
        nick = request.form['nick']
        log_vote(request, inst)
        voted = True
    inst = Instance.gen_random(CODENAMER.wordlist, counts=(5, 4, 4, 1))
    CODENAMER.create_hints(inst, n=5)
    cols = inst.hint_cols()
    perm = list(range(len(cols)))
    random.shuffle(perm[1:])
    name = gin.query_parameter('Codenamer.name')
    return render_template("guess.html", inst=inst, name=name, perm=perm, cols=cols, voted=voted, nick=nick)


@app.route('/', methods=('GET', 'POST'))
def hints():
    inst = Instance()
    voted = False
    if request.method == 'POST':
        inst = Instance.from_form(request.form)
        if 'b_random' in request.form:
            inst = Instance.gen_random(CODENAMER.wordlist)
        if 'b_given' in request.form or 'b_random' in request.form:
            CODENAMER.create_hints(inst, n=TOP)
            inst.hints.insert(0, Hint("", 0.0))
            pass
        elif 'b_vote' in request.form:
            log_vote(request, inst)
            voted = True
            pass
        else:
            raise Exception('Unknown button in POST')
    cols = inst.hint_cols()
    print(inst)
    name = gin.query_parameter('Codenamer.name')
    return render_template("hints.html", inst=inst, name=name, cols=cols, voted=voted)


def open_log_db(dbname):
    db = sqlite3.connect(dbname)
    c = db.cursor()
    c.execute("CREATE TABLE IF NOT EXISTS vote_log (id PRIMARY KEY, ts NUMERIC, ip_addr TEXT, nick TEXT, instance BLOB)")
    db.commit()
    return db


def log_vote(request, instance, dbname=None):
    if dbname is None:
        dbname = 'votes-' + gin.query_parameter('Codenamer.name') + '.sqlite3'
    db = open_log_db(dbname)
    c = db.cursor()
    c.execute("INSERT INTO vote_log (ts, ip_addr, nick, instance) VALUES (?, ?, ?, ?)",
        (time.time(), request.remote_addr, request.form.get('nick', None), pickle.dumps(instance)))
    db.commit()

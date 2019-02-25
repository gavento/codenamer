import sqlite3
import time
import pickle

from flask import Flask, render_template, request

from codenamer import Codenamer
from instance import Hint, Instance



TOP = 15
CODENAMES_FILE = "codenames-en-bgg.txt"
WORDLIST_FILE = "wordlist-en-10000-google-no-swears.txt"

#MODEL_NAME = "model-empty-100.txt"
MODEL_NAME = "glove-twitter-25"
#MODEL_NAME = "conceptnet-numberbatch-17-06-300"

NAME = "en_c-bgg_w-gogle_m-" + MODEL_NAME
LOG_DB_FILE = "votes_" + NAME + ".sqlite3"

CODENAMER = Codenamer(CODENAMES_FILE, WORDLIST_FILE, MODEL_NAME, wordlist_limit=2000)

app = Flask(__name__)

@app.route('/', methods=('GET', 'POST'))
def hello():
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
            log_vote(LOG_DB_FILE, request, inst)
            voted = True
            pass
        else:
            raise Exception('Unknown button in POST')
    cols = inst.hint_cols()
    print(inst)
    return render_template("page.html", inst=inst, name=NAME, cols=cols, voted=voted)


def open_log_db(dbname):
    db = sqlite3.connect(dbname)
    c = db.cursor()
    c.execute("CREATE TABLE IF NOT EXISTS vote_log (id PRIMARY KEY, ts NUMERIC, ip_addr TEXT, nick TEXT, instance BLOB)")
    db.commit()
    return db


def log_vote(dbname, request, instance):
    db = open_log_db(dbname)
    c = db.cursor()
    c.execute("INSERT INTO vote_log (ts, ip_addr, nick, instance) VALUES (?, ?, ?, ?)",
        (time.time(), request.remote_addr, request.form.get('nick', None), pickle.dumps(instance)))
    db.commit()

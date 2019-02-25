from flask import Flask, render_template, request

from codenamer import Codenamer
from instance import Hint, Instance

app = Flask(__name__)

TOP = 20
NAME = "en-bgg-google-twitter-25"
CODENAMES_FILE = "codenames-en-bgg.txt"
WORDLIST_FILE = "wordlist-en-bgg.txt"
MODEL_NAME = "glove-twitter-25"

CODENAMER = Codenamer(CODENAMES_FILE, WORDLIST_FILE, MODEL_NAME)

@app.route('/', methods=('GET', 'POST'))
def hello():
    inst = Instance()
    voted = False
    if request.method == 'POST':
        inst = Instance.from_form(request.form)
        if 'b_random' in request.form:
            inst = Instance.gen_random(WORDLIST)
        if 'b_given' in request.form or 'b_random' in request.form:
            CODENAMER.create_hints(inst, n=TOP)
            inst.hints.insert(0, Hint("", 0.0))
            pass
        elif 'b_vote' in request.form:
            # TODO: store votes
            voted = True
            pass
        else:
            raise Exception('Unknown button in POST')
    cols = [(c, "") for c in inst.hint_cols()]
    print(inst)
    return render_template("page.html", inst=inst, name=NAME, cols=cols, voted=voted)

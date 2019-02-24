#from codenamer import Codenamer
from flask import Flask, request, render_template, g
import attr

app = Flask(__name__)

#CODENAMER = Codenamer('cc.cs.300.bin', 'cs_50k.txt', word_limit=None)
TOP = 20

@attr.s
class Hint:
    word = attr.ib(factory=str)
    score = attr.ib(default=0.0)
    bad = attr.ib(default=False)
    matches = attr.ib(factory=dict)

@attr.s
class Instance:
    w_pos = attr.ib(factory=list)
    w_neut = attr.ib(factory=list)
    w_neg = attr.ib(factory=list)
    w_kill = attr.ib(factory=list)
    hints = attr.ib(factory=list)

    def hint_cols(self):
        return ['BAD'] + self.w_pos + self.w_kill

    @classmethod
    def from_form(cls, form):
        print(list(form.items()))
        def parse_w(s):
            return s.lower().replace(',', ' ').split()
        s = cls(
            parse_w(form['w_pos']),
            parse_w(form['w_neut']),
            parse_w(form['w_neg']),
            parse_w(form['w_kill']),
            []
        )
        cols = s.hint_cols()
        for i in range(1000):
            if 'h_{}'.format(i) not in form:
                break
            vals = set(c for ci, c in enumerate(cols) if form.get('cb_{}_{}'.format(i, ci), '') == "1")
            s.hints.append(Hint(
                form['h_{}'.format(i)],
                form['s_{}'.format(i)],
                'BAD' in vals,
                vals.difference(['BAD']),
            ))
        return s

    @classmethod
    def gen_random(cls, words):
        return cls() # TODO


WORDLIST = []  # TODO: wordlist
NAME = "test"

@app.route('/', methods=('GET', 'POST'))
def hello():
    inst = Instance()
    voted = False
    if request.method == 'POST':
        inst = Instance.from_form(request.form)
        if 'b_random' in request.form:
            inst = Instance.gen_random(WORDLIST)
        if 'b_given' in request.form or 'b_random' in request.form:
            # TODO: generate
            #try:
            #g.msg = CODENAMER.get_hint_msg(w_wanted, w_other, w_avoid, top=TOP)
            inst.hints = [Hint("testword", 4.2)]
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


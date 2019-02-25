import random

import attr


@attr.s
class Hint:
    word = attr.ib(factory=str)
    score = attr.ib(default=0.0)
    bad = attr.ib(default=False)
    matches = attr.ib(factory=set)
    msg = attr.ib(default='')

@attr.s
class Instance:
    RANDOM_WORD_COUNTS = (7, 8, 9, 1)

    w_pos = attr.ib(factory=list)
    w_neut = attr.ib(factory=list)
    w_neg = attr.ib(factory=list)
    w_kill = attr.ib(factory=list)
    hints = attr.ib(factory=list)

    def hint_cols(self):
        l = [('BAD', "c_bad")]
        for w in self.w_pos:
            l.append((w, "c_pos"))
        for w in self.w_neut:
            l.append((w, "c_neut"))
        for w in self.w_neg:
            l.append((w, "c_neg"))
        for w in self.w_kill:
            l.append((w, "c_kill"))
        return l

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
        w = random.sample(words, sum(cls.RANDOM_WORD_COUNTS))
        def take(l, n):
            x = l[:n]
            l[:n] = []
            return x
        ws = [take(w, i) for i in cls.RANDOM_WORD_COUNTS]
        return cls(*ws)

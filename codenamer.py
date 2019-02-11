import numpy as np
import zipfile
import fastText
import numpy as np

class Codenamer:
    def __init__(self, model_fname, words_filename, word_limit=None):
        self.model_filename = model_filename
        self.model = fastText.FastText.load_model(self.model_filename)
        self.dim = self.model.get_dimension()
        self.words_filename = words_filename
        with open(self.words_filename, 'rt') as f:
            self.words = [l.split()[0] for l in f.readlines()[:word_limit]]
        self.words_vecs = self.map_words(self.words)

    def map_words(self, words):
        return np.array([self.model.get_word_vector(w) for w in words])

    def candidate_score(self, word_vec, wanted_vecs, other_vecs, avoid_vecs):
        "return (score, matched_words)"
        return (0.0, []) # TODO

    def get_ranked_candidates(self, wanted_words, other_words, avoid_words):
        "return [(score, matched_words, word)] sorted desc by score."
        wanted_vecs = self.map_words(wanted_words)
        other_vecs = self.map_words(other_words)
        avoid_vecs = self.map_words(avoid_words)
        scores = [] # (score, matches, word)
        for w, v in zip(self.words, self.words_vecs):
            score, matches = self.candidate_score(v, wanted_vecs, other_vecs, avoid_vecs)
            scores.append((score, matches, w))
        scores.sort(reverse=True)
        return scores

    def get_hint_msg(self, wanted_words, other_words, avoid_words, top=10):
        cands = get_ranked_candidates(self, wanted_words, other_words, avoid_words):
        cand_descs = ["{:6.2g} {:15s} (matches {}: {})".format(s, w, len(m), ' '.join(m)) for s, m, w in cands[:top]]
        return "Top {} candidates (out of {}) for\n+ wanted: {}\n- other: {}\n! avoid: {}\n{}".format(
            top, len(cands), ' '.join(wanted_words), ' '.join(other_words), ' '.join(avoid_words),
            '\n'.join(cand_descs))

def load_model_txt(fname):
    with open(fname, "rt") as stream:
        m = gensim.models.KeyedVectors.load_word2vec_format(stream, binary=False, unicode_errors='replace')
    return m


def load_zip(fname):
    with zipfile.ZipFile(fname, "r") as archive:
        stream = archive.open("model.txt")
        m = gensim.models.KeyedVectors.load_word2vec_format(stream, binary=False, unicode_errors='replace')
    return m


def find_hint_msg(w_wanted, w_other, w_avoid, model):
    msg = []
    def lookup(ws):
        res = []
        for w in ws:
            try:
                v = model.get_vector(w)
                res.append(v)
            except KeyError:
                msg.append("W: {!r} not found in map, ignoring".format(w))
        return res
    v_wanted = lookup(w_wanted)
    v_other = lookup(w_other)
    v_avoid = lookup(w_avoid)
    if not v_wanted:
        msg.append("E: no wanted word vectors")
    else:
        msg.append("Most appropriate word and scores:")
        ms = model.most_similar(positive=w_wanted, negative=w_avoid+w_other)
        for w, ws in ms:
            msg.append("  {:10f}  {}".format(ws, w))

        msg.append("Most appropriate word and scores (cosmul):")
        ms = model.most_similar_cosmul(positive=w_wanted, negative=w_avoid+w_other)
        for w, ws in ms:
            msg.append("  {:10f}  {}".format(ws, w))

    return '\n'.join(msg)



if __name__ == '__main__':
    m = load_model_txt("test_model.txt")



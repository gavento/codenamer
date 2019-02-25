import time
import os

import gensim
import gensim.downloader
import numpy as np

from instance import Hint, Instance


class Codenamer:
    def __init__(self, codenames_file, wordlist_file, model_name, *, model_strip_prefix='', codenames_limit=None, wordlist_limit=None, wordlist_minlen=3):
        self.codenames_file = codenames_file
        with open(self.codenames_file, 'rt') as f:
            self.codenames = f.readlines()[:codenames_limit]
        self.wordlist_file = wordlist_file
        with open(self.wordlist_file, 'rt') as f:
            self.wordlist = [l.split()[0] for l in f.readlines() if len(l.split()[0]) > wordlist_minlen][:wordlist_limit]

        self.model_name = model_name
        if os.path.exists(self.model_name):
            self.model = gensim.models.KeyedVectors.load_word2vec_format(self.model_name)
        else:
            self.model = gensim.downloader.load(self.model_name)
        self.dim = self.model.vector_size

        self.wordlist_vecs = self.map_words(self.wordlist)

    def map_words(self, words):
        "return L2-normalized word vectors as ndarray"
        if not words:
            return np.zeros((0, self.dim))
        vlist = []
        for w in words:
            try:
                v = self.model.get_vector(w)
                v = v / np.linalg.norm(v)
            except KeyError:
                v = np.zeros(self.dim)
            vlist.append(v)
        return np.array(vlist, dtype=np.float32)

    def create_hints(self, instance, n=10):
        v_pos = self.map_words(instance.w_pos)
        v_neut = self.map_words(instance.w_neut)
        v_neg = self.map_words(instance.w_neg)
        v_kill = self.map_words(instance.w_kill)
        hints = []
        for w, v in zip(self.wordlist, self.wordlist_vecs):
            score, matches, msg = self.candidate_score(instance, v, v_pos, v_neut, v_neg, v_kill)
            hints.append(Hint(w, score, False, matches, msg))
        hints.sort(reverse=True, key=lambda h: h.score)
        instance.hints = hints[:n]

    def candidate_score(self, instance, v_cand, v_pos, v_neut, v_neg, v_kill):
        return (1.0, [], "")
        # TODO
        "return (score, matched_words, msg)"
        sim_pos = v_pos.dot(v_cand)
        sim_neut = v_neut.dot(v_cand)
        sim_neg = v_neg.dot(v_cand)
        sim_kill = v_kill.dot(v_cand)

        min_wanted = np.min(wanted_cos)
        max_other = np.max(other_cos)
        max_avoid = np.max(avoid_cos)
        max_neg = max(max_other, max_avoid)

        matches = []
        for wi, wc in enumerate(wanted_cos):
            if wc ** 2 > max_neg:
                matches.append(wi)

        score = min_wanted - max_neg
        if max_avoid > 0.0:
            score -= 1.0
        msg = "max_other={} max_avoid={} wanted_cos={}".format(max_avoid, max_avoid, wanted_cos)
        return (score, matches, msg) # TODO

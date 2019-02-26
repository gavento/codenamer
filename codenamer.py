import bz2
import os
import pickle
import time

import gensim
import gensim.downloader
import gin
import numpy as np

from instance import Hint, Instance

@gin.configurable
class Codenamer:
    def __init__(self, codenames_file, wordlist_file, model_name, *, model_prefix='', codenames_limit=None, codenames_minlen=3, wordlist_limit=None, wordlist_minlen=3, name="unknown"):
        def load_list(fname, minlen, limit, prefix=""):
            r = []
            with open(fname, 'rt') as f:
                for l in f.readlines():
                    if limit is not None and len(r) >= limit:
                        break
                    w = l.split()[0]
                    if len(w) > minlen and w.isalpha():
                        r.append(w)                    
            return r

        self.codenames_file = codenames_file
        self.codenames = load_list(self.codenames_file, codenames_minlen, codenames_limit)
        self.wordlist_file = wordlist_file
        self.wordlist = load_list(self.wordlist_file, wordlist_minlen, wordlist_limit)

        self.model_name = model_name
        self.model_prefix = model_prefix
        self.name = name

        cached_name = "cached-model-" + self.model_name + ".bz"
        if os.path.exists(cached_name):
            print("Loading cached model from", cached_name)
            with bz2.BZ2File(cached_name, 'r') as f:
                self.model = pickle.load(f)
        else:
            print("Loading model", self.model_name)
            if os.path.exists(self.model_name):
                self.model = gensim.models.KeyedVectors.load_word2vec_format(self.model_name)
            else:
                self.model = gensim.downloader.load(self.model_name)
            print("Storing model to", cached_name)
            with bz2.BZ2File(cached_name, 'w') as f:
                pickle.dump(self.model, f)

        self.dim = self.model.vector_size
        self.wordlist_vecs = self.map_words(self.wordlist)

    def map_words(self, words):
        "return L2-normalized word vectors as ndarray"
        if not words:
            return np.zeros((0, self.dim))
        vlist = []
        for w in words:
            try:
                v = self.model.get_vector(self.model_prefix + w)
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
            score, matches, msg = self.candidate_score(instance, w, v, v_pos, v_neut, v_neg, v_kill)
            hints.append(Hint(w, score, False, matches, msg))
        hints.sort(reverse=True, key=lambda h: h.score)
        instance.hints = hints[:n]

    def candidate_score(self, instance, word, v_cand, v_pos, v_neut, v_neg, v_kill):
        "return (score, matched_positive_words, msg)"
        if np.linalg.norm(v_cand) < 0.1:
            return (-1000.0, [], "No vectors for word")
        sim_pos = v_pos.dot(v_cand)
        sim_neut = v_neut.dot(v_cand)
        sim_neg = v_neg.dot(v_cand)
        sim_kill = v_kill.dot(v_cand)

        max_neut = np.max(sim_neut)
        max_neg = np.max(sim_neg)
        max_kill = np.max(sim_kill)
        max_avoid = max(max_neut, max_neg, max_kill)

        matches = []
        score = 0.0
        for w, sim in zip(instance.w_pos, sim_pos):
            if sim > max_avoid:
                matches.append(w)
                score += sim - max_avoid
            if w == word:
                score -= 100
        msg = "matches: {}, max_neut/neg/kill: {} {} {}, sim_pos: {}".format(
            ' '.join(matches), max_neut, max_neg, max_kill, sim_pos)
        return (score, matches, msg)

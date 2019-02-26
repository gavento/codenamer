# Codenames hinting AI

An exploration of AI for the game of [Codenames](https://boardgamegeek.com/boardgame/178900/codenames).

* Simple models using various vector embeddings, matching directly on cosine similarity.
* Web interface to use the models in play and collect data on acceptable hints and matches.
* Future plans: incorporate collected statistics into the match weighting.

## Running

```sh
pip install numpy gensim flask attrs
./download_data.sh  # (needed for some combinations)
FLASK_ENV=development FLASK_APP=server.py flask run
```

Models take a *long* time to load (up to few minutes) on every start. Then go to:

* http://localhost:5000/ to generate hints and see debug mesages (also allows voting).
* http://localhost:5000/guess to vote on best matches.

## Data sources

Wordlists and codename lists are loaded as one word per line (whitespace separated), the rest is ignored. Limiting word count on loading takes a prefix (so you may want to have them sorted by frequency).

* `codenames-en-bgg.txt` from [BoardGameGeek forums](https://boardgamegeek.com/thread/1383878/word-list-future-moderators-codenames-games). More can be found [here](https://boardgamegeek.com/thread/1413932/word-list) and [here](https://boardgamegeek.com/filepage/136292/codenames-word-list).
* `wordlist-cs-opensubtitles.txt` from [Wiktionary](https://en.wiktionary.org/wiki/Wiktionary:Frequency_lists/Czech_wordlist) (all word forms).
* `wordlist-cs-syn-lemma.txt` from [Czech national corpus](https://wiki.korpus.cz/doku.php/seznamy:srovnavaci_seznamy#download) (only lemmas).
* `wordlist-en-gutenberg.txt` from [Wiktionary](https://en.wiktionary.org/wiki/Wiktionary:Frequency_lists/PG/2006/04/1-10000).
* `wordlist-en-10000-google-no-swears.txt` from [here](https://github.com/first20hours/google-10000-english).
* `model-empty-100.txt` for testing purposes.

Licenses to these data may vary, see the sources.

### Gensim word embedding models

Many English language models are directly downloadable by gensim are at [gensim-data repo](https://github.com/RaRe-Technologies/gensim-data#models).

Note that the [conceptnet-numberbatch](https://github.com/commonsense/conceptnet-numberbatch) multilang model (also included in gensim models) uses lang-specific prefixes of the form `/c/en/`, `/c/cs/` etc.

## Licence

MIT
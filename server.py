from codenamer import Codenamer
from flask import Flask, request, render_template_string, g

app = Flask(__name__)

tmpl = """
<!doctype html><html><head>
<title>Codenamer</title>
<link rel="stylesheet" href="{{ url_for('static', filename='style.css') }}">
<style>
body {margin: 1em 3em;}
.entry {margin: 1em 0;}
.entry textarea {width: 100%; height: 6em;}
.entry label {padding: 10pt 0;}
.msg {width: 100%; margin:1em 1em;}

</style>
</head><body>
    <h1>Codenamer - {{ g.lang }}</h1>
    <div>
    Message:<br>
    <pre class="msg">{{ g.msg }}</pre>
    </div>
    <div>
    Enter space-separated words:
    <form method="post" class="entry">
        <label for="w_wanted">Wanted words</label><br>
        <textarea name="w_wanted" id="w_wanted">{{ g.w_wanted }}</textarea><br>
        <label for="w_other">Neutral words</label><br>
        <textarea name="w_other" id="w_other">{{ g.w_other }}</textarea><br>
        <label for="w_avoid">Avoid words</label><br>
        <textarea name="w_avoid" id="w_avoid">{{ g.w_avoid }}</textarea><br>
        <input type="submit" value="Find hint">
    </form>
    </div>
</body></html>
"""

CODENAMER = Codenamer('cc.cs.300.bin', 'cs_50k.txt', word_limit=1000)
TOP = 30

def parse_w(s):
    return s.lower().replace(',', ' ').split()

@app.route('/', methods=('GET', 'POST'))
def hello():
    g.msg = ""
    g.lang = 'czech'
    if request.method == 'POST':
        w_wanted = parse_w(request.form['w_wanted'])
        w_other = parse_w(request.form['w_other'])
        w_avoid = parse_w(request.form['w_avoid'])
        try:
            g.msg = CODENAMER.get_hint_msg(w_wanted, w_other, w_avoid, top=TOP)
        except Exception as e:
            g.msg = "Error:\n\n" + str(e)
        g.w_wanted = ' '.join(w_wanted)
        g.w_other = ' '.join(w_other)
        g.w_avoid = ' '.join(w_avoid)
    return render_template_string(tmpl, g=g)


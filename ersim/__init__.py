from flask import Flask
from flask import g
from flask.ext.login import LoginManager
import sqlite3
import os

app = Flask(__name__)
app.config.from_object(__name__)
login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = "/login"
login_manager.login_message = "Hi, please log in."

# Load default config and override config from an environment variable
app.config.update(dict(
    DATABASE=os.path.join(app.root_path, 'extra/test.sqlite'),
    DEBUG=False,
    SECRET_KEY='\x977n\xfcrG4\x06\xed\xf0\xd3\'\x1dh"Q\xc4\xc0\n\xf0\xd9i_\xd4',
    USERNAME='admin',
    PASSWORD='default'
))
app.config.from_envvar('FLASKR_SETTINGS', silent=True)

def connect_db():
    print app.config['DATABASE']
    rv = sqlite3.connect(app.config['DATABASE'])
    rv.row_factory = sqlite3.Row
    return rv

def get_db():
    if not hasattr(g, 'sqlite_db'):
        g.sqlite_db = connect_db()
    return g.sqlite_db

def query_db(query, args=(), one=False):
    cur = get_db().execute(query, args)
    rv = cur.fetchall()
    cur.close()
    return (rv[0] if rv else None) if one else rv

def commit_db(query, args=()):
    conn = get_db()
    cur = conn.execute(query, args)
    conn.commit()

def lastid_db():
    return query_db("SELECT last_insert_rowid()", (), True)[0]

@app.teardown_appcontext
def close_db(error):
    if hasattr(g, 'sqlite_db'):
        g.sqlite_db.close()

from ersim import views
from ersim import login

if __name__ == "__main__":
	app.run(debug=app.config[DEBUG])

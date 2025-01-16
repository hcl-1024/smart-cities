from flask import Flask, g, render_template, request, redirect, url_for
import sqlite3

app = Flask(__name__)

DATABASE = 'people.db'

def get_db():
    db = getattr(g, '_database', None)
    if db is None:
        db = g._database = sqlite3.connect(DATABASE)
    return db

@app.teardown_appcontext
def close_connection(exception):
    db = getattr(g, '_database', None)
    if db is not None:
        db.close()

@app.route('/')
def index():
    db = get_db()
    cursor = db.cursor()
    cursor.execute("SELECT * FROM people")
    people = cursor.fetchall()
    cursor.close()
    return render_template('index.html', people=people)

@app.route('/add', methods=['POST'])
def add():
    db = get_db()
    cursor = db.cursor()
    name = request.form['name']
    cursor.execute("INSERT INTO people (name) VALUES (?)", (name,))
    db.commit()
    cursor.close()
    return redirect(url_for('index'))

if __name__ == '__main__':
    app.run(debug=True)
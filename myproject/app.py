from flask import Flask, render_template, request, redirect, url_for
import sqlite3
import datetime

baseurl = "/smartcities"
app = Flask(__name__, static_url_path=baseurl)

# Function to connect to the database
def get_db_connection():
    conn = sqlite3.connect('database.db')
    conn.row_factory = sqlite3.Row
    return conn

# Create the database and table if it doesn't exist
def init_db():
    conn = get_db_connection()
    conn.execute('''
        CREATE TABLE IF NOT EXISTS entries (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            start TEXT NOT NULL, 
            end TEXT, 
            time INTEGER
        )
    ''')
    conn.commit()
    conn.close()

@app.route(baseurl + '/', methods=['GET', 'POST'])
def index():
    init_db()
    if request.method == 'POST':
        name = request.form['name']
        now = datetime.datetime.now()
        now = now.strftime('%Y-%m-%d %H:%M:%S')


        conn = get_db_connection()

        repeat = conn.execute('SELECT * FROM entries WHERE name = (?) AND end IS NULL', (name,)).fetchone()
        if(repeat): 
            return "Someone has already entered that name! "

        conn.execute('INSERT INTO entries (name, start) VALUES (?, ?)', (name, now))
        conn.commit()
        conn.close()
        

        return redirect(url_for('timer', name=name))
    

    conn = get_db_connection()
    entries = conn.execute('SELECT * FROM entries ORDER BY time ASC').fetchall()
    conn.close()
    
    return render_template('index.html', entries=entries[:10])

@app.route(baseurl + '/timer/<name>', methods=['GET'])
def timer(name):
    conn = get_db_connection()
    entry = conn.execute('SELECT * FROM entries WHERE name = (?) AND end IS NULL', (name,)).fetchone()
    conn.close()
    
    if not entry:
        return "No active timer found for this user."

    return render_template('timer.html', name=name, start_time=entry['start'])

@app.route(baseurl + '/finish', methods=['GET', 'POST'])
def finish():
    init_db()
    now = datetime.datetime.now()
    now = now.strftime('%Y-%m-%d %H:%M:%S')

    if request.method == "POST": 
        name = request.form['name']
        conn = get_db_connection()
        exist = conn.execute('SELECT * FROM entries WHERE name = (?) AND end IS NULL', (name,)).fetchone()
        if(not exist):
            return "Sorry, this user does not exist or you need to make a new account after you've finished before! "

        start_time = conn.execute('SELECT * FROM entries WHERE name = (?) AND end IS NULL', (name,)).fetchone()
        start_time = start_time[2]
        start = datetime.datetime.strptime(start_time, "%Y-%m-%d %H:%M:%S")
        now = datetime.datetime.strptime(now, "%Y-%m-%d %H:%M:%S")
        c = now - start
        time = c.total_seconds()
        conn.execute('UPDATE entries SET time = (?), end = (?) WHERE name = (?) AND end IS NULL', (time, now, name, ))
        rank = conn.execute('''
        SELECT 
            (SELECT COUNT(*) 
            FROM entries AS e2 
            WHERE e2.time <= e1.time) as row_number, 
            e1.*
        FROM entries AS e1
        WHERE end = ?
        ORDER BY time
        ''', (now,)).fetchone()
        rank = rank[0]
        conn.commit()
        conn.close()
        rank = str(rank)
        ranking = "You scored number " + rank + "!"
        return ranking
        
    conn = get_db_connection()
    entries = conn.execute('SELECT * FROM entries ORDER BY time ASC').fetchall()
    conn.close()

    return render_template('finish.html', entries=entries[:10])

if __name__ == '__main__':
    init_db()  
    app.run(debug=True)

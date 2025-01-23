from flask import Flask, render_template, request, redirect
import sqlite3
import datetime

app = Flask(__name__)

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
            end INTEGER, 
            time INTEGER
        )
    ''')
    conn.commit()
    conn.close()

@app.route('/', methods=['GET', 'POST'])
def index():
    init_db()
    if request.method == 'POST':
        name = request.form['name']
        print(name)
        now = datetime.datetime.now()

        # Insert the new entry into the database
        conn = get_db_connection()

        repeat = conn.execute('SELECT * FROM entries WHERE name = (?)', (name,)).fetchone()
        if(repeat): 
            return "Someone has already entered that name! "

        conn.execute('INSERT INTO entries (name, start) VALUES (?, ?)', (name, now))
        conn.commit()
        conn.close()
        
        return redirect('/')
    
    # Fetch all entries to display
    conn = get_db_connection()
    entries = conn.execute('SELECT * FROM entries').fetchall()
    conn.close()
    
    return render_template('index.html', entries=entries)

if __name__ == '__main__':
    init_db()  # Initialize the database
    app.run(debug=True)
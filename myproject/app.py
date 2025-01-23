from flask import Flask, render_template, request, redirect
import sqlite3

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
            email TEXT NOT NULL
        )
    ''')
    conn.commit()
    conn.close()

@app.route('/', methods=['GET', 'POST'])
def index():
    if request.method == 'POST':
        name = request.form['name']
        email = request.form['email']
        
        # Insert the new entry into the database
        conn = get_db_connection()
        conn.execute('INSERT INTO entries (name, email) VALUES (?, ?)', (name, email))
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
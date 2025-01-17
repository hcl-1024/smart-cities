from flask import Flask, render_template, request, redirect, url_for
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///people.db'
db = SQLAlchemy(app)
migrate = Migrate(app, db)

class Person(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(80), unique=True, nullable=False)
    finished = db.Column(db.Boolean)

@app.route('/')
def index():
    people = Person.query.filter_by(finished=False)
    return render_template('index.html', people=people)

@app.route('/add', methods=['POST'])
def add():
    name = request.form['name']
    # Check if the name already exists in the database
    existing_person = Person.query.filter_by(name=name).first()

    if existing_person:
        return "Name already exists in the database!"
    else:
        new_person = Person(name=name)
        db.session.add(new_person)
        db.session.commit()
        return redirect(url_for('index'))

@app.route('/finish', methods=['POST'])
def finish(): 
    name = request.form['name']
    finished_person = Person.query.filter_by(name=name).first()

    if(not finished_person):
        return "Please Enter a Valid Name"
    else:
        finished_person.finished = True

if __name__ == '__main__':
    db.create_all()
    app.run(debug=True)
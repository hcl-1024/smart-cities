from flask import Flask, render_template, request, redirect, url_for

app = Flask(__name__)

@app.route('/')
def index():
    print("placeholder")
    #Get the list of people
    #people = Person.query.filter_by(finished=False)
    #return render_template('index.html', people=people)

@app.route('/add', methods=['POST'])
def add():
    name = request.form['name']
    # Check if the name already exists in the database
    #existing_person = Person.query.filter_by(name=name).first()

    #if existing_person:
        #return "Name already exists in the database!"
    #else:
        #add new person to database
        #return redirect(url_for('index'))

@app.route('/finish', methods=['POST'])
def finish(): 
    name = request.form['name']

    #if(not finished_person):
        #return "Please Enter a Valid Name"
    #else:
        #say the person is finished
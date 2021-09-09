#import typing_extensions
from logging import debug
from flask import Flask, render_template, request, redirect, url_for, session, flash, jsonify
from flaskext.mysql import MySQL
import re
from numpy import insert
from pymysql import connect
import os
import pydicom
from pynetdicom import AE
from flask_mysqldb import MySQLdb


app = Flask(__name__)

# Change this to your secret key (can be anything, it's for extra protection)
app.secret_key = 'your secret key'

# Enter your database connection details below
app.config['MYSQL_DATABASE_HOST'] = 'localhost'
app.config['MYSQL_DATABASE_USER'] = 'root'
app.config['MYSQL_DATABASE_PASSWORD'] = 'root'
app.config['MYSQL_DATABASE_DB'] = 'dicom'
app.config['MYSQL_DATABASE_PORT'] = 3306

# Intialize MySQL
mysql = MySQL()
mysql.init_app(app)

print(mysql)

@app.route('/')
def begin():
    return render_template('begin.html')

# Login-----------------------------------------------------------------------
@app.route('/login/', methods=['GET', 'POST'])
def login():
    # Output message if something goes wrong...
    msg = ''
        # Check if "username" and "password" POST requests exist (user submitted form)
    if request.method == 'POST' and 'username' in request.form and 'password' in request.form:
        # Create variables for easy access
        username = request.form['username']
        password = request.form['password']

                # Check if account exists using MySQL
        conn = mysql.connect()
        cursor = conn.cursor()
        cursor.execute('SELECT * FROM accounts WHERE username = %s AND password = %s', (username, password,))
        conn.commit()
        # Fetch one record and return result
        account = cursor.fetchone()
        print(account)
                # If account exists in accounts table in out database
        if account:
            # Create session data, we can access this data in other routes
            session['loggedin'] = True
            session['id'] = account[0]
            session['username'] = account[1]
            # Redirect to home page
            if session['id']==10 and session['username']=='admin':
                return redirect(url_for('administrator'))
            else:
                return redirect(url_for('home'))
        else:
            # Account doesnt exist or username/password incorrect
            msg = 'Incorrect username/password!'

    return render_template('index.html', msg='')

# http://localhost:5000/pythinlogin/home - this will be the home page, only accessible for loggedin users
@app.route('/home', methods = ['GET', 'POST'])
def home():
    # Check if user is loggedin
    if 'loggedin' in session:
        # User is loggedin show them the home page
        return render_template('home.html', username=session['username'])
    # User is not loggedin redirect to login page
    return redirect(url_for('login'))

@app.route('/administrator', methods = ['POST','GET'])
def administrator():
    # Check if user is loggedin
    if 'loggedin' in session:
        # User is loggedin show them the home page
        return render_template('administrator.html', username=session['username'])
    # User is not loggedin redirect to login page
    if request.method == 'POST':
        if request.form['submit_button'] == 'sendFiles':

            return render_template('administrator.html')
    elif request.method == 'GET':
        return render_template('administrator.html')

    return redirect(url_for('login'))


@app.route('/profile_admin')
def profile_admin():
    # Check if user is loggedin
    if 'loggedin' in session:
        # We need all the account info for the user so we can display it on the profile page
        conn = mysql.connect()
        cursor = conn.cursor()
        cursor.execute('SELECT * FROM accounts WHERE id = %s', (session['id'],))
        account = cursor.fetchone()
        # Show the profile page with account info
        return render_template('profile_admin.html', account=account)
    # User is not loggedin redirect to login page
    return redirect(url_for('login'))

@app.route('/pythonlogin/logout')
def logout():
    # Remove session data, this will log the user out
    session.pop('loggedin', None)
    session.pop('id', None)
    session.pop('username', None)
    # Redirect to login page
    return redirect(url_for('login'))

@app.route('/profile')
def profile():
    # Check if user is loggedin
    if 'loggedin' in session:
        # We need all the account info for the user so we can display it on the profile page
        conn = mysql.connect()
        cursor = conn.cursor()
        cursor.execute('SELECT * FROM accounts WHERE id = %s', (session['id'],))
        account = cursor.fetchone()
        # Show the profile page with account info
        return render_template('profile.html', account=account)
    # User is not loggedin redirect to login page
    return redirect(url_for('login'))

#Admin: Look and edit Users---------------------------------------------
@app.route('/users')
def users():
    if 'loggedin' in session:
        conn = mysql.connect()
        cursor = conn.cursor()
        cursor.execute('SELECT * FROM accounts')
        conn.commit()
        usuarios = cursor.fetchall()
        usuarios=list(usuarios)
        for i in usuarios:
            if i[1]=="admin":
                usuarios.remove(i)

        return render_template('users.html', usuarios=usuarios)
    
    return redirect(url_for('login'))

@app.route('/delete/<string:id>')
def delete_contact(id):
    conn = mysql.connect()
    cursor = conn.cursor()
    cursor.execute('DELETE FROM accounts WHERE id = {0}'.format(id))
    conn.commit()
    usuarios = cursor.fetchall()
    flash('Contact Removed Succesfully!')
    return redirect(url_for('users'))    

@app.route('/edit/<id>')
def edit(id):
    cur = mysql.connect().cursor()
    cur.execute('SELECT * FROM accounts WHERE id = %s',(id))
    mysql.connect().commit()
    data = cur.fetchone()
    return render_template('edit_users.html', i = data)


@app.route('/update/<id>', methods = ['POST'])
def update(id):
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        email = request.form['email']
        conn = mysql.connect()
        cursor = conn.cursor()
        cursor.execute('UPDATE accounts SET username = %s, password = %s,email = %s WHERE id = %s', (username, password,email,id))
        conn.commit()
        flash('Account update Succesfully')
        return redirect(url_for('users'))

    #Register------------------------------------------------------
    # http://localhost:5000/pythinlogin/register - this will be the registration page, we need to use both GET and POST requests
@app.route('/register', methods=['GET', 'POST'])
def register():
    # Output message if something goes wrong...
    msg = ''
    # Check if "username", "password" and "email" POST requests exist (user submitted form)
    if request.method == 'POST' and 'username' in request.form and 'password' in request.form and 'email' in request.form:
        # Create variables for easy access
        username = request.form['username']
        password = request.form['password']
        email = request.form['email']
                # Check if account exists using MySQL
        conn = mysql.connect()
        cursor = conn.cursor()
        cursor.execute('SELECT * FROM accounts WHERE username = %s AND password = %s', (username, password,))
        cursor.execute('SELECT * FROM accounts WHERE username = %s', (username,))
        conn.commit()
        account = cursor.fetchone()
        # If account exists show error and validation checks
        if account:
            msg = 'Account already exists!'
        elif not re.match(r'[^@]+@[^@]+\.[^@]+', email):
            msg = 'Invalid email address!'
        elif not re.match(r'[A-Za-z0-9]+', username):
            msg = 'Username must contain only characters and numbers!'
        elif not username or not password or not email:
            msg = 'Please fill out the form!'
        else:
            # Account doesnt exists and the form data is valid, now insert new account into accounts table
            cursor.execute('INSERT INTO accounts VALUES (NULL, %s, %s, %s)', (username, password, email,))
            conn.commit()
            msg = 'Registro Exitoso!' 
            return redirect(url_for('administrator'))
    elif request.method == 'POST':
        # Form is empty... (no POST data)
        msg = 'Please fill out the form!'
    # Show registration form with message (if any)
    return render_template('register.html', msg=msg)


    #Targets---------------------------------------------------
@app.route('/targets')
def targets():
    if 'loggedin' in session:
        conn = mysql.connect()
        cursor = conn.cursor()
        cursor.execute('SELECT * FROM targets')
        conn.commit()
        target = cursor.fetchall()
        return render_template('targets.html', target=target)
    
    return redirect(url_for('login'))

@app.route('/regist_targets', methods=['GET', 'POST'])
def regist_targets():
    # Output message if something goes wrong...
    msg = ''
    if request.method == 'POST' and 'targetName' in request.form and 'ip' in request.form and 'port' in request.form and 'source' in request.form and 'target' in request.form and 'contact' in request.form:
        # Create variables for easy access
        targetName = request.form['targetName']
        ip = request.form['ip']
        port = request.form['port']
        source = request.form['source']
        target = request.form['target']
        contact = request.form['contact']
                # Check if account exists using MySQL
        conn = mysql.connect()
        cursor = conn.cursor()
        cursor.execute('SELECT * FROM targets WHERE ip = %s AND target= %s', (ip, target,))
        cursor.execute('SELECT * FROM targets WHERE ip = %s', (ip,))
        conn.commit()
        account = cursor.fetchone()
        # If account exists show error and validation checks
        if account:
            msg = 'Account already exists!'
        elif not re.match(r'[^@]+@[^@]+\.[^@]+', contact):
            msg = 'Invalid email address!'
        elif not re.match(r'[A-Za-z0-9]+', ip):
            msg = 'ip must contain only characters and numbers!'
        elif not ip or not source or not contact or not target:
            msg = 'Please fill out the form!'
        else:
            # Account doesnt exists and the form data is valid, now insert new account into accounts table
            cursor.execute('INSERT INTO targets VALUES (NULL, %s, %s, %s, %s, %s, %s)', (targetName,ip, contact, port, source, target))
            conn.commit()
            msg = 'Registro Exitoso!' 
            return redirect(url_for('targets'))
    elif request.method == 'POST':
        # Form is empty... (no POST data)
        msg = 'Please fill out the form!'
    # Show registration form with message (if any)
    return render_template('regist_targets.html', msg=msg)

@app.route('/deleteTarget/<string:id>')
def delete_target(id):
    conn = mysql.connect()
    cursor = conn.cursor()
    cursor.execute('DELETE FROM targets WHERE id = {0}'.format(id))
    conn.commit()
    target = cursor.fetchall()
    flash('Target Removed Succesfully!')
    return redirect(url_for('targets'))

@app.route('/editTarget/<id>')
def edit_target(id):
    cur = mysql.connect().cursor()
    cur.execute('SELECT * FROM targets WHERE id = %s',(id))
    mysql.connect().commit()
    datas = cur.fetchone()
    return render_template('edit_targets.html', i = datas)

@app.route('/updateTarget/<id>', methods = ['POST'])
def update_target(id):
    if request.method == 'POST':
        targetName = request.form['targetName']
        ip = request.form['ip']
        port = request.form['port']
        contact = request.form['contact']
        source = request.form['source']
        target = request.form['target']
        conn = mysql.connect()
        cursor = conn.cursor()
        cursor.execute('UPDATE targets SET targetName = %s, ip = %s,port = %s,contact = %s,source = %s,target = %s WHERE id = %s', (targetName, ip, port,contact, source, target, id))
        conn.commit()
        flash('Target update Succesfully')
        return redirect(url_for('targets'))


#Rules-------------------------------------------------------------------------------------------------
@app.route('/rules')
def rules():
    if 'loggedin' in session:
        conn = mysql.connect()
        cursor = conn.cursor()
        cursor.execute('SELECT * FROM rules')
        conn.commit()
        rule = cursor.fetchall()
        return render_template('rules.html', rule=rule)
    
    return redirect(url_for('login'))

@app.route('/regist_rules', methods=['GET', 'POST'])
def regist_rules():
    # Output message if something goes wrong...
    msg = ''
    if request.method == 'POST' and 'about' in request.form and 'modality' in request.form and 'target' in request.form and 'contact' in request.form and 'coment' in request.form:
        # Create variables for easy access
        about = request.form['about']
        modality = request.form['modality']
        target = request.form['target']
        contact = request.form['contact']
        coment = request.form['coment']
                # Check if account exists using MySQL
        conn = mysql.connect()
        cursor = conn.cursor()
        cursor.execute('SELECT * FROM rules WHERE about = %s AND modality =%s AND target= %s ', (about,modality, target,))
        cursor.execute('SELECT * FROM rules WHERE about = %s', (about,))
        conn.commit()
        account = cursor.fetchone()
        # If account exists show error and validation checks
        if account:
            msg = 'Account already exists!'
        elif not re.match(r'[^@]+@[^@]+\.[^@]+', contact):
            msg = 'Invalid email address!'
        elif not re.match(r'[A-Za-z0-9]+', target):
            msg = 'ip must contain only characters and numbers!'
        elif not about or not target or not contact or not target:
            msg = 'Please fill out the form!'
        else:
            # Account doesnt exists and the form data is valid, now insert new account into accounts table
            cursor.execute('INSERT INTO rules VALUES (NULL, %s,%s, %s, %s, %s)', (about,modality,target, contact, coment))
            conn.commit()
            msg = 'Registro Exitoso!' 
            return redirect(url_for('rules'))
    elif request.method == 'POST':
        # Form is empty... (no POST data)
        msg = 'Please fill out the form!'
    # Show registration form with message (if any)
    return render_template('regist_rules.html', msg=msg)

@app.route('/deleteRules/<string:id>')
def delete_rule(id):
    conn = mysql.connect()
    cursor = conn.cursor()
    cursor.execute('DELETE FROM rules WHERE id = {0}'.format(id))
    conn.commit()
    rule = cursor.fetchall()
    flash('Removed Succesfully!')
    return redirect(url_for('rules'))

@app.route('/editRules/<id>')
def edit_rule(id):
    cur = mysql.connect().cursor()
    cur.execute('SELECT * FROM rules WHERE id = %s',(id))
    mysql.connect().commit()
    reglas = cur.fetchone()
    return render_template('editrules.html', i = reglas)

@app.route('/updateRules/<id>', methods = ['POST'])
def update_rules(id):
    if request.method == 'POST':
        about = request.form['about']
        modality = request.form['modality']
        target = request.form['target']
        contact = request.form['contact']
        coment = request.form['coment']
        
        conn = mysql.connect()
        cursor = conn.cursor()
        cursor.execute('UPDATE rules SET about = %s, target = %s, modality = %s,contact = %s,coment = %s WHERE id = %s', (about,modality,target, contact, coment, id))
        conn.commit()
        flash('update Succesfully')
        return redirect(url_for('rules'))


@app.route('/upload/',  methods=['GET', 'POST'])
def upload():
    # Llame al archivo dicom local
    folder_path = r"C:\Users\Andres\AppData\Local\Programs\Python\Python39\Lib\site-packages\pynetdicom\apps\qrscp\DICOM\DicomFiles"
    list = os.listdir(folder_path)
    for i in list:
        file_name = list(i)
        #file_path = os.path.join(folder_path,file_name)
        #print(file_path)
        ds = pydicom.dcmread(file_name)
        imageType=ds.ImageType
        sOPClassUID=ds.SOPClassUID
        studyDate=ds.StudyDate
        studyTime=ds.StudyTime
        modality=ds.Modality
        manufacturer=ds.Manufacturer
        institutionName=ds.InstitutionName
        studyDescription=ds.StudyDescription
        institutionalDepartmentName=ds.InstitutionalDepartmentName
        patientSex=ds.PatientSex
        patientAge=ds.PatientAge
        patientAddress=ds.PatientAddress
        pregnancyStatus=ds.PregnancyStatus
        bodyPartExamined=ds.BodyPartExamined
        protocolName=ds.ProtocolName
        studyID=ds.StudyID
        seriesNumber=ds.SeriesNumber
        acquisitionNumber=ds.AcquisitionNumber
        imageComments=ds.ImageComments
        photometricInterpretation=ds.PhotometricInterpretation
        studyStatusID=ds.StudyStatusID
        studyPriorityID=ds.StudyPriorityID
        currentPatientLocation=ds.CurrentPatientLocation
        requestingService=ds.RequestingService

            # Check if account exists using MySQL
        conn = mysql.connect()
        cursor = conn.cursor()
        #Now insert new metadata into patients table
        cursor.execute('INSERT INTO patients VALUES (NULL, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)', (modality, bodyPartExamined, studyDate,studyTime,manufacturer,sOPClassUID,institutionName,institutionalDepartmentName,patientSex,patientAge,patientAddress,pregnancyStatus,protocolName,studyID,seriesNumber,acquisitionNumber,imageComments,photometricInterpretation,studyStatusID,studyPriorityID,currentPatientLocation,requestingService,imageType,studyDescription ))
        conn.commit()
        patient = cursor.fetchall()
    return render_template('upload.html', msg='')

@app.route('/administrator', methods = ['GET'])
def main():
    conn = mysql.connect()
    cursor = conn.cursor(MySQLdb.cursors.DictCursor)
    result = cursor.execute("SELECT * FROM patients ORDER BY id")
    patients = cursor.fetchall()
    return render_template('administrator.html', patients=patients)

@app.route("/consults",methods=["POST","GET"])
def carbrand():  
    conn = mysql.connect()
    cursor = conn.cursor()
    cur = mysql.connect.cursor(MySQLdb.cursors.DictCursor)
    if request.method == 'POST':
        category_id = request.form['category_id'] 
        print(category_id)
        result = cur.execute("SELECT * FROM patients WHERE studyDescription = %s ORDER BY modality ASC", [category_id] )
        carmodel = cur.fetchall()  
        OutputArray = []
        for row in carmodel:
            outputObj = {
                'id': row['id'],
                'name': row['studyDescription']}
            OutputArray.append(outputObj)
    return jsonify(OutputArray)

if __name__ == '__main__':
    app.run(debug=True)

if __name__ == '__main__':
    #app.run(host= '0.0.0.0')
    app.run(debug=True)
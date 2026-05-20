from flask import Flask, render_template, request, redirect, session, url_for
from pymongo import MongoClient
from dotenv import load_dotenv
import os
import bcrypt

load_dotenv()

app = Flask(__name__)
app.secret_key = os.getenv('SECRET_KEY')

#Mongo
client = MongoClient(os.getenv('MONGO_URI'))
db = client['flask_login']
usuarios = db['usuarios']

#uploads
UPLOAD_FOLDER = 'static/uploads'
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

@app.route('/')
def home():
    if "usuario" not in session:
        return redirect(url_for('login'))
    return render_template(
        'home.html',
        usuario=session['usuario']
        )
    
#Registro
@app.route('/register', methods=['GET', 'POST'])
def register ():
    if request.method == 'POST':
        nombre = request.form['nombre']
        apellido1 = request.form['apellido1']
        apellido2 = request.form['apellido2']
        correo = request.form['correo']
        username = request.form['username']
        password = request.form['password']
        
        foto = request.files['foto']
        
        usuario_existente = usuarios.find_one({
            'username': username
        })
        
        if usuario_existente:
            return 'El nombre de usuario ya existe. Por favor, elige otro.'
        
        foto_path = ''
        
        if foto:
            foto_path = os.path.join(
                app.config['UPLOAD_FOLDER'],
                foto.filename
            )
            foto.save(foto_path)
            
            #Contraseña
            password_hash = bcrypt.hashpw(
                password.encode('utf-8'),
                bcrypt.gensalt()
            )
            
            #Guardar
            usuarios.insert_one({
                'nombre': nombre,
                'apellido1': apellido1,
                'apellido2': apellido2,
                'correo': correo,
                'username': username,
                'password': password_hash,
                'foto': foto.filename
            })
            
            return redirect(url_for('login'))
    return render_template('register.html')

#Login
@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        
        usuario = usuarios.find_one({
            'username': username
        })
        if not usuario:
            return redirect(url_for('register'))
        if bcrypt.checkpw(
            password.encode('utf-8'),
            usuario['password']
        ):
            session['usuario'] = {
                'nombre': usuario['nombre'],
                'username': usuario['username'],
                'foto': usuario['foto']
            }
            
            return redirect(url_for('home'))
        else:
            return 'Contraseña incorrecta'
    return render_template('login.html')
    #Logout
@app.route('/logout')
def logout():
    session.clear()
    return redirect(url_for('login'))
if __name__ == '__main__':
    app.run(debug=True)

#mongodb+srv://keniarcctpa_db_kenia:sSTZ0y7pd4YOMnA2@usuarios.m2sijsu.mongodb.net/?appName=usuarios
#SECRET_KEY=kenia12345
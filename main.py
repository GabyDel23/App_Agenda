from flask import Flask,session,render_template, redirect, url_for,request
from flask_sqlalchemy import SQLAlchemy

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI']='sqlite:///contactos.sqlite'
app.config['SECRET_KEY']='5dfc118a7256f56d0fc1fcbef8759ccd'

db= SQLAlchemy(app)

# base de dato
class User(db.Model):
    id=db.Column(db.Integer,primary_key=True,autoincrement=True)
    email=db.Column(db.Text,nullable=False,unique=True)
    nombre=db.Column(db.Text,nullable=False)
    password=db.Column(db.Text,nullable=False)
    
class Contact(db.Model):
    id=db.Column(db.Integer,primary_key=True, autoincrement=True)
    nombre=db.Column(db.Text,nullable=False)
    primer_app=db.Column(db.Text,nullable=False)
    segundo_apm=db.Column(db.Text,nullable=False)
    telefono=db.Column(db.Text,nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)  # Relación con User

    
with app.app_context():
    db.create_all()
    #try:
        #obj=User(email='Gabrieladelgado@gmail.com', password='12345',nombre='Gabriela Delgado')
        #db.session.add(obj)
        #db.session.commit()
    #except:
        #pass

@app.route("/", methods=['GET', 'POST'])
def index():
    if 'user_id' not in session:
        return redirect(url_for('login'))  # Redirigir si no hay sesión activa

    if request.method == 'POST':
        nombre = request.form.get('nombre')
        primer_app = request.form.get('primer_app')
        segundo_apm = request.form.get('segundo_apm')
        telefono = request.form.get('telefono')

        if nombre and primer_app and segundo_apm and telefono:
            obj = Contact(
                nombre=nombre,
                primer_app=primer_app,
                segundo_apm=segundo_apm,
                telefono=telefono,
                user_id=session['user_id']  # Asocia el contacto con el usuario actual
            )
            db.session.add(obj)
            db.session.commit()
    # Obtener solo los contactos del usuario actual
    lista_Contact = Contact.query.filter_by(user_id=session['user_id']).all()
    return render_template('index.html', lista_Contact=lista_Contact)

  

# Rutas Seguras
@app.route("/change_password", methods=['GET', 'POST'])
def change_password():
    if 'user_id' not in session:
        return redirect(url_for('login'))  # Redirigir si no hay sesión activa
    if request.method == 'POST':
        current_password = request.form['current_password']
        new_password = request.form['new_password']
        # Obtener el usuario actual
        user = User.query.get(session['user_id'])
        # Verificar la contraseña actual
        if user and user.password == current_password:
            user.password = new_password  # Actualizar la contraseña
            db.session.commit()
            return redirect(url_for('index'))
        else:
            return render_template('change_password.html')

    return render_template('change_password.html')
    

@app.route("/add", methods=['GET', 'POST'])
def add_task():
    if 'user_id' not in session:
        return redirect(url_for('login'))  # Redirigir si no hay sesión activa

    if request.method == 'POST':
        nombre = request.form.get('nombre')
        primer_app = request.form.get('primer_app')
        segundo_apm = request.form.get('segundo_apm')
        telefono = request.form.get('telefono')

        if nombre and primer_app and segundo_apm and telefono:
            obj = Contact(
                nombre=nombre,
                primer_app=primer_app,
                segundo_apm=segundo_apm,
                telefono=telefono,
                user_id=session['user_id']  # Asocia el contacto con el usuario actual
            )
            db.session.add(obj)
            db.session.commit()
            return redirect(url_for('index'))

    return render_template('add.html')



@app.route("/update/<int:id>", methods=['GET', 'POST'])
def update_task(id):
    obj = Contact.query.get(id)
    if obj.user_id != session['user_id']:
        return redirect(url_for('index'))  # Redirigir si el contacto no pertenece al usuario

    if request.method == 'POST':
        # Obtener los nuevos valores del formulario
        obj.nombre = request.form['nombre']
        obj.primer_app = request.form['primer_app']
        obj.segundo_apm = request.form['segundo_apm']
        obj.telefono = request.form['telefono']
        # Guardar cambios en la base de datos
        db.session.commit()
        return redirect(url_for('index'))

    return render_template('update.html', contact=obj)



@app.route("/delete/<int:id>")
def delete_task(id):
    contact = Contact.query.get(id)
    if contact and contact.user_id == session['user_id']:  # Verifica que el contacto pertenezca al usuario
        db.session.delete(contact)
        db.session.commit()
    return redirect(url_for('index'))


@app.route("/profile")
def profile():
    return render_template('profile.html')

#rutas No seguras 
@app.route("/error")
def error():
    return render_template('error.html')

@app.route("/login", methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        # Obtener el email y la contraseña del formulario
        email = request.form['email']
        password = request.form['password']  # Asegúrate de que la contraseña se almacene en texto plano

        # Buscar el usuario en la base de datos
        user = User.query.filter_by(email=email, password=password).first()

        if user:
            # Si el usuario existe, guardar la información en la sesión
            session['name'] = user.nombre
            session['email'] = user.email
            session['user_id'] = user.id  # Opcional, si necesitas el ID del usuario
            return redirect(url_for('index'))
        else:
            # Si el usuario no existe, mostrar un mensaje de error
            error = "Usuario o contraseña incorrectos"
            return render_template('login.html', error=error)

    return render_template('login.html')


@app.route("/logout")
def logout():
    session.clear()
    return redirect(url_for('login'))


@app.route("/register", methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        email = request.form['email']
        nombre = request.form['nombre']
        password = request.form['password']
        # Verificar si el correo electrónico ya existe
        existing_user = User.query.filter_by(email=email).first()
        if existing_user:
            return render_template('register.html')

        # Crear un nuevo usuario
        new_user = User(email=email, nombre=nombre, password=password)
        db.session.add(new_user)
        db.session.commit()
        return redirect(url_for('login'))

    return render_template('register.html')



# Punto de Entrada
if __name__ == "__main__":
    app.run(debug=True)
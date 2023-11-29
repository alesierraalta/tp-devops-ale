from flask import Flask, request, render_template, redirect, url_for
from flask import Response
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager, UserMixin
from flask_login import login_user, login_required, logout_user, current_user
from werkzeug.security import generate_password_hash, check_password_hash
from sqlalchemy.orm import sessionmaker
from prometheus_client import generate_latest, Counter, Histogram
from prometheus_client import CONTENT_TYPE_LATEST

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///notas.db'
app.config['SECRET_KEY'] = 'tu_llave_secreta_aqui'

db = SQLAlchemy(app)
login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = 'login'

# Métricas de ejemplo
REQUEST_COUNT = Counter('request_count', 'App Request Count')
REQUEST_LATENCY = Histogram('request_latency_seconds', 'Request latency')


@app.route('/metrics')
def metrics():
    return Response(generate_latest(), mimetype=CONTENT_TYPE_LATEST)


class Usuario(UserMixin, db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(100), unique=True)
    password_hash = db.Column(db.String())

    def set_password(self, password):
        self.password_hash = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.password_hash, password)


class Nota(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    contenido = db.Column(db.String(1000))
    usuario_id = db.Column(db.Integer, db.ForeignKey('usuario.id'))


# Create the database
with app.app_context():
    db.create_all()


@login_manager.user_loader
def load_user(user_id):
    Session = sessionmaker(bind=db.engine)
    session = Session()
    return session.get(Usuario, int(user_id))


@app.route('/registro', methods=['GET', 'POST'])
def registro():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        existente = Usuario.query.filter_by(username=username).first()
        if existente:
            return redirect(url_for('registro'))
        nuevo = Usuario(username=username)
        nuevo.set_password(password)
        db.session.add(nuevo)
        db.session.commit()
        return redirect(url_for('login'))
    return render_template('registro.html')


@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        user = Usuario.query.filter_by(username=username).first()
        if user and user.check_password(password):
            login_user(user)
            return redirect(url_for('index'))
    return render_template('login.html')


@app.route('/')
@login_required
def index():
    notas = Nota.query.filter_by(usuario_id=current_user.id).all()
    return render_template('index.html', notas=notas)


@app.route('/add', methods=['POST'])
@login_required
def add():
    contenido_nota = request.form['nota'].strip()
    if not contenido_nota:
        return redirect(url_for('index'))
    try:
        nueva = Nota(contenido=contenido_nota, usuario_id=current_user.id)
        db.session.add(nueva)
        db.session.commit()
    except Exception:
        # Manejar la excepción
        return redirect(url_for('index'))
    return redirect(url_for('index'))


@app.route('/edit/<int:nota_id>', methods=['GET', 'POST'])
@login_required
def edit(nota_id):
    nota = Nota.query.filter_by(usuario_id=current_user.id, id=nota_id).first()
    if nota:
        if request.method == 'POST':
            contenido_nota = request.form['nota'].strip()
            if not contenido_nota:
                return redirect(url_for('index'))
            try:
                nota.contenido = contenido_nota
                db.session.commit()
            except Exception:
                # Manejar la excepción
                return redirect(url_for('index'))
            return redirect(url_for('index'))
        return render_template('edit.html', nota=nota)
    return redirect(url_for('index'))


@app.route('/delete/<int:nota_id>', methods=['GET'])
@login_required
def delete(nota_id):
    nota = Nota.query.filter_by(usuario_id=current_user.id, id=nota_id).first()
    if nota:
        try:
            db.session.delete(nota)
            db.session.commit()
        except Exception:
            # Manejar la excepción
            pass  # O registrar la excepción
    return redirect(url_for('index'))


@app.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect(url_for('login'))


if __name__ == '__main__':
    with app.app_context():
        db.create_all()
    app.run(debug=True)

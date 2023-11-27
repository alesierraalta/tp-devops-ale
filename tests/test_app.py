import unittest
import sys
import os
#from flask_sqlalchemy import SQLAlchemy
from app import app, db, Usuario, Nota

# Agregar el directorio de la aplicación al sys.path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), os.path.pardir)))

class FlaskBlogTestCase(unittest.TestCase):

    def setUp(self):
        app.config['TESTING'] = True
        app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///:memory:'
        app.config['WTF_CSRF_ENABLED'] = False
        self.app = app.test_client()

        with app.app_context():
            db.create_all()
            # Crear y añadir un usuario de prueba a la base de datos
            usuario_prueba = Usuario(username='testuser')
            usuario_prueba.set_password('testpassword')
            db.session.add(usuario_prueba)
            db.session.commit()

    def tearDown(self):
        with app.app_context():
            db.session.remove()
            db.drop_all()

    def login(self, username='testuser', password='testpassword'):
        # Método auxiliar para iniciar sesión
        return self.app.post('/login', data={
            'username': username,
            'password': password
        }, follow_redirects=True)

    def logout(self):
        # Método auxiliar para cerrar sesión
        return self.app.get('/logout', follow_redirects=True)

    def test_login_logout(self):
        rv = self.login()
        response_text = rv.data.decode('utf-8')
        print("Respuesta después del inicio de sesión:", response_text)  # Agregar impresión para depuración
        assert 'Bienvenido, testuser' in response_text or 'Cerrar Sesión' in response_text
        rv = self.logout()
        response_text = rv.data.decode('utf-8')
        print("Respuesta después del cierre de sesión:", response_text)  # Agregar impresión para depuración
        assert 'Bienvenido, testuser' not in response_text and 'Cerrar Sesión' not in response_text

    def test_edit_note(self):
        # Prueba para verificar la edición de una nota
        with app.app_context():
            self.login()
            self.app.post('/add', data={'nota': 'Nota para editar'}, follow_redirects=True)
            nota = Nota.query.filter_by(contenido='Nota para editar').first()
            rv = self.app.post(f'/edit/{nota.id}', data={'nota': 'Nota editada'}, follow_redirects=True)
            response_text = rv.data.decode('utf-8')
            print("Respuesta después de editar nota:", response_text)  # Agregar impresión para depuración
            assert b'Nota editada' in rv.data

    def test_delete_note(self):
        # Prueba para verificar la eliminación de una nota
        with app.app_context():
            self.login()
            self.app.post('/add', data={'nota': 'Nota para borrar'}, follow_redirects=True)
            nota = Nota.query.filter_by(contenido='Nota para borrar').first()
            rv = self.app.get(f'/delete/{nota.id}', follow_redirects=True)
            response_text = rv.data.decode('utf-8')
            print("Respuesta después de borrar nota:", response_text)  # Agregar impresión para depuración
            assert b'Nota para borrar' not in rv.data

if __name__ == '__main__':
    unittest.main()

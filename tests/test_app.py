import unittest
import sys
import os
from app import app, db, Usuario, Nota
# Ajustar las importaciones al inicio del archivo
sys.path.append(os.path.abspath(os.path.join(
    os.path.dirname(__file__), os.path.pardir)))

class FlaskBlogTestCase(unittest.TestCase):

    def setUp(self):
        app.config['TESTING'] = True
        app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///:memory:'
        app.config['WTF_CSRF_ENABLED'] = False
        self.app = app.test_client()

        with app.app_context():
            db.create_all()
            usuario_prueba = Usuario(username='testuser')
            usuario_prueba.set_password('testpassword')
            db.session.add(usuario_prueba)
            db.session.commit()

    def tearDown(self):
        with app.app_context():
            db.session.remove()
            db.drop_all()

    def login(self, username='testuser', password='testpassword'):
        return self.app.post('/login', data={
            'username': username, 'password': password
        }, follow_redirects=True)

    def logout(self):
        return self.app.get('/logout', follow_redirects=True)

    def test_login_logout(self):
        rv = self.login()
        response_text = rv.data.decode('utf-8')
        print("Response after logging in:", response_text)
        assert 'Cerrar Sesión' in response_text
        rv = self.logout()
        response_text = rv.data.decode('utf-8')
        assert 'Cerrar Sesión' not in response_text

    def test_edit_note(self):
        with app.app_context():
            self.login()
            response = self.app.post('/add', data={'nota': 'Note to edit'},
                                     follow_redirects=True)
            print("Response after adding note for edit:",
                  response.data.decode('utf-8'))
            note = Nota.query.filter_by(contenido='Note to edit').first()
            if note:
                rv = self.app.post(f'/edit/{note.id}',
                                   data={'nota': 'Edited note'},
                                   follow_redirects=True)
                response_text = rv.data.decode('utf-8')
                print("Response after editing note:", response_text)
                assert 'Edited note' in response_text
            else:
                self.fail("No se encontró la nota para editar")

    def test_delete_note(self):
        with app.app_context():
            self.login()
            response = self.app.post('/add', data={'nota': 'Note to delete'},
                                     follow_redirects=True)
            print("Response after adding note for delete:",
                  response.data.decode('utf-8'))
            note = Nota.query.filter_by(contenido='Note to delete').first()
            if note:
                rv = self.app.get(f'/delete/{note.id}',
                                  follow_redirects=True)
                response_text = rv.data.decode('utf-8')
                print("Response after deleting note:", response_text)
                assert 'Note to delete' not in response_text
            else:
                self.fail("No se encontró la nota para eliminar")


if __name__ == '__main__':
    unittest.main()

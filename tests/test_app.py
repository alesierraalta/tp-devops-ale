import unittest
import sys
import os
# from flask_sqlalchemy import SQLAlchemy
from app import app, db, Usuario, Nota

# Add the app directory to sys.path
sys.path.append(os.path.abspath(os.path.join(
    os.path.dirname(__file__), os.path.pardir)))


class FlaskBlogTestCase(unittest.TestCase):

    def setUp(self):
        app.config['TESTING'] = True
        app.config['SQLALCHEMY_DATABASE_URI'] = \
            'sqlite:///:memory:'
        app.config['WTF_CSRF_ENABLED'] = False
        self.app = app.test_client()

        with app.app_context():
            db.create_all()
            # Create/test user in database
            usuario_prueba = Usuario(username='testuser')
            usuario_prueba.set_password('testpassword')
            db.session.add(usuario_prueba)
            db.session.commit()

    def tearDown(self):
        with app.app_context():
            db.session.remove()
            db.drop_all()

    def login(self, username='testuser', password='testpassword'):
        # Helper method for logging in
        return self.app.post('/login', data={
            'username': username,
            'password': password
        }, follow_redirects=True)

    def logout(self):
        # Helper method for logging out
        return self.app.get('/logout', follow_redirects=True)

    def test_login_logout(self):
        rv = self.login()
        response_text = rv.data.decode('utf-8')
        # Add print for debugging
        print("Response after logging in:", response_text)
        assert 'Welcome, testuser' in response_text \
            or 'Logout' in response_text
        rv = self.logout()
        response_text = rv.data.decode('utf-8')
        # Add print for debugging
        print("Response after logging out:", response_text)
        assert 'Welcome, testuser' not in response_text \
            and 'Logout' not in response_text

    def test_edit_note(self):
        # Test to verify note editing
        with app.app_context():
            self.login()
            self.app.post('/add', data={'note': 'Note to edit'},
                          follow_redirects=True)
            note = Nota.query.filter_by(content='Note to edit').first()
            rv = self.app.post(f'/edit/{note.id}',
                               data={'note': 'Edited note'},
                               follow_redirects=True)
            response_text = rv.data.decode('utf-8')
            # Add print for debugging
            print("Response after editing note:", response_text)
            assert b'Edited note' in rv.data

    def test_delete_note(self):
        # Test to verify note deletion
        with app.app_context():
            self.login()
            self.app.post('/add', data={'note': 'Note to delete'},
                          follow_redirects=True)
            note = Nota.query.filter_by(content='Note to delete').first()
            rv = self.app.get(f'/delete/{note.id}',
                              follow_redirects=True)
            response_text = rv.data.decode('utf-8')
            # Add print for debugging
            print("Response after deleting note:", response_text)
            assert b'Note to delete' not in rv.data


if __name__ == '__main__':
    unittest.main()

import unittest
from app import app

class FlaskBlogTestCase(unittest.TestCase):

    def setUp(self):
        # Configurar Flask en modo de pruebas
        app.config['TESTING'] = True
        self.app = app.test_client()

    def test_index_page(self):
        # Test para la página principal
        response = self.app.get('/')
        self.assertEqual(response.status_code, 200)
        self.assertIn(b'Blog de Notas', response.data)

    def test_add_note(self):
        # Test para añadir una nota
        response = self.app.post('/', data={'nota': 'Test nota'}, follow_redirects=True)
        self.assertIn(b'Test nota', response.data)

    def test_edit_note(self):
        # Primero añadimos una nota
        self.app.post('/', data={'nota': 'Nota original'}, follow_redirects=True)
        # Test para editar la nota
        response = self.app.post('/edit/0', data={'nota': 'Nota editada'}, follow_redirects=True)
        self.assertIn(b'Nota editada', response.data)
        self.assertNotIn(b'Nota original', response.data)

    def test_delete_note(self):
        # Primero añadimos una nota
        self.app.post('/', data={'nota': 'Nota para borrar'}, follow_redirects=True)
        # Test para borrar la nota
        response = self.app.get('/delete/0', follow_redirects=True)
        self.assertNotIn(b'Nota para borrar', response.data)

if __name__ == '__main__':
    unittest.main()

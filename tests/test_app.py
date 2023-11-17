import unittest
import sys
import os
import json

#directorio donde se encuentra app.py al sys.path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), os.path.pardir)))

from app import app

class FlaskBlogTestCase(unittest.TestCase):

    def setUp(self):
        app.config['TESTING'] = True
        self.app = app.test_client()
        # Crear un archivo de notas vacío
        with open('notas.json', 'w') as file:
            json.dump([], file)

    def tearDown(self):
        # Eliminar o vaciar el archivo de notas después de cada prueba
        if os.path.exists('notas.json'):
            os.remove('notas.json')

    def test_index_page(self):
        response = self.app.get('/')
        self.assertEqual(response.status_code, 200)
        self.assertIn(b'Blog de Notas', response.data)

    def test_add_note(self):
        response = self.app.post('/', data={'nota': 'Test nota'}, follow_redirects=True)
        self.assertIn(b'Test nota', response.data)

    def test_edit_note(self):
        # Añadir una nota primero
        self.app.post('/', data={'nota': 'Nota para editar'}, follow_redirects=True)
        # Obtener el número de notas actuales para editar la última añadida
        response = self.app.get('/')
        numero_notas = response.data.count(b'Nota para editar')
        # Editar la última nota añadida
        response = self.app.post(f'/edit/{numero_notas - 1}', data={'nota': 'Nota editada'}, follow_redirects=True)
        self.assertIn(b'Nota editada', response.data)

    def test_delete_note(self):
        # Añadir una nota primero
        self.app.post('/', data={'nota': 'Nota para borrar'}, follow_redirects=True)

        # Obtener el número de notas antes de borrar
        response = self.app.get('/')
        numero_notas_antes = response.data.count(b'<li>')

        # Borrar la primera nota (en este caso, la única)
        self.app.get('/delete/0', follow_redirects=True)

        # Obtener el número de notas después de borrar
        response = self.app.get('/')
        numero_notas_despues = response.data.count(b'<li>')

        # Verificar que el número de notas haya disminuido
        self.assertEqual(numero_notas_antes - 1, numero_notas_despues)

if __name__ == '__main__':
    unittest.main()

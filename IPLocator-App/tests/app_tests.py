import unittest
from app import app

class TestApp(unittest.TestCase):
    def setUp(self):
        app.config['TESTING'] = True
        self.app = app.test_client()

    def test_index_get(self):
        '''
        Empty Entry
        '''
        response = self.app.post('/', data={'ip_or_url': ''})
        self.assertEqual(response.status_code, 200)
        self.assertIn(b'Please Enter a Valid IP Address or Domain Name', response.data)

    def test_index_post_invalid_ip(self):
        '''
        Non-Empty Non-IP Address or Domain Name Entry
        '''
        response = self.app.post('/', data={'ip_or_url': 'invalid_ip_address'})
        self.assertEqual(response.status_code, 200)
        self.assertIn(b'Please Enter a Valid IP Address or Domain Name', response.data)

    def test_index_post_valid_ip(self):
        '''
        IP Address Entry
        '''
        response = self.app.post('/', data={'ip_or_url': '8.8.8.8'})
        self.assertEqual(response.status_code, 200)

    def test_index_post_valid_url(self):
        '''
        Domain Name Entry
        '''
        response = self.app.post('/', data={'ip_or_url': 'www.example.com'})
        self.assertEqual(response.status_code, 200)

if __name__ == '__main__':
    unittest.main()

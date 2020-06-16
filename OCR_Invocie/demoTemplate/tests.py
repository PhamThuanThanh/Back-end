from django.test import TestCase, SimpleTestCase

# Create your tests here.
class SimpleTests(SimpleTestCase):
    def test_home_page_status(self):
        respone = self.client.get('/home')
        self.assertEqual(respone.status_code, 200)

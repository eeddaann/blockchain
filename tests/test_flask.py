from blockchain import app
import unittest


class FlaskBlockchainTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        pass

    @classmethod
    def tearDownClass(cls):
        pass

    def setUp(self):
        # creates a test client
        self.app = app.test_client()
        # propagate the exceptions to the test client
        self.app.testing = True

    def tearDown(self):
        pass

    def test_home_status_code(self):
        # sends HTTP GET request to the application
        # on the specified path
        result = self.app.get('/')
        # assert the status code of the response
        self.assertEqual(result.status_code, 200)

    def test_home_data(self):
        # sends HTTP GET request to the application
        # on the specified path
        result = self.app.get('/')
        # assert the response data
        self.assertIn("Transfer some CimCoins to someone else".encode(), result.data)

    def test_new_transaction_status_code(self):
        # sends HTTP GET request to the application
        # on the specified path
        result = self.app.get('/new_transaction')
        # assert the status code of the response
        self.assertEqual(result.status_code, 200)

    def test_new_transaction_data(self):
        # sends HTTP GET request to the application
        # on the specified path
        result = self.app.get('/new_transaction')
        # assert the response data
        self.assertIn("sender".encode(), result.data)

    def test_login_status_code(self):
        # sends HTTP GET request to the application
        # on the specified path
        result = self.app.get('/login')
        # assert the status code of the response
        self.assertEqual(result.status_code, 200)

    def test_login_data(self):
        # sends HTTP GET request to the application
        # on the specified path
        result = self.app.get('/login')
        # assert the response data
        self.assertIn("wallet id:".encode(), result.data)

    def test_view_chain_status_code(self):
        # sends HTTP GET request to the application
        # on the specified path
        result = self.app.get('/view_chain')
        # assert the status code of the response
        self.assertEqual(result.status_code, 200)

    def test_view_chain_data(self):
        # sends HTTP GET request to the application
        # on the specified path
        result = self.app.get('/view_chain')
        # assert the response data
        self.assertIn("the chain length is:".encode(), result.data)


if __name__ == '__main__':
    unittest.main(verbosity=2)

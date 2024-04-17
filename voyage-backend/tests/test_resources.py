import unittest
import sys
sys.path.append("../src")
import resources.generative_ai_resource


class MyTestCase(unittest.TestCase):
    def test_generative_ai(self):
        self.assertEqual(True, False)  # add assertion here


if __name__ == '__main__':
    unittest.main()

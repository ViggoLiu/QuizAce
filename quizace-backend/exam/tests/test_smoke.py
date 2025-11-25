"""考试模块冒烟测试，确保测试框架运行正常。"""

from django.test import TestCase

# Create your tests here.
class SmokeTestCase(TestCase):
    def test_smoke(self):
        self.assertEqual(1 + 1, 2)
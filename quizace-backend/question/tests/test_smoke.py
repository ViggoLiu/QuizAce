"""题库模块冒烟测试，验证测试框架可运行。"""

from django.test import TestCase

# Create your tests here.
class SmokeTestCase(TestCase):
    def test_smoke(self):
        self.assertEqual(1 + 1, 2)
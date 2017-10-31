# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.test import TestCase

# Create your tests here.
class UtilitiesTestCase(TestCase):
    def setUp(self):
        self.dummyTest = 1
    def test_dummy_test(self):
        self.assertEqual(self.dummyTest, 1)
    def test_dummy_test_2(self):
        self.assertEqual(self.dummyTest, 0)

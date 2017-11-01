# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.test import TestCase
from models import Dummy

# Create your tests here.
class UtilitiesTestCase(TestCase):
    def setUp(self):
        self.dummyTest = 1
        fakeDummy = Dummy(value = 1)
        fakeDummy.save()

    def test_dummy_test(self):
        self.assertEqual(self.dummyTest, 1)

    def test_dummy_model(self):
        dummy = Dummy.objects.get(pk=1)
        self.assertEqual(dummy.value, 1)

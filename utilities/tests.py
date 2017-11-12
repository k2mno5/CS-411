# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.test import TestCase
from . import models as StackQuora

# Create your tests here.
class UtilitiesTestCase(TestCase):
    def setUp(self):
        return;

    def test_dummy_model(self):
        dir(StackQuora)
        firstUser = StackQuora.Users.objects.get(uid=1)
        self.assertEqual(firstUser.username, "Alice")

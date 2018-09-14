from unittest import TestCase
from random import choice

from context import truck #truck import load_route, possible_routes


class TestLoad_route(TestCase):
    def test_load_route(self):
        route = truck.load_route(choice(truck.possible_routes))
        self.assertIsInstance(route, dict)

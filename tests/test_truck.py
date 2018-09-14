from unittest import TestCase

from context import truck #import Truck, possible_routes


class TestTruck(TestCase):
    def setUp(self):
        self.truck = truck.Truck(truck_id='test')

    def test___init__(self):
        self.assertEqual(self.truck.id, 'test')
        # self.fail()

    def test_choose_route(self):
        self.assertFalse(self.truck.route)
        # select a route
        self.truck.choose_route()
        self.assertTrue(self.truck.route)
        self.assertTrue(self.truck.route in truck.possible_routes)

    def test_load_cargo(self):
        self.assertEqual(self.truck.cargo['capacity'], 50)
        self.assertEqual(self.truck.cargo['used'], 0)

        self.truck.load_cargo()
        self.assertEqual(self.truck.cargo['capacity'], 50)
        self.assertTrue(self.truck.cargo['used'] > 0)
    #
    # def test_arrive_at_destination(self):
    #     self.fail()
    #
    # def test_advance_route(self):
    #     self.fail()
    #
    # def test_stay_at_location(self):
    #     self.fail()
    #
    # def test_break_down(self):
    #     self.fail()
    #
    # def test_check_repairs(self):
    #     self.fail()
    #
    # def test_check_stationary_time(self):
    #     self.fail()
    #
    # def test_save(self):
    #     self.fail()
    #
    # def test_send_message(self):
    #     self.fail()
    #
    # def test_to_dict(self):
    #     self.fail()

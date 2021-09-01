from unittest import TestCase
from basewebapi import JSONBaseList, JSONBaseObject 

good_json_object = {'name': 'Foo', 'id': 1}
bad_json_object = 'string'
good_json_list = [{'name': 'Foo', 'id': 1}, {'name': 'Bar', 'id': 2},
                  {'name': 'Baz', 'id': 3}]
bad_json_list = {'name': 'Foo', 'id': 1}
bad_json_list_objects = [{'name': 'Foo', 'id': 1}, 'Bar']
child_objects = {'name': 'Foo', 'id': 1,
                 'friends': [{'name': 'Bar', 'id': 2},
                             {'name': 'Baz', 'id': 3}]}

class TestJSONBaseObject(TestCase):

    def setUp(self):
        self.good_object = JSONBaseObject.from_json(good_json_object)
        self.child_objects = JSONBaseObject(
            child_objects={'friends': JSONBaseList}, **child_objects)

    def test_from_json(self):
        self.assertRaises(ValueError, JSONBaseObject.from_json,
                          bad_json_object)
        self.assertIsInstance(self.good_object, JSONBaseObject)

    def test__init__(self):
        self.assertRaises(KeyError, JSONBaseObject, ['name', 'invalid'],
                          **child_objects)
        self.assertIsInstance(self.child_objects['friends'], JSONBaseList)
        for json_object in self.child_objects['friends']:
            self.assertIsInstance(json_object, JSONBaseObject)


class TestJSONBaseList(TestCase):

    def setUp(self):
        self.good_list = JSONBaseList.from_json(good_json_list, JSONBaseObject)

    def test_from_json(self):
        self.assertRaises(ValueError, JSONBaseList.from_json,
                          bad_json_list, JSONBaseObject)
        self.assertRaises(ValueError, JSONBaseList.from_json,
                          bad_json_list_objects, JSONBaseObject)
        self.assertIsInstance(self.good_list, JSONBaseList)
        for json_object in self.good_list:
            self.assertIsInstance(json_object, JSONBaseObject)

    def test_filter(self):
        self.assertRaises(TypeError, self.good_list.filter)
        self.assertRaises(TypeError, self.good_list.filter, 'One arg')
        self.assertRaises(KeyError, self.good_list.filter, 'invalid_field',
                          'foo')
        filter_test = self.good_list.filter('name', 'Bar')
        self.assertIsInstance(filter_test, JSONBaseList)
        self.assertEqual(1, len(filter_test))
        case_filter_test = self.good_list.filter('name', 'bar')
        self.assertIsInstance(case_filter_test, JSONBaseList)
        self.assertEqual(1, len(case_filter_test))
        fuzzy_filter_test = self.good_list.filter('name', 'ba', fuzzy=True)
        self.assertIsInstance(fuzzy_filter_test, JSONBaseList)
        self.assertEqual(2, len(fuzzy_filter_test))

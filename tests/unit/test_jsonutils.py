# vim: tabstop=4 shiftwidth=4 softtabstop=4

# Copyright 2011 OpenStack LLC.
# All Rights Reserved.
#
#    Licensed under the Apache License, Version 2.0 (the "License"); you may
#    not use this file except in compliance with the License. You may obtain
#    a copy of the License at
#
#         http://www.apache.org/licenses/LICENSE-2.0
#
#    Unless required by applicable law or agreed to in writing, software
#    distributed under the License is distributed on an "AS IS" BASIS, WITHOUT
#    WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied. See the
#    License for the specific language governing permissions and limitations
#    under the License.

import datetime
import unittest

from openstack.common import jsonutils


class JSONUtilsTestCase(unittest.TestCase):

    def test_dumps(self):
        self.assertEqual(jsonutils.dumps({'a': 'b'}), '{"a": "b"}')

    def test_loads(self):
        self.assertEqual(jsonutils.loads('{"a": "b"}'), {'a': 'b'})


class ToPrimitiveTestCase(unittest.TestCase):
    def test_list(self):
        self.assertEquals(jsonutils.to_primitive([1, 2, 3]), [1, 2, 3])

    def test_empty_list(self):
        self.assertEquals(jsonutils.to_primitive([]), [])

    def test_tuple(self):
        self.assertEquals(jsonutils.to_primitive((1, 2, 3)), [1, 2, 3])

    def test_dict(self):
        self.assertEquals(jsonutils.to_primitive(dict(a=1, b=2, c=3)),
                          dict(a=1, b=2, c=3))

    def test_empty_dict(self):
        self.assertEquals(jsonutils.to_primitive({}), {})

    def test_datetime(self):
        x = datetime.datetime(1, 2, 3, 4, 5, 6, 7)
        self.assertEquals(jsonutils.to_primitive(x),
                          "0001-02-03 04:05:06.000007")

    def test_iter(self):
        class IterClass(object):
            def __init__(self):
                self.data = [1, 2, 3, 4, 5]
                self.index = 0

            def __iter__(self):
                return self

            def next(self):
                if self.index == len(self.data):
                    raise StopIteration
                self.index = self.index + 1
                return self.data[self.index - 1]

        x = IterClass()
        self.assertEquals(jsonutils.to_primitive(x), [1, 2, 3, 4, 5])

    def test_iteritems(self):
        class IterItemsClass(object):
            def __init__(self):
                self.data = dict(a=1, b=2, c=3).items()
                self.index = 0

            def __iter__(self):
                return self

            def next(self):
                if self.index == len(self.data):
                    raise StopIteration
                self.index = self.index + 1
                return self.data[self.index - 1]

        x = IterItemsClass()
        ordered = jsonutils.to_primitive(x)
        ordered.sort()
        self.assertEquals(ordered, [['a', 1], ['b', 2], ['c', 3]])

    def test_instance(self):
        class MysteryClass(object):
            a = 10

            def __init__(self):
                self.b = 1

        x = MysteryClass()
        self.assertEquals(jsonutils.to_primitive(x, convert_instances=True),
                          dict(b=1))

        self.assertEquals(jsonutils.to_primitive(x), x)

    def test_typeerror(self):
        x = bytearray  # Class, not instance
        self.assertEquals(jsonutils.to_primitive(x), u"<type 'bytearray'>")

    def test_nasties(self):
        def foo():
            pass
        x = [datetime, foo, dir]
        ret = jsonutils.to_primitive(x)
        self.assertEquals(len(ret), 3)
        self.assertTrue(ret[0].startswith(u"<module 'datetime' from "))
        self.assertTrue(ret[1].startswith('<function foo at 0x'))
        self.assertEquals(ret[2], '<built-in function dir>')

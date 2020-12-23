from unittest import TestCase
from message import BaseMessage


class TestBaseMessage(TestCase):
    def test_constructor(self):
        m = BaseMessage(message="Message")
        self.assertEqual(m.message, "Message")
        self.assertEqual(m.entity, None)
        self.assertEqual(m.category, None)
        self.assertEqual(m.buffer_size, None)
        m = BaseMessage("Message", entity="Id")
        self.assertEqual(m.message, "Message")
        self.assertEqual(m.entity, "Id")
        self.assertEqual(m.category, None)
        self.assertEqual(m.buffer_size, None)
        m = BaseMessage("Message", category="C@tègor!e")
        self.assertEqual(m.message, "Message")
        self.assertEqual(m.entity, None)
        self.assertEqual(m.category, "C@tègor!e")
        self.assertEqual(m.buffer_size, None)
        m = BaseMessage("Message", buffer_size=1023)
        self.assertEqual(m.message, "Message")
        self.assertEqual(m.entity, None)
        self.assertEqual(m.category, None)
        self.assertEqual(m.buffer_size, 1023)

    def test_message(self):
        m = BaseMessage("Message")
        self.assertEqual(m.message, "Message")

    def test_entity(self):
        m = BaseMessage("Message", entity="Id")
        self.assertEqual(m.message, "Message")
        self.assertEqual(m.entity, "Id")

    def test_category(self):
        m = BaseMessage("Message", category="C@tègor!e")
        self.assertEqual(m.message, "Message")
        self.assertEqual(m.category, "C@tègor!e")

    def test_buffer_size(self):
        m = BaseMessage("Message", buffer_size=1023)
        self.assertEqual(m.message, "Message")
        self.assertEqual(m.buffer_size, 1023)

    def test_decode(self):
        json = '{   "msg": "Message",   "ent": "id",   "cat": "C@tègor!e",   "buf": 1050}'
        m = BaseMessage.decode(json_data=json)
        self.assertEqual(m.message, "Message")
        self.assertEqual(m.entity, "id")
        self.assertEqual(m.category, "C@tègor!e")
        self.assertEqual(m.buffer_size, 1050)

    def test_create_dictionary(self):
        m = BaseMessage(message="Message")
        dic = m.create_dictionary()
        self.assertEqual(dic.get("msg"), "Message")
        self.assertEqual(len(dic), 1)
        m = BaseMessage(message="Message", buffer_size=1023)
        dic = m.create_dictionary()
        self.assertEqual(dic.get("msg"), "Message")
        self.assertEqual(dic.get("buf"), 1023)
        self.assertEqual(len(dic), 2)
        m = BaseMessage(message="Message", category="C@tègor!e")
        dic = m.create_dictionary()
        self.assertEqual(dic.get("msg"), "Message")
        self.assertEqual(dic.get("cat"), "C@tègor!e")
        self.assertEqual(len(dic), 2)
        m = BaseMessage(message="Message", category="C@tègor!e", buffer_size=1023)
        dic = m.create_dictionary()
        self.assertEqual(dic.get("msg"), "Message")
        self.assertEqual(dic.get("cat"), "C@tègor!e")
        self.assertEqual(dic.get("buf"), 1023)
        self.assertEqual(len(dic), 3)
        m = BaseMessage(message="Message", entity="Id")
        dic = m.create_dictionary()
        self.assertEqual(dic.get("msg"), "Message")
        self.assertEqual(dic.get("ent"), "Id")
        self.assertEqual(len(dic), 2)
        m = BaseMessage(message="Message", entity="Id", buffer_size=1023)
        dic = m.create_dictionary()
        self.assertEqual(dic.get("msg"), "Message")
        self.assertEqual(dic.get("ent"), "Id")
        self.assertEqual(dic.get("buf"), 1023)
        self.assertEqual(len(dic), 3)
        m = BaseMessage(message="Message", entity="Id", category="C@tègor!e")
        dic = m.create_dictionary()
        self.assertEqual(dic.get("msg"), "Message")
        self.assertEqual(dic.get("ent"), "Id")
        self.assertEqual(dic.get("cat"), "C@tègor!e")
        self.assertEqual(len(dic), 3)
        m = BaseMessage(message="Message", entity="Id", category="C@tègor!e", buffer_size=1023)
        dic = m.create_dictionary()
        self.assertEqual(dic.get("msg"), "Message")
        self.assertEqual(dic.get("ent"), "Id")
        self.assertEqual(dic.get("cat"), "C@tègor!e")
        self.assertEqual(dic.get("buf"), 1023)
        self.assertEqual(len(dic), 4)

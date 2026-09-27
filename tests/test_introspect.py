import sqlite3
import unittest

from dbfamiliarity.db.introspect import inspect_table, list_tables, sample_rows


class IntrospectionTest(unittest.TestCase):
    def test_introspection_roundtrip(self):
        conn = sqlite3.connect(":memory:")
        conn.execute("create table city(id integer primary key, name text)")
        conn.execute("insert into city values (1, 'Hangzhou')")
        self.assertEqual(list_tables(conn), ["city"])
        meta = inspect_table(conn, "city")
        self.assertEqual(meta["row_count"], 1)
        self.assertTrue(meta["columns"][0]["primary_key"])
        self.assertEqual(sample_rows(conn, "city", 1)[0]["name"], "Hangzhou")
        conn.close()


if __name__ == "__main__":
    unittest.main()

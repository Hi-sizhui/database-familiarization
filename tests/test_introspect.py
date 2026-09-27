import sqlite3

from dbfamiliarity.db.introspect import inspect_table, list_tables, sample_rows


def test_introspection_roundtrip():
    conn = sqlite3.connect(":memory:")
    conn.execute("create table city(id integer primary key, name text)")
    conn.execute("insert into city values (1, 'Hangzhou')")
    assert list_tables(conn) == ["city"]
    meta = inspect_table(conn, "city")
    assert meta["row_count"] == 1
    assert meta["columns"][0]["primary_key"] is True
    assert sample_rows(conn, "city", 1)[0]["name"] == "Hangzhou"

import sqlite3
import tempfile
import unittest
from pathlib import Path
import sys

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))
from dbfamiliarity import Familiarizer, SQLiteProfiler


class TestCore(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.NamedTemporaryFile(suffix=".sqlite", delete=False)
        self.tmp.close()
        conn = sqlite3.connect(self.tmp.name)
        conn.executescript("""
        PRAGMA foreign_keys=ON;
        CREATE TABLE parent(id INTEGER PRIMARY KEY, name TEXT);
        CREATE TABLE child(id INTEGER PRIMARY KEY, parent_id INTEGER, value REAL,
                           FOREIGN KEY(parent_id) REFERENCES parent(id));
        INSERT INTO parent VALUES (1,'A'),(2,'B');
        INSERT INTO child VALUES (1,1,2.0),(2,2,5.0),(3,2,7.0);
        """)
        conn.commit()
        conn.close()

    def tearDown(self):
        Path(self.tmp.name).unlink(missing_ok=True)

    def test_preflight_and_probe(self):
        p = SQLiteProfiler(self.tmp.name)
        mem = p.preflight()
        self.assertEqual(set(mem.structural["tables"]), {"parent", "child"})
        fam = Familiarizer(p, policy="adaptive")
        mem = fam.run(3, mem)
        self.assertGreater(len(mem.empirical), 0)
        mem = Familiarizer(p, policy="adaptive").run(10)
        self.assertGreaterEqual(len(mem.relations), 1)

    def test_freeze_roundtrip(self):
        p = SQLiteProfiler(self.tmp.name)
        mem = Familiarizer(p, policy="adaptive").run(2).freeze()
        path = Path(self.tmp.name).with_suffix(".json")
        mem.to_json(path)
        restored = mem.from_json(path)
        self.assertTrue(restored.frozen)
        self.assertEqual(mem.fact_count(), restored.fact_count())
        path.unlink(missing_ok=True)


if __name__ == "__main__":
    unittest.main()

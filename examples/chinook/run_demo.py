from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "src"))

from dbfamiliarity import Familiarizer, SQLiteProfiler

DB = ROOT / "data/public/chinook/chinook_fixture.sqlite"
MEMORY = ROOT / "results/demo_memory.json"

if not DB.exists():
    raise SystemExit("Run: python scripts/build_chinook_fixture.py")

mem = Familiarizer(SQLiteProfiler(DB), policy="adaptive", seed=7).run(12).freeze()
MEMORY.parent.mkdir(parents=True, exist_ok=True)
mem.to_json(MEMORY)

print("database:", DB)
print("tables:", len(mem.structural["tables"]))
print("profiled_columns:", len(mem.empirical))
print("profiled_joins:", len(mem.relations))
print("memory_facts:", mem.fact_count())
print("frozen_memory:", MEMORY)

# GitHub project notes

The public repository is:

https://github.com/Hi-sizhui/database-familiarization

The repository contains the executable research harness, public demo database generator, experiment design, tests and model adapters.

Real organizational databases are intentionally excluded from version control. The demo SQLite database is generated locally by:

```bash
python examples/tourism_demo/build_db.py
```

For the research workflow, keep this separation:

1. **Public repository:** code, synthetic/demo data, benchmark definitions, experiment scripts and reproducible results that are safe to publish.
2. **Private environment:** real tourism-statistics data, credentials, internal schemas and potentially sensitive business information.
3. **Paper artifacts:** anonymized aggregate results and selected reproducibility artifacts.

The GitHub repository is the open-source companion to the research paper, not a substitute for the paper itself.

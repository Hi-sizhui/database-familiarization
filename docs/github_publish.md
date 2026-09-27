# Public data policy

This repository is a public research companion.

## Git-tracked

- source code;
- benchmark registry;
- public small fixtures;
- scripts;
- experiment definitions;
- reproducibility documentation.

## Downloaded locally but ignored by Git

- large benchmark archives;
- Git LFS/Xet objects;
- Docker database volumes;
- benchmark credentials;
- gated ground-truth files;
- any organizational database.

## Benchmark sources

The benchmark registry records official sources and licenses. Researchers should follow the source project's current access conditions rather than mirror gated or restricted assets into this repository.

The main current sources are:

- BIRD Mini-Dev — CC BY-SA 4.0.
- LiveSQLBench-Base-Lite-SQLite — CC BY-SA 4.0.
- BIRD-INTERACT / Mini-Interact — CC BY-SA 4.0.
- Spider 2.0 — follow the upstream repository's current access and usage terms.

The included Chinook SQLite fixture is from the upstream Chinook project, which publishes it under the MIT license.

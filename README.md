# memcore

[![PyPI version](https://img.shields.io/pypi/v/memcore.svg)](https://pypi.org/project/memcore/)
[![CI](https://github.com/Genious07/memcore/actions/workflows/ci.yml/badge.svg)](https://github.com/Genious07/memcore/actions/workflows/ci.yml)
[![License: MIT](https://img.shields.io/badge/License-MIT-green.svg)](LICENSE)
[![Python 3.9+](https://img.shields.io/badge/python-3.9+-blue.svg)](https://pypi.org/project/memcore/)

Open-source, model-agnostic memory layer for LLMs.

Drop memcore into any LLM application to give it persistent, structured memory — no API key required, no infrastructure to run, no vendor lock-in.

```python
import memcore

with memcore.MemCore() as mem:
    mem.add("My name is Alice. I prefer dark mode and I work in Python.")
    results = mem.search("programming preferences")
    for r in results:
        print(r.content)
```

---

## Why memcore?

Most LLM apps lose context between sessions. Vector databases are heavy to set up. Existing memory libraries tie you to a specific LLM or cloud service.

memcore is:
- **Zero config** — SQLite storage, works out of the box
- **Model agnostic** — plug in any LLM or use the built-in Gemma extractor
- **Pure library** — no daemon, no background process, no ports
- **Open source** — MIT licensed, runs fully offline

---

## Installation

```bash
pip install memcore
```

With semantic vector search (downloads ~130MB embedding model on first use):

```bash
pip install "memcore[vector]"
```

With LLM-powered extraction (downloads Gemma ~800MB on first use):

```bash
pip install "memcore[llm]"
```

---

## Architecture

memcore uses a **3-layer memory model** inspired by human cognition:

| Layer | Description | Promoted when |
|-------|-------------|---------------|
| **Working** | Short-term, recent facts | accessed 3+ times |
| **Episodic** | Mid-term, frequently used facts | accessed 10+ times |
| **Semantic** | Long-term, core knowledge | stays permanently |

### 5 core primitives

| Primitive | What it does |
|-----------|-------------|
| **Ingestion** | Extracts discrete facts from raw text |
| **Consolidation** | Promotes memories across layers |
| **Decay** | Reduces scores on idle memories, prunes stale ones |
| **Retrieval** | Fetches relevant memories, boosts access count |
| **Conflict resolution** | Deduplicates near-duplicate memories |

---

## Usage

### Default (rule-based extractor, no LLM needed)

```python
import memcore

mem = memcore.MemCore()
mem.add("I am a Python developer. I love open source.")
results = mem.search("developer")
```

### With semantic vector search (best recall)

```python
# pip install "memcore[vector]"
mem = memcore.MemCore(use_vector=True)
mem.add("I prefer concise explanations and dislike verbose output.")
results = mem.search("communication style")  # matches semantically, not just by keyword
```

### With Gemma LLM extractor (best quality)

```python
mem = memcore.MemCore(use_llm=True)
# Downloads gemma-3-1b-it-Q4_K_M.gguf (~800MB) on first run
mem.add("Long conversation text with lots of context...")
```

### Bring your own LLM extractor

```python
from memcore.extractors.base import BaseExtractor

class MyExtractor(BaseExtractor):
    def extract(self, text: str) -> list[str]:
        # call OpenAI, Anthropic, Ollama, anything
        return ["fact 1", "fact 2"]

mem = memcore.MemCore(extractor=MyExtractor())
```

### Custom storage backend

```python
from memcore.storage.base import BaseStorage

class PostgresStorage(BaseStorage):
    # implement the interface
    ...

mem = memcore.MemCore(storage=PostgresStorage())
```

### Memory maintenance

```python
mem.consolidate()   # promote memories based on access patterns
mem.decay()         # decay and prune stale memories
```

---

## Roadmap

- [ ] Vector similarity search (FAISS / sqlite-vec)
- [ ] Async support
- [ ] PostgreSQL storage backend
- [ ] LLM-based conflict resolution
- [ ] REST API server mode
- [ ] JavaScript / TypeScript port

---

## Contributing

Contributions are welcome. Please open an issue before submitting large PRs.

```bash
git clone https://github.com/Genious07/memcore
cd memcore
pip install -e ".[dev]"
pytest
```

---

## License

MIT

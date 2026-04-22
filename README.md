# mindlayer

[![PyPI version](https://img.shields.io/pypi/v/mindlayer-ai.svg)](https://pypi.org/project/mindlayer-ai/)
[![CI](https://github.com/Genious07/mindlayer/actions/workflows/ci.yml/badge.svg)](https://github.com/Genious07/mindlayer/actions/workflows/ci.yml)
[![License: MIT](https://img.shields.io/badge/License-MIT-green.svg)](LICENSE)
[![Python 3.9+](https://img.shields.io/badge/python-3.9+-blue.svg)](https://pypi.org/project/mindlayer-ai/)

Open-source, model-agnostic memory layer for LLMs.

Drop mindlayer into any LLM application to give it persistent, structured memory — no API key required, no infrastructure to run, no vendor lock-in.

```python
import mindlayer

with mindlayer.MemCore() as mem:
    mem.add("My name is Alice. I prefer dark mode and I work in Python.")
    results = mem.search("programming preferences")
    for r in results:
        print(r.content)
```

---

## Why mindlayer?

Most LLM apps lose context between sessions. Vector databases are heavy to set up. Existing memory libraries tie you to a specific LLM or cloud service.

mindlayer is:
- **Zero config** — SQLite storage, works out of the box
- **Model agnostic** — plug in any LLM or use the built-in Gemma extractor
- **Pure library** — no daemon, no background process, no ports
- **Open source** — MIT licensed, runs fully offline

---

## Installation

```bash
pip install mindlayer-ai
```

With semantic vector search (downloads ~130MB embedding model on first use):

```bash
pip install "mindlayer-ai[vector]"
```

With LLM-powered extraction (downloads Gemma ~800MB on first use):

```bash
pip install "mindlayer-ai[llm]"
```

---

## Architecture

mindlayer uses a **3-layer memory model** inspired by human cognition:

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
import mindlayer

mem = mindlayer.MemCore()
mem.add("I am a Python developer. I love open source.")
results = mem.search("developer")
```

### With semantic vector search (best recall)

```python
# pip install "mindlayer[vector]"
mem = mindlayer.MemCore(use_vector=True)
mem.add("I prefer concise explanations and dislike verbose output.")
results = mem.search("communication style")  # matches semantically, not just by keyword
```

### With Gemma LLM extractor (best quality)

```python
mem = mindlayer.MemCore(use_llm=True)
# Downloads gemma-3-1b-it-Q4_K_M.gguf (~800MB) on first run
mem.add("Long conversation text with lots of context...")
```

### Bring your own LLM extractor

```python
from mindlayer.extractors.base import BaseExtractor

class MyExtractor(BaseExtractor):
    def extract(self, text: str) -> list[str]:
        # call OpenAI, Anthropic, Ollama, anything
        return ["fact 1", "fact 2"]

mem = mindlayer.MemCore(extractor=MyExtractor())
```

### Custom storage backend

```python
from mindlayer.storage.base import BaseStorage

class PostgresStorage(BaseStorage):
    # implement the interface
    ...

mem = mindlayer.MemCore(storage=PostgresStorage())
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
git clone https://github.com/Genious07/mindlayer
cd mindlayer
pip install -e ".[dev,vector]"
pytest
```

---

## License

MIT

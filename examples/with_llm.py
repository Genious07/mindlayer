"""Usage with Gemma LLM extractor (downloads ~800MB model on first run)."""
import mindlayer

with mindlayer.MemCore(use_llm=True) as mem:
    mem.add("""
        Today I had a long conversation with a user named Sam.
        Sam mentioned he is a data scientist working at a startup in San Francisco.
        He prefers concise explanations and dislikes verbose output.
        He uses Python and is learning Rust on weekends.
    """)

    results = mem.search("Sam preferences")
    for r in results:
        print(f"[{r.layer}] {r.content}")

"""Basic usage — no API key, no setup required."""
import memcore

with memcore.MemCore() as mem:
    # Add memories from conversation text
    mem.add("My name is Alice. I prefer dark mode and I use VSCode.")
    mem.add("I am a backend developer. I work in Python and Go.")

    # Search memories
    results = mem.search("programming language")
    for r in results:
        print(f"[{r.layer}] {r.content}  (score={r.score:.2f})")

    # Run maintenance
    mem.consolidate()
    mem.decay()

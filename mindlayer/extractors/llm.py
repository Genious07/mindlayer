from pathlib import Path
from typing import List, Optional

from .base import BaseExtractor

MODEL_REPO = "bartowski/gemma-3-1b-it-GGUF"
MODEL_FILE = "gemma-3-1b-it-Q4_K_M.gguf"
DEFAULT_CACHE_DIR = Path.home() / ".cache" / "mindlayer" / "models"

EXTRACT_PROMPT = """\
Extract distinct memory facts from the text below.
Return one fact per line. Facts should be short, self-contained statements.
Only include information worth remembering long-term.

Text:
{text}

Facts:"""


class GemmaExtractor(BaseExtractor):
    def __init__(self, model_path: Optional[str] = None, n_ctx: int = 512):
        self._model_path = model_path or self._ensure_model()
        self._llm = None  # lazy load

    def _ensure_model(self) -> str:
        try:
            from huggingface_hub import hf_hub_download
        except ImportError:
            raise ImportError("Install huggingface-hub: pip install mindlayer[llm]")

        DEFAULT_CACHE_DIR.mkdir(parents=True, exist_ok=True)
        path = DEFAULT_CACHE_DIR / MODEL_FILE
        if not path.exists():
            print(f"[mindlayer] Downloading {MODEL_FILE} (~800MB, one-time)...")
            hf_hub_download(
                repo_id=MODEL_REPO,
                filename=MODEL_FILE,
                local_dir=str(DEFAULT_CACHE_DIR),
            )
        return str(path)

    def _load(self) -> None:
        if self._llm is not None:
            return
        try:
            from llama_cpp import Llama
        except ImportError:
            raise ImportError("Install llama-cpp-python: pip install mindlayer[llm]")
        self._llm = Llama(model_path=self._model_path, n_ctx=512, verbose=False)

    def extract(self, text: str) -> List[str]:
        self._load()
        prompt = EXTRACT_PROMPT.format(text=text)
        output = self._llm(prompt, max_tokens=256, stop=["\n\n"])
        raw = output["choices"][0]["text"].strip()
        facts = [line.lstrip("-•* ").strip() for line in raw.splitlines() if line.strip()]
        return facts

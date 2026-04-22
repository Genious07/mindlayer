import re
from typing import List

from .base import BaseExtractor

_FACT_PATTERNS = [
    r"(?:my name is|i am|i'm)\s+\w+",
    r"(?:i (?:prefer|like|love|hate|dislike|use|work with))\s+.+",
    r"(?:i am|i'm)\s+(?:a|an)\s+\w+",
    r"(?:i (?:live|work|study) (?:in|at))\s+.+",
    r"(?:my \w+ is)\s+.+",
]

_COMPILED = [re.compile(p, re.IGNORECASE) for p in _FACT_PATTERNS]


class RulesExtractor(BaseExtractor):
    def extract(self, text: str) -> List[str]:
        facts = []
        sentences = re.split(r"[.!?\n]", text)
        for sentence in sentences:
            sentence = sentence.strip()
            if not sentence:
                continue
            for pattern in _COMPILED:
                if pattern.search(sentence):
                    facts.append(sentence)
                    break
        return facts

from memcore.extractors.rules import RulesExtractor


def test_extract_name():
    e = RulesExtractor()
    facts = e.extract("My name is Bob.")
    assert any("Bob" in f for f in facts)


def test_extract_preference():
    e = RulesExtractor()
    facts = e.extract("I prefer Python over JavaScript.")
    assert len(facts) > 0


def test_extract_no_facts():
    e = RulesExtractor()
    facts = e.extract("The sky is blue today.")
    assert facts == []


def test_extract_multiple():
    e = RulesExtractor()
    text = "I am a developer. I love open source. I work in Berlin."
    facts = e.extract(text)
    assert len(facts) >= 2

from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True)
class PaperSummary:
    claim: str
    method: str
    takeaway: str
    experiment_hint: str
    tags: tuple[str, ...]


def summarize_paper(*, title: str, abstract: str, topic: str) -> PaperSummary:
    sentences = _split_sentences(abstract)
    claim = sentences[0] if sentences else abstract.strip()
    method = sentences[1] if len(sentences) > 1 else "Method not clearly extracted."
    takeaway = _best_takeaway(sentences, topic)
    experiment_hint = (
        f"Test one small {topic} change motivated by this paper before attempting larger rewrites."
    )
    tags = tuple(dict.fromkeys([topic, *_infer_tags(title, abstract)]))
    return PaperSummary(
        claim=claim,
        method=method,
        takeaway=takeaway,
        experiment_hint=experiment_hint,
        tags=tags,
    )


def format_summary(summary: PaperSummary) -> str:
    return (
        f"Claim: {summary.claim}\n"
        f"Method: {summary.method}\n"
        f"Takeaway: {summary.takeaway}\n"
        f"Experiment hint: {summary.experiment_hint}"
    )


def _split_sentences(text: str) -> list[str]:
    text = " ".join(text.split())
    if not text:
        return []
    sentences = [part.strip() for part in text.replace("! ", ". ").replace("? ", ". ").split(". ")]
    return [sentence.rstrip(".") for sentence in sentences if sentence]


def _best_takeaway(sentences: list[str], topic: str) -> str:
    topic_lower = topic.lower()
    for sentence in sentences:
        if topic_lower in sentence.lower():
            return sentence
    return sentences[min(2, len(sentences) - 1)] if sentences else "No clear takeaway."


def _infer_tags(title: str, abstract: str) -> list[str]:
    text = f"{title} {abstract}".lower()
    tags = []
    for tag, terms in {
        "optimizer": ("adam", "muon", "optimizer", "momentum"),
        "schedule": ("schedule", "warmup", "decay", "learning rate"),
        "architecture": ("transformer", "attention", "activation", "mlp"),
        "regularization": ("weight decay", "dropout", "regularization"),
    }.items():
        if any(term in text for term in terms):
            tags.append(tag)
    return tags

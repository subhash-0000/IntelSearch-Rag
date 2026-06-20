from __future__ import annotations

from abc import ABC, abstractmethod


class BaseGenerator(ABC):
    @abstractmethod
    def generate(self, query: str, contexts: list[str]) -> str:
        raise NotImplementedError


class HeuristicGenerator(BaseGenerator):
    """
    Deterministic fallback generator that composes concise answers from retrieved evidence.
    This keeps the app usable with zero API keys and no additional model serving.
    """

    def generate(self, query: str, contexts: list[str]) -> str:
        if not contexts:
            return "I could not find grounded evidence in the indexed documents."

        lead = contexts[0][:320].strip()
        support = contexts[1][:220].strip() if len(contexts) > 1 else ""
        answer = [
            f"Based on indexed documentation, here is the best supported response to: '{query}'.",
            lead,
        ]
        if support:
            answer.append(f"Additional supporting evidence: {support}")
        answer.append("If you need stricter compliance validation, verify the cited sources below.")
        return "\n\n".join(answer)

import time
from typing import List, Dict, Any
import requests

from app.config import config
from app.rag.retriever import RAGRetriever


class RAGEvaluator:
    """
    Evaluation suite for the RAG pipeline.
    Uses direct REST API calls to Gemini — no SDK required.
    """

    def __init__(self, collection=None):
        self.api_key = config.GEMINI_API_KEY
        self.base_url = config.GEMINI_BASE_URL
        self.retriever = RAGRetriever(collection=collection)

    # ------------------------------------------------------------------ #
    #  LLM                                                                 #
    # ------------------------------------------------------------------ #

    def _generate(self, prompt: str) -> str:
        """Call Gemini REST API directly."""
        url = f"{self.base_url}/{config.GEMINI_MODEL}:generateContent?key={self.api_key}"
        payload = {
            "contents": [{"parts": [{"text": prompt}]}],
            "generationConfig": {
                "temperature": 0.1,
                "maxOutputTokens": 512
            }
        }
        try:
            response = requests.post(url, json=payload, timeout=60)
            response.raise_for_status()
            data = response.json()
            return data["candidates"][0]["content"]["parts"][0]["text"]
        except Exception as e:
            print(f"[RAGEvaluator] LLM error: {e}")
            return ""

    # ------------------------------------------------------------------ #
    #  EVALUATION                                                          #
    # ------------------------------------------------------------------ #

    def evaluate_query(self, query: str, expected_answer: str = None) -> Dict[str, Any]:
        """Run full evaluation on a single query."""
        start = time.time()
        result = self.retriever.answer(query)
        latency = round(time.time() - start, 3)

        eval_result = {
            "query": query,
            "answer": result.get("answer", ""),
            "sources": result.get("sources", []),
            "confidence": result.get("confidence", "unknown"),
            "avg_similarity": result.get("avg_similarity", 0),
            "contexts_used": result.get("contexts_used", 0),
            "latency_seconds": latency,
        }

        quality_score = self._score_response(
            query,
            result.get("answer", ""),
            result.get("contexts", []),
            expected_answer
        )
        eval_result.update(quality_score)

        return eval_result

    def run_benchmark(self, test_cases: List[Dict[str, str]]) -> Dict[str, Any]:
        """
        Run evaluation on multiple test cases.
        Each test case: {"query": str, "expected": str (optional)}
        """
        results = []
        for case in test_cases:
            result = self.evaluate_query(
                case["query"],
                case.get("expected")
            )
            results.append(result)

        latencies = [r["latency_seconds"] for r in results]
        similarities = [r["avg_similarity"] for r in results]
        quality_scores = [r.get("quality_score", 0) for r in results]
        confidences = [r["confidence"] for r in results]

        return {
            "total_queries": len(results),
            "individual_results": results,
            "metrics": {
                "avg_latency": round(sum(latencies) / len(latencies), 3),
                "max_latency": round(max(latencies), 3),
                "min_latency": round(min(latencies), 3),
                "avg_similarity": round(sum(similarities) / len(similarities), 4),
                "avg_quality_score": round(sum(quality_scores) / len(quality_scores), 2),
                "high_confidence_rate": round(confidences.count("high") / len(confidences), 2),
                "failure_rate": round(
                    sum(1 for r in results if r.get(
                        "quality_score", 0) < 3) / len(results), 2
                )
            }
        }

    def _score_response(
        self,
        query: str,
        answer: str,
        contexts: List[Dict],
        expected: str = None
    ) -> Dict[str, Any]:
        """Use Gemini to score response quality on multiple dimensions."""

        context_text = "\n".join([c.get("text", "")[:200]
                                 for c in contexts[:3]])
        expected_section = f"\nExpected answer: {expected}" if expected else ""

        prompt = f"""Rate this RAG system response on a scale of 1-5 for each criterion.

Query: {query}
Retrieved Context (snippet): {context_text[:500]}
System Answer: {answer[:500]}{expected_section}

Score each dimension (1=poor, 5=excellent) and respond ONLY in this exact format with no extra text:
RELEVANCE: [number]
ACCURACY: [number]
COMPLETENESS: [number]
GROUNDEDNESS: [number]
OVERALL: [number]
FEEDBACK: [one sentence]"""

        try:
            response_text = self._generate(prompt)
            return self._parse_scores(response_text)
        except Exception:
            return {
                "relevance": 0,
                "accuracy": 0,
                "completeness": 0,
                "groundedness": 0,
                "quality_score": 0,
                "feedback": "Evaluation failed"
            }

    def _parse_scores(self, score_text: str) -> Dict[str, Any]:
        """Parse the LLM scoring response."""
        scores = {}
        if not score_text:
            return {
                "relevance": 0, "accuracy": 0, "completeness": 0,
                "groundedness": 0, "quality_score": 0, "feedback": "No response"
            }

        lines = score_text.strip().split("\n")
        for line in lines:
            line = line.strip()
            for key in ["RELEVANCE", "ACCURACY", "COMPLETENESS", "GROUNDEDNESS", "OVERALL"]:
                if line.startswith(f"{key}:"):
                    try:
                        # Extract first digit found
                        import re
                        nums = re.findall(r'\d', line)
                        val = int(nums[0]) if nums else 0
                        scores[key.lower()] = min(val, 5)
                    except Exception:
                        scores[key.lower()] = 0
            if line.startswith("FEEDBACK:"):
                scores["feedback"] = line.replace("FEEDBACK:", "").strip()

        scores["quality_score"] = scores.get("overall", 0)

        # Fill missing keys with 0
        for key in ["relevance", "accuracy", "completeness", "groundedness", "quality_score"]:
            scores.setdefault(key, 0)
        scores.setdefault("feedback", "No feedback provided")

        return scores

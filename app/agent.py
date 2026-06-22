import requests
from typing import List, Dict, Any

from app.config import config
from app.rag.retriever import RAGRetriever


class DocuMindAgent:
    """
    AI Agent that decides HOW to handle complex queries:
    - Decompose multi-part questions
    - Route to appropriate tools (RAG, summarization, comparison)
    - Synthesize final response
    """

    TOOLS = {
        "rag_search": "Search documents for specific information",
        "summarize": "Summarize a document or topic",
        "compare": "Compare information across multiple documents",
        "analyze_risk": "Identify risks, issues, or anomalies",
        "extract_data": "Extract structured data from documents"
    }

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
                "temperature": 0.3,
                "maxOutputTokens": 2048
            }
        }
        try:
            response = requests.post(url, json=payload, timeout=60)
            response.raise_for_status()
            data = response.json()
            return data["candidates"][0]["content"]["parts"][0]["text"]
        except Exception as e:
            print(f"[Agent] LLM error: {e}")
            return f"Error generating response: {str(e)}"

    # ------------------------------------------------------------------ #
    #  PUBLIC                                                              #
    # ------------------------------------------------------------------ #

    def run(self, user_query: str, chat_history: List[Dict] = None) -> Dict[str, Any]:
        """
        Agent pipeline:
        1. Plan actions
        2. Execute each action
        3. Synthesize final response
        """
        plan = self._plan(user_query)

        action_results = []
        for action in plan.get("actions", ["rag_search"]):
            result = self._execute_action(action, user_query)
            action_results.append(result)

        final_response = self._synthesize(user_query, plan, action_results)

        return {
            "answer": final_response.get("answer", ""),
            "plan": plan,
            "action_results": action_results,
            "sources": final_response.get("sources", []),
            "confidence": final_response.get("confidence", "medium"),
            "agent_reasoning": plan.get("reasoning", "")
        }

    # ------------------------------------------------------------------ #
    #  PLANNING                                                            #
    # ------------------------------------------------------------------ #

    def _plan(self, query: str) -> Dict[str, Any]:
        """Ask LLM to decompose the query into a plan."""
        tools_desc = "\n".join([f"- {k}: {v}" for k, v in self.TOOLS.items()])
        prompt = f"""You are an AI agent planner. Analyze the user query and create an execution plan.

Available tools:
{tools_desc}

User Query: "{query}"

Respond in this exact format:
INTENT: [one line describing what user wants]
REASONING: [why you chose these actions]
ACTIONS: [comma-separated list of tools to use, e.g.: rag_search, analyze_risk]
SUBQUERIES: [if multiple searches needed, list them separated by |]"""

        try:
            response_text = self._generate(prompt)
            return self._parse_plan(response_text, query)
        except Exception as e:
            return {
                "intent": "answer question",
                "reasoning": "Direct search",
                "actions": ["rag_search"],
                "subqueries": [query]
            }

    def _parse_plan(self, plan_text: str, original_query: str) -> Dict[str, Any]:
        """Parse the structured plan response."""
        plan = {
            "intent": "",
            "reasoning": "",
            "actions": ["rag_search"],
            "subqueries": [original_query]
        }
        for line in plan_text.strip().split("\n"):
            line = line.strip()
            if line.startswith("INTENT:"):
                plan["intent"] = line.replace("INTENT:", "").strip()
            elif line.startswith("REASONING:"):
                plan["reasoning"] = line.replace("REASONING:", "").strip()
            elif line.startswith("ACTIONS:"):
                actions_str = line.replace("ACTIONS:", "").strip()
                plan["actions"] = [a.strip() for a in actions_str.split(",")]
            elif line.startswith("SUBQUERIES:"):
                sq_str = line.replace("SUBQUERIES:", "").strip()
                plan["subqueries"] = [q.strip() for q in sq_str.split("|")]
        return plan

    # ------------------------------------------------------------------ #
    #  EXECUTION                                                           #
    # ------------------------------------------------------------------ #

    def _execute_action(self, action: str, query: str) -> Dict[str, Any]:
        """Execute a single planned action."""
        action = action.strip()
        if action == "rag_search":
            return self.retriever.answer(query)
        elif action == "summarize":
            contexts = self.retriever.retrieve(query, n_results=8)
            return self._summarize_contexts(contexts, query)
        elif action == "analyze_risk":
            contexts = self.retriever.retrieve(query, n_results=8)
            return self._analyze_risks(contexts, query)
        elif action == "compare":
            contexts = self.retriever.retrieve(query, n_results=10)
            return self._compare_docs(contexts, query)
        else:
            return self.retriever.answer(query)

    def _summarize_contexts(self, contexts: List[Dict], query: str) -> Dict[str, Any]:
        if not contexts:
            return {"answer": "No documents found to summarize.", "sources": []}

        context_text = "\n\n".join(
            [f"[{c['source']}]: {c['text']}" for c in contexts])
        prompt = f"""Summarize the following document content in relation to: "{query}"

Content:
{context_text}

Provide a structured summary with key points, main themes, and important details."""

        answer = self._generate(prompt)
        sources = list({c["source"] for c in contexts})
        return {"answer": answer, "sources": sources}

    def _analyze_risks(self, contexts: List[Dict], query: str) -> Dict[str, Any]:
        if not contexts:
            return {"answer": "No documents found for risk analysis.", "sources": []}

        context_text = "\n\n".join(
            [f"[{c['source']}]: {c['text']}" for c in contexts])
        prompt = f"""Analyze the following content and identify risks, issues, warnings, or concerns related to: "{query}"

Content:
{context_text}

Structure your response as:
HIGH RISKS:
MEDIUM RISKS:
LOW RISKS / OBSERVATIONS:
RECOMMENDATIONS:"""

        answer = self._generate(prompt)
        sources = list({c["source"] for c in contexts})
        return {"answer": answer, "sources": sources}

    def _compare_docs(self, contexts: List[Dict], query: str) -> Dict[str, Any]:
        if not contexts:
            return {"answer": "No documents found for comparison.", "sources": []}

        by_source = {}
        for ctx in contexts:
            src = ctx["source"]
            by_source.setdefault(src, []).append(ctx["text"])

        context_text = ""
        for src, texts in by_source.items():
            context_text += f"\n## {src}:\n" + " ".join(texts[:2])

        prompt = f"""Compare the following documents in relation to: "{query}"

{context_text}

Provide a structured comparison highlighting:
- Similarities
- Differences
- Key takeaways from each source"""

        answer = self._generate(prompt)
        return {"answer": answer, "sources": list(by_source.keys())}

    # ------------------------------------------------------------------ #
    #  SYNTHESIS                                                           #
    # ------------------------------------------------------------------ #

    def _synthesize(self, query: str, plan: Dict, results: List[Dict]) -> Dict[str, Any]:
        """Combine all action results into a final coherent answer."""
        if not results:
            return {"answer": "No results generated.", "sources": [], "confidence": "low"}

        if len(results) == 1:
            return results[0]

        combined = "\n\n---\n\n".join([r.get("answer", "") for r in results])
        all_sources = list({s for r in results for s in r.get("sources", [])})

        prompt = f"""You collected the following analysis results for the user query: "{query}"

{combined}

Write a single, clear, comprehensive final answer that synthesizes all the above findings.
Be well-structured, professional, and cite sources where relevant."""

        answer = self._generate(prompt)
        return {
            "answer": answer,
            "sources": all_sources,
            "confidence": "high"
        }

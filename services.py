from google import genai
from google.genai import types
import json
import os
import re
from typing import List, Optional
from dotenv import load_dotenv

load_dotenv()

# Use Gemini 2.5 Flash
MODEL_NAME = "gemini-2.5-flash"

def _get_client() -> genai.Client:
    return genai.Client(api_key=os.getenv("GEMINI_API_KEY"))

def _generate(prompt: str) -> str:
    """Single helper to call Gemini and return text."""
    client = _get_client()
    response = client.models.generate_content(
        model=MODEL_NAME,
        contents=prompt,
    )
    return response.text

def _clean_json(text: str) -> str:
    """Strip markdown code fences if Gemini wraps JSON in them."""
    text = text.strip()
    text = re.sub(r"^```(?:json)?", "", text)
    text = re.sub(r"```$", "", text)
    return text.strip()

def _safe_json(text: str) -> dict:
    try:
        return json.loads(_clean_json(text))
    except json.JSONDecodeError:
        # try extracting first JSON object
        match = re.search(r"\{.*\}", text, re.DOTALL)
        if match:
            return json.loads(match.group())
        raise ValueError("Gemini response was not valid JSON")

# ─── 1. EVALUATE ───────────────────────────────────────────────────────────────

def evaluate_prompt(prompt: str, domain: str = "general") -> dict:
    """
    Score a prompt across 7 quality dimensions.
    Returns overall_score, grade, per-dimension scores, strengths, weaknesses, suggestions.
    """
    evaluation_prompt = f"""You are an expert prompt engineer specialising in chatbot system prompts.
Evaluate the following system prompt for the domain: "{domain}".

PROMPT TO EVALUATE:
\"\"\"{prompt}\"\"\"

Return ONLY valid JSON — no explanation, no markdown fences — in EXACTLY this format:
{{
  "overall_score": <number 0-100>,
  "grade": "<A+ | A | B | C | D | F>",
  "dimensions": {{
    "clarity":         {{"score": <0-10>, "feedback": "<one sentence>"}},
    "specificity":     {{"score": <0-10>, "feedback": "<one sentence>"}},
    "role_definition": {{"score": <0-10>, "feedback": "<one sentence>"}},
    "context_richness":{{"score": <0-10>, "feedback": "<one sentence>"}},
    "output_format":   {{"score": <0-10>, "feedback": "<one sentence>"}},
    "constraints":     {{"score": <0-10>, "feedback": "<one sentence>"}},
    "tone_consistency":{{"score": <0-10>, "feedback": "<one sentence>"}}
  }},
  "strengths": ["<strength 1>", "<strength 2>"],
  "weaknesses": ["<weakness 1>", "<weakness 2>", "<weakness 3>"],
  "improvement_suggestions": ["<suggestion 1>", "<suggestion 2>", "<suggestion 3>"]
}}"""

    return _safe_json(_generate(evaluation_prompt))

# ─── 2. OPTIMIZE ───────────────────────────────────────────────────────────────

def optimize_prompt(prompt: str, domain: str = "general", goal: str = "improve overall quality") -> dict:
    """
    Take a prompt and return an improved version with explanation and before/after scores.
    """
    opt_prompt = f"""You are a senior prompt engineer. Your task is to optimize this chatbot system prompt.

DOMAIN: {domain}
OPTIMIZATION GOAL: {goal}

ORIGINAL PROMPT:
\"\"\"{prompt}\"\"\"

Rules:
- Keep the same core purpose
- Apply prompt engineering best practices (role, context, format, constraints, tone)
- Do NOT add fake examples unless asked
- Be precise, not verbose

Return ONLY valid JSON in EXACTLY this format:
{{
  "optimized_prompt": "<the full improved prompt>",
  "original_score": <0-100>,
  "optimized_score": <0-100>,
  "improvement": <optimized_score - original_score>,
  "changes_made": [
    "<specific change 1>",
    "<specific change 2>",
    "<specific change 3>"
  ],
  "explanation": "<2-3 sentences explaining the key improvements>"
}}"""

    result = _safe_json(_generate(opt_prompt))
    result["original_prompt"] = prompt
    return result

# ─── 3. GENERATE VARIANTS ──────────────────────────────────────────────────────

def generate_variants(prompt: str, domain: str = "general", count: int = 3, style: str = "balanced") -> list:
    """
    Generate N different styled variants of a prompt — each with a quality score.
    """

    styles = {
        "balanced": "Mix of professional tone, clear structure, and concise constraints",
        "concise": "Short, direct, minimal words — just the essential instructions",
        "detailed": "Rich context, thorough constraints, comprehensive examples",
        "formal": "Formal corporate tone, precise language",
        "friendly": "Warm, conversational, approachable tone"
    }
    style_description = styles.get(style, styles["balanced"])

    var_prompt = f"""You are a prompt engineer. Generate {count} distinct variants of this system prompt.

DOMAIN: {domain}
ORIGINAL PROMPT:
\"\"\"{prompt}\"\"\"

Style guideline: {style_description}

Each variant should approach the same goal differently. Vary: tone, structure, specificity, role framing.

Return ONLY valid JSON as a list in EXACTLY this format:
[
  {{
    "variant_number": 1,
    "prompt": "<full variant prompt>",
    "score": <0-100>,
    "style_description": "<what makes this variant unique>",
    "key_difference": "<the main thing changed from original>"
  }},
  ...
]"""

    response = _generate(var_prompt)
    result = _safe_json(response.text)
    if isinstance(result, list):
        return result
    # sometimes Gemini wraps in a key
    for key in result:
        if isinstance(result[key], list):
            return result[key]
    return []

# ─── 4. COMPARE ────────────────────────────────────────────────────────────────

def compare_prompts(prompt_a: str, prompt_b: str, test_input: str, domain: str = "general") -> dict:
    """
    Test two prompts with the same user message, score both responses, declare winner.
    """

    # Get response A
    resp_a = _generate(f"SYSTEM: {prompt_a}\n\nUSER: {test_input}")

    # Get response B
    resp_b = _generate(f"SYSTEM: {prompt_b}\n\nUSER: {test_input}")

    # Judge both
    judge_prompt = f"""You are a neutral AI judge evaluating two chatbot responses.

DOMAIN: {domain}
USER MESSAGE: "{test_input}"

RESPONSE A (from Prompt A):
\"\"\"{resp_a}\"\"\"

RESPONSE B (from Prompt B):
\"\"\"{resp_b}\"\"\"

Evaluate both responses on: accuracy, relevance, helpfulness, clarity, tone.

Return ONLY valid JSON in EXACTLY this format:
{{
  "score_a": <0-100>,
  "score_b": <0-100>,
  "winner": "<A | B | TIE>",
  "winner_reason": "<one clear sentence>",
  "detailed_analysis": {{
    "accuracy":    {{"a": <0-10>, "b": <0-10>}},
    "relevance":   {{"a": <0-10>, "b": <0-10>}},
    "helpfulness": {{"a": <0-10>, "b": <0-10>}},
    "clarity":     {{"a": <0-10>, "b": <0-10>}},
    "tone":        {{"a": <0-10>, "b": <0-10>}}
  }}
}}"""

    judgment = _safe_json(_generate(judge_prompt))

    return {
        "prompt_a": prompt_a,
        "prompt_b": prompt_b,
        "test_input": test_input,
        "response_a": resp_a,
        "response_b": resp_b,
        **judgment
    }

# ─── 5. TEST A PROMPT ──────────────────────────────────────────────────────────

def test_prompt(prompt: str, user_input: str, domain: str = "general") -> dict:
    """
    Run a user message through a prompt, get the response, and score it.
    """

    response_text = _generate(f"SYSTEM: {prompt}\n\nUSER: {user_input}")

    score_prompt = f"""You are a quality evaluator for chatbot responses.

DOMAIN: {domain}
USER MESSAGE: "{user_input}"
CHATBOT RESPONSE:
\"\"\"{response_text}\"\"\"

Return ONLY valid JSON in EXACTLY this format:
{{
  "response_score": <0-100>,
  "response_analysis": {{
    "accuracy":    {{"score": <0-10>, "note": "<brief note>"}},
    "relevance":   {{"score": <0-10>, "note": "<brief note>"}},
    "helpfulness": {{"score": <0-10>, "note": "<brief note>"}},
    "clarity":     {{"score": <0-10>, "note": "<brief note>"}},
    "tone":        {{"score": <0-10>, "note": "<brief note>"}}
  }}
}}"""

    analysis = _safe_json(_generate(score_prompt))

    return {
        "prompt": prompt,
        "user_input": user_input,
        "response": response_text,
        **analysis
    }

# ─── 6. FULL PIPELINE ──────────────────────────────────────────────────────────

def run_full_pipeline(prompt: str, test_inputs: List[str], domain: str = "general", goal: str = "improve overall quality") -> dict:
    """
    One-shot full pipeline:
    1. Evaluate original prompt
    2. Optimize it
    3. Test both original + optimized on all test inputs
    4. Return full comparison
    """

    # Step 1: evaluate original
    original_eval = evaluate_prompt(prompt, domain)

    # Step 2: optimize
    optimization = optimize_prompt(prompt, domain, goal)
    optimized_prompt = optimization["optimized_prompt"]

    # Step 3: test both prompts on each input
    original_responses = []
    optimized_responses = []

    for inp in test_inputs[:3]:  # limit to 3 to save API quota
        o_resp = _generate(f"SYSTEM: {prompt}\n\nUSER: {inp}")
        opt_resp = _generate(f"SYSTEM: {optimized_prompt}\n\nUSER: {inp}")
        original_responses.append({"input": inp, "response": o_resp})
        optimized_responses.append({"input": inp, "response": opt_resp})

    return {
        "original_prompt": prompt,
        "optimized_prompt": optimized_prompt,
        "original_evaluation": original_eval,
        "optimization_details": optimization,
        "original_responses": original_responses,
        "optimized_responses": optimized_responses,
        "summary": {
            "original_score": original_eval.get("overall_score", 0),
            "optimized_score": optimization.get("optimized_score", 0),
            "improvement": optimization.get("improvement", 0),
            "grade_before": original_eval.get("grade", "N/A"),
        }
    }

# ─── 7. SUGGEST DOMAIN TEMPLATES ───────────────────────────────────────────────

def suggest_starter_prompt(domain: str, use_case: str) -> dict:
    """
    Generate a high-quality starter system prompt from scratch for a given domain + use case.
    """

    suggest_prompt = f"""You are an expert prompt engineer.
Create a professional, high-quality chatbot system prompt for:
DOMAIN: {domain}
USE CASE: {use_case}

Apply all best practices: clear role, context, response format, tone, constraints, and error handling.

Return ONLY valid JSON in EXACTLY this format:
{{
  "generated_prompt": "<the full system prompt>",
  "score": <0-100>,
  "key_features": ["<feature 1>", "<feature 2>", "<feature 3>"],
  "recommended_test_inputs": ["<test message 1>", "<test message 2>", "<test message 3>"]
}}"""

    return _safe_json(_generate(suggest_prompt))

from pydantic import BaseModel, Field
from typing import Optional, List
from datetime import datetime


# ─── REQUEST MODELS ────────────────────────────────────────────────────────────

class EvaluateRequest(BaseModel):
    prompt: str = Field(..., description="The system prompt to evaluate")
    domain: str = Field(default="general", description="Domain: general, customer_support, education, healthcare, ecommerce, hr, legal")

class OptimizeRequest(BaseModel):
    prompt: str = Field(..., description="The system prompt to optimize")
    domain: str = Field(default="general", description="Target domain")
    optimization_goal: str = Field(default="improve overall quality", description="What specific aspect to improve")

class VariantsRequest(BaseModel):
    prompt: str = Field(..., description="Base prompt to generate variants from")
    domain: str = Field(default="general")
    count: int = Field(default=3, ge=2, le=5, description="Number of variants to generate (2-5)")
    style: str = Field(default="balanced", description="Style: balanced, concise, detailed, formal, friendly")

class CompareRequest(BaseModel):
    prompt_a: str = Field(..., description="First prompt")
    prompt_b: str = Field(..., description="Second prompt")
    test_input: str = Field(..., description="User message to test both prompts")
    domain: str = Field(default="general")

class TestPromptRequest(BaseModel):
    prompt: str = Field(..., description="System prompt to test")
    user_input: str = Field(..., description="User message to send")
    domain: str = Field(default="general")

class SaveTemplateRequest(BaseModel):
    name: str = Field(..., description="Name for this template")
    prompt: str = Field(..., description="The prompt to save")
    domain: str = Field(default="general")
    score: Optional[float] = None

class FullPipelineRequest(BaseModel):
    prompt: str = Field(..., description="Original prompt")
    test_inputs: List[str] = Field(..., description="List of test user messages")
    domain: str = Field(default="general")
    optimization_goal: str = Field(default="improve overall quality")


# ─── RESPONSE MODELS ───────────────────────────────────────────────────────────

class DimensionScore(BaseModel):
    score: float
    feedback: str

class EvaluationResult(BaseModel):
    overall_score: float
    grade: str
    dimensions: dict
    strengths: List[str]
    weaknesses: List[str]
    improvement_suggestions: List[str]

class OptimizationResult(BaseModel):
    original_prompt: str
    optimized_prompt: str
    original_score: float
    optimized_score: float
    improvement: float
    changes_made: List[str]
    explanation: str

class VariantResult(BaseModel):
    variant_number: int
    prompt: str
    score: float
    style_description: str
    key_difference: str

class CompareResult(BaseModel):
    prompt_a: str
    prompt_b: str
    test_input: str
    response_a: str
    response_b: str
    score_a: float
    score_b: float
    winner: str
    winner_reason: str
    detailed_analysis: dict

class TestResult(BaseModel):
    prompt: str
    user_input: str
    response: str
    response_score: float
    response_analysis: dict

class TemplateResponse(BaseModel):
    id: int
    name: str
    prompt: str
    domain: str
    score: Optional[float]
    use_count: int
    created_at: datetime

    class Config:
        from_attributes = True

class OptimizationHistoryResponse(BaseModel):
    id: int
    original_prompt: str
    optimized_prompt: Optional[str]
    domain: str
    original_score: Optional[float]
    optimized_score: Optional[float]
    improvement: Optional[float]
    created_at: datetime

    class Config:
        from_attributes = True

class StatsResponse(BaseModel):
    total_optimizations: int
    total_templates: int
    total_tests: int
    total_comparisons: int
    average_improvement: float
    best_domain: str
    top_templates: List[dict]

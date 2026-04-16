from fastapi import FastAPI, HTTPException, Depends
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy.orm import Session
from sqlalchemy import func
from datetime import datetime
from typing import List, Optional

from database import init_db, get_db, OptimizationRecord, Template, TestResult as TestResultDB, CompareRecord
from models import (
    EvaluateRequest, OptimizeRequest, VariantsRequest,
    CompareRequest, TestPromptRequest, SaveTemplateRequest,
    FullPipelineRequest, TemplateResponse, OptimizationHistoryResponse, StatsResponse
)
import services

# ─── APP SETUP ─────────────────────────────────────────────────────────────────

app = FastAPI(
    title="Prompt Optimization System",
    description="""
    ## Prompt Optimization System — Gemini 2.5 Flash

    A full backend for scientifically improving chatbot system prompts.

    ### Features
    - **Evaluate** — Score any prompt across 7 quality dimensions
    - **Optimize** — Auto-improve a prompt using Gemini
    - **Variants** — Generate multiple styled versions of a prompt
    - **Compare** — A/B test two prompts with real user messages
    - **Test** — Run a prompt + user message and score the response
    - **Full Pipeline** — Evaluate → Optimize → Test in one shot
    - **Templates** — Save and reuse your best prompts
    - **History** — Track all your optimizations over time
    - **Stats** — Dashboard metrics
    - **Suggest** — Generate a prompt from scratch for any domain
    """,
    version="1.0.0"
)

# Allow all origins so frontend (Antigravity or any) can connect
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Initialize DB on startup
@app.on_event("startup")
def on_startup():
    init_db()


# ─── HEALTH ────────────────────────────────────────────────────────────────────

@app.get("/", tags=["Health"])
def root():
    return {
        "status": "running",
        "app": "Prompt Optimization System",
        "model": "gemini-2.5-flash-preview-04-17",
        "version": "1.0.0"
    }

@app.get("/health", tags=["Health"])
def health():
    return {"status": "ok", "timestamp": datetime.utcnow().isoformat()}


# ─── 1. EVALUATE ───────────────────────────────────────────────────────────────

@app.post("/api/evaluate", tags=["Core"])
def evaluate(req: EvaluateRequest, db: Session = Depends(get_db)):
    """
    Evaluate a system prompt and get a detailed quality report.

    Returns:
    - overall_score (0–100)
    - grade (A+ to F)
    - 7 dimension scores: clarity, specificity, role_definition,
      context_richness, output_format, constraints, tone_consistency
    - strengths, weaknesses, improvement_suggestions
    """
    try:
        result = services.evaluate_prompt(req.prompt, req.domain)
        return {"success": True, "data": result}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


# ─── 2. OPTIMIZE ───────────────────────────────────────────────────────────────

@app.post("/api/optimize", tags=["Core"])
def optimize(req: OptimizeRequest, db: Session = Depends(get_db)):
    """
    Optimize a system prompt. Returns improved version with before/after scores.

    Also saves the record to history automatically.
    """
    try:
        result = services.optimize_prompt(req.prompt, req.domain, req.optimization_goal)

        # Save to DB
        record = OptimizationRecord(
            original_prompt=req.prompt,
            optimized_prompt=result.get("optimized_prompt"),
            domain=req.domain,
            original_score=result.get("original_score"),
            optimized_score=result.get("optimized_score"),
            improvement=result.get("improvement"),
        )
        db.add(record)
        db.commit()
        db.refresh(record)

        return {"success": True, "data": result, "record_id": record.id}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


# ─── 3. GENERATE VARIANTS ──────────────────────────────────────────────────────

@app.post("/api/variants", tags=["Core"])
def variants(req: VariantsRequest):
    """
    Generate multiple styled variants of a prompt.

    - count: 2–5 variants
    - style: balanced | concise | detailed | formal | friendly
    """
    try:
        result = services.generate_variants(req.prompt, req.domain, req.count, req.style)
        return {"success": True, "data": result, "count": len(result)}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


# ─── 4. COMPARE ────────────────────────────────────────────────────────────────

@app.post("/api/compare", tags=["Core"])
def compare(req: CompareRequest, db: Session = Depends(get_db)):
    """
    A/B test two prompts with the same user message.

    Both prompts are tested with Gemini 2.5 Flash.
    Responses are scored. A winner is declared with reasoning.
    """
    try:
        result = services.compare_prompts(req.prompt_a, req.prompt_b, req.test_input, req.domain)

        # Save to DB
        record = CompareRecord(
            prompt_a=req.prompt_a,
            prompt_b=req.prompt_b,
            test_input=req.test_input,
            response_a=result.get("response_a"),
            response_b=result.get("response_b"),
            score_a=result.get("score_a"),
            score_b=result.get("score_b"),
            winner=result.get("winner"),
            domain=req.domain,
        )
        db.add(record)
        db.commit()

        return {"success": True, "data": result}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


# ─── 5. TEST PROMPT ────────────────────────────────────────────────────────────

@app.post("/api/test", tags=["Core"])
def test_prompt(req: TestPromptRequest, db: Session = Depends(get_db)):
    """
    Run a user message through a system prompt and score the response.

    Returns the actual chatbot response + quality analysis.
    """
    try:
        result = services.test_prompt(req.prompt, req.user_input, req.domain)

        # Save to DB
        record = TestResultDB(
            prompt=req.prompt,
            user_input=req.user_input,
            response=result.get("response"),
            response_score=result.get("response_score"),
            domain=req.domain,
        )
        db.add(record)
        db.commit()

        return {"success": True, "data": result}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


# ─── 6. FULL PIPELINE ──────────────────────────────────────────────────────────

@app.post("/api/pipeline", tags=["Core"])
def full_pipeline(req: FullPipelineRequest, db: Session = Depends(get_db)):
    """
    One-shot full workflow:
    1. Evaluate original prompt
    2. Optimize it
    3. Test original AND optimized on all your test messages
    4. Return complete side-by-side comparison

    This is the most powerful endpoint — use it to see full before/after.
    """
    try:
        result = services.run_full_pipeline(
            req.prompt, req.test_inputs, req.domain, req.optimization_goal
        )

        # Save optimization to DB
        opt = result.get("optimization_details", {})
        record = OptimizationRecord(
            original_prompt=req.prompt,
            optimized_prompt=opt.get("optimized_prompt"),
            domain=req.domain,
            original_score=result["summary"].get("original_score"),
            optimized_score=result["summary"].get("optimized_score"),
            improvement=result["summary"].get("improvement"),
        )
        db.add(record)
        db.commit()

        return {"success": True, "data": result}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


# ─── 7. SUGGEST STARTER PROMPT ─────────────────────────────────────────────────

@app.post("/api/suggest", tags=["Utilities"])
def suggest_prompt(domain: str, use_case: str):
    """
    Generate a high-quality system prompt from scratch.

    Provide a domain (e.g. 'customer_support') and use_case
    (e.g. 'e-commerce returns chatbot') — get a ready-to-use prompt.
    """
    try:
        result = services.suggest_starter_prompt(domain, use_case)
        return {"success": True, "data": result}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


# ─── 8. TEMPLATES ──────────────────────────────────────────────────────────────

@app.post("/api/templates", tags=["Templates"], response_model=dict)
def save_template(req: SaveTemplateRequest, db: Session = Depends(get_db)):
    """Save a prompt as a reusable template."""
    template = Template(
        name=req.name,
        prompt=req.prompt,
        domain=req.domain,
        score=req.score,
    )
    db.add(template)
    db.commit()
    db.refresh(template)
    return {"success": True, "message": "Template saved", "id": template.id}


@app.get("/api/templates", tags=["Templates"])
def get_templates(domain: Optional[str] = None, db: Session = Depends(get_db)):
    """Get all saved templates, optionally filtered by domain."""
    query = db.query(Template)
    if domain:
        query = query.filter(Template.domain == domain)
    templates = query.order_by(Template.use_count.desc()).all()
    return {
        "success": True,
        "data": [
            {
                "id": t.id,
                "name": t.name,
                "prompt": t.prompt,
                "domain": t.domain,
                "score": t.score,
                "use_count": t.use_count,
                "created_at": t.created_at.isoformat(),
            }
            for t in templates
        ],
        "count": len(templates)
    }


@app.get("/api/templates/{template_id}", tags=["Templates"])
def get_template(template_id: int, db: Session = Depends(get_db)):
    """Get a specific template and increment its use count."""
    template = db.query(Template).filter(Template.id == template_id).first()
    if not template:
        raise HTTPException(status_code=404, detail="Template not found")
    template.use_count += 1
    db.commit()
    return {
        "success": True,
        "data": {
            "id": template.id,
            "name": template.name,
            "prompt": template.prompt,
            "domain": template.domain,
            "score": template.score,
            "use_count": template.use_count,
            "created_at": template.created_at.isoformat(),
        }
    }


@app.delete("/api/templates/{template_id}", tags=["Templates"])
def delete_template(template_id: int, db: Session = Depends(get_db)):
    """Delete a saved template."""
    template = db.query(Template).filter(Template.id == template_id).first()
    if not template:
        raise HTTPException(status_code=404, detail="Template not found")
    db.delete(template)
    db.commit()
    return {"success": True, "message": f"Template {template_id} deleted"}


# ─── 9. HISTORY ────────────────────────────────────────────────────────────────

@app.get("/api/history", tags=["History"])
def get_history(limit: int = 20, domain: Optional[str] = None, db: Session = Depends(get_db)):
    """Get optimization history, newest first."""
    query = db.query(OptimizationRecord)
    if domain:
        query = query.filter(OptimizationRecord.domain == domain)
    records = query.order_by(OptimizationRecord.created_at.desc()).limit(limit).all()
    return {
        "success": True,
        "data": [
            {
                "id": r.id,
                "original_prompt": r.original_prompt[:200] + "..." if len(r.original_prompt) > 200 else r.original_prompt,
                "optimized_prompt": (r.optimized_prompt[:200] + "...") if r.optimized_prompt and len(r.optimized_prompt) > 200 else r.optimized_prompt,
                "domain": r.domain,
                "original_score": r.original_score,
                "optimized_score": r.optimized_score,
                "improvement": r.improvement,
                "created_at": r.created_at.isoformat(),
            }
            for r in records
        ],
        "count": len(records)
    }


@app.get("/api/history/{record_id}", tags=["History"])
def get_history_record(record_id: int, db: Session = Depends(get_db)):
    """Get the full detail of a specific optimization record."""
    record = db.query(OptimizationRecord).filter(OptimizationRecord.id == record_id).first()
    if not record:
        raise HTTPException(status_code=404, detail="Record not found")
    return {
        "success": True,
        "data": {
            "id": record.id,
            "original_prompt": record.original_prompt,
            "optimized_prompt": record.optimized_prompt,
            "domain": record.domain,
            "original_score": record.original_score,
            "optimized_score": record.optimized_score,
            "improvement": record.improvement,
            "created_at": record.created_at.isoformat(),
        }
    }


# ─── 10. STATS ─────────────────────────────────────────────────────────────────

@app.get("/api/stats", tags=["Dashboard"])
def get_stats(db: Session = Depends(get_db)):
    """
    Dashboard stats for the frontend.
    Returns totals, average improvement, best domain, top templates.
    """
    total_optimizations = db.query(OptimizationRecord).count()
    total_templates = db.query(Template).count()
    total_tests = db.query(TestResultDB).count()
    total_comparisons = db.query(CompareRecord).count()

    avg_improvement = db.query(
        func.avg(OptimizationRecord.improvement)
    ).scalar() or 0.0

    # Best performing domain
    best_domain_row = db.query(
        OptimizationRecord.domain,
        func.avg(OptimizationRecord.improvement).label("avg_imp")
    ).group_by(OptimizationRecord.domain).order_by(
        func.avg(OptimizationRecord.improvement).desc()
    ).first()
    best_domain = best_domain_row[0] if best_domain_row else "N/A"

    # Top 3 templates by use count
    top_templates = db.query(Template).order_by(Template.use_count.desc()).limit(3).all()

    return {
        "success": True,
        "data": {
            "total_optimizations": total_optimizations,
            "total_templates": total_templates,
            "total_tests": total_tests,
            "total_comparisons": total_comparisons,
            "average_improvement": round(avg_improvement, 2),
            "best_domain": best_domain,
            "top_templates": [
                {"id": t.id, "name": t.name, "use_count": t.use_count, "score": t.score}
                for t in top_templates
            ]
        }
    }


# ─── DOMAINS LIST ──────────────────────────────────────────────────────────────

@app.get("/api/domains", tags=["Utilities"])
def get_domains():
    """List of supported domains."""
    return {
        "success": True,
        "data": [
            {"value": "general",          "label": "General"},
            {"value": "customer_support", "label": "Customer Support"},
            {"value": "education",        "label": "Education / Tutoring"},
            {"value": "healthcare",       "label": "Healthcare"},
            {"value": "ecommerce",        "label": "E-Commerce"},
            {"value": "hr",               "label": "Human Resources"},
            {"value": "legal",            "label": "Legal"},
            {"value": "finance",          "label": "Finance"},
            {"value": "tech_support",     "label": "Tech Support"},
        ]
    }

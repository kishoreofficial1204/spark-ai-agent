"""Spark AI tools: calculator, summarizer, rewriter, study planner, code explainer.

Each tool has a clear one-line docstring — that line is read by Strands Decider 2B's
tool-selection pattern as the option description.
"""

from __future__ import annotations

import ast
import operator
import re
from typing import Any

from strands import tool

# ---------------------------------------------------------------------------
# Safe arithmetic evaluator (no eval/exec)
# ---------------------------------------------------------------------------
_OPS: dict[type, Any] = {
    ast.Add: operator.add,
    ast.Sub: operator.sub,
    ast.Mult: operator.mul,
    ast.Div: operator.truediv,
    ast.Pow: operator.pow,
    ast.Mod: operator.mod,
    ast.UAdd: operator.pos,
    ast.USub: operator.neg,
    ast.FloorDiv: operator.floordiv,
}


def _safe_eval(node: ast.expr) -> float | int:
    if isinstance(node, ast.Constant) and isinstance(node.value, (int, float)):
        return node.value
    if isinstance(node, ast.BinOp):
        op = _OPS.get(type(node.op))
        if op is None:
            raise ValueError(f"unsupported operator: {type(node.op).__name__}")
        left, right = _safe_eval(node.left), _safe_eval(node.right)
        if isinstance(node.op, ast.Div) and right == 0:
            raise ZeroDivisionError("division by zero")
        if isinstance(node.op, ast.FloorDiv) and right == 0:
            raise ZeroDivisionError("division by zero")
        return op(left, right)
    if isinstance(node, ast.UnaryOp):
        op = _OPS.get(type(node.op))
        if op is None:
            raise ValueError(f"unsupported unary operator: {type(node.op).__name__}")
        return op(_safe_eval(node.operand))
    raise ValueError(f"unsupported expression element: {type(node).__name__}")


# ---------------------------------------------------------------------------
# Tools
# ---------------------------------------------------------------------------

@tool
def calculate(expression: str) -> dict:
    """Evaluate a mathematical expression and return the exact numeric result."""
    cleaned = expression.strip()
    # strip trailing punctuation like "?" or "."
    cleaned = re.sub(r"[^0-9+\-*/().% \t\^]+$", "", cleaned).strip()
    # support ^ as exponentiation
    cleaned = cleaned.replace("^", "**")
    try:
        tree = ast.parse(cleaned, mode="eval")
        result = _safe_eval(tree.body)
        # return int when result is a whole number
        if isinstance(result, float) and result.is_integer():
            result = int(result)
        return {"result": result, "expression": cleaned}
    except ZeroDivisionError:
        return {"error": "division by zero", "expression": cleaned}
    except (SyntaxError, ValueError) as e:
        return {"error": f"invalid expression: {e}", "expression": cleaned}
    except Exception as e:  # noqa: BLE001
        return {"error": str(e), "expression": cleaned}


@tool
def summarize_text(text: str, style: str = "short") -> dict:
    """Summarize provided text in short, detailed, or bullet-point style."""
    # The LLM (via the Strands agent) generates the actual summary;
    # this tool validates inputs and structures the request.
    valid_styles = ("short", "detailed", "bullets")
    if style not in valid_styles:
        style = "short"
    if not text.strip():
        return {"error": "no text provided to summarize", "style": style}
    word_count = len(text.split())
    # Return a structured instruction the agent uses to produce the summary
    return {
        "text": text.strip(),
        "style": style,
        "word_count": word_count,
        "instruction": (
            f"Summarize the following text in '{style}' style. "
            f"{'Write one concise paragraph.' if style == 'short' else ''}"
            f"{'Write multiple paragraphs preserving all key points.' if style == 'detailed' else ''}"
            f"{'Write as a bullet-point list.' if style == 'bullets' else ''}"
            f"\n\nText:\n{text.strip()}"
        ),
    }


@tool
def rewrite_text(text: str, style: str = "professional") -> dict:
    """Rewrite provided text in a chosen style: professional, simple, concise, or formal."""
    valid_styles = ("professional", "simple", "concise", "formal")
    if style not in valid_styles:
        style = "professional"
    if not text.strip():
        return {"error": "no text provided to rewrite", "style": style}
    style_instructions = {
        "professional": "clear, polished, business-appropriate language",
        "simple": "plain, easy-to-understand language suitable for a general audience",
        "concise": "as few words as possible while preserving the full meaning",
        "formal": "formal, academic, or official register with no contractions",
    }
    return {
        "text": text.strip(),
        "style": style,
        "original_length": len(text.split()),
        "instruction": (
            f"Rewrite the following text in {style_instructions[style]}. "
            f"Preserve the original meaning exactly. Correct any grammar issues.\n\n"
            f"Text:\n{text.strip()}"
        ),
    }


@tool
def create_study_plan(subjects: str, available_days: int, hours_per_day: float) -> dict:
    """Generate a structured day-by-day study plan from subjects, available days, and hours per day."""
    if not subjects.strip():
        return {"error": "please provide the subjects or topics you want to study"}
    if available_days <= 0:
        return {"error": "available_days must be at least 1"}
    if hours_per_day <= 0:
        return {"error": "hours_per_day must be greater than 0"}

    subject_list = [s.strip() for s in re.split(r"[,;/\n]+", subjects) if s.strip()]
    if not subject_list:
        return {"error": "could not parse subjects — separate them with commas"}

    total_hours = available_days * hours_per_day
    hours_per_subject = total_hours / len(subject_list)
    days_per_subject = max(1, round(hours_per_subject / hours_per_day))

    plan = []
    day = 1
    for subject in subject_list:
        for i in range(days_per_subject):
            if day > available_days:
                break
            plan.append({
                "day": day,
                "subject": subject,
                "hours": hours_per_day,
                "session": f"Day {day}: {subject} — session {i + 1} of {days_per_subject}",
            })
            day += 1
        if day > available_days:
            break

    # fill any remaining days with review
    while day <= available_days:
        plan.append({"day": day, "subject": "Review & practice", "hours": hours_per_day,
                     "session": f"Day {day}: Review all subjects"})
        day += 1

    return {
        "subjects": subject_list,
        "available_days": available_days,
        "hours_per_day": hours_per_day,
        "total_hours": total_hours,
        "plan": plan,
    }


@tool
def explain_code(code: str, language: str = "auto", error_message: str = "") -> dict:
    """Explain what a code snippet does; optionally diagnose an error message."""
    if not code.strip():
        return {"error": "no code provided"}

    # Auto-detect language from common patterns
    detected = language
    if language == "auto":
        if re.search(r"\bdef |import |print\(|:\s*$", code, re.M):
            detected = "Python"
        elif re.search(r"\bfunction |const |let |var |=>|console\.log", code):
            detected = "JavaScript"
        elif re.search(r"public\s+class |System\.out|void main", code):
            detected = "Java"
        elif re.search(r"#include|std::|cout|cin", code):
            detected = "C++"
        elif re.search(r"\bfn |let mut |println!", code):
            detected = "Rust"
        else:
            detected = "unknown"

    return {
        "code": code.strip(),
        "language": detected,
        "has_error_context": bool(error_message.strip()),
        "instruction": (
            f"Explain the following {detected} code in plain language. "
            f"Describe what it does overall, explain the key functions, variables, and logic. "
            f"{'Also explain this error and suggest a fix: ' + error_message.strip() if error_message.strip() else ''}"
            f"\n\nCode:\n```{detected.lower()}\n{code.strip()}\n```"
        ),
    }


TOOLS = [calculate, summarize_text, rewrite_text, create_study_plan, explain_code]

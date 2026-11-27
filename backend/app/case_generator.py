from __future__ import annotations

import html
import json
import logging
import re
from dataclasses import dataclass
from typing import Optional

import httpx

from app.config import settings
from app.models import CasePacket, InterviewerPersona

logger = logging.getLogger(__name__)


def slugify_case_id(text: str) -> str:
    slug = re.sub(r"[^a-z0-9]+", "-", text.lower()).strip("-")
    return slug[:64] or "custom-case"


def _strip_html(raw: str) -> str:
    cleaned = re.sub(r"(?is)<(script|style|noscript|svg|header|footer|nav).*?>.*?</\1>", " ", raw)
    cleaned = re.sub(r"(?s)<[^>]+>", " ", cleaned)
    cleaned = html.unescape(cleaned)
    cleaned = re.sub(r"\s+", " ", cleaned).strip()
    return cleaned


async def fetch_url_text(url: str, max_chars: int = 10000) -> tuple[str, Optional[str]]:
    """Fetch a public URL and extract clean readable text. Returns (text, error_or_none)."""
    try:
        async with httpx.AsyncClient(
            follow_redirects=True,
            timeout=15.0,
            headers={"User-Agent": "ProductSenseHarness/0.3 (+https://localhost)"},
        ) as client:
            res = await client.get(url)
            res.raise_for_status()
            content_type = res.headers.get("content-type", "")
            raw = res.text
            text = _strip_html(raw) if "html" in content_type.lower() or "<html" in raw[:500].lower() else raw.strip()
            return text[:max_chars], None
    except Exception as exc:
        logger.warning("Failed to fetch URL %s: %s", url, exc)
        return "", f"Could not fetch {url}: {exc}"


@dataclass
class GeneratedCaseResult:
    case_packet: CasePacket
    warnings: list[str]
    used_demo_mode: bool


def _extract_first_heading(markdown: str) -> str:
    for line in markdown.splitlines():
        stripped = line.strip()
        if stripped.startswith("# "):
            return stripped[2:].strip()
    return ""


def _infer_company_and_role(source_markdown: str, company: Optional[str], role: Optional[str]) -> tuple[str, str]:
    inferred_company = (company or "").strip()
    inferred_role = (role or "").strip()

    heading = _extract_first_heading(source_markdown)
    if not inferred_role:
        m = re.search(r"(?:Target Role|Role)\s*:\s*([^\n_*]+)", source_markdown, re.IGNORECASE)
        if m:
            inferred_role = m.group(1).strip()
        elif "—" in heading:
            inferred_role = heading.split("—")[0].replace("Role Prep:", "").strip()
        else:
            inferred_role = "Senior Product Manager"

    if not inferred_company:
        if "—" in heading:
            inferred_company = heading.split("—")[-1].strip()
        else:
            m = re.search(r"(?:Company)\s*:\s*([^\n_*]+)", source_markdown, re.IGNORECASE)
            inferred_company = m.group(1).strip() if m else "Target Company"

    return inferred_company, inferred_role


def _demo_generate_case(
    source_markdown: str,
    url_sections: list[tuple[str, str]],
    topic: Optional[str],
    company: Optional[str],
    role: Optional[str],
    duration_minutes: int,
    case_id: Optional[str],
) -> CasePacket:
    inferred_company, inferred_role = _infer_company_and_role(source_markdown, company, role)
    title = (topic or "").strip() or f"{inferred_company} Product Strategy & Architecture Prioritisation"
    final_id = slugify_case_id(case_id or f"{inferred_company}-{title}")

    excerpt_lines = [
        ln.strip()
        for ln in source_markdown.splitlines()
        if ln.strip() and not ln.strip().startswith("---")
    ][:18]
    excerpt_block = "\n".join(excerpt_lines) if excerpt_lines else "No source markdown provided."

    url_summary = ""
    if url_sections:
        bullets = [f"- `{u}` ({len(txt)} chars indexed)" for u, txt in url_sections]
        url_summary = "\n\n### Public Documentation Referenced\n" + "\n".join(bullets)

    brief_md = (
        f"# {title}\n\n"
        f"**Company:** {inferred_company}  \n"
        f"**Role:** {inferred_role}\n\n"
        f"---\n\n"
        f"## 1. Strategic & Product Context\n\n"
        f"{excerpt_block}{url_summary}\n\n"
        f"---\n\n"
        f"## 2. The Challenge\n\n"
        f"You are stepping into the **{inferred_role}** role at **{inferred_company}** with competing demands "
        f"between foundational platform reliability/experience debt and high-visibility strategic bets around **{title}**.\n\n"
        f"**Decision Needed:** Recommend your 2-quarter product strategy, architectural boundaries "
        f"(Core Platform vs. Application/Experience layer), Trust-by-Design guardrails, and roadmap sequencing.\n\n"
        f"> _Generated in local Demo Mode. Set `GEMINI_API_KEY` in `.env` for richer LLM-synthesised case packets._\n"
    )

    return CasePacket(
        id=final_id,
        title=title,
        company=inferred_company,
        role=inferred_role,
        duration_minutes=duration_minutes,
        difficulty="Senior PM",
        tags=[inferred_company, "Product Strategy", "Prioritisation", "Architecture"],
        interviewers=[
            InterviewerPersona(
                name="Alex",
                role="Group Product Manager",
                focus="Strategy, user/customer segmentation, commercial trade-offs, measurable KPIs",
            ),
            InterviewerPersona(
                name="Sam",
                role="Principal Engineer",
                focus="Core vs. Application architecture, reliability, security/compliance guardrails, delivery capacity",
            ),
        ],
        candidate_brief_markdown=brief_md,
        hidden_facts={
            "engineering_capacity": "1 dedicated cross-functional squad of 5 engineers for the next 2 quarters; platform/identity dependencies require 2 weeks lead time.",
            "current_pain_points": "Legacy workflows and inconsistent contracts drive ~35% of Tier-2 support escalations and slow customer time-to-value.",
            "commercial_pressure": "2 enterprise prospects are pushing for the flagship capability this quarter, while an existing key customer is stalled on foundational onboarding friction.",
            "compliance_and_risk": "Security and Compliance require deterministic policy controls, least-privilege permissions, and immutable audit logs before general availability.",
            "success_baseline": "Leadership expects measurable improvement in activation time and support ticket deflection within 6 months.",
        },
        curveballs=[
            "Engineering pushes back: the foundational reliability work and the flagship feature cannot both ship in Q1 — one must slip to Q2. Which do you cut and how do you justify the risk?",
            "Executive leadership wants a marquee customer demo in 8 weeks while Support says onboarding escalations are spiking. What ships in 8 weeks without violating Trust-by-Design?",
        ],
        evaluation_focus=[
            "Asking targeted clarifying questions before jumping into solutions",
            "Explicit strategic framing and trade-off rigor tied to company goals",
            "Clear separation of Core Platform vs. Application/Experience layer",
            "Trust-by-Design (security, compliance, reliability baked in)",
            "Crisp executive synthesis with concrete metrics and sequencing",
        ],
    )


async def generate_case_packet(
    source_markdown: str,
    urls: list[str] | None = None,
    topic: Optional[str] = None,
    company: Optional[str] = None,
    role: Optional[str] = None,
    duration_minutes: int = 45,
    case_id: Optional[str] = None,
) -> GeneratedCaseResult:
    """Generate a validated CasePacket from role-prep markdown + optional public doc URLs."""
    warnings: list[str] = []
    url_sections: list[tuple[str, str]] = []

    for raw_url in urls or []:
        u = raw_url.strip()
        if not u:
            continue
        text, err = await fetch_url_text(u)
        if err:
            warnings.append(err)
        elif text:
            url_sections.append((u, text))

    if settings.demo_mode:
        packet = _demo_generate_case(
            source_markdown=source_markdown,
            url_sections=url_sections,
            topic=topic,
            company=company,
            role=role,
            duration_minutes=duration_minutes,
            case_id=case_id,
        )
        return GeneratedCaseResult(case_packet=packet, warnings=warnings, used_demo_mode=True)

    from google import genai
    from google.genai import types

    docs_context = ""
    if url_sections:
        parts = [f"### URL: {u}\n{txt[:6000]}" for u, txt in url_sections]
        docs_context = "\n\nPUBLIC DOCUMENTATION EXCERPTS:\n" + "\n\n".join(parts)

    topic_line = f"REQUESTED CASE FOCUS / TOPIC: {topic}" if topic else "REQUESTED CASE FOCUS / TOPIC: Pick the highest-leverage, most realistic product prioritisation & architecture dilemma from the source material."
    company_line = f"COMPANY OVERRIDE: {company}" if company else ""
    role_line = f"ROLE OVERRIDE: {role}" if role else ""
    id_line = f"CASE ID OVERRIDE: {slugify_case_id(case_id)}" if case_id else ""

    prompt = f"""You are a Bar-Raiser Product Management Interview Designer creating a realistic, challenging {duration_minutes}-minute Product Sense & Architecture case study packet.

{topic_line}
{company_line}
{role_line}
{id_line}

SOURCE ROLE PREP / JD / PROPOSAL MATERIAL:
{source_markdown[:24000]}
{docs_context}

DESIGN RULES:
1. `candidate_brief_markdown` MUST contain ONLY high-signal business context, product/technical background, observed tension/challenge, and a concise **Decision Needed** prompt (1.5–2.5 pages, well-structured Markdown). Do NOT include interview-format meta instructions (no "Be prepared to ask clarifying questions", no "Deliver a 2-minute wrap-up" — the harness lobby explains exercise rules).
2. `interviewers`: Exactly 2 complementary realistic panel personas (e.g., Group PM / VP Product + Principal Platform Engineer / Architect) tailored to this company.
3. `hidden_facts`: 5 to 7 concrete, realistic hidden constraints (e.g. `engineering_capacity`, `current_system_state`, `commercial_pressure`, `compliance_stance`, `metrics_baseline`) that the candidate must uncover by asking smart clarifying questions.
4. `curveballs`: Exactly 2 sharp, realistic stakeholder conflict curveballs for Phase 4 (engineering vs. commercial deadline, compliance blocker, or executive escalation).
5. `evaluation_focus`: 4 to 5 sharp grading criteria specific to this role and company.
6. `id`: lowercase kebab-case slug (e.g., `company-short-topic`).

Return ONLY valid JSON matching this exact schema:
{{
  "id": "kebab-case-id",
  "title": "Concise case title",
  "company": "Company name",
  "role": "Target PM role title",
  "duration_minutes": {duration_minutes},
  "difficulty": "Senior / Staff PM",
  "tags": ["Tag1", "Tag2", "Tag3", "Tag4"],
  "interviewers": [
    {{ "name": "Alex", "role": "Role", "focus": "Focus areas" }},
    {{ "name": "Sam", "role": "Role", "focus": "Focus areas" }}
  ],
  "candidate_brief_markdown": "# Title\\n\\n...",
  "hidden_facts": {{
    "engineering_capacity": "...",
    "current_state": "...",
    "commercial_pressure": "...",
    "compliance_stance": "...",
    "key_metric_baseline": "..."
  }},
  "curveballs": [
    "Curveball 1...",
    "Curveball 2..."
  ],
  "evaluation_focus": [
    "Criterion 1",
    "Criterion 2",
    "Criterion 3",
    "Criterion 4"
  ]
}}"""

    client = genai.Client(api_key=settings.gemini_api_key)
    response = client.models.generate_content(
        model=settings.gemini_interviewer_model,
        contents=prompt,
        config=types.GenerateContentConfig(
            response_mime_type="application/json",
            temperature=0.45,
        ),
    )
    raw = (response.text or "").strip()
    data = json.loads(raw)
    if case_id:
        data["id"] = slugify_case_id(case_id)
    else:
        data["id"] = slugify_case_id(str(data.get("id") or data.get("title") or "custom-case"))
    data["duration_minutes"] = duration_minutes

    packet = CasePacket.model_validate(data)
    return GeneratedCaseResult(case_packet=packet, warnings=warnings, used_demo_mode=False)

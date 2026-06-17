#!/usr/bin/env python3
"""Enrich external-index/skills.yaml with a per-repo `skills` field.

The user wants the frontend to describe what concrete skills each repo
contains, so users can search for a specific capability and learn
which repo provides it. This script derives an initial `skills` list
for every repo from its category, tags, and summary — using a curated
category→skills map plus keyword extraction from the summary.

Idempotent: re-running it overwrites the `skills` field with a fresh
derivation, so it is safe to run repeatedly. After running, hand-edit
the most important repos (top-starred) to refine the list.
"""
from __future__ import annotations

import re
import sys
from pathlib import Path

try:
    from ruamel.yaml import YAML
except ImportError:
    print("ruamel.yaml required: pip install ruamel.yaml", file=sys.stderr)
    sys.exit(1)

REPO = Path(__file__).resolve().parent.parent
SKILLS_YAML = REPO / "external-index" / "skills.yaml"

# Category → canonical skill capabilities. These are the concrete
# things a user would look for when trying to find a repo. Kept
# short (3-6 items) so the card stays scannable.
CATEGORY_SKILLS: dict[str, list[str]] = {
    "official-cookbooks": [
        "tool use", "structured output", "RAG", "function calling", "prompt patterns",
    ],
    "prompt-libraries": [
        "system prompts", "role prompts", "few-shot", "prompt templates",
    ],
    "agent-frameworks": [
        "multi-step agents", "tool routing", "planning", "memory", "ReAct",
    ],
    "rag-retrieval": [
        "chunking", "retrieval", "reranking", "RAG pipeline", "hybrid search",
    ],
    "vector-databases": [
        "vector search", "ANN index", "similarity search", "filtering",
    ],
    "embeddings": [
        "text embeddings", "multilingual embeddings", "sentence encoding",
    ],
    "evaluation": [
        "LLM-as-judge", "eval harness", "A/B testing", "regression tests",
    ],
    "benchmarks": [
        "reasoning benchmarks", "MMLU", "agent benchmarks", "leaderboards",
    ],
    "tool-use": [
        "function calling", "tool registry", "tool routing", "API bindings",
    ],
    "mcp-protocol": [
        "MCP server", "MCP client", "tool gateway", "resource registry",
    ],
    "llm-serving": [
        "inference engine", "batched serving", "streaming", "KV cache",
    ],
    "fine-tuning": [
        "SFT", "LoRA", "QLoRA", "preference optimization", "DPO",
    ],
    "distributed-training": [
        "FSDP", "DeepSpeed", "Megatron", "multi-GPU", "pipeline parallel",
    ],
    "quantization": [
        "INT8 quant", "INT4 quant", "GPTQ", "AWQ", "weight compression",
    ],
    "model-merging": [
        "model merging", "MoE", "sparse experts", "TIES merge",
    ],
    "guardrails": [
        "content moderation", "jailbreak detection", "PII redaction", "output filter",
    ],
    "safety-alignment": [
        "RLHF", "constitutional AI", "red-teaming", "alignment eval",
    ],
    "privacy-federated": [
        "federated learning", "differential privacy", "secure aggregation",
    ],
    "observability": [
        "tracing", "token logging", "cost tracking", "latency metrics",
    ],
    "memory": [
        "long-term memory", "episodic memory", "context window", "memory store",
    ],
    "knowledge-graphs": [
        "entity extraction", "relation extraction", "graph RAG", "KG query",
    ],
    "synthetic-data": [
        "data generation", "distillation", "self-instruct", "data augmentation",
    ],
    "data-pipelines": [
        "data ingestion", "ETL", "deduplication", "tokenization",
    ],
    "dev-tools": [
        "SDK", "CLI", "notebook templates", "debugging",
    ],
    "code-llms": [
        "code completion", "code generation", "code repair", "repo understanding",
    ],
    "code-assistants": [
        "IDE integration", "inline completion", "chat", "refactor",
    ],
    "terminal-cli": [
        "shell commands", "terminal automation", "CLI agent",
    ],
    "browser-automation": [
        "web scraping", "form filling", "page navigation", "DOM interaction",
    ],
    "computer-use": [
        "screen capture", "mouse/keyboard", "GUI automation", "OS control",
    ],
    "multimodal": [
        "vision", "image understanding", "OCR", "audio transcription",
    ],
    "image-generation": [
        "text-to-image", "image editing", "inpainting", "ControlNet",
    ],
    "video-generation": [
        "text-to-video", "video editing", "frame interpolation",
    ],
    "audio-tts": [
        "text-to-speech", "voice cloning", "audio synthesis",
    ],
    "speech-recognition": [
        "ASR", "streaming transcription", "speaker diarization",
    ],
    "translation": [
        "machine translation", "multilingual", "alignment",
    ],
    "chat-ui": [
        "chat interface", "streaming UI", "model selector", "history",
    ],
    "workflow-orchestration": [
        "DAG", "node graph", "pipeline builder", "visual editor",
    ],
    "data-analysis": [
        "SQL generation", "charting", "pandas", "notebook analysis",
    ],
    "document-processing": [
        "PDF parsing", "OCR", "table extraction", "layout analysis",
    ],
    "knowledge-management": [
        "note graph", "wiki", "second brain", "linking",
    ],
    "education": [
        "tutoring", "quiz generation", "explanation", "curriculum",
    ],
    "research-papers": [
        "arxiv search", "paper summarization", "citation graph",
    ],
    "awesome-lists": [
        "curated index", "resource list", "link collection",
    ],
    "tutorials": [
        "walkthroughs", "examples", "lessons", "guides",
    ],
    "templates-starters": [
        "project templates", "boilerplate", "starter kit",
    ],
    "case-studies": [
        "production reports", "postmortems", "industry benchmarks",
    ],
}

# Keyword → skill mapping for extracting from summaries. When the
# summary mentions one of these keywords, the corresponding skill is
# added. This catches capabilities the category map misses.
KEYWORD_SKILLS: list[tuple[str, str]] = [
    (r"\btool[ -]?use\b", "tool use"),
    (r"\bfunction[ -]?calling\b", "function calling"),
    (r"\bstructured output\b", "structured output"),
    (r"\bRAG\b|\bretrieval[ -]augmented\b", "RAG"),
    (r"\bchunking\b", "chunking"),
    (r"\brerank", "reranking"),
    (r"\bembed", "embeddings"),
    (r"\bvector store\b|\bvector db\b|\bANN\b", "vector search"),
    (r"\bMCP\b|model context protocol", "MCP server"),
    (r"\bagent\b", "agents"),
    (r"\bReAct\b", "ReAct"),
    (r"\bplanning\b", "planning"),
    (r"\bmemory\b", "memory"),
    (r"\bguardrail", "guardrails"),
    (r"\bmoderation\b", "content moderation"),
    (r"\bjailbreak\b", "jailbreak detection"),
    (r"\bPII\b", "PII redaction"),
    (r"\bRLHF\b", "RLHF"),
    (r"\bDPO\b", "DPO"),
    (r"\bLoRA\b|\bQLoRA\b", "LoRA"),
    (r"\bSFT\b|supervised fine[ -]?tun", "SFT"),
    (r"\bquantiz", "quantization"),
    (r"\bGPTQ\b|\bAWQ\b", "weight compression"),
    (r"\bDeepSpeed\b|\bFSDP\b|\bMegatron\b", "distributed training"),
    (r"\bMoE\b|mixture[ -]of[ -]experts", "MoE"),
    (r"\bmodel merg", "model merging"),
    (r"\bbenchmark\b|\beval\b", "evaluation"),
    (r"\bLLM[ -]as[ -]judge\b", "LLM-as-judge"),
    (r"\btracing\b|\bote?lemetry\b", "tracing"),
    (r"\bcost track", "cost tracking"),
    (r"\bknowledge graph\b|\bKG\b", "knowledge graph"),
    (r"\bsynthetic data\b", "synthetic data"),
    (r"\bdata pipeline\b|\bETL\b", "data pipeline"),
    (r"\bcode completion\b|\bautocomplete\b", "code completion"),
    (r"\bcode generation\b", "code generation"),
    (r"\bIDE\b|\bVS ?Code\b|\bJetBrains\b", "IDE integration"),
    (r"\bterminal\b|\bshell\b|\bCLI\b", "CLI"),
    (r"\bbrowser\b|\bweb ?automation\b|\bselenium\b|\bplaywright\b", "browser automation"),
    (r"\bcomputer use\b|\bscreen capture\b|\bGUI automation\b", "computer use"),
    (r"\bvision\b|\bimage understanding\b", "vision"),
    (r"\bOCR\b", "OCR"),
    (r"\btext[ -]to[ -]image\b|\bimage gen", "text-to-image"),
    (r"\bControlNet\b", "ControlNet"),
    (r"\binpaint", "inpainting"),
    (r"\btext[ -]to[ -]video\b|\bvideo gen", "text-to-video"),
    (r"\bTTS\b|text[ -]to[ -]speech", "text-to-speech"),
    (r"\bvoice cloning\b", "voice cloning"),
    (r"\bASR\b|speech[ -]to[ -]text|transcription", "ASR"),
    (r"\bspeaker diariz", "speaker diarization"),
    (r"\btranslat", "translation"),
    (r"\bchat UI\b|\bchat interface\b|\bchatbot UI\b", "chat UI"),
    (r"\bstreaming UI\b", "streaming UI"),
    (r"\bworkflow\b|\bDAG\b|\bnode graph\b", "workflow orchestration"),
    (r"\bSQL\b", "SQL generation"),
    (r"\bchart\b|\bvisualization\b", "charting"),
    (r"\bPDF\b", "PDF parsing"),
    (r"\btable extraction\b", "table extraction"),
    (r"\bnote graph\b|\bsecond brain\b|\bwiki\b", "knowledge management"),
    (r"\btutor", "tutoring"),
    (r"\bquiz\b", "quiz generation"),
    (r"\barxiv\b", "arxiv search"),
    (r"\bpaper summar", "paper summarization"),
    (r"\btemplate\b|\bboilerplate\b|\bstarter kit\b", "project templates"),
    (r"\bpostmortem\b|\bcase study\b", "case studies"),
    (r"\bawesome\b|\bcurated list\b", "curated index"),
    (r"\btutorial\b|\bwalkthrough\b", "tutorials"),
    (r"\bprompt\b", "prompts"),
    (r"\bfine[ -]?tun", "fine-tuning"),
    (r"\binference\b|\bserving\b", "inference serving"),
    (r"\bstreaming\b", "streaming"),
    (r"\bKV cache\b", "KV cache"),
    (r"\bAPI\b", "API"),
    (r"\bSDK\b", "SDK"),
    (r"\bdocker\b|\bkubernetes\b|\bk8s\b", "deployment"),
    (r"\bopen ?source\b", "open-source"),
]


def derive_skills(entry: dict) -> list[str]:
    """Derive a skills list from category + tags + summary."""
    cat = entry.get("category", "")
    summary = (entry.get("summary") or "").lower()
    tags = [t.lower() for t in (entry.get("tags") or [])]

    skills: list[str] = []
    seen: set[str] = set()

    def add(s: str) -> None:
        key = s.lower()
        if key not in seen:
            seen.add(key)
            skills.append(s)

    # 1. Category-derived canonical skills
    for s in CATEGORY_SKILLS.get(cat, []):
        add(s)

    # 2. Keyword extraction from summary
    for pattern, skill in KEYWORD_SKILLS:
        if re.search(pattern, summary, re.IGNORECASE):
            add(skill)

    # 3. Tags that look like concrete capabilities (not just vendor names)
    # Tags like "claude", "openai", "gpt" are vendor names, skip those.
    VENDOR_TAGS = {
        "claude", "anthropic", "openai", "gpt", "gemini", "google", "vertex",
        "meta", "llama", "mistral", "cohere", "nvidia", "microsoft", "azure",
        "aws", "huggingface", "hf", "langchain", "llamaindex", "official",
        "awesome", "community", "indie", "personal",
    }
    for tag in tags:
        if tag in VENDOR_TAGS:
            continue
        # Skip very short or generic tags
        if len(tag) < 3:
            continue
        # Use the tag as-is if it looks like a capability
        add(tag)

    # Cap at 8 to keep cards scannable
    return skills[:8]


def main() -> int:
    if not SKILLS_YAML.exists():
        print(f"  error  {SKILLS_YAML} not found", file=sys.stderr)
        return 1

    yaml = YAML(typ="rt")
    yaml.preserve_quotes = True
    yaml.width = 4096  # avoid line wrapping
    with SKILLS_YAML.open(encoding="utf-8") as f:
        data = yaml.load(f)

    skills = data.get("skills", []) if data else []
    enriched = 0
    for s in skills:
        new_skills = derive_skills(s)
        if new_skills:
            s["skills"] = new_skills
            enriched += 1
        elif "skills" in s:
            del s["skills"]

    with SKILLS_YAML.open("w", encoding="utf-8") as f:
        yaml.dump(data, f)

    print(f"  enriched {enriched}/{len(skills)} repos with skills field")
    return 0


if __name__ == "__main__":
    sys.exit(main())

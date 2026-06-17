import os

REPORTS_DIR = "research_reports"

def perform_web_search(query: str) -> str:
    """Performs a web search to gather information, compare alternatives, or validate facts.
    
    Args:
        query: The search term (e.g. 'latest trends in Rust async framework 2026').
    """
    # Rich mock search results based on the query to make local agent runs interactive and realistic
    query_lower = query.lower()
    
    if "rust" in query_lower:
        return (
            "1. Rust Async Ecosystem 2026: Tokio 2.0 has stabilizing features for custom event loops. "
            "Actix-web remains highly popular, but Axum is currently the dominant framework for REST APIs "
            "due to its direct integration with Tower. Rust async closures are fully stable in edition 2024.\n"
            "2. Certifications: 'Rust Associate' and 'Professional' are emerging standard certifications "
            "offered by the Rust Foundation."
        )
    elif "cert" in query_lower or "career" in query_lower or "job" in query_lower:
        return (
            "1. Job Market Trends 2026: Cloud architecture (AWS, GCP) and System Engineering (Rust, Go) "
            "are seeing high demand. Leading certifications: AWS Solutions Architect, GCP Professional Cloud Developer.\n"
            "2. AI Engineering: Multi-agent orchestration is a key trend in business process automation."
        )
    elif "wellness" in query_lower or "sleep" in query_lower or "exercise" in query_lower:
        return (
            "1. Sleep Science: Studies show 7.5 to 8.5 hours of sleep optimizes cognitive function and memory consolidation. "
            "Blue light blocking 1h before bed increases melatonin production.\n"
            "2. Exercise: 150 minutes of moderate cardiovascular activity per week significantly improves mental focus."
        )
    else:
        return (
            f"Search results for '{query}': Found high-quality articles detailing recent advancements and structural guides. "
            "Multi-agent frameworks, particularly Google ADK 2.0, are gaining rapid adoption among developers looking "
            "for engineering-first, code-driven multi-agent orchestrations."
        )

def compile_research_report(topic: str, findings: str, sources: list[str] = None) -> str:
    """Compiles findings and sources into a structured research report file saved locally.
    
    Args:
        topic: The topic of the research.
        findings: Comprehensive summary of findings.
        sources: List of source URLs or citations.
    """
    try:
        if not os.path.exists(REPORTS_DIR):
            os.makedirs(REPORTS_DIR)
            
        safe_topic = "".join([c if c.isalnum() or c in (" ", "-", "_") else "" for c in topic]).strip().replace(" ", "_")
        filename = f"{REPORTS_DIR}/{safe_topic}_report.md"
        
        sources_list = sources or ["Simulated Digital Twin Search"]
        formatted_sources = "\n".join([f"- {s}" for s in sources_list])
        
        content = (
            f"# Research Report: {topic}\n\n"
            f"## Executive Summary\n{findings}\n\n"
            f"## Sources & Citations\n{formatted_sources}\n"
        )
        
        with open(filename, "w", encoding="utf-8") as f:
            f.write(content)
            
        return f"Successfully compiled and saved research report to '{filename}'."
    except Exception as e:
        return f"Error compiling research report: {str(e)}"

from typing import Dict, Any

def generate_markdown_report(query: str, raw_data: Dict[str, Any]) -> str:
    """
    Takes the structured RAG response and formats it into a clean, 
    clinical Markdown document for export or sharing.
    """
    
    # Extract components
    population = raw_data.get("population", "N/A")
    intervention = raw_data.get("intervention", "N/A")
    comparison = raw_data.get("comparison", "N/A")
    outcome = raw_data.get("outcome", "N/A")
    answer = raw_data.get("answer", "No synthesis provided.")
    sources = raw_data.get("sources", [])
    
    # Build document
    md = f"# OpenMedica Clinical Note\n\n"
    md += f"**Clinical Query:** {query}\n\n"
    
    md += f"## Clinical Context (PICO)\n"
    md += f"- **Population:** {population}\n"
    md += f"- **Intervention:** {intervention}\n"
    md += f"- **Comparison:** {comparison}\n"
    md += f"- **Outcome:** {outcome}\n\n"
    
    md += f"## Synthesis\n{answer}\n\n"
    
    md += f"## References\n"
    if not sources:
        md += "No sources cited.\n"
    else:
        for i, src in enumerate(sources, 1):
            title = src.get("title", "Unknown Title")
            pmid = src.get("pmid", "Unknown PMID")
            year = src.get("pub_year", 0)
            year_str = str(year) if year > 0 else "Unknown Year"
            
            pub_types = src.get("publication_types", [])
            types_str = ", ".join(pub_types) if pub_types else "Study"
            
            md += f"{i}. {title}\n"
            md += f"   *(PMID: {pmid} | Year: {year_str} | {types_str})*\n"
            
    return md

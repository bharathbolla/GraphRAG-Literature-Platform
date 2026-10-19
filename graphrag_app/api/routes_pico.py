import io
import csv
from typing import Optional
from fastapi import APIRouter
from fastapi.responses import StreamingResponse
from state import app_state

router = APIRouter()

@router.get("/pico")
async def get_pico_matrix(drug: Optional[str] = None, condition: Optional[str] = None):
    """Returns structured PICO clinical trial rows for matrix comparison and filtering."""
    rows = []
    for art in app_state.articles:
        pmid = art.pmid
        pico = art.pico
        if not pico:
            continue
            
        pop = pico.population
        inter = pico.interventions[0] if pico.interventions else None
        comp = pico.comparators[0] if pico.comparators else None
        outcomes = pico.outcomes
        
        study_code = art.title.split("(")[-1].replace(")", "") if "(" in art.title else art.title[:20]
        
        # Filters
        if drug and inter and (drug.lower() not in inter.name.lower()):
            continue
        if condition and pop and (condition.lower() not in pop.condition.lower()):
            continue
            
        for out in outcomes:
            rows.append({
                "pmid": pmid,
                "study_acronym": study_code,
                "journal_year": f"{art.journal.split()[0]} {art.year}",
                "study_design": art.study_design,
                "sample_size": pop.n if pop and pop.n else 0,
                "population": pop.description if pop else "N/A",
                "population_quote": pop.evidence if pop else "",
                "intervention": f"{inter.name} ({inter.dose})" if inter else "N/A",
                "intervention_quote": inter.evidence if inter else "",
                "comparator": comp.name if comp else "Placebo",
                "outcome": out.name,
                "effect_size": f"{out.measure} {out.effect}",
                "ci_95": f"({out.ci_low} - {out.ci_high})",
                "p_value": out.p_value or "",
                "direction": out.direction,
                "evidence_quote": out.evidence
            })
            
    return {"pico_rows": rows, "total_rows": len(rows)}

@router.get("/export/pico.csv")
async def export_pico_csv():
    """Generates an RFC 4180 compliant CSV of the PICO grid for systematic literature review workflows."""
    output = io.StringIO()
    writer = csv.writer(output)
    
    headers = [
        "PMID", "Study Acronym", "Journal & Year", "Study Design", "Sample Size (N)",
        "Population Description", "Intervention", "Comparator", "Clinical Outcome",
        "Effect Size", "95% Confidence Interval", "P-Value", "Direction", "Verbatim Evidence Quote"
    ]
    writer.writerow(headers)
    
    for art in app_state.articles:
        pmid = art.pmid
        pico = art.pico
        if not pico:
            continue
        pop = pico.population
        inter = pico.interventions[0] if pico.interventions else None
        comp = pico.comparators[0] if pico.comparators else None
        study_code = art.title.split("(")[-1].replace(")", "") if "(" in art.title else art.title[:20]
        
        for out in pico.outcomes:
            writer.writerow([
                pmid,
                study_code,
                f"{art.journal} ({art.year})",
                art.study_design,
                pop.n if pop and pop.n else "",
                pop.description if pop else "",
                f"{inter.name} {inter.dose}" if inter else "",
                comp.name if comp else "Placebo",
                out.name,
                f"{out.measure} {out.effect}",
                f"{out.ci_low} - {out.ci_high}",
                out.p_value or "",
                out.direction,
                out.evidence
            ])
            
    output.seek(0)
    return StreamingResponse(
        io.BytesIO(output.getvalue().encode("utf-8")),
        media_type="text/csv",
        headers={"Content-Disposition": "attachment; filename=GraphRAG_PICO_Evidence_Matrix.csv"}
    )

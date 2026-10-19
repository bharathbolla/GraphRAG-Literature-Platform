from fastapi import APIRouter
from fastapi.responses import JSONResponse
from typing import List, Dict, Any
from state import app_state

router = APIRouter()

@router.get("/ner")
async def get_ner():
    """Returns all normalized biomedical entities indexed across the active corpus."""
    entities_map: Dict[tuple, dict] = {}
    
    for art in app_state.articles:
        pmid = art.pmid
        for ent in art.entities:
            key = (ent.name, ent.type.value if hasattr(ent.type, "value") else str(ent.type), ent.cui or "")
            if key not in entities_map:
                entities_map[key] = {
                    "name": ent.name,
                    "type": ent.type.value if hasattr(ent.type, "value") else str(ent.type),
                    "cui": ent.cui or "Unassigned",
                    "rxnorm": ent.rxnorm,
                    "papers_count": 0,
                    "pmids": []
                }
            if pmid not in entities_map[key]["pmids"]:
                entities_map[key]["papers_count"] += 1
                entities_map[key]["pmids"].append(pmid)
                
    result = list(entities_map.values())
    result.sort(key=lambda x: x["papers_count"], reverse=True)
    return {"entities": result}

@router.get("/ner/{entity_name}/cooccurrences")
async def get_entity_cooccurrences(entity_name: str):
    """Calculates entity co-occurrence counts across all indexed clinical trials."""
    target = entity_name.lower().strip()
    cooccur: Dict[str, dict] = {}
    
    for art in app_state.articles:
        ent_names = [e.name.lower() for e in art.entities]
        if any(target in en for en in ent_names):
            for e in art.entities:
                if e.name.lower() != target:
                    key = e.name
                    if key not in cooccur:
                        cooccur[key] = {
                            "entity": e.name,
                            "type": e.type.value if hasattr(e.type, "value") else str(e.type),
                            "cui": e.cui or "Unassigned",
                            "co_occurrences": 0
                        }
                    cooccur[key]["co_occurrences"] += 1
                    
    sorted_co = list(cooccur.values())
    sorted_co.sort(key=lambda x: x["co_occurrences"], reverse=True)
    return {"target_entity": entity_name, "cooccurrences": sorted_co[:12]}

@router.get("/ner/{entity_name}/mentions")
async def get_entity_mentions(entity_name: str):
    """Returns trial publications and exact supporting sentences mentioning the target entity."""
    target = entity_name.lower().strip()
    mentions = []
    
    for art in app_state.articles:
        ent_names = [e.name.lower() for e in art.entities]
        if any(target in en for en in ent_names):
            # Find evidence sentence
            evidence = ""
            if art.pico:
                # check outcome
                for out in art.pico.outcomes:
                    if target in out.name.lower():
                        evidence = out.evidence
                        break
                # check intervention
                if not evidence:
                    for inter in art.pico.interventions:
                        if target in inter.name.lower():
                            evidence = inter.evidence
                            break
                # check population
                if not evidence and art.pico.population:
                    if target in art.pico.population.condition.lower() or target in art.pico.population.description.lower():
                        evidence = art.pico.population.evidence

            if not evidence:
                evidence = art.abstract.split("\n")[0] if "\n" in art.abstract else art.abstract[:200]
                
            study_code = art.title.split("(")[-1].replace(")", "") if "(" in art.title else art.title[:25]
            mentions.append({
                "pmid": art.pmid,
                "study_acronym": study_code,
                "title": art.title,
                "journal_year": f"{art.journal} ({art.year})",
                "study_design": art.study_design,
                "sample_size": art.sample_size,
                "evidence_sentence": evidence
            })
            
    return {"target_entity": entity_name, "total_mentions": len(mentions), "mentions": mentions}

@router.get("/ner/export/concepts.json")
async def export_concepts_json():
    """Exports all normalized UMLS Concept Unique Identifiers (CUIs) and metadata in JSON."""
    concepts = []
    for art in app_state.articles:
        for ent in art.entities:
            concepts.append({
                "cui": ent.cui or "Unassigned",
                "name": ent.name,
                "type": ent.type.value if hasattr(ent.type, "value") else str(ent.type),
                "rxnorm": ent.rxnorm,
                "pmid": art.pmid
            })
    return JSONResponse(
        content={"catalog_version": "2.0", "concepts": concepts},
        headers={"Content-Disposition": "attachment; filename=Biomedical_Concept_Catalog.json"}
    )

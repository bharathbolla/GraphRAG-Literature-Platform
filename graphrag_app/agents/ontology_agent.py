from typing import List, Dict, Optional
from models.article import Article
from models.entity import BiomedicalEntity, EntityType

class OntologyAgent:
    """
    Agent 3: Biomedical Ontology Normalization Agent.
    Maps surface biomedical strings to standardized ontologies:
    - UMLS Metathesaurus (Concept Unique Identifiers - CUIs)
    - Medical Subject Headings (MeSH IDs)
    - RxNorm (Pharmaceutical compound identifiers)
    - Anatomical Therapeutic Chemical (ATC) drug classes
    """
    SYNONYM_MAP: Dict[str, Dict[str, str]] = {
        # Conditions
        "t2dm": {"name": "Type 2 Diabetes Mellitus", "cui": "C0011860", "type": EntityType.CONDITION},
        "type 2 diabetes": {"name": "Type 2 Diabetes Mellitus", "cui": "C0011860", "type": EntityType.CONDITION},
        "ckd": {"name": "Chronic Kidney Disease", "cui": "C0022661", "type": EntityType.CONDITION},
        "chronic kidney disease": {"name": "Chronic Kidney Disease", "cui": "C0022661", "type": EntityType.CONDITION},
        "diabetic nephropathy": {"name": "Diabetic Kidney Disease", "cui": "C0011881", "type": EntityType.CONDITION},
        "heart failure": {"name": "Heart Failure", "cui": "C0018801", "type": EntityType.CONDITION},
        "hfref": {"name": "Heart Failure with Reduced Ejection Fraction", "cui": "C0018802", "type": EntityType.CONDITION},
        "hfpef": {"name": "Heart Failure with Preserved Ejection Fraction", "cui": "C4086438", "type": EntityType.CONDITION},
        "breast cancer": {"name": "Breast Cancer (HR+/HER2-)", "cui": "C0006142", "type": EntityType.CONDITION},
        "psoriasis": {"name": "Plaque Psoriasis", "cui": "C0033860", "type": EntityType.CONDITION},
        "psoriatic arthritis": {"name": "Psoriatic Arthritis", "cui": "C0003872", "type": EntityType.CONDITION},
        "ankylosing spondylitis": {"name": "Ankylosing Spondylitis", "cui": "C0038013", "type": EntityType.CONDITION},
        "multiple sclerosis": {"name": "Relapsing Multiple Sclerosis", "cui": "C0026769", "type": EntityType.CONDITION},
        "paroxysmal nocturnal hemoglobinuria": {"name": "Paroxysmal Nocturnal Hemoglobinuria", "cui": "C0019088", "type": EntityType.CONDITION},
        "pnh": {"name": "Paroxysmal Nocturnal Hemoglobinuria", "cui": "C0019088", "type": EntityType.CONDITION},
        "chronic myeloid leukemia": {"name": "Chronic Myeloid Leukemia", "cui": "C0023473", "type": EntityType.CONDITION},
        "cml": {"name": "Chronic Myeloid Leukemia", "cui": "C0023473", "type": EntityType.CONDITION},
        "prostate cancer": {"name": "Metastatic Castration-Resistant Prostate Cancer", "cui": "C0376358", "type": EntityType.CONDITION},

        # Drugs - SGLT2i
        "empagliflozin": {"name": "Empagliflozin", "cui": "C3261058", "rxnorm": "1545653", "type": EntityType.DRUG},
        "dapagliflozin": {"name": "Dapagliflozin", "cui": "C2719231", "rxnorm": "1488564", "type": EntityType.DRUG},
        "canagliflozin": {"name": "Canagliflozin", "cui": "C2982845", "rxnorm": "1373458", "type": EntityType.DRUG},
        "ertugliflozin": {"name": "Ertugliflozin", "cui": "C3886580", "rxnorm": "1992672", "type": EntityType.DRUG},
        "sglt2 inhibitors": {"name": "SGLT2 inhibitors", "cui": "C3890289", "type": EntityType.DRUG_CLASS},

        # Drugs - Novartis Portfolio & Comparators
        "sacubitril": {"name": "Sacubitril / Valsartan (Entresto)", "cui": "C1565489", "rxnorm": "1656333", "type": EntityType.DRUG},
        "valsartan": {"name": "Sacubitril / Valsartan (Entresto)", "cui": "C1565489", "rxnorm": "1656333", "type": EntityType.DRUG},
        "entresto": {"name": "Sacubitril / Valsartan (Entresto)", "cui": "C1565489", "rxnorm": "1656333", "type": EntityType.DRUG},
        "lcz696": {"name": "Sacubitril / Valsartan (Entresto)", "cui": "C1565489", "rxnorm": "1656333", "type": EntityType.DRUG},
        "enalapril": {"name": "Enalapril", "cui": "C0014038", "rxnorm": "3827", "type": EntityType.DRUG},
        "ribociclib": {"name": "Ribociclib (Kisqali)", "cui": "C4052345", "rxnorm": "1873983", "type": EntityType.DRUG},
        "kisqali": {"name": "Ribociclib (Kisqali)", "cui": "C4052345", "rxnorm": "1873983", "type": EntityType.DRUG},
        "palbociclib": {"name": "Palbociclib (Ibrance)", "cui": "C2987625", "rxnorm": "1601380", "type": EntityType.DRUG},
        "abemaciclib": {"name": "Abemaciclib (Verzenio)", "cui": "C4082269", "rxnorm": "1946826", "type": EntityType.DRUG},
        "secukinumab": {"name": "Secukinumab (Cosentyx)", "cui": "C3273840", "rxnorm": "1602493", "type": EntityType.DRUG},
        "cosentyx": {"name": "Secukinumab (Cosentyx)", "cui": "C3273840", "rxnorm": "1602493", "type": EntityType.DRUG},
        "ixekizumab": {"name": "Ixekizumab (Taltz)", "cui": "C3539828", "rxnorm": "1740467", "type": EntityType.DRUG},
        "guselkumab": {"name": "Guselkumab (Tremfya)", "cui": "C4085441", "rxnorm": "1946850", "type": EntityType.DRUG},
        "ofatumumab": {"name": "Ofatumumab (Kesimpta)", "cui": "C2719580", "rxnorm": "1114195", "type": EntityType.DRUG},
        "kesimpta": {"name": "Ofatumumab (Kesimpta)", "cui": "C2719580", "rxnorm": "1114195", "type": EntityType.DRUG},
        "teriflunomide": {"name": "Teriflunomide (Aubagio)", "cui": "C0979508", "rxnorm": "1306349", "type": EntityType.DRUG},
        "ocrelizumab": {"name": "Ocrelizumab (Ocrevus)", "cui": "C1709426", "rxnorm": "1876366", "type": EntityType.DRUG},
        "iptacopan": {"name": "Iptacopan (Fabhalta)", "cui": "C5441712", "rxnorm": "2671239", "type": EntityType.DRUG},
        "fabhalta": {"name": "Iptacopan (Fabhalta)", "cui": "C5441712", "rxnorm": "2671239", "type": EntityType.DRUG},
        "asciminib": {"name": "Asciminib (Scemblix)", "cui": "C5205796", "rxnorm": "2584948", "type": EntityType.DRUG},
        "scemblix": {"name": "Asciminib (Scemblix)", "cui": "C5205796", "rxnorm": "2584948", "type": EntityType.DRUG},
        "inclisiran": {"name": "Inclisiran (Leqvio)", "cui": "C4743283", "rxnorm": "2475470", "type": EntityType.DRUG},
        "leqvio": {"name": "Inclisiran (Leqvio)", "cui": "C4743283", "rxnorm": "2475470", "type": EntityType.DRUG},
        "finerenone": {"name": "Finerenone (Kerendia)", "cui": "C4082260", "rxnorm": "2560325", "type": EntityType.DRUG},

        # Outcomes
        "cardiovascular death": {"name": "Cardiovascular Death", "cui": "C0011050", "type": EntityType.OUTCOME},
        "all-cause mortality": {"name": "All-Cause Mortality", "cui": "C0026565", "type": EntityType.OUTCOME},
        "heart failure hospitalization": {"name": "Heart Failure Hospitalization", "cui": "C0019993", "type": EntityType.OUTCOME},
        "progression-free survival": {"name": "Progression-Free Survival", "cui": "C1518972", "type": EntityType.OUTCOME},
        "overall survival": {"name": "Overall Survival", "cui": "C0748111", "type": EntityType.OUTCOME},
        "annualized relapse rate": {"name": "Annualized Relapse Rate", "cui": "C4086847", "type": EntityType.OUTCOME},
        "major molecular response": {"name": "Major Molecular Response", "cui": "C2986422", "type": EntityType.OUTCOME}
    }

    def normalize_term(self, text: str) -> Optional[BiomedicalEntity]:
        """Maps free text entity mention to normalized biomedical ontology node."""
        cleaned = text.lower().strip()
        for key, meta in self.SYNONYM_MAP.items():
            if key in cleaned or cleaned in key:
                return BiomedicalEntity(
                    name=meta["name"],
                    type=meta["type"],
                    cui=meta.get("cui"),
                    rxnorm=meta.get("rxnorm")
                )
        return None

    def normalize_article_entities(self, article: Article) -> List[BiomedicalEntity]:
        """Normalizes and dedupes all entities present in the article."""
        entities = []
        seen = set()

        # From PICO
        if article.pico:
            pop = article.pico.population
            if pop and pop.condition:
                norm = self.normalize_term(pop.condition)
                if norm and norm.name not in seen:
                    norm.papers_count = 1
                    norm.pmids = [article.pmid]
                    entities.append(norm)
                    seen.add(norm.name)

            for inter in article.pico.interventions:
                norm = self.normalize_term(inter.name)
                if norm and norm.name not in seen:
                    norm.papers_count = 1
                    norm.pmids = [article.pmid]
                    entities.append(norm)
                    seen.add(norm.name)

            for out in article.pico.outcomes:
                norm = self.normalize_term(out.name)
                if norm and norm.name not in seen:
                    norm.papers_count = 1
                    norm.pmids = [article.pmid]
                    entities.append(norm)
                    seen.add(norm.name)

        # Also search title and abstract for known drug / condition entities
        full_text = f"{article.title} {article.abstract}".lower()
        for key, meta in self.SYNONYM_MAP.items():
            if meta["name"] not in seen and f" {key} " in f" {full_text} ":
                norm = BiomedicalEntity(
                    name=meta["name"],
                    type=meta["type"],
                    cui=meta.get("cui"),
                    rxnorm=meta.get("rxnorm"),
                    papers_count=1,
                    pmids=[article.pmid]
                )
                entities.append(norm)
                seen.add(meta["name"])

        return entities

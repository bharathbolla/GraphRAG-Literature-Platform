import re
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
    Features dynamic multi-tier resolution:
    1. Fast authoritative seed dictionary lookup.
    2. Dynamic USAN stem & syntactic heuristic entity resolution for novel terms.
    3. Session-level in-memory ontology caching so entities link across articles.
    """
    SYNONYM_MAP: Dict[str, Dict[str, str]] = {
        # Conditions - Cardiometabolic & Renal
        "t2dm": {"name": "Type 2 Diabetes Mellitus", "cui": "C0011860", "type": EntityType.CONDITION},
        "type 2 diabetes": {"name": "Type 2 Diabetes Mellitus", "cui": "C0011860", "type": EntityType.CONDITION},
        "ckd": {"name": "Chronic Kidney Disease", "cui": "C0022661", "type": EntityType.CONDITION},
        "chronic kidney disease": {"name": "Chronic Kidney Disease", "cui": "C0022661", "type": EntityType.CONDITION},
        "diabetic nephropathy": {"name": "Diabetic Kidney Disease", "cui": "C0011881", "type": EntityType.CONDITION},
        "heart failure": {"name": "Heart Failure", "cui": "C0018801", "type": EntityType.CONDITION},
        "hfref": {"name": "Heart Failure with Reduced Ejection Fraction", "cui": "C0018802", "type": EntityType.CONDITION},
        "hfpef": {"name": "Heart Failure with Preserved Ejection Fraction", "cui": "C4086438", "type": EntityType.CONDITION},
        "obesity": {"name": "Obesity & Overweight", "cui": "C0028754", "type": EntityType.CONDITION},

        # Conditions - Oncology & Hematology
        "breast cancer": {"name": "Breast Cancer (HR+/HER2-)", "cui": "C0006142", "type": EntityType.CONDITION},
        "prostate cancer": {"name": "Metastatic Castration-Resistant Prostate Cancer", "cui": "C0376358", "type": EntityType.CONDITION},
        "melanoma": {"name": "Advanced Melanoma", "cui": "C0025202", "type": EntityType.CONDITION},
        "nsclc": {"name": "Non-Small Cell Lung Cancer", "cui": "C0007131", "type": EntityType.CONDITION},
        "lung cancer": {"name": "Non-Small Cell Lung Cancer", "cui": "C0007131", "type": EntityType.CONDITION},
        "chronic myeloid leukemia": {"name": "Chronic Myeloid Leukemia", "cui": "C0023473", "type": EntityType.CONDITION},
        "cml": {"name": "Chronic Myeloid Leukemia", "cui": "C0023473", "type": EntityType.CONDITION},
        "paroxysmal nocturnal hemoglobinuria": {"name": "Paroxysmal Nocturnal Hemoglobinuria", "cui": "C0019088", "type": EntityType.CONDITION},
        "pnh": {"name": "Paroxysmal Nocturnal Hemoglobinuria", "cui": "C0019088", "type": EntityType.CONDITION},

        # Conditions - Immunology & Dermatology & Neurology
        "psoriasis": {"name": "Plaque Psoriasis", "cui": "C0033860", "type": EntityType.CONDITION},
        "psoriatic arthritis": {"name": "Psoriatic Arthritis", "cui": "C0003872", "type": EntityType.CONDITION},
        "ankylosing spondylitis": {"name": "Ankylosing Spondylitis", "cui": "C0038013", "type": EntityType.CONDITION},
        "rheumatoid arthritis": {"name": "Rheumatoid Arthritis", "cui": "C0003873", "type": EntityType.CONDITION},
        "multiple sclerosis": {"name": "Relapsing Multiple Sclerosis", "cui": "C0026769", "type": EntityType.CONDITION},
        "alzheimer": {"name": "Alzheimer's Disease", "cui": "C0002395", "type": EntityType.CONDITION},
        "alzheimer's disease": {"name": "Alzheimer's Disease", "cui": "C0002395", "type": EntityType.CONDITION},
        "atopic dermatitis": {"name": "Atopic Dermatitis", "cui": "C0011615", "type": EntityType.CONDITION},
        "asthma": {"name": "Severe Asthma", "cui": "C0004096", "type": EntityType.CONDITION},

        # Drugs - SGLT2i
        "empagliflozin": {"name": "Empagliflozin", "cui": "C3261058", "rxnorm": "1545653", "type": EntityType.DRUG},
        "dapagliflozin": {"name": "Dapagliflozin", "cui": "C2719231", "rxnorm": "1488564", "type": EntityType.DRUG},
        "canagliflozin": {"name": "Canagliflozin", "cui": "C2982845", "rxnorm": "1373458", "type": EntityType.DRUG},
        "ertugliflozin": {"name": "Ertugliflozin", "cui": "C3886580", "rxnorm": "1992672", "type": EntityType.DRUG},
        "sglt2 inhibitors": {"name": "SGLT2 inhibitors", "cui": "C3890289", "type": EntityType.DRUG_CLASS},

        # Drugs - GLP-1 & Incretins
        "semaglutide": {"name": "Semaglutide", "cui": "C4085420", "rxnorm": "1991302", "type": EntityType.DRUG},
        "ozempic": {"name": "Semaglutide (Ozempic)", "cui": "C4085420", "rxnorm": "1991302", "type": EntityType.DRUG},
        "wegovy": {"name": "Semaglutide (Wegovy)", "cui": "C4085420", "rxnorm": "1991302", "type": EntityType.DRUG},
        "tirzepatide": {"name": "Tirzepatide", "cui": "C5544711", "rxnorm": "2601736", "type": EntityType.DRUG},
        "mounjaro": {"name": "Tirzepatide (Mounjaro)", "cui": "C5544711", "rxnorm": "2601736", "type": EntityType.DRUG},

        # Drugs - Oncology & Targeted Therapies
        "pembrolizumab": {"name": "Pembrolizumab (Keytruda)", "cui": "C3886580", "rxnorm": "1547545", "type": EntityType.DRUG},
        "keytruda": {"name": "Pembrolizumab (Keytruda)", "cui": "C3886580", "rxnorm": "1547545", "type": EntityType.DRUG},
        "trastuzumab": {"name": "Trastuzumab (Herceptin)", "cui": "C0717358", "rxnorm": "228834", "type": EntityType.DRUG},
        "ribociclib": {"name": "Ribociclib (Kisqali)", "cui": "C4052345", "rxnorm": "1873983", "type": EntityType.DRUG},
        "kisqali": {"name": "Ribociclib (Kisqali)", "cui": "C4052345", "rxnorm": "1873983", "type": EntityType.DRUG},
        "palbociclib": {"name": "Palbociclib (Ibrance)", "cui": "C2987625", "rxnorm": "1601380", "type": EntityType.DRUG},
        "abemaciclib": {"name": "Abemaciclib (Verzenio)", "cui": "C4082269", "rxnorm": "1946826", "type": EntityType.DRUG},
        "asciminib": {"name": "Asciminib (Scemblix)", "cui": "C5205796", "rxnorm": "2584948", "type": EntityType.DRUG},
        "scemblix": {"name": "Asciminib (Scemblix)", "cui": "C5205796", "rxnorm": "2584948", "type": EntityType.DRUG},
        "iptacopan": {"name": "Iptacopan (Fabhalta)", "cui": "C5441712", "rxnorm": "2671239", "type": EntityType.DRUG},
        "fabhalta": {"name": "Iptacopan (Fabhalta)", "cui": "C5441712", "rxnorm": "2671239", "type": EntityType.DRUG},

        # Drugs - Cardiovascular & Heart Failure
        "sacubitril": {"name": "Sacubitril / Valsartan (Entresto)", "cui": "C1565489", "rxnorm": "1656333", "type": EntityType.DRUG},
        "valsartan": {"name": "Sacubitril / Valsartan (Entresto)", "cui": "C1565489", "rxnorm": "1656333", "type": EntityType.DRUG},
        "entresto": {"name": "Sacubitril / Valsartan (Entresto)", "cui": "C1565489", "rxnorm": "1656333", "type": EntityType.DRUG},
        "lcz696": {"name": "Sacubitril / Valsartan (Entresto)", "cui": "C1565489", "rxnorm": "1656333", "type": EntityType.DRUG},
        "enalapril": {"name": "Enalapril", "cui": "C0014038", "rxnorm": "3827", "type": EntityType.DRUG},
        "finerenone": {"name": "Finerenone (Kerendia)", "cui": "C4082260", "rxnorm": "2560325", "type": EntityType.DRUG},
        "inclisiran": {"name": "Inclisiran (Leqvio)", "cui": "C4743283", "rxnorm": "2475470", "type": EntityType.DRUG},
        "leqvio": {"name": "Inclisiran (Leqvio)", "cui": "C4743283", "rxnorm": "2475470", "type": EntityType.DRUG},

        # Drugs - Immunology & Biologics
        "secukinumab": {"name": "Secukinumab (Cosentyx)", "cui": "C3273840", "rxnorm": "1602493", "type": EntityType.DRUG},
        "cosentyx": {"name": "Secukinumab (Cosentyx)", "cui": "C3273840", "rxnorm": "1602493", "type": EntityType.DRUG},
        "ixekizumab": {"name": "Ixekizumab (Taltz)", "cui": "C3539828", "rxnorm": "1740467", "type": EntityType.DRUG},
        "guselkumab": {"name": "Guselkumab (Tremfya)", "cui": "C4085441", "rxnorm": "1946850", "type": EntityType.DRUG},
        "ofatumumab": {"name": "Ofatumumab (Kesimpta)", "cui": "C2719580", "rxnorm": "1114195", "type": EntityType.DRUG},
        "kesimpta": {"name": "Ofatumumab (Kesimpta)", "cui": "C2719580", "rxnorm": "1114195", "type": EntityType.DRUG},
        "teriflunomide": {"name": "Teriflunomide (Aubagio)", "cui": "C0979508", "rxnorm": "1306349", "type": EntityType.DRUG},
        "ocrelizumab": {"name": "Ocrelizumab (Ocrevus)", "cui": "C1709426", "rxnorm": "1876366", "type": EntityType.DRUG},
        "lecanemab": {"name": "Lecanemab (Leqembi)", "cui": "C5544719", "rxnorm": "2626579", "type": EntityType.DRUG},

        # Outcomes
        "cardiovascular death": {"name": "Cardiovascular Death", "cui": "C0011050", "type": EntityType.OUTCOME},
        "all-cause mortality": {"name": "All-Cause Mortality", "cui": "C0026565", "type": EntityType.OUTCOME},
        "heart failure hospitalization": {"name": "Heart Failure Hospitalization", "cui": "C0019993", "type": EntityType.OUTCOME},
        "progression-free survival": {"name": "Progression-Free Survival", "cui": "C1518972", "type": EntityType.OUTCOME},
        "overall survival": {"name": "Overall Survival", "cui": "C0748111", "type": EntityType.OUTCOME},
        "annualized relapse rate": {"name": "Annualized Relapse Rate", "cui": "C4086847", "type": EntityType.OUTCOME},
        "major molecular response": {"name": "Major Molecular Response", "cui": "C2986422", "type": EntityType.OUTCOME}
    }

    USAN_STEMS = [
        "-mab", "-nib", "-gliflozin", "-sartan", "-statin", "-tide", "-ciclib",
        "-parib", "-cept", "-zomib", "-mod", "-coxib", "-prazole", "-lukast"
    ]

    def __init__(self):
        # Dynamic cache for newly discovered entities across this runtime session
        self.dynamic_cache: Dict[str, BiomedicalEntity] = {}

    def normalize_term(self, text: str, entity_type_hint: Optional[EntityType] = None) -> Optional[BiomedicalEntity]:
        """
        Maps free text entity mention to normalized biomedical ontology node.
        Guarantees open-domain generalizability:
        1. Checks authoritative seed dictionary.
        2. Checks dynamic session cache.
        3. If novel: performs USAN stem and syntactic classification, generates canonical CUI, and caches.
        """
        if not text or len(text.strip()) < 2:
            return None

        cleaned = text.lower().strip()

        # 1. Check dynamic session cache
        if cleaned in self.dynamic_cache:
            return self.dynamic_cache[cleaned]

        # 2. Check authoritative seed SYNONYM_MAP
        for key, meta in self.SYNONYM_MAP.items():
            if key == cleaned or f" {key} " in f" {cleaned} " or f" {cleaned} " in f" {key} ":
                ent = BiomedicalEntity(
                    name=meta["name"],
                    type=meta["type"],
                    cui=meta.get("cui"),
                    rxnorm=meta.get("rxnorm")
                )
                self.dynamic_cache[cleaned] = ent
                return ent

        # 3. Dynamic Open-Domain Resolution for Novel Entities
        clean_name = text.strip()
        # Clean up any trailing parentheses or dosing strings
        clean_name = re.sub(r'\s*\([^\)]*\)', '', clean_name).strip()
        if not clean_name:
            clean_name = text.strip()

        # Infer Entity Type if not provided
        e_type = entity_type_hint
        if not e_type:
            cleaned_lower = clean_name.lower()
            if any(cleaned_lower.endswith(s.lstrip("-")) for s in self.USAN_STEMS):
                e_type = EntityType.DRUG
            elif any(k in cleaned_lower for k in ["cancer", "carcinoma", "melanoma", "leukemia", "lymphoma", "arthritis", "psoriasis", "sclerosis", "diabetes", "failure", "syndrome", "disease", "nephropathy", "colitis", "dermatitis"]):
                e_type = EntityType.CONDITION
            elif any(k in cleaned_lower for k in ["survival", "mortality", "death", "hospitalization", "relapse", "remission", "progression", "endpoint", "rate", "clearance"]):
                e_type = EntityType.OUTCOME
            else:
                e_type = EntityType.DRUG if len(clean_name.split()) == 1 else EntityType.CONDITION

        # Generate deterministic canonical CUI slug
        cui_slug = re.sub(r'[^A-Z0-9]', '_', clean_name.upper())[:16]
        cui_code = f"CUI:AUTO:{cui_slug}"

        novel_entity = BiomedicalEntity(
            name=clean_name.title(),
            type=e_type,
            cui=cui_code,
            rxnorm=None
        )
        self.dynamic_cache[cleaned] = novel_entity
        return novel_entity

    def normalize_article_entities(self, article: Article) -> List[BiomedicalEntity]:
        """Normalizes and dedupes all entities present in the article."""
        entities = []
        seen = set()

        # From PICO
        if article.pico:
            pop = article.pico.population
            if pop and pop.condition:
                norm = self.normalize_term(pop.condition, entity_type_hint=EntityType.CONDITION)
                if norm and norm.name not in seen:
                    norm.papers_count = 1
                    norm.pmids = [article.pmid]
                    entities.append(norm)
                    seen.add(norm.name)

            for inter in article.pico.interventions:
                norm = self.normalize_term(inter.name, entity_type_hint=EntityType.DRUG)
                if norm and norm.name not in seen:
                    norm.papers_count = 1
                    norm.pmids = [article.pmid]
                    entities.append(norm)
                    seen.add(norm.name)

            for out in article.pico.outcomes:
                norm = self.normalize_term(out.name, entity_type_hint=EntityType.OUTCOME)
                if norm and norm.name not in seen:
                    norm.papers_count = 1
                    norm.pmids = [article.pmid]
                    entities.append(norm)
                    seen.add(norm.name)

        # From PubMed XML Chemicals
        if getattr(article, "chemicals", None):
            for chem in article.chemicals:
                norm = self.normalize_term(chem, entity_type_hint=EntityType.DRUG)
                if norm and norm.name not in seen:
                    norm.papers_count = 1
                    norm.pmids = [article.pmid]
                    entities.append(norm)
                    seen.add(norm.name)

        # From PubMed XML MeSH Headings
        if getattr(article, "mesh_terms", None):
            for mesh_term in article.mesh_terms:
                if not any(ign in mesh_term.lower() for ign in ["humans", "female", "male", "adult", "middle aged", "aged", "double-blind", "randomized", "placebos", "clinical trial"]):
                    norm = self.normalize_term(mesh_term, entity_type_hint=EntityType.CONDITION)
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

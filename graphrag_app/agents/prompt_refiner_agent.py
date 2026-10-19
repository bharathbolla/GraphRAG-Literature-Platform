import re
from typing import List, Set
from models.chat import RefinedPrompt, QueryIntent
from models.article import Article, IngestionPromptSuggestion
from agents.llm_client import gemini_client
from config import settings

class PromptRefinerAgent:
    """
    Agent: Autonomous Clinical Prompt Strategy Refiner.
    Inspects user clinical questions, extracts biomedical intents and entities,
    and constructs exactly three refined, high-value prompt formulations:
    1. Head-to-Head Comparative Efficacy
    2. Safety, Tolerability & Biomarker Deep-Dive
    3. Guideline & Class-Level Therapeutic Landscape
    """
    def __init__(self):
        pass

    def generate_refined_prompts(
        self,
        query: str,
        matched_pmids: Set[str],
        active_articles: List[Article]
    ) -> List[RefinedPrompt]:
        """Generates 3 refined prompt variants tailored dynamically via Gemini Flash or domain heuristics."""
        # 1. Attempt dynamic prompt generation via Gemini Flash
        if settings.USE_DYNAMIC_AGENTS and gemini_client.is_available():
            matched_articles = [a for a in active_articles if a.pmid in matched_pmids] or active_articles
            dynamic_suggestions = gemini_client.generate_dynamic_prompts(query, matched_articles)
            if dynamic_suggestions:
                prompts = []
                for s in dynamic_suggestions:
                    prompts.append(
                        RefinedPrompt(
                            category=s.get("category", "Comparative Head-to-Head"),
                            prompt=s.get("prompt", query),
                            rationale=s.get("rationale", "Dynamic clinical inquiry refinement powered by Gemini Flash.")
                        )
                    )
                if len(prompts) == 3:
                    return prompts

        # 2. Heuristic domain fallback
        q = query.lower()

        # Domain 1: Heart Failure & Cardiorenal (Entresto, SGLT2i, CKD)
        if any(k in q for k in ["heart failure", "hf", "kidney", "ckd", "renal", "sacubitril", "entresto", "sglt2", "empagliflozin", "dapagliflozin"]):
            return [
                RefinedPrompt(
                    category="Comparative Head-to-Head",
                    prompt="Compare cardiovascular death and heart failure hospitalization hazard ratios between Sacubitril/Valsartan (PARADIGM-HF) and SGLT2 inhibitors (DAPA-HF, EMPEROR-Reduced).",
                    rationale="Evaluates comparative relative risk reductions across cornerstone neurohormonal and metabolic therapies."
                ),
                RefinedPrompt(
                    category="Safety & Biomarker Deep-Dive",
                    prompt="Compare the incidence of hyperkalemia, acute kidney injury, and treatment discontinuation across heart failure and CKD trials.",
                    rationale="Pinpoints critical safety differentiators, renal hemodynamic impacts, and tolerability profiles."
                ),
                RefinedPrompt(
                    category="Guideline & Class Landscape",
                    prompt="What is the multi-trial consensus regarding 4-pillar GDMT initiation and eGFR preservation across cardiorenal populations?",
                    rationale="Synthesizes guideline-directed medical therapy synergy and long-term renal trajectory benefits."
                )
            ]

        # Domain 2: Oncology / Breast Cancer (CDK4/6, Ribociclib, Kisqali)
        elif any(k in q for k in ["breast cancer", "ribociclib", "kisqali", "cdk4", "palbociclib", "abemaciclib", "oncology", "pfs", "survival"]):
            return [
                RefinedPrompt(
                    category="Comparative Head-to-Head",
                    prompt="Compare progression-free survival (PFS) and overall survival (OS) hazard ratios between Ribociclib, Palbociclib, and Abemaciclib in HR+/HER2- breast cancer.",
                    rationale="Benchmarks efficacy across the CDK4/6 inhibitor class in endocrine-resistant and metastatic settings."
                ),
                RefinedPrompt(
                    category="Safety & Biomarker Deep-Dive",
                    prompt="What are the key safety differentiators regarding QTc prolongation, neutropenia, and diarrhea across CDK4/6 inhibitor trials?",
                    rationale="Analyzes distinct toxicity profiles and dose reduction frequencies across competing agents."
                ),
                RefinedPrompt(
                    category="Guideline & Class Landscape",
                    prompt="What is the clinical consensus evidence for CDK4/6 inhibitors combined with endocrine therapy in early versus metastatic breast cancer?",
                    rationale="Provides evidence synthesis across disease stages and adjuvant treatment standards."
                )
            ]

        # Domain 3: Immunology / Dermatology / Rheumatology (Secukinumab, Cosentyx, IL-17, Psoriasis)
        elif any(k in q for k in ["psoriasis", "secukinumab", "cosentyx", "il-17", "ixekizumab", "guselkumab", "arthritis", "spondylitis"]):
            return [
                RefinedPrompt(
                    category="Comparative Head-to-Head",
                    prompt="Compare PASI 90 and PASI 100 complete skin clearance response rates between Secukinumab (Cosentyx), Ixekizumab, and Guselkumab at Week 12 and Week 52.",
                    rationale="Contrasts rapid skin clearance thresholds across IL-17 and IL-23 biologic classes."
                ),
                RefinedPrompt(
                    category="Safety & Biomarker Deep-Dive",
                    prompt="What are the incidence rates of mucosal candidiasis and inflammatory bowel disease exacerbations reported in IL-17 inhibitor trials?",
                    rationale="Evaluates mechanism-specific safety considerations and clinical contraindications."
                ),
                RefinedPrompt(
                    category="Guideline & Class Landscape",
                    prompt="What is the multi-indication evidence for Secukinumab across plaque psoriasis, psoriatic arthritis, and ankylosing spondylitis?",
                    rationale="Maps cross-indication rheumatology and dermatology outcomes in the knowledge graph."
                )
            ]

        # Domain 4: Neuroscience / Multiple Sclerosis (Ofatumumab, Kesimpta, B-Cell)
        elif any(k in q for k in ["multiple sclerosis", "ms", "ofatumumab", "kesimpta", "relapse", "ocrelizumab", "teriflunomide"]):
            return [
                RefinedPrompt(
                    category="Comparative Head-to-Head",
                    prompt="Compare annualized relapse rates (ARR) and 3-month confirmed disability worsening between subcutaneous Ofatumumab and oral Teriflunomide (ASCLEPIOS).",
                    rationale="Contrasts targeted anti-CD20 B-cell therapy against oral standard-of-care immunomodulators."
                ),
                RefinedPrompt(
                    category="Safety & Biomarker Deep-Dive",
                    prompt="What are the immunoglobulin G/M levels and severe infection risks observed during chronic B-cell depletion therapy in MS?",
                    rationale="Assesses immune reconstitution, hypogammaglobulinemia risk, and long-term surveillance markers."
                ),
                RefinedPrompt(
                    category="Guideline & Class Landscape",
                    prompt="What does the multi-trial evidence indicate regarding early high-efficacy B-cell therapy versus escalation therapy in relapsing MS?",
                    rationale="Examines therapeutic paradigm shifts in disease-modifying therapy algorithms."
                )
            ]

        # Domain 5: General / Cross-Trial Synthesis
        else:
            return [
                RefinedPrompt(
                    category="Comparative Head-to-Head",
                    prompt="Which specific clinical trials in the corpus demonstrated statistically significant relative risk reductions for their primary composite endpoints?",
                    rationale="Extracts verified hazard ratios and confidence intervals across all indexed active treatment arms."
                ),
                RefinedPrompt(
                    category="Safety & Biomarker Deep-Dive",
                    prompt="Compare adverse event rates, all-cause hospitalizations, and treatment discontinuation profiles across the indexed trial cohort.",
                    rationale="Surfaces tolerability trade-offs and safety endpoints backed by verbatim study proof."
                ),
                RefinedPrompt(
                    category="Guideline & Class Landscape",
                    prompt="What are the primary clinical consensus themes and therapeutic community clusters identified across the knowledge graph?",
                    rationale="Applies global Leiden community detection to synthesize overarching clinical paradigms."
                )
            ]

    def generate_ingestion_suggestions(self, query_or_topic: str) -> List[IngestionPromptSuggestion]:
        """
        Synthesizes 3-4 optimized PubMed query formulations designed to
        maximize trial recall, eliminate review noise, and capture active comparators.
        """
        q = (query_or_topic or "").lower().strip()

        # Domain 1: Cardiorenal & Heart Failure (Entresto, SGLT2i, CKD)
        if any(k in q for k in ["heart failure", "hf", "kidney", "ckd", "renal", "sacubitril", "entresto", "sglt2", "empagliflozin", "dapagliflozin", "cardiorenal"]):
            return [
                IngestionPromptSuggestion(
                    strategy_label="Exhaustive 4-Pillar GDMT Landscape",
                    optimized_query='(sacubitril OR valsartan OR empagliflozin OR dapagliflozin OR finerenone OR spironolactone) AND ("heart failure"[Mesh] OR "heart failure with reduced ejection fraction") AND ("clinical trial, phase iii"[pt] OR "randomized controlled trial"[pt]) NOT ("review"[pt])',
                    expected_yield="20-40 Phase 3 RCTs",
                    rationale="Expands with all 4 pillars of guideline-directed medical therapy (ARNI, SGLT2i, MRA, Beta-blockers) to build a complete comparative multi-drug landscape.",
                    target_drugs=["Sacubitril/Valsartan (Entresto)", "Empagliflozin (Jardiance)", "Dapagliflozin (Farxiga)", "Finerenone (Kerendia)"]
                ),
                IngestionPromptSuggestion(
                    strategy_label="Head-to-Head Active Comparators",
                    optimized_query='("sacubitril" OR "LCZ696" OR "Entresto") AND ("enalapril" OR "valsartan") AND ("heart failure") AND ("randomized controlled trial"[pt])',
                    expected_yield="8-15 Direct RCTs",
                    rationale="Filters specifically for direct active comparator superiority trials (PARADIGM-HF, PARAGON-HF, PIONEER-HF) evaluating ARNI vs ACEi/ARB standard of care.",
                    target_drugs=["Sacubitril/Valsartan", "Enalapril", "Valsartan"]
                ),
                IngestionPromptSuggestion(
                    strategy_label="Cardiorenal & Kidney Disease Endpoints",
                    optimized_query='(empagliflozin OR dapagliflozin OR canagliflozin) AND ("chronic kidney disease"[Mesh] OR "diabetic nephropathies"[Mesh]) AND ("eGFR" OR "kidney failure" OR "mortality") AND ("clinical trial, phase iii"[pt])',
                    expected_yield="12-25 Landmark Trials",
                    rationale="Targets pivotal trials measuring renal composite endpoints (eGFR decline >=50%, ESKD, renal death) in CKD cohorts with and without diabetes.",
                    target_drugs=["Empagliflozin (EMPA-KIDNEY)", "Dapagliflozin (DAPA-CKD)", "Canagliflozin (CREDENCE)"]
                )
            ]

        # Domain 2: Oncology / Breast Cancer (Ribociclib, Kisqali, CDK4/6)
        elif any(k in q for k in ["breast", "ribociclib", "kisqali", "cdk4", "cdk6", "cdk4/6", "palbociclib", "abemaciclib"]):
            return [
                IngestionPromptSuggestion(
                    strategy_label="Exhaustive CDK4/6 Inhibitor Class Landscape",
                    optimized_query='(ribociclib OR palbociclib OR abemaciclib) AND ("breast neoplasms"[Mesh] OR "breast cancer") AND ("clinical trial, phase iii"[pt] OR "randomized controlled trial"[pt]) NOT ("review"[pt])',
                    expected_yield="15-30 Phase 3 RCTs",
                    rationale="Captures complete registration trials across all three FDA/EMA approved CDK4/6 inhibitors (MONALEESA, PALOMA, MONARCH) for cross-agent meta-analysis.",
                    target_drugs=["Ribociclib (Kisqali)", "Palbociclib (Ibrance)", "Abemaciclib (Verzenio)"]
                ),
                IngestionPromptSuggestion(
                    strategy_label="Overall Survival (OS) Landmark Endpoints",
                    optimized_query='(ribociclib OR palbociclib OR abemaciclib) AND ("overall survival" OR "mortality benefit") AND ("breast cancer") AND ("randomized controlled trial"[pt])',
                    expected_yield="8-14 Pivotal Trials",
                    rationale="Isolates mature trials reporting statistically significant Overall Survival hazard ratios in endocrine-resistant settings.",
                    target_drugs=["Ribociclib (MONALEESA-7)", "Abemaciclib (MONARCH-2)", "Palbociclib"]
                ),
                IngestionPromptSuggestion(
                    strategy_label="Early Breast Cancer Adjuvant Escalation",
                    optimized_query='(ribociclib OR abemaciclib) AND ("early breast cancer" OR "adjuvant") AND ("invasive disease-free survival") AND ("phase 3" OR "phase III")',
                    expected_yield="6-10 Adjuvant Trials",
                    rationale="Focuses on modern early breast cancer trials (NATALEE, monarchE) evaluating disease recurrence prevention.",
                    target_drugs=["Ribociclib (NATALEE)", "Abemaciclib (monarchE)"]
                )
            ]

        # Domain 3: Immunology / Dermatology / Rheumatology (Secukinumab, Cosentyx, IL-17)
        elif any(k in q for k in ["psoriasis", "secukinumab", "cosentyx", "il-17", "ixekizumab", "guselkumab", "skyrizi", "ankylosing", "spondylitis"]):
            return [
                IngestionPromptSuggestion(
                    strategy_label="Biologic Multi-Mechanism Class Expansion",
                    optimized_query='(secukinumab OR ixekizumab OR guselkumab OR risankizumab OR adalimumab) AND ("psoriasis"[Mesh] OR "psoriatic arthritis"[Mesh]) AND ("clinical trial, phase iii"[pt] OR "randomized controlled trial"[pt])',
                    expected_yield="25-45 Phase 3 RCTs",
                    rationale="Broadens ingestion across IL-17A, IL-23, and TNF-alpha biologics for comprehensive comparative efficacy in skin and joint disease.",
                    target_drugs=["Secukinumab (Cosentyx)", "Ixekizumab (Taltz)", "Guselkumab (Tremfya)", "Risankizumab (Skyrizi)"]
                ),
                IngestionPromptSuggestion(
                    strategy_label="Complete Skin Clearance (PASI 90 / 100)",
                    optimized_query='(secukinumab OR ixekizumab OR guselkumab) AND ("PASI 90" OR "PASI 100" OR "clearance") AND ("randomized controlled trial"[pt])',
                    expected_yield="12-20 Pivotal Trials",
                    rationale="Filters for registration trials with stringent complete clearance endpoints at Week 12 and Week 52.",
                    target_drugs=["Secukinumab", "Ixekizumab", "Guselkumab"]
                ),
                IngestionPromptSuggestion(
                    strategy_label="Axial Spondyloarthritis & Ankylosing Spondylitis",
                    optimized_query='(secukinumab OR ixekizumab) AND ("ankylosing spondylitis"[Mesh] OR "axial spondyloarthritis") AND ("ASAS20" OR "ASAS40") AND ("clinical trial, phase iii"[pt])',
                    expected_yield="8-16 Phase 3 Trials",
                    rationale="Captures axial rheumatology trials (MEASURE 1 & 2) linking joint mobility and spinal progression to the knowledge graph.",
                    target_drugs=["Secukinumab (MEASURE)", "Ixekizumab (COAST)"]
                )
            ]

        # Domain 4: Neuroscience / Multiple Sclerosis & B-Cell Depletion (Ofatumumab, Kesimpta, CD20)
        elif any(k in q for k in [
            "multiple sclerosis", "ms", "ofatumumab", "kesimpta", "relapse", "ocrelizumab", 
            "teriflunomide", "anti-cd20", "ublituximab", "briumvi", "rituximab", 
            "cladribine", "mavenclad", "fingolimod", "gilenya", "siponimod", "mayzent"
        ]) or ("cd20" in q and "depletion" in q) or ("b-cell" in q and ("depletion" in q or "ms" in q)):
            return [
                IngestionPromptSuggestion(
                    strategy_label="High-Efficacy B-Cell Depletion Landscape",
                    optimized_query='(ofatumumab OR ocrelizumab OR ublituximab OR rituximab) AND ("multiple sclerosis"[Mesh]) AND ("clinical trial, phase iii"[pt] OR "randomized controlled trial"[pt]) NOT ("review"[pt])',
                    expected_yield="15-28 Phase 3 RCTs",
                    rationale="Captures all targeted anti-CD20 monoclonal antibody therapies in relapsing and progressive multiple sclerosis.",
                    target_drugs=["Ofatumumab (Kesimpta)", "Ocrelizumab (Ocrevus)", "Ublituximab (Briumvi)"]
                ),
                IngestionPromptSuggestion(
                    strategy_label="Active Comparator Superiority Trials",
                    optimized_query='(ofatumumab OR ocrelizumab) AND ("teriflunomide" OR "interferon beta") AND ("annualized relapse rate") AND ("randomized controlled trial"[pt])',
                    expected_yield="6-12 Head-to-Head RCTs",
                    rationale="Isolates landmark active comparator trials (ASCLEPIOS I & II, OPERA I & II) testing B-cell therapy vs oral immunomodulators.",
                    target_drugs=["Ofatumumab (ASCLEPIOS)", "Teriflunomide (Aubagio)", "Ocrelizumab (OPERA)"]
                ),
                IngestionPromptSuggestion(
                    strategy_label="Confirmed Disability Progression (CDW) Endpoints",
                    optimized_query='(ofatumumab OR ocrelizumab OR cladribine) AND ("disability worsening" OR "EDSS" OR "disability progression") AND ("phase 3" OR "phase III")',
                    expected_yield="8-15 Landmark Trials",
                    rationale="Extracts sustained 3-month and 6-month disability delay parameters and neuroprotective endpoints.",
                    target_drugs=["Ofatumumab", "Ocrelizumab", "Cladribine"]
                )
            ]

        # Domain 5A: Targeted Hematology & Allosteric STAMP in CML (Scemblix, Asciminib)
        elif any(k in q for k in ["cml", "asciminib", "scemblix", "nilotinib", "tasigna", "bcr-abl", "bcr::abl1", "bosutinib", "ponatinib"]):
            return [
                IngestionPromptSuggestion(
                    strategy_label="Allosteric STAMP & TKI Landscape in CML",
                    optimized_query='(asciminib OR bosutinib OR ponatinib OR nilotinib) AND ("leukemia, myelogenous, chronic, bcr-abl positive"[Mesh] OR "chronic myeloid leukemia") AND ("clinical trial, phase iii"[pt] OR "randomized controlled trial"[pt])',
                    expected_yield="6-12 Pivotal RCTs",
                    rationale="Filters for major molecular response (MMR) registration trials (ASCEMBL, ASC4FIRST) evaluating allosteric STAMP vs ATP-competitive TKIs.",
                    target_drugs=["Asciminib (Scemblix)", "Bosutinib (Bosulif)", "Nilotinib (Tasigna)"]
                ),
                IngestionPromptSuggestion(
                    strategy_label="Head-to-Head TKI Resistance Benchmarks",
                    optimized_query='("asciminib" OR "Scemblix") AND ("bosutinib" OR "imatinib" OR "dasatinib") AND ("major molecular response" OR "MMR") AND ("randomized controlled trial"[pt])',
                    expected_yield="4-8 Head-to-Head RCTs",
                    rationale="Targets comparative superiority trials in resistant or newly diagnosed chronic myeloid leukemia.",
                    target_drugs=["Asciminib", "Bosutinib", "Imatinib"]
                ),
                IngestionPromptSuggestion(
                    strategy_label="Molecular Response & Progression-Free Survival",
                    optimized_query='(asciminib OR ponatinib) AND ("overall survival" OR "progression-free survival" OR "molecular response") AND ("clinical trial"[pt])',
                    expected_yield="5-10 Landmark Studies",
                    rationale="Captures deep molecular response rates (MR4.5) and long-term cytogenetic remission outcomes.",
                    target_drugs=["Asciminib", "Ponatinib"]
                )
            ]

        # Domain 5B: Radioligand Therapy in Prostate Cancer (Pluvicto, PSMA)
        elif any(k in q for k in ["prostate", "pluvicto", "lutetium", "psma", "177lu", "mcrpc"]):
            return [
                IngestionPromptSuggestion(
                    strategy_label="Radioligand Therapy in mCRPC",
                    optimized_query='("177Lu-PSMA-617" OR "lutetium" OR "pluvicto" OR "radium-223") AND ("prostatic neoplasms"[Mesh] OR "castration-resistant prostate cancer") AND ("clinical trial, phase iii"[pt] OR "randomized controlled trial"[pt])',
                    expected_yield="8-15 Phase 3 RCTs",
                    rationale="Captures targeted beta-emitter radioligand trials (VISION, PSMAfore) vs androgen-receptor directed therapies in metastatic castration-resistant prostate cancer.",
                    target_drugs=["Lutetium-177 PSMA-617 (Pluvicto)", "Enzalutamide", "Abiraterone"]
                ),
                IngestionPromptSuggestion(
                    strategy_label="Targeted Radioligand vs ARDT Comparators",
                    optimized_query='("pluvicto" OR "177Lu-PSMA-617") AND ("enzalutamide" OR "abiraterone" OR "cabazitaxel") AND ("overall survival" OR "radiographic progression-free survival") AND ("randomized controlled trial"[pt])',
                    expected_yield="4-8 Landmark RCTs",
                    rationale="Isolates registration trials benchmarking PSMA radioligand therapy against next-generation androgen axis therapies.",
                    target_drugs=["Lutetium-177 PSMA-617", "Enzalutamide", "Abiraterone"]
                ),
                IngestionPromptSuggestion(
                    strategy_label="PSA Response & Radiographic Progression Endpoints",
                    optimized_query='("177Lu-PSMA-617" OR "pluvicto") AND ("PSA response" OR "rPFS" OR "survival") AND ("clinical trial"[pt])',
                    expected_yield="6-12 Pivotal Trials",
                    rationale="Extracts objective response rates, radiographic progression-free survival, and quality-of-life parameters.",
                    target_drugs=["Pluvicto (VISION)", "Pluvicto (PSMAfore)"]
                )
            ]

        # Domain 6: Dynamic Query Optimization for ANY Custom Topic or Drug Input
        elif q:
            clean_term = re.sub(r'[^a-zA-Z0-9\s\-]', ' ', query_or_topic).strip()
            clean_term = re.sub(r'\s+', ' ', clean_term)
            words = [w for w in clean_term.split() if len(w) > 2]
            quoted_phrase = f'"{clean_term}"' if len(clean_term.split()) > 1 else clean_term
            or_terms = " OR ".join(f'"{w}"' for w in words) if words else clean_term
            query_core = f'({quoted_phrase} OR ({or_terms}))' if len(words) > 1 else quoted_phrase

            return [
                IngestionPromptSuggestion(
                    strategy_label=f"Phase 3 Trial Landscape: {clean_term.title()}",
                    optimized_query=f'{query_core} AND ("clinical trial, phase iii"[pt] OR "randomized controlled trial"[pt]) NOT ("review"[pt] OR "editorial"[pt])',
                    expected_yield="10-25 Phase 3 RCTs",
                    rationale=f"Constructs an exhaustive Phase 3 and RCT boolean filter around '{clean_term}' while filtering out narrative reviews and editorials.",
                    target_drugs=[clean_term.title()]
                ),
                IngestionPromptSuggestion(
                    strategy_label=f"Active Comparator Superiority: {clean_term.title()}",
                    optimized_query=f'({quoted_phrase}) AND ("standard of care" OR "placebo" OR "comparator" OR "superiority") AND ("randomized controlled trial"[pt])',
                    expected_yield="6-15 Controlled Trials",
                    rationale=f"Isolates head-to-head superiority and active-comparator controlled trials for cross-arm evidence comparison.",
                    target_drugs=[clean_term.title(), "Active Comparator / Standard of Care"]
                ),
                IngestionPromptSuggestion(
                    strategy_label=f"Pivotal Clinical Endpoints: {clean_term.title()}",
                    optimized_query=f'({quoted_phrase}) AND ("overall survival" OR "primary endpoint" OR "hazard ratio" OR "efficacy" OR "safety") AND ("clinical trial"[pt])',
                    expected_yield="8-18 Landmark Studies",
                    rationale=f"Focuses on clinical trials reporting quantifiable primary endpoints, hazard ratios with 95% CIs, and safety metrics.",
                    target_drugs=[clean_term.title()]
                )
            ]

        # Default: General High-Yield Starter Pack (When input is empty)
        else:
            return [
                IngestionPromptSuggestion(
                    strategy_label="Cardiorenal 4-Pillar GDMT Landscape",
                    optimized_query='(sacubitril OR empagliflozin OR dapagliflozin OR finerenone) AND ("heart failure" OR "chronic kidney disease") AND ("clinical trial, phase iii"[pt] OR "randomized controlled trial"[pt]) NOT ("review"[pt])',
                    expected_yield="20-35 Phase 3 RCTs",
                    rationale="Combines first-in-class ARNI, SGLT2 inhibitors, and non-steroidal MRAs across landmark cardiorenal populations.",
                    target_drugs=["Sacubitril/Valsartan", "Empagliflozin", "Dapagliflozin", "Finerenone"]
                ),
                IngestionPromptSuggestion(
                    strategy_label="CDK4/6 Oncology Inhibitor Class",
                    optimized_query='(ribociclib OR palbociclib OR abemaciclib) AND ("breast cancer"[Mesh] OR "breast neoplasms") AND ("overall survival" OR "progression-free survival") AND ("randomized controlled trial"[pt])',
                    expected_yield="15-25 Phase 3 RCTs",
                    rationale="Captures complete survival and progression endpoints across the CDK4/6 inhibitor breast cancer portfolio.",
                    target_drugs=["Ribociclib", "Palbociclib", "Abemaciclib"]
                ),
                IngestionPromptSuggestion(
                    strategy_label="Targeted Biologics in Autoimmune & Dermatology",
                    optimized_query='(secukinumab OR ixekizumab OR guselkumab) AND ("psoriasis" OR "psoriatic arthritis") AND ("PASI" OR "ACR") AND ("clinical trial, phase iii"[pt])',
                    expected_yield="15-30 Phase 3 RCTs",
                    rationale="Extracts high-clearance biologic trials across dermatological and rheumatological indications.",
                    target_drugs=["Secukinumab", "Ixekizumab", "Guselkumab"]
                )
            ]


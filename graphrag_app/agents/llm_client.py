"""
Gemini Flash LLM Client for Dynamic Autonomous Clinical Agents.
Powered by Google Gemini 3.8 Flash via the modern `google.genai` SDK.
"""

import os
import json
import logging
from typing import Optional, List, Dict, Any
from config import settings

logger = logging.getLogger("graphrag.gemini")

class GeminiClient:
    """
    Manages communication with Google Gemini 3.8 Flash using the official google.genai SDK.
    Supports dynamic fallback across candidate model names and graceful degradation
    when API keys are unconfigured.
    """
    def __init__(self):
        self.api_key = settings.GEMINI_API_KEY
        self.configured = False
        self._client = None
        self._init_client()

    def _init_client(self):
        """Initializes the modern Google GenAI client."""
        if not self.api_key:
            logger.info("GeminiClient: GEMINI_API_KEY not configured. Operating in dynamic hybrid mode.")
            return

        try:
            from google import genai
            self._client = genai.Client(api_key=self.api_key)
            self.configured = True
            logger.info(f"GeminiClient: Successfully initialized with target model '{settings.GEMINI_MODEL}'.")
        except Exception as e:
            logger.warning(f"GeminiClient initialization error: {e}")
            self.configured = False

    def is_available(self) -> bool:
        return self.configured and self._client is not None

    def get_model_chain(self) -> List[str]:
        """Returns prioritized candidate model chain starting with user-specified model."""
        candidates = []
        if settings.GEMINI_MODEL:
            candidates.append(settings.GEMINI_MODEL)
        for m in settings.GEMINI_FALLBACK_MODELS:
            if m not in candidates:
                candidates.append(m)
        return candidates

    def generate_clinical_synthesis(
        self,
        query: str,
        intent_str: str,
        evidence_rows: List[Any],
        active_articles: List[Any],
        system_prompt: str
    ) -> Optional[str]:
        """
        Dynamically synthesizes multi-document clinical trial evidence using Gemini 3.8 Flash.
        Strictly grounds claims in provided evidence rows and citations.
        """
        if not self.is_available():
            return None

        from google.genai import types

        # Format evidence context
        evidence_context = []
        for row in evidence_rows:
            evidence_context.append(
                f"- Study: {row.study_name} (PMID:{row.pmid}, {row.journal} {row.year})\n"
                f"  Drug/Dose: {row.drug} {row.dose}\n"
                f"  Population: {row.population} (N={row.sample_size:,})\n"
                f"  Outcome: {row.outcome} | Effect: {row.effect_size} (95% CI: {row.ci_95}), P-Value: {row.p_value}\n"
                f"  Verbatim Passage: \"{row.evidence_quote}\"\n"
            )

        context_str = "\n".join(evidence_context) if evidence_context else "No direct PICO rows available."

        articles_summary = []
        for a in active_articles:
            articles_summary.append(f"PMID:{a.pmid} - {a.title} ({a.journal} {a.year}, N={a.sample_size:,}):\n{a.abstract}\n")
        articles_str = "\n".join(articles_summary)

        prompt = f"""
{system_prompt}

---
USER QUERY:
"{query}"

RETRIEVAL ROUTE / INTENT:
{intent_str}

VERIFIED CLINICAL EVIDENCE TABLE (USE FOR EXACT HAZARD RATIOS, CIs, SAMPLE SIZES):
{context_str}

RELEVANT PUBLICATION ABSTRACTS:
{articles_str}

---
INSTRUCTIONS FOR SYNTHESIS:
1. Provide an executive, comparative clinical synthesis answering the user query.
2. Structure your narrative with clear headers per study/compound.
3. Every numerical statement (HR, 95% CI, p-value, patient N) MUST be strictly taken from the verified evidence above.
4. Cite the exact study and PubMed tag (e.g. `[PMID:XXXXXXXX]`) for every claim.
5. End with a 2-sentence clinical consensus summary highlighting the cardiorenal / therapeutic takeaway.
"""

        for model_name in self.get_model_chain():
            try:
                response = self._client.models.generate_content(
                    model=model_name,
                    contents=prompt,
                    config=types.GenerateContentConfig(
                        temperature=0.1,
                        max_output_tokens=1500
                    )
                )
                if response and response.text:
                    logger.info(f"GeminiClient: Clinical synthesis successfully generated via {model_name}.")
                    return response.text.strip()
            except Exception as e:
                logger.warning(f"GeminiClient generation with model {model_name} failed: {e}. Trying fallback...")

        return None

    def generate_dynamic_prompts(
        self,
        query: str,
        matched_articles: List[Any]
    ) -> Optional[List[Dict[str, str]]]:
        """
        Dynamically formulates 3 distinct, high-impact clinical prompt variations using Gemini 3.8 Flash.
        """
        if not self.is_available():
            return None

        from google.genai import types

        studies = [f"{a.title} (PMID:{a.pmid})" for a in matched_articles[:5]]
        studies_context = "; ".join(studies)

        prompt = f"""
You are the Clinical Prompt Strategy Refiner for Novartis Medical Affairs.
Given the user query: "{query}"
And the retrieved clinical studies: {studies_context}

Generate exactly 3 high-impact prompt variations that guide the user to explore the literature deeper.
Return ONLY valid JSON matching this exact array format:
[
  {{
    "category": "Comparative Head-to-Head",
    "prompt": "<Specific head-to-head comparative question>",
    "rationale": "<1-sentence clinical rationale>"
  }},
  {{
    "category": "Safety & Biomarker Deep-Dive",
    "prompt": "<Specific safety, adverse events, or biomarker question>",
    "rationale": "<1-sentence clinical rationale>"
  }},
  {{
    "category": "Guideline & Class Landscape",
    "prompt": "<Broad therapeutic guideline or multi-study consensus question>",
    "rationale": "<1-sentence clinical rationale>"
  }}
]
"""
        for model_name in self.get_model_chain():
            try:
                response = self._client.models.generate_content(
                    model=model_name,
                    contents=prompt,
                    config=types.GenerateContentConfig(
                        temperature=0.2,
                        response_mime_type="application/json"
                    )
                )
                if response and response.text:
                    clean_text = response.text.strip()
                    if clean_text.startswith("```json"):
                        clean_text = clean_text[7:]
                    if clean_text.endswith("```"):
                        clean_text = clean_text[:-3]
                    data = json.loads(clean_text)
                    if isinstance(data, list) and len(data) >= 3:
                        logger.info(f"GeminiClient: Dynamic prompt suggestions generated via {model_name}.")
                        return data[:3]
            except Exception as e:
                logger.warning(f"GeminiClient prompt generation with {model_name} failed: {e}")

        return None

    def extract_dynamic_pico(
        self,
        title: str,
        abstract: str,
        pmid: str
    ) -> Optional[Dict[str, Any]]:
        """
        Extracts structured PICO (Population, Intervention, Comparator, Outcomes)
        from a raw clinical trial title and abstract using Gemini 3.8 Flash.
        """
        if not self.is_available():
            return None

        from google.genai import types

        prompt = f"""
You are a Clinical Data Extraction Guard for systematic literature reviews.
Extract the structured PICO parameters from the following clinical trial publication:

Title: {title}
PMID: {pmid}
Abstract:
{abstract}

Return ONLY valid JSON adhering strictly to this schema:
{{
  "population": {{
    "condition": "<Primary medical indication, e.g. Chronic Kidney Disease, HFrEF>",
    "n": <Integer sample size or null>,
    "description": "<Concise description of the cohort criteria>",
    "evidence": "<Verbatim sentence from abstract describing population>"
  }},
  "interventions": [
    {{
      "name": "<Generic drug name, e.g. Empagliflozin>",
      "dose": "<Dose if stated, e.g. 10 mg daily, or 'Standard dose'>",
      "drug_cui": "<Optional UMLS CUI if known or null>",
      "rxnorm": "<Optional RxNorm code if known or null>"
    }}
  ],
  "comparator": "<Comparator, e.g. Placebo, standard of care>",
  "outcomes": [
    {{
      "name": "<Endpoint name, e.g. Progression of kidney disease or CV death>",
      "measure": "<HR, OR, or RR>",
      "effect": <Float numerical effect size, e.g. 0.72>,
      "ci_low": <Float lower 95% CI bound, e.g. 0.64>,
      "ci_high": <Float upper 95% CI bound, e.g. 0.82>,
      "p_value": "<Exact p-value, e.g. P<0.001>",
      "direction": "FAVORS_INTERVENTION",
      "evidence": "<EXACT verbatim sentence from abstract stating this statistical result>"
    }}
  ]
}}
"""
        for model_name in self.get_model_chain():
            try:
                response = self._client.models.generate_content(
                    model=model_name,
                    contents=prompt,
                    config=types.GenerateContentConfig(
                        temperature=0.0,
                        response_mime_type="application/json"
                    )
                )
                if response and response.text:
                    clean_text = response.text.strip()
                    if clean_text.startswith("```json"):
                        clean_text = clean_text[7:]
                    if clean_text.endswith("```"):
                        clean_text = clean_text[:-3]
                    data = json.loads(clean_text)
                    logger.info(f"GeminiClient: Dynamic PICO extracted for PMID:{pmid} via {model_name}.")
                    return data
            except Exception as e:
                logger.warning(f"GeminiClient PICO extraction with {model_name} failed: {e}")

        return None

    def generate_embeddings(self, texts: List[str]) -> List[List[float]]:
        """
        Generates dense semantic vector embeddings for input texts.
        Prioritizes text-embedding-004 and modern gemini-embedding models with 768 output dimensions.
        Falls back gracefully if offline or unconfigured.
        """
        if not self.is_available() or not texts:
            return []

        try:
            from google.genai import types
        except ImportError:
            return []

        candidate_embedding_models = []
        if getattr(self, "_active_embedding_model", None):
            candidate_embedding_models.append(self._active_embedding_model)
        if settings.EMBEDDING_MODEL and settings.EMBEDDING_MODEL not in candidate_embedding_models:
            candidate_embedding_models.append(settings.EMBEDDING_MODEL)
        for m in settings.EMBEDDING_FALLBACK_MODELS:
            if m not in candidate_embedding_models:
                candidate_embedding_models.append(m)

        batch_size = 32
        all_embeddings: List[List[float]] = []

        for i in range(0, len(texts), batch_size):
            batch = texts[i : i + batch_size]
            batch_result = None

            for model_name in candidate_embedding_models:
                try:
                    cfg = types.EmbedContentConfig(output_dimensionality=settings.EMBEDDING_DIMENSIONS)
                    res = self._client.models.embed_content(
                        model=model_name,
                        contents=batch if len(batch) > 1 else batch[0],
                        config=cfg
                    )
                    if res and res.embeddings:
                        batch_result = [list(e.values) for e in res.embeddings]
                        self._active_embedding_model = model_name
                        logger.info(f"GeminiClient: Generated {len(batch_result)} embeddings ({settings.EMBEDDING_DIMENSIONS}d) via {model_name}.")
                        break
                except Exception as e:
                    logger.debug(f"GeminiClient: Embedding attempt with {model_name} failed: {e}")
                    continue

            if batch_result:
                all_embeddings.extend(batch_result)
            else:
                logger.warning(f"GeminiClient: Failed to generate dense embeddings for batch.")
                return []

        return all_embeddings

# Singleton LLM client instance
gemini_client = GeminiClient()

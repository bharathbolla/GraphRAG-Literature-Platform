import re
from typing import Optional, List
from pydantic import BaseModel, Field, model_validator
from .pico import PICOData
from .entity import BiomedicalEntity

class SectionChunk(BaseModel):
    section_name: str = Field(..., description="Section header e.g. BACKGROUND, METHODS, RESULTS, CONCLUSIONS")
    content: str = Field(..., description="Verbatim text content of section")

class Article(BaseModel):
    pmid: str = Field(..., description="PubMed Unique Identifier")
    doi: Optional[str] = Field(None, description="Digital Object Identifier")
    title: str = Field(..., description="Full scientific title")
    journal: str = Field(..., description="Journal abbreviation/name")
    year: int = Field(..., description="Publication year")
    authors: str = Field(..., description="Primary author list / study group")
    study_design: str = Field(default="Phase 3 Double-Blind RCT", description="Clinical study design")
    sample_size: int = Field(default=0, description="Total patient enrollment N")
    abstract: str = Field(..., description="Abstract text with section headers")
    pico: Optional[PICOData] = Field(None, description="Extracted structured PICO data")
    entities: List[BiomedicalEntity] = Field(default_factory=list, description="Extracted biomedical entities")
    section_chunks: List[SectionChunk] = Field(default_factory=list, description="Section-aware text chunks")
    mesh_terms: List[str] = Field(default_factory=list, description="PubMed Medical Subject Headings (MeSH)")
    chemicals: List[str] = Field(default_factory=list, description="PubMed Chemical and Drug Substance terms")

    @model_validator(mode="after")
    def populate_section_chunks(self):
        if not self.section_chunks and self.abstract:
            pattern = r"(BACKGROUND|METHODS|RESULTS|CONCLUSIONS|OBJECTIVES|DISCUSSION):"
            parts = re.split(pattern, self.abstract)
            if len(parts) > 1:
                chunks = []
                idx = 1
                while idx < len(parts):
                    sec_name = parts[idx].strip()
                    sec_content = parts[idx+1].strip() if idx+1 < len(parts) else ""
                    chunks.append(SectionChunk(section_name=sec_name, content=sec_content))
                    idx += 2
                self.section_chunks = chunks
            else:
                self.section_chunks = [
                    SectionChunk(section_name="FULL_ABSTRACT", content=self.abstract)
                ]
        return self

class IngestRequest(BaseModel):
    query_or_pmid: str = Field(..., description="Search keyword or explicit PubMed PMID to ingest")
    max_results: Optional[int] = Field(default=10, description="Max trials to fetch and ingest")

class IngestionPromptSuggestion(BaseModel):
    strategy_label: str = Field(..., description="Strategy name e.g. Exhaustive Class Landscape, Head-to-Head Active Comparators, Pivotal Landmark Endpoints")
    optimized_query: str = Field(..., description="Optimized PubMed boolean query string ready for execution")
    expected_yield: str = Field(..., description="Estimated trial count e.g. '15-30 Phase 3 RCTs'")
    rationale: str = Field(..., description="Why this query improves recall, precision, and multi-doc graph coverage")
    target_drugs: List[str] = Field(default_factory=list, description="Key compounds covered in this query")

class QuerySuggestionRequest(BaseModel):
    query: Optional[str] = Field(default="", description="User input text or topic to generate suggestions for")

class ArticleStats(BaseModel):
    indexed_articles: int
    section_chunks: int
    kg_edges: int
    normalized_entities: int
    thematic_communities: int
    total_enrolled_patients: int
    total_articles: int
    total_nodes: int
    total_edges: int
    unique_entities: int
    benchmark_name: str
    llm_model: Optional[str] = "gemini-3.8-flash"
    llm_active: Optional[bool] = False
    embedding_model: Optional[str] = "text-embedding-004"
    embedding_dimensions: Optional[int] = 768
    dense_vectors_active: Optional[bool] = True

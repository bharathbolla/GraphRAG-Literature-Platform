from enum import Enum
from typing import Optional, List
from pydantic import BaseModel, Field

class EntityType(str, Enum):
    CONDITION = "Condition"
    DRUG = "Drug"
    DRUG_CLASS = "DrugClass"
    OUTCOME = "Outcome"
    GENE = "Gene"

class BiomedicalEntity(BaseModel):
    name: str = Field(..., description="Canonical entity surface name")
    type: EntityType = Field(..., description="Semantic entity category")
    cui: Optional[str] = Field(None, description="UMLS Concept Unique Identifier or MeSH ID")
    rxnorm: Optional[str] = Field(None, description="RxNorm identifier for pharmacologic agents")
    papers_count: int = Field(default=0, description="Number of papers mentioning this entity")
    pmids: List[str] = Field(default_factory=list, description="List of referencing PMIDs")

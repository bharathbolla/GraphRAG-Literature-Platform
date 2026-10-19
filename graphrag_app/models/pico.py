from typing import Optional, List
from pydantic import BaseModel, Field

class Population(BaseModel):
    description: str = Field(..., description="Full text description of enrolled population")
    condition: str = Field(..., description="Target primary medical condition")
    condition_cui: Optional[str] = Field(None, description="UMLS CUI for condition")
    n: Optional[int] = Field(None, description="Total sample size N")
    age_mean: Optional[str] = Field(None, description="Mean or median age")
    setting: Optional[str] = Field(None, description="Clinical trial setting")
    evidence: str = Field(..., description="Verbatim evidence quote from publication")

class Intervention(BaseModel):
    name: str = Field(..., description="Drug or intervention name")
    drug_cui: Optional[str] = Field(None, description="UMLS Concept Unique Identifier")
    rxnorm: Optional[str] = Field(None, description="RxNorm code")
    dose: Optional[str] = Field(None, description="Dose and regimen")
    duration: Optional[str] = Field(None, description="Trial duration or follow-up")
    evidence: str = Field(..., description="Verbatim evidence quote from publication")

class Comparator(BaseModel):
    name: str = Field(..., description="Control or active comparator name")
    drug_cui: Optional[str] = Field(None, description="UMLS CUI")
    evidence: str = Field(..., description="Verbatim evidence quote")

class ClinicalOutcome(BaseModel):
    name: str = Field(..., description="Clinical endpoint or outcome name")
    outcome_cui: Optional[str] = Field(None, description="UMLS CUI")
    timepoint: Optional[str] = Field(None, description="Evaluation timepoint")
    effect: str = Field(..., description="Numerical effect size (e.g. 0.72)")
    measure: str = Field(default="Hazard Ratio (HR)", description="Measure type (HR, RR, MD, OR)")
    ci_low: Optional[str] = Field(None, description="95% CI lower bound")
    ci_high: Optional[str] = Field(None, description="95% CI upper bound")
    p_value: Optional[str] = Field(None, description="Reported p-value")
    direction: str = Field(default="Significant Benefit", description="Clinical benefit direction")
    evidence: str = Field(..., description="Verbatim evidence quote from publication")

class PICOData(BaseModel):
    population: Population
    interventions: List[Intervention] = Field(default_factory=list)
    comparators: List[Comparator] = Field(default_factory=list)
    outcomes: List[ClinicalOutcome] = Field(default_factory=list)

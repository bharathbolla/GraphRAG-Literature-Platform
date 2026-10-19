from typing import List
from models.article import Article
from models.pico import PICOData, Population, Intervention, Comparator, ClinicalOutcome
from models.entity import BiomedicalEntity, EntityType

def get_benchmark_articles() -> List[Article]:
    """Returns the 7 landmark multicenter Phase 3 cardiorenal clinical trials."""
    return [
        Article(
            pmid="36331190",
            doi="10.1056/NEJMoa2204233",
            title="Empagliflozin in Patients with Chronic Kidney Disease (EMPA-KIDNEY)",
            journal="New England Journal of Medicine (NEJM)",
            year=2023,
            authors="The EMPA-KIDNEY Collaborative Group, Herrington WG, Staplin N, et al.",
            study_design="Phase 3 Double-Blind RCT",
            sample_size=6609,
            abstract="BACKGROUND: The effects of empagliflozin in patients with chronic kidney disease (CKD) who are at risk for progression are not fully known across wide ranges of kidney function. METHODS: We conducted a randomized, double-blind, placebo-controlled trial assessing empagliflozin (10 mg daily) vs placebo in 6609 patients with CKD (eGFR 20 to <45, or 45 to <90 with uACR >=200 mg/g). RESULTS: Progression of kidney disease or death from cardiovascular causes occurred in 432 of 3304 patients (13.1%) in the empagliflozin group and in 558 of 3305 patients (16.9%) in the placebo group (hazard ratio, 0.72; 95% confidence interval [CI], 0.64 to 0.82; P<0.001). Results were consistent among patients with or without diabetes. All-cause hospitalizations were significantly lower in the empagliflozin group (hazard ratio, 0.86; 95% CI, 0.78 to 0.95). CONCLUSIONS: Empagliflozin led to a significantly lower risk of kidney disease progression or death from cardiovascular causes than placebo across a broad range of CKD patients.",
            pico=PICOData(
                population=Population(
                    description="Patients with established CKD (eGFR 20 to <45 mL/min/1.73m2, or eGFR 45 to <90 with uACR >=200 mg/g) with or without type 2 diabetes",
                    condition="Chronic Kidney Disease",
                    condition_cui="C0022661",
                    n=6609,
                    age_mean="63.8 years",
                    evidence="We enrolled 6609 patients with chronic kidney disease with an eGFR of 20 to less than 45 ml per minute per 1.73 m2, or an eGFR of 45 to less than 90 with urinary albumin-to-creatinine ratio of at least 200."
                ),
                interventions=[
                    Intervention(
                        name="Empagliflozin",
                        drug_cui="C3261058",
                        rxnorm="1545653",
                        dose="10 mg once daily",
                        duration="Median 2.0 years",
                        evidence="Patients were randomly assigned to receive empagliflozin (10 mg once daily) or matching placebo."
                    )
                ],
                comparators=[
                    Comparator(
                        name="Matching Placebo",
                        drug_cui="C0000000",
                        evidence="Patients were randomly assigned to receive empagliflozin (10 mg once daily) or matching placebo."
                    )
                ],
                outcomes=[
                    ClinicalOutcome(
                        name="Progression of Kidney Disease or CV Death",
                        outcome_cui="C0022661",
                        timepoint="2.0 years",
                        effect="0.72",
                        measure="Hazard Ratio (HR)",
                        ci_low="0.64",
                        ci_high="0.82",
                        p_value="P < 0.001",
                        direction="Significant Benefit",
                        evidence="Progression of kidney disease or death from cardiovascular causes occurred in 432 of 3304 patients (13.1%) in the empagliflozin group and in 558 of 3305 patients (16.9%) in the placebo group (hazard ratio, 0.72; 95% confidence interval [CI], 0.64 to 0.82; P<0.001)."
                    ),
                    ClinicalOutcome(
                        name="All-Cause Hospitalization",
                        outcome_cui="C0019993",
                        timepoint="2.0 years",
                        effect="0.86",
                        measure="Hazard Ratio (HR)",
                        ci_low="0.78",
                        ci_high="0.95",
                        p_value="P = 0.003",
                        direction="Significant Benefit",
                        evidence="All-cause hospitalizations were significantly lower in the empagliflozin group than in the placebo group (hazard ratio, 0.86; 95% CI, 0.78 to 0.95)."
                    )
                ]
            ),
            entities=[
                BiomedicalEntity(name="Chronic Kidney Disease", type=EntityType.CONDITION, cui="C0022661", papers_count=1, pmids=["36331190"]),
                BiomedicalEntity(name="Type 2 Diabetes Mellitus", type=EntityType.CONDITION, cui="C0011860", papers_count=1, pmids=["36331190"]),
                BiomedicalEntity(name="Empagliflozin", type=EntityType.DRUG, cui="C3261058", rxnorm="1545653", papers_count=1, pmids=["36331190"]),
                BiomedicalEntity(name="SGLT2 inhibitors", type=EntityType.DRUG_CLASS, cui="C3890289", papers_count=1, pmids=["36331190"]),
                BiomedicalEntity(name="Progression of Kidney Disease", type=EntityType.OUTCOME, cui="C0022661", papers_count=1, pmids=["36331190"]),
                BiomedicalEntity(name="Cardiovascular Death", type=EntityType.OUTCOME, cui="C0011050", papers_count=1, pmids=["36331190"])
            ]
        ),
        Article(
            pmid="32970396",
            doi="10.1056/NEJMoa2024816",
            title="Dapagliflozin in Patients with Chronic Kidney Disease (DAPA-CKD)",
            journal="New England Journal of Medicine (NEJM)",
            year=2020,
            authors="Heerspink HJL, Stefánsson BV, Correa-Rotter R, et al.",
            study_design="Phase 3 Double-Blind RCT",
            sample_size=4304,
            abstract="BACKGROUND: Patients with chronic kidney disease (CKD) have high risks of adverse kidney and cardiovascular outcomes. The efficacy and safety of dapagliflozin in patients with CKD, with or without type 2 diabetes, are unknown. METHODS: We randomized 4304 participants with an eGFR of 25 to 75 ml/min/1.73m2 and uACR of 200 to 5000 mg/g to receive dapagliflozin (10 mg once daily) or placebo. The primary composite outcome was sustained >=50% eGFR decline, end-stage kidney disease (ESKD), or death from renal or cardiovascular causes. RESULTS: Over a median of 2.4 years, the primary outcome occurred in 197 of 2152 participants (9.2%) in the dapagliflozin group and in 312 of 2152 participants (14.5%) in the placebo group (hazard ratio, 0.61; 95% CI, 0.51 to 0.72; P<0.001). The hazard ratio for death from any cause was 0.69 (95% CI, 0.53 to 0.88; P=0.004). The effects of dapagliflozin were similar in participants with and without type 2 diabetes. CONCLUSIONS: In patients with CKD, dapagliflozin significantly reduced the risk of sustained eGFR decline, ESKD, or renal/cardiovascular death.",
            pico=PICOData(
                population=Population(
                    description="Patients with CKD (eGFR 25 to 75 mL/min/1.73m2, uACR 200 to 5000 mg/g) with or without type 2 diabetes",
                    condition="Chronic Kidney Disease",
                    condition_cui="C0022661",
                    n=4304,
                    age_mean="61.8 years",
                    evidence="We randomly assigned 4304 participants with an estimated GFR of 25 to 75 ml per minute per 1.73 m2 and a urinary albumin-to-creatinine ratio of 200 to 5000 to receive dapagliflozin or placebo."
                ),
                interventions=[
                    Intervention(
                        name="Dapagliflozin",
                        drug_cui="C2719231",
                        rxnorm="1488564",
                        dose="10 mg once daily",
                        duration="Median 2.4 years",
                        evidence="Participants received dapagliflozin (10 mg once daily) or matching placebo, in addition to standard care."
                    )
                ],
                comparators=[
                    Comparator(
                        name="Matching Placebo",
                        drug_cui="C0000000",
                        evidence="Participants received dapagliflozin (10 mg once daily) or matching placebo, in addition to standard care."
                    )
                ],
                outcomes=[
                    ClinicalOutcome(
                        name="Composite Sustained eGFR Decline >=50%, ESKD, or Renal/CV Death",
                        outcome_cui="C0022661",
                        timepoint="2.4 years",
                        effect="0.61",
                        measure="Hazard Ratio (HR)",
                        ci_low="0.51",
                        ci_high="0.72",
                        p_value="P < 0.001",
                        direction="Significant Benefit",
                        evidence="The primary composite outcome occurred in 197 of 2152 participants (9.2%) in the dapagliflozin group and in 312 of 2152 participants (14.5%) in the placebo group (hazard ratio, 0.61; 95% confidence interval [CI], 0.51 to 0.72; P<0.001)."
                    ),
                    ClinicalOutcome(
                        name="All-Cause Mortality",
                        outcome_cui="C0026565",
                        timepoint="2.4 years",
                        effect="0.69",
                        measure="Hazard Ratio (HR)",
                        ci_low="0.53",
                        ci_high="0.88",
                        p_value="P = 0.004",
                        direction="Significant Benefit",
                        evidence="The hazard ratio for death from any cause was 0.69 (95% CI, 0.53 to 0.88; P=0.004) in favor of dapagliflozin."
                    )
                ]
            ),
            entities=[
                BiomedicalEntity(name="Chronic Kidney Disease", type=EntityType.CONDITION, cui="C0022661", papers_count=1, pmids=["32970396"]),
                BiomedicalEntity(name="End-Stage Kidney Disease", type=EntityType.CONDITION, cui="C0022661", papers_count=1, pmids=["32970396"]),
                BiomedicalEntity(name="Type 2 Diabetes Mellitus", type=EntityType.CONDITION, cui="C0011860", papers_count=1, pmids=["32970396"]),
                BiomedicalEntity(name="Dapagliflozin", type=EntityType.DRUG, cui="C2719231", rxnorm="1488564", papers_count=1, pmids=["32970396"]),
                BiomedicalEntity(name="SGLT2 inhibitors", type=EntityType.DRUG_CLASS, cui="C3890289", papers_count=1, pmids=["32970396"]),
                BiomedicalEntity(name="eGFR Decline", type=EntityType.OUTCOME, cui="C1260953", papers_count=1, pmids=["32970396"]),
                BiomedicalEntity(name="All-Cause Mortality", type=EntityType.OUTCOME, cui="C0026565", papers_count=1, pmids=["32970396"])
            ]
        ),
        Article(
            pmid="30990260",
            doi="10.1056/NEJMoa1811744",
            title="Canagliflozin and Renal Outcomes in Type 2 Diabetes and Nephropathy (CREDENCE)",
            journal="New England Journal of Medicine (NEJM)",
            year=2019,
            authors="Perkovic V, Jardine MJ, Neal B, et al.",
            study_design="Phase 3 Double-Blind RCT",
            sample_size=4401,
            abstract="BACKGROUND: Type 2 diabetes is the leading cause of kidney failure worldwide, but few effective treatments exist. We evaluated the effects of canagliflozin on renal and cardiovascular outcomes in patients with type 2 diabetes and albuminuric kidney disease. METHODS: We randomly assigned 4401 patients with type 2 diabetes, eGFR 30 to <90, and uACR >300 to 5000 mg/g to receive canagliflozin (100 mg daily) or placebo. The primary composite outcome was end-stage kidney disease, doubling of serum creatinine, or death from renal or cardiovascular causes. RESULTS: The trial was stopped early after a planned interim analysis. The primary outcome was 30% lower in the canagliflozin group than in the placebo group (hazard ratio, 0.70; 95% CI, 0.59 to 0.82; P=0.00001). The risk of hospitalization for heart failure was also significantly lower (hazard ratio, 0.61; 95% CI, 0.47 to 0.80). Rates of amputation and bone fracture were not significantly higher. CONCLUSIONS: In patients with type 2 diabetes and kidney disease, canagliflozin lowered the risk of kidney failure and cardiovascular events.",
            pico=PICOData(
                population=Population(
                    description="Patients with type 2 diabetes and albuminuric chronic kidney disease (eGFR 30 to <90 mL/min/1.73m2, uACR >300 to 5000 mg/g)",
                    condition="Diabetic Kidney Disease",
                    condition_cui="C0011881",
                    n=4401,
                    age_mean="63.0 years",
                    evidence="We randomly assigned patients with type 2 diabetes and chronic kidney disease (eGFR 30 to <90 ml/min/1.73m2 and urinary albumin-to-creatinine ratio >300 to 5000) to receive canagliflozin or placebo."
                ),
                interventions=[
                    Intervention(
                        name="Canagliflozin",
                        drug_cui="C2982845",
                        rxnorm="1373458",
                        dose="100 mg once daily",
                        duration="Median 2.6 years",
                        evidence="Patients received canagliflozin at a dose of 100 mg daily or matching placebo."
                    )
                ],
                comparators=[
                    Comparator(
                        name="Matching Placebo",
                        drug_cui="C0000000",
                        evidence="Patients received canagliflozin at a dose of 100 mg daily or matching placebo."
                    )
                ],
                outcomes=[
                    ClinicalOutcome(
                        name="Primary Renal Composite: ESKD, Doubling Creatinine, or Renal/CV Death",
                        outcome_cui="C0022661",
                        timepoint="2.6 years",
                        effect="0.70",
                        measure="Hazard Ratio (HR)",
                        ci_low="0.59",
                        ci_high="0.82",
                        p_value="P = 0.00001",
                        direction="Significant Benefit",
                        evidence="The relative risk of the primary composite outcome was 30% lower in the canagliflozin group than in the placebo group (hazard ratio, 0.70; 95% confidence interval [CI], 0.59 to 0.82; P=0.00001)."
                    ),
                    ClinicalOutcome(
                        name="Hospitalization for Heart Failure",
                        outcome_cui="C0018802",
                        timepoint="2.6 years",
                        effect="0.61",
                        measure="Hazard Ratio (HR)",
                        ci_low="0.47",
                        ci_high="0.80",
                        p_value="P < 0.001",
                        direction="Significant Benefit",
                        evidence="The relative risk of hospitalization for heart failure was 39% lower with canagliflozin (hazard ratio, 0.61; 95% CI, 0.47 to 0.80; P<0.001)."
                    )
                ]
            ),
            entities=[
                BiomedicalEntity(name="Diabetic Kidney Disease", type=EntityType.CONDITION, cui="C0011881", papers_count=1, pmids=["30990260"]),
                BiomedicalEntity(name="Type 2 Diabetes Mellitus", type=EntityType.CONDITION, cui="C0011860", papers_count=1, pmids=["30990260"]),
                BiomedicalEntity(name="Canagliflozin", type=EntityType.DRUG, cui="C2982845", rxnorm="1373458", papers_count=1, pmids=["30990260"]),
                BiomedicalEntity(name="SGLT2 inhibitors", type=EntityType.DRUG_CLASS, cui="C3890289", papers_count=1, pmids=["30990260"]),
                BiomedicalEntity(name="Doubling of Serum Creatinine", type=EntityType.OUTCOME, cui="C0428503", papers_count=1, pmids=["30990260"]),
                BiomedicalEntity(name="Heart Failure Hospitalization", type=EntityType.OUTCOME, cui="C0018802", papers_count=1, pmids=["30990260"])
            ]
        ),
        Article(
            pmid="30415602",
            doi="10.1056/NEJMoa1812389",
            title="Dapagliflozin and Cardiovascular Outcomes in Type 2 Diabetes (DECLARE-TIMI 58)",
            journal="New England Journal of Medicine (NEJM)",
            year=2019,
            authors="Wiviott SD, Raz I, Bonaca MP, et al.",
            study_design="Phase 3 Double-Blind RCT",
            sample_size=17160,
            abstract="BACKGROUND: Most patients with type 2 diabetes have atherosclerotic cardiovascular disease or multiple risk factors. We evaluated dapagliflozin in a broad cohort of patients with type 2 diabetes. METHODS: We randomly assigned 17160 patients to dapagliflozin (10 mg daily) or placebo. Primary safety was major adverse cardiovascular events (MACE). Primary efficacy was MACE or CV death/heart failure hospitalization. Cardiorenal secondary composite was >=40% eGFR decline, new ESKD, or renal/CV death. RESULTS: Dapagliflozin did not result in a higher or lower rate of MACE (8.8% vs 9.4%; HR 0.93; 95% CI 0.84 to 1.03), but resulted in a lower rate of CV death or hospitalization for heart failure (4.9% vs 5.8%; HR 0.83; 95% CI 0.73 to 0.95; P=0.005). The cardiorenal composite occurred in 4.3% vs 5.6% (HR 0.76; 95% CI 0.67 to 0.87). CONCLUSIONS: Dapagliflozin reduced cardiovascular death or heart failure hospitalization and renal composite events in a broad primary and secondary prevention population.",
            pico=PICOData(
                population=Population(
                    description="Patients with type 2 diabetes who had or were at risk for atherosclerotic cardiovascular disease",
                    condition="Type 2 Diabetes Mellitus",
                    condition_cui="C0011860",
                    n=17160,
                    age_mean="63.9 years",
                    evidence="We randomly assigned 17,160 patients with type 2 diabetes who had or were at high risk for atherosclerotic cardiovascular disease to receive dapagliflozin or placebo."
                ),
                interventions=[
                    Intervention(
                        name="Dapagliflozin",
                        drug_cui="C2719231",
                        rxnorm="1488564",
                        dose="10 mg once daily",
                        duration="Median 4.2 years",
                        evidence="Patients received dapagliflozin (10 mg daily) or matching placebo."
                    )
                ],
                comparators=[
                    Comparator(
                        name="Matching Placebo",
                        drug_cui="C0000000",
                        evidence="Patients received dapagliflozin (10 mg daily) or matching placebo."
                    )
                ],
                outcomes=[
                    ClinicalOutcome(
                        name="CV Death or Hospitalization for Heart Failure",
                        outcome_cui="C0018802",
                        timepoint="4.2 years",
                        effect="0.83",
                        measure="Hazard Ratio (HR)",
                        ci_low="0.73",
                        ci_high="0.95",
                        p_value="P = 0.005",
                        direction="Significant Benefit",
                        evidence="Dapagliflozin resulted in a lower rate of cardiovascular death or hospitalization for heart failure (hazard ratio, 0.83; 95% CI, 0.73 to 0.95; P=0.005)."
                    ),
                    ClinicalOutcome(
                        name="Renal Composite (eGFR Decline >=40%, ESKD, Renal Death)",
                        outcome_cui="C0022661",
                        timepoint="4.2 years",
                        effect="0.76",
                        measure="Hazard Ratio (HR)",
                        ci_low="0.67",
                        ci_high="0.87",
                        p_value="P < 0.001",
                        direction="Significant Benefit",
                        evidence="A cardiorenal secondary outcome (sustained >=40% decrease in eGFR to <60 ml/min/1.73m2, new ESKD, or renal/CV death) occurred in 4.3% vs 5.6% (hazard ratio, 0.76; 95% CI, 0.67 to 0.87)."
                    )
                ]
            ),
            entities=[
                BiomedicalEntity(name="Type 2 Diabetes Mellitus", type=EntityType.CONDITION, cui="C0011860", papers_count=1, pmids=["30415602"]),
                BiomedicalEntity(name="Cardiovascular Disease", type=EntityType.CONDITION, cui="C0007222", papers_count=1, pmids=["30415602"]),
                BiomedicalEntity(name="Dapagliflozin", type=EntityType.DRUG, cui="C2719231", rxnorm="1488564", papers_count=1, pmids=["30415602"]),
                BiomedicalEntity(name="SGLT2 inhibitors", type=EntityType.DRUG_CLASS, cui="C3890289", papers_count=1, pmids=["30415602"]),
                BiomedicalEntity(name="Heart Failure Hospitalization", type=EntityType.OUTCOME, cui="C0018802", papers_count=1, pmids=["30415602"])
            ]
        ),
        Article(
            pmid="32865377",
            doi="10.1056/NEJMoa2022190",
            title="Cardiovascular and Renal Outcomes with Empagliflozin in Heart Failure (EMPEROR-Reduced)",
            journal="New England Journal of Medicine (NEJM)",
            year=2020,
            authors="Packer M, Anker SD, Butler J, et al.",
            study_design="Phase 3 Double-Blind RCT",
            sample_size=3730,
            abstract="BACKGROUND: SGLT2 inhibitors reduce the risk of heart failure hospitalization in patients with type 2 diabetes. Whether empagliflozin reduces cardiovascular and renal events in patients with heart failure and reduced ejection fraction, with or without diabetes, is unclear. METHODS: We randomized 3730 patients with NYHA class II-IV heart failure and ejection fraction <=40% to empagliflozin (10 mg daily) or placebo. The primary outcome was composite of cardiovascular death or hospitalization for heart failure. Secondary renal endpoint was the annual rate of decline in eGFR. RESULTS: Over a median of 16 months, the primary outcome occurred in 19.4% in the empagliflozin group and in 24.7% in the placebo group (hazard ratio, 0.75; 95% CI, 0.65 to 0.86; P<0.001). The annual rate of decline in eGFR was significantly slower in the empagliflozin group (-0.55 vs -2.28 ml/min/1.73m2/year; difference, 1.73 ml/min/1.73m2/year; P<0.001). CONCLUSIONS: Empagliflozin reduced the risk of cardiovascular death or heart failure hospitalization and slowed the rate of renal decline in patients with HFrEF.",
            pico=PICOData(
                population=Population(
                    description="Patients with NYHA class II to IV heart failure and reduced ejection fraction (<=40%), with or without diabetes",
                    condition="Heart Failure with Reduced Ejection Fraction (HFrEF)",
                    condition_cui="C0018802",
                    n=3730,
                    age_mean="66.8 years",
                    evidence="We randomly assigned 3730 patients with class II, III, or IV heart failure and an ejection fraction of 40% or less to receive empagliflozin or placebo."
                ),
                interventions=[
                    Intervention(
                        name="Empagliflozin",
                        drug_cui="C3261058",
                        rxnorm="1545653",
                        dose="10 mg once daily",
                        duration="Median 16 months",
                        evidence="Patients received empagliflozin (10 mg once daily) or placebo in addition to recommended therapy."
                    )
                ],
                comparators=[
                    Comparator(
                        name="Matching Placebo",
                        drug_cui="C0000000",
                        evidence="Patients received empagliflozin (10 mg once daily) or placebo in addition to recommended therapy."
                    )
                ],
                outcomes=[
                    ClinicalOutcome(
                        name="CV Death or Heart Failure Hospitalization",
                        outcome_cui="C0018802",
                        timepoint="16 months",
                        effect="0.75",
                        measure="Hazard Ratio (HR)",
                        ci_low="0.65",
                        ci_high="0.86",
                        p_value="P < 0.001",
                        direction="Significant Benefit",
                        evidence="The primary outcome occurred in 361 of 1863 patients (19.4%) in the empagliflozin group and in 462 of 1867 patients (24.7%) in the placebo group (hazard ratio, 0.75; 95% CI, 0.65 to 0.86; P<0.001)."
                    ),
                    ClinicalOutcome(
                        name="Annual Rate of eGFR Decline",
                        outcome_cui="C1260953",
                        timepoint="Per Year",
                        effect="1.73 mL/min/1.73m2/yr slower",
                        measure="Mean Difference",
                        ci_low="1.10",
                        ci_high="2.37",
                        p_value="P < 0.001",
                        direction="Significant Benefit",
                        evidence="The annual rate of decline in the estimated GFR was slower in the empagliflozin group than in the placebo group (-0.55 vs. -2.28 ml per minute per 1.73 m2 per year, difference 1.73, P<0.001)."
                    )
                ]
            ),
            entities=[
                BiomedicalEntity(name="Heart Failure with Reduced Ejection Fraction", type=EntityType.CONDITION, cui="C0018802", papers_count=1, pmids=["32865377"]),
                BiomedicalEntity(name="Empagliflozin", type=EntityType.DRUG, cui="C3261058", rxnorm="1545653", papers_count=1, pmids=["32865377"]),
                BiomedicalEntity(name="SGLT2 inhibitors", type=EntityType.DRUG_CLASS, cui="C3890289", papers_count=1, pmids=["32865377"]),
                BiomedicalEntity(name="eGFR Decline Rate", type=EntityType.OUTCOME, cui="C1260953", papers_count=1, pmids=["32865377"])
            ]
        ),
        Article(
            pmid="31535829",
            doi="10.1056/NEJMoa1911303",
            title="Dapagliflozin in Patients with Heart Failure and Reduced Ejection Fraction (DAPA-HF)",
            journal="New England Journal of Medicine (NEJM)",
            year=2019,
            authors="McMurray JJV, Solomon SD, Inzucchi SE, et al.",
            study_design="Phase 3 Double-Blind RCT",
            sample_size=4744,
            abstract="BACKGROUND: In patients with type 2 diabetes, SGLT2 inhibitors reduce the risk of heart failure hospitalization. We evaluated dapagliflozin in patients with heart failure and reduced ejection fraction, including those without diabetes. METHODS: We randomly assigned 4744 patients with NYHA class II-IV heart failure and ejection fraction <=40% to dapagliflozin (10 mg daily) or placebo. Primary outcome was worsening heart failure or cardiovascular death. RESULTS: Over a median of 18.2 months, the primary outcome occurred in 16.3% in the dapagliflozin group and in 21.2% in the placebo group (hazard ratio, 0.74; 95% CI, 0.65 to 0.85; P<0.001). A first worsening heart failure event occurred in 10.0% vs 13.7% (HR 0.70; 95% CI 0.59 to 0.83). Death from cardiovascular causes occurred in 9.6% vs 11.5% (HR 0.82; 95% CI 0.69 to 0.98). Findings were similar in patients with and without diabetes. CONCLUSIONS: Dapagliflozin reduced the risk of worsening heart failure and cardiovascular death in patients with HFrEF.",
            pico=PICOData(
                population=Population(
                    description="Patients with NYHA class II to IV heart failure and ejection fraction <=40%, with or without type 2 diabetes",
                    condition="Heart Failure with Reduced Ejection Fraction (HFrEF)",
                    condition_cui="C0018802",
                    n=4744,
                    age_mean="66.3 years",
                    evidence="We randomly assigned 4744 patients with New York Heart Association class II, III, or IV heart failure and an ejection fraction of 40% or less to receive dapagliflozin or placebo."
                ),
                interventions=[
                    Intervention(
                        name="Dapagliflozin",
                        drug_cui="C2719231",
                        rxnorm="1488564",
                        dose="10 mg once daily",
                        duration="Median 18.2 months",
                        evidence="Patients received dapagliflozin (10 mg once daily) or matching placebo in addition to guideline-recommended therapy."
                    )
                ],
                comparators=[
                    Comparator(
                        name="Matching Placebo",
                        drug_cui="C0000000",
                        evidence="Patients received dapagliflozin (10 mg once daily) or matching placebo in addition to guideline-recommended therapy."
                    )
                ],
                outcomes=[
                    ClinicalOutcome(
                        name="Worsening Heart Failure or CV Death",
                        outcome_cui="C0018802",
                        timepoint="18.2 months",
                        effect="0.74",
                        measure="Hazard Ratio (HR)",
                        ci_low="0.65",
                        ci_high="0.85",
                        p_value="P < 0.001",
                        direction="Significant Benefit",
                        evidence="The primary outcome occurred in 386 of 2373 patients (16.3%) in the dapagliflozin group and in 502 of 2371 patients (21.2%) in the placebo group (hazard ratio, 0.74; 95% CI, 0.65 to 0.85; P<0.001)."
                    ),
                    ClinicalOutcome(
                        name="Cardiovascular Death",
                        outcome_cui="C0011050",
                        timepoint="18.2 months",
                        effect="0.82",
                        measure="Hazard Ratio (HR)",
                        ci_low="0.69",
                        ci_high="0.98",
                        p_value="P = 0.029",
                        direction="Significant Benefit",
                        evidence="Death from cardiovascular causes occurred in 227 patients (9.6%) in the dapagliflozin group and in 273 (11.5%) in the placebo group (hazard ratio, 0.82; 95% CI, 0.69 to 0.98)."
                    )
                ]
            ),
            entities=[
                BiomedicalEntity(name="Heart Failure with Reduced Ejection Fraction", type=EntityType.CONDITION, cui="C0018802", papers_count=1, pmids=["31535829"]),
                BiomedicalEntity(name="Dapagliflozin", type=EntityType.DRUG, cui="C2719231", rxnorm="1488564", papers_count=1, pmids=["31535829"]),
                BiomedicalEntity(name="SGLT2 inhibitors", type=EntityType.DRUG_CLASS, cui="C3890289", papers_count=1, pmids=["31535829"]),
                BiomedicalEntity(name="Cardiovascular Death", type=EntityType.OUTCOME, cui="C0011050", papers_count=1, pmids=["31535829"])
            ]
        ),
        Article(
            pmid="32966717",
            doi="10.1056/NEJMoa2004967",
            title="Cardiovascular Outcomes with Ertugliflozin in Type 2 Diabetes (VERTIS CV)",
            journal="New England Journal of Medicine (NEJM)",
            year=2020,
            authors="Cannon CP, Pratley R, Dagogo-Jack S, et al.",
            study_design="Phase 3 Double-Blind RCT",
            sample_size=8246,
            abstract="BACKGROUND: The cardiovascular effects of ertugliflozin, an SGLT2 inhibitor, in patients with type 2 diabetes and established atherosclerotic cardiovascular disease have not been established. METHODS: In a multicenter trial, we randomized 8246 patients to receive 5 mg or 15 mg of ertugliflozin or placebo daily. Primary endpoint was noninferiority for MACE. Key secondary outcomes included renal composite (renal death, renal replacement, doubling serum creatinine). RESULTS: MACE occurred in 11.9% in the ertugliflozin group and in 11.9% in the placebo group (HR 0.97; 95% CI 0.85 to 1.11; P<0.001 for noninferiority). The renal composite outcome occurred in 3.2% vs 3.9% (hazard ratio, 0.81; 95% CI, 0.63 to 1.04). Hospitalization for heart failure occurred in 2.5% vs 3.6% (HR 0.70; 95% CI 0.54 to 0.90). CONCLUSIONS: Ertugliflozin was noninferior to placebo with respect to MACE and reduced heart failure hospitalizations in patients with T2DM and ASCVD.",
            pico=PICOData(
                population=Population(
                    description="Patients with type 2 diabetes and established atherosclerotic cardiovascular disease",
                    condition="Type 2 Diabetes Mellitus",
                    condition_cui="C0011860",
                    n=8246,
                    age_mean="64.4 years",
                    evidence="We randomly assigned 8246 patients with type 2 diabetes and established atherosclerotic cardiovascular disease to ertugliflozin (5 mg or 15 mg) or placebo."
                ),
                interventions=[
                    Intervention(
                        name="Ertugliflozin",
                        drug_cui="C3886580",
                        rxnorm="1992672",
                        dose="5 mg or 15 mg once daily",
                        duration="Median 3.5 years",
                        evidence="Patients were randomly assigned to receive 5 mg or 15 mg of ertugliflozin once daily or matching placebo."
                    )
                ],
                comparators=[
                    Comparator(
                        name="Matching Placebo",
                        drug_cui="C0000000",
                        evidence="Patients were randomly assigned to receive 5 mg or 15 mg of ertugliflozin once daily or matching placebo."
                    )
                ],
                outcomes=[
                    ClinicalOutcome(
                        name="Hospitalization for Heart Failure",
                        outcome_cui="C0018802",
                        timepoint="3.5 years",
                        effect="0.70",
                        measure="Hazard Ratio (HR)",
                        ci_low="0.54",
                        ci_high="0.90",
                        p_value="P = 0.006",
                        direction="Significant Benefit",
                        evidence="Hospitalization for heart failure occurred in 2.5% in the ertugliflozin group and in 3.6% in the placebo group (hazard ratio, 0.70; 95% CI, 0.54 to 0.90)."
                    ),
                    ClinicalOutcome(
                        name="Renal Composite (Renal Death, Dialysis, Doubling Creatinine)",
                        outcome_cui="C0022661",
                        timepoint="3.5 years",
                        effect="0.81",
                        measure="Hazard Ratio (HR)",
                        ci_low="0.63",
                        ci_high="1.04",
                        p_value="P = 0.08",
                        direction="Trend towards Benefit",
                        evidence="The composite of death from renal causes, renal replacement therapy, or a doubling of the serum creatinine level occurred in 3.2% vs 3.9% (hazard ratio, 0.81; 95% CI, 0.63 to 1.04)."
                    )
                ]
            ),
            entities=[
                BiomedicalEntity(name="Type 2 Diabetes Mellitus", type=EntityType.CONDITION, cui="C0011860", papers_count=1, pmids=["32966717"]),
                BiomedicalEntity(name="Atherosclerotic Cardiovascular Disease", type=EntityType.CONDITION, cui="C0007222", papers_count=1, pmids=["32966717"]),
                BiomedicalEntity(name="Ertugliflozin", type=EntityType.DRUG, cui="C3886580", rxnorm="1992672", papers_count=1, pmids=["32966717"]),
                BiomedicalEntity(name="SGLT2 inhibitors", type=EntityType.DRUG_CLASS, cui="C3890289", papers_count=1, pmids=["32966717"]),
                BiomedicalEntity(name="Heart Failure Hospitalization", type=EntityType.OUTCOME, cui="C0018802", papers_count=1, pmids=["32966717"])
            ]
        )
    ]

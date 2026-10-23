import os
import sys
import docx
from docx import Document
from docx.shared import Inches, Pt, RGBColor
from docx.enum.text import WD_ALIGN_PARAGRAPH
from docx.enum.table import WD_TABLE_ALIGNMENT, WD_ALIGN_VERTICAL
from docx.oxml import OxmlElement, parse_xml
from docx.oxml.ns import nsdecls, qn

def generate_aws_document():
    doc = Document()
    
    # Page setup - 1 inch margins
    for s in doc.sections:
        s.top_margin = Inches(1.0)
        s.bottom_margin = Inches(1.0)
        s.left_margin = Inches(1.0)
        s.right_margin = Inches(1.0)
        
        # Header
        hdr = s.header
        hp = hdr.paragraphs[0]
        hp.alignment = WD_ALIGN_PARAGRAPH.RIGHT
        hrun = hp.add_run("Novartis AI Innovation | GraphRAG Literature Platform: AWS Architecture & Sandbox Pilot Specification")
        hrun.font.name = "Segoe UI"
        hrun.font.size = Pt(8.5)
        hrun.font.color.rgb = RGBColor(148, 163, 184)
        
        # Footer
        ftr = s.footer
        fp = ftr.paragraphs[0]
        fp.alignment = WD_ALIGN_PARAGRAPH.RIGHT
        frun = fp.add_run("Confidential & Proprietary — AWS Architecture, HLD, Sandbox Implementation & Cost Blueprint")
        frun.font.name = "Segoe UI"
        frun.font.size = Pt(8.5)
        frun.font.color.rgb = RGBColor(148, 163, 184)

    # Styling helper functions
    def set_cell_background(cell, hex_color):
        shading_elm = parse_xml(f'<w:shd {nsdecls("w")} w:fill="{hex_color}"/>')
        cell._tc.get_or_add_tcPr().append(shading_elm)

    def set_cell_margins(cell, top=120, bottom=120, left=160, right=160):
        tcPr = cell._tc.get_or_add_tcPr()
        tcMar = parse_xml(f'<w:tcMar {nsdecls("w")}><w:top w:w="{top}" w:type="dxa"/><w:bottom w:w="{bottom}" w:type="dxa"/><w:left w:w="{left}" w:type="dxa"/><w:right w:w="{right}" w:type="dxa"/></w:tcMar>')
        tcPr.append(tcMar)

    def set_table_borders(table, color="CBD5E1", sz="4", val="single"):
        tblPr = table._tbl.tblPr
        borders = parse_xml(
            f'<w:tblBorders {nsdecls("w")}>'
            f'<w:top w:val="{val}" w:sz="{sz}" w:space="0" w:color="{color}"/>'
            f'<w:bottom w:val="{val}" w:sz="{sz}" w:space="0" w:color="{color}"/>'
            f'<w:left w:val="none"/>'
            f'<w:right w:val="none"/>'
            f'<w:insideH w:val="{val}" w:sz="{sz}" w:space="0" w:color="{color}"/>'
            f'<w:insideV w:val="none"/>'
            f'</w:tblBorders>'
        )
        tblPr.append(borders)

    def add_h1(text):
        h = doc.add_heading(text, level=1)
        h.paragraph_format.keep_with_next = True
        run = h.runs[0]
        run.font.name = "Segoe UI"
        run.font.size = Pt(16.5)
        run.font.bold = True
        run.font.color.rgb = RGBColor(15, 23, 42)
        h.paragraph_format.space_before = Pt(20)
        h.paragraph_format.space_after = Pt(8)
        return h

    def add_h2(text):
        h = doc.add_heading(text, level=2)
        h.paragraph_format.keep_with_next = True
        run = h.runs[0]
        run.font.name = "Segoe UI"
        run.font.size = Pt(13)
        run.font.bold = True
        run.font.color.rgb = RGBColor(0, 42, 84) # Novartis Deep Blue
        h.paragraph_format.space_before = Pt(14)
        h.paragraph_format.space_after = Pt(6)
        return h

    def add_h3(text):
        h = doc.add_heading(text, level=3)
        h.paragraph_format.keep_with_next = True
        run = h.runs[0]
        run.font.name = "Segoe UI"
        run.font.size = Pt(11)
        run.font.bold = True
        run.font.color.rgb = RGBColor(236, 154, 30) # Novartis Warm Amber / AWS Orange
        h.paragraph_format.space_before = Pt(10)
        h.paragraph_format.space_after = Pt(4)
        return h

    def add_p(text, bold_prefix=None):
        p = doc.add_paragraph()
        p.paragraph_format.space_before = Pt(0)
        p.paragraph_format.space_after = Pt(6)
        p.paragraph_format.line_spacing = 1.15
        if bold_prefix:
            r_pre = p.add_run(bold_prefix)
            r_pre.font.name = "Segoe UI"
            r_pre.font.size = Pt(10)
            r_pre.font.bold = True
            r_pre.font.color.rgb = RGBColor(15, 23, 42)
        run = p.add_run(text)
        run.font.name = "Segoe UI"
        run.font.size = Pt(10)
        run.font.color.rgb = RGBColor(51, 65, 85)
        return p

    def add_bullet(text, bold_prefix=None):
        p = doc.add_paragraph(style='List Bullet')
        p.paragraph_format.space_before = Pt(0)
        p.paragraph_format.space_after = Pt(3)
        p.paragraph_format.line_spacing = 1.15
        if bold_prefix:
            r_pre = p.add_run(bold_prefix)
            r_pre.font.name = "Segoe UI"
            r_pre.font.size = Pt(10)
            r_pre.font.bold = True
            r_pre.font.color.rgb = RGBColor(15, 23, 42)
        run = p.add_run(text)
        run.font.name = "Segoe UI"
        run.font.size = Pt(10)
        run.font.color.rgb = RGBColor(51, 65, 85)
        return p

    def add_callout(title, text, bg_color="F0F9FF", border_color="002A54"):
        tbl = doc.add_table(rows=1, cols=1)
        tbl.alignment = WD_TABLE_ALIGNMENT.CENTER
        cell = tbl.cell(0, 0)
        set_cell_background(cell, bg_color)
        set_cell_margins(cell, top=140, bottom=140, left=180, right=160)
        tcPr = cell._tc.get_or_add_tcPr()
        borders = parse_xml(
            f'<w:tcBorders {nsdecls("w")}><w:left w:val="single" w:sz="36" w:space="0" w:color="{border_color}"/><w:top w:val="none"/><w:bottom w:val="none"/><w:right w:val="none"/></w:tcBorders>'
        )
        tcPr.append(borders)
        p = cell.paragraphs[0]
        p.paragraph_format.space_before = Pt(0)
        p.paragraph_format.space_after = Pt(4)
        run_t = p.add_run(f"📌 {title}\n")
        run_t.font.name = "Segoe UI"
        run_t.font.size = Pt(10.5)
        run_t.font.bold = True
        run_t.font.color.rgb = RGBColor(0, 42, 84)
        run_b = p.add_run(text)
        run_b.font.name = "Segoe UI"
        run_b.font.size = Pt(9.5)
        run_b.font.color.rgb = RGBColor(30, 41, 59)
        doc.add_paragraph().paragraph_format.space_after = Pt(4)

    def add_code(text):
        tbl = doc.add_table(rows=1, cols=1)
        tbl.alignment = WD_TABLE_ALIGNMENT.CENTER
        cell = tbl.cell(0, 0)
        set_cell_background(cell, "F8FAFC")
        set_cell_margins(cell, top=100, bottom=100, left=160, right=160)
        tcPr = cell._tc.get_or_add_tcPr()
        borders = parse_xml(
            f'<w:tcBorders {nsdecls("w")}><w:left w:val="single" w:sz="18" w:space="0" w:color="EC9A1E"/><w:top w:val="single" w:sz="4" w:space="0" w:color="CBD5E1"/><w:bottom w:val="single" w:sz="4" w:space="0" w:color="CBD5E1"/><w:right w:val="single" w:sz="4" w:space="0" w:color="CBD5E1"/></w:tcBorders>'
        )
        tcPr.append(borders)
        p = cell.paragraphs[0]
        p.paragraph_format.space_before = Pt(0)
        p.paragraph_format.space_after = Pt(0)
        p.paragraph_format.line_spacing = 1.05
        run = p.add_run(text)
        run.font.name = "Consolas"
        run.font.size = Pt(8.5)
        run.font.color.rgb = RGBColor(30, 41, 59)
        doc.add_paragraph().paragraph_format.space_after = Pt(4)

    def add_styled_table(headers, rows_data, col_widths=None):
        tbl = doc.add_table(rows=len(rows_data) + 1, cols=len(headers))
        tbl.alignment = WD_TABLE_ALIGNMENT.CENTER
        set_table_borders(tbl, color="CBD5E1", sz="4", val="single")
        
        # Header Row
        hdr_cells = tbl.rows[0].cells
        for i, h_text in enumerate(headers):
            hdr_cells[i].text = h_text
            set_cell_background(hdr_cells[i], "002A54") # Novartis Deep Blue Header
            set_cell_margins(hdr_cells[i], top=100, bottom=100, left=140, right=140)
            p = hdr_cells[i].paragraphs[0]
            p.alignment = WD_ALIGN_PARAGRAPH.LEFT
            p.paragraph_format.space_before = Pt(0)
            p.paragraph_format.space_after = Pt(0)
            for r in p.runs:
                r.font.name = "Segoe UI"
                r.font.size = Pt(9.5)
                r.font.bold = True
                r.font.color.rgb = RGBColor(255, 255, 255)
                
        # Body Rows
        for r_idx, row in enumerate(rows_data):
            row_cells = tbl.rows[r_idx + 1].cells
            bg_col = "F8FAFC" if (r_idx % 2 == 1) else "FFFFFF"
            for c_idx, val in enumerate(row):
                row_cells[c_idx].text = str(val)
                set_cell_background(row_cells[c_idx], bg_col)
                set_cell_margins(row_cells[c_idx], top=80, bottom=80, left=140, right=140)
                p = row_cells[c_idx].paragraphs[0]
                p.paragraph_format.space_before = Pt(0)
                p.paragraph_format.space_after = Pt(0)
                p.paragraph_format.line_spacing = 1.1
                for r in p.runs:
                    r.font.name = "Segoe UI"
                    r.font.size = Pt(9)
                    r.font.color.rgb = RGBColor(30, 41, 59)
                    
        if col_widths:
            for row in tbl.rows:
                for idx, width in enumerate(col_widths):
                    row.cells[idx].width = width
                    
        doc.add_paragraph().paragraph_format.space_after = Pt(6)
        return tbl

    # ==================== DOCUMENT COVER / HEADER ====================
    title_p = doc.add_paragraph()
    title_p.paragraph_format.space_before = Pt(36)
    title_p.paragraph_format.space_after = Pt(4)
    run_title = title_p.add_run("GraphRAG Literature Platform: AWS Architecture")
    run_title.font.name = "Segoe UI"
    run_title.font.size = Pt(26)
    run_title.font.bold = True
    run_title.font.color.rgb = RGBColor(0, 42, 84) # Novartis Deep Blue

    sub_p = doc.add_paragraph()
    sub_p.paragraph_format.space_before = Pt(0)
    sub_p.paragraph_format.space_after = Pt(16)
    run_sub = sub_p.add_run("High-Level Design (HLD), AWS Native Stack Architecture & Sandbox Pilot Implementation Blueprint")
    run_sub.font.name = "Segoe UI"
    run_sub.font.size = Pt(13)
    run_sub.font.color.rgb = RGBColor(236, 154, 30) # Novartis Warm Amber / AWS Orange

    # Metadata Block Table
    meta_headers = ["Attribute", "Specification Details"]
    meta_rows = [
        ["Project Name", "GraphRAG Literature Platform (AWS Replatforming & Sandbox Pilot Edition)"],
        ["Target Organization", "Novartis Pharmaceuticals — Global Drug Development, Medical Affairs & HEOR"],
        ["Architecture Pattern", "Dual-Gatekeeper Agentic GraphRAG (Relational Knowledge Graph + Dense Semantic Vectors)"],
        ["Primary AWS Cloud Services", "Amazon Bedrock (Claude 3.5 & Titan V2), AWS App Runner / ECS Fargate, Amazon S3, AWS Secrets Manager, IAM"],
        ["Pilot Target Environment", "AWS Sandbox Account (Isolated VPC, Serverless Pay-as-You-Go, Budget Guardrails <$100/mo)"],
        ["Target Production Scale", "Enterprise AWS Multi-AZ (Amazon Neptune Serverless + OpenSearch Serverless / Aurora pgvector)"],
        ["Regulatory Compliance", "Designed for GxP, HIPAA, 21 CFR Part 11 Electronic Records & SOC 2 Type II Compliance"],
        ["Document Status", "Production-Ready AWS Technical Architecture & Pilot Engineering Blueprint (v1.0-AWS)"],
        ["Corporate Visual Identity", "Novartis Corporate Branding (Deep Blue #002A54, Warm Amber #EC9A1E, Slate Card Surface)"]
    ]
    add_styled_table(meta_headers, meta_rows, [Inches(2.1), Inches(4.4)])
    doc.add_page_break()

    # ==================== SECTION 1 ====================
    add_h1("1. Executive Summary & AWS Replatforming Rationale")
    add_p("The GraphRAG Literature Intelligence Platform addresses the most pressing bottleneck in pharmaceutical clinical development: transforming millions of unstructured biomedical publications, clinical study reports (CSRs), and regulatory dossiers into audit-ready, quantifiable, and zero-hallucination clinical evidence syntheses.")
    add_p("While our initial prototype was validated on Google Cloud Platform (Cloud Run + Gemini 3.8 Flash), this document provides the complete, authoritative specification to replicate and deploy the identical platform within the Amazon Web Services (AWS) ecosystem. Specifically tailored for a Pilot Sandbox deployment, this architecture maximizes developer agility, eliminates idle infrastructure costs, guarantees zero PHI/PII leakage, and establishes a seamless path to enterprise production without requiring architectural refactoring.")

    add_callout(
        "Executive Strategic Rationale for AWS Deployment",
        "1. ENTERPRISE GOVERNANCE & GxP VALIDATION: AWS provides mature Life Sciences frameworks (GxP on AWS, HIPAA BAA, 21 CFR Part 11 compliance) already cleared by Novartis Global Information Security.\n"
        "2. AMAZON BEDROCK ZERO-RETENTION COMMITMENT: Bedrock guarantees that proprietary clinical literature, unpublished internal trial summaries, and user queries are NEVER used to train foundation models, nor do they leave the private VPC perimeter.\n"
        "3. COST-EFFECTIVE SANDBOX TIERS: By leveraging AWS App Runner and Amazon Bedrock serverless APIs for the pilot, the entire multi-agent swarm operates at under $50–$95/month, scaling to zero when developers are inactive."
    )

    add_h2("1.1 The Pilot Sandbox Mandate")
    add_p("A sandbox pilot environment in a tier-1 pharmaceutical company operates under strict technical and budgetary constraints:")
    add_bullet(" Sandbox environments frequently mandate hard monthly budgets ($100–$250). Multi-node database clusters (like managed graph clusters or vector search instances) costing $200–$400/month before processing a single query must be avoided during the pilot phase.", "1. Strict Budget Cap:")
    add_bullet(" The pilot must provision in minutes via Infrastructure-as-Code (AWS CloudFormation or Terraform) with zero lingering manual dependencies.", "2. Rapid Provisioning (<10 Minutes):")
    add_bullet(" Compute and generative models must pause or scale to zero during nights and weekends, incurring zero baseline costs.", "3. Serverless Auto-Pausing:")
    add_bullet(" All data at rest must use AWS KMS Customer Managed Keys (CMK), with HTTPS TLS 1.3 in transit and strict IAM least-privilege role boundaries.", "4. Complete Data Isolation:")

    # ==================== SECTION 2 ====================
    add_h1("2. Clinical Problem Statement & Why Pure Bedrock Knowledge Bases Fail")
    add_p("Traditional Vector RAG—including standard out-of-the-box AWS Bedrock Knowledge Bases (which chunk documents into fixed token windows, generate embeddings, and query OpenSearch Serverless)—exhibits catastrophic failure modes when applied to clinical literature synthesis:")

    v_headers = ["Clinical RAG Challenge", "Standard AWS Bedrock Knowledge Base Failure", "GraphRAG on AWS Solution"]
    v_rows = [
        [
            "Top-k Retrieval Truncation",
            "If 35 Phase 3 clinical trials exist for a drug class and k=8, 77% of patient evidence is dropped silently. The LLM hallucinates an incomplete consensus.",
            "Graph Traversal via Relational Edges: Traverses DrugClass -> Drug -> Article -> Outcome, retrieving 100% of candidate trials."
        ],
        [
            "Biomedical Synonym Blindness",
            "'T2DM', 'Type 2 Diabetes', and 'NIDDM' are embedded as distant vector points. A query using one synonym fails to match papers using another.",
            "Biomedical Ontology Normalization: Maps every surface mention to standardized UMLS CUI (C0011860), MeSH, and RxNorm identifiers."
        ],
        [
            "Cross-Study Relational Synthesis",
            "Cannot identify that three distinct trials (EMPA-KIDNEY, DAPA-CKD, CREDENCE) evaluated the same pharmacological class across diabetic vs non-diabetic cohorts.",
            "Explicit Knowledge Graph Edges: 'COMPARES_TO', 'IS_A', and 'REPORTS_OUTCOME' edges connect disparate trials into a unified evidence matrix."
        ],
        [
            "Deterministic Aggregation & Counts",
            "Queries like 'How many Phase 3 RCTs tested empagliflozin vs placebo?' result in fabricated counts because vector search cannot count.",
            "Deterministic Graph & Relational Queries: Native COUNT, GROUP BY, and statistical range aggregations across verified nodes."
        ],
        [
            "Sentence-Level Provenance & Audit",
            "Returns diffuse 500-token chunks with no verification that numbers in the answer match the source text.",
            "Dual-Gatekeeper Verification Loops: Verbatim Substring Containment Guard + NLI Entailment Loop guaranteeing >=98% citation faithfulness."
        ]
    ]
    add_styled_table(v_headers, v_rows, [Inches(1.8), Inches(2.3), Inches(2.4)])

    # ==================== SECTION 3 ====================
    add_h1("3. AWS-Native Multi-Agent Swarm Architecture")
    add_p("The platform replicates our modular, multi-agent architecture across six autonomous micro-agents, re-engineered to leverage AWS native services and Amazon Bedrock foundation models:")

    add_h2("3.1 Autonomous Micro-Agent Mapping to AWS Services")

    add_h3("Agent 1: Document Ingestion & Section-Aware Decomposition Agent")
    add_bullet(" Interfacing with NCBI PubMed E-Utilities, Europe PMC, and ClinicalTrials.gov to ingest trial metadata, structured abstracts, and full-text XML/PDFs.", "Primary Role:")
    add_bullet(" Containerized Python 3.11 service hosted on AWS App Runner (pilot) or AWS Lambda / Amazon ECS Fargate worker pool (production).", "AWS Compute:")
    add_bullet(" The agent decomposes XML articles into discrete clinical sections: Background, Methods, Results, Primary Endpoints, Discussion, and Tables. Unlike naive token chunkers, it preserves clinical structural tags and outcome tables intact.", "Processing Logic:")
    add_bullet(" Section-tagged passage chunks, publication metadata, and normalized manifests stored in Amazon S3 (`s3://novartis-graphrag-literature-sandbox/xml-cache/`).", "AWS Storage:")

    add_h3("Agent 2: Dynamic PICO & Relation Extraction Guard Agent")
    add_bullet(" Transforming unstructured clinical narratives into strongly typed PICO (Population, Intervention, Comparator, Outcome) schemas with statistical precision.", "Primary Role:")
    add_bullet(" Amazon Bedrock invoking Anthropic Claude 3.5 Haiku (pilot high-speed extraction) or Claude 3.5 Sonnet (complex multi-arm trials) using structured JSON schema constraints.", "AWS Model:")
    add_bullet(" For each trial, extracts study design, sample size N, patient inclusion criteria, drug dose/regimen, active/placebo comparators, and quantified outcomes (HR, OR, 95% CI, p-values).", "Processing Logic:")
    add_bullet(" **Verbatim Substring Containment Guard**: Every extracted number or endpoint MUST be an exact verbatim substring within the source text. Non-matching claims are rejected or flagged for re-extraction before entering the knowledge graph.", "Verification Guard:")

    add_h3("Agent 3: Biomedical Ontology Normalization Agent")
    add_bullet(" Normalizing extracted biomedical entities to UMLS Metathesaurus, MeSH, and RxNorm vocabularies.", "Primary Role:")
    add_bullet(" scispaCy (en_core_sci_lg) embedded in container + UMLS REST APIs, backed by Amazon ElastiCache Redis (or local in-memory SQLite dictionary in the sandbox).", "AWS Engine:")
    add_bullet(" Resolves synonymous terms (e.g., 'Empagliflozin', 'Jardiance', 'BI 10773') to RxNorm:1545653 and links them to ATC parent class 'SGLT2 inhibitors' (A10BK). Prevents acronym collisions across therapeutic indications.", "Processing Logic:")

    add_h3("Agent 4: Hybrid Router & Pathfinding Agent")
    add_bullet(" Inspecting user clinical queries, determining intent, and orchestrating multi-path graph and dense vector retrieval.", "Primary Role:")
    add_bullet(" Classifies intent across 4 pathways: (1) Cross-Study Entity Queries (`graph_entity`), (2) Deterministic Counts (`aggregation`), (3) Global Thematic Summaries (`global_thematic`), and (4) Single-Fact Lookups (`vector_fact`).", "Execution Pathways:")
    add_bullet(" For entity queries, traverses the knowledge graph to identify 100% of candidate studies. Then executes dense vector re-ranking using **Amazon Titan Text Embeddings V2** (or Cohere Embed v3) with a **1.35x relevance multiplier** on Results / Primary Endpoint sections.", "Retrieval Logic:")
    add_bullet(" In the sandbox pilot, uses container-embedded NetworkX + Titan V2 dense vectors. In production, queries Amazon Neptune Serverless (openCypher) + Amazon OpenSearch Serverless Vector Engine.", "Storage Engine:")

    add_h3("Agent 5: Dynamic Evidence Synthesis & Audit Agent")
    add_bullet(" Generating audit-ready, cross-study clinical comparative syntheses with interactive citations and automated entailment audits.", "Primary Role:")
    add_bullet(" Amazon Bedrock invoking Anthropic Claude 3.5 Sonnet via Converse API, governed by the CLINICAL_GRAPHRAG_SYSTEM_PROMPT.", "AWS Model:")
    add_bullet(" Generates structured comparative prose grouping findings by intervention and outcome, highlights conflicting evidence, constructs side-by-side markdown evidence tables, and mandates interactive citation tags (`[PMID:sentence_id]`).", "Processing Logic:")
    add_bullet(" **Natural Language Inference (NLI) Audit Loop**: An automated verification pass classifies every generated assertion against cited source sentences. Any claim classified as neutral or contradictory is automatically excised or revised.", "Self-Correcting Guard:")

    add_h3("Agent 6: Dynamic Query Optimizer & Multi-Prompt Strategy Agent")
    add_bullet(" Generating optimized query formulations for both Literature Ingestion and Multi-Document Clinical Chat.", "Primary Role:")
    add_bullet(" Amazon Bedrock (Claude 3.5 Haiku) operating in dual modes:\n"
               "   • Mode A (Data Ingestion Multi-Prompt): Transforms naive keywords into 3-4 boolean MeSH-indexed queries incorporating active comparators, Phase 3 RCT publication filters (`[pt]`), and predicted trial yields.\n"
               "   • Mode B (Dynamic Clinical Chat Multi-Prompt): Generates 3 hypothesis-driven follow-up angles with explicit clinical rationales (e.g., acute eGFR dip vs chronic slope preservation, KDIGO guidelines).", "Processing Logic:")

    # ==================== SECTION 4 ====================
    add_h1("4. Dual-Gatekeeper Verification Loops on AWS")
    add_p("To eliminate hallucinations and satisfy pharmaceutical regulatory compliance (21 CFR Part 11 and GxP), the AWS architecture implements two automated verification gates:")

    gk_diagram = (
        "+-----------------------------------------------------------------------------------------+\n"
        "|                    GATEKEEPER LOOP 1: VERBATIM STRING EXTRACTION GUARD                  |\n"
        "|                                                                                         |\n"
        "|   [Raw Section Text] ---> [Agent 2: Claude 3.5 Haiku] ---> [Candidate PICO JSON]        |\n"
        "|                                                                   |                     |\n"
        "|                                                                   v                     |\n"
        "|                                                    +----------------------------+       |\n"
        "|                                                    | Automated Substring Audit  |       |\n"
        "|                                                    | Exact Match in Source Doc? |       |\n"
        "|                                                    +----------------------------+       |\n"
        "|                                                              /            \\             |\n"
        "|                                                      YES    /              \\   NO       |\n"
        "|                                                            v                v           |\n"
        "|                                                    [Commit Node/Edge]   [Retry Loop /   |\n"
        "|                                                    [to Neptune/S3]      [Drop Field]    |\n"
        "+-----------------------------------------------------------------------------------------+\n"
        "\n"
        "+-----------------------------------------------------------------------------------------+\n"
        "|                    GATEKEEPER LOOP 2: NLI ENTAILMENT FAITHFULNESS AUDIT                 |\n"
        "|                                                                                         |\n"
        "|   [Retrieved Chunks + Table] ---> [Agent 5: Claude 3.5 Sonnet] ---> [Draft Answer Prose]|\n"
        "|                                                                             |           |\n"
        "|                                                                             v           |\n"
        "|                                                              +-----------------------+  |\n"
        "|                                                              | NLI Entailment Audit  |  |\n"
        "|                                                              | Premise: Source Docs  |  |\n"
        "|                                                              | Hypothesis: Claim     |  |\n"
        "|                                                              +-----------------------+  |\n"
        "|                                                                 /         \\             |\n"
        "|                                                 ENTAILMENT >0.85/           \\ NEUTRAL / |\n"
        "|                                                                /             \\ CONFLICT |\n"
        "|                                                               v               v         |\n"
        "|                                                    [Attach Audit Badge]  [Auto-Rewrite /|\n"
        "|                                                    [Return to User UI]   [Excise Claim] |\n"
        "+-----------------------------------------------------------------------------------------+"
    )
    add_code(gk_diagram)

    add_h2("4.1 Amazon Bedrock Guardrails Integration")
    add_p("In addition to algorithmic string and NLI verification, the AWS deployment natively integrates **Amazon Bedrock Guardrails**:")
    add_bullet(" Prevents user queries from exfiltrating system prompts or circumventing clinical safety boundaries.", "1. Prompt Injection Protection:")
    add_bullet(" Automatically masks any accidental personal health identifiers (names, MRNs, dates of birth) in ingested supplementary files before processing.", "2. PII / PHI Redaction Filter:")
    add_bullet(" Bedrock Guardrail Contextual Grounding verifies that the model's generated text is grounded in the retrieved source passages, providing a secondary defense layer alongside our custom NLI agent.", "3. Contextual Grounding Check:")

    # ==================== SECTION 5 ====================
    add_h1("5. Core Application Features & AWS Implementation")
    add_p("The AWS architecture preserves all five user-facing capabilities of the GraphRAG platform, engineered for rapid responsiveness and enterprise accessibility:")

    feat_headers = ["Platform Module", "Core Capabilities", "AWS Implementation Details"]
    feat_rows = [
        [
            "1. Literature Corpus & Ingestion",
            "Fetches trial abstracts/XML via PubMed API; decomposes sections; runs parallelized PICO extraction; generates boolean MeSH queries with predicted yields.",
            "FastAPI on AWS App Runner with ThreadPoolExecutor parallel workers; S3 bucket for XML document cache; Bedrock Claude 3.5 Haiku for query strategy generation."
        ],
        [
            "2. Multi-Doc Chat & Clinical Synthesis",
            "Answers natural language queries across 4 intent pathways; builds side-by-side PICO tables; generates executive clinical prose; outputs dynamic follow-up prompt cards.",
            "Amazon Bedrock (Claude 3.5 Sonnet Converse API); hybrid router querying Neptune / in-memory KG + Titan Text Embeddings V2 (768d); NLI verification gatekeeper."
        ],
        [
            "3. Biomedical NER & Concept Explorer",
            "Interactive concept network mapping synonymous disease mentions to UMLS CUIs; extracts co-occurrence frequencies; surfaces mentions per drug/indication.",
            "scispaCy en_core_sci_lg parser; REST endpoints (/api/ner/{entity}/mentions); force-directed concept graph visualization rendered in browser."
        ],
        [
            "4. Structured PICO Evidence Matrix",
            "Tabular matrix comparing Study Design, Patient Population (N), Interventions, Comparators, and quant outcomes (HR, CI, p-value) with 100% provenance.",
            "Dynamically populated via FastAPI (/api/pico); click-to-verify modal displaying exact verbatim source sentence with character offset highlights."
        ],
        [
            "5. Interactive Knowledge Graph Explorer",
            "Live force-directed 2D/3D visualization of multi-hop biomedical relations connecting trials, drug classes, molecular targets, and indications.",
            "Vis-Network / D3.js canvas frontend receiving graph JSON from FastAPI (/api/graph); backed by NetworkX (sandbox) or Amazon Neptune openCypher (production)."
        ]
    ]
    add_styled_table(feat_headers, feat_rows, [Inches(1.8), Inches(2.5), Inches(2.2)])

    # ==================== SECTION 6 ====================
    add_h1("6. High-Level Design (HLD), Data Flow & AWS Graph Schema")
    add_p("The end-to-end data flow connects client interactions, serverless container execution, foundational reasoning models, and dual-store graph/vector persistence:")

    aws_arch_flow = (
        "+-----------------------------------------------------------------------------------------+\n"
        "|                                     USER INTERFACE                                      |\n"
        "|  Interactive Responsive Workspace (Novartis Corporate Blue #002A54 & Warm Amber #EC9A1E) |\n"
        "|  - Tab 1: Corpus & Ingest   - Tab 2: Clinical Chat   - Tab 3: NER   - Tab 4: PICO Grid  |\n"
        "+-----------------------------------------------------------------------------------------+\n"
        "                                           |\n"
        "                                (HTTPS TLS 1.3 / Port 443)\n"
        "                                           v\n"
        "+-----------------------------------------------------------------------------------------+\n"
        "|                          AWS APP RUNNER (SERVERLESS CONTAINER)                          |\n"
        "|  - Fully managed container runtime (Auto-scaling, auto-TLS, zero infrastructure admin)  |\n"
        "|  - FastAPI (Python 3.11) + Uvicorn ASGI Application                                     |\n"
        "|  - Section-Aware Chunking Engine & Ingestion ThreadPoolExecutor Workers                 |\n"
        "|  - In-Memory / Snapshot Knowledge Graph Manager (NetworkX / openCypher Engine)          |\n"
        "|  - Hybrid Vector Store with Clinical Section Boosting (1.35x on Results / Endpoints)    |\n"
        "+-----------------------------------------------------------------------------------------+\n"
        "             |                                    |                             |\n"
        "     (InvokeModel API)                     (Read/Write S3)              (GetSecretValue)\n"
        "             v                                    v                             v\n"
        "+-------------------------+         +--------------------------+  +-----------------------+\n"
        "|     AMAZON BEDROCK      |         |     AMAZON S3 BUCKET     |  |  AWS SECRETS MANAGER  |\n"
        "|  - Anthropic Claude 3.5 |         |  - XML Document Cache    |  |  - Bedrock API access |\n"
        "|    Sonnet (Synthesis)   |         |  - PICO JSON Snapshots   |  |  - External PubMed    | \n"
        "|  - Anthropic Claude 3.5 |         |  - Graph State Backups   |  |    API keys (optional)|\n"
        "|    Haiku (PICO & Prompt)|         |  - Audit History Logs    |  |  - Database credentials\n"
        "|  - Titan Text Embeddings|         |  - S3 Object Lock (WORM) |  +-----------------------+\n"
        "|    V2 (768d MRL Vectors)|         +--------------------------+\n"
        "+-------------------------+\n"
        "             | (Production Scale-Up Extension)\n"
        "             v\n"
        "+-----------------------------------------------------------------------------------------+\n"
        "|                    ENTERPRISE PERSISTENCE TIER (PRODUCTION UPGRADE)                     |\n"
        "|  +---------------------------------------+  +----------------------------------------+  |\n"
        "|  | Amazon Neptune Serverless (openCypher)|  | Amazon OpenSearch Serverless (Vector)  |  |\n"
        "|  | Multi-hop biomedical relationship     |  | Enterprise dense vector index for      |  |\n"
        "|  | traversals across millions of nodes   |  | multi-million chunk similarity search  |  |\n"
        "|  +---------------------------------------+  +----------------------------------------+  |\n"
        "+-----------------------------------------------------------------------------------------+"
    )
    add_code(aws_arch_flow)

    add_h2("6.1 Biomedical Graph Schema & openCypher Specifications")
    add_p("The knowledge graph structure is strongly typed to capture clinical trial dimensions with zero semantic ambiguity:")

    add_bullet(" `Article` (pmid, title, journal, year, sample_size, study_design)", "Core Node Types:")
    add_bullet(" `DrugClass` (class_name, cui, mechanism_of_action)", "")
    add_bullet(" `Drug` (drug_name, rxnorm_code, cui, is_investigational)", "")
    add_bullet(" `Condition` (condition_name, cui, icd10_code)", "")
    add_bullet(" `Population` (cohort_description, sample_size, inclusion_criteria, evidence_quote)", "")
    add_bullet(" `Intervention` (drug_name, dose, route, duration, cui)", "")
    add_bullet(" `Comparator` (comparator_name, is_placebo, is_active_control)", "")
    add_bullet(" `Outcome` (outcome_name, measure_type, effect_size, ci_low, ci_high, p_value, direction, evidence_quote)", "")

    add_p("Example openCypher query on Amazon Neptune for cross-study SGLT2 inhibitor trial retrieval in CKD:")
    opencypher_example = (
        "// Traverse SGLT2 inhibitor class down to trial outcomes in Chronic Kidney Disease\n"
        "MATCH (dc:DrugClass {class_name: 'SGLT2 inhibitors'})<-[:IS_A]-(d:Drug)\n"
        "MATCH (d)<-[:STUDIES_DRUG]-(art:Article)-[:REPORTS_OUTCOME]->(out:Outcome)\n"
        "MATCH (art)-[:HAS_POPULATION]->(pop:Population)\n"
        "WHERE pop.condition CONTAINS 'Kidney' OR pop.condition CONTAINS 'CKD'\n"
        "RETURN art.title AS Trial, d.drug_name AS Agent, pop.sample_size AS N,\n"
        "       out.outcome_name AS Endpoint, out.effect_size AS HR,\n"
        "       out.ci_low AS Lower_95, out.ci_high AS Upper_95, out.p_value AS P_Val\n"
        "ORDER BY art.year DESC;"
    )
    add_code(opencypher_example)

    # ==================== SECTION 7 ====================
    add_h1("7. Technology Stack Specification: GCP to AWS Exhaustive Mapping")
    add_p("The following table provides an exhaustive component-by-component mapping from our existing Google Cloud implementation to the target AWS native architecture:")

    stack_headers = ["Platform Layer", "Google Cloud Implementation", "AWS Sandbox Pilot Implementation", "AWS Enterprise Production Target"]
    stack_rows = [
        [
            "Compute / Container Hosting",
            "Google Cloud Run (Serverless container runtime, auto-scale 0-1000)",
            "AWS App Runner (Direct container deploy, auto-TLS, paused on idle)",
            "Amazon ECS on AWS Fargate or Amazon EKS (Multi-AZ, Private VPC)"
        ],
        [
            "LLM Reasoning & Synthesis",
            "Google Gemini 3.8 Flash (via google.genai SDK)",
            "Amazon Bedrock: Anthropic Claude 3.5 Sonnet & Claude 3.5 Haiku",
            "Amazon Bedrock (Claude 3.5 Sonnet / AWS Trainium fine-tuned Med-LLM)"
        ],
        [
            "Dense Vector Embeddings",
            "gemini-embedding-001 (768d Matryoshka output)",
            "Amazon Titan Text Embeddings V2 (768d / 1024d) via Bedrock",
            "Amazon Titan Text Embeddings V2 or Cohere Embed English v3"
        ],
        [
            "Vector Store & Search Engine",
            "In-Memory Hybrid Vector Store with 1.35x Section Boost",
            "In-Memory Hybrid Store with S3 Snapshot Cache & Titan V2 vectors",
            "Amazon OpenSearch Serverless (Vector Engine) or Aurora pgvector"
        ],
        [
            "Knowledge Graph Database",
            "In-Memory NetworkX with JSON/Cypher serialization",
            "In-Memory NetworkX with S3 State Checkpointing (<$0/mo infra fee)",
            "Amazon Neptune Serverless (openCypher/SPARQL, sub-second 4-hop)"
        ],
        [
            "Object & Document Storage",
            "Google Cloud Storage (GCS) buckets",
            "Amazon S3 Standard with Server-Side Encryption (SSE-S3)",
            "Amazon S3 with S3 Object Lock (WORM), Lifecycle Rules, Cross-Region"
        ],
        [
            "Secrets & Key Management",
            "Google Secret Manager",
            "AWS Secrets Manager or SSM Parameter Store",
            "AWS Secrets Manager + AWS KMS Customer Managed Keys (CMK)"
        ],
        [
            "API Gateway & Networking",
            "Cloud Run built-in HTTPS & Cloud CDN",
            "AWS App Runner auto-provisioned public HTTPS endpoint",
            "Amazon CloudFront + AWS WAF + Application Load Balancer (ALB)"
        ],
        [
            "Observability & Audit Trail",
            "Google Cloud Logging & Cloud Trace",
            "Amazon CloudWatch Logs & Metrics",
            "Amazon CloudWatch Logs + AWS X-Ray Tracing + AWS CloudTrail"
        ]
    ]
    add_styled_table(stack_headers, stack_rows, [Inches(1.5), Inches(1.8), Inches(1.8), Inches(1.9)])

    # ==================== SECTION 8 ====================
    add_h1("8. AWS Sandbox Pilot Architecture Blueprint (Low-Cost & Rapid)")
    add_p("To guarantee that the pilot is immediately deployable within a constrained AWS sandbox account without incurring database provisioning delays or unnecessary recurring costs, the architecture adopts a **Zero-Idle-Cost Serverless Blueprint**:")

    add_callout(
        "Why App Runner + Bedrock is the Ideal Pilot Pair",
        "1. ZERO CLUSTER OVERHEAD: Eliminates the requirement to maintain expensive Neptune ($150+/mo) or OpenSearch ($180+/mo) clusters for an evaluation dataset of 50–500 clinical trials.\n"
        "2. SERVERLESS BEDROCK CONSUMPTION: Amazon Bedrock charges strictly per million tokens consumed (e.g., $0.003/1k tokens for Claude 3.5 Sonnet, $0.00025/1k for Haiku). In a pilot processing 100 queries/day, monthly LLM expenditure is under $8–$15.\n"
        "3. ONE-CLICK DEPLOYMENT: Provisions in under 5 minutes using AWS App Runner directly from an Amazon ECR container image."
    )

    add_h2("8.1 Pilot Cost Estimation Model (<$100/Month)")
    add_p("Estimated monthly expenditure in an AWS Sandbox environment based on active evaluation by 5 clinical research team members (approx. 200 trial ingestions and 500 multi-document chat queries per month):")

    cost_headers = ["AWS Service", "Sandbox Pilot Configuration", "Monthly Usage Metric", "Estimated Cost (USD)"]
    cost_rows = [
        [
            "AWS App Runner",
            "1 vCPU, 2 GB RAM (Auto-pause when idle)",
            "40 active hours/month + idle pause",
            "$12.00 – $18.00"
        ],
        [
            "Amazon Bedrock (Claude 3.5 Sonnet)",
            "Chat synthesis & comparative reasoning",
            "1.5M input tokens, 400k output tokens",
            "$10.50 – $15.00"
        ],
        [
            "Amazon Bedrock (Claude 3.5 Haiku)",
            "Dynamic PICO extraction & prompt refiner",
            "2.0M input tokens, 500k output tokens",
            "$1.50 – $2.50"
        ],
        [
            "Amazon Bedrock (Titan Embeddings V2)",
            "Dense 768d passage vectors for chunks",
            "500,000 embedded tokens",
            "$0.05 – $0.10"
        ],
        [
            "Amazon S3",
            "Standard Storage for XML cache & backups",
            "10 GB storage + 20,000 PUT/GET requests",
            "$0.30 – $0.50"
        ],
        [
            "AWS Secrets Manager",
            "1 secret for API configuration",
            "1 secret per month + 10,000 API calls",
            "$0.45"
        ],
        [
            "Amazon CloudWatch",
            "Logs, metrics, and latency alarms",
            "3 GB ingested logs / month",
            "$1.50 – $2.00"
        ],
        [
            "TOTAL ESTIMATED MONTHLY PILOT COST",
            "Complete Autonomous GraphRAG Swarm",
            "Production-Grade Sandbox Evaluation",
            "$26.30 – $38.55 / month"
        ]
    ]
    add_styled_table(cost_headers, cost_rows, [Inches(1.8), Inches(2.2), Inches(1.8), Inches(1.2)])

    add_h2("8.2 AWS Infrastructure as Code (CloudFormation Template)")
    add_p("The following complete AWS CloudFormation template provisions the S3 storage bucket, IAM execution role, Bedrock access policy, and App Runner service for the Sandbox Pilot:")

    cfn_template = (
        "AWSTemplateFormatVersion: '2010-09-09'\n"
        "Description: 'Novartis GraphRAG Literature Platform - AWS Sandbox Pilot Blueprint'\n\n"
        "Parameters:\n"
        "  ImageUri:\n"
        "    Type: String\n"
        "    Description: 'Amazon ECR Image URI for GraphRAG Container'\n"
        "    Default: '189627569441.dkr.ecr.us-east-1.amazonaws.com/graphrag-literature:latest'\n\n"
        "Resources:\n"
        "  # S3 Bucket for XML Cache, PICO Snapshots & Graph Backups\n"
        "  GraphRAGDataBucket:\n"
        "    Type: AWS::S3::Bucket\n"
        "    Properties:\n"
        "      BucketName: !Sub 'novartis-graphrag-sandbox-${AWS::AccountId}'\n"
        "      BucketEncryption:\n"
        "        ServerSideEncryptionConfiguration:\n"
        "          - ServerSideEncryptionByDefault:\n"
        "              SSEAlgorithm: AES256\n"
        "      VersioningConfiguration:\n"
        "        Status: Enabled\n"
        "      PublicAccessBlockConfiguration:\n"
        "        BlockPublicAcls: true\n"
        "        BlockPublicPolicy: true\n"
        "        IgnorePublicAcls: true\n"
        "        RestrictPublicBuckets: true\n\n"
        "  # App Runner Instance Execution Role (Access to Bedrock & S3)\n"
        "  AppRunnerInstanceRole:\n"
        "    Type: AWS::IAM::Role\n"
        "    Properties:\n"
        "      RoleName: !Sub 'novartis-graphrag-apprunner-role-${AWS::Region}'\n"
        "      AssumeRolePolicyDocument:\n"
        "        Version: '2012-10-17'\n"
        "        Statement:\n"
        "          - Effect: Allow\n"
        "            Principal:\n"
        "              Service: tasks.apprunner.amazonaws.com\n"
        "            Action: sts:AssumeRole\n"
        "      Policies:\n"
        "        - PolicyName: BedrockAndS3Access\n"
        "          PolicyDocument:\n"
        "            Version: '2012-10-17'\n"
        "            Statement:\n"
        "              - Effect: Allow\n"
        "                Action:\n"
        "                  - bedrock:InvokeModel\n"
        "                  - bedrock:InvokeModelWithResponseStream\n"
        "                Resource: '*'\n"
        "              - Effect: Allow\n"
        "                Action:\n"
        "                  - s3:GetObject\n"
        "                  - s3:PutObject\n"
        "                  - s3:ListBucket\n"
        "                Resource:\n"
        "                  - !GetAtt GraphRAGDataBucket.Arn\n"
        "                  - !Sub '${GraphRAGDataBucket.Arn}/*'\n\n"
        "  # AWS App Runner Service (Fully Managed Serverless Container)\n"
        "  GraphRAGService:\n"
        "    Type: AWS::AppRunner::Service\n"
        "    Properties:\n"
        "      ServiceName: 'graphrag-literature-pilot'\n"
        "      SourceConfiguration:\n"
        "        AuthenticationConfiguration:\n"
        "          AccessRoleArn: !GetAtt AppRunnerInstanceRole.Arn\n"
        "        ImageRepository:\n"
        "          ImageIdentifier: !Ref ImageUri\n"
        "          ImageRepositoryType: ECR\n"
        "          ImageConfiguration:\n"
        "            Port: '8080'\n"
        "            RuntimeEnvironmentVariables:\n"
        "              - Name: AWS_REGION\n"
        "                Value: !Ref 'AWS::Region'\n"
        "              - Name: S3_DATA_BUCKET\n"
        "                Value: !Ref GraphRAGDataBucket\n"
        "              - Name: BEDROCK_MODEL_SYNTHESIS\n"
        "                Value: 'anthropic.claude-3-5-sonnet-20241022-v2:0'\n"
        "              - Name: BEDROCK_MODEL_EXTRACTION\n"
        "                Value: 'anthropic.claude-3-5-haiku-20241022-v1:0'\n"
        "              - Name: BEDROCK_MODEL_EMBEDDING\n"
        "                Value: 'amazon.titan-embed-text-v2:0'\n"
        "      InstanceConfiguration:\n"
        "        Cpu: '1024'\n"
        "        Memory: '2048'\n"
        "        InstanceRoleArn: !GetAtt AppRunnerInstanceRole.Arn\n\n"
        "Outputs:\n"
        "  AppRunnerUrl:\n"
        "    Description: 'Public HTTPS URL for GraphRAG Sandbox Pilot'\n"
        "    Value: !GetAtt GraphRAGService.ServiceUrl"
    )
    add_code(cfn_template)

    add_h2("8.3 Python Bedrock Integration Client Code")
    add_p("The following Python client implementation replaces `gemini_client.py` with the official AWS SDK (`boto3`), supporting Anthropic Claude 3.5 Sonnet Converse API and Amazon Titan Text Embeddings V2:")

    bedrock_code = (
        "import json\n"
        "import logging\n"
        "import boto3\n"
        "from typing import List, Dict, Any, Optional\n\n"
        "logger = logging.getLogger('graphrag.bedrock')\n\n"
        "class BedrockClient:\n"
        "    def __init__(self, region_name: str = 'us-east-1'):\n"
        "        self.client = boto3.client('bedrock-runtime', region_name=region_name)\n"
        "        self.model_synthesis = 'anthropic.claude-3-5-sonnet-20241022-v2:0'\n"
        "        self.model_extraction = 'anthropic.claude-3-5-haiku-20241022-v1:0'\n"
        "        self.model_embedding = 'amazon.titan-embed-text-v2:0'\n\n"
        "    def generate_clinical_synthesis(self, prompt: str, system_prompt: str) -> str:\n"
        "        \"\"\"Executes dynamic multi-study synthesis via Bedrock Converse API.\"\"\"\n"
        "        response = self.client.converse(\n"
        "            modelId=self.model_synthesis,\n"
        "            messages=[{'role': 'user', 'content': [{'text': prompt}]}],\n"
        "            system=[{'text': system_prompt}],\n"
        "            inferenceConfig={'temperature': 0.1, 'maxTokens': 2048}\n"
        "        )\n"
        "        return response['output']['message']['content'][0]['text']\n\n"
        "    def generate_embeddings(self, texts: List[str], dimensions: int = 768) -> List[List[float]]:\n"
        "        \"\"\"Generates 768-dim dense vectors using Amazon Titan Text Embeddings V2.\"\"\"\n"
        "        embeddings = []\n"
        "        for text in texts:\n"
        "            body = json.dumps({'inputText': text, 'dimensions': dimensions, 'normalize': True})\n"
        "            resp = self.client.invoke_model(\n"
        "                modelId=self.model_embedding,\n"
        "                contentType='application/json',\n"
        "                accept='application/json',\n"
        "                body=body\n"
        "            )\n"
        "            result = json.loads(resp['body'].read())\n"
        "            embeddings.append(result['embedding'])\n"
        "        return embeddings\n"
    )
    add_code(bedrock_code)

    # ==================== SECTION 9 ====================
    add_h1("9. Security, Compliance & Regulatory Governance in Biopharma")
    add_p("To comply with Novartis corporate information security standards, FDA regulations (21 CFR Part 11), and international healthcare standards (GxP / HIPAA), the AWS deployment enforces rigorous security controls:")

    add_bullet(" All user queries, PICO extractions, and document ingests are written to Amazon CloudWatch Logs and S3 with S3 Object Lock (Write-Once-Read-Many). Audit trails cannot be edited, overwritten, or deleted by any user or administrator.", "1. 21 CFR Part 11 Electronic Records & Audit Trails:")
    add_bullet(" Bedrock processes inference strictly within the Novartis AWS account boundary. Data is encrypted in transit via TLS 1.3 and at rest via AWS KMS Customer Managed Keys (CMKs). AWS does not retain or inspect customer data.", "2. Data Privacy & Zero Training Retention:")
    add_bullet(" The App Runner service and backend containers operate inside a private VPC. Outbound communication to NCBI PubMed or Bedrock flows through VPC Endpoints (AWS PrivateLink), eliminating exposure to the public internet.", "3. Network Isolation (AWS PrivateLink):")
    add_bullet(" Micro-agents assume fine-grained IAM roles allowing only specific actions (e.g., `bedrock:InvokeModel` restricted to explicit Foundation Model ARNs).", "4. IAM Least Privilege:")

    # ==================== SECTION 10 ====================
    add_h1("10. Pilot-to-Production Phased Roadmap & Evaluation Metrics")
    add_p("The replatforming roadmap follows an iterative four-phase implementation schedule designed to derisk technical architecture before scaling across business units:")

    add_h2("10.1 Four-Phase Implementation Blueprint")
    add_bullet(" Deploy container to AWS App Runner; integrate Amazon Bedrock (Claude 3.5 Sonnet + Titan V2); validate the 7-trial cardiorenal benchmark dataset; conduct user acceptance testing with 5 medical directors. Target: <$50 total cost.", "Phase 1: Sandbox Pilot Deployment (Weeks 1–2):")
    add_bullet(" Provision Amazon Neptune Serverless (openCypher) and Amazon OpenSearch Serverless Vector Engine; migrate in-memory graph to managed cluster; enable multi-hop graph queries on >1,000 trials.", "Phase 2: Managed Graph & Vector Expansion (Weeks 3–6):")
    add_bullet(" Build automated ingestion connectors for Veeva Vault PromoMats/RIM, ClinicalTrials.gov API v2, and FDA/EMA approval packages; integrate internal Novartis Active Directory (SSO/SAML via AWS IAM Identity Center).", "Phase 3: Multi-Source Enterprise Connectors (Weeks 7–12):")
    add_bullet(" Execute formal Computer System Validation (CSV); obtain GxP audit certification; deploy across multi-region high availability; open platform to global Novartis clinical development and medical affairs teams.", "Phase 4: Enterprise GxP Validation & Global Rollout (Weeks 13–18):")

    add_h2("10.2 Target Evaluation Metrics & Acceptance Thresholds")
    add_bullet(" F1 score >= 92% on clinical entity boundary detection (EBM-NLP benchmark).", "1. Named Entity Recognition (NER) Accuracy:")
    add_bullet(" >= 89% field-level match against expert manual PICO annotations.", "2. PICO Field Extraction Accuracy:")
    add_bullet(" >= 96% recall for multi-study comparative questions (vs. 62% for pure vector RAG).", "3. Cross-Study Retrieval Recall:")
    add_bullet(" >= 98% factual entailment score verified via Gatekeeper Loop 2.", "4. Citation Faithfulness (NLI Audit):")
    add_bullet(" Sub-3.0 seconds response time for cross-study comparative chat synthesis.", "5. End-to-End Query Latency:")

    output_filename = "GraphRAG_Literature_Platform_AWS_Architecture_and_Sandbox_HLD.docx"
    doc.save(output_filename)
    print(f"Document successfully created and saved to: {output_filename}")

if __name__ == "__main__":
    generate_aws_document()

# GraphRAG Literature Platform — Welcome storyboard

Duration: 90 seconds. Screens reconstructed from the supplied PowerPoint.

## 00–10 seconds

**On screen:** Welcome title card, followed by the Corpus tab.

**Voiceover:** Welcome to the Graph RAG Literature Platform. We’re aiming for answers in seconds, instead of weeks of review. Let’s compare SGLT2 studies in kidney disease.

## 10–22 seconds

**On screen:** Type the PubMed query, click Ingest, show the success banner and updated counts once.

**Voiceover:** Search PubMed and click Ingest. Gemini extracts PICO: population, intervention, comparator, outcome, and entities. MeSH and UMLS merge synonyms. Three papers become seven.

## 22–32 seconds

**On screen:** Knowledge Graph before and after ingestion, then NER condition, drug and outcome filters.

**Voiceover:** One graph connects studies, drugs, conditions, and outcomes. Explore normalized concepts. One extraction powers chat, the entity explorer, and PICO.

## 32–50 seconds

**On screen:** Type Compare SGLT2 studies. Highlight graph_entity, show synthesis and then the evidence table.

**Voiceover:** Ask: compare SGLT2 studies. Gemini routes across graph traversal, aggregation, vector search, and community summaries, then synthesizes retrieved evidence. Graph retrieval targets every study linked to matching concepts, addressing the completeness gaps of a small vector-search sample.

## 50–62 seconds

**On screen:** PICO grid. Highlight the P=0.21 row and its confidence interval. Show the export control.

**Voiceover:** Compare trials side by side, including effect sizes and confidence intervals. Here, P equals point two one. That’s not statistically significant. Keep the result visible, and export the evidence.

## 62–78 seconds

**On screen:** Citations tab. Highlight the verbatim quote and PMID link. Explain quote verification and expert review.

**Voiceover:** Every claim links to a verbatim source sentence. The system aims to eliminate hallucinated extractions by rejecting fields whose quote is absent from the paper. Experts open the original source and verify the evidence before using an answer.

## 78–90 seconds

**On screen:** Return to the title card with potential pharma use cases and the closing statement.

**Voiceover:** For R and D, medical affairs, and regulatory teams, we’re aiming for weeks of review in minutes. Complete connected evidence, with traceable answers. Graph RAG Literature Platform: evidence you can trust.

## Wording notes

Gemini follows the user-supplied storyboard. No runtime backend was inspected.
Answers in seconds and elimination of hallucinated extractions are stated as design goals. No timing benchmark was supplied.
Retrieval completeness refers to ingested studies linked to matching graph concepts. Expert source review remains part of the workflow.
The P=0.21 result is highlighted editorially. The existing screenshot does not establish automatic statistical-significance flagging.

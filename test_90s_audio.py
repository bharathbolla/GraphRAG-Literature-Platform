import subprocess
import os
import json

# Narration segments for 90-second video
# Voice: en-US-ChristopherNeural or en-US-JennyNeural with rate=+12%
# Warm, human, natural presentation delivery
segments = [
    # 0-6s: Welcome & Introduction
    ('part1_intro', 
     'Welcome to the GraphRAG Literature Platform. This platform helps pharma teams find, connect, and compare research evidence with traceable sources.',
     '+10%'),
    
    # 6-17s: Ingestion & Extraction Layer
    ('part2_ingest',
     'We begin by ingesting clinical articles directly from PubMed. Our pipeline parses sections, extracts structured PICO fields, and normalizes every medical term to MeSH and UMLS concepts.',
     '+12%'),
     
    # 17-28s: The Growing Knowledge Graph & GraphRAG's advantage
    ('part2_graph',
     'As papers enter, they don’t sit in isolated vectors. They build a living knowledge graph of trials, drug classes, and outcomes, overcoming top-k retrieval blind spots.',
     '+12%'),

    # 28-39s: Multi-Doc Chat & Hybrid Routing
    ('part2_chat',
     'When asking cross-study questions, GraphRAG uses hybrid routing. It traverses drug hierarchies to compare trials like EMPA-KIDNEY and DAPA-CKD with verified citations.',
     '+12%'),

    # 39-49s: NER Explorer & Synonyms
    ('part2_ner',
     'In the NER Explorer, synonyms resolve to unified concept IDs, revealing co-occurrence patterns, study counts, and sentence provenance across the corpus.',
     '+12%'),

    # 49-60s: PICO Grid & Sentence Provenance
    ('part2_pico',
     'The PICO Grid extracts population, intervention, comparator, and outcome fields into a structured matrix, linking every hazard ratio to its source sentence for systematic review.',
     '+12%'),

    # 60-85s: Pharma Use Cases
    # R&D + Clinical Dev
    ('part3_rd_clin',
     'Across pharma, in R&D, scientists explore disease pathways. In Clinical Development, teams benchmark trial designs and compare effect sizes against standard of care.',
     '+12%'),

    # Medical Affairs + Market Access
    ('part3_med_market',
     'Medical Affairs teams deliver citation-backed answers to KOL inquiries in minutes, while Market Access teams instantly assemble comparative efficacy dossiers for reimbursement.',
     '+12%'),

    # Safety + Regulatory
    ('part3_safe_reg',
     'Safety specialists uncover adverse event signals across co-occurrence networks, and Regulatory teams prepare audit-ready briefing packages with sentence-level provenance.',
     '+12%'),

    # 85-90s: Closing Benefit
    ('part4_closing',
     'A shared evidence base with findings linked directly to source passages. Empowering smarter, faster biomedical decisions.',
     '+10%')
]

os.makedirs('audio_90s', exist_ok=True)
total_dur = 0.0

print("Generating neural human voiceover segments...")
for name, text, rate in segments:
    out_mp3 = f'audio_90s/{name}.mp3'
    out_wav = f'audio_90s/{name}.wav'
    
    cmd = [
        'uv', 'run', '--with', 'edge-tts',
        'edge-tts',
        '--voice', 'en-US-ChristopherNeural',
        '--rate', rate,
        '--text', text,
        '--write-media', out_mp3
    ]
    subprocess.run(cmd, check=True)
    
    # Convert to WAV for exact sample rate and duration measurement
    subprocess.run(['ffmpeg', '-y', '-i', out_mp3, '-ar', '44100', '-ac', '2', out_wav], 
                   stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL, check=True)
    
    res = subprocess.run(['ffmpeg', '-i', out_wav], stderr=subprocess.PIPE, text=True)
    for line in res.stderr.splitlines():
        if 'Duration:' in line:
            part = line.split('Duration:')[1].split(',')[0].strip()
            h, m, s = part.split(':')
            dur = float(h)*3600 + float(m)*60 + float(s)
            print(f'{name} ({rate}): {part} ({dur:.2f}s)')
            total_dur += dur

print(f'\nTotal raw spoken duration: {total_dur:.2f}s (leaves ~10s of natural breath/scene transition pauses across 90s!)')

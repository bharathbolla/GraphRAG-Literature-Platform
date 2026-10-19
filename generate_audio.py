import subprocess
import os

scripts = [
    ('scene1', 'Welcome to the GraphRAG Literature Platform. In the Corpus store, querying PubMed retrieves clinical trials, automatically generating section-aware chunks and extracting verified PICO fields.'),
    ('scene2', 'In Multi-Document Chat, asking cross-study questions triggers hybrid routing. The platform traverses drug class hierarchies to synthesize findings across trials with sentence-level citations.'),
    ('scene3', 'The NER Explorer unifies biomedical terms into MeSH and UMLS concept IDs, mapping cross-document co-occurrence networks and verified sentence provenance.'),
    ('scene4', 'The PICO Grid structures trial evidence across populations, interventions, and outcomes. Every hazard ratio and confidence interval links directly to its source sentence for systematic review.'),
    ('scene5', 'Finally, the Interactive Knowledge Graph visualizes trials, drug classes, and patient populations, growing dynamically as new literature is indexed to ensure grounded, multi-document synthesis.')
]

os.makedirs('audio_scenes', exist_ok=True)

total_dur = 0.0

for name, text in scripts:
    ps_script = f'''
Add-Type -AssemblyName System.Speech
$synth = New-Object System.Speech.Synthesis.SpeechSynthesizer
$synth.SelectVoice("Microsoft Zira Desktop")
$synth.Rate = 1
$synth.SetOutputToWaveFile("audio_scenes/{name}.wav")
$synth.Speak("{text}")
$synth.Dispose()
'''
    with open('tmp_synth.ps1', 'w', encoding='utf-8') as f:
        f.write(ps_script)
    
    subprocess.run(['powershell', '-ExecutionPolicy', 'Bypass', '-File', 'tmp_synth.ps1'], check=True)
    
    # Check duration with ffprobe/ffmpeg
    res = subprocess.run(
        ['ffmpeg', '-i', f'audio_scenes/{name}.wav'],
        stderr=subprocess.PIPE, text=True
    )
    for line in res.stderr.splitlines():
        if 'Duration:' in line:
            # Duration: 00:00:15.23,
            part = line.split('Duration:')[1].split(',')[0].strip()
            h, m, s = part.split(':')
            dur = float(h)*3600 + float(m)*60 + float(s)
            print(f'{name}: {part} ({dur:.2f}s)')
            total_dur += dur

if os.path.exists('tmp_synth.ps1'):
    os.remove('tmp_synth.ps1')

print(f'\nTotal audio duration: {total_dur:.2f} seconds')

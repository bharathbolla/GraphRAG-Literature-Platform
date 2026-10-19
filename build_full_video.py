import os
import sys
import subprocess
import numpy as np
from PIL import Image, ImageDraw, ImageFont

print("Initializing video generation pipeline...")

# Paths
FONTS_DIR = os.environ.get('WINDIR', 'C:\\Windows') + '\\Fonts\\'
FONT_BOLD = ImageFont.truetype(FONTS_DIR + 'segoeuib.ttf', 14)
FONT_REG = ImageFont.truetype(FONTS_DIR + 'segoeui.ttf', 13)
FONT_CAP_TAG = ImageFont.truetype(FONTS_DIR + 'segoeuib.ttf', 13)
FONT_CAP_TEXT = ImageFont.truetype(FONTS_DIR + 'segoeui.ttf', 15)

# Scripts and timings
SCENES = [
    {
        'id': 'scene1',
        'title': 'STEP 1: INGESTION & GRAPH BUILD',
        'caption': 'Query PubMed to ingest clinical articles with verified PICO extraction & MeSH normalization.',
        'audio_file': 'audio_scenes/scene1.wav',
        'start_sec': 0.0,
        'audio_delay_ms': 500,
        'duration_sec': 12.0,
        'url': 'https://graphrag.novartis.internal/corpus'
    },
    {
        'id': 'scene2',
        'title': 'STEP 2: MULTI-DOC CHAT & SYNTHESIS',
        'caption': 'Hybrid query routing traverses drug classes to synthesize findings across trials with citations.',
        'audio_file': 'audio_scenes/scene2.wav',
        'start_sec': 12.0,
        'audio_delay_ms': 12300,
        'duration_sec': 12.0,
        'url': 'https://graphrag.novartis.internal/chat-synthesis'
    },
    {
        'id': 'scene3',
        'title': 'STEP 3: BIOMEDICAL NER EXPLORER',
        'caption': 'Entities unified into MeSH & UMLS concept IDs with co-occurrence networks and sentence provenance.',
        'audio_file': 'audio_scenes/scene3.wav',
        'start_sec': 24.0,
        'audio_delay_ms': 24300,
        'duration_sec': 11.0,
        'url': 'https://graphrag.novartis.internal/ner-explorer'
    },
    {
        'id': 'scene4',
        'title': 'STEP 4: PICO EVIDENCE EXTRACTION GRID',
        'caption': 'Structured PICO matrix linking hazard ratios and confidence intervals to verified quotes for systematic review.',
        'audio_file': 'audio_scenes/scene4.wav',
        'start_sec': 35.0,
        'audio_delay_ms': 35300,
        'duration_sec': 12.0,
        'url': 'https://graphrag.novartis.internal/pico-grid'
    },
    {
        'id': 'scene5',
        'title': 'STEP 5: INTERACTIVE KNOWLEDGE GRAPH',
        'caption': 'Visualizes interconnected trials, drug classes, and populations, dynamically growing as literature expands.',
        'audio_file': 'audio_scenes/scene5.wav',
        'start_sec': 47.0,
        'audio_delay_ms': 47300,
        'duration_sec': 13.0,
        'url': 'https://graphrag.novartis.internal/knowledge-graph'
    }
]

TOTAL_DURATION = 60.0
FPS = 30
TOTAL_FRAMES = int(TOTAL_DURATION * FPS)

# Step A: Build master audio track
print("Building master audio track...")
filter_complex = (
    '[0:a]adelay=500|500[a0];'
    '[1:a]adelay=12300|12300[a1];'
    '[2:a]adelay=24300|24300[a2];'
    '[3:a]adelay=35300|35300[a3];'
    '[4:a]adelay=47300|47300[a4];'
    '[a0][a1][a2][a3][a4]amix=inputs=5:duration=longest:dropout_transition=0,volume=1.8,loudnorm=I=-16:TP=-1.5:LRA=11[aout]'
)

cmd_audio = [
    'ffmpeg', '-y',
    '-i', 'audio_scenes/scene1.wav',
    '-i', 'audio_scenes/scene2.wav',
    '-i', 'audio_scenes/scene3.wav',
    '-i', 'audio_scenes/scene4.wav',
    '-i', 'audio_scenes/scene5.wav',
    '-filter_complex', filter_complex,
    '-map', '[aout]',
    '-t', '60.0',
    '-ar', '44100',
    '-ac', '2',
    'master_audio.wav'
]
subprocess.run(cmd_audio, check=True)
print("Master audio created successfully!")

# Step B: Pre-render and cache base frames for slides
print("Pre-rendering base slide frames...")

WIN_X, WIN_Y, WIN_W, WIN_H = 40, 20, 1840, 975
CHROME_H = 42
BODY_W = WIN_W
BODY_H = WIN_H - CHROME_H

def render_base_slide(slide_path, url_text):
    # Base 1920x1080 canvas
    canvas = Image.new('RGB', (1920, 1080), color=(11, 15, 25))
    
    # Window
    window = Image.new('RGB', (WIN_W, WIN_H), color=(15, 23, 42))
    w_draw = ImageDraw.Draw(window)
    
    # Title bar
    w_draw.rectangle([0, 0, WIN_W, CHROME_H], fill=(24, 33, 47))
    # Traffic lights
    w_draw.ellipse([20, 15, 32, 27], fill=(255, 95, 86))
    w_draw.ellipse([40, 15, 52, 27], fill=(255, 189, 46))
    w_draw.ellipse([60, 15, 72, 27], fill=(39, 201, 63))
    
    # Tab
    w_draw.rounded_rectangle([90, 8, 290, 42], radius=6, fill=(15, 23, 42))
    w_draw.text((105, 16), 'GraphRAG Platform v0.1.0', fill=(226, 232, 240), font=FONT_BOLD)
    
    # URL address bar
    addr_x1, addr_y1, addr_x2, addr_y2 = 330, 8, 1450, 34
    w_draw.rounded_rectangle([addr_x1, addr_y1, addr_x2, addr_y2], radius=6, fill=(15, 23, 42), outline=(51, 65, 85))
    
    # Padlock icon
    pad_x, pad_y = addr_x1 + 14, addr_y1 + 9
    w_draw.rectangle([pad_x, pad_y + 4, pad_x + 9, pad_y + 11], fill=(148, 163, 184))
    w_draw.arc([pad_x + 2, pad_y, pad_x + 7, pad_y + 7], 180, 0, fill=(148, 163, 184), width=1)
    w_draw.text((addr_x1 + 32, addr_y1 + 5), url_text, fill=(203, 213, 225), font=FONT_REG)
    
    # Slide image inside body
    s_img = Image.open(slide_path).convert('RGB')
    scale = min(BODY_W / s_img.size[0], BODY_H / s_img.size[1])
    new_w, new_h = int(s_img.size[0] * scale), int(s_img.size[1] * scale)
    s_scaled = s_img.resize((new_w, new_h), Image.Resampling.LANCZOS)
    
    off_x = (BODY_W - new_w) // 2
    off_y = CHROME_H + (BODY_H - new_h) // 2
    window.paste(s_scaled, (off_x, off_y))
    
    canvas.paste(window, (WIN_X, WIN_Y))
    return canvas, (WIN_X + off_x, WIN_Y + off_y, scale)

# Cache pre-rendered slides
slide_cache = {}
slide_meta = {}

slides_to_load = [
    ('slide_01.png', 'https://graphrag.novartis.internal/corpus'),
    ('slide_02.png', 'https://graphrag.novartis.internal/corpus'),
    ('slide_03.png', 'https://graphrag.novartis.internal/corpus'),
    ('slide_04.png', 'https://graphrag.novartis.internal/chat-synthesis'),
    ('slide_05.png', 'https://graphrag.novartis.internal/chat-synthesis'),
    ('slide_06.png', 'https://graphrag.novartis.internal/ner-explorer'),
    ('slide_07.png', 'https://graphrag.novartis.internal/pico-grid'),
    ('slide_08.png', 'https://graphrag.novartis.internal/knowledge-graph'),
    ('slide_09.png', 'https://graphrag.novartis.internal/knowledge-graph'),
    ('slide_10.png', 'https://graphrag.novartis.internal/ner-explorer'),
    ('slide_11.png', 'https://graphrag.novartis.internal/ner-explorer'),
    ('slide_12.png', 'https://graphrag.novartis.internal/ner-explorer'),
    ('slide_14.png', 'https://graphrag.novartis.internal/chat-synthesis')
]

for s_file, url in slides_to_load:
    path = os.path.join('slides_extracted', s_file)
    c, m = render_base_slide(path, url)
    slide_cache[s_file] = c
    slide_meta[s_file] = m

print(f"Cached {len(slide_cache)} base slides.")

# Create high-res cursor
cursor_img = Image.new('RGBA', (48, 48), (0, 0, 0, 0))
c_draw = ImageDraw.Draw(cursor_img)
poly = [(0, 0), (0, 24), (6, 19), (12, 30), (16, 28), (10, 17), (18, 17)]
shadow_poly = [(x+2, y+2) for x, y in poly]
c_draw.polygon(shadow_poly, fill=(0, 0, 0, 110))
for dx in [-1, 0, 1]:
    for dy in [-1, 0, 1]:
        c_draw.polygon([(x+dx, y+dy) for x, y in poly], fill=(20, 20, 20, 255))
c_draw.polygon(poly, fill=(255, 255, 255, 255))

# Coordinate translation helper
def to_screen_coords(slide_name, sx, sy):
    ox, oy, scale = slide_meta[slide_name]
    return int(ox + sx * scale), int(oy + sy * scale)

# Smooth easing
def ease_in_out(t):
    return t * t * (3.0 - 2.0 * t)

print("Starting video frame generation and FFmpeg streaming...")

# Start ffmpeg subprocess to receive raw frames
cmd_video = [
    'ffmpeg', '-y',
    '-f', 'rawvideo',
    '-vcodec', 'rawvideo',
    '-s', '1920x1080',
    '-pix_fmt', 'bgr24',
    '-r', str(FPS),
    '-i', '-',
    '-i', 'master_audio.wav',
    '-c:v', 'libx264',
    '-pix_fmt', 'yuv420p',
    '-preset', 'fast',
    '-crf', '18',
    '-c:a', 'aac',
    '-b:a', '192k',
    '-shortest',
    'graphrag_presentation_demo.mp4'
]

ffmpeg_proc = subprocess.Popen(cmd_video, stdin=subprocess.PIPE)

# Animation schedule definition
# Define cursor waypoints and slide displays for all 1800 frames
for frame_idx in range(TOTAL_FRAMES):
    sec = frame_idx / FPS
    
    # Determine current scene and captions
    if frame_idx < 360: # Scene 1 (0-12s)
        scene = SCENES[0]
        # Slide progression:
        # 0-90: slide_01
        # 90-180: slide_02
        # 180-360: slide_03
        if frame_idx < 90:
            current_slide = 'slide_01.png'
            # Cursor enters from (1400, 700) to search box (500, 467)
            t = np.clip(frame_idx / 70.0, 0.0, 1.0)
            e = ease_in_out(t)
            p_start = (1400, 700)
            p_end = to_screen_coords('slide_01.png', 450, 467)
            cur_x = int(p_start[0] + (p_end[0] - p_start[0]) * e)
            cur_y = int(p_start[1] + (p_end[1] - p_start[1]) * e)
            clicking = (70 <= frame_idx <= 85)
            click_pt = p_end
            click_progress = (frame_idx - 70) / 15.0 if clicking else 0.0
        elif frame_idx < 180:
            current_slide = 'slide_02.png'
            # Cursor moves from search box (450, 467) to Ingest button (1312, 467)
            t = np.clip((frame_idx - 90) / 60.0, 0.0, 1.0)
            e = ease_in_out(t)
            p_start = to_screen_coords('slide_02.png', 450, 467)
            p_end = to_screen_coords('slide_02.png', 1312, 467)
            cur_x = int(p_start[0] + (p_end[0] - p_start[0]) * e)
            cur_y = int(p_start[1] + (p_end[1] - p_start[1]) * e)
            clicking = (150 <= frame_idx <= 170)
            click_pt = p_end
            click_progress = (frame_idx - 150) / 20.0 if clicking else 0.0
        else:
            current_slide = 'slide_03.png'
            # Ingested! Cursor hovers over success stats, then moves towards Chat tab (603, 42)
            if frame_idx < 270:
                cur_x, cur_y = to_screen_coords('slide_03.png', 800, 310)
                clicking = False
            else:
                t = np.clip((frame_idx - 270) / 80.0, 0.0, 1.0)
                e = ease_in_out(t)
                p_start = to_screen_coords('slide_03.png', 800, 310)
                p_end = to_screen_coords('slide_03.png', 603, 42)
                cur_x = int(p_start[0] + (p_end[0] - p_start[0]) * e)
                cur_y = int(p_start[1] + (p_end[1] - p_start[1]) * e)
                clicking = (frame_idx >= 345)
                click_pt = p_end
                click_progress = (frame_idx - 345) / 15.0 if clicking else 0.0
                
    elif frame_idx < 720: # Scene 2 (12-24s): Chat & Synthesis
        scene = SCENES[1]
        # 360-440: slide_04
        # 440-580: slide_05
        # 580-720: slide_14
        if frame_idx < 440:
            current_slide = 'slide_04.png'
            # Cursor moves from Chat tab (603, 42) to chat query input (500, 350)
            t = np.clip((frame_idx - 360) / 60.0, 0.0, 1.0)
            e = ease_in_out(t)
            p_start = to_screen_coords('slide_04.png', 603, 42)
            p_end = to_screen_coords('slide_04.png', 940, 350) # Query button
            cur_x = int(p_start[0] + (p_end[0] - p_start[0]) * e)
            cur_y = int(p_start[1] + (p_end[1] - p_start[1]) * e)
            clicking = (frame_idx >= 420)
            click_pt = p_end
            click_progress = (frame_idx - 420) / 20.0 if clicking else 0.0
        elif frame_idx < 580:
            current_slide = 'slide_05.png'
            # Generated answer displayed. Cursor hovers, then glides to 'Evidence Table' tab (830, 467)
            if frame_idx < 500:
                cur_x, cur_y = to_screen_coords('slide_05.png', 500, 600)
                clicking = False
            else:
                t = np.clip((frame_idx - 500) / 65.0, 0.0, 1.0)
                e = ease_in_out(t)
                p_start = to_screen_coords('slide_05.png', 500, 600)
                p_end = to_screen_coords('slide_05.png', 830, 467) # Evidence table tab
                cur_x = int(p_start[0] + (p_end[0] - p_start[0]) * e)
                cur_y = int(p_start[1] + (p_end[1] - p_start[1]) * e)
                clicking = (frame_idx >= 565)
                click_pt = p_end
                click_progress = (frame_idx - 565) / 15.0 if clicking else 0.0
        else:
            current_slide = 'slide_14.png'
            # In Evidence Table! Cursor inspects row, then glides up to 'NER Explorer' tab (761, 42)
            if frame_idx < 640:
                cur_x, cur_y = to_screen_coords('slide_14.png', 700, 670)
                clicking = False
            else:
                t = np.clip((frame_idx - 640) / 70.0, 0.0, 1.0)
                e = ease_in_out(t)
                p_start = to_screen_coords('slide_14.png', 700, 670)
                p_end = to_screen_coords('slide_14.png', 761, 42) # NER Explorer tab
                cur_x = int(p_start[0] + (p_end[0] - p_start[0]) * e)
                cur_y = int(p_start[1] + (p_end[1] - p_start[1]) * e)
                clicking = (frame_idx >= 705)
                click_pt = p_end
                click_progress = (frame_idx - 705) / 15.0 if clicking else 0.0
                
    elif frame_idx < 1050: # Scene 3 (24-35s): Biomedical NER Explorer
        scene = SCENES[2]
        # 720-790: slide_06 (All concepts)
        # 790-870: slide_10 (Condition)
        # 870-950: slide_11 (Drug)
        # 950-1050: slide_12 (Outcome)
        if frame_idx < 790:
            current_slide = 'slide_06.png'
            # Cursor moves to 'Condition' filter pill (95, 298)
            t = np.clip((frame_idx - 720) / 55.0, 0.0, 1.0)
            e = ease_in_out(t)
            p_start = to_screen_coords('slide_06.png', 761, 42)
            p_end = to_screen_coords('slide_06.png', 95, 298)
            cur_x = int(p_start[0] + (p_end[0] - p_start[0]) * e)
            cur_y = int(p_start[1] + (p_end[1] - p_start[1]) * e)
            clicking = (frame_idx >= 775)
            click_pt = p_end
            click_progress = (frame_idx - 775) / 15.0 if clicking else 0.0
        elif frame_idx < 870:
            current_slide = 'slide_10.png'
            # Cursor moves to 'Drug' filter pill (135, 298)
            t = np.clip((frame_idx - 790) / 60.0, 0.0, 1.0)
            e = ease_in_out(t)
            p_start = to_screen_coords('slide_10.png', 95, 298)
            p_end = to_screen_coords('slide_10.png', 135, 298)
            cur_x = int(p_start[0] + (p_end[0] - p_start[0]) * e)
            cur_y = int(p_start[1] + (p_end[1] - p_start[1]) * e)
            clicking = (frame_idx >= 850)
            click_pt = p_end
            click_progress = (frame_idx - 850) / 20.0 if clicking else 0.0
        elif frame_idx < 950:
            current_slide = 'slide_11.png'
            # Cursor moves to 'Outcome' filter pill (185, 298)
            t = np.clip((frame_idx - 870) / 60.0, 0.0, 1.0)
            e = ease_in_out(t)
            p_start = to_screen_coords('slide_11.png', 135, 298)
            p_end = to_screen_coords('slide_11.png', 185, 298)
            cur_x = int(p_start[0] + (p_end[0] - p_start[0]) * e)
            cur_y = int(p_start[1] + (p_end[1] - p_start[1]) * e)
            clicking = (frame_idx >= 930)
            click_pt = p_end
            click_progress = (frame_idx - 930) / 20.0 if clicking else 0.0
        else:
            current_slide = 'slide_12.png'
            # Outcome view. Cursor hovers over co-occurrences, then moves to 'PICO Grid' tab (861, 42)
            if frame_idx < 990:
                cur_x, cur_y = to_screen_coords('slide_12.png', 600, 550)
                clicking = False
            else:
                t = np.clip((frame_idx - 990) / 50.0, 0.0, 1.0)
                e = ease_in_out(t)
                p_start = to_screen_coords('slide_12.png', 600, 550)
                p_end = to_screen_coords('slide_12.png', 861, 42) # PICO tab
                cur_x = int(p_start[0] + (p_end[0] - p_start[0]) * e)
                cur_y = int(p_start[1] + (p_end[1] - p_start[1]) * e)
                clicking = (frame_idx >= 1035)
                click_pt = p_end
                click_progress = (frame_idx - 1035) / 15.0 if clicking else 0.0
                
    elif frame_idx < 1410: # Scene 4 (35-47s): PICO Evidence Grid
        scene = SCENES[3]
        current_slide = 'slide_07.png'
        # Cursor hovers on EMPA-KIDNEY 'View Quote' (1240, 485), then over to CSV export (1260, 205), then to Knowledge Graph tab (1007, 42)
        if frame_idx < 1170:
            t = np.clip((frame_idx - 1050) / 80.0, 0.0, 1.0)
            e = ease_in_out(t)
            p_start = to_screen_coords('slide_07.png', 861, 42)
            p_end = to_screen_coords('slide_07.png', 1240, 485) # View quote button
            cur_x = int(p_start[0] + (p_end[0] - p_start[0]) * e)
            cur_y = int(p_start[1] + (p_end[1] - p_start[1]) * e)
            clicking = (frame_idx >= 1150)
            click_pt = p_end
            click_progress = (frame_idx - 1150) / 20.0 if clicking else 0.0
        elif frame_idx < 1290:
            t = np.clip((frame_idx - 1170) / 80.0, 0.0, 1.0)
            e = ease_in_out(t)
            p_start = to_screen_coords('slide_07.png', 1240, 485)
            p_end = to_screen_coords('slide_07.png', 1240, 205) # Export CSV
            cur_x = int(p_start[0] + (p_end[0] - p_start[0]) * e)
            cur_y = int(p_start[1] + (p_end[1] - p_start[1]) * e)
            clicking = (frame_idx >= 1270)
            click_pt = p_end
            click_progress = (frame_idx - 1270) / 20.0 if clicking else 0.0
        else:
            t = np.clip((frame_idx - 1290) / 100.0, 0.0, 1.0)
            e = ease_in_out(t)
            p_start = to_screen_coords('slide_07.png', 1240, 205)
            p_end = to_screen_coords('slide_07.png', 1007, 42) # Knowledge Graph tab
            cur_x = int(p_start[0] + (p_end[0] - p_start[0]) * e)
            cur_y = int(p_start[1] + (p_end[1] - p_start[1]) * e)
            clicking = (frame_idx >= 1390)
            click_pt = p_end
            click_progress = (frame_idx - 1390) / 20.0 if clicking else 0.0
            
    else: # Scene 5 (47-60s): Interactive Knowledge Graph
        scene = SCENES[4]
        # 1410-1570: slide_08 (21 nodes)
        # 1570-1800: slide_09 (39 nodes, expanded)
        if frame_idx < 1570:
            current_slide = 'slide_08.png'
            # Cursor inspects central SGLT2 inhibitors cluster
            t = np.clip((frame_idx - 1410) / 80.0, 0.0, 1.0)
            e = ease_in_out(t)
            p_start = to_screen_coords('slide_08.png', 1007, 42)
            p_end = to_screen_coords('slide_08.png', 680, 520) # Central cluster
            cur_x = int(p_start[0] + (p_end[0] - p_start[0]) * e)
            cur_y = int(p_start[1] + (p_end[1] - p_start[1]) * e)
            clicking = False
        else:
            current_slide = 'slide_09.png'
            # Expanded graph!
            t = np.clip((frame_idx - 1570) / 100.0, 0.0, 1.0)
            e = ease_in_out(t)
            p_start = to_screen_coords('slide_09.png', 680, 520)
            p_end = to_screen_coords('slide_09.png', 550, 480)
            cur_x = int(p_start[0] + (p_end[0] - p_start[0]) * e)
            cur_y = int(p_start[1] + (p_end[1] - p_start[1]) * e)
            clicking = False
            
    # Now compose the frame
    base_frame = slide_cache[current_slide].copy()
    
    # Draw ripple if clicking
    if clicking:
        ripple_radius = int(8 + 24 * click_progress)
        alpha = int(220 * (1.0 - click_progress))
        overlay = Image.new('RGBA', (1920, 1080), (0, 0, 0, 0))
        o_draw = ImageDraw.Draw(overlay)
        rx, ry = click_pt
        o_draw.ellipse([rx - ripple_radius, ry - ripple_radius, rx + ripple_radius, ry + ripple_radius], outline=(56, 189, 248, alpha), width=3)
        o_draw.ellipse([rx - ripple_radius//2, ry - ripple_radius//2, rx + ripple_radius//2, ry + ripple_radius//2], fill=(56, 189, 248, alpha//2))
        base_frame = Image.alpha_composite(base_frame.convert('RGBA'), overlay).convert('RGB')
        
    # Paste cursor
    base_frame.paste(cursor_img, (cur_x, cur_y), cursor_img)
    
    # Draw bottom caption bar
    cap_w = 1580
    cap_h = 56
    cap_x = (1920 - cap_w) // 2
    cap_y = 1010

    c_overlay = Image.new('RGBA', (1920, 1080), (0, 0, 0, 0))
    c_draw = ImageDraw.Draw(c_overlay)
    c_draw.rounded_rectangle([cap_x, cap_y, cap_x + cap_w, cap_y + cap_h], radius=14, fill=(15, 23, 42, 245), outline=(51, 65, 85, 255), width=1)
    
    tag_w = int(FONT_CAP_TAG.getlength(scene['title'])) + 22
    c_draw.rounded_rectangle([cap_x + 10, cap_y + 10, cap_x + 10 + tag_w, cap_y + cap_h - 10], radius=8, fill=(37, 99, 235, 255))
    c_draw.text((cap_x + 21, cap_y + 18), scene['title'], fill=(255, 255, 255), font=FONT_CAP_TAG)
    c_draw.text((cap_x + 10 + tag_w + 16, cap_y + 17), scene['caption'], fill=(241, 245, 249), font=FONT_CAP_TEXT)
    
    # Smooth fade out at the very end (last 1 second: 1770-1800)
    if frame_idx >= 1770:
        fade = (frame_idx - 1770) / 30.0
        c_draw.rectangle([0, 0, 1920, 1080], fill=(11, 15, 25, int(255 * fade)))

    final_frame = Image.alpha_composite(base_frame.convert('RGBA'), c_overlay).convert('RGB')
    
    # Convert PIL Image to BGR raw bytes for FFmpeg
    arr_rgb = np.array(final_frame)
    arr_bgr = arr_rgb[:, :, ::-1] # RGB to BGR
    ffmpeg_proc.stdin.write(arr_bgr.tobytes())
    
    if frame_idx % 150 == 0:
        print(f"Rendered frame {frame_idx}/{TOTAL_FRAMES} ({frame_idx/FPS:.1f}s)")

ffmpeg_proc.stdin.close()
ffmpeg_proc.wait()
print(f"Video encoding complete! Exit code: {ffmpeg_proc.returncode}")

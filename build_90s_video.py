import os
import sys
import subprocess
import numpy as np
from PIL import Image, ImageDraw, ImageFont

print("Initializing 90-second video pipeline...")

# Fonts
FONTS_DIR = os.environ.get('WINDIR', 'C:\\Windows') + '\\Fonts\\'
FONT_BOLD = ImageFont.truetype(FONTS_DIR + 'segoeuib.ttf', 14)
FONT_REG = ImageFont.truetype(FONTS_DIR + 'segoeui.ttf', 13)
FONT_CAP_TAG = ImageFont.truetype(FONTS_DIR + 'segoeuib.ttf', 13)
FONT_CAP_TEXT = ImageFont.truetype(FONTS_DIR + 'segoeui.ttf', 15)

FONT_CARD_TAG = ImageFont.truetype(FONTS_DIR + 'segoeuib.ttf', 12)
FONT_CARD_TITLE = ImageFont.truetype(FONTS_DIR + 'segoeuib.ttf', 17)
FONT_CARD_LABEL = ImageFont.truetype(FONTS_DIR + 'segoeuib.ttf', 13)
FONT_CARD_BODY = ImageFont.truetype(FONTS_DIR + 'segoeui.ttf', 13)

FPS = 30
TOTAL_DURATION = 90.0
TOTAL_FRAMES = int(TOTAL_DURATION * FPS) # 2700 frames

# Pre-render base frames
WIN_X, WIN_Y, WIN_W, WIN_H = 40, 20, 1840, 975
CHROME_H = 42
BODY_W = WIN_W
BODY_H = WIN_H - CHROME_H

def render_base_slide(slide_path, url_text):
    canvas = Image.new('RGB', (1920, 1080), color=(11, 15, 25))
    window = Image.new('RGB', (WIN_W, WIN_H), color=(15, 23, 42))
    w_draw = ImageDraw.Draw(window)
    
    # Chrome bar
    w_draw.rectangle([0, 0, WIN_W, CHROME_H], fill=(24, 33, 47))
    # Traffic lights
    w_draw.ellipse([20, 15, 32, 27], fill=(255, 95, 86))
    w_draw.ellipse([40, 15, 52, 27], fill=(255, 189, 46))
    w_draw.ellipse([60, 15, 72, 27], fill=(39, 201, 63))
    
    # Tab
    w_draw.rounded_rectangle([90, 8, 290, 42], radius=6, fill=(15, 23, 42))
    w_draw.text((105, 16), 'GraphRAG Platform v0.1.0', fill=(226, 232, 240), font=FONT_BOLD)
    
    # URL bar
    addr_x1, addr_y1, addr_x2, addr_y2 = 330, 8, 1450, 34
    w_draw.rounded_rectangle([addr_x1, addr_y1, addr_x2, addr_y2], radius=6, fill=(15, 23, 42), outline=(51, 65, 85))
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
    p = os.path.join('slides_extracted', s_file)
    c, m = render_base_slide(p, url)
    slide_cache[s_file] = c
    slide_meta[s_file] = m

print(f"Cached {len(slide_cache)} base slides.")

# Create cursor
cursor_img = Image.new('RGBA', (48, 48), (0, 0, 0, 0))
c_draw = ImageDraw.Draw(cursor_img)
poly = [(0, 0), (0, 24), (6, 19), (12, 30), (16, 28), (10, 17), (18, 17)]
shadow_poly = [(x+2, y+2) for x, y in poly]
c_draw.polygon(shadow_poly, fill=(0, 0, 0, 110))
for dx in [-1, 0, 1]:
    for dy in [-1, 0, 1]:
        c_draw.polygon([(x+dx, y+dy) for x, y in poly], fill=(20, 20, 20, 255))
c_draw.polygon(poly, fill=(255, 255, 255, 255))

def to_screen_coords(slide_name, sx, sy):
    ox, oy, scale = slide_meta[slide_name]
    return int(ox + sx * scale), int(oy + sy * scale)

def ease_in_out(t):
    return t * t * (3.0 - 2.0 * t)

# Pre-render Use Case Spotlight Cards
def draw_usecase_card(card_tag, title, label1, body1, label2, body2, is_closing=False):
    card_img = Image.new('RGBA', (1920, 1080), (0, 0, 0, 0))
    draw = ImageDraw.Draw(card_img)
    
    if is_closing:
        # Centered prominent closing banner
        card_w, card_h = 920, 190
        card_x, card_y = (1920 - card_w) // 2, 380
        draw.rounded_rectangle([card_x, card_y, card_x + card_w, card_y + card_h], radius=18, fill=(11, 15, 25, 248), outline=(56, 189, 248, 240), width=2)
        
        draw.rounded_rectangle([card_x + 24, card_y + 18, card_x + 250, card_y + 44], radius=6, fill=(2, 132, 199, 255))
        draw.text((card_x + 36, card_y + 23), card_tag, fill=(255, 255, 255), font=FONT_CARD_TAG)
        
        font_closing_h = ImageFont.truetype(FONTS_DIR + 'segoeuib.ttf', 20)
        draw.text((card_x + 265, card_y + 20), title, fill=(255, 255, 255), font=font_closing_h)
        
        draw.text((card_x + 24, card_y + 70), label1, fill=(56, 189, 248), font=FONT_CARD_LABEL)
        draw.text((card_x + 195, card_y + 68), body1, fill=(226, 232, 240), font=FONT_CAP_TEXT)
        
        draw.text((card_x + 24, card_y + 120), label2, fill=(74, 222, 128), font=FONT_CARD_LABEL)
        draw.text((card_x + 195, card_y + 118), body2, fill=(226, 232, 240), font=FONT_CAP_TEXT)
    else:
        # Sleek top-right card that keeps the central tool screen visible
        card_w, card_h = 800, 168
        card_x, card_y = 1040, 95
        draw.rounded_rectangle([card_x, card_y, card_x + card_w, card_y + card_h], radius=16, fill=(11, 15, 25, 245), outline=(56, 189, 248, 220), width=2)
        
        draw.rounded_rectangle([card_x + 16, card_y + 14, card_x + 230, card_y + 38], radius=6, fill=(2, 132, 199, 255))
        draw.text((card_x + 24, card_y + 18), card_tag, fill=(255, 255, 255), font=FONT_CARD_TAG)
        draw.text((card_x + 245, card_y + 16), title, fill=(255, 255, 255), font=FONT_CARD_TITLE)
        
        draw.text((card_x + 20, card_y + 62), label1, fill=(56, 189, 248), font=FONT_CARD_LABEL)
        draw.text((card_x + 175, card_y + 60), body1, fill=(226, 232, 240), font=FONT_CARD_BODY)
        
        draw.text((card_x + 20, card_y + 108), label2, fill=(74, 222, 128), font=FONT_CARD_LABEL)
        draw.text((card_x + 175, card_y + 106), body2, fill=(226, 232, 240), font=FONT_CARD_BODY)
        
    return card_img

card_rd_clin = draw_usecase_card(
    'PHARMA USE CASE',
    'R&D Discovery & Clinical Development',
    '[R&D Discovery]',
    'Rapid target validation & disease mechanism exploration across papers',
    '[Clinical Dev]',
    'Benchmark trial designs, eligibility criteria & comparative effect sizes'
)

card_med_market = draw_usecase_card(
    'PHARMA USE CASE',
    'Medical Affairs & Market Access / HEOR',
    '[Medical Affairs]',
    'Rapid citation-backed answers to field KOL inquiries in minutes',
    '[Market Access]',
    'Instant comparative efficacy tables for reimbursement dossiers'
)

card_safe_reg = draw_usecase_card(
    'PHARMA USE CASE',
    'Safety / PV & Regulatory Review',
    '[Safety & PV]',
    'Detect rare adverse event signals & drug interactions across co-occurrences',
    '[Regulatory]',
    'Prepare audit-ready briefing packages with sentence provenance'
)

card_closing = draw_usecase_card(
    'THE GRAPHRAG ADVANTAGE',
    'A Shared, Traceable Evidence Base',
    '[Traceable Evidence]',
    'Every single finding linked directly to its verified source passage',
    '[Unified Insights]',
    'Cross-functional alignment from early discovery to post-market regulatory review',
    is_closing=True
)

# Start ffmpeg pipe
print("Starting FFmpeg 90-second rendering pipeline...")
cmd_video = [
    'ffmpeg', '-y',
    '-f', 'rawvideo',
    '-vcodec', 'rawvideo',
    '-s', '1920x1080',
    '-pix_fmt', 'bgr24',
    '-r', str(FPS),
    '-i', '-',
    '-i', 'master_audio_90s.wav',
    '-c:v', 'libx264',
    '-pix_fmt', 'yuv420p',
    '-preset', 'fast',
    '-crf', '18',
    '-c:a', 'aac',
    '-b:a', '192k',
    '-shortest',
    'graphrag_presentation_90s_demo.mp4'
]

ffmpeg_proc = subprocess.Popen(cmd_video, stdin=subprocess.PIPE)

for frame_idx in range(TOTAL_FRAMES):
    sec = frame_idx / FPS
    spotlight_card = None
    
    # 1. 0.0s - 6.7s (Frames 0 - 200): Welcome & Intro
    if frame_idx < 200:
        current_slide = 'slide_01.png'
        tag_title = 'WELCOME & PLATFORM OVERVIEW'
        caption_text = 'This platform helps pharma teams find, connect, and compare research evidence with traceable sources.'
        # Cursor enters and settles near search bar
        t = np.clip(frame_idx / 150.0, 0.0, 1.0)
        e = ease_in_out(t)
        p_start = (1400, 700)
        p_end = to_screen_coords('slide_01.png', 450, 467)
        cur_x = int(p_start[0] + (p_end[0] - p_start[0]) * e)
        cur_y = int(p_start[1] + (p_end[1] - p_start[1]) * e)
        clicking = False
        
    # 2. 6.7s - 18.0s (Frames 200 - 540): Ingestion & Extraction Layer
    elif frame_idx < 540:
        tag_title = '1. INGESTION & EXTRACTION LAYER'
        caption_text = 'Query PubMed to parse sections, extract PICO elements, and normalize terms to MeSH and UMLS.'
        if frame_idx < 260:
            current_slide = 'slide_01.png'
            cur_x, cur_y = to_screen_coords('slide_01.png', 450, 467)
            clicking = (frame_idx >= 240)
            click_pt = (cur_x, cur_y)
            click_progress = (frame_idx - 240) / 20.0 if clicking else 0.0
        elif frame_idx < 380:
            current_slide = 'slide_02.png'
            t = np.clip((frame_idx - 260) / 80.0, 0.0, 1.0)
            e = ease_in_out(t)
            p_start = to_screen_coords('slide_02.png', 450, 467)
            p_end = to_screen_coords('slide_02.png', 1312, 467) # Ingest button
            cur_x = int(p_start[0] + (p_end[0] - p_start[0]) * e)
            cur_y = int(p_start[1] + (p_end[1] - p_start[1]) * e)
            clicking = (frame_idx >= 355)
            click_pt = p_end
            click_progress = (frame_idx - 355) / 25.0 if clicking else 0.0
        else:
            current_slide = 'slide_03.png'
            # Slide shows 4 new papers, 7 articles, 88 edges! Cursor moves to Knowledge Graph tab (1007, 42)
            if frame_idx < 460:
                cur_x, cur_y = to_screen_coords('slide_03.png', 800, 310)
                clicking = False
            else:
                t = np.clip((frame_idx - 460) / 70.0, 0.0, 1.0)
                e = ease_in_out(t)
                p_start = to_screen_coords('slide_03.png', 800, 310)
                p_end = to_screen_coords('slide_03.png', 1007, 42) # Knowledge Graph tab
                cur_x = int(p_start[0] + (p_end[0] - p_start[0]) * e)
                cur_y = int(p_start[1] + (p_end[1] - p_start[1]) * e)
                clicking = (frame_idx >= 520)
                click_pt = p_end
                click_progress = (frame_idx - 520) / 20.0 if clicking else 0.0
                
    # 3. 18.0s - 29.5s (Frames 540 - 885): Growing Knowledge Graph & GraphRAG advantage
    elif frame_idx < 885:
        tag_title = '2. DYNAMIC KNOWLEDGE GRAPH'
        caption_text = 'Overcomes top-k blind spots by building a living graph connecting trials, drug classes & outcomes.'
        if frame_idx < 720:
            current_slide = 'slide_08.png'
            # 21 nodes graph. Cursor hovers over SGLT2 central cluster
            t = np.clip((frame_idx - 540) / 70.0, 0.0, 1.0)
            e = ease_in_out(t)
            p_start = to_screen_coords('slide_08.png', 1007, 42)
            p_end = to_screen_coords('slide_08.png', 680, 520)
            cur_x = int(p_start[0] + (p_end[0] - p_start[0]) * e)
            cur_y = int(p_start[1] + (p_end[1] - p_start[1]) * e)
            clicking = False
        else:
            current_slide = 'slide_09.png'
            # Expands to 39 nodes and 56 relations! Cursor moves to Chat tab (603, 42)
            if frame_idx < 810:
                cur_x, cur_y = to_screen_coords('slide_09.png', 550, 480)
                clicking = False
            else:
                t = np.clip((frame_idx - 810) / 65.0, 0.0, 1.0)
                e = ease_in_out(t)
                p_start = to_screen_coords('slide_09.png', 550, 480)
                p_end = to_screen_coords('slide_09.png', 603, 42) # Chat tab
                cur_x = int(p_start[0] + (p_end[0] - p_start[0]) * e)
                cur_y = int(p_start[1] + (p_end[1] - p_start[1]) * e)
                clicking = (frame_idx >= 865)
                click_pt = p_end
                click_progress = (frame_idx - 865) / 20.0 if clicking else 0.0
                
    # 4. 29.5s - 41.2s (Frames 885 - 1235): Multi-Document Chat & Hybrid Routing
    elif frame_idx < 1235:
        tag_title = '3. HYBRID ROUTING & SYNTHESIS'
        caption_text = 'Traverses drug hierarchies to synthesize multi-trial outcomes with sentence-level citations.'
        if frame_idx < 960:
            current_slide = 'slide_04.png'
            t = np.clip((frame_idx - 885) / 60.0, 0.0, 1.0)
            e = ease_in_out(t)
            p_start = to_screen_coords('slide_04.png', 603, 42)
            p_end = to_screen_coords('slide_04.png', 940, 350)
            cur_x = int(p_start[0] + (p_end[0] - p_start[0]) * e)
            cur_y = int(p_start[1] + (p_end[1] - p_start[1]) * e)
            clicking = (frame_idx >= 940)
            click_pt = p_end
            click_progress = (frame_idx - 940) / 20.0 if clicking else 0.0
        elif frame_idx < 1100:
            current_slide = 'slide_05.png'
            if frame_idx < 1030:
                cur_x, cur_y = to_screen_coords('slide_05.png', 500, 600)
                clicking = False
            else:
                t = np.clip((frame_idx - 1030) / 60.0, 0.0, 1.0)
                e = ease_in_out(t)
                p_start = to_screen_coords('slide_05.png', 500, 600)
                p_end = to_screen_coords('slide_05.png', 830, 467) # Evidence Table tab
                cur_x = int(p_start[0] + (p_end[0] - p_start[0]) * e)
                cur_y = int(p_start[1] + (p_end[1] - p_start[1]) * e)
                clicking = (frame_idx >= 1080)
                click_pt = p_end
                click_progress = (frame_idx - 1080) / 20.0 if clicking else 0.0
        else:
            current_slide = 'slide_14.png'
            if frame_idx < 1160:
                cur_x, cur_y = to_screen_coords('slide_14.png', 700, 670)
                clicking = False
            else:
                t = np.clip((frame_idx - 1160) / 65.0, 0.0, 1.0)
                e = ease_in_out(t)
                p_start = to_screen_coords('slide_14.png', 700, 670)
                p_end = to_screen_coords('slide_14.png', 761, 42) # NER Explorer tab
                cur_x = int(p_start[0] + (p_end[0] - p_start[0]) * e)
                cur_y = int(p_start[1] + (p_end[1] - p_start[1]) * e)
                clicking = (frame_idx >= 1215)
                click_pt = p_end
                click_progress = (frame_idx - 1215) / 20.0 if clicking else 0.0
                
    # 5. 41.2s - 50.8s (Frames 1235 - 1525): Biomedical NER Explorer
    elif frame_idx < 1525:
        tag_title = '4. BIOMEDICAL NER EXPLORER'
        caption_text = 'Resolves synonyms to unified concept IDs, mapping co-occurrence patterns & paper frequencies.'
        if frame_idx < 1310:
            current_slide = 'slide_06.png'
            t = np.clip((frame_idx - 1235) / 60.0, 0.0, 1.0)
            e = ease_in_out(t)
            p_start = to_screen_coords('slide_06.png', 761, 42)
            p_end = to_screen_coords('slide_06.png', 95, 298) # Condition pill
            cur_x = int(p_start[0] + (p_end[0] - p_start[0]) * e)
            cur_y = int(p_start[1] + (p_end[1] - p_start[1]) * e)
            clicking = (frame_idx >= 1290)
            click_pt = p_end
            click_progress = (frame_idx - 1290) / 20.0 if clicking else 0.0
        elif frame_idx < 1380:
            current_slide = 'slide_10.png'
            t = np.clip((frame_idx - 1310) / 55.0, 0.0, 1.0)
            e = ease_in_out(t)
            p_start = to_screen_coords('slide_10.png', 95, 298)
            p_end = to_screen_coords('slide_10.png', 135, 298) # Drug pill
            cur_x = int(p_start[0] + (p_end[0] - p_start[0]) * e)
            cur_y = int(p_start[1] + (p_end[1] - p_start[1]) * e)
            clicking = (frame_idx >= 1360)
            click_pt = p_end
            click_progress = (frame_idx - 1360) / 20.0 if clicking else 0.0
        elif frame_idx < 1450:
            current_slide = 'slide_11.png'
            t = np.clip((frame_idx - 1380) / 55.0, 0.0, 1.0)
            e = ease_in_out(t)
            p_start = to_screen_coords('slide_11.png', 135, 298)
            p_end = to_screen_coords('slide_11.png', 185, 298) # Outcome pill
            cur_x = int(p_start[0] + (p_end[0] - p_start[0]) * e)
            cur_y = int(p_start[1] + (p_end[1] - p_start[1]) * e)
            clicking = (frame_idx >= 1430)
            click_pt = p_end
            click_progress = (frame_idx - 1430) / 20.0 if clicking else 0.0
        else:
            current_slide = 'slide_12.png'
            if frame_idx < 1485:
                cur_x, cur_y = to_screen_coords('slide_12.png', 600, 550)
                clicking = False
            else:
                t = np.clip((frame_idx - 1485) / 35.0, 0.0, 1.0)
                e = ease_in_out(t)
                p_start = to_screen_coords('slide_12.png', 600, 550)
                p_end = to_screen_coords('slide_12.png', 861, 42) # PICO tab
                cur_x = int(p_start[0] + (p_end[0] - p_start[0]) * e)
                cur_y = int(p_start[1] + (p_end[1] - p_start[1]) * e)
                clicking = (frame_idx >= 1510)
                click_pt = p_end
                click_progress = (frame_idx - 1510) / 15.0 if clicking else 0.0
                
    # 6. 50.8s - 60.5s (Frames 1525 - 1815): PICO Grid & Provenance
    elif frame_idx < 1815:
        current_slide = 'slide_07.png'
        tag_title = '5. PICO EVIDENCE EXTRACTION GRID'
        caption_text = 'Organizes trials into PICO parameters, linking every effect size & CI to its verified source quote.'
        if frame_idx < 1650:
            t = np.clip((frame_idx - 1525) / 80.0, 0.0, 1.0)
            e = ease_in_out(t)
            p_start = to_screen_coords('slide_07.png', 861, 42)
            p_end = to_screen_coords('slide_07.png', 1240, 485) # View quote
            cur_x = int(p_start[0] + (p_end[0] - p_start[0]) * e)
            cur_y = int(p_start[1] + (p_end[1] - p_start[1]) * e)
            clicking = (frame_idx >= 1630)
            click_pt = p_end
            click_progress = (frame_idx - 1630) / 20.0 if clicking else 0.0
        elif frame_idx < 1740:
            t = np.clip((frame_idx - 1650) / 70.0, 0.0, 1.0)
            e = ease_in_out(t)
            p_start = to_screen_coords('slide_07.png', 1240, 485)
            p_end = to_screen_coords('slide_07.png', 1240, 205) # Export CSV
            cur_x = int(p_start[0] + (p_end[0] - p_start[0]) * e)
            cur_y = int(p_start[1] + (p_end[1] - p_start[1]) * e)
            clicking = (frame_idx >= 1720)
            click_pt = p_end
            click_progress = (frame_idx - 1720) / 20.0 if clicking else 0.0
        else:
            t = np.clip((frame_idx - 1740) / 60.0, 0.0, 1.0)
            e = ease_in_out(t)
            p_start = to_screen_coords('slide_07.png', 1240, 205)
            p_end = to_screen_coords('slide_07.png', 1007, 42) # Back to Knowledge Graph for use cases!
            cur_x = int(p_start[0] + (p_end[0] - p_start[0]) * e)
            cur_y = int(p_start[1] + (p_end[1] - p_start[1]) * e)
            clicking = (frame_idx >= 1795)
            click_pt = p_end
            click_progress = (frame_idx - 1795) / 20.0 if clicking else 0.0
            
    # 7. 60.5s - 70.2s (Frames 1815 - 2105): Use Case 1 - R&D & Clinical Development
    elif frame_idx < 2105:
        current_slide = 'slide_09.png' # Knowledge Graph visible
        spotlight_card = card_rd_clin
        tag_title = 'USE CASE: R&D & CLINICAL DEVELOPMENT'
        caption_text = 'Explore disease mechanisms in R&D; benchmark trial designs and effect sizes in Clinical Dev.'
        cur_x, cur_y = to_screen_coords('slide_09.png', 600, 520)
        clicking = False
        
    # 8. 70.2s - 77.5s (Frames 2105 - 2325): Use Case 2 - Medical Affairs & Market Access
    elif frame_idx < 2325:
        current_slide = 'slide_14.png' # Evidence Table visible
        spotlight_card = card_med_market
        tag_title = 'USE CASE: MEDICAL AFFAIRS & MARKET ACCESS'
        caption_text = 'Rapid citation-backed KOL answers for Medical Affairs; comparative efficacy for Market Access.'
        cur_x, cur_y = to_screen_coords('slide_14.png', 650, 600)
        clicking = False
        
    # 9. 77.5s - 84.5s (Frames 2325 - 2535): Use Case 3 - Safety & Regulatory Review
    elif frame_idx < 2535:
        current_slide = 'slide_12.png' # NER Co-occurrences & Sentences visible
        spotlight_card = card_safe_reg
        tag_title = 'USE CASE: SAFETY & REGULATORY REVIEW'
        caption_text = 'Detect adverse event signals for Safety; audit-ready submissions with quote provenance for Regulatory.'
        cur_x, cur_y = to_screen_coords('slide_12.png', 500, 550)
        clicking = False
        
    # 10. 84.5s - 90.0s (Frames 2535 - 2700): Closing Benefit & Call to Action
    else:
        current_slide = 'slide_09.png'
        spotlight_card = card_closing
        tag_title = 'THE GRAPHRAG ADVANTAGE'
        caption_text = 'A unified evidence base with findings linked to source passages for faster, safer decisions.'
        cur_x, cur_y = (1750, 950)
        clicking = False

    # Base frame from cache
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
        
    # Apply use case card overlay if active
    if spotlight_card is not None:
        base_frame = Image.alpha_composite(base_frame.convert('RGBA'), spotlight_card).convert('RGB')
        
    # Paste cursor (unless in final closing card)
    if frame_idx < 2535:
        base_frame.paste(cursor_img, (cur_x, cur_y), cursor_img)
        
    # Draw lower-third caption bar
    cap_w = 1580
    cap_h = 56
    cap_x = (1920 - cap_w) // 2
    cap_y = 1010

    c_overlay = Image.new('RGBA', (1920, 1080), (0, 0, 0, 0))
    c_draw = ImageDraw.Draw(c_overlay)
    c_draw.rounded_rectangle([cap_x, cap_y, cap_x + cap_w, cap_y + cap_h], radius=14, fill=(15, 23, 42, 245), outline=(51, 65, 85, 255), width=1)
    
    tag_w = int(FONT_CAP_TAG.getlength(tag_title)) + 24
    c_draw.rounded_rectangle([cap_x + 10, cap_y + 10, cap_x + 10 + tag_w, cap_y + cap_h - 10], radius=8, fill=(37, 99, 235, 255))
    c_draw.text((cap_x + 22, cap_y + 18), tag_title, fill=(255, 255, 255), font=FONT_CAP_TAG)
    c_draw.text((cap_x + 10 + tag_w + 16, cap_y + 17), caption_text, fill=(241, 245, 249), font=FONT_CAP_TEXT)
    
    # Smooth closing fade out (last 1.2s: 2664 - 2700)
    if frame_idx >= 2664:
        fade = (frame_idx - 2664) / 36.0
        c_draw.rectangle([0, 0, 1920, 1080], fill=(11, 15, 25, int(255 * fade)))

    final_frame = Image.alpha_composite(base_frame.convert('RGBA'), c_overlay).convert('RGB')
    
    arr_rgb = np.array(final_frame)
    arr_bgr = arr_rgb[:, :, ::-1]
    ffmpeg_proc.stdin.write(arr_bgr.tobytes())
    
    if frame_idx % 300 == 0:
        print(f"Rendered frame {frame_idx}/{TOTAL_FRAMES} ({frame_idx/FPS:.1f}s)")

ffmpeg_proc.stdin.close()
ffmpeg_proc.wait()
print(f"90-second video encoding complete! Exit code: {ffmpeg_proc.returncode}")

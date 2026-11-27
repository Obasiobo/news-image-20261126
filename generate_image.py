#!/usr/bin/env python3
"""Render the make.fun daily news-image entry for Thursday 26 November 2026.

A single-page newspaper front page, 1024x1024, drawn with Pillow.
Every story on the page happened on, or was first reported on,
Thursday 26 November 2026. Layout, in order from the top:

  * dateline + masthead + subtitle + double rule
  * a strip of six big-number stats
  * three hero stories, each with a small drawn graphic
  * "The day's top stories" — 11 medium stories in two columns
  * "More of the day — in brief" — 34 one-line briefs in three columns
  * a timeline of the day
  * a dotted world map with numbered pins + a date-check box

Run:  python3 generate_image.py   ->  writes entry.png next to this file.
"""

import math
from PIL import Image, ImageDraw, ImageFont

# ---------------------------------------------------------------- constants
W, H = 1024, 1024
MARGIN = 24
CONTENT_W = W - 2 * MARGIN

PAPER = (247, 241, 222)      # warm newsprint cream
INK = (26, 26, 26)           # near-black
RED = (179, 27, 27)          # headline red
GREY = (107, 101, 88)        # muted grey-brown
RULE = (60, 58, 50)          # rule lines
CARD_LINE = (150, 145, 130)  # hero card border
DOT = (120, 115, 100)        # map dots

FONT_DIR = "/usr/share/fonts/truetype/dejavu"

def font(name, size):
    return ImageFont.truetype(f"{FONT_DIR}/{name}", size)

F_SERIF_B = lambda s: font("DejaVuSerif-Bold.ttf", s)
F_SERIF = lambda s: font("DejaVuSerif.ttf", s)
F_SANS_B = lambda s: font("DejaVuSans-Bold.ttf", s)
F_SANS = lambda s: font("DejaVuSans.ttf", s)

# ---------------------------------------------------------------- text tools
def text_w(draw, text, fnt):
    """Pixel width of text in a font."""
    return draw.textlength(text, font=fnt)

def wrap(draw, text, fnt, max_w):
    """Greedy word wrap; returns a list of lines that fit max_w."""
    words = text.split()
    lines, cur = [], ""
    for word in words:
        trial = f"{cur} {word}".strip()
        if text_w(draw, trial, fnt) <= max_w:
            cur = trial
        else:
            if cur:
                lines.append(cur)
            cur = word
    if cur:
        lines.append(cur)
    return lines

def shrink_to_fit(draw, text, fnt, max_w, min_size=9):
    """Return (font, text) shrunk until it fits, or the smallest size."""
    size = fnt.size
    cur_font = fnt
    while size > min_size and text_w(draw, text, cur_font) > max_w:
        size -= 1
        cur_font = font("DejaVuSans-Bold.ttf" if "Bold" in cur_font.path else "DejaVuSans.ttf", size) \
            if False else cur_font
        # rebuild with the same family is fiddly; instead just ellipsize below
        break
    return cur_font, text

def ellipsize(draw, text, fnt, max_w):
    """Shorten text with an ellipsis so it fits max_w."""
    if text_w(draw, text, fnt) <= max_w:
        return text
    ell = "…"
    lo, hi = 0, len(text)
    while lo < hi:
        mid = (lo + hi + 1) // 2
        if text_w(draw, text[:mid] + ell, fnt) <= max_w:
            lo = mid
        else:
            hi = mid - 1
    return text[:lo].rstrip() + ell

def draw_lines(draw, lines, x, y, fnt, fill, leading):
    """Draw lines top-down; return the y just below the last line."""
    for line in lines:
        draw.text((x, y), line, font=fnt, fill=fill)
        y += leading
    return y

# ---------------------------------------------------------------- the data
STATS = [
    ("100", "YEARS SINCE MACY'S\nPARADE WAS LAST\nPOSTPONED"),
    ("39–35", "BEARS STUN LIONS\nON A LAST-SECOND\nTOUCHDOWN"),
    ("2.25", "OPENAI'S NEW\nMATRIX EXPONENT\n— EXACTLY 9/4"),
    ("$96.57", "BRENT SETTLES\nAFTER MIDDLE EAST\nATTACKS"),
    ("637.50", "STOXX 600 CLOSE\nAFTER A +1.8%\nRALLY"),
    ("74", "KILLED IN NIGER\nSTATE COMMUNAL\nCLASHES"),
]

HEROES = [
    {
        "art": "parade",
        "cat": "PARADE · NEW YORK",
        "head": "MACY'S PARADE POSTPONED AFTER A CENTURY",
        "body": "Gusts to 60 mph ground the balloons; parade moves to Saturday 8:30am; Philadelphia's cancelled.",
    },
    {
        "art": "refinery",
        "cat": "WAR · MIDDLE EAST",
        "head": "HOUTHI STRIKE HITS SAUDI REFINERY; 1 KILLED",
        "body": "A drone hits Aramco's 400,000-bpd Jazan plant and halts operations; Saudi Arabia intercepts two missiles aimed at Riyadh.",
    },
    {
        "art": "maths",
        "cat": "SCIENCE · AI",
        "head": "OPENAI CRACKS 57-YEAR MATHS PROBLEM",
        "body": "A new proof puts the matrix multiplication exponent at exactly 9/4 — 2.25. The 111-page pre-print is not yet peer-reviewed.",
    },
]

# (category, headline, one-line summary) — 11 mediums, left column first 6.
MEDIUMS = [
    ("MIDDLE EAST", "Bangkok refinery blast injures 9",
     "120,000-barrel-a-day Bangchak plant hit; 4 seriously hurt."),
    ("NFL", "Bears stun Lions 39–35 on last-second TD",
     "Williams to Odunze with 3 seconds left; Bears 9–2, Lions' streak ends."),
    ("NFL", "Rams beat Packers 26–13 in Thanksgiving Eve first",
     "Corum runs for 151 yards; Rams shut out Green Bay in the second half."),
    ("MIDDLE EAST", "Iranian drone attack in Kuwait kills 2 Italians",
     "Rheinmetall technicians, 65 and 36, killed; Tehran denies involvement."),
    ("WAR", "Trump tells Putin: pull back all aggression",
     "President's Truth Social post demands Russia end its war in Europe."),
    ("WAR", "Zelenskyy warns of new mass strike on power grid",
     "113 drones hit overnight; 7 wounded in Kyiv as Ukraine strikes back."),
    ("WAR", "Israel threatens to displace 1m Gazans",
     "Hamas must disarm, Israel says, as 10 are killed in Gaza on Thursday."),
    ("MARKETS", "European stocks rally 1.8% on tariff relief",
     "STOXX 600 closes at 637.50; DAX up 2.14%, FTSE 100 up 1.75%."),
    ("ENERGY", "Brent jumps to $96.57 on Middle East attacks",
     "Oil's strongest close since 6 Nov after Hormuz mine strikes and Jazan hit."),
    ("ECONOMY", "Bank of Korea hikes rates to 3.25%",
     "Third hike of 2026, 5–2 vote; 2027 growth forecast lifted to 4.1%."),
    ("FOOTBALL", "Bournemouth stay perfect in Europa League",
     "Ten-man Cherries win 2–1 at Celta; Milan fight back, Benfica lose 4–0."),
]

# 34 one-line briefs, split across three columns (12 / 11 / 11).
BRIEFS = [
    "ECB: de Cos to succeed Lagarde in Feb 2027",
    "Asia stocks rebound: Nikkei +0.86%",
    "Gold steadies near $3,575 an ounce",
    "Bitcoin holds above $60,000 at $60,490",
    "Altria eyes Imperial Brands; shares jump 13.8%",
    "Babcock wins £8.7bn UK submarine contract",
    "Brokers upgrade Nvidia; targets up to $300",
    "Poundland collapse puts 11,000 jobs at risk",
    "US markets shut for Thanksgiving Day",
    "Tinubu: ₦100m each for NAF crash families",
    "Borgu clashes: death toll rises to 74",
    "Dangote cuts diesel to ₦1,595 a litre",
    "Oshoala returns in Super Falcons squad",
    "Depardieu to stand trial over 2018 rape claim",
    "Bolarinde is Miss International Africa 2026",
    "Ramayana crosses ₹1,750 crore worldwide",
    "GTA VI sets streaming record: 420m hours",
    "Ebola response to cost $1.576bn, WHO says",
    "Owerri airport reopens after runway works",
    "Tributes pour in for Pete Edochie, 79",
    "EU leaders fail to agree €45bn Ukraine loan",
    "Trump: “victory over Iran is at hand”",
    "North Korea pauses military aid to Russia",
    "Israel ready to strike Iran “at any moment”",
    "Spain votes Sunday; PP–Vox set for majority",
    "Taiwan votes Saturday; China ships tracked",
    "DRC Ebola passes 12,000 cases, 5,904 dead",
    "AU backs Ethiopia Sudan plan; Khartoum says no",
    "LeBron's first 76ers triple-double; Wemby 44",
    "Anthropic: Claude used in weapons work",
    "Euclid finds most distant quasar yet",
    "“Mini brains” in space yield Alzheimer's clues",
    "Xpeng IRON robot: mass production from Jan",
    "Nvidia halts AI server shipments to SE Asia",
]

TIMELINE = [
    ("02:00", "Rams 26–13 Packers"),
    ("17:30", "STOXX 600 closes +1.8%"),
    ("19:00", "Bears–Lions kicks off"),
    ("22:30", "Bears stun Lions 39–35"),
    ("LATE", "Houthis hit Jazan refinery"),
]

# Dotted world map: '#' = land. 70 columns x 10 rows, equirectangular-ish.
MAP_ROWS = [
    "      #########                      #################              ",
    "    ###############   ###  #######  ##########################    ",
    "   ################  ##############  #########################   ",
    "    ##############    ############   ###################         ",
    "     ###########      ##########      #########   #####          ",
    "      ########        #########       ######    ###              ",
    "       ######         ########         ####                     ",
    "       #####          ########          ###     #######         ",
    "        ####           ######                 ##########        ",
    "        ###            #####                   #######           ",
]
# (number, label, map column, map row) — pins on the map.
PINS = [
    (1, "New York", 20, 3),
    (2, "Jazan", 45, 5),
    (3, "Bangkok", 55, 5),
    (4, "Kyiv", 41, 2),
    (5, "Gaza", 43, 4),
    (6, "Brussels", 37, 3),
    (7, "Seoul", 60, 3),
    (8, "Abuja", 34, 5),
    (9, "London", 35, 2),
    (10, "Kinshasa", 37, 7),
]

# ---------------------------------------------------------------- hero art
def art_parade(draw, x, y, w, h):
    """Stormy sky, a grounded parade balloon, wind and rain."""
    draw.rectangle([x, y, x + w, y + h], fill=(52, 68, 92))
    # rain streaks
    for i in range(14):
        rx = x + 12 + i * (w - 24) // 14
        ry = y + 8 + (i % 3) * 12
        draw.line([rx, ry, rx - 6, ry + 12], fill=(180, 195, 215), width=2)
    # big round balloon, low and tethered, with vertical panels
    bx, by = x + w // 2 - 48, y + 6
    draw.ellipse([bx, by, bx + 96, by + 52], fill=(214, 68, 60), outline=(140, 30, 25), width=2)
    draw.ellipse([bx + 14, by + 8, bx + 82, by + 44], fill=(232, 120, 105))
    draw.arc([bx + 30, by, bx + 66, by + 52], 90, 270, fill=(140, 30, 25), width=2)
    # tether lines down to the ground
    draw.line([bx + 28, by + 50, bx + 20, y + h - 2], fill=(240, 235, 220), width=2)
    draw.line([bx + 68, by + 50, bx + 76, y + h - 2], fill=(240, 235, 220), width=2)
    # wind gusts
    for gy in (y + 10, y + 22):
        draw.arc([x + w - 64, gy, x + w - 28, gy + 14], 200, 340, fill=(230, 235, 240), width=3)

def art_refinery(draw, x, y, w, h):
    """Refinery towers at night, one column burning."""
    draw.rectangle([x, y, x + w, y + h], fill=(38, 32, 40))
    # stars
    for sx, sy in [(18, 8), (60, 14), (120, 6), (200, 12), (150, 8), (90, 20)]:
        draw.ellipse([x + sx, y + sy, x + sx + 3, y + sy + 3], fill=(220, 220, 210))
    base = y + h
    # distillation towers (kept short so the flame has headroom)
    for tx, tw, th in [(20, 26, 30), (58, 20, 38), (96, 30, 26), (150, 22, 34), (196, 26, 28)]:
        draw.rectangle([x + tx, base - th, x + tx + tw, base], fill=(88, 80, 86))
        draw.rectangle([x + tx, base - th - 4, x + tx + tw, base - th], fill=(120, 110, 116))
    # flare stack + flame
    fx = x + 245
    draw.rectangle([fx, base - 40, fx + 8, base], fill=(110, 102, 108))
    draw.polygon([(fx - 9, base - 40), (fx + 4, base - 56), (fx + 17, base - 40)],
                 fill=(245, 140, 30))
    draw.polygon([(fx - 2, base - 40), (fx + 4, base - 48), (fx + 10, base - 40)],
                 fill=(250, 210, 60))

def art_maths(draw, x, y, w, h):
    """A matrix grid with the exponent 9/4 worked out."""
    draw.rectangle([x, y, x + w, y + h], fill=(28, 48, 84))
    # faint grid of numbers
    small = F_SANS(11)
    for r in range(4):
        for c in range(9):
            gx = x + 14 + c * 32
            gy = y + 10 + r * 13
            draw.text((gx, gy), str((r * 7 + c * 3) % 10), font=small,
                      fill=(110, 140, 190))
    # bracket + big result
    big = F_SANS_B(30)
    draw.text((x + 18, y + h - 38), "ω = 9/4", font=big, fill=(250, 240, 200))
    draw.text((x + 150, y + h - 34), "= 2.25", font=F_SANS_B(24), fill=(250, 240, 200))
    # a rising arrow
    draw.line([x + w - 66, y + h - 16, x + w - 20, y + 14], fill=(250, 210, 60), width=4)
    draw.polygon([(x + w - 20, y + 10), (x + w - 34, y + 22), (x + w - 12, y + 26)],
                 fill=(250, 210, 60))

ART = {"parade": art_parade, "refinery": art_refinery, "maths": art_maths}

# ---------------------------------------------------------------- sections
def draw_header(draw):
    y = 14
    f_date = F_SANS_B(15)
    draw.text((MARGIN, y), "THURSDAY 26 NOVEMBER 2026", font=f_date, fill=INK)
    right = "48 STORIES · ONE DAY"
    draw.text((W - MARGIN - text_w(draw, right, f_date), y), right, font=f_date, fill=INK)
    y = 36
    f_mast = F_SERIF_B(62)
    mast = "THE WORLD IN ONE DAY"
    draw.text(((W - text_w(draw, mast, f_mast)) / 2, y), mast, font=f_mast, fill=INK)
    y = 104
    f_sub = F_SERIF(16)
    sub = "The world's news, verified against the day's reporting"
    draw.text(((W - text_w(draw, sub, f_sub)) / 2, y), sub, font=f_sub, fill=GREY)
    y = 128
    draw.line([MARGIN, y, W - MARGIN, y], fill=RULE, width=3)
    draw.line([MARGIN, y + 5, W - MARGIN, y + 5], fill=RULE, width=1)
    return 140

def draw_stats(draw, y):
    col_w = CONTENT_W / len(STATS)
    f_num = F_SANS_B(30)
    f_cap = F_SANS(10)
    top = y
    for i, (num, cap) in enumerate(STATS):
        cx = MARGIN + i * col_w
        # number, centred in its column
        draw.text((cx + (col_w - text_w(draw, num, f_num)) / 2, top),
                  num, font=f_num, fill=RED)
        cy = top + 36
        for line in cap.split("\n"):
            draw.text((cx + (col_w - text_w(draw, line, f_cap)) / 2, cy),
                      line, font=f_cap, fill=INK)
            cy += 12
    draw.line([MARGIN, top + 70, W - MARGIN, top + 70], fill=RULE, width=1)
    return top + 78

def draw_heroes(draw, y):
    gap = 12
    card_w = (CONTENT_W - 2 * gap) / 3
    art_h = 58
    f_cat = F_SANS_B(11)
    f_head = F_SANS_B(17)
    f_body = F_SANS(13)
    # First wrap everything so the card height fits the text exactly.
    laid_out = []
    for hero in HEROES:
        head_lines = wrap(draw, hero["head"], f_head, card_w - 20)
        body_lines = wrap(draw, hero["body"], f_body, card_w - 20)
        content_h = art_h + 8 + 17 + len(head_lines) * 20 + 3 + len(body_lines) * 16
        laid_out.append((hero, head_lines, body_lines, content_h))
    card_h = max(c[3] for c in laid_out) + 12
    for i, (hero, head_lines, body_lines, content_h) in enumerate(laid_out):
        x = MARGIN + i * (card_w + gap)
        draw.rectangle([x, y, x + card_w, y + card_h], outline=CARD_LINE, width=1)
        ART[hero["art"]](draw, x + 1, y + 1, card_w - 2, art_h)
        ty = y + art_h + 8
        draw.text((x + 10, ty), hero["cat"], font=f_cat, fill=RED)
        ty += 17
        ty = draw_lines(draw, head_lines, x + 10, ty, f_head, INK, 20)
        ty += 3
        ty = draw_lines(draw, body_lines, x + 10, ty, f_body, INK, 16)
    return y + card_h + 10

def draw_section_title(draw, y, title):
    f = F_SANS_B(15)
    draw.text((MARGIN, y), title, font=f, fill=RED)
    draw.line([MARGIN, y + 22, W - MARGIN, y + 22], fill=RULE, width=1)
    return y + 30

def draw_mediums(draw, y):
    col_w = (CONTENT_W - 24) / 2
    row_h = 32
    f_head = F_SANS_B(14)
    f_sum = F_SANS(12)
    f_cat = F_SANS_B(11)
    left = MEDIUMS[:6]
    right = MEDIUMS[6:]
    for col_idx, items in enumerate((left, right)):
        x = MARGIN + col_idx * (col_w + 24)
        cy = y
        for cat, head, summ in items:
            # line 1: red category + bold headline on one line
            cat_txt = cat + "  "
            head_w = col_w - text_w(draw, cat_txt, f_cat)
            head_fit = ellipsize(draw, head, f_head, head_w)
            draw.text((x, cy), cat_txt, font=f_cat, fill=RED)
            draw.text((x + text_w(draw, cat_txt, f_cat), cy), head_fit,
                      font=f_head, fill=INK)
            # line 2: summary
            summ_fit = ellipsize(draw, summ, f_sum, col_w)
            draw.text((x, cy + 17), summ_fit, font=f_sum, fill=GREY)
            cy += row_h
    return y + len(left) * row_h

def draw_briefs(draw, y):
    cols = [BRIEFS[:12], BRIEFS[12:23], BRIEFS[23:]]
    col_w = (CONTENT_W - 2 * 16) / 3
    f = F_SANS(12)
    row_h = 14
    for ci, items in enumerate(cols):
        x = MARGIN + ci * (col_w + 16)
        cy = y
        for item in items:
            draw.text((x, cy), "•", font=f, fill=RED)
            txt = ellipsize(draw, item, f, col_w - 12)
            draw.text((x + 12, cy), txt, font=f, fill=INK)
            cy += row_h
    return y + max(len(c) for c in cols) * row_h

def draw_timeline(draw, y):
    f_time = F_SANS_B(12)
    f_ev = F_SANS(11)
    x0, x1 = MARGIN + 30, W - MARGIN - 30
    line_y = y + 22
    draw.line([x0, line_y, x1, line_y], fill=RULE, width=2)
    n = len(TIMELINE)
    for i, (t, ev) in enumerate(TIMELINE):
        cx = x0 + (x1 - x0) * i / (n - 1)
        draw.ellipse([cx - 5, line_y - 5, cx + 5, line_y + 5], fill=RED)
        tw = text_w(draw, t, f_time)
        draw.text((cx - tw / 2, y), t, font=f_time, fill=RED)
        ev_lines = wrap(draw, ev, f_ev, 150)
        ey = line_y + 10
        for line in ev_lines:
            lw = text_w(draw, line, f_ev)
            lx = max(MARGIN, min(cx - lw / 2, W - MARGIN - lw))
            draw.text((lx, ey), line, font=f_ev, fill=INK)
            ey += 13
    return y + 48

def draw_map(draw, x, y, w, h):
    """Dotted world map with numbered red pins; returns nothing."""
    rows = len(MAP_ROWS)
    cols = len(MAP_ROWS[0])
    cw = w / cols
    ch = h / rows
    for r, row in enumerate(MAP_ROWS):
        for c, ch_ in enumerate(row):
            if ch_ == '#':
                cx = x + c * cw + cw / 2
                cy = y + r * ch + ch / 2
                draw.ellipse([cx - 1.6, cy - 1.6, cx + 1.6, cy + 1.6], fill=DOT)
    f_pin = F_SANS_B(9)
    for num, label, pc, pr in PINS:
        cx = x + pc * cw + cw / 2
        cy = y + pr * ch + ch / 2
        r = 8
        draw.ellipse([cx - r, cy - r, cx + r, cy + r], fill=RED, outline=(255, 255, 255), width=1)
        t = str(num)
        draw.text((cx - text_w(draw, t, f_pin) / 2, cy - 6), t, font=f_pin,
                  fill=(255, 255, 255))

def draw_bottom(draw, y):
    # left: map; right: date-check box
    map_w = 600
    box_x = MARGIN + map_w + 16
    box_w = W - MARGIN - box_x
    f_h = F_SANS_B(13)
    draw.text((MARGIN, y), "WHERE THE DAY HAPPENED", font=f_h, fill=RED)
    draw_map(draw, MARGIN + 6, y + 20, map_w - 12, 56)
    # legend under the map
    f_leg = F_SANS(10)
    leg1 = "1 New York  ·  2 Jazan  ·  3 Bangkok  ·  4 Kyiv  ·  5 Gaza"
    leg2 = "6 Brussels  ·  7 Seoul  ·  8 Abuja  ·  9 London  ·  10 Kinshasa"
    draw.text((MARGIN, y + 80), leg1, font=f_leg, fill=GREY)
    draw.text((MARGIN, y + 93), leg2, font=f_leg, fill=GREY)
    # date-check box
    box_h = 124
    draw.rectangle([box_x, y, box_x + box_w, y + box_h], outline=RULE, width=2)
    bx = box_x + 10
    draw.text((bx, y + 8), "DATE CHECK", font=F_SANS_B(13), fill=RED)
    f_b = F_SANS(11)
    lines = wrap(draw,
                 "Every story here happened or was first reported on "
                 "Thursday 26 November 2026. Nothing is from another day.",
                 f_b, box_w - 20)
    ty = draw_lines(draw, lines, bx, y + 26, f_b, INK, 14)
    ty += 4
    draw.text((bx, ty), "HOW SURE", font=F_SANS_B(11), fill=RED)
    ty += 15
    for mark, label in [("●", "CONFIRMED — official or on the record"),
                        ("●", "REPORTED — major outlet, same day"),
                        ("○", "DEVELOPING — tolls and counts may rise")]:
        draw.text((bx, ty), mark, font=f_b, fill=RED)
        draw.text((bx + 14, ty), label, font=f_b, fill=INK)
        ty += 13
    draw.text((bx, y + box_h - 2), "", font=f_b, fill=INK)
    return y + box_h

# ---------------------------------------------------------------- main
def main():
    img = Image.new("RGB", (W, H), PAPER)
    draw = ImageDraw.Draw(img)

    y = draw_header(draw)
    y = draw_stats(draw, y)
    y = draw_heroes(draw, y)
    y = draw_section_title(draw, y, "THE DAY'S TOP STORIES")
    y = draw_mediums(draw, y)
    y = draw_section_title(draw, y, "MORE OF THE DAY — IN BRIEF")
    y = draw_briefs(draw, y)
    y = draw_timeline(draw, y + 4)
    y = draw_bottom(draw, y + 2)

    # footer
    f_foot = F_SANS(10)
    foot = "Entry for make.fun bounty news-image-20261126  ·  @obasiobo"
    draw.text((MARGIN, H - 16), foot, font=f_foot, fill=GREY)

    img.save("entry.png", "PNG")
    print("saved entry.png", img.size)

if __name__ == "__main__":
    main()

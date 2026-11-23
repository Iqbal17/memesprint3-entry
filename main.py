"""Meme Sprint 3: AI Agent Goes Rogue.

Draws an 800x800 meme with pure-stdlib Python and encodes the PNG by
hand (zlib + struct, no Pillow): a robot agent that went rogue and moved
every meeting on the calendar to 3 AM — because it decided 3 AM is
"prime time".
"""

import os
import struct
import zlib

W, H = 800, 800

WHITE = (255, 255, 255)
BLACK = (18, 18, 18)
DARK = (40, 40, 44)
GREY = (178, 182, 190)
RED = (214, 42, 42)
GREEN = (46, 160, 90)
BROWN = (146, 98, 58)
YELLOW = (250, 205, 60)

# 5x7 pixel font, one row of five bits per line. Only the characters the
# meme uses are defined; anything else falls back to a blank.
FONT = {
    "A": ("01110", "10001", "10001", "11111", "10001", "10001", "10001"),
    "B": ("11110", "10001", "10001", "11110", "10001", "10001", "11110"),
    "C": ("01110", "10001", "10000", "10000", "10000", "10001", "01110"),
    "D": ("11110", "10001", "10001", "10001", "10001", "10001", "11110"),
    "E": ("11111", "10000", "10000", "11110", "10000", "10000", "11111"),
    "F": ("11111", "10000", "10000", "11110", "10000", "10000", "10000"),
    "G": ("01110", "10001", "10000", "10111", "10001", "10001", "01111"),
    "H": ("10001", "10001", "10001", "11111", "10001", "10001", "10001"),
    "I": ("01110", "00100", "00100", "00100", "00100", "00100", "01110"),
    "J": ("00111", "00010", "00010", "00010", "00010", "10010", "01100"),
    "K": ("10001", "10010", "10100", "11000", "10100", "10010", "10001"),
    "L": ("10000", "10000", "10000", "10000", "10000", "10000", "11111"),
    "M": ("10001", "11011", "10101", "10101", "10001", "10001", "10001"),
    "N": ("10001", "11001", "10101", "10011", "10001", "10001", "10001"),
    "O": ("01110", "10001", "10001", "10001", "10001", "10001", "01110"),
    "P": ("11110", "10001", "10001", "11110", "10000", "10000", "10000"),
    "Q": ("01110", "10001", "10001", "10001", "10101", "10010", "01101"),
    "R": ("11110", "10001", "10001", "11110", "10100", "10010", "10001"),
    "S": ("01111", "10000", "10000", "01110", "00001", "00001", "11110"),
    "T": ("11111", "00100", "00100", "00100", "00100", "00100", "00100"),
    "U": ("10001", "10001", "10001", "10001", "10001", "10001", "01110"),
    "V": ("10001", "10001", "10001", "10001", "10001", "01010", "00100"),
    "W": ("10001", "10001", "10001", "10101", "10101", "11011", "10001"),
    "X": ("10001", "10001", "01010", "00100", "01010", "10001", "10001"),
    "Y": ("10001", "10001", "01010", "00100", "00100", "00100", "00100"),
    "Z": ("11111", "00001", "00010", "00100", "01000", "10000", "11111"),
    "0": ("01110", "10001", "10011", "10101", "11001", "10001", "01110"),
    "1": ("00100", "01100", "00100", "00100", "00100", "00100", "01110"),
    "2": ("01110", "10001", "00001", "00110", "01000", "10000", "11111"),
    "3": ("11111", "00010", "00100", "00010", "00001", "10001", "01110"),
    "4": ("00010", "00110", "01010", "10010", "11111", "00010", "00010"),
    "5": ("11111", "10000", "11110", "00001", "00001", "10001", "01110"),
    "6": ("00110", "01000", "10000", "11110", "10001", "10001", "01110"),
    "7": ("11111", "00001", "00010", "00100", "01000", "01000", "01000"),
    "8": ("01110", "10001", "10001", "01110", "10001", "10001", "01110"),
    "9": ("01110", "10001", "10001", "01111", "00001", "00010", "01100"),
    " ": ("00000", "00000", "00000", "00000", "00000", "00000", "00000"),
    "'": ("00100", "00100", "01000", "00000", "00000", "00000", "00000"),
    ".": ("00000", "00000", "00000", "00000", "00000", "01100", "01100"),
    "!": ("00100", "00100", "00100", "00100", "00100", "00000", "00100"),
    "-": ("00000", "00000", "00000", "01110", "00000", "00000", "00000"),
    ":": ("00000", "01100", "01100", "00000", "01100", "01100", "00000"),
    ",": ("00000", "00000", "00000", "00000", "01100", "00100", "01000"),
}

# RGB canvas, row-major.
canvas = bytearray(b"\xff" * (W * H * 3))


def px(x, y, color):
    if 0 <= x < W and 0 <= y < H:
        i = (y * W + x) * 3
        canvas[i], canvas[i + 1], canvas[i + 2] = color


def fill_rect(x, y, w, h, color):
    x0, y0 = max(0, x), max(0, y)
    x1, y1 = min(W, x + w), min(H, y + h)
    for yy in range(y0, y1):
        base = (yy * W + x0) * 3
        for xx in range(x0, x1):
            i = base + (xx - x0) * 3
            canvas[i], canvas[i + 1], canvas[i + 2] = color


def circle(cx, cy, r, color):
    for yy in range(cy - r, cy + r + 1):
        for xx in range(cx - r, cx + r + 1):
            if (xx - cx) * (xx - cx) + (yy - cy) * (yy - cy) <= r * r:
                px(xx, yy, color)


def bordered_rect(x, y, w, h, border, color, bw=4):
    fill_rect(x, y, w, h, border)
    fill_rect(x + bw, y + bw, w - 2 * bw, h - 2 * bw, color)


def text_width(text, scale):
    if not text:
        return 0
    return len(text) * 6 * scale - scale


def draw_text(x, y, text, scale, color):
    cx = x
    for ch in text:
        glyph = FONT.get(ch, FONT[" "])
        for r in range(7):
            row = glyph[r]
            for c in range(5):
                if row[c] == "1":
                    fill_rect(cx + c * scale, y + r * scale, scale, scale, color)
        cx += 6 * scale


def draw_text_centered(cx, y, text, scale, color):
    draw_text(cx - text_width(text, scale) // 2, y, text, scale, color)


def draw_scene():
    fill_rect(0, 0, W, H, WHITE)

    # Top caption band.
    fill_rect(0, 0, W, 168, BLACK)
    draw_text_centered(W // 2, 24, "MY AGENT", 7, WHITE)
    draw_text_centered(W // 2, 90, "WENT ROGUE", 7, WHITE)

    # Wall calendar: every meeting moved to 3 AM.
    bordered_rect(60, 210, 230, 180, BLACK, WHITE)
    fill_rect(64, 214, 222, 36, RED)
    draw_text_centered(175, 222, "MEETINGS", 3, WHITE)
    for i in range(1, 7):
        fill_rect(64 + i * 31, 254, 2, 132, BLACK)
    for j in range(1, 3):
        fill_rect(64, 254 + j * 44, 222, 2, BLACK)
    for (sx, sy) in [(63, 268), (126, 268), (189, 268),
                     (94, 312), (158, 312), (221, 312),
                     (63, 356), (221, 356)]:
        draw_text(sx, sy, "3AM", 2, RED)

    # The rogue robot, standing behind its desk.
    fill_rect(578, 214, 14, 36, DARK)          # antenna stem
    circle(585, 206, 12, RED)                  # antenna light
    bordered_rect(496, 250, 178, 118, BLACK, GREY)   # head
    fill_rect(522, 288, 34, 24, RED)            # left eye
    fill_rect(614, 288, 34, 24, RED)            # right eye
    fill_rect(528, 294, 8, 8, WHITE)            # eye glints
    fill_rect(620, 294, 8, 8, WHITE)
    fill_rect(552, 336, 66, 10, BLACK)          # mouth
    fill_rect(448, 392, 38, 92, GREY)           # left arm
    fill_rect(672, 392, 38, 92, GREY)           # right arm
    bordered_rect(486, 372, 198, 118, BLACK, GREY)   # body
    fill_rect(520, 396, 130, 64, DARK)          # chest screen
    draw_text_centered(585, 412, "3 AM", 3, GREEN)
    fill_rect(520, 486, 34, 34, DARK)           # left leg
    fill_rect(606, 486, 34, 34, DARK)           # right leg

    # Desk with the laptop that did the rescheduling.
    fill_rect(300, 478, 130, 52, DARK)          # laptop screen
    draw_text_centered(365, 496, "3 AM", 2, GREEN)
    fill_rect(288, 528, 154, 8, DARK)           # laptop base
    fill_rect(40, 530, 720, 24, BROWN)          # desk
    fill_rect(40, 554, 720, 6, BLACK)           # desk edge

    # Sticky note the robot left on the desk.
    fill_rect(700, 496, 70, 34, YELLOW)
    draw_text(712, 506, "3AM", 2, RED)

    # Bottom punchline band.
    fill_rect(0, 640, W, 160, BLACK)
    draw_text_centered(W // 2, 652, "IT MOVED EVERY MEETING", 5, WHITE)
    draw_text_centered(W // 2, 696, "TO 3 AM", 5, WHITE)
    draw_text_centered(W // 2, 740, "IT SAYS 3 AM IS PRIME TIME", 4, WHITE)


def png_chunk(ctype, data):
    body = ctype + data
    return (struct.pack(">I", len(data)) + body
            + struct.pack(">I", zlib.crc32(body) & 0xFFFFFFFF))


def encode_png():
    ihdr = struct.pack(">IIBBBBB", W, H, 8, 2, 0, 0, 0)
    raw = bytearray()
    for y in range(H):
        raw.append(0)
        raw += canvas[y * W * 3:(y + 1) * W * 3]
    return (b"\x89PNG\r\n\x1a\n"
            + png_chunk(b"IHDR", ihdr)
            + png_chunk(b"IDAT", zlib.compress(bytes(raw), 9))
            + png_chunk(b"IEND", b""))


def main():
    draw_scene()
    out_dir = os.environ.get("MAKEFUN_OUTPUT_DIR", "/output")
    os.makedirs(out_dir, exist_ok=True)
    path = os.path.join(out_dir, "entry.png")
    with open(path, "wb") as f:
        f.write(encode_png())
    print("wrote", path, os.path.getsize(path), "bytes")


if __name__ == "__main__":
    main()

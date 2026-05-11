#!/usr/bin/env python3
"""
gen_icons.py — 產生台南市停車場查詢 PWA 所需的所有圖示
執行方式：python gen_icons.py
會在 icons/ 資料夾中輸出各尺寸的 PNG 圖示
"""

import os
from PIL import Image, ImageDraw, ImageFont

SIZES = [72, 96, 128, 144, 152, 192, 384, 512]
OUTPUT_DIR = "icons"

# ── 品牌色彩 ──────────────────────────────────────────────
BG_TOP    = (15,  90, 60)   # 深綠（頂部漸層）
BG_BOT    = (10,  50, 35)   # 更深綠（底部漸層）
ACCENT    = (255, 200, 0)   # 金黃（P 字）
SHADOW    = (0,   0,   0, 80)

os.makedirs(OUTPUT_DIR, exist_ok=True)


def draw_gradient_bg(draw, size):
    """垂直線性漸層背景"""
    for y in range(size):
        ratio = y / size
        r = int(BG_TOP[0] + (BG_BOT[0] - BG_TOP[0]) * ratio)
        g = int(BG_TOP[1] + (BG_BOT[1] - BG_TOP[1]) * ratio)
        b = int(BG_TOP[2] + (BG_BOT[2] - BG_TOP[2]) * ratio)
        draw.line([(0, y), (size, y)], fill=(r, g, b))


def draw_rounded_rect(draw, xy, radius, fill):
    x0, y0, x1, y1 = xy
    draw.rounded_rectangle([x0, y0, x1, y1], radius=radius, fill=fill)


def make_icon(size: int) -> Image.Image:
    img = Image.new("RGBA", (size, size), (0, 0, 0, 0))
    draw = ImageDraw.Draw(img)

    # ── 圓角背景 ─────────────────────────────────────────
    radius = int(size * 0.22)
    # 漸層用臨時圖層
    grad = Image.new("RGBA", (size, size), (0, 0, 0, 0))
    gd = ImageDraw.Draw(grad)
    draw_gradient_bg(gd, size)
    mask = Image.new("L", (size, size), 0)
    md = ImageDraw.Draw(mask)
    md.rounded_rectangle([0, 0, size - 1, size - 1], radius=radius, fill=255)
    img.paste(grad, mask=mask)

    draw = ImageDraw.Draw(img)

    # ── 外框光澤線 ────────────────────────────────────────
    bw = max(2, int(size * 0.025))
    draw.rounded_rectangle(
        [bw // 2, bw // 2, size - bw // 2 - 1, size - bw // 2 - 1],
        radius=radius - bw // 2,
        outline=(255, 255, 255, 40),
        width=bw,
    )

    # ── 停車 P 字圓形底板 ─────────────────────────────────
    cx, cy = size // 2, size // 2
    circle_r = int(size * 0.32)
    draw.ellipse(
        [cx - circle_r, cy - circle_r, cx + circle_r, cy + circle_r],
        fill=(0, 0, 0, 60),
    )
    draw.ellipse(
        [cx - circle_r + bw, cy - circle_r + bw,
         cx + circle_r - bw, cy + circle_r - bw],
        fill=(255, 200, 0, 30),
        outline=ACCENT + (200,),
        width=max(2, int(size * 0.015)),
    )

    # ── P 字 ─────────────────────────────────────────────
    font_size = int(size * 0.40)
    try:
        font = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf", font_size)
    except Exception:
        font = ImageFont.load_default()

    text = "P"
    bbox = draw.textbbox((0, 0), text, font=font)
    tw = bbox[2] - bbox[0]
    th = bbox[3] - bbox[1]
    tx = cx - tw // 2 - bbox[0]
    ty = cy - th // 2 - bbox[1]

    # 陰影
    draw.text((tx + max(1, size // 80), ty + max(1, size // 80)), text,
              font=font, fill=(0, 0, 0, 120))
    # 主文字
    draw.text((tx, ty), text, font=font, fill=ACCENT)

    # ── 小圓點裝飾（右下） ────────────────────────────────
    dot_r = max(3, int(size * 0.05))
    dot_x = int(size * 0.76)
    dot_y = int(size * 0.76)
    draw.ellipse(
        [dot_x - dot_r, dot_y - dot_r, dot_x + dot_r, dot_y + dot_r],
        fill=ACCENT,
    )

    return img


def main():
    print("🎨 開始產生 PWA 圖示...")
    for s in SIZES:
        icon = make_icon(s)
        path = os.path.join(OUTPUT_DIR, f"icon-{s}x{s}.png")
        icon.save(path, "PNG")
        print(f"  ✅ {path}")

    # 額外：apple-touch-icon (180×180)
    icon180 = make_icon(180)
    apple_path = os.path.join(OUTPUT_DIR, "apple-touch-icon.png")
    icon180.save(apple_path, "PNG")
    print(f"  ✅ {apple_path}")

    # favicon 16×16 & 32×32
    for s in (16, 32):
        fav = make_icon(s)
        fav_path = os.path.join(OUTPUT_DIR, f"favicon-{s}x{s}.png")
        fav.save(fav_path, "PNG")
        print(f"  ✅ {fav_path}")

    print(f"\n🎉 完成！共產生 {len(SIZES) + 3} 個圖示於 {OUTPUT_DIR}/ 資料夾")


if __name__ == "__main__":
    main()

"""Generate file-type icons for the kPDF file lists."""
from PIL import Image, ImageDraw, ImageFont
from pathlib import Path

ICON_SIZE = 32
ICON_DIR = Path("c:/Users/Klemen/Work/kpdf/assets/icons")
ICON_DIR.mkdir(parents=True, exist_ok=True)

FILE_TYPES = {
    "pdf":  ("#C0392B", "white", "PDF"),
    "jpg":  ("#2980B9", "white", "JPG"),
    "jpeg": ("#2980B9", "white", "JPG"),
    "png":  ("#27AE60", "white", "PNG"),
    "gif":  ("#8E44AD", "white", "GIF"),
    "tif":  ("#E67E22", "white", "TIF"),
    "tiff": ("#E67E22", "white", "TIF"),
    "bmp":  ("#7F8C8D", "white", "BMP"),
}

def make_icon(bg_color, text_color, label):
    img = Image.new("RGBA", (ICON_SIZE, ICON_SIZE), (0, 0, 0, 0))
    draw = ImageDraw.Draw(img)

    # Rounded-ish rectangle as document body
    draw.rectangle([2, 0, ICON_SIZE - 2, ICON_SIZE - 1], fill=bg_color)

    # Folded corner (top-right)
    fold = 7
    draw.polygon([
        (ICON_SIZE - 2 - fold, 0),
        (ICON_SIZE - 2, fold),
        (ICON_SIZE - 2 - fold, fold),
    ], fill="white")

    # Label text
    try:
        font = ImageFont.truetype("arialbd.ttf", 9)
    except:
        font = ImageFont.load_default()

    bbox = draw.textbbox((0, 0), label, font=font)
    tw = bbox[2] - bbox[0]
    th = bbox[3] - bbox[1]
    tx = (ICON_SIZE - tw) // 2
    ty = (ICON_SIZE - th) // 2 + 3
    draw.text((tx, ty), label, fill=text_color, font=font)

    return img

for ext, (bg, fg, label) in FILE_TYPES.items():
    icon = make_icon(bg, fg, label)
    out = ICON_DIR / f"{ext}.png"
    icon.save(out)
    print(f"✓ {out.name}")

print(f"\nIcons saved to: {ICON_DIR}")

"""Generate a custom PDF icon for kPDF application."""
from PIL import Image, ImageDraw, ImageFont
from pathlib import Path

# Create icon
icon_size = 256
icon = Image.new('RGB', (icon_size, icon_size), color='#2E5090')  # Dark blue background

draw = ImageDraw.Draw(icon)

# Draw a red rectangle representing a PDF document
margin = 30
doc_left = margin
doc_top = margin
doc_right = icon_size - margin
doc_bottom = icon_size - margin

# White document background
draw.rectangle([doc_left, doc_top, doc_right, doc_bottom], fill='white', outline='#2E5090', width=3)

# Red "PDF" label bar at top
label_height = 50
draw.rectangle([doc_left, doc_top, doc_right, doc_top + label_height], fill='#E63946')

# Draw "PDF" text in white
try:
    # Try to use a built-in font, fallback to default
    font = ImageFont.truetype("arial.ttf", 60)
except:
    font = ImageFont.load_default()

text = "PDF"
# Calculate text position for centering
bbox = draw.textbbox((0, 0), text, font=font)
text_width = bbox[2] - bbox[0]
text_height = bbox[3] - bbox[1]
text_x = (icon_size - text_width) // 2
text_y = (label_height - text_height) // 2 + doc_top

draw.text((text_x, text_y), text, fill='white', font=font)

# Draw some horizontal lines to represent text/content in the document
line_y_start = doc_top + label_height + 30
line_spacing = 20
line_width = 80

for i in range(4):
    y = line_y_start + (i * line_spacing)
    draw.line([(margin + 20, y), (margin + 20 + line_width, y)], fill='#CCCCCC', width=3)

# Save icon as PNG
icon_path = Path("c:/Users/Klemen/Work/kpdf/assets/kpdf_icon.png")
icon_path.parent.mkdir(exist_ok=True)
icon.save(icon_path)
print(f"✓ Icon created: {icon_path}")

# Also save as ICO for Windows taskbar
icon.save(icon_path.with_suffix('.ico'))
print(f"✓ Icon created: {icon_path.with_suffix('.ico')}")

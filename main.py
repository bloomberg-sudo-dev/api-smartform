from pdf2image import convert_from_path
from PIL import ImageDraw, ImageFont
import pytesseract
from collections import defaultdict

# --- Field data (JSON-style) ---
field_data = {
    "familyName": "Doe",
    "givenName": "John",
    "email": "john.doe@example.com",
    "application": "Study Permit"
}

# --- Map from field name to label text expected in OCR ---
label_map = {
    "familyName": "family name (surname)",
    "givenName": "given name",
    "email": "email address",
    "application": "type of application"
}

# --- Load PDF pages as images ---
pages = convert_from_path("imm5476e.pdf", dpi=300)

# Load font
try:
    font = ImageFont.truetype("arial.ttf", 28)
except:
    font = ImageFont.load_default()
    print("⚠️ Using default font")

# --- Process each page ---
for page_num, page in enumerate(pages):
    draw = ImageDraw.Draw(page)

    # OCR data
    ocr_data = pytesseract.image_to_data(page, output_type=pytesseract.Output.DICT)
    lines = defaultdict(list)

    for i, word in enumerate(ocr_data['text']):
        if word.strip():
            line_no = ocr_data['line_num'][i]
            lines[line_no].append({
                "word": word,
                "left": ocr_data['left'][i],
                "top": ocr_data['top'][i]
            })

    # Rebuild lines
    line_texts = []
    for words in lines.values():
        text = " ".join(w["word"] for w in words)
        avg_x = sum(w["left"] for w in words) // len(words)
        avg_y = sum(w["top"] for w in words) // len(words)
        line_texts.append((text, avg_x, avg_y))

    # Draw matching field values on this page
    for field_key, value in field_data.items():
        target_label = label_map.get(field_key, "").lower()

        match_found = False
        for full_text, x, y in line_texts:
            if target_label in full_text.lower():
                print(f"✅ Page {page_num+1}: Placing '{value}' near: '{full_text}' at ({x}, {y})")
                draw.text((x + 250, y), value, fill="black", font=font)
                match_found = True
                break

        if not match_found:
            print(f"⚠️ Page {page_num+1}: No match found for: '{target_label}'")

# --- Save all pages into final PDF ---
pages[0].save("filled_imm5476e.pdf", "PDF", save_all=True, append_images=pages[1:])
print("✅ All pages saved to filled_imm5476e.pdf")

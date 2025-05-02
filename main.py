from pdf2image import convert_from_path
from PIL import Image, ImageDraw, ImageFont
import pytesseract

# --- Step 1: Load field data (can be loaded from a JSON file) ---
field_data = {
    "familyName": "Doe",
    "dateOfBirth": "1990-01-01",
    "address": "123 Main St, Cityville, CA",
    "postalCode": "12345",
    "phoneNumber": "+1-234-567-8900",
    "givenName": "John",
    "email": "john.doe@example.com",
    "application": "Work  Permit"
}

# Optional: fallback label text (for OCR-based search if needed)
label_map = {
    "familyName": "family name",
    "dateOfBirth": "date of birth",
    "address": "address",
    "postalCode": "postal code",
    "phoneNumber": "phone number",
    "givenName": "given name",
    "email": "email address",
    "application": "type of application"
}

# --- Step 2: Manually calibrated field coordinates (adjust as needed) ---
manual_positions = {
    "familyName": (400, 1435),
    "givenName": (1500, 1435),
    "email": (400, 1730),
    "application": (400, 2070)
}

# --- Step 3: Convert PDF to image ---
pages = convert_from_path("IRCC_forms/imm5476e.pdf", dpi=300)
first_page = pages[0].copy()  # Work on a copy

draw = ImageDraw.Draw(first_page)

# Load font
try:
    font = ImageFont.truetype("arial.ttf", 28)
except:
    font = ImageFont.load_default()
    print("⚠️ Using default font (arial.ttf not found)")

# --- Step 4: OCR debug block (optional, for visual inspection) ---
ocr_data = pytesseract.image_to_data(first_page, output_type=pytesseract.Output.DICT)

for i in range(len(ocr_data['text'])):
    word = ocr_data['text'][i]
    x, y, w, h = ocr_data['left'][i], ocr_data['top'][i], ocr_data['width'][i], ocr_data['height'][i]
    if word.strip():
        draw.rectangle([(x, y), (x + w, y + h)], outline="red")  # draw box
        # draw.text((x, y), word, fill="blue", font=font)          # draw label

# --- Step 5: Draw user data at fixed positions ---
for field_key, value in field_data.items():
    if field_key in manual_positions:
        x, y = manual_positions[field_key]
        print(f"✅ Writing '{value}' at ({x},{y}) for field: {field_key}")
        draw.text((x, y), value, fill="black", font=font)
    else:
        print(f"⚠️ No manual position found for field: {field_key}")

# --- Step 6: Save the filled PDF ---
pages[0] = first_page  # Replace the modified page in the list
output_path = "IRCC_forms/filled_imm5476e.pdf"
pages[0].save(output_path, "PDF", save_all=True, append_images=pages[1:])
print(f"✅ Done. Output saved to {output_path}")

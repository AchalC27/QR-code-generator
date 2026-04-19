import streamlit as st
from PIL import Image, ImageDraw, ImageFont
import qrcode
import os

st.title("🌱 Product Label QR Generator")

# ---------------- INPUTS ---------------- #

product_name = st.text_input("Product Name")
description = st.text_input("Description")

st.subheader("Composition")

if "composition" not in st.session_state:
    st.session_state.composition = [{"name": "", "value": 0.0}]

def add_row():
    st.session_state.composition.append({"name": "", "value": 0.0})

total = 0
for i, comp in enumerate(st.session_state.composition):
    col1, col2 = st.columns([3, 1])
    comp["name"] = col1.text_input(f"Component {i+1}", key=f"name_{i}")
    comp["value"] = col2.number_input(f"% {i+1}", min_value=0.0, step=0.1, key=f"val_{i}")
    total += comp["value"]

st.button("➕ Add Row", on_click=add_row)
st.markdown(f"### Total: {total:.2f} %")

crop = st.text_input("Crop Name")
dose = st.text_input("Dose")

# ---------------- GENERATE ---------------- #

if st.button("Generate Label + QR"):

    img = Image.new("RGBA", (900, 1200), "#f7f7f7")
    draw = ImageDraw.Draw(img)

    try:
        title_font = ImageFont.truetype("arial.ttf", 48)
        bold_font = ImageFont.truetype("arialbd.ttf", 26)
        normal_font = ImageFont.truetype("arial.ttf", 24)
        small_font = ImageFont.truetype("arial.ttf", 20)
    except:
        title_font = bold_font = normal_font = small_font = None

    # Helper function for center alignment
    def center_text(text, y, font, fill):
        bbox = draw.textbbox((0, 0), text, font=font)
        text_width = bbox[2] - bbox[0]
        x = (900 - text_width) // 2
        draw.text((x, y), text, fill=fill, font=font)

    y = 40

    # ---------------- PRODUCT NAME (CENTERED RED) ---------------- #
    center_text(product_name.upper(), y, title_font, "#d32f2f")
    y += 70

    # ---------------- DESCRIPTION (CENTERED) ---------------- #
    center_text(description, y, normal_font, "#333333")
    y += 50

    # ---------------- COMPOSITION ---------------- #
    draw.text((50, y), "COMPOSITION", fill="#000000", font=bold_font)
    y += 35

    for comp in st.session_state.composition:
        draw.text((50, y), comp["name"], fill="#222222", font=normal_font)
        draw.text((750, y), f"{comp['value']:.2f}", fill="#000000", font=normal_font)
        y += 30

    # Total
    y += 10
    draw.text((50, y), "Total", fill="#000000", font=bold_font)
    draw.text((750, y), f"{total:.2f}", fill="#000000", font=bold_font)
    y += 50

    # ---------------- CROP & DOSE ---------------- #
    draw.text((50, y), "Name of the crop –", fill="#000000", font=bold_font)
    draw.text((300, y), crop, fill="#333333", font=normal_font)
    y += 35

    draw.text((50, y), "Doses:", fill="#000000", font=bold_font)
    draw.text((200, y), dose, fill="#333333", font=normal_font)
    y += 40

    # Agriculture line (bold + underline)
    text = "(For Agriculture Use only)"
    draw.text((50, y), text, fill="#000000", font=bold_font)
    draw.line((50, y+28, 420, y+28), fill="black", width=1)
    y += 50

    # Manufactured line (bold + underline)
    text2 = "Manufactured, Packed and Marketed by"
    draw.text((50, y), text2, fill="#000000", font=bold_font)
    draw.line((50, y+28, 600, y+28), fill="black", width=1)
    y += 50

    # ---------------- FIXED LOGO (BOTTOM RIGHT, PROPER RATIO) ---------------- #
    try:
        logo_img = Image.open("logo.png").convert("RGBA")

        # Maintain aspect ratio
        max_width = 220
        ratio = max_width / logo_img.width
        new_size = (int(logo_img.width * ratio), int(logo_img.height * ratio))

        logo_img = logo_img.resize(new_size, Image.LANCZOS)

        # Position: bottom-right with margin
        x_pos = img.width - new_size[0] - 40
        y_pos = img.height - new_size[1] - 40

        # Transparent layer
        temp = Image.new("RGBA", img.size, (255, 255, 255, 0))
        temp.paste(logo_img, (x_pos, y_pos), logo_img)

        # Merge
        img = Image.alpha_composite(img.convert("RGBA"), temp).convert("RGB")

    except Exception as e:
        st.error(f"Logo error: {e}")

    # Company Name
    draw.text((50, y), "Puma Crop Care", fill="#000000", font=title_font)
    y += 50

    manufacturer_lines = [
        "Plot No A -5, Nand gaon Peth M.I.D.C.",
        "Nagpur Road, Amravati – 444901 (M.S.)",
        "Email – pumacropcare@gmail.com",
        "Customer Care No. 9767899807"
    ]

    for line in manufacturer_lines:
        draw.text((50, y), line, fill="#333333", font=small_font)
        y += 25

    # ---------------- SAVE ---------------- #
    if not os.path.exists("output"):
        os.makedirs("output")

    image_path = "output/label.jpg"
    img.save(image_path)

    st.image(image_path, caption="Styled Label")

    # ---------------- QR ---------------- #
    qr_data = f"http://localhost:8501/{image_path}"
    qr = qrcode.make(qr_data)

    qr_path = "output/qr.png"
    qr.save(qr_path)

    st.image(qr_path, caption="QR Code")

    # Download buttons
    with open(image_path, "rb") as f:
        st.download_button("Download Label", f, "label.jpg")

    with open(qr_path, "rb") as f:
        st.download_button("Download QR", f, "qr.png")
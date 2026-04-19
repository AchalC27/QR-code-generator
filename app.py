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

    WIDTH, HEIGHT = 900, 1200
    img = Image.new("RGBA", (WIDTH, HEIGHT), "#f7f7f7")
    draw = ImageDraw.Draw(img)

    # Fonts (safe fallback)
    try:
        title_font = ImageFont.truetype("arial.ttf", 48)
        bold_font = ImageFont.truetype("arialbd.ttf", 28)
        normal_font = ImageFont.truetype("arial.ttf", 26)
        small_font = ImageFont.truetype("arial.ttf", 22)
    except:
        title_font = bold_font = normal_font = small_font = ImageFont.load_default()

    # Center helper
    def center(text, y, font, color):
        bbox = draw.textbbox((0, 0), text, font=font)
        x = (WIDTH - (bbox[2] - bbox[0])) // 2
        draw.text((x, y), text, fill=color, font=font)

    y = 40

    # ---------------- TITLE ---------------- #
    center(product_name.upper(), y, title_font, "#d32f2f")
    y += 70

    center(description, y, normal_font, "#444")
    y += 60

    # ---------------- COMPOSITION ---------------- #
    draw.text((60, y), "COMPOSITION", fill="black", font=bold_font)
    y += 40

    RIGHT = WIDTH - 80

    for comp in st.session_state.composition:
        name = comp["name"]
        val = f"{comp['value']:.2f}"

        draw.text((60, y), name, fill="#222", font=normal_font)

        bbox = draw.textbbox((0, 0), val, font=normal_font)
        draw.text((RIGHT - (bbox[2]-bbox[0]), y), val, fill="black", font=normal_font)

        y += 35

    # Total
    y += 10
    draw.text((60, y), "Total", fill="black", font=bold_font)

    total_text = f"{total:.2f}"
    bbox = draw.textbbox((0, 0), total_text, font=bold_font)
    draw.text((RIGHT - (bbox[2]-bbox[0]), y), total_text, fill="black", font=bold_font)

    y += 60

    # ---------------- DETAILS ---------------- #
    draw.text((60, y), "Name of the crop –", fill="black", font=bold_font)
    draw.text((350, y), crop, fill="#333", font=normal_font)
    y += 40

    draw.text((60, y), "Doses:", fill="black", font=bold_font)
    draw.text((200, y), dose, fill="#333", font=normal_font)
    y += 50

    # Agriculture line
    text = "(For Agriculture Use only)"
    draw.text((60, y), text, fill="black", font=bold_font)
    draw.line((60, y+30, 450, y+30), fill="black", width=2)
    y += 60

    # Manufactured line
    text2 = "Manufactured, Packed and Marketed by"
    draw.text((60, y), text2, fill="black", font=bold_font)
    draw.line((60, y+30, 700, y+30), fill="black", width=2)
    y += 60

    # ---------------- COMPANY ---------------- #
    draw.text((60, y), "Puma Crop Care", fill="black", font=title_font)
    y += 50

    manufacturer_lines = [
        "Plot No A -5, Nand gaon Peth M.I.D.C.",
        "Nagpur Road, Amravati – 444901 (M.S.)",
        "Email – pumacropcare@gmail.com",
        "Customer Care No. 9767899807"
    ]

    for line in manufacturer_lines:
        draw.text((60, y), line, fill="#444", font=small_font)
        y += 28

    # ---------------- LOGO (BOTTOM RIGHT) ---------------- #
    try:
        logo = Image.open("logo.png").convert("RGBA")

        max_width = 220
        ratio = max_width / logo.width
        new_size = (int(logo.width * ratio), int(logo.height * ratio))
        logo = logo.resize(new_size, Image.LANCZOS)

        x = WIDTH - new_size[0] - 40
        y_logo = HEIGHT - new_size[1] - 40

        temp = Image.new("RGBA", img.size, (255, 255, 255, 0))
        temp.paste(logo, (x, y_logo), logo)

        img = Image.alpha_composite(img, temp)

    except:
        pass

    # ---------------- SAVE ---------------- #
    if not os.path.exists("output"):
        os.makedirs("output")

    image_path = "output/label.png"
    img = img.convert("RGB")
    img.save(image_path)

    st.image(image_path, caption="Generated Label")

    # ---------------- QR ---------------- #
    qr_data = "https://your-app-name.streamlit.app"  # CHANGE AFTER DEPLOY
    qr = qrcode.make(qr_data)

    qr_path = "output/qr.png"
    qr.save(qr_path)

    st.image(qr_path, caption="QR Code")

    # Downloads
    with open(image_path, "rb") as f:
        st.download_button("Download Label", f, "label.png")

    with open(qr_path, "rb") as f:
        st.download_button("Download QR", f, "qr.png")
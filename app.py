import streamlit as st
import cv2
import numpy as np
import matplotlib.pyplot as plt

# -------------------------------------------------
# SETUP
# -------------------------------------------------
st.set_page_config(page_title="Spektrometer", layout="wide")
st.title("📡 Spektrometer Web App (stabile Version)")

# -------------------------------------------------
# SESSION STATE
# -------------------------------------------------
if "img" not in st.session_state:
    st.session_state.img = None

if "calib" not in st.session_state:
    st.session_state.calib = None

# -------------------------------------------------
# IMAGE UPLOAD
# -------------------------------------------------
file = st.file_uploader("Bild hochladen", type=["png", "jpg", "jpeg"])

if file:
    file_bytes = np.asarray(bytearray(file.read()), dtype=np.uint8)
    img = cv2.imdecode(file_bytes, 1)

    gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
    st.session_state.img = gray

# -------------------------------------------------
# CHECK IMAGE
# -------------------------------------------------
if st.session_state.img is None:
    st.stop()

img = st.session_state.img

# -------------------------------------------------
# ROI SLIDER + OVERLAY PREVIEW
# -------------------------------------------------
st.subheader("📐 ROI Auswahl mit Overlay")

h, w = img.shape

x1, x2 = st.slider("X Bereich", 0, w, (0, w))
y1, y2 = st.slider("Y Bereich", 0, h, (0, h))

# -------------------------------------------------
# PREVIEW IMAGE (3-channel für Overlay)
# -------------------------------------------------
preview = cv2.cvtColor(img, cv2.COLOR_GRAY2BGR)

# -------------------------------------------------
# OVERLAY ERSTELLEN
# -------------------------------------------------
overlay = preview.copy()

cv2.rectangle(
    overlay,
    (x1, y1),
    (x2, y2),
    (0, 255, 0),
    -1  # gefüllt für Transparenz
)

alpha = 0.25  # Transparenz
preview = cv2.addWeighted(overlay, alpha, preview, 1 - alpha, 0)

# Rahmen nochmal scharf drüber
cv2.rectangle(
    preview,
    (x1, y1),
    (x2, y2),
    (0, 255, 0),
    2
)

# -------------------------------------------------
# DISPLAY
# -------------------------------------------------
st.image(preview, caption="ROI Vorschau (Overlay)", use_container_width=True)

# -------------------------------------------------
# ROI EXTRAKTION
# -------------------------------------------------
roi = img[y1:y2, x1:x2]

if roi.size == 0:
    st.warning("ROI ist leer")
    st.stop()

# -------------------------------------------------
# SPEKTRUM
# -------------------------------------------------
st.subheader("📈 Spektrum")

intensity = np.mean(roi, axis=0)
pixel = np.arange(len(intensity))

fig, ax = plt.subplots()
ax.plot(pixel, intensity)
ax.set_xlabel("Pixel")
ax.set_ylabel("Intensität")
ax.grid()

st.pyplot(fig)

# -------------------------------------------------
# PEAK / KALIBRIERUNG
# -------------------------------------------------
st.subheader("📍 Kalibrierung")

p1 = st.number_input("Peak 1 Pixel", 0, len(pixel)-1, 10)
l1 = st.number_input("Wellenlänge 1 (nm)", value=500.0)

p2 = st.number_input("Peak 2 Pixel", 0, len(pixel)-1, 100)
l2 = st.number_input("Wellenlänge 2 (nm)", value=600.0)

if st.button("Kalibrieren"):
    a = (l2 - l1) / (p2 - p1)
    b = l1 - a * p1
    st.session_state.calib = (a, b)
    st.success("Kalibriert!")

# -------------------------------------------------
# KALIBRIERTES SPEKTRUM
# -------------------------------------------------
if st.session_state.calib is not None:
    a, b = st.session_state.calib
    wavelength = a * pixel + b

    st.subheader("🌈 Wellenlängen-Spektrum")

    fig2, ax2 = plt.subplots()
    ax2.plot(wavelength, intensity)
    ax2.set_xlabel("Wellenlänge (nm)")
    ax2.set_ylabel("Intensität")
    ax2.grid()

    st.pyplot(fig2)

# -------------------------------------------------
# CSV EXPORT
# -------------------------------------------------
st.subheader("💾 Export")

mode = st.selectbox("X-Achse", ["Pixel", "Wellenlänge (nm)"])

if st.button("CSV exportieren"):

    if mode == "Pixel" or st.session_state.calib is None:
        x = pixel
        name = "pixel"
    else:
        a, b = st.session_state.calib
        x = a * pixel + b
        name = "wavelength"

    data = np.column_stack((x, intensity))

    csv_str = "\n".join([f"{x[i]},{intensity[i]}" for i in range(len(x))])

    st.download_button(
        "Download CSV",
        data=csv_str,
        file_name=f"spectrum_{name}.csv",
        mime="text/csv"
    )

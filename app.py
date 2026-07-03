import streamlit as st
import cv2
import numpy as np
import matplotlib.pyplot as plt

# -------------------------------------------------
# APP SETUP
# -------------------------------------------------
st.set_page_config(page_title="Spektrometer", layout="wide")
st.title("📡 Spektrometer Web App (stabile Version)")

# -------------------------------------------------
# SESSION STATE
# -------------------------------------------------
if "img" not in st.session_state:
    st.session_state.img = None

if "roi" not in st.session_state:
    st.session_state.roi = None

if "calib" not in st.session_state:
    st.session_state.calib = None  # (a, b)

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
# ROI SLIDER (STABILSTE LÖSUNG)
# -------------------------------------------------
st.subheader("📐 ROI Auswahl")

h, w = img.shape

x1, x2 = st.slider("X Bereich", 0, w, (0, w))
y1, y2 = st.slider("Y Bereich", 0, h, (0, h))

roi = img[y1:y2, x1:x2]

st.image(roi, caption="ROI Vorschau", clamp=True)

# -------------------------------------------------
# SPEKTRUM
# -------------------------------------------------
st.subheader("📈 Spektrum")

if roi.size == 0:
    st.warning("ROI ist leer")
    st.stop()

intensity = np.mean(roi, axis=0)
pixel = np.arange(len(intensity))

fig, ax = plt.subplots()
ax.plot(pixel, intensity)
ax.set_xlabel("Pixel")
ax.set_ylabel("Intensität")
ax.grid()

st.pyplot(fig)

# -------------------------------------------------
# PEAK PICKING (SIMPEL & STABIL)
# -------------------------------------------------
st.subheader("📍 Peak Auswahl (Kalibrierung)")

p1 = st.number_input("Peak 1 Pixel", min_value=0, max_value=len(pixel)-1, value=10)
l1 = st.number_input("Wellenlänge 1 (nm)", value=500.0)

p2 = st.number_input("Peak 2 Pixel", min_value=0, max_value=len(pixel)-1, value=100)
l2 = st.number_input("Wellenlänge 2 (nm)", value=600.0)

if st.button("Kalibrieren"):
    a = (l2 - l1) / (p2 - p1)
    b = l1 - a * p1
    st.session_state.calib = (a, b)
    st.success("Kalibriert!")

# -------------------------------------------------
# WAVELENGTH AXIS
# -------------------------------------------------
if st.session_state.calib is not None:
    a, b = st.session_state.calib
    wavelength = a * pixel + b

    st.subheader("🌈 Kalibriertes Spektrum")

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

    st.download_button(
        "Download CSV",
        data=np.savetxt(None, data, delimiter=","),
        file_name=f"spectrum_{name}.csv",
        mime="text/csv"
    )

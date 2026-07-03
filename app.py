import streamlit as st
import cv2
import numpy as np
import matplotlib.pyplot as plt
from scipy.signal import find_peaks, savgol_filter

# -------------------------------------------------
# SETUP
# -------------------------------------------------
st.set_page_config(page_title="Spektrometer", layout="wide")
st.title("📡 Spektrometer Web App (Auto Peak Detection)")

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

if st.session_state.img is None:
    st.stop()

img = st.session_state.img

# -------------------------------------------------
# ROI (einfach stabil gelassen)
# -------------------------------------------------
st.subheader("📐 ROI Auswahl")

h, w = img.shape
x1, x2 = st.slider("X Bereich", 0, w, (0, w))
y1, y2 = st.slider("Y Bereich", 0, h, (0, h))

roi = img[y1:y2, x1:x2]

st.image(roi, caption="ROI")

# -------------------------------------------------
# SPEKTRUM
# -------------------------------------------------
st.subheader("📈 Spektrum")

intensity = np.mean(roi, axis=0)
pixel = np.arange(len(intensity))

# -------------------------------------------------
# GLÄTTUNG (WICHTIG FÜR PEAKS)
# -------------------------------------------------
if len(intensity) > 11:
    smooth = savgol_filter(intensity, 11, 3)
else:
    smooth = intensity

fig, ax = plt.subplots()
ax.plot(pixel, intensity, alpha=0.3, label="raw")
ax.plot(pixel, smooth, label="smooth")
ax.legend()
ax.grid()

st.pyplot(fig)

# -------------------------------------------------
# PEAK DETECTION
# -------------------------------------------------
st.subheader("📍 Automatische Peaks")

peaks, _ = find_peaks(smooth, distance=10)

peak_values = smooth[peaks]

# Top Peaks auswählen
top_idx = np.argsort(peak_values)[-10:]  # max 10 Peaks
peaks = peaks[top_idx]

st.write("Gefundene Peaks:", peaks)

# -------------------------------------------------
# USER AUSWAHL DER 2 PEAKS
# -------------------------------------------------
if len(peaks) >= 2:

    p1 = st.selectbox("Peak 1 wählen", peaks)
    p2 = st.selectbox("Peak 2 wählen", peaks)

    l1 = st.number_input("Wellenlänge Peak 1 (nm)", value=500.0)
    l2 = st.number_input("Wellenlänge Peak 2 (nm)", value=600.0)

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

    st.subheader("🌈 Kalibriertes Spektrum")

    fig2, ax2 = plt.subplots()
    ax2.plot(wavelength, smooth)
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

    data = np.column_stack((x, smooth))

    csv_str = "\n".join([f"{x[i]},{smooth[i]}" for i in range(len(x))])

    st.download_button(
        "Download CSV",
        data=csv_str,
        file_name=f"spectrum_{name}.csv",
        mime="text/csv"
    )

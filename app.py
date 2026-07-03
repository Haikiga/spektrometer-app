import streamlit as st
import cv2
import numpy as np
import plotly.graph_objects as go

# -------------------------------------------------
# SETUP
# -------------------------------------------------
st.set_page_config(page_title="Spektrometer", layout="wide")
st.title("Spektrometer Web App")

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
# ROI SELECTION
# -------------------------------------------------
st.subheader("Bereich Auswählen")

h, w = img.shape

x1, x2 = st.slider("X Bereich", 0, w, (0, w))
y1, y2 = st.slider("Y Bereich", 0, h, (0, h))

roi = img[y1:y2, x1:x2]

# Overlay
preview = cv2.cvtColor(img, cv2.COLOR_GRAY2BGR)
overlay = preview.copy()

cv2.rectangle(overlay, (x1, y1), (x2, y2), (0, 255, 0), -1)
preview = cv2.addWeighted(overlay, 0.25, preview, 0.75, 0)
cv2.rectangle(preview, (x1, y1), (x2, y2), (0, 255, 0), 2)

st.image(preview, caption="ROI Overlay", use_container_width=True)

if roi.size == 0:
    st.warning("ROI ist leer")
    st.stop()

# -------------------------------------------------
# SPEKTRUM
# -------------------------------------------------
st.subheader("Spektrum")

intensity = np.mean(roi, axis=0)
pixel = np.arange(len(intensity))

fig = go.Figure()

fig.add_trace(go.Scatter(
    x=pixel,
    y=intensity,
    mode="lines",
    name="Spektrum",
    hovertemplate="Pixel: %{x}<br>Intensität: %{y}<extra></extra>"
))

fig.update_layout(
    height=500,
    xaxis_title="Pixel",
    yaxis_title="Intensität",
    hovermode="x unified"
)

st.plotly_chart(fig, use_container_width=True)

# -------------------------------------------------
# KALIBRIERUNG
# -------------------------------------------------
st.subheader("Kalibrierung (2 Punkte wählen)")

p1 = st.number_input("Pixel 1", 0, len(pixel)-1, 10)
l1 = st.number_input("Wellenlänge 1 (nm)", value=500.0)

p2 = st.number_input("Pixel 2", 0, len(pixel)-1, 100)
l2 = st.number_input("Wellenlänge 2 (nm)", value=600.0)

if st.button("Kalibrieren"):
    if p1 != p2:
        a = (l2 - l1) / (p2 - p1)
        b = l1 - a * p1
        st.session_state.calib = (a, b)
        st.success("Kalibriert!")

# -------------------------------------------------
# KALIBRIERTES SPEKTRUM
# -------------------------------------------------
if st.session_state.calib is not None:

    st.subheader("Wellenlängen-Spektrum")

    a, b = st.session_state.calib
    wavelength = a * pixel + b

    fig2 = go.Figure()

    fig2.add_trace(go.Scatter(
        x=wavelength,
        y=intensity,
        mode="lines",
        name="Kalibriert",
        hovertemplate="λ: %{x:.2f} nm<br>I: %{y}<extra></extra>"
    ))

    fig2.update_layout(
        height=500,
        xaxis_title="Wellenlänge (nm)",
        yaxis_title="Intensität"
    )

    st.plotly_chart(fig2, use_container_width=True)

# -------------------------------------------------
# CSV EXPORT
# -------------------------------------------------
st.subheader("Export")

mode = st.selectbox("X-Achse", ["Pixel", "Wellenlänge (nm)"])

if st.button("CSV exportieren"):

    if mode == "Pixel" or st.session_state.calib is None:
        x = pixel
        name = "pixel"
    else:
        a, b = st.session_state.calib
        x = a * pixel + b
        name = "wavelength"

    csv_str = "\n".join([f"{x[i]},{intensity[i]}" for i in range(len(x))])

    st.download_button(
        "Download CSV",
        data=csv_str,
        file_name=f"spectrum_{name}.csv",
        mime="text/csv"
    )

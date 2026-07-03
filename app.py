import streamlit as st
import cv2
import numpy as np
import matplotlib.pyplot as plt

from streamlit_drawable_canvas import st_canvas

st.title("📡 Spektrometer Web App")

# -------------------------------------------------
# IMAGE UPLOAD
# -------------------------------------------------
file = st.file_uploader("Bild hochladen", type=["png", "jpg", "jpeg"])

if file:
    file_bytes = np.asarray(bytearray(file.read()), dtype=np.uint8)
    img = cv2.imdecode(file_bytes, 1)

    gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)

    st.subheader("🔍 Bild + ROI Auswahl")

    # -------------------------------------------------
    # ROI CANVAS
    # -------------------------------------------------
    canvas_result = st_canvas(
        fill_color="rgba(255, 0, 0, 0.2)",
        stroke_width=2,
        stroke_color="#ff0000",
        background_image=cv2.cvtColor(gray, cv2.COLOR_GRAY2RGB),
        update_streamlit=True,
        height=400,
        drawing_mode="rect",
        key="canvas"
    )

    roi = None

    if canvas_result.json_data is not None:
        objects = canvas_result.json_data["objects"]

        if len(objects) > 0:
            obj = objects[-1]

            x = int(obj["left"])
            y = int(obj["top"])
            w = int(obj["width"])
            h = int(obj["height"])

            roi = gray[y:y+h, x:x+w]

    # -------------------------------------------------
    # SPECTRUM
    # -------------------------------------------------
    if roi is not None and roi.size > 0:
        intensity = np.mean(roi, axis=0)

        st.subheader("📈 Spektrum")

        fig, ax = plt.subplots()
        ax.plot(intensity)
        ax.set_xlabel("Pixel")
        ax.set_ylabel("Intensität")
        ax.grid()

        st.pyplot(fig)

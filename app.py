import streamlit as st
import cv2
import numpy as np
import matplotlib.pyplot as plt

st.title("📡 Spektrometer Web App")

file = st.file_uploader("Bild hochladen", type=["png", "jpg", "jpeg"])

if file:
    file_bytes = np.asarray(bytearray(file.read()), dtype=np.uint8)
    img = cv2.imdecode(file_bytes, 1)

    gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)

    st.image(gray, caption="Spektrum Bild", use_column_width=True)

    roi = gray  # später verbessern

    intensity = np.mean(roi, axis=0)

    fig, ax = plt.subplots()
    ax.plot(intensity)
    ax.set_title("Spektrum")

    st.pyplot(fig)

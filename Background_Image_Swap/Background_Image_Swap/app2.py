import streamlit as st
from rembg import remove
from PIL import Image, ImageEnhance
import io
import cv2
import numpy as np

st.title("🎨 Background Swap with Adjustments & Filters")

# Upload images
uploaded_foreground = st.file_uploader("Upload the foreground image", type=["png", "jpg", "jpeg"])
uploaded_background = st.file_uploader("Upload the background image", type=["png", "jpg", "jpeg"])

if uploaded_foreground and uploaded_background:
    foreground = Image.open(uploaded_foreground).convert("RGBA")
    background = Image.open(uploaded_background).convert("RGBA")

    # Remove background
    no_bg = remove(foreground)

    # Resize background to match foreground
    background = background.resize(no_bg.size)

    # Adjustments
    st.sidebar.header("🔧 Adjustments")

    # Opacity Control
    opacity = st.sidebar.slider("Opacity of Foreground", 0.1, 1.0, 1.0)
    fg_np = np.array(no_bg).astype(float)  # Convert to NumPy array
    fg_np[..., 3] = fg_np[..., 3] * opacity  # Modify alpha channel
    no_bg = Image.fromarray(fg_np.astype(np.uint8))  # Convert back to image

    # Brightness & Contrast
    brightness = st.sidebar.slider("Brightness", 0.5, 2.0, 1.0)
    contrast = st.sidebar.slider("Contrast", 0.5, 2.0, 1.0)
    enhancer = ImageEnhance.Brightness(no_bg)
    no_bg = enhancer.enhance(brightness)
    enhancer = ImageEnhance.Contrast(no_bg)
    no_bg = enhancer.enhance(contrast)

    # Blur effect on background
    blur_intensity = st.sidebar.slider("Background Blur", 0, 10, 0)
    if blur_intensity > 0:
        bg_np = np.array(background)
        bg_np = cv2.GaussianBlur(bg_np, (blur_intensity * 2 + 1, blur_intensity * 2 + 1), 0)
        background = Image.fromarray(bg_np)

    # Combine images
    combined = Image.alpha_composite(background, no_bg)

    # Function to apply filters
    def apply_filter(image, filter_type):
        img_np = np.array(image.convert("RGB"))  # Convert to NumPy array

        if filter_type == "Cartoon":
            gray = cv2.cvtColor(img_np, cv2.COLOR_RGB2GRAY)
            edges = cv2.Canny(gray, 100, 200)
            img_cartoon = cv2.bitwise_and(img_np, img_np, mask=edges)
            return Image.fromarray(img_cartoon)

        elif filter_type == "Sketch":
            gray = cv2.cvtColor(img_np, cv2.COLOR_RGB2GRAY)
            inv = cv2.bitwise_not(gray)
            blur = cv2.GaussianBlur(inv, (21, 21), 0)
            sketch = cv2.divide(gray, 255 - blur, scale=256)
            return Image.fromarray(sketch)

        elif filter_type == "Neon Glow":
            blur = cv2.GaussianBlur(img_np, (21, 21), 0)
            neon = cv2.addWeighted(img_np, 1.5, blur, -0.5, 0)
            return Image.fromarray(neon)

        elif filter_type == "Greyscale":
            grey = cv2.cvtColor(img_np, cv2.COLOR_RGB2GRAY)
            return Image.fromarray(grey).convert("RGB")  # Convert back to RGB for compatibility

        return image  # If no filter is selected, return the original image

    # Sidebar Filter Selection
    st.sidebar.header("🎨 Filters")
    filter_option = st.sidebar.selectbox("Choose a Filter", ["None", "Cartoon", "Sketch", "Neon Glow", "Greyscale"])

    # Apply selected filter
    if filter_option != "None":
        combined = apply_filter(combined, filter_option)

    # Display final image
    st.image(combined, caption="Edited Image", use_container_width=True)

    # Provide download option
    img_byte_arr = io.BytesIO()
    combined.save(img_byte_arr, format="PNG")
    st.download_button("📥 Download Image", data=img_byte_arr.getvalue(), file_name="edited_image.png", mime="image/png")

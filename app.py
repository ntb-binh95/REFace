import os
import requests
import base64
from io import BytesIO

import streamlit as st
from streamlit_image_select import image_select
from PIL import Image

st.set_page_config(page_title="SiteMana Demo", page_icon="🖼️")
st.title("Personalize Advertisement Demo")

if "src_image" not in st.session_state:
    st.session_state.src_image = ""

if "select_image" not in st.session_state:
    st.session_state.select_image = ""

if "output_image" not in st.session_state:
    st.session_state.output_image = None

if "submitted" not in st.session_state:
    st.session_state.submitted = False

if "uploaded" not in st.session_state:
    st.session_state.uploaded = False

SWAP_FACE_URL = "http://localhost:5001/process_images"

TARGET_IMGS = [
    "examples/FaceSwap/Target/zero-calories.jpg", 
    "examples/FaceSwap/Target/teeth-whitening.jpg", 
    "examples/FaceSwap/Target/burn-fat.jpg"
]
SRC_IMGS = [
    "examples/FaceSwap/Source/source_1.jpg", 
    "examples/FaceSwap/Source/source_2.jpg", 
    "examples/FaceSwap/Source/snoopdog.jpg", 
]

INPUT_FOLDER = "./input_files"

def run_swap_face(src_path, tgt_path, steps, scale):
    src_img = open(src_path, 'rb')
    tgt_img = open(tgt_path, 'rb')

    data = {
        'steps': (None, str(steps)),
        'scale': (None, str(scale)),
        'image1': (src_path, src_img, 'image/jpeg'),
        'image2': (tgt_path, tgt_img, 'image/jpeg')
    }

    response = requests.post(SWAP_FACE_URL, files=data)

    src_img.close()
    tgt_img.close()

    # Check if the response was successful
    if response.status_code == 200:
        json_response = response.json()

        if json_response.get('output_image_url', None) != None:
            # Get the image data from the JSON response
            input_image1_data = json_response['input_image1']
            input_image2_data = json_response['input_image2']
            output_image_data = json_response['output_image_url']

            # Remove the "data:image/jpeg;base64," prefix from the image data
            input_image1_data = input_image1_data.split(',')[1]
            input_image2_data = input_image2_data.split(',')[1]
            output_image_data = output_image_data.split(',')[1]

            # Decode the base64 image data
            input_image1_bytes = base64.b64decode(input_image1_data)
            input_image2_bytes = base64.b64decode(input_image2_data)
            output_image_bytes = base64.b64decode(output_image_data)
            # Save the images to files
            with open('input_image1.jpg', 'wb') as f:
                f.write(input_image1_bytes)

            with open('input_image2.jpg', 'wb') as f:
                f.write(input_image2_bytes)

            with open('output_image.jpg', 'wb') as f:
                f.write(output_image_bytes)

            # Alternatively, you can display the images using PIL
            output_image = Image.open(BytesIO(output_image_bytes))
        else:
            output_image = json_response["no_face_error"]
    else:
        output_image = None
    return output_image

st.subheader("1. Source image")
st.text("Upload your file or choose below image to continue:")
upload_image, choose_image = st.columns(2)
with upload_image:
    uploaded_file = st.file_uploader("Choose a file")
    if uploaded_file is not None and st.session_state.uploaded == False:
        st.session_state.uploaded = True
        input_path = os.path.join(INPUT_FOLDER, uploaded_file.name)
        with open(input_path,'wb') as f:
            f.write(uploaded_file.read())
        st.session_state.src_image = input_path
        print(st.session_state.src_image)

with choose_image:
    selected = image_select("Choose Source Image", SRC_IMGS)
    print("st select: ", st.session_state.select_image)
    print("select: ",  selected)
    if st.session_state.select_image != selected:
        st.session_state.src_image = selected
    st.session_state.select_image = selected

# if st.session_state.uploaded_image != "":
#     st.session_state.src_image = st.session_state.uploaded_image
st.info(f"Selected source image: {os.path.basename(st.session_state.src_image)}")

st.subheader("2. Target image")
target_img = image_select("Choose Target Image", TARGET_IMGS)

st.subheader("3. Submit")
scale = st.slider("Scale", 1.0, 5.0, 2.5, step=0.1)
steps = st.slider("Steps", 5, 50, 20)
if st.button("Submit", type="primary", disabled=False, use_container_width=True):
    with st.spinner("Running..."):
        output_image = run_swap_face(st.session_state.src_image, target_img, steps, scale)
        st.session_state.output_image = output_image
        st.session_state.submitted = True

if isinstance(st.session_state.output_image, str):
    st.error(st.session_state.output_image)
    st.text("You input image: ")
    st.image(Image.open(st.session_state.src_image))
    st.session_state.output_image - None
elif st.session_state.output_image and st.session_state.submitted:
    st.image(st.session_state.output_image)
elif st.session_state.submitted:
    st.error("Internal server error")
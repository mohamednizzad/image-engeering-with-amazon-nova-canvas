import streamlit as st
import base64
import io
import os
from datetime import datetime
from random import randint
from PIL import Image
from amazon_image_gen import BedrockImageGenerator
import file_utils

# Set page configuration
st.set_page_config(
    page_title="AI Engineering Month: Amazon Nova Canvas",
    page_icon="🖼️",
    layout="wide"
)

# Initialize session state variables if they don't exist
if 'output_directory' not in st.session_state:
    generation_id = datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
    st.session_state.output_directory = f"output/{generation_id}"

if 'generated_images' not in st.session_state:
    st.session_state.generated_images = []

# Function to encode image to base64
def encode_image_to_base64(image_file):
    if image_file is not None:
        bytes_data = image_file.getvalue()
        return base64.b64encode(bytes_data).decode("utf-8")
    return None

# Function to display generated images
def display_generated_images(images_list):
    if not images_list:
        return
    
    cols = st.columns(min(3, len(images_list)))
    for i, image_base64 in enumerate(images_list):
        with cols[i % 3]:
            image_bytes = base64.b64decode(image_base64)
            image = Image.open(io.BytesIO(image_bytes))
            st.image(image, use_column_width=True)
            
            # Add download button for each image
            buf = io.BytesIO()
            image.save(buf, format="PNG")
            btn = st.download_button(
                label=f"Download Image {i+1}",
                data=buf.getvalue(),
                file_name=f"generated_image_{i+1}.png",
                mime="image/png"
            )

# Main app title
st.title("Image Engineering with Amazon Nova Canvas")
st.markdown("Generate and manipulate images using Amazon Bedrock's image generation capabilities")

# Sidebar for feature selection
st.sidebar.title("Features")
feature = st.sidebar.selectbox(
    "Select Feature",
    [
        "Simple Image Generation",
        "Color-Guided Generation",
        "Image-Guided Generation",
        "Instant Customization",
        "Background Replacement"
    ]
)

# Common parameters for all features
with st.sidebar.expander("Common Settings", expanded=True):
    quality = st.selectbox("Image Quality", ["standard", "premium"], index=0)
    width = st.select_slider("Width", options=[512, 768, 1024, 1280, 1536], value=1024)
    height = st.select_slider("Height", options=[512, 768, 1024, 1280, 1536], value=768)
    cfg_scale = st.slider("CFG Scale (Prompt Adherence)", 1.0, 10.0, 7.0, 0.1)
    num_images = st.slider("Number of Images", 1, 5, 1)
    use_random_seed = st.checkbox("Use Random Seed", value=True)
    seed = st.number_input("Seed", 0, 858993459, randint(0, 858993459), disabled=use_random_seed)

# Main content area based on selected feature
if feature == "Simple Image Generation":
    st.header("Simple Image Generation")
    
    text_prompt = st.text_area(
        "Text Prompt",
        "A beautiful landscape with mountains and a lake at sunset",
        help="Describe the image you want to generate"
    )
    
    negative_prompt = st.text_area(
        "Negative Prompt (Optional)",
        "clouds, people, text",
        help="List things you want to avoid in the image"
    )
    
    if st.button("Generate Images"):
        with st.spinner("Generating images..."):
            # Configure the inference parameters
            inference_params = {
                "taskType": "TEXT_IMAGE",
                "textToImageParams": {
                    "text": text_prompt,
                    "negativeText": negative_prompt,
                },
                "imageGenerationConfig": {
                    "numberOfImages": num_images,
                    "quality": quality,
                    "width": width,
                    "height": height,
                    "cfgScale": cfg_scale,
                    "seed": randint(0, 858993459) if use_random_seed else seed,
                },
            }
            
            # Create the generator
            generator = BedrockImageGenerator(output_directory=st.session_state.output_directory)
            
            # Generate the image(s)
            response = generator.generate_images(inference_params)
            
            if "images" in response:
                st.session_state.generated_images = response["images"]
                file_utils.save_base64_images(response["images"], st.session_state.output_directory, "image")
                st.success(f"Generated {len(response['images'])} image(s)!")
            else:
                st.error("Failed to generate images. Check the logs for details.")
    
    # Display generated images
    if st.session_state.generated_images:
        display_generated_images(st.session_state.generated_images)

elif feature == "Color-Guided Generation":
    st.header("Color-Guided Generation")
    
    text_prompt = st.text_area(
        "Text Prompt",
        "digital painting of a landscape, dreamy and ethereal",
        help="Describe the image you want to generate"
    )
    
    # Color selection
    st.subheader("Select Colors (up to 5)")
    col1, col2, col3, col4, col5 = st.columns(5)
    
    with col1:
        color1 = st.color_picker("Color 1", "#81FC81")
    with col2:
        color2 = st.color_picker("Color 2", "#386739")
    with col3:
        color3 = st.color_picker("Color 3", "#C9D688")
    with col4:
        color4 = st.color_picker("Color 4", "#FFFFFF")
    with col5:
        color5 = st.color_picker("Color 5", "#FFFFFF")
    
    # Reference image upload (optional)
    st.subheader("Reference Image (Optional)")
    reference_image = st.file_uploader("Upload a reference image for color guidance", type=["png", "jpg", "jpeg"])
    reference_image_base64 = encode_image_to_base64(reference_image) if reference_image else None
    
    if reference_image:
        st.image(reference_image, caption="Reference Image", width=300)
    
    if st.button("Generate Images"):
        with st.spinner("Generating images..."):
            # Configure the inference parameters
            inference_params = {
                "taskType": "COLOR_GUIDED_GENERATION",
                "colorGuidedGenerationParams": {
                    "text": text_prompt,
                    "colors": [color1, color2, color3, color4, color5],
                },
                "imageGenerationConfig": {
                    "numberOfImages": num_images,
                    "quality": quality,
                    "width": width,
                    "height": height,
                    "cfgScale": cfg_scale,
                    "seed": randint(0, 858993459) if use_random_seed else seed,
                },
            }
            
            # Add reference image if provided
            if reference_image_base64:
                inference_params["colorGuidedGenerationParams"]["referenceImage"] = reference_image_base64
            
            # Create the generator
            generator = BedrockImageGenerator(output_directory=st.session_state.output_directory)
            
            # Generate the image(s)
            response = generator.generate_images(inference_params)
            
            if "images" in response:
                st.session_state.generated_images = response["images"]
                file_utils.save_base64_images(response["images"], st.session_state.output_directory, "image")
                st.success(f"Generated {len(response['images'])} image(s)!")
            else:
                st.error("Failed to generate images. Check the logs for details.")
    
    # Display generated images
    if st.session_state.generated_images:
        display_generated_images(st.session_state.generated_images)

elif feature == "Image-Guided Generation":
    st.header("Image-Guided Generation")
    
    text_prompt = st.text_area(
        "Text Prompt",
        "3d animated film style, a person in a colorful outfit",
        help="Describe the image you want to generate"
    )
    
    # Conditioning image upload
    st.subheader("Conditioning Image")
    conditioning_image = st.file_uploader("Upload a conditioning image", type=["png", "jpg", "jpeg"])
    
    if conditioning_image is not None:
        st.image(conditioning_image, caption="Conditioning Image", width=300)
        
        # Control mode and strength
        control_mode = st.selectbox("Control Mode", ["CANNY_EDGE", "SEGMENTATION"], index=1)
        control_strength = st.slider("Control Strength", 0.1, 1.0, 0.3, 0.1)
        
        if st.button("Generate Images"):
            with st.spinner("Generating images..."):
                # Encode the image to base64
                conditioning_image_base64 = encode_image_to_base64(conditioning_image)
                
                # Configure the inference parameters
                inference_params = {
                    "taskType": "TEXT_IMAGE",
                    "textToImageParams": {
                        "text": text_prompt,
                        "conditionImage": conditioning_image_base64,
                        "controlMode": control_mode,
                        "controlStrength": control_strength,
                    },
                    "imageGenerationConfig": {
                        "numberOfImages": num_images,
                        "quality": quality,
                        "width": width,
                        "height": height,
                        "cfgScale": cfg_scale,
                        "seed": randint(0, 858993459) if use_random_seed else seed,
                    },
                }
                
                # Create the generator
                generator = BedrockImageGenerator(output_directory=st.session_state.output_directory)
                
                # Generate the image(s)
                response = generator.generate_images(inference_params)
                
                if "images" in response:
                    st.session_state.generated_images = response["images"]
                    file_utils.save_base64_images(response["images"], st.session_state.output_directory, "image")
                    st.success(f"Generated {len(response['images'])} image(s)!")
                else:
                    st.error("Failed to generate images. Check the logs for details.")
        
        # Display generated images
        if st.session_state.generated_images:
            display_generated_images(st.session_state.generated_images)
    else:
        st.info("Please upload a conditioning image to continue")

elif feature == "Instant Customization":
    st.header("Instant Customization")
    
    text_prompt = st.text_area(
        "Text Prompt",
        "a person sits in a school classroom looking bored, illustrated story",
        help="Describe the image you want to generate"
    )
    
    negative_prompt = st.text_area(
        "Negative Prompt (Optional)",
        "",
        help="List things you want to avoid in the image"
    )
    
    # Reference images upload
    st.subheader("Reference Images")
    st.info("Upload 1-3 reference images of the same subject in different poses/angles")
    
    col1, col2, col3 = st.columns(3)
    
    with col1:
        ref_image1 = st.file_uploader("Reference Image 1", type=["png", "jpg", "jpeg"])
        if ref_image1:
            st.image(ref_image1, caption="Reference 1", use_column_width=True)
    
    with col2:
        ref_image2 = st.file_uploader("Reference Image 2", type=["png", "jpg", "jpeg"])
        if ref_image2:
            st.image(ref_image2, caption="Reference 2", use_column_width=True)
    
    with col3:
        ref_image3 = st.file_uploader("Reference Image 3", type=["png", "jpg", "jpeg"])
        if ref_image3:
            st.image(ref_image3, caption="Reference 3", use_column_width=True)
    
    similarity_strength = st.slider("Similarity Strength", 0.2, 1.0, 0.9, 0.1)
    
    if st.button("Generate Images") and ref_image1:
        with st.spinner("Generating images..."):
            # Encode the images to base64
            images = []
            for img in [ref_image1, ref_image2, ref_image3]:
                if img is not None:
                    images.append(encode_image_to_base64(img))
            
            # Configure the inference parameters
            inference_params = {
                "taskType": "IMAGE_VARIATION",
                "imageVariationParams": {
                    "images": images,
                    "text": text_prompt,
                    "similarityStrength": similarity_strength,
                },
                "imageGenerationConfig": {
                    "numberOfImages": num_images,
                    "quality": quality,
                    "width": width,
                    "height": height,
                    "cfgScale": cfg_scale,
                    "seed": randint(0, 858993459) if use_random_seed else seed,
                },
            }
            
            # Add negative text if provided
            if negative_prompt:
                inference_params["imageVariationParams"]["negativeText"] = negative_prompt
            
            # Create the generator
            generator = BedrockImageGenerator(output_directory=st.session_state.output_directory)
            
            # Generate the image(s)
            response = generator.generate_images(inference_params)
            
            if "images" in response:
                st.session_state.generated_images = response["images"]
                file_utils.save_base64_images(response["images"], st.session_state.output_directory, "image")
                st.success(f"Generated {len(response['images'])} image(s)!")
            else:
                st.error("Failed to generate images. Check the logs for details.")
    
    # Display generated images
    if st.session_state.generated_images:
        display_generated_images(st.session_state.generated_images)

elif feature == "Background Replacement":
    st.header("Background Replacement")
    
    # Choose between background replacement and removal
    operation_type = st.radio(
        "Select Operation",
        ["Background Replacement", "Background Removal"]
    )
    
    # Source image upload
    source_image = st.file_uploader("Upload Source Image", type=["png", "jpg", "jpeg"])
    
    if source_image:
        st.image(source_image, caption="Source Image", width=300)
        
        if operation_type == "Background Replacement":
            text_prompt = st.text_area(
                "Background Description",
                "a sparse stylish kitchen, highly detailed, highest quality",
                help="Describe the new background to generate"
            )
            
            mask_prompt = st.text_input(
                "Mask Prompt (Object to Keep)",
                "person",
                help="Describe the object(s) to keep from the original image"
            )
            
            outpainting_mode = st.selectbox(
                "Outpainting Mode",
                ["DEFAULT", "PRECISE"],
                index=1,
                help="DEFAULT softens the mask. PRECISE keeps it sharp."
            )
            
            if st.button("Replace Background"):
                with st.spinner("Processing image..."):
                    # Encode the image to base64
                    source_image_base64 = encode_image_to_base64(source_image)
                    
                    # Configure the inference parameters
                    inference_params = {
                        "taskType": "OUTPAINTING",
                        "outPaintingParams": {
                            "image": source_image_base64,
                            "text": text_prompt,
                            "maskPrompt": mask_prompt,
                            "outPaintingMode": outpainting_mode,
                        },
                        "imageGenerationConfig": {
                            "numberOfImages": num_images,
                            "quality": quality,
                            "cfgScale": cfg_scale,
                            "seed": randint(0, 858993459) if use_random_seed else seed,
                        },
                    }
                    
                    # Create the generator
                    generator = BedrockImageGenerator(output_directory=st.session_state.output_directory)
                    
                    # Generate the image(s)
                    response = generator.generate_images(inference_params)
                    
                    if "images" in response:
                        st.session_state.generated_images = response["images"]
                        file_utils.save_base64_images(response["images"], st.session_state.output_directory, "image")
                        st.success(f"Generated {len(response['images'])} image(s)!")
                    else:
                        st.error("Failed to generate images. Check the logs for details.")
        
        else:  # Background Removal
            if st.button("Remove Background"):
                with st.spinner("Removing background..."):
                    # Encode the image to base64
                    source_image_base64 = encode_image_to_base64(source_image)
                    
                    # Configure the inference parameters
                    inference_params = {
                        "taskType": "BACKGROUND_REMOVAL",
                        "backgroundRemovalParams": {
                            "image": source_image_base64,
                        },
                    }
                    
                    # Create the generator
                    generator = BedrockImageGenerator(output_directory=st.session_state.output_directory)
                    
                    # Generate the image(s)
                    response = generator.generate_images(inference_params)
                    
                    if "images" in response:
                        st.session_state.generated_images = response["images"]
                        file_utils.save_base64_images(response["images"], st.session_state.output_directory, "image")
                        st.success("Background removed successfully!")
                    else:
                        st.error("Failed to remove background. Check the logs for details.")
        
        # Display generated images
        if st.session_state.generated_images:
            display_generated_images(st.session_state.generated_images)
    else:
        st.info("Please upload a source image to continue")

# Footer
st.sidebar.markdown("---")
st.sidebar.info(
    "This application uses Amazon Bedrock's image generation capabilities. "
    "All generated images are saved in the output directory."
)
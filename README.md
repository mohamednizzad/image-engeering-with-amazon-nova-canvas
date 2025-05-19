# Amazon Nova Canvas: AI-Powered Image Generation with AWS Bedrock

A Python-based image generation application that leverages AWS Bedrock's Nova Canvas model to create, manipulate, and customize images through an intuitive Streamlit interface. The application provides advanced image generation capabilities including text-to-image, color-guided generation, and image-guided generation with real-time preview and customization options.

This project combines AWS Bedrock's powerful image generation capabilities with a user-friendly web interface, allowing users to generate high-quality images with precise control over parameters such as quality, dimensions, and style. The application supports multiple generation modes, extensive customization options, and provides a seamless experience for both simple text-to-image generation and more complex guided image creation tasks.

## Repository Structure
```
.
├── amazon_image_gen.py          # Core image generation class using AWS Bedrock API
├── amazon_image_streamlit_app.py # Main Streamlit application interface
├── requirements.txt             # Core Python dependencies
├── streamlit_requirements.txt   # Additional Streamlit-specific dependencies
└── output/                     # Generated images and metadata storage
    └── [timestamp]/           # Timestamped output directories containing:
        ├── request.json       # Generation request parameters
        ├── response_body.json # API response data
        └── response_metadata.json # AWS response metadata
```

## Usage Instructions
### Prerequisites
- Python 3.7 or higher
- AWS account with Bedrock access
- AWS credentials configured locally
- Required Python packages:
  - boto3 >= 1.33.8
  - Pillow >= 10.1.0
  - ipywidgets >= 8.1.5
  - streamlit >= 1.30.0 (for web interface)

### Installation
1. Clone the repository:
```bash
git clone <repository-url>
cd <repository-name>
```

2. Install dependencies:
```bash
# For core functionality
pip install -r requirements.txt

# For Streamlit interface
pip install -r streamlit_requirements.txt
```

3. Configure AWS credentials:
```bash
aws configure
```

### Quick Start
1. Launch the Streamlit application:
```bash
streamlit run amazon_image_streamlit_app.py
```

2. Select a generation mode:
- Simple Image Generation
- Color-Guided Generation
- Image-Guided Generation

3. Configure generation parameters:
- Enter text prompt
- Adjust image quality and dimensions
- Set CFG scale and seed values
- Click "Generate Images" to create your images

### More Detailed Examples

**Simple Text-to-Image Generation:**
```python
from amazon_image_gen import BedrockImageGenerator

generator = BedrockImageGenerator()
inference_params = {
    "taskType": "TEXT_IMAGE",
    "textToImageParams": {
        "text": "A beautiful landscape with mountains and a lake at sunset",
        "negativeText": "clouds, people, text"
    },
    "imageGenerationConfig": {
        "numberOfImages": 1,
        "quality": "standard",
        "width": 1024,
        "height": 768,
        "cfgScale": 7.0,
        "seed": 123456
    }
}

response = generator.generate_images(inference_params)
```

**Color-Guided Generation:**
```python
inference_params = {
    "taskType": "COLOR_GUIDED_GENERATION",
    "colorGuidedGenerationParams": {
        "text": "digital painting of a landscape",
        "colors": ["#81FC81", "#386739", "#C9D688"]
    },
    "imageGenerationConfig": {
        "numberOfImages": 1,
        "quality": "standard",
        "width": 1024,
        "height": 768
    }
}
```

### Troubleshooting

**Common Issues:**

1. AWS Credentials Error
```
Error: Failed to initialize AWS Bedrock client
```
Solution:
- Verify AWS credentials are properly configured
- Check region settings
- Ensure Bedrock service access is enabled

2. Image Generation Timeout
```
Error: Read timeout error
```
Solution:
- Reduce number of requested images
- Check network connection
- Retry the request

3. Invalid Parameters
```
Error: ValidationException
```
Solution:
- Verify image dimensions are within allowed range (320-4096 pixels)
- Check that all required parameters are provided
- Ensure text prompts meet minimum length requirements

## Data Flow
The application processes image generation requests through AWS Bedrock's Nova Canvas model, handling both synchronous and asynchronous operations with proper error handling and response processing.

```ascii
[User Input] -> [Streamlit Interface] -> [BedrockImageGenerator]
                                              |
                                        [AWS Bedrock API]
                                              |
                                     [Image Generation Model]
                                              |
                                    [Response Processing]
                                              |
                            [Image Display & File Storage]
```

Key Component Interactions:
- Streamlit interface collects user input and configuration
- BedrockImageGenerator handles AWS API communication
- AWS Bedrock processes generation requests
- Response handler processes and validates API responses
- File system manages output storage and organization
- Image display component renders generated images
- Error handling system manages failures at each step
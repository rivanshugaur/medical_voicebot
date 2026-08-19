import os
from dotenv import load_dotenv
import base64
from groq import Groq
load_dotenv()

def encode_image(image_path):
    try:
        with open(image_path, 'rb') as image_file:
            encoded_image = base64.b64encode(image_file.read()).decode('utf-8')
        return encoded_image
    except Exception as e:
        print(f"Error encoding image: {e}")
        return None

model="qwen/qwen3.6-27b"

def analyze_image_with_query(query, system_prompt, model, encoded_image, GROQ_API_KEY):
    """
    Analyze an image with a text query using Groq's vision models.

    Args:
        query (str): The text query to ask about the image
        model (str): The model ID to use for analysis
        encoded_image (str): Base64 encoded image data
        GROQ_API_KEY (str): Groq API key

    Returns:
        str: The model's response or an error message
    """
    if encoded_image is None:
        return "Error: Could not process the image."

    try:
        client = Groq(api_key=GROQ_API_KEY)

        # Format the messages according to Groq's API requirements
        chat_completion = client.chat.completions.create(
            model=model,
            messages=[
    {
        "role": "system",
        "content": system_prompt
    },
    {
        "role": "user",
        "content": [
            {
                "type": "text",
                "text": query
            },
            {
                "type": "image_url",
                "image_url": {
                    "url": f"data:image/jpeg;base64,{encoded_image}"
                }
            }
        ]
    }
]
        )

        import re
        content = chat_completion.choices[0].message.content
        # Remove <think>...</think> blocks including newlines
        content = re.sub(r'<think>.*?</think>', '', content, flags=re.DOTALL).strip()
        return content
    except Exception as e:
        print(f"Error analyzing image: {e}")
        return f"Error analyzing image: {str(e)}"




# llm/llm_wrapper.py
import os
from huggingface_hub import InferenceClient
from dotenv import load_dotenv



def generate_script_api(topic, duration_seconds=5, audience="high school"):
    HF_TOKEN = os.environ.get("HF_TOKEN")
    assert HF_TOKEN
    
    client = InferenceClient(
        model="meta-llama/Meta-LLaMA-3-8B-Instruct",
        token=HF_TOKEN
    )
    
    # Get the directory of the current script
    script_dir = os.path.dirname(os.path.abspath(__file__))

    # Construct the path to your prompt file by going up one level and then into prompts
    prompt_file_path = os.path.join(script_dir, "prompts", "educational_prompt.txt")

    try:
        with open(prompt_file_path, "r") as file:
            prompt_content = file.read()
    except FileNotFoundError:
        return f"Error: Prompt file not found at '{prompt_file_path}'"

    # Substitute the variables in the prompt
    prompt = prompt_content.format(topic=topic, audience=audience, duration_seconds=duration_seconds)
    
    messages = [
        {"role": "user", "content": prompt}
    ]

    print("DEBUG: Attempting to generate text...")
    try:
        response = client.chat_completion(
            messages=messages,
            stream=False,
            max_tokens=400,
            temperature=0.7
        )
        return response.choices[0].message.content
    except Exception as e:
        print(f"Error during API call: {e}")
        return "An error occurred during text generation."
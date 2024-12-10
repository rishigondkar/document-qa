from flask import Flask, request, jsonify, json  # Import required Flask modules
from openai import OpenAI

import os
from dotenv import load_dotenv
from PIL import Image
import requests
import base64




load_dotenv()

OPENAI_API_KEY = os.getenv('OPENAI_API_KEY')
OLLAMA_URL = "http://localhost:11434/api/chat"

app = Flask(__name__)


@app.route('/')
def hello_world():
    return "Hello, World!"

@app.route('/models')
def available_models():
    return ["llama3.2-vision:11b", "Clip", "Blip"]

@app.route("/generate_domain_knowledge", methods=["POST"])
def generate_domain_knowledge():
    try:
        # Parse the incoming request
        data = request.json
        category_name = data.get("category_name")
        category_description = data.get("category_description")

        if not category_name or not category_description:
            return jsonify({"error": "Both category_name and category_description are required"}), 400

        # OpenAI API Call
        client = OpenAI()
        response = client.chat.completions.create(
            model="gpt-4o",
            messages=[
                {"role": "system", "content": "You are an assistant for generating domain knowledge."},
                {"role": "user", "content": f"""Generate comprehensive domain knowledge for a specified category.

                    - Input: 
                    - **Category Name**: {category_name}.
                    - **Category Description**: {category_description}.

                    - Objective: Develop a thorough and structured piece of domain knowledge that covers important aspects related to the specified category.

                    # Steps

                    1. **Understand the Category**: Review and comprehend the provided name and description to get an overview of the main themes.
                    2. **Research**: Gather information from authoritative sources related to the category including history, key concepts, significant figures, and recent developments.
                    3. **Organize Information**: Structure the information logically, covering all aspects mentioned in the description.
                    4. **Synthesize**: Combine the research into a coherent summary that effectively communicates the gathered domain knowledge.

                    # Output Format

                    The output should be a structured document consisting of sections like Introduction, History, Key Concepts, Notable Figures, Current Trends, and Conclusion. Aim for a coherent summary, approximately 500-1000 words in length, depending on the complexity of the category.

                    # Examples

                    ### Example 1

                    **Input:**
                    - **Category Name**: Renewable Energy
                    - **Category Description**: The development and utilization of energy from renewable resources, including solar, wind, hydro, and biomass. Important aspects include technology advancements, policy impacts, and environmental benefits.

                    **Output:**
                    1. **Introduction**: Overview of renewable energy and its significance.
                    2. **History**: Evolution of renewable energy technologies and policies.
                    3. **Key Concepts**: Detailed explanation of different renewable energy types.
                    4. **Notable Figures**: Key personalities in the field.
                    5. **Current Trends**: Recent advancements and market trends.
                    6. **Conclusion**: Summary of the potential and challenges of renewable energy.

                    ### Example 2

                    **Input:**
                    - **Category Name**: Artificial Intelligence
                    - **Category Description**: The field of computer science focusing on creating systems capable of performing tasks that require human intelligence, such as learning, reasoning, problem-solving, and language understanding.

                    **Output:**
                    1. **Introduction**: Explanation of artificial intelligence and its importance.
                    2. **History**: Milestones and evolutions in AI research.
                    3. **Key Concepts**: Overview of machine learning, neural networks, and other AI technologies.
                    4. **Notable Figures**: Influential researchers and developers in AI.
                    5. **Current Trends**: Latest innovations and ethical considerations.
                    6. **Conclusion**: Future outlook and potential societal impacts of AI. 

                    # Notes

                    - Ensure factual accuracy and rely on reputable sources.
                    - Adapt the amount of detail in each section to match the importance and complexity of the information."""}
            ])
        # response = openai.ChatCompletion.create(
        #     model="gpt-4",
        #     messages=[
        #         {"role": "system", "content": "You are an assistant for generating domain knowledge."},
        #         {"role": "user", "content": f"Generate domain knowledge for category: {category_name}.\nDescription: {category_description}"}
        #     ],
        #     max_tokens=500,
        #     temperature=0.7
        # )

        # Extract response
        print(response)
        generated_knowledge = response.choices[0].message.content.strip()

        return jsonify({"generated_domain_knowledge": generated_knowledge}), 200

    except Exception as e:
        # Fallback for any unexpected error
        return jsonify({"error": f"Internal server error: {str(e)}"}), 500





@app.route('/generate_image_description', methods=['POST'])
def generate_image_description():
    print("yayayayay")
    # try:
    # Parse the incoming JSON payload
    image_file = request.files.get("image")
    if not image_file:
        return jsonify({"error": "Image file is missing"}), 400

    # Read the image as binary data
    image_data = image_file.read()

    # print(request.json)
    json_data = request.form.to_dict()
    print(json_data)
    # data = json.loads(request.form.get("json", "{}"))
    # print(data)
    print("point3")

    # Extract required fields from the payload
    model = request.form.get("model", "llama3.2-vision:11b")
    domain_knowledge = request.form.get("domain_knowledge", "")
    temperature = float(request.form.get("temperature", 0.6))
    num_ctx = int(request.form.get("num_ctx", 2048))
    top_p = float(request.form.get("top_p", 0.8))
    top_k = int(request.form.get("top_k", 30))
    repeat_penalty = float(request.form.get("repeat_penalty", 1.2))
    print("point3")
    print(model, domain_knowledge, temperature)

    # Ensure all required fields are provided
    # if not image_base64:
    #     return jsonify({"error": "Image data is missing"}), 400

    # image = Image.open(io.BytesIO(image_data))
    image_base64 = base64.b64encode(image_data).decode('utf-8')



    # Prepare the prompt for llama3.2vision
    prompt = f"Domain Knowledge(Ignore domain knowledge if empty):\n{domain_knowledge}\nGenerate a description for the given image."

    # Call the Ollama API
    
    json_schema = {
        "type": "object",
        "properties": {
            "description": {"type":"string"},
        },
        "required": ["description"]
    }

    ollama_payload = {
        "model": model,
        "messages": [
            {
                "role": "user",
                "content": prompt,
                "images": [image_base64]
            }
        ],
        "options": {
            "temperature": temperature,
            "num_ctx": num_ctx,
            "top_p": top_p,
            "top_k": top_k,
            "repeat_penalty": repeat_penalty
        },
        "stream": False,
        # "format": json_schema
    }
    print("point5")

    headers = {"Content-Type": "application/json"}
    ollama_response = requests.post(OLLAMA_URL, json=ollama_payload)
    print("point6")

    # Check the response from Ollama
    print(ollama_payload)
    print(ollama_response.status_code)
    if ollama_response.status_code == 200:
        print("point7")
        response_data = ollama_response.json()
        print(response_data)
        message_content = response_data.get("message", {}).get("content", {})
        print("point7")
        print(message_content)
        # structured_data = json.loads(message_content)
        # print("point7")
        # print("-------------------------------------")
        # print(structured_data)
        # description = structured_data.get("description", "Unknown")

        # description = response_data.get("text", "No description generated.")

        contextual_knowledge = generate_context_knowledge(message_content)
        prompt = f"Domain Knowledge(Ignore domain knowledge if empty):\n{domain_knowledge}\n, Contextual knowledge: {contextual_knowledge} Generate a description for the given image using the domain and contextual knowledge in natural readable language."
        ollama_payload = {
            "model": model,
            "messages": [
                {
                    "role": "user",
                    "content": prompt,
                    "images": [image_base64]
                }
            ],
            "options": {
                "temperature": temperature,
                "num_ctx": num_ctx,
                "top_p": top_p,
                "top_k": top_k,
                "repeat_penalty": repeat_penalty
            },
            "stream": False,
            # "format": json_schema
        }
        headers = {"Content-Type": "application/json"}
        ollama_response = requests.post(OLLAMA_URL, json=ollama_payload)
        if ollama_response.status_code == 200:
            print("point7")
            response_data = ollama_response.json()
            print(response_data)
            message_content = response_data.get("message", {}).get("content", {})
            print("point7")
            print(message_content)

            return jsonify({"description": message_content}), 200
    else:
        return jsonify({
            "error": f"Ollama API call failed with status code {ollama_response.status_code}",
            "details": ollama_response.text
        }), ollama_response.status_code

    # except Exception as e:
    #     return jsonify({"error": f"An error occurred: {str(e)}"}), 500




def generate_context_knowledge(description):
    try:
        # OpenAI API Call
        abc = "asausahj"
        client = OpenAI()
        response = client.chat.completions.create(
            model="gpt-4o",
            messages=[
                {"role": "system", "content": "You are an assistant for generating conextual knowledge."},
                {"role": "user", "content": content}])
                
                
                
                
        content = """Basic Description of Image:""" + abc +"""
            Task Objective:

            Based on the above description of the image, create a structured context to refine and generate a detailed, domain-specific description of the objects in the image. Give the context in {} json format without any extra information. Follow these steps:

            Object Identification: Identify all key objects and elements mentioned in the description, grouping them logically by category (e.g., "natural elements," "man-made objects," "animals," etc.).

            Attributes & Features: For each identified object, list:

            Relevant physical attributes (e.g., color, shape, size).
            Functional characteristics or possible uses (if applicable).
            Cultural, historical, or contextual significance (if applicable).
            Domain Relevance: Provide domain-specific insights or information about each object. For instance:

            If the object is a type of plant, include botanical details.
            If the object is a vehicle, include engineering or usage-related details.
            If it's a landmark, include historical and geographical facts.
            Web-Enhanced Insights: Search the internet for any unique, up-to-date, or specific information related to the identified objects or themes in the image. Include only verified and relevant data, avoiding unrelated or overly general facts.

            Output Format: Structure the context in a systematic and concise format like this:

            Category: [e.g., Natural Elements]
            Object: [e.g., Tree]
            Attributes: [Green foliage, tall, deciduous]
            Function/Use: [Provides shade, habitat for birds]
            Domain-Specific Insight: [Scientific name, ecological role]
            Repeat for other objects/categories.
            Final Output Example:

            plaintext
            Copy code
            **Category:** Man-made Objects
            - **Object:** Bridge
            - **Attributes:** Arched, metallic structure, spanning a river
            - **Function/Use:** Enables transportation across the river
            - **Domain-Specific Insight:** Designed using a suspension system for durability; iconic in local architecture.

            **Category:** Animals
            - **Object:** Horse
            - **Attributes:** Brown, muscular build, medium-sized
            - **Function/Use:** Traditionally used in agriculture and transportation
            - **Domain-Specific Insight:** Known for endurance; popular in equestrian sports.
            Additional Notes: Ensure that the information provided is generalizable and avoids random or extraneous details. The output should be comprehensive yet focused, aiding in creating a more detailed and meaningful description of the image."""
            
                            # response = openai.ChatCompletion.create(
        #     model="gpt-4",
        #     messages=[
        #         {"role": "system", "content": "You are an assistant for generating domain knowledge."},
        #         {"role": "user", "content": f"Generate domain knowledge for category: {category_name}.\nDescription: {category_description}"}
        #     ],
        #     max_tokens=500,
        #     temperature=0.7
        # )

        # Extract response
        print(response)
        generated_knowledge = response.choices[0].message.content.strip()
        return generated_knowledge


    except Exception as e:
        # Fallback for any unexpected error
        return ""



if __name__ == '__main__':
    app.run(debug=True)


# curl http://127.0.0.1:12345/api/chat -d '{
#   "model": "llama3.2-vision:11b",
#   "messages": [
#     {
#       "role": "user",
#       "content": "Describe the image."
#     }
#   ]
# }'

import streamlit as st
from openai import OpenAI
import requests
import base64
from PIL import Image
import json




# clicked = st.button("Click Me")

def fetch_models():
    try:
        response = requests.get("https://af07-76-126-187-116.ngrok-free.app/models")
        response.raise_for_status()
        st.session_state.models = response.json()

        # Initialize form keys for each model
        for model in st.session_state.models:
            if model + "_" + st.session_state.selected_category + "_" + "temperature_slider" not in st.session_state.form:
                st.session_state.form[model + "_" + st.session_state.selected_category + "_" + "temperature_slider"] = 0.5
            if model + "_" + st.session_state.selected_category + "_" + "num_ctx_slider" not in st.session_state.form:
                st.session_state.form[model + "_" + st.session_state.selected_category + "_" + "num_ctx_slider"] = 2048
            if model + "_" + st.session_state.selected_category + "_" + "top_p_slider" not in st.session_state.form:
                st.session_state.form[model + "_" + st.session_state.selected_category + "_" + "top_p_slider"] = 0.8
            if model + "_" + st.session_state.selected_category + "_" + "top_k_slider" not in st.session_state.form:
                st.session_state.form[model + "_" + st.session_state.selected_category + "_" + "top_k_slider"] = 30
            if model + "_" + st.session_state.selected_category + "_" + "repeat_penaulty_slider" not in st.session_state.form:
                st.session_state.form[model + "_" + st.session_state.selected_category + "_" + "repeat_penaulty_slider"] = 1.2
    except Exception as e:
        st.error(f"Failed to fetch models: {e}")
        st.session_state.models = []

def update_domain_knowledge(category_name, category_description):

    api_url = "https://af07-76-126-187-116.ngrok-free.app/generate_domain_knowledge"
    
    # Prepare payload
    payload = {
        "category_name": category_name,
        "category_description": category_description
    }
    try:
        # Make the API call
        response = requests.post(api_url, json=payload)
        
        # Check response status
        if response.status_code == 200:
            # Extract the generated domain knowledge
            generated_knowledge = response.json().get("generated_domain_knowledge", "")
            if generated_knowledge:
                # Update the associated_domain_knowledge field dynamically
                st.session_state["domain_knowledge_input"] = generated_knowledge
            else:
                st.warning("No domain knowledge returned from the API.")
        else:
            st.error(f"Error: {response.status_code} - {response.text}")
    except Exception as e:
        st.error(f"API call failed: {e}")
    # try:
    #     response = requests.post(api_url, json=payload)
    #     if response.status_code == 200:
    #         generated_knowledge = response.json().get("generated_domain_knowledge", "")
    #         if generated_knowledge:
    #             st.session_state["domain_knowledge_input"] = generated_knowledge
    #         else:
    #             st.warning("No domain knowledge returned from the API.")
    #     else:
    #         st.error(f"Error: {response.status_code} - {response.text}")
    # except Exception as e:
    #     st.error(f"API call failed: {e}")

@st.dialog("Change Settings")
def setting():
    with st.form("model_form"):
        st.write(f"Tuning parameters for {st.session_state.selected_model}")

        # Fetch current slider and checkbox values
        temperature_slider_val = st.slider(
            "Temperature slider",
            0.0, 1.5,
            value=float(st.session_state.form[st.session_state.selected_model + "_" + st.session_state.selected_category + "_" + "temperature_slider"]),
            step=0.1,  # Add a step parameter of type float
            key=st.session_state.selected_model + "_" + st.session_state.selected_category + "_" + "temperature_slider_key",
        )
        num_ctx_slider_val = st.slider(
            "Context Length slider",
            512, 4096,
            value=int(st.session_state.form[st.session_state.selected_model + "_" + st.session_state.selected_category + "_" + "num_ctx_slider"]),
            step=2,
            key=st.session_state.selected_model + "_" + st.session_state.selected_category + "_" + "num_ctx_slider_key",
        )
        top_p_slider_val = st.slider(
            "Top-p slider",
            0.0, 1.0,
            value=float(st.session_state.form[st.session_state.selected_model + "_" + st.session_state.selected_category + "_" + "top_p_slider"]),
            step=0.01,
            key=st.session_state.selected_model + "_" + st.session_state.selected_category + "_" + "top_p_slider_key",
        )
        top_k_slider_val = st.slider(
            "Top-k slider",
            1, 100,
            value=int(st.session_state.form[st.session_state.selected_model + "_" + st.session_state.selected_category + "_" + "top_k_slider"]),
            step=1,
            key=st.session_state.selected_model + "_" + st.session_state.selected_category + "_" + "top_k_slider_key",
        )
        repeat_penaulty_slider_val = st.slider(
            "Repeat Penaulty slider",
            1.0, 2.0,
            value=float(st.session_state.form[st.session_state.selected_model + "_" + st.session_state.selected_category + "_" + "repeat_penaulty_slider"]),
            step = 0.01,
            key=st.session_state.selected_model + "_" + st.session_state.selected_category + "_" + "repeat_penaulty_slider_key",
        )
        

        # Form submission
        submitted = st.form_submit_button("Submit")
        if submitted:
            st.session_state.form[st.session_state.selected_model + "_" + st.session_state.selected_category + "_" + "temperature_slider"] = temperature_slider_val
            st.session_state.form[st.session_state.selected_model + "_" + st.session_state.selected_category + "_" + "num_ctx_slider"] = num_ctx_slider_val
            st.session_state.form[st.session_state.selected_model + "_" + st.session_state.selected_category + "_" + "top_p_slider"] = top_p_slider_val
            st.session_state.form[st.session_state.selected_model + "_" + st.session_state.selected_category + "_" + "top_k_slider"] = top_k_slider_val
            st.session_state.form[st.session_state.selected_model + "_" + st.session_state.selected_category + "_" + "repeat_penaulty_slider"] = repeat_penaulty_slider_val
            st.success(f"Updated {st.session_state.selected_model} settings.")
            st.rerun()


@st.dialog("Create Category")
def category():
    with st.form("category_form"):

        # Fetch current slider and checkbox values
        category_name = st.text_input("Category Name", type="default")
        category_description = st.text_area("Category description")
        # associated_domain_knowledge = st.text_area(
        #     "Domain Knowledge", 
        #     value=st.session_state["domain_knowledge_input"], 
        #     key="domain_knowledge_input"
        # )
        generate_domain_knowledge = st.form_submit_button("Generate Domain Knowledge")
        if generate_domain_knowledge:
            if category_name and category_description:
                update_domain_knowledge(category_name, category_description)
                associated_domain_knowledge = st.text_area(
                    "Domain Knowledge", 
                    value=st.session_state["domain_knowledge_input"], 
                    key="domain_knowledge_input"
                )
                st.session_state.gen_domain_knowledge = associated_domain_knowledge
            else:
                st.warning("Please fill out both Category Name and Description.")

        # Form submission
        submitted = st.form_submit_button("Submit")
        if submitted:
            # # Update session state with the form values
            # st.session_state.form[st.session_state.selected_model + "_slider"] = slider_val
            # st.session_state.form[st.session_state.selected_model + "_checkbox"] = checkbox_val
            st.session_state.categories.insert(-1,category_name)
            st.session_state.category_properties[category_name] = {}
            st.session_state.category_properties[category_name]["category_name"] = category_name
            st.session_state.category_properties[category_name]["category_description"] = category_description
            # if 'associated_domain_knowledge' in locals() or 'associated_domain_knowledge' in globals():
            #     if associated_domain_knowledge:  # Ensure it's not empty or None
            st.session_state.category_properties[category_name]["associated_domain_knowledge"] = st.session_state.gen_domain_knowledge
            st.session_state.selected_category = category_name
            st.session_state.form[st.session_state.selected_model + "_" + st.session_state.selected_category + "_" + "temperature_slider"] = 0.5
            st.session_state.form[st.session_state.selected_model + "_" + st.session_state.selected_category + "_" + "num_ctx_slider"] = 2048
            st.session_state.form[st.session_state.selected_model + "_" + st.session_state.selected_category + "_" + "top_p_slider"] = 0.8
            st.session_state.form[st.session_state.selected_model + "_" + st.session_state.selected_category + "_" + "top_k_slider"] = 30
            st.session_state.form[st.session_state.selected_model + "_" + st.session_state.selected_category + "_" + "repeat_penaulty_slider"] = 1.2
            st.success(f"Updated {st.session_state.selected_model} settings.")
            st.rerun()


def encode_image_to_base64(image_bytes):
    # Encode the image bytes to Base64
    base64_encoded = base64.b64encode(image_bytes).decode('utf-8')
    return base64_encoded


if "models" not in st.session_state:
    st.session_state.models = None

# Initialize session state
if "form" not in st.session_state:
    st.session_state.form = {}
if "selected_model" not in st.session_state:
    st.session_state.selected_model = "default_model"

# Ensure the selected model has keys in the form
if st.session_state.selected_model + "_slider" not in st.session_state.form:
    st.session_state.form[st.session_state.selected_model + "_slider"] = 0
if st.session_state.selected_model + "_checkbox" not in st.session_state.form:
    st.session_state.form[st.session_state.selected_model + "_checkbox"] = False

# Initialize session state for domain knowledge
if "domain_knowledge_input" not in st.session_state:
    st.session_state["domain_knowledge_input"] = ""  # Default value

if "categories" not in st.session_state:
    st.session_state.categories = ["default", "New Category"]

if "selected_category" not in st.session_state:
    st.session_state.selected_category = "default"  # Set default selection

if "category_properties" not in st.session_state:
    st.session_state.category_properties = {"default":{"category_name":"default", "category_description":"default",}}  # Set default selection




# # st.session_state.models = ["abc","def","ghi"]
# if "form" not in st.session_state:
#     st.session_state.form = {st.session_state.selected_model+"_slider": 0, st.session_state.selected_model+"_checkbox": False}
# st.write(st.session_state.form[st.session_state.selected_model + "_slider"])
# if "vote" not in st.session_state:
fetch_models()

st.title("📄 Image Description Generator")
st.write(
    "Upload the image below and the selected model will generate a description for it."
)

col1, col2, col3 = st.columns([3, 1, 1])
with col1:
    if st.session_state.models:
        st.session_state.selected_model = st.selectbox(
            "Select the model you want to use:",
            st.session_state.models,
        )
    else:
        st.write("No models available.")

with col2:
    st.session_state.selected_category = st.selectbox(
            "Category:",
            st.session_state.categories,
            index=st.session_state.categories.index(st.session_state.selected_category),
        )
    if st.session_state.selected_category == "New Category":
        category()

with col3:
    st.markdown("<br>", unsafe_allow_html=True)
    st.button("Settings", on_click=setting)


# st.session_state.selected_model = st.selectbox(
#     "Select the model you want to use:",
#     (st.session_state.models),
# )
# st.button("Settings", on_click=setting)

# else:
# st.write(
#     f"Setting set, {st.session_state.selected_model + '_slider'} {st.session_state.form[st.session_state.selected_model + '_slider']} "
#     f"checkbox {st.session_state.form[st.session_state.selected_model + '_checkbox']}"
# )

# st.write(st.session_state.form)
# with st.form("my_form"):
#     st.write("Inside the form")
#     slider_val = st.slider("Form slider")
#     checkbox_val = st.checkbox("Form checkbox")

#     # Every form must have a submit button.
#     submitted = st.form_submit_button("Submit")
#     if submitted:
#         st.write("slider", slider_val, "checkbox", checkbox_val)
# st.write("Outside the form")
# Show title and description.



# Ask user for their OpenAI API key via `st.text_input`.
# Alternatively, you can store the API key in `./.streamlit/secrets.toml` and access it
# via `st.secrets`, see https://docs.streamlit.io/develop/concepts/connections/secrets-management
# openai_api_key = st.text_input("OpenAI API Key", type="password")
# if not openai_api_key:
#     st.info("Please add your OpenAI API key to continue.", icon="🗝️")
# else:

#     # Create an OpenAI client.
#     client = OpenAI(api_key=openai_api_key)

# Let the user upload a file via `st.file_uploader`.
uploaded_file = st.file_uploader(
    "Upload a document (.jpg, .jpeg or .png)", type=("jpg", "png", "jpeg")
)

generate_description_button = st.button("Generate Description")
if generate_description_button and uploaded_file:
    image_bytes = uploaded_file.read()
    image_base64 = encode_image_to_base64(image_bytes)
    st.image(uploaded_file, caption="Uploaded Image", use_container_width=True)
    # st.text("Base64 Encoded Image:")
    # st.text(image_base64)

    selected_model = st.session_state.selected_model
    selected_category = st.session_state.selected_category
    domain_knowledge = st.session_state.category_properties.get(selected_category, {}).get(
        "associated_domain_knowledge", ""
    )
    # st.write("Domain knowledge",domain_knowledge)
    # Fetch slider values from session state
    temperature = st.session_state.form.get(
        f"{selected_model}_{selected_category}_temperature_slider", 0.5
    )
    num_ctx = st.session_state.form.get(
        f"{selected_model}_{selected_category}_num_ctx_slider", 2048
    )
    top_p = st.session_state.form.get(
        f"{selected_model}_{selected_category}_top_p_slider", 0.8
    )
    top_k = st.session_state.form.get(
        f"{selected_model}_{selected_category}_top_k_slider", 30
    )
    repeat_penalty = st.session_state.form.get(
        f"{selected_model}_{selected_category}_repeat_penaulty_slider", 1.2
    )
    # Prepare payload for API call
    payload = {
        "model": selected_model,
        "domain_knowledge": domain_knowledge,
        "temperature": temperature,
        "num_ctx": num_ctx,
        "top_p": top_p,
        "top_k": top_k,
        "repeat_penalty": repeat_penalty,
    }
    files = {"image": uploaded_file}
    netlify_url = "https://af07-76-126-187-116.ngrok-free.app/generate_image_description"
    try:
        # response = requests.post(netlify_url, files={"json": (None, json.dumps(payload), "application/json"), "file_key": uploaded_file})
        response = requests.post(netlify_url, data=payload, files=files)
        response.raise_for_status()  # Raise error for bad status codes

        # Parse and display the response
        generated_description = response.json().get("description", "No description generated.")
        st.success("Generated Description:")
        st.text(generated_description)
    except Exception as e:
        st.error(f"Failed to generate image description: {e}")


# # Ask the user for a question via `st.text_area`.
# question = st.text_area(
#     "Now ask a question about the document!",
#     placeholder="Can you give me a short summary?",
#     disabled=not uploaded_file,
# )

# if uploaded_file and question:

#     # Process the uploaded file and question.
#     document = uploaded_file.read().decode()
#     messages = [
#         {
#             "role": "user",
#             "content": f"Here's a document: {document} \n\n---\n\n {question}",
#         }
#     ]

    # Generate an answer using the OpenAI API.
    # stream = client.chat.completions.create(
    #     model="gpt-3.5-turbo",
    #     messages=messages,
    #     stream=True,
    # )

    # Stream the response to the app using `st.write_stream`.
    # st.write_stream(stream)

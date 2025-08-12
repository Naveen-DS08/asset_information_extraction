import streamlit as st 
import json 
from extractor import extract_asset_info 

# Set page config 
st.set_page_config(
    page_title="Asset Information Extractor🔎", 
    layout = "centered", 
    initial_sidebar_state="expanded"
)
st.title("Asset Information Extractor🔍")
st.markdown("Enter asset details to search for and extract structured information.")

# Dictionary to map user-friendly names to Groq model names
GROQ_MODELS = {
    "Llama 3 8B": "llama3-8b-8192",
    "Llama 3 70B": "llama3-70b-8192",
    "Gemma 7B": "gemma-7b-it",
    "Mixtral 8x7B": "mixtral-8x7b-32768"
}

# Setup sidebar for api and model configuration  
st.sidebar.header("Configuration")
groq_api_key = st.sidebar.text_input(
    "Groq API Key",
    type="password",
    help="You can find your API key on the Groq Console."
)

selected_model_name = st.sidebar.selectbox(
    "Select LLM Model",
    list(GROQ_MODELS.keys()),
    help="Choose the large language model to use for extraction."
)

# Form for asset details 
with st.form("Asset Input Form"):
    st.header("Asset Details")
    model_number = st.text_input(
        "Modle Number",
        placeholder="eg., MRN85HD",
        help= "The specific model number of the asset"
    )
    asset_classification_name = st.text_input(
        "Asset Classification",
        placeholder="e.g., Generator (Marine)",
        help="The general classification of the asset.",
    )
    
    # Optional fields to improve search
    manufacturer = st.text_input(
        "Manufacturer (Optional)",
        placeholder="e.g., Cummins",
        help="Providing the manufacturer can improve search accuracy."
    )

    submit_button = st.form_submit_button("Extract Information")

# Handling after form submission 
if submit_button:
    if not groq_api_key:
        st.error("Please provide your Groq API key")
    elif not model_number or not asset_classification_name:
        st.error("Please provide both a Model Number and an Asset classification name")
    else:
        with st.spinner("Searching and Extraction Information..."):
            input_data = {
                "model_number": model_number,
                "asset_classification_name": asset_classification_name,
                "manufacturer": manufacturer  
            }
            try:
                # get the model name from user 
                model_to_use = GROQ_MODELS[selected_model_name]

                # call the function for information extraction 
                result_json = extract_asset_info(
                    input_data= input_data,
                    groq_api_key=groq_api_key,
                    model_to_use=model_to_use
                )

                # Display the results 
                st.subheader("Extraction Result")
                st.success("Information extracted successfully!")

                st.json(result_json)

                # Display the parsed information in a more readable format
                st.subheader("Parsed Details")
                st.write(f"**Asset Classification:** {result_json.get('asset_classification', 'N/A')}")
                st.write(f"**Manufacturer:** {result_json.get('manufacturer', 'N/A')}")
                st.write(f"**Model Number:** {result_json.get('model_number', 'N/A')}")
                st.write(f"**Product Line:** {result_json.get('product_line', 'N/A')}")
                st.write(f"**Summary:** {result_json.get('summary', 'N/A')}")

            except Exception as e:
                st.error(f"An unexpected error occurred: {e}")
                st.info("Please check your Groq API key and model selection.")



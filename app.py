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
    "Llama 3 8B": "llama-3.1-8b-instant",
    "Llama 3 70B": "llama-3.3-70b-versatile",
    "Gemma 2 9B": "gemma2-9b-it",
    "Qwen": "qwen/qwen3-32b"
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

# Input method selection 
input_method = st.radio(
    "Choose Input method",
    options = ["Form input", "JSON input"]
)

# Form for asset details 
with st.form("Asset Input Form"):
    st.header("Asset Details")

    # Check for the input method
    if input_method == "Form input":
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
        input_json_text = None  # Clear JSON text if form is used
    else:
        # use text area for JSON input with the example 
        example_json = json.dumps(
            {
                "model_number": 'MRN85HD',
                "asset_classification_name": "Generator (Marine)",
                "Manufacturer": ""
            }, indent=2
        )
        input_json_text = st.text_area(
            "JSON input",
            value= example_json,
            height = 200,
            help = "Paste JSON object with 'Model Number', 'asset_classification_name' and optional 'manufacturer'. "
        )
        model_number = None
        asset_classification_name = None
        manufacturer = None

    submit_button = st.form_submit_button("Extract Information")

# Handling after form submission 
if submit_button:
    if not groq_api_key:
        st.error("Please provide your Groq API key")
    else:
        # Determine the input data based on the selected method
        input_data = {}
        if input_method == "Form input":
            if not model_number or not asset_classification_name:
                st.error("Please provide both a Model Number and an Asset Classification.")
                st.stop()
            input_data = {
                "model_number": model_number,
                "asset_classification_name": asset_classification_name,
                "manufacturer": manufacturer
            }
        else: # JSON Input
            try:
                # Parse the JSON input
                input_data = json.loads(input_json_text)
                if not input_data.get("model_number") or not input_data.get("asset_classification_name"):
                    st.error("The JSON object must contain 'model_number' and 'asset_classification_name' keys.")
                    st.stop()
            except json.JSONDecodeError:
                st.error("Invalid JSON format. Please check your input.")
                st.stop() 

        with st.spinner("Searching and Extraction Information..."):
            
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



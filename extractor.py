import os
from dotenv import load_dotenv
from langchain_groq import ChatGroq
from pydantic import BaseModel, Field 
from langchain_community.tools.ddg_search.tool import DuckDuckGoSearchRun
from langchain_community.utilities import DuckDuckGoSearchAPIWrapper
from langchain_core.prompts import ChatPromptTemplate 

# Load environmental variable
load_dotenv()
os.environ["GROQ_API_KEY"] = os.getenv("GROQ_API_KEY")

# Intilize the tools
search_api_wrapper = DuckDuckGoSearchAPIWrapper()
search_tool = DuckDuckGoSearchRun(api_wrapper=search_api_wrapper)

# Structure for an output
class ProductInfo(BaseModel):
    """Structured output for asset information."""
    asset_classification: str = Field(..., description="The type of asset, e.g., 'Marine Generator'")
    manufacturer: str = Field(..., description="The name of the product manufacturer, e.g., 'Cummins'")
    model_number: str = Field(..., description="The model number of the product, e.g., 'MRN85HD'")
    product_line: str = Field(..., description="The product line or brand, e.g., 'Onan'")
    summary: str = Field(..., description="A brief summary of the product") 

# prompt messages 
system_prompt = """
You are an expert at extracting structured product information.
Use the provided search results to identify the manufacturer, product line,
and a summary for the given asset. Your final output must be
a JSON object that adheres strictly to the provided schema.
"""

human_message = """
Extract information for the following asset:
Model Number: {model_number}
Asset Classification: {asset_classification_name}

Search Results:
{search_results}
"""

# Create the prompt template
prompt = ChatPromptTemplate.from_messages([
    ("system", system_prompt),
    ("human", human_message)
])


def extract_asset_info(input_data:dict, groq_api_key:str, model_to_use:str)-> dict:
    """
    Extracts structured asset information using a RAG pipeline.

    Args:
        input_data: A dictionary with 'model_number' and 'asset_classification_name'.
        groq_api_key: The API key for Groq.
        model_name: The name of the Groq model to use.

    Returns:
        A dictionary with the extracted and validated asset information.
    """
    retries = 0
    max_retries = 5
    # Initilize LLM
    llm = ChatGroq(
        model=model_to_use,
        temperature=0.2, 
        api_key= groq_api_key)
    
    # Bind the Pydantic model to the LLM to get structured output
    chain = prompt | llm.with_structured_output(ProductInfo)
    
    while retries < max_retries:
        try:
            # 1. Perform web search
            search_query = f"{input_data['model_number']} {input_data['asset_classification_name']}"
            search_results = search_tool.run(search_query)

            # 2. Invoke the LLM chain
            response = chain.invoke({
                "model_number": input_data["model_number"],
                "asset_classification_name": input_data["asset_classification_name"],
                "search_results": search_results
            })

            # If we get a valid response, return it
            return response.model_dump()

        except Exception as e:
            print(f"Error parsing response: {e}. Retrying... ({retries + 1}/5)")
            retries += 1
        
    # 3. Fallback mechanism if all retries fail
    print("Max retries exceeded. Returning fallback response.")

    return {
        "asset_classification": "Generator Emissions/UREA/DPF Systems",
        "model_number": input_data["model_number"],
        "manufacturer": "",
        "product_line": "",
        "summary": ""
    }

if __name__ == "__main__":
    extract_asset_info()
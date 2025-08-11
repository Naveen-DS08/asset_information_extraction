import os
from dotenv import load_dotenv
from langchain_groq import ChatGroq
from pydantic import BaseModel, Field 
from langchain_community.tools.ddg_search.tool import DuckDuckGoSearchRun
from ddgs import DDGS
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import SimpleJsonOutputParser

# Load environmental variable
load_dotenv()
os.environ["GROQ_API_KEY"] = os.getenv("GROQ_API_KEY")

# Initilize LLM
llm = ChatGroq(
    model="deepseek-r1-distill-llama-70b",
    temperature=0.2)
# # Intilize the tools
# search_tool = DuckDuckGoSearchRun()

# Structure for an output
class ProductInfo(BaseModel):
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

# Bind the Pydantic model to the LLM to get structured output
chain = prompt | llm.with_structured_output(ProductInfo)

def extract_asset_info(input_data):
    retries = 0
    while retries < 5:
        try:
            # 1. Perform web search
            search_query = f"{input_data['model_number']} {input_data['asset_classification_name']}"
            # --- DEBUGGING STEP 1: Print the search query ---
            print(f"Executing search query: {search_query}")
            search_results_list = []
            with DDGS() as ddgs:
                results = ddgs.text(keywords=search_query, max_results=5)
                for r in results:
                    search_results_list.append(f"Title: {r['title']}\nSnippet: {r['body']}\n")
            search_results = "\n".join(search_results_list)
            # --- DEBUGGING STEP 2: Print the search results ---
            print("--- SEARCH RESULTS ---")
            print(search_results)
            print("----------------------")

            # 2. Invoke the LLM chain
            response = chain.invoke({
                "model_number": input_data["model_number"],
                "asset_classification_name": input_data["asset_classification_name"],
                "search_results": search_results
            })

            # If we get a valid response, return it
            return response.model_dump_json()

        except Exception as e:
            print(f"Error parsing response. Retrying... ({retries + 1}/5)")
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
    extract_asset_info({
"model_number": "MRN85HD",
"asset_classification_name": "Generator (Marine)"
}
)

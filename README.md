# 📊 RAG Asset Information Extractor

This project is a Streamlit web application that uses a Retrieval-Augmented Generation (RAG) pipeline to extract structured information about assets from web search results. The system takes a product's model number and classification, performs an online search, and then uses a Large Language Model (LLM) to parse the search results and return a structured JSON output.

## ✨ Features

* **Flexible LLM Integration**: Uses the Groq API, allowing you to select from a variety of powerful models like Llama 3, Gemma, and Qwen.

* **Multiple Input Methods**: Supports both a simple form input and a direct JSON paste for asset details.

* **Robust Error Handling**: Implements a retry mechanism and a fallback response for failed extractions.

* **Structured Output**: Returns validated data in a clean JSON format, thanks to Pydantic models.


## 🛠️ Prerequisites

Before you begin, ensure you have the following installed:

* Python 3.8 or higher

* `uv` (Python package installer)

## 📦 Setup

1.  **Clone the repository or save the files**: Save the provided `extractor.py`, `app.py`, and `requirements.txt` files into a single project directory.

2.  **Install dependencies**: Open your terminal or command prompt, navigate to your project directory, and run the following command to install all required libraries:

    ```bash
    uv pip install -r requirements.txt
    ```

3.  **Get a Groq API Key**: Visit the [Groq Console](https://console.groq.com/keys) to create an API key. You will need this to use the LLM.

4.  **Run the application**: Launch the Streamlit application from your terminal with this command:

    ```bash
    streamlit run app.py
    ```

    This will open the application in your default web browser.

## ⚙️ Usage

1.  **Configure in the Sidebar**: Enter your **Groq API Key** and select your preferred **LLM Model** from the dropdown menu in the sidebar.

2.  **Choose Input Method**: Use the radio button to switch between `Form Input` and `JSON Input`.

    * **Form Input**: Fill in the `Model Number` and `Asset Classification` fields.

    * **JSON Input**: Paste a complete JSON object into the text area.

3.  **Submit**: Click the "Extract Information" button. The application will perform a search and display the extracted information in both raw JSON and a readable format.

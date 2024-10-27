# ![QuantIQ Logo](imgs/quantiq_logo_75x75.jpg) 
# QUANT-IQ
# A Quantitative Analysis Tool for Intelligent Financial Review

## About:
**QUANT-IQ** is a powerful tool for analyzing financial statements, using OpenAI and Streamlit to streamline document processing and generate insightful reports. Quant-IQ is a streamlined tool designed to evaluate companies by analyzing their financial statements and additional data. Utilizing advanced algorithms, Quant-IQ assesses key metrics such as revenue growth, profitability, profit growth, and liquidity to determine a company’s financial health and growth potential. Users can easily upload financial documents and spreadsheets, which Quant-IQ integrates into its evaluation framework. The intuitive interface generates comprehensive reports with summaries, financial snapshots, evidence-based analysis, and a scoring system based on a standardized rubric. Additionally, Quant-IQ creates tailored questions for CEOs to gain deeper insights into their business strategies. By automating the financial review process, Quant-IQ enhances efficiency and ensures consistent, informed decision-making for program administrators.

## Features:
- Upload and analyze financial documents (PDF, DOCX, or ZIP files).
- Prompt editor.
- Generate detailed reports in PDF format.
- Automatic moderation check using OpenAI.
- Zip multiple analysis reports for easy download.

## Installation:
1. Clone the repository:
   ```bash
   git clone https://github.com/sieverett/QuantIQ.git
   cd yourrepository
   ```
2. Install required dependencies:
   ```bash
   pip install -r requirements.txt
   ```

3. Set up environment variables:
   - Create a `.env` file in the root of your project:
     ```
     OPENAI_API_KEY=your_openai_api_key
     ```

4. Run the Streamlit app:
   ```bash
   streamlit run app.py
   ```

## Run local on Docker

1. In directory with Dockerfile, build image:
```bash
docker build -t quantiq-app .
```
2. Run docker container:
```bash
docker run -d -p 8501:8501 --name quantiq-app quantiq-app
```
3. Open in browser - `https:localhost:8501`

## Deploy to Azure

In vscode:
1. From `images` Push to `registries`
2. From `registries` create web app


## Usage:
- Upload financial documents (PDF, DOCX, ZIP).
- Click the **Analyze** button to generate reports.
- Download the analysis as a PDF or ZIP file.

This program, **QUANT-IQ**, is designed to help users analyze financial statements by leveraging the **OpenAI GPT** API and several core Python libraries to automate the analysis and generate reports.

## How it works:
1. **File Upload & Handling**: Users upload financial documents in various formats (PDF, DOCX, or ZIP). The program then processes these files, either individually or in bulk, and extracts their content for analysis.
   - **Library used**: `os`, `zipfile`, `docx`, `pandas`.

2. **AI-Powered Analysis**: The tool integrates with **OpenAI GPT** via its API to analyze the content of financial documents. It uses a moderation endpoint to ensure the uploaded content adheres to guidelines, then processes the documents to generate meaningful insights. Completions are returned as HTML.
   - **LLM used**: `OpenAI GPT-4o` (via the `openai` library).
   
3. **Report Generation**: Once the documents are analyzed, generating detailed reports converting HTML to PDF format with `pdfkit` support. The reports include financial insights extracted from the uploaded documents.
   - **Library used**: `pdfkit`.

4. **Streamlit Integration**: The app uses **Streamlit** to provide a user-friendly interface, allowing users to interact with the tool by uploading files, analyzing them, and downloading the results.
   - **Library used**: `streamlit`.

## Core Libraries:
- **OpenAI GPT**: Used to analyze financial statements and generate insightful textual content.
- **Streamlit**: A framework to create the user interface for uploading files and interacting with the tool.
- **pdfkit**: For generating PDF reports from HTML/Markdown content.
- **docx**: For handling DOCX file uploads and extracting data from them.
- **zipfile**: To handle zipped files and manage bulk document processing.

## Contributing:
1. Fork the repository.
2. Create a new branch (`git checkout -b feature/YourFeature`).
3. Commit your changes (`git commit -m 'Add YourFeature'`).
4. Push to the branch (`git push origin feature/YourFeature`).
5. Open a pull request.

## License:
This project is licensed under the MIT License.
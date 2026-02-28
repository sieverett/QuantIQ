# QUANT-IQ

A quantitative analysis tool for intelligent financial review.

![Python](https://img.shields.io/badge/Python-3776AB?style=for-the-badge&logo=python&logoColor=white)
![Streamlit](https://img.shields.io/badge/Streamlit-FF4B4B?style=for-the-badge&logo=streamlit&logoColor=white)
![OpenAI](https://img.shields.io/badge/OpenAI-412991?style=for-the-badge&logo=openai&logoColor=white)
![Docker](https://img.shields.io/badge/Docker-2496ED?style=for-the-badge&logo=docker&logoColor=white)

## About

QUANT-IQ analyzes financial statements using the OpenAI GPT API and presents results through a Streamlit web interface. Users upload financial documents in PDF, DOCX, or ZIP format, and the tool generates structured reports covering revenue growth, profitability, liquidity, and overall financial health. Reports are scored on a standardized rubric and exported as PDF.

## Features

- Upload and analyze financial documents in PDF, DOCX, CSV, XLSX, or ZIP format
- Bulk processing of multiple documents, individually or grouped by directory
- Two analysis modes: OpenAI Assistants API (file search) or Chat Completions (structured outputs)
- Editable analysis prompt with save, restore, and download support
- Automated PDF report generation with styled HTML output
- Downloadable ZIP archive of all analysis results
- Customizable logo for branded reports
- Deployable locally or via Docker

## Getting Started

### Prerequisites

- Python 3.10+
- An [OpenAI API key](https://platform.openai.com/api-keys)
- For Assistant mode: an [OpenAI Assistant ID](https://platform.openai.com/assistants/)
- `wkhtmltopdf` or WeasyPrint system dependencies (used for HTML-to-PDF conversion)

### Installation

```bash
git clone https://github.com/sieverett/QuantIQ.git
cd QuantIQ
pip install -r requirements.txt
```

### Configuration

Create a `.env` file in the project root:

```
OPENAI_API_KEY=your_openai_api_key
```

Or set the key through the Settings page in the app after launch.

### Run

```bash
streamlit run app.py
```

### Docker

```bash
docker build -t quantiq-app .
docker run -d -p 8501:8501 --name quantiq-app quantiq-app
```

Then open `http://localhost:8501` in your browser.

## Usage

1. Set your OpenAI API key (and optionally an Assistant ID) in the **Settings** tab.
2. Upload financial documents through the **Analyze** tab.
3. Click **Analyze** to generate reports.
4. Download individual reports or a ZIP archive of all results.

## Project Structure

```
QuantIQ/
├── app.py                  # Streamlit application entry point
├── components/             # UI components (sidebar, analyzer, settings, prompt editor)
├── quantiq/                # Core logic (analysis, reporting, file handling, logging)
├── prompts/                # Prompt templates and output format definitions
├── utils/                  # Session and auth utilities
├── styles/                 # Custom CSS
├── imgs/                   # Logo assets
├── templates/              # HTML report template
├── Dockerfile
└── requirements.txt
```

## License

This project is licensed under the MIT License.

# 🌿 Automated EFRAG VSME Data Extraction & XBRL Pipeline

An intelligent, end-to-end pipeline designed to bridge the gap between messy unstructured corporate sustainability disclosures (PDFs) and the strictly formatted **EFRAG Voluntary SME (VSME)** digital reporting standard.

By combining layout-aware document parsing, dynamic schema compilation across 800+ Excel named ranges, long-context LLM extraction, and conversational Human-in-the-Loop (HITL) resolution, this tool transforms PDF reports directly into validation-ready, XBRL-compliant digital files.

---

## 🏗️ Architecture & Pipeline Overview

```
                      +-----------------------------+
                      |   Source Unstructured PDF   |
                      +--------------+--------------+
                                     |
                                     v
                      +-----------------------------+
                      |     1. Parsing (Docling)    |
                      |   Native Markdown + Tables  |
                      +--------------+--------------+
                                     |
+--------------------------+         v              +---------------------------+
| EFRAG Blank Template     |---> [ 2. Dynamic ] <---| EFRAG Sample Knowledge    |
| (800+ Named Ranges via   |     [   Schema   ]     | Base (Few-shot formatting |
|  openpyxl)               |     [ & Examples ]     |  guidelines)              |
+--------------------------+         |              +---------------------------+
                                     v
                      +-----------------------------+
                      | 3. Full-Context Extraction  |
                      | (Single-pass long-context)  |
                      +--------------+--------------+
                                     |
                       [ Any missing/null data? ]
                               /            \
                       Yes    /              \   No
                             v                v
      +-----------------------------+   +-----------------------------+
      |  4. Conversational HITL     |   |   5. Safe Excel Injection   |
      |  Natural language copilot + |   |   (openpyxl -> Named Ranges)|
      |  Pydantic schema patching   |   +--------------+--------------+
      +--------------+--------------+                  |
                     |                                 |
                     +---------------------------------+
                                     |
                                     v
                      +-----------------------------+
                      |     6. XBRL Compliance      |
                      |  EFRAG CLI -> Inline XBRL   |
                      +-----------------------------+

```

---

## ⚡ Key Pipeline Stages

### 1. Structure-Aware Document Parsing (`Docling`)

Extracting ESG data requires understanding complex visual layouts. Using `Docling`, incoming PDF reports are converted into structured Markdown, preserving multi-row financial grids, dense metric tables, and nested sections without layout decay.

### 2. Dynamic Schema Generation & Few-Shot Prompting

* **Dynamic Schema via `openpyxl`:** Instead of hardcoding 800+ sustainability metrics, the system inspects the official blank template (`VSME-Digital-Template-1.3.0.xlsx`) at runtime, extracting all defined Named Ranges to synthesize an extraction schema dynamically.
* **Few-Shot Conditioning:** The official reference data (`VSME-Digital-Template-Sample-1.3.0.xlsx`) serves as an in-context knowledge base. The LLM references exact EFRAG syntactic conventions (date stamps, units, indicator codes, and scaling rules) to eliminate downstream syntax discrepancies.

### 3. Full-Context Structured Extraction

Rather than chunking documents and losing inter-table narrative context, the engine passes the complete parsed Markdown batch into a long-context LLM in a single pass. Native cross-attention simultaneously resolves cross-page dependencies, footnotes, and KPI tables directly into the dynamic schema.

### 4. Interactive Human-in-the-Loop (HITL) Copilot

When a non-negotiable metric is omitted or unavailable in the source text, the model flags the key as `null` rather than hallucinating:

* The system pings the user via an interactive copilot interface:
> *"I couldn't find the total water withdrawal data (Metric E3-1). Could you provide it in cubic meters ($m^3$)?"*


* The user responds in plain English (e.g., *"We consumed 14,200 m3 last fiscal year"*).
* A **Pydantic** validator parses the natural language input, casts it to the correct structural type, and safely patches the target schema.

### 5. Safe Excel Injection (`openpyxl`)

Once the validated data model is 100% complete:

* Target cells are targeted **exclusively via Named Ranges**, preventing coordinate drift across template updates or sheet adjustments.
* Existing formatting, calculation formulas, and validation metadata remain intact.

### 6. XBRL Compliance & Generation

The resulting spreadsheet is completely validated against EFRAG structural expectations and ready for immediate ingestion by EFRAG’s open-source XBRL CLI converter to output compliant **Inline XBRL (`.html` / `.xbrl`)** files.

---

## 📂 Project Structure

```bash
├── data/
│   ├── templates/
│   │   ├── VSME-Digital-Template-1.3.0.xlsx        # Target blank EFRAG template
│   │   └── VSME-Digital-Template-Sample-1.3.0.xlsx # Few-shot reference template
│   └── uploads/                                    # Input source PDF reports
├── src/
│   ├── parser/
│   │   └── docling_parser.py                       # PDF -> Markdown conversion
│   ├── schema/
│   │   ├── range_extractor.py                      # openpyxl Named Range reader
│   │   └── models.py                               # Dynamic Pydantic schema builder
│   ├── extractor/
│   │   ├── prompt_templates.py                     # Few-shot prompts & system specs
│   │   └── engine.py                               # Long-context LLM orchestrator
│   ├── copilot/
│   │   └── hitl_manager.py                         # Interactive question-answering & patcher
│   ├── writer/
│   │   └── excel_writer.py                         # openpyxl Named Range injector
│   └── xbrl/
│       └── converter.py                            # EFRAG XBRL conversion runner
├── tests/
├── .env.example
├── requirements.txt
└── main.py

```

---

## 🚀 Quickstart

### Prerequisites

* Python 3.10+
* Valid LLM API Key (e.g., OpenAI, Anthropic, or Google Vertex)
* EFRAG XBRL Conversion Tool (installed per official guidelines)

### Installation

1. **Clone the repository:**
```bash
git clone https://github.com/your-org/efrag-vsme-copilot.git
cd efrag-vsme-copilot

```


2. **Set up virtual environment:**
```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
pip install -r requirements.txt

```


3. **Configure Environment Variables:**
```bash
cp .env.example .env

```


Add your API keys and path to the EFRAG XBRL CLI binary in `.env`.

### Running the Pipeline

Run the pipeline on your target PDF disclosure:

```bash
python main.py --input data/uploads/annual_sustainability_report.pdf \
               --template data/templates/VSME-Digital-Template-1.3.0.xlsx \
               --output data/output/VSME_Report_Final.xlsx \
               --generate-xbrl

```

If missing values are detected, the CLI prompt will guide you through resolving flagged metrics step-by-step.

---

## 🛠️ Tech Stack

* **Document Ingestion:** [Docling](https://github.com/DS4SD/docling)
* **Spreadsheet Manipulation:** [openpyxl](https://openpyxl.readthedocs.io/)
* **Schema Validation:** [Pydantic v2](https://www.google.com/search?q=https://docs.pydantic.dev/)
* **LLM Engine:** Long-context models (Claude 3.5 Sonnet / Gemini 1.5 Pro / GPT-4o)
* **Reporting Standard:** [EFRAG VSME Standard](https://www.efrag.org/)

---

## 📄 License

Distributed under the Apache 2.0 License. See `LICENSE` for more information.

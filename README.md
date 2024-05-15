# PDF Content Extractor

## Overview

This Python script extracts key mathematical content from a specified PDF file and formats the output as rich Markdown with mathematical formulas in LaTeX. This tool is designed for users already familiar with the mathematical content, aiming to provide a concise and compact summary ideal for quick reference.

## Features

- Split large PDF files into manageable chunks.
- Skip initial pages that may not contain relevant content.
- Extract definitions, formulas, lemmas, and theorems.
- Output the extracted information in a structured Markdown format, with LaTeX for formulas.

## Requirements

- Python 3.8 or higher
- `openai`
- `PyPDF2`
- `tqdm`

## Setup

1. **Clone the repository:**

   ```bash
   git clone https://github.com/BertilBraun/Pdf-Extraction
   cd Pdf-Extraction
   ```

2. **Install the required packages:**

   ```bash
   pip install -r requirements.txt
   ```

3. **Settings setup:**

   Create a copy of the `example_settings.py` file and rename it to `settings.py`:

   ```bash
   cp settings_template.py settings.py
   ```

4. **API Key Configuration:**
   Store your OpenAI API key in the `settings.py` by replacing the placeholder in the `OPENAI_API_KEY` variable.

## Usage

1. **Prepare Your PDF:**
   Replace the placeholder in `PATH_TO_PDF` in the `settings.py` with the path to your PDF file.

2. **Configure Extraction Settings:**
   - `PAGES_PER_CHUNK`: Number of pages per chunk for processing.
   - `INITIAL_PAGES_TO_SKIP`: Number of initial pages to skip.

3. **Run the Script:**

   ```bash
   python main.py
   ```

## Output

The output will be generated in the `output` directory as a Markdown file, formatted with each entry separated by:

```markdown
{Identification Number} **{Name}**
{Intuitive short description}
Formal: {Formula or definition in LaTeX}
```

An Example of the output is shown below:

```markdown
1.1.6 **Epigraph**  
The epigraph consists of the graph of function f over X, including all points above it.  
Formal: $\text{epi}(f, X) = \{(x, \alpha) \in X \times \mathbb{R} \mid f(x) \leq \alpha\}$
```

## Contributing

Contributions are welcome! For major changes, please open an issue first to discuss what you would like to change.

# PDF Insurance Data - Exploratory Data Analysis (EDA) Notebook

## Overview

This repository now includes a comprehensive Jupyter Notebook (`PDF_Insurance_Data_EDA.ipynb`) that performs exploratory data analysis on insurance policy PDF documents.

## What's Included

### Main Deliverable
- **`PDF_Insurance_Data_EDA.ipynb`**: A complete, executable Jupyter Notebook containing:
  - PDF text extraction from all policy documents in `data/queplan_insurance/`
  - Data cleaning and preprocessing
  - Univariate and multivariate statistical analysis
  - 25+ professional visualizations
  - 5 complex testable data-driven questions with executable code answers
  - Summary statistics and insights

## Requirements

### Python Packages
The notebook requires the following packages (install using pip):

```bash
pip install jupyter pandas numpy matplotlib seaborn PyMuPDF
```

Or install all at once:
```bash
pip install jupyter pandas numpy matplotlib seaborn PyMuPDF
```

### Data Location
The notebook expects PDF files to be located in:
```
data/queplan_insurance/
```

Currently, the repository contains 9 insurance policy PDF files in this directory.

## How to Use the Notebook

### Option 1: Using Jupyter Notebook Interface

1. **Install Dependencies:**
   ```bash
   pip install jupyter pandas numpy matplotlib seaborn PyMuPDF
   ```

2. **Start Jupyter Notebook:**
   ```bash
   jupyter notebook
   ```

3. **Open the Notebook:**
   - Navigate to `PDF_Insurance_Data_EDA.ipynb` in the Jupyter interface
   - Run all cells sequentially (Cell → Run All) or execute cells individually

### Option 2: Using JupyterLab

1. **Install JupyterLab:**
   ```bash
   pip install jupyterlab
   ```

2. **Start JupyterLab:**
   ```bash
   jupyter lab
   ```

3. **Open and run the notebook** as described above

### Option 3: Command Line Execution

Execute the notebook from the command line and generate an output with results:

```bash
jupyter nbconvert --to notebook --execute PDF_Insurance_Data_EDA.ipynb --output PDF_Insurance_Data_EDA_executed.ipynb
```

This will create a new notebook with all cells executed and outputs included.

### Option 4: Convert to HTML Report

Generate an HTML report with all visualizations:

```bash
jupyter nbconvert --to html --execute PDF_Insurance_Data_EDA.ipynb
```

This creates `PDF_Insurance_Data_EDA.html` that can be opened in any web browser.

## Notebook Structure

The notebook is organized into the following sections:

### 1. Introduction
- Overview of the data source and analysis objectives
- Context about insurance policy documents

### 2. Library Imports and Setup
- Import of all required Python libraries
- Configuration of plotting styles and settings

### 3. Data Loading and PDF Text Extraction
- Functions to extract text from PDF files using PyMuPDF
- Extraction of policy metadata (policy numbers, types, article counts)
- Coverage keyword extraction (cobertura, reembolso, deducible, etc.)

### 4. Data Cleaning and Preprocessing
- Data quality checks
- Handling missing values
- Feature engineering (avg words per page, complexity scores, etc.)

### 5. Univariate Analysis
- Descriptive statistics for all numerical features
- Distribution plots (histograms with mean/median lines)
- Policy type frequency analysis
- Coverage keyword frequency analysis

### 6. Bivariate and Multivariate Analysis
- Correlation analysis with heatmap visualization
- Relationship exploration (page count vs word count, etc.)
- Grouped statistics by policy type
- Box plots comparing different policy types

### 7. Additional Visualizations and Insights
- Document complexity analysis
- Comparative visualizations across all policies
- Custom complexity scoring system

### 8. Testable Data-Driven Questions
Five complex questions with executable Python code answers:

1. **Average articles per policy type** - Statistical analysis of document structure
2. **Coverage term frequency vs document length** - Correlation analysis
3. **Deductible vs reimbursement mentions** - Comparative analysis
4. **Exclusion distribution by policy type** - Grouped statistical analysis
5. **Policy complexity vs legal term frequency** - Multivariate correlation study

### 9. Summary and Conclusions
- Key findings and insights
- Overall statistics
- Export of cleaned data to CSV

## Output Files

When executed, the notebook generates:

1. **`data/structure_data/eda_extracted_data.csv`**: 
   - Cleaned and processed data from all PDF files
   - Includes all extracted features and calculated metrics
   - Can be used for further analysis or machine learning

## Key Features

### Data Extraction
- Extracts text from 9 insurance policy PDF files
- Identifies policy numbers, types, and structural elements
- Counts occurrences of key insurance terminology

### Statistical Analysis
- Comprehensive descriptive statistics
- Correlation analysis between variables
- Grouped analysis by policy type
- Custom metrics (complexity scores, coverage density, etc.)

### Visualizations
The notebook includes 25+ professional visualizations:
- Histograms with statistical markers
- Bar charts and horizontal bar charts
- Pie charts
- Scatter plots with trend lines
- Correlation heatmaps
- Box plots for distribution comparison
- Multi-panel comparative visualizations

### Testable Questions
Each of the 5 complex questions includes:
- Clear problem statement
- Executable Python code
- Visualizations to illustrate findings
- Key insights and interpretations

## Analysis Highlights

The notebook analyzes insurance policy documents across multiple dimensions:

- **Document Characteristics**: Length, page count, word count, article count
- **Policy Types**: Catastrophic, Hospitalization, Health, Accident, Life, Dental, Complementary
- **Coverage Terms**: cobertura, reembolso, deducible, prima, exclusión, beneficio, asegurado, prestación
- **Complexity Metrics**: Custom scoring based on multiple factors
- **Relationships**: Correlations between different document features

## Notes

- All content in the notebook is in **English** as required
- The notebook is fully executable and self-contained
- No modifications were made to existing repository files (except .gitignore)
- The generated CSV output is excluded from git via .gitignore

## Troubleshooting

### Import Errors
If you encounter import errors, ensure all dependencies are installed:
```bash
pip install --upgrade jupyter pandas numpy matplotlib seaborn PyMuPDF
```

### PDF Extraction Issues
If PDF extraction fails:
- Verify that PDF files exist in `data/queplan_insurance/`
- Check file permissions
- Ensure PyMuPDF (fitz) is properly installed

### Visualization Issues
If plots don't display:
- For Jupyter Notebook, ensure you're using `%matplotlib inline` (already included)
- For command-line execution, visualizations will be saved in the output notebook

## Contributing

This notebook is part of the Insurance Policy Generation Chatbot project's data ingestion and analysis pipeline. For questions or contributions, refer to the main project README.

## License

This notebook follows the same license as the main project repository.

# Health Technology Assessment (HTA) Data Extraction and Analysis

Welcome to the Health Technology Assessment (HTA) Data Extraction and Analysis repository. This repository contains scripts and notebooks for extracting and processing data from various health technology assessment sources such as NICE (National Institute for Health and Care Excellence), SMC (Scottish Medicines Consortium). Additionally, it includes example of some other processing code for data extraction from pubmed.

## Table of Contents

- [Introduction](#introduction)
- [Installation](#installation)
- [Usage](#usage)
  - [Extracting Data from NICE](#extracting-data-from-nice)
  - [Extracting Data from SMC](#extracting-data-from-smc)
- [Addition Code](#addition-code)
  - [Example: Extracting Data from PubMed](#example-extracting-data-from-pubmed)
- [Files](#files)
- [License](#license)

## Introduction

Health Technology Assessment (HTA) is a systematic evaluation of properties, effects, and impacts of health technology. This repository provides tools for extracting and analyzing HTA data from various sources to support evidence-based decision-making in healthcare.

## Installation

1. Clone the repository:
   ```bash
   git clone https://github.com/yourusername/hta-data-extraction.git
   cd hta-data-extraction
   ```
2. Install the required packages::
    ```bash 
    pip install -r requirements.txt
    ```
## Usage

### Extracting Data from NICE
To extract data from NICE, use the `extract_links_NICE.py`, `extract_information_NICE.py`, `extract_reviews_NICE.py` and `OCR_NICE.py` scripts.

1. `extract_links_NICE.py` : To extract list of HTAs in NICE with TA number, URL, publication date, title. Output: CSV file.
2. `extract_information_NICE.py`: To extract metadata from each HTAs mentioned in above CSV file. Output: CSV file.
3. `extract_reviews_NICE.py` : To extract reviews (committee meeting) from HTAs. Output: CSV file.
4. `OCR_NICE.py` : To extract data from draft pdf of the HTAs. Output: CSV file.

    ```bash
    python extract_links_NICE.py
    python extract_information_NICE.py
    python extract_reviews_NICE.py
    python OCR_NICE.py
    ```
### Extracting Data from SMC
To extract data from SMC, use the `extract_links_SMC.py` and `extract_information_SMC.py` scripts.

1. `extract_links_SMC.py` : To extract list of HTAs in SMC with ID number, URL, publication date, title. Output: CSV file.
2. `extract_information_SMC.py`: To extract metadata from each HTAs mentioned in above CSV file. Output: CSV file.

    ```bash
    python extract_links_SMC.py
    python extract_information_SMC.py
    ```

## Addition Code
List of Addition codes that can be helpful.

### Example: Extracting Data from PubMed
For data extraction from PubMed, refer to the `pubmed_example.py` script. This script demonstrates how to query PubMed and process the results.

  ```bash
    python pubmed_example.py
  ```

## Files

- `extract_links_NICE.py`
- `extract_information_NICE.py`
- `extract_reviews_NICE.py`
- `OCR_NICE.py`
- `extract_links_SMC.py`
- `extract_information_SMC.py`
- `pubmed_example.py`
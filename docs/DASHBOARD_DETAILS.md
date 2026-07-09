# Dashboard Details

## Purpose

The dashboard mechanizes the ACR/CAPR/CPR review workflow for ATT copper decom planning. It helps identify active/working circuits, assigned/review pairs, defective pairs, spare pairs, and count makeup relationships before scoping a removal/step-down decision.

## Dashboard sections

### 1. Input

The user uploads ACR, CAPR, or CPR PDF reports. No sample data is loaded.

### 2. File summary

The dashboard extracts and displays:

- source file name
- report type
- report date
- work center
- employee ID
- cable ID
- pair low/high range
- PDF page count

### 3. Decision output

The tool produces one of three decisions:

- **HOLD / DO NOT DECOM YET**: working/active circuits are found.
- **ENGINEERING REVIEW REQUIRED**: assigned/review records are found, but no working records.
- **PROCEED CANDIDATE**: no working or assigned/review records are found in the uploaded files.

### 4. Pair status analysis

The dashboard reads pair-level CAPR/CPR blocks and extracts:

- pair number
- status
- CKID
- line pair status
- service type
- BP/color
- CAPR reference
- terminal
- address
- city/state
- defect type

### 5. ACR count makeup

The dashboard extracts count sections from ACR files:

- IN COUNT
- OUT COUNT
- QUALIFIED PAIRS

This helps show the upstream/downstream count makeup and routing context.

### 6. Output export

The output can be exported as:

- pair-level CSV
- ACR count CSV
- decision JSON

## Status grouping

| Raw status | Group |
|---|---|
| WKG | Working / active circuit |
| PCF, RCF, CF, 95DLC, D1GLC | Review / assigned |
| DEF | Defective |
| SPR | Spare |
| blank/unknown | Unknown / needs check |

## Why no sample data is included

This version is designed for production-style review of your actual uploaded reports. Sample data can mislead the result, so it has been removed. The dashboard starts empty until you upload your own PDFs.

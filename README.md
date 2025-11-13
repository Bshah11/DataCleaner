# ⚔️ TI4 Data Cleaner: RAG Source Data Hardening ⚔️

This repository serves as the **Data Engineering pipeline** for the **Twilight Imperium 4th Edition (TI4)** RAG (Retrieval-Augmented Generation) project.

Its sole purpose is to convert messy, vertically structured, and multi-line human-readable spreadsheet data (downloaded from Google Sheets or community sources) into clean, **granular, horizontally structured CSVs** that are optimized for vector embedding and large language model (LLM) consumption.

---

## 🎯 PROJECT GOAL (Data Engineering Scope)

To transform highly nested, asymmetric TI4 component information (Factions, Leaders, Units, Techs) into a normalized, predictable CSV format suitable for building a high-fidelity Vector Database.

## 📁 FOLDER STRUCTURE

```text
DataCleaner/
├── RawData/               # INPUT: Messy, vertically formatted CSVs and source PDFs.
├── StructuredData/        # OUTPUT: Clean, final CSVs ready for RAG indexing.
└── Scripts/               # EXECUTION: Python scripts for data transformation.
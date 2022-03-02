#!/bin/bash

echo "[PIPELINE] INGESTION STARTING..."
python3 ./pipeline/ingestion.py

echo "[PIPELINE] PROCESSING STARTING..."
python3 ./pipeline/processed.py 
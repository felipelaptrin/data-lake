#!/bin/bash

echo "[INFRA] - BUILDING DATA LAKE..."
cd ./artifacts/datalake && terraform init && terraform apply -auto-approve

echo "[INFRA] - CREATING NETWORK..."
cd ../network && terraform init && terraform apply -auto-approve

echo "[INFRA] - CREATING PERMISSIONS..."
cd ../permissions && terraform init && terraform apply -auto-approve

cd ../..
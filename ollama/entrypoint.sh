#!/bin/sh

set -e

echo "========================================"
echo "Starting Ollama..."
echo "========================================"

ollama serve &

SERVER_PID=$!

until ollama list >/dev/null 2>&1
do
    echo "Waiting for Ollama..."
    sleep 1
done

echo "Pulling model ${OLLAMA_MODEL}..."

ollama pull "${OLLAMA_MODEL}"

echo "========================================"
echo "Ollama is ready."
echo "========================================"

wait $SERVER_PID
#!/bin/bash

echo "Updating system..."
sudo apt update

echo "Installing required packages..."
sudo apt install -y build-essential cmake git python3 python3-pip ninja

echo "Creating python virtual environment..."
mkdir -p ~/Documents/urs_ws/llama_ws
cd ~/Documents/urs_ws/llama_ws
python3 -m venv llama
source llama/bin/activate

git clone https://github.com/ggerganov/llama.cpp.git
cd llama.cpp
cmake -B build -DGGML_CUDA=ON
cmake --build build -j$(nproc)

echo "testing build: usage: ./build/bin/llama-cli [options]"
./build/bin/llama-cli -h

echo "Installation complete!"


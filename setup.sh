#!/bin/bash

echo "Updating system..."
sudo apt update

echo "Installing required packages..."
sudo apt install -y build-essential cmake git python3 python3-pip ninja-build
sudo apt install -y htop wget curl unzip

echo "Creating python virtual environment..."
mkdir -p ~/Documents/urs_ws/llama_ws
cd ~/Documents/urs_ws/llama_ws
apt install python3.10-venv
python3 -m venv llama
source llama/bin/activate

echo "Clonning llama-cpp..."
git clone https://github.com/ggerganov/llama.cpp.git
cd llama.cpp
echo "Building llama-cpp..."
cmake -B build -DGGML_CUDA=ON
cmake --build build -j$(nproc)

echo "testing llama-cpp build: usage: ./build/bin/llama-cli [options]"
./build/bin/llama-cli -h

echo "Installing llama-cpp-python"
cd ../
git clone --recurse-submodules https://github.com/abetlen/llama-cpp-python.git
cd llama-cpp-python
CMAKE_ARGS="-DGGML_CUDA=ON" pip install -e .

echo "Downloading llama3 model..."
cd ../
mkdir -p ~/Documents/urs_ws/llama_ws/models/llama3
cd models/llama3
wget https://huggingface.co/TheBloke/Llama-3-OpenOrca-7B-GGUF/resolve/main/llama-3-openorca-7b.Q4_K_M.gguf

echo "Testing model..."
cd ~/Documents/urs_ws/llama_ws/llama.cpp
./build/bin/llama-cli -m ~/models/llama3/llama-3-openorca-7b.Q4_K_M.gguf -p "Hello from my dual arm robot!"
echo "Installation complete!"


#!/bin/bash

sudo apt install -y nvidia-driver-560

sudo apt install -y cuda-toolkit-12-4
nvcc --version   # verify


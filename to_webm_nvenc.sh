#!/bin/bash

RED='\033[38;2;243;139;168m'
GREEN='\033[38;2;166;227;161m'
BLUE='\033[38;2;137;180;250m'
YELLOW='\033[38;2;249;226;175m'
NC='\033[0m'

if ! command -v ffmpeg &> /dev/null; then
    echo -e "${RED}❌ ffmpeg is not installed${NC}"
    exit 1
fi

if [ $# -ge 1 ]; then
    input_file="$1"
else
    echo -e "${BLUE}🎬 Please enter the file path enclosed in quotes \" \":${NC}"
    read -rp "> " input_file
    
    input_file="${input_file%\"}"
    input_file="${input_file#\"}"
    input_file="${input_file%\'}"
    input_file="${input_file#\'}"
fi

if [ ! -f "$input_file" ]; then
    echo -e "${RED}❌ File does not exist: $input_file${NC}"
    exit 1
fi

filename=$(basename -- "$input_file")
name="${filename%.*}"
output_file="${name}.webm"


if ffmpeg -encoders | grep -q "av1_nvenc"; then
    echo -e "${YELLOW}⏳ Using NVIDIA AV1 Hardware Encoding (Fastest/Best)...${NC}"
    ffmpeg -hwaccel cuda -hide_banner -loglevel error -stats -i "$input_file" -c:v av1_nvenc -preset slow -c:a libopus "$output_file"
else

    echo -e "${YELLOW}⚠️ NVENC VP9 encode not supported by hardware.${NC}"
    echo -e "${BLUE}⏳ Using Hybrid CUDA Decoding + CPU VP9 Encoding...${NC}"
    ffmpeg -hwaccel cuda -hide_banner -loglevel error -stats -i "$input_file" -c:v libvpx-vp9 -b:v 0 -crf 30 -c:a libopus "$output_file"
fi

if [ $? -eq 0 ]; then
    echo -e "${GREEN}✅ Conversion completed successfully: $output_file${NC}"
else
    echo -e "${RED}❌ Conversion failed. Check your NVIDIA drivers/CUDA.${NC}"
fi
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
    echo -e "${BLUE}🖼️ Please enter the image path enclosed in quotes \" \":${NC}"
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
output_file="${name}.png"

echo -e "${YELLOW}⏳ Converting to PNG...${NC}"


ffmpeg -hide_banner -loglevel error -stats -i "$input_file" "$output_file"

if [ $? -eq 0 ]; then
    echo -e "${GREEN}✅ Successfully converted to: $output_file${NC}"
else
    echo -e "${RED}❌ Conversion failed${NC}"
fi
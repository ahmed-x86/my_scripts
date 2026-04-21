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
output_file="${name}_compressed.png"

echo -e "${YELLOW}⏳ Compressing to PNG losslessly...${NC}"

ffmpeg -hide_banner -loglevel error -stats -i "$input_file" -c:v png -compression_level 100 "$output_file"

if [ $? -eq 0 ]; then
    original_size=$(du -h "$input_file" | cut -f1)
    new_size=$(du -h "$output_file" | cut -f1)
    echo -e "${GREEN}✅ Successfully compressed!${NC}"
    echo -e "${BLUE}📊 Original Size: ${YELLOW}$original_size${NC}"
    echo -e "${BLUE}📊 New Size:      ${GREEN}$new_size${NC}"
    echo -e "${BLUE}📁 Saved as:      ${YELLOW}$output_file${NC}"
else
    echo -e "${RED}❌ Compression failed${NC}"
fi
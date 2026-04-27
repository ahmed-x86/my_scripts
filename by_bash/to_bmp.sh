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
output_file="${name}.bmp"

echo -e "${BLUE}🎯 Select BMP Pixel Format:${NC}"
echo -e "1) RGB 24-bit (Standard)"
echo -e "2) RGB 16-bit (565 - Useful for low-level/embedded)"
echo -e "3) Grayscale (8-bit Gray)"
read -rp "> " p_choice

case $p_choice in
    1) p_fmt="rgb24" ;;
    2) p_fmt="rgb565le" ;;
    3) p_fmt="gray" ;;
    *) p_fmt="rgb24" ;;
esac

echo -e "${YELLOW}⏳ Converting to BMP (${p_fmt})...${NC}"

ffmpeg -hide_banner -loglevel error -stats -i "$input_file" -pix_fmt "$p_fmt" "$output_file"

if [ $? -eq 0 ]; then
    echo -e "${GREEN}✅ Successfully converted to: $output_file${NC}"
else
    echo -e "${RED}❌ Conversion failed${NC}"
fi
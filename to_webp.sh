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
output_file="${name}.webp"

echo -e "${BLUE}🎯 Select WebP Mode:${NC}"
echo -e "1) Lossless (Best quality, larger size)"
echo -e "2) Lossy (Optimized for Web/GitHub - 75% quality)"
echo -e "3) High Compression (Smallest size - 50% quality)"
read -rp "> " mode_choice

case $mode_choice in
    1) dl_args="-lossless 1" ;;
    2) dl_args="-q:v 75" ;;
    3) dl_args="-q:v 50" ;;
    *) dl_args="-q:v 75" ;;
esac

echo -e "${YELLOW}⏳ Converting to WebP...${NC}"

ffmpeg -hide_banner -loglevel error -stats -i "$input_file" $dl_args "$output_file"

if [ $? -eq 0 ]; then
    echo -e "${GREEN}✅ Successfully converted to: $output_file${NC}"
else
    echo -e "${RED}❌ Conversion failed${NC}"
fi
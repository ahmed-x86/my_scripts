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

echo -e "${BLUE}📏 Select Icon Size:${NC}"
echo -e "1) 16x16   (Small Favicon)"
echo -e "2) 32x32   (Standard Favicon)"
echo -e "3) 48x48   (Desktop Icon)"
echo -e "4) 64x64"
echo -e "5) 128x128"
echo -e "6) 256x256 (High Quality)"
echo -e "7) 512x512"
echo -e "8) 1024x1024 (Maximum)"
echo -e "9) Custom Size"
read -rp "> " size_choice

case $size_choice in
    1) size=16 ;;
    2) size=32 ;;
    3) size=48 ;;
    4) size=64 ;;
    5) size=128 ;;
    6) size=256 ;;
    7) size=512 ;;
    8) size=1024 ;;
    9) 
        echo -e "${YELLOW}Enter custom size (e.g., 200):${NC}"
        read -rp "> " size ;;
    *) 
        echo -e "${RED}Invalid choice, defaulting to 256x256${NC}"
        size=256 ;;
esac

output_file="${name}_${size}x${size}.ico"

echo -e "${YELLOW}⏳ Generating icon [${size}x${size}]...${NC}"

ffmpeg -hide_banner -loglevel error -stats -i "$input_file" -vf "scale=$size:$size:flags=lanczos" "$output_file"

if [ $? -eq 0 ]; then
    echo -e "${GREEN}✅ Icon created successfully: $output_file${NC}"
else
    echo -e "${RED}❌ Icon creation failed${NC}"
fi
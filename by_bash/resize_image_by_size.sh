#!/bin/bash

RED='\033[38;2;243;139;168m'
GREEN='\033[38;2;166;227;161m'
BLUE='\033[38;2;137;180;250m'
YELLOW='\033[38;2;249;226;175m'
NC='\033[0m'


if ! command -v magick &> /dev/null; then
    echo -e "${RED}❌ ImageMagick is not installed. Please run: sudo pacman -S imagemagick${NC}"
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
extension="${filename##*.}"
name="${filename%.*}"


orig_size_bytes=$(stat -c%s "$input_file")
orig_size_kb=$((orig_size_bytes / 1024))

echo -e "${BLUE}ℹ️ Original image size is: ${YELLOW}${orig_size_kb} KB${NC}"

echo -e "${BLUE}💾 Enter target maximum size in KB (e.g., for 1MB type 1024):${NC}"
read -rp "> " target_kb


if ! [[ "$target_kb" =~ ^[0-9]+$ ]]; then
    echo -e "${RED}❌ Invalid input. Please enter numbers only.${NC}"
    exit 1
fi


if [ "$target_kb" -ge "$orig_size_kb" ]; then
    echo -e "${RED}❌ Target size (${target_kb} KB) must be smaller than the original size (${orig_size_kb} KB).${NC}"
    exit 1
fi


output_file="${name}_${target_kb}KB.jpg"

echo -e "${YELLOW}⏳ Compressing image to ~${target_kb} KB...${NC}"


magick "$input_file" -define jpeg:extent="${target_kb}kb" "$output_file"

if [ $? -eq 0 ]; then
    new_size_kb=$(( $(stat -c%s "$output_file") / 1024 ))
    echo -e "${GREEN}✅ Image compressed successfully!${NC}"
    echo -e "${GREEN}📁 Output: $output_file (${new_size_kb} KB)${NC}"
else
    echo -e "${RED}❌ Compression failed${NC}"
fi
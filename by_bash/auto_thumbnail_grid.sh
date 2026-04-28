#!/bin/bash

RED='\033[38;2;243;139;168m'
GREEN='\033[38;2;166;227;161m'
BLUE='\033[38;2;137;180;250m'
YELLOW='\033[38;2;249;226;175m'
NC='\033[0m'

if ! command -v ffmpeg &> /dev/null || ! command -v ffprobe &> /dev/null || ! command -v awk &> /dev/null; then
    echo -e "${RED}❌ ffmpeg, ffprobe, or awk is not installed${NC}"
    exit 1
fi

if [ $# -ge 1 ]; then
    input_file="$1"
else
    echo -e "${BLUE}🎞️ Please enter the video path enclosed in quotes \" \":${NC}"
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

echo -e "${BLUE}🎯 Enter number of columns (e.g., 4) [Default: 4]:${NC}"
read -rp "> " cols
cols=${cols:-4}

echo -e "${BLUE}🎯 Enter number of rows (e.g., 4) [Default: 4]:${NC}"
read -rp "> " rows
rows=${rows:-4}

echo -e "${BLUE}🎯 Enter thumbnail width in pixels (e.g., 320) [Default: 320]:${NC}"
read -rp "> " thumb_width
thumb_width=${thumb_width:-320}

filename=$(basename -- "$input_file")
name="${filename%.*}"
output_file="${name}_grid_${cols}x${rows}.jpg"

duration=$(ffprobe -v error -show_entries format=duration -of default=noprint_wrappers=1:nokey=1 "$input_file")


interval=$(awk -v dur="$duration" -v c="$cols" -v r="$rows" 'BEGIN {
    total_tiles = c * r;
    if (total_tiles <= 0) total_tiles = 16;
    printf "%.3f", dur / total_tiles;
}')

echo -e "${YELLOW}⏳ Generating ${cols}x${rows} thumbnail grid...${NC}"


ffmpeg -hide_banner -loglevel error -stats -y -i "$input_file" \
    -vf "fps=1/${interval},scale=${thumb_width}:-1,tile=${cols}x${rows}" \
    -vframes 1 "$output_file"

if [ $? -eq 0 ]; then
    echo -e "${GREEN}✅ Grid completed: $output_file${NC}"
else
    echo -e "${RED}❌ Grid generation failed${NC}"
fi
#!/bin/bash

# تعريف الألوان
RED='\033[38;2;243;139;168m'
GREEN='\033[38;2;166;227;161m'
BLUE='\033[38;2;137;180;250m'
YELLOW='\033[38;2;249;226;175m'
NC='\033[0m'


if [ $# -ge 1 ]; then 
    input_file="$1"
else
    echo -e "${BLUE}✂️ Enter file path to cut:${NC}"
    read -rp "> " input_file

    input_file="${input_file%\"}"
    input_file="${input_file#\"}"
    input_file="${input_file%\'}"
    input_file="${input_file#\'}"
fi


if [ ! -f "$input_file" ]; then
    echo -e "${RED}❌ File does not exist${NC}"
    exit 1
fi


echo -e "${BLUE}⏱️ Enter start time (HH:MM:SS) e.g., 00:01:52:${NC}"
read -rp "> " start_time

echo -e "${BLUE}⏱️ Enter end time (HH:MM:SS) e.g., 00:02:03:${NC}"
read -rp "> " end_time


filename=$(basename -- "$input_file")
ext="${filename##*.}"
name="${filename%.*}"


output_file="${name}_cut.${ext}"

echo -e "${YELLOW}⏳ Cutting file losslessly from [${start_time}] to [${end_time}]...${NC}"


ffmpeg -hide_banner -loglevel error -stats -i "$input_file" -ss "$start_time" -to "$end_time" -c copy "$output_file"

if [ $? -eq 0 ]; then
    echo -e "${GREEN}✅ Successfully cut to: $output_file${NC}"
else
    echo -e "${RED}❌ Cutting failed${NC}"
fi
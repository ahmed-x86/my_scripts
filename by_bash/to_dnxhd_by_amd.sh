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
output_file="${name}_davinci_amd.mov"

echo -e "${YELLOW}⏳ Converting to DaVinci Resolve (DNxHR) with AMD VA-API Decoding...${NC}"
notify-send "Video Converter" "Starting AMD-assisted conversion for $input_file..." -i video-x-generic


ffmpeg -hwaccel vaapi -hwaccel_device /dev/dri/renderD128 -hide_banner -loglevel error -stats -i "$input_file" \
    -c:v dnxhd -profile:v dnxhr_sq -pix_fmt yuv422p -c:a pcm_s16le "$output_file"

if [ $? -eq 0 ]; then
    echo -e "${GREEN}✅ Conversion completed successfully: $output_file${NC}"
    notify-send "Success" "AMD-assisted conversion finished: $output_file" -i dialog-information
else
    echo -e "${RED}❌ Conversion failed${NC}"
    notify-send "Error" "Conversion failed!" -i dialog-error
fi
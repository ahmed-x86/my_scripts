#!/bin/bash

RED='\033[38;2;243;139;168m'
GREEN='\033[38;2;166;227;161m'
BLUE='\033[38;2;137;180;250m'
YELLOW='\033[38;2;249;226;175m'
NC='\033[0m'

send_notification() {
    local title="$1"
    local message="$2"
    local icon="$3"
    if command -v notify-send &> /dev/null; then
        notify-send "$title" "$message" -i "$icon" || true
    fi
}

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
output_file="${name}_prores_cuda.mov"

echo -e "${YELLOW}⏳ Converting to ProRes 422 with CUDA Decoding...${NC}"
send_notification "Video Converter" "Starting CUDA-assisted ProRes conversion for $input_file..." "video-x-generic"

ffmpeg -y -hwaccel cuda -hide_banner -loglevel error -stats -i "$input_file" -c:v prores_ks -profile:v 2 -vendor apl0 -bits_per_mb 8000 -pix_fmt yuv422p10le -c:a pcm_s16le "$output_file"

if [ $? -eq 0 ]; then
    echo -e "${GREEN}✅ Conversion completed successfully: $output_file${NC}"
    send_notification "Success" "CUDA-assisted conversion finished: $output_file" "dialog-information"
else
    echo -e "${RED}❌ Conversion failed${NC}"
    send_notification "Error" "Conversion failed!" "dialog-error"
fi
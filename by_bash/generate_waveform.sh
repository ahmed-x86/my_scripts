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
    echo -e "${BLUE}🎵 Please enter the audio or video file path enclosed in quotes \" \":${NC}"
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
output_file="${name}_waveform.mp4"

echo -e "${YELLOW}⏳ Generating Audio Waveform Video...${NC}"

if command -v notify-send &> /dev/null; then
    notify-send "Waveform Generator" "Starting waveform generation for $input_file..." -i multimedia-volume-control
fi


ffmpeg -y -hide_banner -loglevel error -stats -i "$input_file" \
    -filter_complex "[0:a]showwaves=s=1920x1080:mode=cline:colors=cyan[v]" \
    -map "[v]" -map 0:a \
    -c:v libx264 -preset fast -crf 22 -c:a aac -b:a 192k \
    "$output_file"

if [ $? -eq 0 ]; then
    echo -e "${GREEN}✅ Waveform video completed: $output_file${NC}"
    if command -v notify-send &> /dev/null; then
        notify-send "Success" "Waveform finished: $output_file" -i dialog-information
    fi
else
    echo -e "${RED}❌ Generation failed${NC}"
    if command -v notify-send &> /dev/null; then
        notify-send "Error" "Waveform generation failed!" -i dialog-error
    fi
fi
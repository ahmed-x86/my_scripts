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
    echo -e "${BLUE}🖼️ Please enter the video file path enclosed in quotes \" \":${NC}"
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

echo -e "${BLUE}Select extraction mode:${NC}"
echo -e "1) Single frame at specific time (e.g., 00:01:23)"
echo -e "2) Multiple frames (e.g., 1 frame per second)"
read -rp "> " mode

if [ "$mode" == "1" ]; then
    echo -e "${YELLOW}Enter timestamp (HH:MM:SS):${NC}"
    read -rp "> " timestamp
    
    output_file="${name}_frame_${timestamp//:/_}.jpg"
    echo -e "${YELLOW}⏳ Extracting frame...${NC}"
    
    ffmpeg -hide_banner -loglevel error -stats -ss "$timestamp" -i "$input_file" -vframes 1 -q:v 2 "$output_file"

elif [ "$mode" == "2" ]; then
    echo -e "${YELLOW}Enter fps (e.g., 1 for 1 frame/sec, 0.1 for 1 frame/10sec):${NC}"
    read -rp "> " fps
    
    mkdir -p "${name}_frames"
    output_file="${name}_frames/frame_%04d.jpg"
    echo -e "${YELLOW}⏳ Extracting frames into /${name}_frames ...${NC}"
    
    ffmpeg -hide_banner -loglevel error -stats -i "$input_file" -vf "fps=$fps" -q:v 2 "$output_file"

else
    echo -e "${RED}❌ Invalid option${NC}"
    exit 1
fi

if [ $? -eq 0 ]; then
    echo -e "${GREEN}✅ Extraction completed successfully${NC}"
else
    echo -e "${RED}❌ Extraction failed${NC}"
fi
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
    echo -e "${BLUE}📂 Please enter the video file path enclosed in quotes \" \":${NC}"
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

echo -e "${BLUE}📏 Select Scaling Percentage (NVIDIA NVENC):${NC}"
echo -e "1) 90%"
echo -e "2) 80%"
echo -e "3) 75%"
echo -e "4) 70%"
echo -e "5) 60%"
echo -e "6) 50%"
echo -e "7) 40%"
echo -e "8) 30%"
echo -e "9) 25%"
echo -e "10) 20%"
echo -e "11) 10%"
echo -e "12) 5%"
read -rp "> " size_choice

case $size_choice in
    1) scale="0.90"; pct="90" ;;
    2) scale="0.80"; pct="80" ;;
    3) scale="0.75"; pct="75" ;;
    4) scale="0.70"; pct="70" ;;
    5) scale="0.60"; pct="60" ;;
    6) scale="0.50"; pct="50" ;;
    7) scale="0.40"; pct="40" ;;
    8) scale="0.30"; pct="30" ;;
    9) scale="0.25"; pct="25" ;;
    10) scale="0.20"; pct="20" ;;
    11) scale="0.10"; pct="10" ;;
    12) scale="0.05"; pct="5" ;;
    *) scale="0.50"; pct="50" ;;
esac


output_file="${name}_${pct}percent_nvenc.mkv"

echo -e "${YELLOW}⏳ Resizing and Encoding to MKV using NVIDIA NVENC...${NC}"
notify-send "Video Resizer" "Starting NVENC hardware encoding for $input_file..." -i video-x-generic


ffmpeg -hwaccel cuda -hide_banner -loglevel error -stats -i "$input_file" \
    -vf "scale=trunc(iw*${scale}/2)*2:trunc(ih*${scale}/2)*2" \
    -c:v h264_nvenc -preset p4 -c:a aac "$output_file"

if [ $? -eq 0 ]; then
    echo -e "${GREEN}✅ NVENC Encoding completed: $output_file${NC}"
    notify-send "Success" "NVENC Resize finished: $output_file" -i dialog-information
else
    echo -e "${RED}❌ NVENC Encoding failed (Check drivers/CUDA)${NC}"
    notify-send "Error" "NVENC process failed!" -i dialog-error
fi
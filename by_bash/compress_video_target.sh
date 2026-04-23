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

echo -e "${BLUE}🎯 Enter target file size in MB (e.g., 8, 25):${NC}"
read -rp "> " target_size_mb

filename=$(basename -- "$input_file")
name="${filename%.*}"
output_file="${name}_${target_size_mb}MB.mp4"

duration=$(ffprobe -v error -show_entries format=duration -of default=noprint_wrappers=1:nokey=1 "$input_file")

audio_bitrate=128

video_bitrate=$(awk -v target="$target_size_mb" -v dur="$duration" -v ab="$audio_bitrate" 'BEGIN {
    total_bitrate = (target * 8192) / dur;
    vb = total_bitrate - ab;
    if (vb < 10) vb = 10;
    printf "%.0f", vb;
}')

echo -e "${YELLOW}⏳ Compressing to ~${target_size_mb}MB (Video: ${video_bitrate}kbps, Audio: ${audio_bitrate}kbps)...${NC}"
echo -e "${YELLOW}⏳ Pass 1/2...${NC}"

ffmpeg -hide_banner -loglevel error -stats -y -i "$input_file" -c:v libx264 -b:v "${video_bitrate}k" -pass 1 -an -f mp4 /dev/null

if [ $? -ne 0 ]; then
    echo -e "${RED}❌ Pass 1 failed${NC}"
    rm -f ffmpeg2pass-0.log ffmpeg2pass-0.log.mbtree
    exit 1
fi

echo -e "${YELLOW}⏳ Pass 2/2...${NC}"

ffmpeg -hide_banner -loglevel error -stats -y -i "$input_file" -c:v libx264 -b:v "${video_bitrate}k" -pass 2 -c:a aac -b:a "${audio_bitrate}k" "$output_file"

if [ $? -eq 0 ]; then
    echo -e "${GREEN}✅ Compression completed: $output_file${NC}"
else
    echo -e "${RED}❌ Compression failed${NC}"
fi

rm -f ffmpeg2pass-0.log ffmpeg2pass-0.log.mbtree
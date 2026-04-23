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

if [ $# -ge 2 ]; then
    video_file="$1"
    audio_file="$2"
else
    echo -e "${BLUE}🎬 Please enter the VIDEO file path enclosed in quotes \" \":${NC}"
    read -rp "> " video_file
    video_file="${video_file%\"}"
    video_file="${video_file#\"}"
    video_file="${video_file%\'}"
    video_file="${video_file#\'}"

    echo -e "${BLUE}🎵 Please enter the NEW AUDIO file path enclosed in quotes \" \":${NC}"
    read -rp "> " audio_file
    audio_file="${audio_file%\"}"
    audio_file="${audio_file#\"}"
    audio_file="${audio_file%\'}"
    audio_file="${audio_file#\'}"
fi

if [ ! -f "$video_file" ]; then
    echo -e "${RED}❌ Video file does not exist: $video_file${NC}"
    exit 1
fi

if [ ! -f "$audio_file" ]; then
    echo -e "${RED}❌ Audio file does not exist: $audio_file${NC}"
    exit 1
fi

filename=$(basename -- "$video_file")
name="${filename%.*}"
ext="${filename##*.}"
output_file="${name}_new_audio.${ext}"

echo -e "${YELLOW}⏳ Replacing audio losslessly...${NC}"

ffmpeg -hide_banner -loglevel error -stats -i "$video_file" -i "$audio_file" -map 0:v:0 -map 1:a:0 -c:v copy -c:a copy -shortest "$output_file"

if [ $? -eq 0 ]; then
    echo -e "${GREEN}✅ Audio replaced successfully: $output_file${NC}"
else
    echo -e "${RED}❌ Process failed${NC}"
fi
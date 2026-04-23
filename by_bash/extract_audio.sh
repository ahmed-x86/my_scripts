#!/bin/bash

RED='\033[38;2;243;139;168m'
GREEN='\033[38;2;166;227;161m'
BLUE='\033[38;2;137;180;250m'
YELLOW='\033[38;2;249;226;175m'
NC='\033[0m'

if [ $# -ge 1 ]; then 
    input_file="$1"
else
    echo -e "${BLUE}🎵 Enter file path to extract audio:${NC}"
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

filename=$(basename -- "$input_file")
name="${filename%.*}"

codec=$(ffprobe -v error -select_streams a:0 -show_entries stream=codec_name -of default=noprint_wrappers=1:nokey=1 "$input_file")

case "$codec" in
    mp3) ext="mp3" ;;
    aac) ext="m4a" ;;
    opus) ext="opus" ;;
    vorbis) ext="ogg" ;;
    flac) ext="flac" ;;
    *) ext="mka" ;;
esac

output_file="${name}_extracted.${ext}"

echo -e "${YELLOW}⏳ Extracting original [${codec}] audio stream...${NC}"

ffmpeg -hide_banner -loglevel error -stats -i "$input_file" -vn -c:a copy "$output_file"

if [ $? -eq 0 ]; then
    echo -e "${GREEN}✅ Successfully extracted to: $output_file${NC}"
else
    echo -e "${RED}❌ Extraction failed${NC}"
fi
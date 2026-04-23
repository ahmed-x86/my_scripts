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
    echo -e "${BLUE}📱 Please enter the video path enclosed in quotes \" \":${NC}"
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
ext="${filename##*.}"

echo -e "${BLUE}📏 Select Social Media Resolution:${NC}"
echo -e "1) 1080x1920 (9:16 - TikTok / Reels / Shorts)"
echo -e "2) 1080x1350 (4:5 - Instagram Portrait)"
echo -e "3) 1080x1080 (1:1 - Square Post)"
echo -e "4) 1920x1080 (16:9 - YouTube Landscape)"
echo -e "5) 720x1280  (9:16 - 720p Vertical)"
echo -e "6) Custom Size"
read -rp "> " size_choice

case $size_choice in
    1) width=1080; height=1920 ;;
    2) width=1080; height=1350 ;;
    3) width=1080; height=1080 ;;
    4) width=1920; height=1080 ;;
    5) width=720; height=1280 ;;
    6) 
        echo -e "${YELLOW}Enter width (e.g., 1080):${NC}"
        read -rp "> " width
        echo -e "${YELLOW}Enter height (e.g., 1920):${NC}"
        read -rp "> " height ;;
    *) 
        echo -e "${RED}Invalid choice, defaulting to 1080x1920${NC}"
        width=1080; height=1920 ;;
esac

output_file="${name}_${width}x${height}.${ext}"

echo -e "${YELLOW}⏳ Resizing video to [${width}x${height}]...${NC}"

ffmpeg -hide_banner -loglevel error -stats -i "$input_file" -vf "scale=${width}:${height}:force_original_aspect_ratio=decrease,pad=${width}:${height}:(ow-iw)/2:(oh-ih)/2:black" -c:a copy "$output_file"

if [ $? -eq 0 ]; then
    echo -e "${GREEN}✅ Video ready for social media: $output_file${NC}"
else
    echo -e "${RED}❌ Video resizing failed${NC}"
fi
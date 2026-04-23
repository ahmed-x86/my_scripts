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
    logo_file="$2"
else
    echo -e "${BLUE}🎬 Please enter the VIDEO file path enclosed in quotes \" \":${NC}"
    read -rp "> " video_file
    video_file="${video_file%\"}"
    video_file="${video_file#\"}"
    video_file="${video_file%\'}"
    video_file="${video_file#\'}"

    echo -e "${BLUE}🖼️ Please enter the LOGO file path (PNG with transparency) enclosed in quotes \" \":${NC}"
    read -rp "> " logo_file
    logo_file="${logo_file%\"}"
    logo_file="${logo_file#\"}"
    logo_file="${logo_file%\'}"
    logo_file="${logo_file#\'}"
fi

if [ ! -f "$video_file" ]; then
    echo -e "${RED}❌ Video file does not exist: $video_file${NC}"
    exit 1
fi

if [ ! -f "$logo_file" ]; then
    echo -e "${RED}❌ Logo file does not exist: $logo_file${NC}"
    exit 1
fi

# طلب تحديد مكان الشعار
echo -e "${BLUE}📍 Select Watermark Position:${NC}"
echo -e "1) Top-Left"
echo -e "2) Top-Right"
echo -e "3) Bottom-Left"
echo -e "4) Bottom-Right"
echo -e "5) Center"
read -rp "> " position_choice

case $position_choice in
    1) overlay_pos="10:10" ;;
    2) overlay_pos="W-w-10:10" ;;
    3) overlay_pos="10:H-h-10" ;;
    4) overlay_pos="W-w-10:H-h-10" ;;
    5) overlay_pos="(W-w)/2:(H-h)/2" ;;
    *) 
        echo -e "${RED}Invalid choice, defaulting to Bottom-Right${NC}"
        overlay_pos="W-w-10:H-h-10" ;;
esac


echo -e "${BLUE} Enter Opacity level (0.1 to 1.0) [e.g., 0.5 for 50% transparent, 1.0 for solid]:${NC}"
read -rp "> " opacity


if [ -z "$opacity" ]; then
    opacity=1.0
fi

filename=$(basename -- "$video_file")
name="${filename%.*}"
ext="${filename##*.}"
output_file="${name}_watermarked.${ext}"

echo -e "${YELLOW}⏳ Adding watermark (Opacity: ${opacity}) to position...${NC}"


ffmpeg -hide_banner -loglevel error -stats -i "$video_file" -i "$logo_file" \
-filter_complex "[1:v]format=rgba,colorchannelmixer=aa=${opacity}[logo];[0:v][logo]overlay=${overlay_pos}" \
-c:v libx264 -preset fast -crf 23 -c:a copy "$output_file"

if [ $? -eq 0 ]; then
    echo -e "${GREEN}✅ Watermark added successfully: $output_file${NC}"
else
    echo -e "${RED}❌ Process failed${NC}"
fi
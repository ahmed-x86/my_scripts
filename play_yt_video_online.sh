#!/bin/bash

RED='\033[38;2;243;139;168m'
GREEN='\033[38;2;166;227;161m'
BLUE='\033[38;2;137;180;250m'
YELLOW='\033[38;2;249;226;175m'
NC='\033[0m'

if ! command -v yt-dlp &> /dev/null; then
    echo -e "${RED}❌ yt-dlp is not installed. (Run: sudo pacman -S yt-dlp)${NC}"
    exit 1
fi

if ! command -v mpv &> /dev/null; then
    echo -e "${RED}❌ mpv is not installed. (Run: sudo pacman -S mpv)${NC}"
    exit 1
fi

if [ $# -ge 1 ]; then
    url="$1"
else
    echo -e "${BLUE}🔗 Please enter the YouTube URL enclosed in quotes \" \":${NC}"
    read -rp "> " url
    
    url="${url%\"}"; url="${url#\"}"
    url="${url%\'}"; url="${url#\'}"
fi

if [ -z "$url" ]; then
    echo -e "${RED}❌ URL cannot be empty${NC}"
    exit 1
fi

echo -e "${BLUE}📊 Do you want to select video quality manually? (y/n):${NC}"
read -rp "> " manual_quality

if [[ "$manual_quality" == "y" || "$manual_quality" == "Y" ]]; then
    echo -e "${YELLOW}⏳ Fetching video formats...${NC}"
    yt-dlp -F "$url"
    
    echo -e "${BLUE}✍️ Enter the format code (e.g., 299+140, or 'best'):${NC}"
    read -rp "> " format_code
    
    if [ -n "$format_code" ]; then
        echo -e "${YELLOW}🍿 Streaming video in mpv (Format: $format_code)...${NC}"
        mpv --ytdl-format="$format_code" "$url"
    else
        echo -e "${YELLOW}🍿 Streaming video in mpv (Best Quality)...${NC}"
        mpv "$url"
    fi
else
    echo -e "${YELLOW}🍿 Streaming video in mpv (Best Quality)...${NC}"
    mpv "$url"
fi
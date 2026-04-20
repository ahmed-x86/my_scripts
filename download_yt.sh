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

if ! command -v ffmpeg &> /dev/null; then
    echo -e "${YELLOW}⚠️ ffmpeg is not installed. Some features (like embedding chapters/subs) may not work. (Run: sudo pacman -S ffmpeg)${NC}"
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

dl_args=()

echo -e "${YELLOW}⏳ Fetching video formats...${NC}"

yt-dlp -F "$url"
echo -e "${BLUE}📊 Enter the format code (e.g., 299+140 for 1080p60, or 'best'):${NC}"
read -rp "> " format_code

if [ -z "$format_code" ]; then
    format_code="bestvideo+bestaudio/best"
fi
dl_args+=("-f" "$format_code")

echo -e "${BLUE}📝 Do you want to download subtitles? (y/n):${NC}"
read -rp "> " want_subs

if [[ "$want_subs" == "y" || "$want_subs" == "Y" ]]; then
    echo -e "${YELLOW}⏳ Fetching available subtitles...${NC}"
    yt-dlp --list-subs "$url"
    
    echo -e "${BLUE}✍️ Enter the subtitle language code (e.g., ar, en) or type 'all':${NC}"
    read -rp "> " sub_lang
    
    if [ "$sub_lang" == "all" ]; then
        dl_args+=("--write-sub" "--write-auto-sub" "--all-subs" "--embed-subs")
    elif [ -n "$sub_lang" ]; then
        dl_args+=("--write-sub" "--write-auto-sub" "--sub-lang" "$sub_lang" "--embed-subs")
    fi
fi

echo -e "${BLUE}🖼️ Do you want to download the thumbnail? (y/n):${NC}"
read -rp "> " want_thumb

if [[ "$want_thumb" == "y" || "$want_thumb" == "Y" ]]; then
    dl_args+=("--write-thumbnail" "--convert-thumbnails" "jpg")
fi

echo -e "${BLUE}📑 Do you want to embed chapters into the video? (y/n):${NC}"
read -rp "> " want_chapters
if [[ "$want_chapters" == "y" || "$want_chapters" == "Y" ]]; then
    dl_args+=("--embed-chapters")
fi

echo -e "${BLUE}✂️ Do you want to split the video into separate files based on chapters? (y/n):${NC}"
read -rp "> " split_chapters
if [[ "$split_chapters" == "y" || "$split_chapters" == "Y" ]]; then
    dl_args+=("--split-chapters")
fi

echo -e "${BLUE}📄 Do you want to save video info (description, likes, views) to a txt file? (y/n):${NC}"
read -rp "> " want_info
if [[ "$want_info" == "y" || "$want_info" == "Y" ]]; then
    dl_args+=("--print-to-file" "Title: %(title)s
Channel: %(uploader)s
Upload Date: %(upload_date)s
Views: %(view_count)s
Likes: %(like_count)s

=========================
Description:
%(description)s" "%(title)s_info.txt")
fi

echo -e "${YELLOW}⏳ Starting download...${NC}"

yt-dlp "${dl_args[@]}" "$url"

if [ $? -eq 0 ]; then
    echo -e "${GREEN}✅ Download completed successfully!${NC}"
else
    echo -e "${RED}❌ Download failed!${NC}"
fi

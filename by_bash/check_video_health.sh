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
    echo -e "${BLUE}🔍 Please enter the video path to check (CPU Mode):${NC}"
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


log_file="corruption_report.txt"
> "$log_file"

echo -e "${YELLOW}⏳ Scanning video for integrity issues using CPU...${NC}"
echo -e "${BLUE}ℹ️ This process decodes every frame to ensure the file is 100% healthy.${NC}"


notify-send "Video Health Check" "Starting thorough scan for $input_file..." -i security-high


ffmpeg -v error -i "$input_file" -f null - > "$log_file" 2>&1


if [ ! -s "$log_file" ]; then
    echo -e "${GREEN}✅ Perfect! No corruption or decoding errors detected.${NC}"
    notify-send "Success" "Video is 100% Healthy: $input_file" -i dialog-information
    rm "$log_file"
else
    echo -e "${RED}❌ CORRUPTION DETECTED!${NC}"
    echo -e "${YELLOW}--------------------------------------------------${NC}"
    cat "$log_file"
    echo -e "${YELLOW}--------------------------------------------------${NC}"
    echo -e "${BLUE}📄 Full error details saved in: $log_file${NC}"
    notify-send "Integrity Warning" "Corruption found in $input_file" -i dialog-warning
fi
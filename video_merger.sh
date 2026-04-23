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

echo -e "${BLUE}📂 Please enter the FIRST video path enclosed in quotes \" \":${NC}"
read -rp "> " input_file1


input_file1="${input_file1%\"}"
input_file1="${input_file1#\"}"
input_file1="${input_file1%\'}"
input_file1="${input_file1#\'}"

if [ ! -f "$input_file1" ]; then
    echo -e "${RED}❌ File does not exist: $input_file1${NC}"
    exit 1
fi


echo -e "${BLUE}📂 Please enter the SECOND video path enclosed in quotes \" \":${NC}"
read -rp "> " input_file2


input_file2="${input_file2%\"}"
input_file2="${input_file2#\"}"
input_file2="${input_file2%\'}"
input_file2="${input_file2#\'}"

if [ ! -f "$input_file2" ]; then
    echo -e "${RED}❌ File does not exist: $input_file2${NC}"
    exit 1
fi


filename=$(basename -- "$input_file1")
name="${filename%.*}"
ext="${filename##*.}"
output_file="${name}_merged.${ext}"


list_file="temp_concat_list.txt"
echo "file '$input_file1'" > "$list_file"
echo "file '$input_file2'" >> "$list_file"

echo -e "${YELLOW}⏳ Merging videos losslessly...${NC}"


ffmpeg -hide_banner -loglevel error -stats -f concat -safe 0 -i "$list_file" -c copy "$output_file"

# التحقق من النتيجة
if [ $? -eq 0 ]; then
    echo -e "${GREEN}✅ Merging completed successfully: $output_file${NC}"
else
    echo -e "${RED}❌ Merging failed${NC}"
fi

# مسح الملف المؤقت لتنظيف المكان
rm -f "$list_file"
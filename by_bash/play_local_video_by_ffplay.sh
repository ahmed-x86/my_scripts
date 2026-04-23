#!/bin/bash

RED='\033[38;2;243;139;168m'
GREEN='\033[38;2;166;227;161m'
BLUE='\033[38;2;137;180;250m'
YELLOW='\033[38;2;249;226;175m'
NC='\033[0m'


if ! command -v ffplay &> /dev/null || ! command -v ffprobe &> /dev/null; then
    echo -e "${RED}❌ ffplay or ffprobe is not installed.${NC}"
    exit 1
fi

if [ $# -ge 1 ]; then
    input_file="$1"
else
    echo -e "${BLUE}📂 Please enter the video file path enclosed in quotes \" \":${NC}"
    read -rp "> " input_file
    
    input_file="${input_file%\"}"; input_file="${input_file#\"}"
    input_file="${input_file%\'}"; input_file="${input_file#\'}"
fi

if [ -z "$input_file" ]; then
    echo -e "${RED}❌ Path cannot be empty${NC}"
    exit 1
fi

if [ ! -f "$input_file" ]; then
    echo -e "${RED}❌ File does not exist: $input_file${NC}"
    exit 1
fi

options=()
hwdec_args=()

options+=("CPU (Software Decoding)")
hwdec_args+=("no")

if lspci | grep -iE 'vga|3d|display' | grep -iq intel; then
    options+=("Intel GPU")
    hwdec_args+=("qsv")
fi

if lspci | grep -iE 'vga|3d|display' | grep -iq amd; then

    options+=("AMD GPU (Fallback to CPU in ffplay)")
    hwdec_args+=("no")
fi

if lspci | grep -iE 'vga|3d|display' | grep -iq nvidia; then
    options+=("Nvidia GPU")
    hwdec_args+=("cuvid")
fi

echo -e "${BLUE}🖥️  Select Decoding Device:${NC}"
for i in "${!options[@]}"; do
    echo -e "${YELLOW}$((i+1)). ${options[$i]}${NC}"
done

read -rp "> " hw_choice

if ! [[ "$hw_choice" =~ ^[0-9]+$ ]] || [ "$hw_choice" -lt 1 ] || [ "$hw_choice" -gt "${#options[@]}" ]; then
    echo -e "${RED}❌ Invalid selection. Defaulting to CPU.${NC}"
    hw_arg="no"
    selected_name="CPU"
else
    index=$((hw_choice-1))
    hw_arg="${hwdec_args[$index]}"
    selected_name="${options[$index]}"
fi


echo -e "${YELLOW}⏳ Probing video codec...${NC}"
codec=$(ffprobe -v error -select_streams v:0 -show_entries stream=codec_name -of default=noprint_wrappers=1:nokey=1 "$input_file")
    
ffplay_args=""

if [ "$hw_arg" == "cuvid" ]; then
    case "$codec" in
        h264) ffplay_args="-vcodec h264_cuvid" ;;
        hevc) ffplay_args="-vcodec hevc_cuvid" ;;
        vp9) ffplay_args="-vcodec vp9_cuvid" ;;
        *) echo -e "${YELLOW}⚠️ Unsupported codec ($codec) for Nvidia HW decoding in ffplay. Using CPU.${NC}" ;;
    esac
elif [ "$hw_arg" == "qsv" ]; then
    case "$codec" in
        h264) ffplay_args="-vcodec h264_qsv" ;;
        hevc) ffplay_args="-vcodec hevc_qsv" ;;
        *) echo -e "${YELLOW}⚠️ Unsupported codec ($codec) for Intel HW decoding in ffplay. Using CPU.${NC}" ;;
    esac
fi

echo -e "${GREEN}🍿 Playing local video via ${selected_name} (Codec: ${codec})...${NC}"


ffplay -autoexit $ffplay_args "$input_file"
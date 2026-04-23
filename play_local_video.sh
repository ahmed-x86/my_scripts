#!/bin/bash

RED='\033[38;2;243;139;168m'
GREEN='\033[38;2;166;227;161m'
BLUE='\033[38;2;137;180;250m'
YELLOW='\033[38;2;249;226;175m'
NC='\033[0m'

if ! command -v mpv &> /dev/null; then
    echo -e "${RED}❌ mpv is not installed. (Run: sudo pacman -S mpv)${NC}"
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
    hwdec_args+=("vaapi")
fi

if lspci | grep -iE 'vga|3d|display' | grep -iq amd; then
    options+=("AMD GPU")
    hwdec_args+=("vaapi")
fi

if lspci | grep -iE 'vga|3d|display' | grep -iq nvidia; then
    if command -v nvidia-smi &> /dev/null; then
        major_cc=$(nvidia-smi --query-gpu=compute_cap --format=csv,noheader | awk -F'.' '{print $1}' | head -n 1)
        if [ -n "$major_cc" ] && [ "$major_cc" -lt 6 ]; then
            options+=("Nvidia GPU (Old Cards)")
            hwdec_args+=("vdpau")
        else
            options+=("Nvidia GPU (Modern Cards)")
            hwdec_args+=("nvdec")
        fi
    else
        options+=("Nvidia GPU")
        hwdec_args+=("nvdec")
    fi
fi

if lsmod | grep -iq nouveau; then
    options+=("Nvidia Open Source Driver (Nouveau)")
    hwdec_args+=("vaapi")
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

extra_mpv_args=""
if [[ "$selected_name" == "Intel GPU" ]]; then
    extra_mpv_args="--vo=gpu --gpu-context=wayland"
fi

echo -e "${GREEN}🍿 Playing local video via ${selected_name}...${NC}"
mpv --hwdec="$hw_arg" $extra_mpv_args "$input_file"
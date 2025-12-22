#!/bin/bash

# Check if ffmpeg is installed
if ! command -v ffmpeg &> /dev/null; then
    echo "❌ ffmpeg is not installed"
    exit 1
fi

# Ask for input file path
read -rp "🎬 Enter the path of the file to convert to WebM: " input_file

# Check if the file exists
if [ ! -f "$input_file" ]; then
    echo "❌ File does not exist"
    exit 1
fi

# Extract filename without extension
filename=$(basename -- "$input_file")
name="${filename%.*}"

# Output file name (Changed to .webm)
output_file="${name}.webm"

# Convert to WebM
# -c:v libvpx-vp9 : Video codec (VP9 is standard for WebM)
# -c:a libopus    : Audio codec (Opus is best for WebM)
# -b:v 0 -crf 30  : Constant quality mode (adjust 30 for quality vs size)
echo "⏳ Converting to WebM..."
ffmpeg -i "$input_file" -c:v libvpx-vp9 -b:v 0 -crf 30 -c:a libopus "$output_file"

# Check conversion status
if [ $? -eq 0 ]; then
    echo "✅ Conversion completed successfully: $output_file"
else
    echo "❌ Conversion failed"
fi

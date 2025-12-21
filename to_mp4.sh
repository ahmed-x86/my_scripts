#!/bin/bash

# Check if ffmpeg is installed
if ! command -v ffmpeg &> /dev/null; then
    echo "❌ ffmpeg is not installed"
    exit 1
fi

# Ask for input file path
read -rp "📂 Enter the path of the file to convert: " input_file

# Remove surrounding single or double quotes if present
input_file="${input_file%\"}"
input_file="${input_file#\"}"
input_file="${input_file%\'}"
input_file="${input_file#\'}"

# Check if the file exists
if [ ! -f "$input_file" ]; then
    echo "❌ File does not exist"
    exit 1
fi

# Extract filename without extension
filename=$(basename -- "$input_file")
name="${filename%.*}"

# Output file name
output_file="${name}.mp4"

# Convert to MP4
echo "⏳ Converting..."
ffmpeg -i "$input_file" -c:v libx264 -c:a aac -movflags +faststart "$output_file"

# Check conversion status
if [ $? -eq 0 ]; then
    echo "✅ Conversion completed successfully: $output_file"
else
    echo "❌ Conversion failed"
fi

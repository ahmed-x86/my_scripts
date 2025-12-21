#!/bin/bash

# Check if ffmpeg is installed
if ! command -v ffmpeg &> /dev/null; then
    echo "❌ ffmpeg is not installed"
    exit 1
fi

# Ask for input file path
read -rp "🎵 Enter the path of the file to convert to MP3: " input_file

# Check if the file exists
if [ ! -f "$input_file" ]; then
    echo "❌ File does not exist"
    exit 1
fi

# Extract filename without extension
filename=$(basename -- "$input_file")
name="${filename%.*}"

# Output file name
output_file="${name}.mp3"

# Convert to MP3
echo "⏳ Converting..."
ffmpeg -i "$input_file" -vn -c:a libmp3lame -b:a 192k "$output_file"

# Check conversion status
if [ $? -eq 0 ]; then
    echo "✅ Conversion completed successfully: $output_file"
else
    echo "❌ Conversion failed"
fi

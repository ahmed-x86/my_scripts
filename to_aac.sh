#!/bin/bash

# Check if ffmpeg is installed
if ! command -v ffmpeg &> /dev/null; then
    echo "❌ ffmpeg is not installed"
    exit 1
fi

# Ask for input file path
read -rp "🎵 Enter the path of the file to convert to AAC: " input_file

# Check if the file exists
if [ ! -f "$input_file" ]; then
    echo "❌ File does not exist"
    exit 1
fi

# Extract filename without extension
filename=$(basename -- "$input_file")
name="${filename%.*}"

# Output file name
# Note: .m4a is the standard container for AAC audio. 
# If you strictly need raw .aac extension, change m4a to aac below.
output_file="${name}.m4a"

# Convert to AAC
# -vn         : Disable video (Audio only)
# -c:a aac    : Use the Native FFmpeg AAC encoder
# -b:a 192k   : Set audio bitrate to 192k (High Quality)
echo "⏳ Converting to AAC..."
ffmpeg -i "$input_file" -vn -c:a aac -b:a 192k "$output_file"

# Check conversion status
if [ $? -eq 0 ]; then
    echo "✅ Conversion completed successfully: $output_file"
else
    echo "❌ Conversion failed"
fi

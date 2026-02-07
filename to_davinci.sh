#!/bin/bash

if [ -z "$1" ]; then
    echo "Usage: $0 <video_file>"
    exit 1
fi

INPUT="$1"
OUTPUT="${INPUT%.*}_davinci.mov"


ffmpeg -i "$INPUT" -c:v dnxhd -profile:v dnxhr_sq -pix_fmt yuv422p -c:a pcm_s16le "$OUTPUT"

echo "تم التحويل بنجاح: $OUTPUT"

#!/bin/bash

if [ -z "$1" ]; then
    echo "Usage: $0 <video_file>"
    exit 1
fi

INPUT="$1"
OUTPUT="${INPUT%.*}_davinci.mov"

# إشعار ببدء التحويل
notify-send "Video Converter" "Starting conversion for $INPUT..." -i video-x-generic

# التحويل
ffmpeg -i "$INPUT" -c:v dnxhd -profile:v dnxhr_sq -pix_fmt yuv422p -c:a pcm_s16le "$OUTPUT"

# التحقق من نجاح العملية وإرسال الإشعار المناسب
if [ $? -eq 0 ]; then
    notify-send "Success" "Conversion finished: $OUTPUT" -i dialog-information
else
    notify-send "Error" "Conversion failed!" -i dialog-error
fi

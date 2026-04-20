# My Scripts 🛠️

A collection of vanilla Bash scripts for efficient media conversion using FFmpeg on Arch Linux. These scripts are optimized for performance, clean output, and support for NVIDIA hardware acceleration where applicable.

## Features
- **Catppuccin Mocha** themed CLI output.
- **Dynamic Input**: Accepts file paths as arguments or prompts for them.
- **Hardware Acceleration**: Uses CUDA for decoding and scaling to speed up heavy conversions.
- **Professional Formats**: Scripts for DaVinci Resolve, WebM, MP4, and high-quality Audio.

## Scripts Overview

### 🎬 Video Conversion
- `to_mp4.sh`: Standard H.264/AAC MP4 conversion.
- `to_mkv.sh`: High-quality MKV container conversion.
- `to_webm.sh`: VP9/Opus conversion for web usage.
- `to_davinci.sh`: Converts video to DNxHR (MOV) for DaVinci Resolve (CPU based).
- `to_davinci_cuda.sh`: Uses **CUDA** to accelerate decoding and pixel format conversion for DaVinci Resolve.

### 🎵 Audio Conversion
- `to_aac.sh`: Converts audio to high-quality AAC (M4A).
- `to_mp3.sh`: Converts audio to 192k MP3.

## Usage

1. **Direct Argument**:
   ```bash
   ./to_mp4.sh "path/to/video.mkv"
   ```

2. **Interactive Mode**:
   Simply run the script, and it will prompt you for the path.
   ```bash
   ./to_mp4.sh
   ```

## CUDA Acceleration
The `to_davinci_cuda.sh` script leverages NVIDIA's CUDA cores to handle decoding and color space conversion (`yuv422p`). This reduces the load on the CPU and speeds up the preparation of files for editing in DaVinci Resolve.

### Requirements
- NVIDIA GPU with proprietary drivers.
- FFmpeg built with `--enable-cuda-llvm` and `--enable-nvdec`.
- `cuda` toolkit installed on the system.


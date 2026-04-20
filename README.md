# My Scripts 🛠️

A collection of vanilla Bash scripts for efficient media conversion using FFmpeg on Arch Linux. These scripts are optimized for performance, clean output, and support for NVIDIA hardware acceleration where applicable.

## Features
- **Catppuccin Mocha** themed CLI output.
- **Dynamic Input**: Accepts file paths as arguments or prompts for them.
- **Hardware Acceleration**: Uses NVIDIA NVDEC, NVENC, and CUDA pipelines to speed up heavy conversions.
- **Professional Formats**: Scripts for DaVinci Resolve, WebM, MP4, and high-quality Audio.

## Scripts Overview

### 🎬 Standard Video Conversion (CPU)
- `to_mp4.sh`: Standard H.264/AAC MP4 conversion.
- `to_mkv.sh`: High-quality MKV container conversion.
- `to_webm.sh`: VP9/Opus conversion for web usage.
- `to_davinci.sh`: Converts video to DNxHR (MOV) for DaVinci Resolve.

### ⚡ Hardware Accelerated Video (NVIDIA)
- `to_mp4_nvenc.sh` & `to_mkv_nvenc.sh`: Uses full NVIDIA hardware encoding (NVENC) for lightning-fast conversions.
- `to_webm_nvenc.sh`: Smart encoding script. Automatically uses ultra-fast **AV1 NVENC** hardware encoding if you are on a newer NVIDIA GPU (e.g., RTX 40-series). For older GPUs lacking VP9/AV1 hardware encoders, it intelligently falls back to a hybrid CUDA-decoding + CPU-encoding approach.
- `*_by_cuda.sh`: Hybrid scripts (`to_mp4_by_cuda.sh`, `to_mkv_by_cuda.sh`, `to_webm_by_cuda.sh`) that use the GPU strictly for decoding (`-hwaccel cuda`) to reduce system load, leaving the final encoding to the CPU.

### 🚀 DaVinci Resolve Specific
Because DaVinci Resolve on Linux has specific format requirements, this repository provides two distinct hardware-accelerated scripts for **NVIDIA GPUs**:
1. **`to_davinci_by_cuda.sh` (Basic NVDEC Decoding)**: Uses the GPU only to decode the input video. Works on almost all NVIDIA GPUs.
2. **`to_davinci_cuda_full.sh` (Full CUDA Pipeline)**: Strictly for CUDA-enabled GPUs. Keeps decoded frames in VRAM and uses CUDA compute cores for heavy YUV422p color space conversion, minimizing CPU overhead before the final DNxHR encode.

### 🎵 Audio Tools
- `to_aac.sh`: Converts audio to high-quality AAC (M4A).
- `to_mp3.sh`: Converts audio to 192k MP3.
- `extract_audio.sh`: Extracts the original audio stream directly from a video **without re-encoding**. Lightning fast and zero quality loss. Automatically detects the codec and uses the correct container.

### 🖼️ Utilities
- `extract_frames.sh`: Interactive script to extract a single high-quality frame at a specific timestamp, or multiple frames at a specific FPS interval.
- `to_gif.sh`: Creates high-quality GIFs from video files using intelligent FFmpeg palette generation.

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


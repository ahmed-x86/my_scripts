# My Scripts 🛠️

A collection of vanilla Bash scripts for efficient media conversion and downloading using FFmpeg and yt-dlp on Arch Linux. These scripts are optimized for performance, clean output, and support for NVIDIA hardware acceleration where applicable.

## Features
- **Catppuccin Mocha** themed CLI output.
- **Dynamic Input**: Accepts file paths/URLs as arguments or prompts for them.
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
- `to_webm_nvenc.sh`: Smart encoding script. Automatically uses ultra-fast **AV1 NVENC** if supported (RTX 40-series+), otherwise falls back to a hybrid CUDA-decoding + CPU-encoding approach.
- `*_by_cuda.sh`: Hybrid scripts that use the GPU strictly for decoding (`-hwaccel cuda`) to reduce system load.
### 📼 play video
- `play_local_video_by_ffplay` : this script for play local video in your device by ffplay
- `play_yt_video_online` : this script for play video in youtube without ADs by url (by mpv)
- `play_local_video.sh` : this script for play local video in your device by mpv

### 🚀 DaVinci Resolve Specific
Because DaVinci Resolve on Linux has specific format requirements, this repository provides two distinct hardware-accelerated scripts for **NVIDIA GPUs**:
1. **`to_davinci_by_cuda.sh`**: Basic NVDEC Decoding. Works on almost all NVIDIA GPUs.
2. **`to_davinci_cuda_full.sh`**: Full CUDA Pipeline. Uses CUDA compute cores for heavy YUV422p conversion entirely in VRAM.

### 📥 Downloader
- `download_yt.sh`: An interactive **yt-dlp** wrapper. It fetches available formats, allows you to choose specific video/audio combinations, handles automatic and manual subtitles (with embedding support), and can download/convert thumbnails to JPG.

### 🎵 Audio Tools
- `to_aac.sh` & `to_mp3.sh`: Standard audio conversion.
- `extract_audio.sh`: Extracts the original audio stream **without re-encoding**. Zero quality loss and lightning fast.

### 🖼️ Utilities
- `extract_frames.sh`: Interactive frame extraction (Single frame or batch extraction via FPS).
- `to_gif.sh`: Creates high-quality GIFs using intelligent FFmpeg palette generation.

## Usage

1. **Direct Argument**:
   ```bash
   ./to_mp4.sh "path/to/video.mkv"
   ./download_yt.sh "https://www.youtube.com/watch?v=..."
   ```

2. **Interactive Mode**:
   Simply run the script, and it will prompt you for the input.
   ```bash
   ./to_mp4.sh
   ```

## License
Licensed under the **GPL-3.0 License**. See the `LICENSE` file for details.

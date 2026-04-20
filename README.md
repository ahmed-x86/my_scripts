# My Scripts 🛠️

A collection of vanilla Bash scripts for efficient media conversion using FFmpeg on Arch Linux. These scripts are optimized for performance, clean output, and support for NVIDIA hardware acceleration where applicable.

## Features
- **Catppuccin Mocha** themed CLI output.
- **Dynamic Input**: Accepts file paths as arguments or prompts for them.
- **Hardware Acceleration**: Uses NVIDIA NVDEC and CUDA pipelines to speed up heavy conversions.
- **Professional Formats**: Scripts for DaVinci Resolve, WebM, MP4, and high-quality Audio.

## Scripts Overview

### 🎬 Video Conversion
- `to_mp4.sh`: Standard H.264/AAC MP4 conversion.
- `to_mkv.sh`: High-quality MKV container conversion.
- `to_webm.sh`: VP9/Opus conversion for web usage.
- `to_davinci.sh`: Converts video to DNxHR (MOV) for DaVinci Resolve (Pure CPU).

### 🚀 DaVinci Resolve & Hardware Acceleration
Because DaVinci Resolve on Linux has specific format requirements, this repository provides two distinct hardware-accelerated scripts for **NVIDIA GPUs**:

1. **`to-davinci_by-cuda.sh` (Basic NVDEC Decoding)**
   - **Compatibility:** Works on almost **all NVIDIA GPUs** (GeForce, Quadro, etc.) that feature a hardware video decoder (NVDEC).
   - **Mechanism:** Uses the GPU only to decode the input video (`-hwaccel cuda`). The color space conversion and encoding are offloaded back to the CPU.

2. **`to_davinci_cuda_full.sh` (Full CUDA Pipeline)**
   - **Compatibility:** Strictly for **NVIDIA CUDA-enabled GPUs**. It will **NOT** work on AMD or Intel GPUs. It requires the `cuda` toolkit installed on your system and an FFmpeg build compiled with CUDA filters support (e.g., `--enable-cuda-llvm`).
   - **Mechanism:** Keeps the decoded frames entirely within the GPU's VRAM (`-hwaccel_output_format cuda`). It utilizes the CUDA compute cores to perform the heavy YUV422p color space conversion (`scale_cuda`), minimizing CPU overhead to the absolute minimum before the final CPU-based DNxHR encoding.

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

# to_webm_nvenc.sh
## it for new nvidia GPUs
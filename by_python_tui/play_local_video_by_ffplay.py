#!/usr/bin/env python3
import os, sys, shutil, curses, subprocess
from tui_base import check_dependencies, setup_catppuccin_colors, prompt_input, prompt_choice

def get_gpu_info():
    try: return subprocess.check_output(["lspci"], text=True).lower()
    except: return ""

def get_video_codec(input_file):
    try: return subprocess.check_output(["ffprobe", "-v", "error", "-select_streams", "v:0", "-show_entries", "stream=codec_name", "-of", "default=noprint_wrappers=1:nokey=1", input_file], text=True).strip()
    except: return None

def main_tui(stdscr):
    curses.curs_set(0)
    setup_catppuccin_colors()
    
    input_file = prompt_input(stdscr, "📂 Enter Video File Path")
    if not input_file or not os.path.isfile(input_file): return
    
    options = [{"label": "CPU (Software Decoding)", "hw": "no"}]
    gpu_info = get_gpu_info()
    
    if "intel" in gpu_info: options.append({"label": "Intel GPU", "hw": "qsv"})
    if "amd" in gpu_info or "ati" in gpu_info: options.append({"label": "AMD GPU", "hw": "no"})
    if "nvidia" in gpu_info: options.append({"label": "Nvidia GPU", "hw": "cuvid"})
    
    idx = prompt_choice(stdscr, options, "🖥️ Select Decoding Device")
    selected = options[idx]
    
    codec = get_video_codec(input_file)
    ffplay_vcodec = []
    
    if selected['hw'] == "cuvid" and codec in ["h264", "hevc", "vp9"]:
        ffplay_vcodec = ["-vcodec", f"{codec}_cuvid"]
    elif selected['hw'] == "qsv" and codec in ["h264", "hevc"]:
        ffplay_vcodec = ["-vcodec", f"{codec}_qsv"]
        
    cmd = ["ffplay", "-autoexit"] + ffplay_vcodec + [input_file]
    
    # Suspend curses to show ffplay
    curses.endwin()
    print(f"\n🍿 Playing video via {selected['label']} (Codec: {codec})...\n")
    subprocess.run(cmd)
    stdscr.refresh()

if __name__ == "__main__":
    if not shutil.which("ffplay"):
        print("❌ ffplay is not installed.")
        sys.exit(1)
    curses.wrapper(main_tui)
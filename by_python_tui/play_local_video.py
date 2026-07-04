#!/usr/bin/env python3
import os, sys, shutil, curses, subprocess
from tui_base import setup_catppuccin_colors, prompt_input, prompt_choice, draw_logo

def get_gpu_info():
    try: return subprocess.check_output(["lspci"], text=True).lower()
    except: return ""

def main_tui(stdscr):
    curses.curs_set(0)
    setup_catppuccin_colors()
    
    input_file = prompt_input(stdscr, "📂 Enter Video File Path")
    if not input_file or not os.path.isfile(input_file): return
    
    options = [{"label": "CPU (Software Decoding)", "hw": "no"}]
    gpu_info = get_gpu_info()
    
    if "intel" in gpu_info: options.append({"label": "Intel GPU", "hw": "vaapi"})
    if "amd" in gpu_info or "ati" in gpu_info: options.append({"label": "AMD GPU", "hw": "vaapi"})
    if "nvidia" in gpu_info: options.append({"label": "Nvidia GPU", "hw": "nvdec"})
    
    idx = prompt_choice(stdscr, options, "🖥️ Select Decoding Device")
    selected = options[idx]
    
    extra_args = ["--vo=gpu", "--gpu-context=wayland"] if "Intel" in selected['label'] else []
    cmd = ["mpv", f"--hwdec={selected['hw']}"] + extra_args + [input_file]
    
    # إيقاف Curses مؤقتاً لتشغيل مشغل MPV
    curses.endwin()
    print(f"\n🍿 Playing video via {selected['label']}...\n")
    subprocess.run(cmd)
    stdscr.refresh()

if __name__ == "__main__":
    if not shutil.which("mpv"):
        print("❌ mpv is not installed.")
        sys.exit(1)
    curses.wrapper(main_tui)
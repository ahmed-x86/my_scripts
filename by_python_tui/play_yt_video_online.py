#!/usr/bin/env python3
import os, sys, shutil, curses, subprocess
from tui_base import setup_catppuccin_colors, prompt_input, prompt_choice

def get_lspci_vga():
    try: return subprocess.check_output(["lspci"], text=True).lower()
    except: return ""

def main_tui(stdscr):
    curses.curs_set(0)
    setup_catppuccin_colors()
    
    url = prompt_input(stdscr, "🔗 Enter YouTube URL")
    if not url: return
    
    options = [{"label": "CPU (Software Decoding)", "hw": "no"}]
    vga_info = get_lspci_vga()
    
    if "intel" in vga_info: options.append({"label": "Intel GPU", "hw": "vaapi"})
    if "amd" in vga_info: options.append({"label": "AMD GPU", "hw": "vaapi"})
    if "nvidia" in vga_info: options.append({"label": "Nvidia GPU", "hw": "nvdec"})
    
    idx = prompt_choice(stdscr, options, "🖥️ Select Decoding Device")
    selected = options[idx]
    
    extra_args = ["--vo=gpu", "--gpu-context=wayland"] if "Intel" in selected['label'] else []
    
    q_opts = [{"label": "Automatic (Best Quality)"}, {"label": "Manual Selection (Fetch Formats)"}]
    q_idx = prompt_choice(stdscr, q_opts, "📊 Select Quality Method")
    
    cmd = ["mpv", f"--hwdec={selected['hw']}"] + extra_args
    
    if q_idx == 1:
        # إيقاف Curses مؤقتاً لجلب وعرض صيغ yt-dlp في الشاشة العادية
        curses.endwin()
        print("\n⏳ Fetching video formats...\n")
        subprocess.run(["yt-dlp", "-F", url])
        format_code = input("\n✍️ Enter the format code (e.g., 299+140) or press Enter for best: ").strip()
        stdscr.refresh()
        
        if format_code:
            cmd.extend([f"--ytdl-format={format_code}", url])
        else:
            cmd.append(url)
    else:
        cmd.append(url)

    curses.endwin()
    print(f"\n🍿 Streaming video via {selected['label']}...\n")
    try:
        subprocess.run(cmd)
    except KeyboardInterrupt:
        pass
    stdscr.refresh()

if __name__ == "__main__":
    if not shutil.which("yt-dlp") or not shutil.which("mpv"):
        print("❌ yt-dlp or mpv is not installed.")
        sys.exit(1)
    curses.wrapper(main_tui)
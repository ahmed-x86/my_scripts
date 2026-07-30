#!/usr/bin/env python3

import os
import sys
import shutil
import subprocess
import curses
import json


LOGO = [
    " ██╗   ██╗████████╗    ██████╗ ██╗     ██████╗ ",
    " ╚██╗ ██╔╝╚══██╔══╝    ██╔══██╗██║     ██╔══██╗",
    "  ╚████╔╝    ██║       ██║  ██║██║     ██████╔╝",
    "   ╚██╔╝     ██║       ██║  ██║██║     ██╔═══╝ ",
    "    ██║      ██║       ██████╔╝███████╗██║     ",
    "    ╚═╝      ╚═╝       ╚═════╝ ╚══════╝╚═╝     "
]


def check_dependencies():
    if not shutil.which("yt-dlp"):
        print("❌ yt-dlp is not installed. Please install it first.")
        sys.exit(1)
    if not shutil.which("ffmpeg"):
        print("⚠️  ffmpeg is not installed. Features like embedding chapters/subs may fail.")
        print("Press Enter to continue anyway or Ctrl+C to abort...")
        try:
            input()
        except KeyboardInterrupt:
            sys.exit(1)


def setup_catppuccin_colors():
    curses.use_default_colors()
    try:
        if curses.can_change_color():
            def set_hex(col_id, hex_code):
                h = hex_code.lstrip('#')
                r, g, b = tuple(int(h[i:i+2], 16) for i in (0, 2, 4))
                curses.init_color(col_id, int(r*1000/255), int(g*1000/255), int(b*1000/255))

            BLUE = 200; set_hex(BLUE, "#89b4fa")
            MAUVE = 201; set_hex(MAUVE, "#cba6f7")
            GREEN = 202; set_hex(GREEN, "#a6e3a1")
            PEACH = 203; set_hex(PEACH, "#fab387")
            RED = 204; set_hex(RED, "#f38ba8")
            SURFACE1 = 205; set_hex(SURFACE1, "#45475a")
            OVERLAY0 = 206; set_hex(OVERLAY0, "#6c7086")
            BASE = 207; set_hex(BASE, "#1e1e2e")

            curses.init_pair(1, MAUVE, -1)
            curses.init_pair(2, GREEN, -1)
            curses.init_pair(3, PEACH, -1)
            curses.init_pair(4, BLUE, -1)
            curses.init_pair(5, OVERLAY0, -1)
            curses.init_pair(6, BASE, BLUE)
            curses.init_pair(7, RED, SURFACE1)
            curses.init_pair(8, BLUE, -1)
            curses.init_pair(9, PEACH, SURFACE1)
            curses.init_pair(10, BASE, GREEN)
        else:
            raise Exception()
    except:
        curses.init_pair(1, curses.COLOR_MAGENTA, -1)
        curses.init_pair(2, curses.COLOR_GREEN, -1)
        curses.init_pair(3, curses.COLOR_YELLOW, -1)
        curses.init_pair(4, curses.COLOR_BLUE, -1)
        curses.init_pair(5, curses.COLOR_CYAN, -1)
        curses.init_pair(6, curses.COLOR_BLACK, curses.COLOR_BLUE)
        curses.init_pair(7, curses.COLOR_RED, curses.COLOR_WHITE)
        curses.init_pair(8, curses.COLOR_BLUE, -1)
        curses.init_pair(9, curses.COLOR_YELLOW, curses.COLOR_WHITE)
        curses.init_pair(10, curses.COLOR_BLACK, curses.COLOR_GREEN)

def draw_logo(stdscr, start_y, max_x):
    for i, line in enumerate(LOGO):
        x = (max_x - len(line)) // 2
        stdscr.addstr(start_y + i, x, line, curses.color_pair(8) | curses.A_BOLD)
    return start_y + len(LOGO) + 2


def prompt_input(stdscr, title, default_text=""):
    curses.curs_set(1)
    input_str = default_text
    while True:
        stdscr.clear()
        max_y, max_x = stdscr.getmaxyx()
        try:
            logo_bottom = draw_logo(stdscr, max_y // 4 - 2, max_x)
            box_w = min(80, max_x - 4)
            start_x = (max_x - box_w) // 2
            input_y = logo_bottom + 3
            
            stdscr.addstr(input_y, start_x, f" {title} ", curses.color_pair(4) | curses.A_BOLD)
            stdscr.addstr(input_y + 1, start_x, f"╭{'─' * (box_w-2)}╮", curses.color_pair(5))
            stdscr.addstr(input_y + 2, start_x, "│ ", curses.color_pair(5))
            stdscr.addstr(input_y + 2, start_x + 2, input_str.ljust(box_w-4), curses.color_pair(1))
            stdscr.addstr(input_y + 2, start_x + box_w - 2, " │", curses.color_pair(5))
            stdscr.addstr(input_y + 3, start_x, f"╰{'─' * (box_w-2)}╯", curses.color_pair(5))
            stdscr.move(input_y + 2, start_x + 2 + len(input_str))
        except curses.error: pass
        stdscr.refresh()
        
        c = stdscr.getch()
        if c in (curses.KEY_ENTER, 10, 13): break
        elif c in (curses.KEY_BACKSPACE, 8, 127) and len(input_str) > 0: input_str = input_str[:-1]
        elif 32 <= c <= 126 and len(input_str) < max_x - 10: input_str += chr(c)
    curses.curs_set(0)
    return input_str.strip()

def prompt_choice_scrollable(stdscr, options, title):
    current_idx = 0
    scroll_offset = 0
    while True:
        stdscr.clear()
        max_y, max_x = stdscr.getmaxyx()
        try:
            logo_bottom = draw_logo(stdscr, 2, max_x)
            box_w = min(90, max_x - 4)
            start_x = (max_x - box_w) // 2
            start_y = logo_bottom + 2
            
            max_display = min(len(options), max_y - start_y - 4)
            
            if current_idx < scroll_offset: scroll_offset = current_idx
            elif current_idx >= scroll_offset + max_display: scroll_offset = current_idx - max_display + 1
            
            stdscr.addstr(start_y, start_x, f" {title} ", curses.color_pair(4) | curses.A_BOLD)
            stdscr.addstr(start_y + 1, start_x, f"╭{'─' * (box_w-2)}╮", curses.color_pair(5))
            
            for i in range(max_display):
                opt_idx = i + scroll_offset
                opt = options[opt_idx]
                y_pos = start_y + 2 + i
                
                label = f"  {opt.get('icon', '•')}  {opt['label']} "
                if len(label) > box_w - 4: label = label[:box_w-7] + "..."
                label_padded = label.ljust(box_w - 4)
                
                stdscr.addstr(y_pos, start_x, "│ ", curses.color_pair(5))
                if opt_idx == current_idx:
                    stdscr.addstr(y_pos, start_x + 2, label_padded, curses.color_pair(7) | curses.A_BOLD)
                else:
                    stdscr.addstr(y_pos, start_x + 2, label_padded, curses.color_pair(1))
                stdscr.addstr(y_pos, start_x + box_w - 2, " │", curses.color_pair(5))
                
            stdscr.addstr(start_y + 2 + max_display, start_x, f"╰{'─' * (box_w-2)}╯", curses.color_pair(5))
        except curses.error: pass
        stdscr.refresh()
        
        c = stdscr.getch()
        if c == curses.KEY_UP and current_idx > 0: current_idx -= 1
        elif c == curses.KEY_DOWN and current_idx < len(options) - 1: current_idx += 1
        elif c in (curses.KEY_ENTER, 10, 13): return current_idx

def show_loading(stdscr, msg=" ⏳ Fetching data from yt-dlp... "):
    stdscr.clear()
    max_y, max_x = stdscr.getmaxyx()
    try:
        draw_logo(stdscr, max_y // 4 - 2, max_x)
        stdscr.addstr(max_y // 2 + 2, (max_x - len(msg)) // 2, msg, curses.color_pair(3) | curses.A_BOLD)
    except curses.error: pass
    stdscr.refresh()


def fetch_video_info(url, state):
    cmd = ["yt-dlp", "-J", "--no-playlist", "--skip-download"]
    if state['cookie_type'] == 'browser': cmd.extend(["--cookies-from-browser", state['cookie_val']])
    elif state['cookie_type'] == 'file': cmd.extend(["--cookies", state['cookie_val']])
    cmd.append(url)
    
    try:
        res = subprocess.run(cmd, capture_output=True, text=True, check=True)
        return json.loads(res.stdout)
    except Exception:
        return None


def run_dashboard(stdscr, url):
    state = {
        'format': 'bestvideo+bestaudio/best',
        'format_label': 'Best Video + Audio',
        'skip_video': False,
        'subs': None,
        'subs_label': 'Skip',
        'thumb': False,
        'chapters': False,
        'split': False,
        'info': False,
        'cookie_type': None,
        'cookie_val': None,
        'archive': False,
        'save_dir': None,
        'save_dir_label': 'Here'
    }
    
    current_idx = 0
    cached_info = None

    while True:
        stdscr.clear()
        max_y, max_x = stdscr.getmaxyx()
        
        menu_items = [
            {"icon": "", "key": "Quality", "val": "Skip Completely" if state['skip_video'] else state['format_label']},
            {"icon": "📝", "key": "Subtitles", "val": state['subs_label']},
            {"icon": "🖼️", "key": "Thumbnail", "val": "Yes" if state['thumb'] else "Skip"},
            {"icon": "📑", "key": "Chapters", "val": ("Split" if state['split'] else "Embed") if state['chapters'] else "Skip"},
            {"icon": "📄", "key": "Metadata", "val": "Save to .txt" if state['info'] else "Skip"},
            {"icon": "🍪", "key": "Cookies", "val": state['cookie_type'].capitalize() if state['cookie_type'] else "Skip"},
            {"icon": "📦", "key": "Archive", "val": "Use Archive" if state['archive'] else "Skip"},
            {"icon": "📁", "key": "Location", "val": state['save_dir_label']},
            {"icon": "🚀", "key": "START DOWNLOAD", "val": ""}
        ]
        
        try:
            logo_bottom = draw_logo(stdscr, 2, max_x)
            box_w = min(85, max_x - 4)
            start_x = (max_x - box_w) // 2
            start_y = logo_bottom + 1
            
            stdscr.addstr(start_y, start_x, " 🛠️  Download Configuration Dashboard ", curses.color_pair(4) | curses.A_BOLD)
            stdscr.addstr(start_y + 1, start_x, f"╭{'─' * (box_w-2)}╮", curses.color_pair(5))
            
            for i, item in enumerate(menu_items):
                y_pos = start_y + 2 + i
                left_text = f"  {item['icon']}  {item['key']}"
                
                # Truncate value string if it's too long
                display_val = item['val']
                if len(display_val) > 30:
                    display_val = display_val[:27] + "..."
                right_text = f"[{display_val}]  " if item['val'] else "  "
                
                pad_len = box_w - len(left_text) - len(right_text) - 2
                pad = " " * pad_len if pad_len > 0 else ""
                
                stdscr.addstr(y_pos, start_x, "│ ", curses.color_pair(5))
                
                if i == current_idx:
                    if item['key'] == "START DOWNLOAD":
                        stdscr.addstr(y_pos, start_x + 2, (left_text + pad + right_text), curses.color_pair(10) | curses.A_BOLD)
                    else:
                        stdscr.addstr(y_pos, start_x + 2, (left_text + pad + right_text), curses.color_pair(6) | curses.A_BOLD)
                else:
                    if item['key'] == "START DOWNLOAD":
                        stdscr.addstr(y_pos, start_x + 2, left_text, curses.color_pair(2) | curses.A_BOLD)
                    else:
                        stdscr.addstr(y_pos, start_x + 2, left_text, curses.color_pair(1))
                    stdscr.addstr(y_pos, start_x + 2 + len(left_text) + len(pad), right_text, curses.color_pair(3))
                    
                stdscr.addstr(y_pos, start_x + box_w - 2, " │", curses.color_pair(5))
                
            stdscr.addstr(start_y + 2 + len(menu_items), start_x, f"╰{'─' * (box_w-2)}╯", curses.color_pair(5))
            stdscr.addstr(max_y - 2, 0, " Use UP/DOWN to navigate, ENTER to change, CTRL+C to quit. ".center(max_x), curses.color_pair(5))
        except curses.error: pass
        stdscr.refresh()
        
        c = stdscr.getch()
        if c == curses.KEY_UP and current_idx > 0: current_idx -= 1
        elif c == curses.KEY_DOWN and current_idx < len(menu_items) - 1: current_idx += 1
        elif c in (curses.KEY_ENTER, 10, 13):
            # 1. Video Quality Action
            if current_idx == 0:
                opts = [
                    {"icon": "⭐", "label": "Default (Best Video + Audio)"},
                    {"icon": "🎵", "label": "Audio Only (Best Audio)"},
                    {"icon": "🚫", "label": "Skip Completely (No Video/Audio)"},
                    {"icon": "☁️", "label": "Fetch Custom Formats (Select V + A)..."},
                    {"icon": "🔧", "label": "Manual Format Code"}
                ]
                choice = prompt_choice_scrollable(stdscr, opts, "  Select Quality")
                if choice == 0: state.update({'format': 'bestvideo+bestaudio/best', 'format_label': 'Best Video + Audio', 'skip_video': False})
                elif choice == 1: state.update({'format': 'bestaudio/best', 'format_label': 'Audio Only', 'skip_video': False})
                elif choice == 2: state.update({'skip_video': True})
                elif choice == 3:
                    show_loading(stdscr)
                    if not cached_info: cached_info = fetch_video_info(url, state)
                    
                    if cached_info and 'formats' in cached_info:
                        v_opts = [
                            {"icon": "🌟", "label": "Best Available Video", "id": "bestvideo"},
                            {"icon": "🚫", "label": "Skip Video", "id": "none"}
                        ]
                        a_opts = [
                            {"icon": "🌟", "label": "Best Available Audio", "id": "bestaudio"},
                            {"icon": "🚫", "label": "Skip Audio", "id": "none"}
                        ]
                        
                        for f in cached_info['formats'][::-1]:
                            fid = str(f.get('format_id', ''))
                            ext = f.get('ext', '')
                            vcodec = f.get('vcodec', 'none')
                            acodec = f.get('acodec', 'none')
                            
                            if vcodec != 'none':
                                res = f.get('resolution', '?')
                                fps = f.get('fps', '')
                                fps_str = f"{fps}fps" if fps else ""
                                v_opts.append({"icon": "🎬", "label": f"{res} {fps_str} ({ext}) [{vcodec}]", "id": fid})
                                
                            if acodec != 'none':
                                abr = f.get('abr', 0)
                                abr_str = f"{int(abr)}kbps" if abr else ""
                                a_opts.append({"icon": "🎵", "label": f"{abr_str} ({ext}) [{acodec}]".strip(), "id": fid})
                        
                        
                        v_choice = prompt_choice_scrollable(stdscr, v_opts, "🎬  Select Video Quality")
                        sel_v = v_opts[v_choice]
                        
                        
                        a_choice = prompt_choice_scrollable(stdscr, a_opts, "🎵  Select Audio Quality")
                        sel_a = a_opts[a_choice]
                        
                        
                        if sel_v['id'] == 'none' and sel_a['id'] == 'none':
                            state.update({'skip_video': True, 'format_label': 'Skip Completely', 'format': 'none'})
                        elif sel_v['id'] == 'none':
                            state.update({'format': sel_a['id'], 'format_label': f"Audio: {sel_a['id']}", 'skip_video': False})
                        elif sel_a['id'] == 'none':
                            state.update({'format': sel_v['id'], 'format_label': f"Video: {sel_v['id']}", 'skip_video': False})
                        else:
                            state.update({
                                'format': f"{sel_v['id']}+{sel_a['id']}", 
                                'format_label': f"V:{sel_v['id']} + A:{sel_a['id']}", 
                                'skip_video': False
                            })
                            
                elif choice == 4:
                    custom = prompt_input(stdscr, "🔧 Enter format code (e.g. 137+140)")
                    if custom: state.update({'format': custom, 'format_label': custom, 'skip_video': False})

            # 2. Subtitles Action
            elif current_idx == 1:
                opts = [
                    {"icon": "🚫", "label": "Skip"},
                    {"icon": "🇺🇸", "label": "English (en)"},
                    {"icon": "🇸🇦", "label": "Arabic (ar)"},
                    {"icon": "🌍", "label": "All Subtitles"},
                    {"icon": "☁️", "label": "Fetch Available Subtitles..."},
                    {"icon": "🔧", "label": "Custom Language Code"}
                ]
                choice = prompt_choice_scrollable(stdscr, opts, "📝 Select Subtitles")
                if choice == 0: state.update({'subs': None, 'subs_label': 'Skip'})
                elif choice == 1: state.update({'subs': 'en', 'subs_label': 'English'})
                elif choice == 2: state.update({'subs': 'ar', 'subs_label': 'Arabic'})
                elif choice == 3: state.update({'subs': 'all', 'subs_label': 'All Subtitles'})
                elif choice == 4:
                    show_loading(stdscr)
                    if not cached_info: cached_info = fetch_video_info(url, state)
                    if cached_info:
                        sub_keys = list(cached_info.get('subtitles', {}).keys()) + list(cached_info.get('automatic_captions', {}).keys())
                        sub_keys = list(set(sub_keys))
                        if sub_keys:
                            sub_opts = [{"icon": "💬", "label": lang} for lang in sorted(sub_keys)]
                            s_choice = prompt_choice_scrollable(stdscr, sub_opts, "☁️  Available Subtitles")
                            sel_lang = sub_opts[s_choice]['label']
                            state.update({'subs': sel_lang, 'subs_label': sel_lang})
                        else:
                            prompt_input(stdscr, "⚠️ No subtitles found. Press Enter to return.")
                elif choice == 5:
                    custom = prompt_input(stdscr, "🔧 Enter language code (e.g. fr, de)")
                    if custom: state.update({'subs': custom, 'subs_label': custom})

            
            elif current_idx == 2:
                state['thumb'] = not state['thumb']
            
            
            elif current_idx == 3:
                opts = [{"icon": "🚫", "label": "Skip"}, {"icon": "📑", "label": "Embed Only"}, {"icon": "✂️", "label": "Embed & Split"}]
                choice = prompt_choice_scrollable(stdscr, opts, "📑 Chapters Config")
                if choice == 0: state.update({'chapters': False, 'split': False})
                elif choice == 1: state.update({'chapters': True, 'split': False})
                elif choice == 2: state.update({'chapters': True, 'split': True})

            
            elif current_idx == 4:
                state['info'] = not state['info']

            
            elif current_idx == 5:
                opts = [{"icon": "🚫", "label": "Skip"}, {"icon": "🌐", "label": "Browser"}, {"icon": "📁", "label": "Text File"}]
                choice = prompt_choice_scrollable(stdscr, opts, "🍪 Cookies Config")
                if choice == 0: state.update({'cookie_type': None, 'cookie_val': None})
                elif choice == 1:
                    browser = prompt_input(stdscr, "🌐 Enter browser name (e.g. zen, chrome)")
                    if browser: state.update({'cookie_type': 'browser', 'cookie_val': browser})
                elif choice == 2:
                    c_file = prompt_input(stdscr, "📁 Enter absolute path to cookies.txt")
                    if c_file: state.update({'cookie_type': 'file', 'cookie_val': c_file})

            
            elif current_idx == 6:
                state['archive'] = not state['archive']

            
            elif current_idx == 7:
                opts = [
                    {"icon": "📍", "label": "Here (Current Directory)"},
                    {"icon": "📥", "label": "Downloads Folder (~/Downloads)"},
                    {"icon": "🔧", "label": "Custom Path"}
                ]
                choice = prompt_choice_scrollable(stdscr, opts, "📁 Select Save Location")
                if choice == 0:
                    state.update({'save_dir': None, 'save_dir_label': 'Here'})
                elif choice == 1:
                    dl_path = os.path.expanduser("~/Downloads")
                    state.update({'save_dir': dl_path, 'save_dir_label': 'Downloads'})
                elif choice == 2:
                    custom_path = prompt_input(stdscr, "🔧 Enter absolute path (e.g., /home/user/Videos)")
                    if custom_path:
                        state.update({'save_dir': custom_path, 'save_dir_label': custom_path})

            # 9. START DOWNLOAD
            elif current_idx == 8:
                return state


def execute_download(stdscr, url, state):
    dl_args = ["yt-dlp", "--no-playlist", "--continue"]
    
    if state['skip_video']: dl_args.append("--skip-download")
    else: dl_args.extend(["-f", state['format']])
    
    if state['subs']:
        if state['subs'] == 'all': dl_args.extend(["--all-subs", "--write-auto-sub", "--embed-subs"])
        else: dl_args.extend(["--write-sub", "--write-auto-sub", "--sub-lang", state['subs'], "--embed-subs"])
    
    if state['thumb']: dl_args.extend(["--write-thumbnail", "--convert-thumbnails", "jpg"])
    
    if state['chapters']:
        dl_args.append("--embed-chapters")
        if state['split']: dl_args.append("--split-chapters")
        
    if state['info']:
        info_template = "Title: %(title)s\nChannel: %(uploader)s\nViews: %(view_count)s\n=========================\n%(description)s"
        dl_args.extend(["--print-to-file", info_template, "%(title)s_info.txt"])
        
    if state['cookie_type'] == 'browser': dl_args.extend(["--cookies-from-browser", state['cookie_val']])
    elif state['cookie_type'] == 'file': dl_args.extend(["--cookies", state['cookie_val']])
        
    if state['archive']: dl_args.extend(["--download-archive", "downloaded_archive.txt"])
    
    # Save directory logic
    if state['save_dir']:
        dl_args.extend(["-P", state['save_dir']])
        
    dl_args.append(url)

    max_y, max_x = stdscr.getmaxyx()
    p = subprocess.Popen(dl_args, stdout=subprocess.PIPE, stderr=subprocess.STDOUT, text=True, bufsize=1)
    
    box_w = min(100, max_x - 4)
    box_y = max_y - 6
    start_x = (max_x - box_w) // 2

    while True:
        line = p.stdout.readline()
        if not line and p.poll() is not None: break
            
        line = line.strip()
        if line:
            stdscr.clear()
            try:
                draw_logo(stdscr, 2, max_x)
                stdscr.addstr(box_y - 1, start_x, "   Downloading in progress... ", curses.color_pair(4) | curses.A_BOLD)
                
                display_line = line if len(line) <= box_w - 4 else line[:box_w-7] + "..."
                stdscr.addstr(box_y, start_x, f"╭{'─' * (box_w-2)}╮", curses.color_pair(5))
                stdscr.addstr(box_y + 1, start_x, "│ ", curses.color_pair(5))
                stdscr.addstr(box_y + 1, start_x + 2, display_line.ljust(box_w-4), curses.color_pair(1))
                stdscr.addstr(box_y + 1, start_x + box_w - 2, " │", curses.color_pair(5))
                stdscr.addstr(box_y + 2, start_x, f"╰{'─' * (box_w-2)}╯", curses.color_pair(5))
            except curses.error: pass
            stdscr.refresh()
            
    stdscr.clear()
    try:
        draw_logo(stdscr, max_y // 4 - 2, max_x)
        if p.returncode == 0:
            msg = "   Download Completed Successfully! "
            color = curses.color_pair(2)
        else:
            msg = "   Download Failed! Check terminal for details. "
            color = curses.color_pair(7)
            
        stdscr.addstr(max_y // 2 + 2, (max_x - len(msg)) // 2, msg, color | curses.A_BOLD)
        stdscr.addstr(max_y // 2 + 4, (max_x - 22) // 2, " Press any key to exit ", curses.color_pair(5))
    except curses.error: pass
    stdscr.refresh()
    stdscr.getch()

def main_tui(stdscr):
    curses.curs_set(0)
    setup_catppuccin_colors()
    
    url = prompt_input(stdscr, "  Enter YouTube URL")
    if not url: return

    final_state = run_dashboard(stdscr, url)
    
    if final_state:
        execute_download(stdscr, url, final_state)

if __name__ == "__main__":
    check_dependencies()
    try:
        curses.wrapper(main_tui)
    except KeyboardInterrupt:
        print("\n🛑 Execution interrupted by user.")
        sys.exit(0)
    except Exception as e:
        print(f"\n❌ An unexpected error occurred: {e}")
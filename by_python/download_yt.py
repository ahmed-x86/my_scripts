#!/usr/bin/env python3

import os
import sys
import shutil
import subprocess

# Colors
RED = '\033[38;2;243;139;168m'
GREEN = '\033[38;2;166;227;161m'
BLUE = '\033[38;2;137;180;250m'
YELLOW = '\033[38;2;249;226;175m'
NC = '\033[0m'

def check_dependencies():
    if not shutil.which("yt-dlp"):
        print(f"{RED}❌ yt-dlp is not installed. (Run: sudo pacman -S yt-dlp){NC}")
        sys.exit(1)
    
    if not shutil.which("ffmpeg"):
        print(f"{YELLOW}⚠️ ffmpeg is not installed. Some features (like embedding chapters/subs) may not work. (Run: sudo pacman -S ffmpeg){NC}")

def main():
    check_dependencies()

    if len(sys.argv) >= 2:
        url = sys.argv[1]
    else:
        print(f"{BLUE}🔗 Please enter the YouTube URL enclosed in quotes \" \":{NC}")
        url = input("> ").strip()
        
    url = url.strip('"\'')

    if not url:
        print(f"{RED}❌ URL cannot be empty{NC}")
        sys.exit(1)

    dl_args = ["yt-dlp"]

    # Option to skip downloading the video itself
    print(f"{BLUE}🎬 Do you want to download the video itself? (y/n):{NC}")
    want_video = input("> ").strip().lower()

    if want_video == 'n':
        dl_args.append("--skip-download")
    else:
        print(f"{YELLOW}⏳ Fetching video formats...{NC}")
        subprocess.run(["yt-dlp", "-F", url])
        
        print(f"{BLUE}📊 Enter the format code (e.g., 299+140 for 1080p60, or 'best'):{NC}")
        format_code = input("> ").strip()

        if not format_code:
            format_code = "bestvideo+bestaudio/best"
        
        dl_args.extend(["-f", format_code])

    print(f"{BLUE}📝 Do you want to download subtitles? (y/n):{NC}")
    want_subs = input("> ").strip().lower()

    if want_subs == 'y':
        print(f"{YELLOW}⏳ Fetching available subtitles...{NC}")
        subprocess.run(["yt-dlp", "--list-subs", url])
        
        print(f"{BLUE}✍️ Enter the subtitle language code (e.g., ar, en) or type 'all':{NC}")
        sub_lang = input("> ").strip()
        
        if sub_lang == "all":
            dl_args.extend(["--write-sub", "--write-auto-sub", "--all-subs", "--embed-subs"])
        elif sub_lang:
            dl_args.extend(["--write-sub", "--write-auto-sub", "--sub-lang", sub_lang, "--embed-subs"])

    print(f"{BLUE}🖼️ Do you want to download the thumbnail? (y/n):{NC}")
    want_thumb = input("> ").strip().lower()

    if want_thumb == 'y':
        dl_args.extend(["--write-thumbnail", "--convert-thumbnails", "jpg"])

    print(f"{BLUE}📑 Do you want to embed chapters into the video? (y/n):{NC}")
    want_chapters = input("> ").strip().lower()
    
    if want_chapters == 'y':
        dl_args.extend(["--embed-chapters"])

    print(f"{BLUE}✂️ Do you want to split the video into separate files based on chapters? (y/n):{NC}")
    split_chapters = input("> ").strip().lower()
    
    if split_chapters == 'y':
        dl_args.extend(["--split-chapters"])

    print(f"{BLUE}📄 Do you want to save video info (description, likes, views) to a txt file? (y/n):{NC}")
    want_info = input("> ").strip().lower()
    
    if want_info == 'y':
        info_template = (
            "Title: %(title)s\n"
            "Channel: %(uploader)s\n"
            "Upload Date: %(upload_date)s\n"
            "Views: %(view_count)s\n"
            "Likes: %(like_count)s\n\n"
            "=========================\n"
            "Description:\n"
            "%(description)s"
        )
        dl_args.extend(["--print-to-file", info_template, "%(title)s_info.txt"])

    print(f"{BLUE}🍪 Do you want to use cookies for authentication? (y/n):{NC}")
    want_cookies = input("> ").strip().lower()
    
    if want_cookies == 'y':
        print(f"{BLUE}1) From a browser (e.g., zen, firefox, chrome)\n2) From a text file{NC}")
        cookie_choice = input("> ").strip()
        
        if cookie_choice == '1':
            print(f"{BLUE}🌐 Enter browser name (e.g., zen, firefox, chrome, brave, edge):{NC}")
            browser = input("> ").strip().lower()
            if browser:
                dl_args.extend(["--cookies-from-browser", browser])
        elif cookie_choice == '2':
            print(f"{BLUE}📁 Enter the path to the cookies file:{NC}")
            cookie_file = input("> ").strip().strip('"\'')
            if os.path.isfile(cookie_file):
                dl_args.extend(["--cookies", cookie_file])
            else:
                print(f"{RED}❌ File not found. Proceeding without cookies.{NC}")

    print(f"{YELLOW}⏳ Starting download...{NC}")
    dl_args.append(url)

    try:
        process = subprocess.run(dl_args)
        if process.returncode == 0:
            print(f"{GREEN}✅ Download completed successfully!{NC}")
        else:
            print(f"{RED}❌ Download failed!{NC}")
            
    except KeyboardInterrupt:
        print(f"\n{RED}🛑 Download interrupted by user.{NC}")
        sys.exit(1)

if __name__ == "__main__":
    main()
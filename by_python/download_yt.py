#!/usr/bin/env python3
import os
import sys
import shutil
import subprocess
import argparse

# Colors for terminal output
RED = '\033[38;2;243;139;168m'
GREEN = '\033[38;2;166;227;161m'
BLUE = '\033[38;2;137;180;250m'
YELLOW = '\033[38;2;249;226;175m'
NC = '\033[0m'

def get_yes_no(prompt, default='y'):
    """Function to ensure the user inputs (y or n) correctly"""
    while True:
        choice = input(f"{prompt} [{default.upper()}/{( 'y' if default=='n' else 'n' )}]: ").strip().lower()
        if not choice:
            return default == 'y'
        if choice in ['y', 'yes']:
            return True
        if choice in ['n', 'no']:
            return False
        print(f"{RED}❌ Invalid input! Please enter 'y' for yes or 'n' for no.{NC}")

def check_dependencies():
    # Modified error message to be OS-independent
    if not shutil.which("yt-dlp"):
        print(f"{RED}❌ yt-dlp is not installed. Please install it first.{NC}")
        sys.exit(1)
    
    if not shutil.which("ffmpeg"):
        print(f"{YELLOW}⚠️ ffmpeg is not installed. Some features (like embedding chapters/subs) may not work.{NC}")

def main():
    check_dependencies()

    # 4. Use argparse to add command-line features
    parser = argparse.ArgumentParser(description="Interactive yt-dlp wrapper script")
    parser.add_argument("url", nargs="?", help="The YouTube URL to download")
    parser.add_argument("--proxy", help="Use proxy (e.g., http://127.0.0.1:8080)")
    parser.add_argument("--limit-rate", help="Limit download rate (e.g., 500K, 2M)")
    parser.add_argument("--archive", help="Download archive file to avoid re-downloading")
    args = parser.parse_args()

    url = args.url
    if not url:
        print(f"{BLUE}🔗 Please enter the YouTube URL:{NC}")
        url = input("> ").strip()
        
    url = url.strip('"\'')

    # 1. Validate the URL
    if not url or not url.startswith(("http://", "https://")):
        print(f"{RED}❌ Invalid URL! It must start with http:// or https://{NC}")
        sys.exit(1)

    dl_args = ["yt-dlp"]

    # 7. Resume download if interrupted (Resume)
    dl_args.append("--continue")

    # 8. Prevent downloading playlists as requested
    dl_args.append("--no-playlist")

    # Option to skip downloading the video itself
    if not get_yes_no(f"{BLUE}🎬 Do you want to download the video itself?", 'y'):
        dl_args.append("--skip-download")
    else:
        print(f"{YELLOW}⏳ Fetching video formats...{NC}")
        try:
            subprocess.run(["yt-dlp", "-F", url], check=True)
        except subprocess.CalledProcessError:
            print(f"{RED}❌ Failed to fetch formats. Please check the URL or your internet connection.{NC}")
            sys.exit(1)
        
        # 2. Basic validation for the format code
        print(f"{BLUE}📊 Enter the format code (e.g., 299+140) [Default: bestvideo+bestaudio/best]:{NC}")
        format_code = input("> ").strip()
        if not format_code:
            format_code = "bestvideo+bestaudio/best"
        dl_args.extend(["-f", format_code])

    # 3. Validate subtitle language
    if get_yes_no(f"{BLUE}📝 Do you want to download subtitles?", 'n'):
        print(f"{YELLOW}⏳ Fetching available subtitles...{NC}")
        subprocess.run(["yt-dlp", "--list-subs", url])
        
        print(f"{BLUE}✍️ Enter the subtitle language code (e.g., ar, en) or type 'all' [Default: ar]:{NC}")
        sub_lang = input("> ").strip()
        
        if sub_lang.lower() == "all":
            dl_args.extend(["--write-sub", "--write-auto-sub", "--all-subs", "--embed-subs"])
        else:
            if not sub_lang:
                sub_lang = "ar"
            # Simple check for language code length
            if len(sub_lang) < 2:
                print(f"{YELLOW}⚠️ Language code seems unusual, but proceeding anyway...{NC}")
            dl_args.extend(["--write-sub", "--write-auto-sub", "--sub-lang", sub_lang, "--embed-subs"])

    if get_yes_no(f"{BLUE}🖼️ Do you want to download the thumbnail?", 'n'):
        dl_args.extend(["--write-thumbnail", "--convert-thumbnails", "jpg"])

    if get_yes_no(f"{BLUE}📑 Do you want to embed chapters into the video?", 'n'):
        dl_args.extend(["--embed-chapters"])

    if get_yes_no(f"{BLUE}✂️ Do you want to split the video into separate files based on chapters?", 'n'):
        dl_args.extend(["--split-chapters"])

    if get_yes_no(f"{BLUE}📄 Do you want to save video info to a txt file?", 'n'):
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

    if get_yes_no(f"{BLUE}🍪 Do you want to use cookies for authentication?", 'n'):
        print(f"{BLUE}1) From a browser (e.g., zen, firefox, chrome)\n2) From a text file\n[Press Enter to skip]{NC}")
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

    # 5. Choose save directory
    print(f"{BLUE}📁 Enter save directory (Leave blank for current directory):{NC}")
    save_dir = input("> ").strip()
    if save_dir:
        dl_args.extend(["-P", save_dir])

    # 6. Choose filename template
    print(f"{BLUE}🏷️ Enter filename template (Leave blank for default: '%(title)s.%(ext)s'):{NC}")
    file_name = input("> ").strip()
    if file_name:
        if "%(ext)s" not in file_name:
            file_name += ".%(ext)s"
        dl_args.extend(["-o", file_name])

    # Apply argparse inputs (Proxy, Rate limit, Archive)
    if args.proxy:
        dl_args.extend(["--proxy", args.proxy])
    
    if args.limit_rate:
        dl_args.extend(["--limit-rate", args.limit_rate])
        
    if args.archive:
        dl_args.extend(["--download-archive", args.archive])
    else:
        # 11. Archive (Interactive question if not passed via argparse)
        if get_yes_no(f"{BLUE}📦 Do you want to use a download archive to prevent re-downloading later?", 'n'):
            dl_args.extend(["--download-archive", "downloaded_archive.txt"])

    # Append the URL at the end
    dl_args.append(url)

    # 12. Print the final command before execution
    final_command = " ".join(dl_args)
    print(f"\n{YELLOW}🚀 Final Command:{NC}")
    print(f"{GREEN}{final_command}{NC}\n")

    print(f"{YELLOW}⏳ Starting download...{NC}")
    
    # 13. Detailed error handling using try-except
    try:
        # check=True will raise CalledProcessError if the command fails
        process = subprocess.run(dl_args, check=True)
        print(f"{GREEN}✅ Download completed successfully!{NC}")
        
    except subprocess.CalledProcessError as e:
        print(f"\n{RED}❌ Download failed! yt-dlp exited with code {e.returncode}{NC}")
        print(f"{YELLOW}💡 You can review the final command above and try running it manually to see the exact issue.{NC}")
    except FileNotFoundError:
        print(f"\n{RED}❌ Error: Program not found. Make sure yt-dlp is installed and in your PATH.{NC}")
    except KeyboardInterrupt:
        print(f"\n{RED}🛑 Download interrupted by user (Ctrl+C).{NC}")
        sys.exit(1)
    except Exception as e:
        print(f"\n{RED}❌ An unexpected error occurred: {e}{NC}")

if __name__ == "__main__":
    main()
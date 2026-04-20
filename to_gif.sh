#!/bin/bash
# to_gif.sh

RED='\033[38;2;243;139;168m'; YELLOW='\033[38;2;249;226;175m'; NC='\033[0m'


output_file="${name}.gif"
echo -e "${YELLOW}⏳ Generating high-quality GIF...${NC}"

ffmpeg -hide_banner -loglevel error -stats -i "$input_file" \
    -vf "fps=15,scale=720:-1:flags=lanczos,split[s0][s1];[s0]palettegen[p];[s1][p]paletteuse" \
    -loop 0 "$output_file"

echo -e "${GREEN}✅ GIF Created: $output_file${NC}"
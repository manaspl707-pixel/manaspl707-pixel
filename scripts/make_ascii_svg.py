import os
import math
from PIL import Image

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

INPUT = os.path.join(BASE_DIR, "source-prepped.png")
OUTPUT = os.path.join(BASE_DIR, "manas-ascii.svg")

# ASCII settings
COLS = 150
ART_WIDTH = 760

# ASCII characters from light to dark
RAMP = " .:-=+*#%@"

# Animation settings
ROW_DELAY = 0.035
ROW_DURATION = 0.32


def image_to_ascii(image_path):
    img = Image.open(image_path).convert("L")

    # Keep terminal characters approximately proportional
    cell_width = ART_WIDTH / COLS
    cell_height = cell_width * 1.8

    rows = max(1, round(img.height / img.width * COLS / 1.8))

    img = img.resize((COLS, rows))

    pixels = list(img.getdata())

    lines = []

    for y in range(rows):
        line = ""

        for x in range(COLS):
            value = pixels[y * COLS + x]

            # Darker pixels → darker ASCII character
            index = int((255 - value) / 256 * len(RAMP))
            index = min(index, len(RAMP) - 1)

            line += RAMP[index]

        lines.append(line.rstrip())

    return lines, rows, cell_height


def make_svg(lines, rows, cell_height):
    terminal_header = 42
    top_padding = 30
    bottom_padding = 48

    art_height = rows * cell_height
    height = terminal_header + top_padding + art_height + bottom_padding

    font_size = max(4, cell_height * 0.92)

    svg = []

    svg.append(
        f'''<svg xmlns="http://www.w3.org/2000/svg"
        width="{ART_WIDTH}"
        height="{height:.0f}"
        viewBox="0 0 {ART_WIDTH:.0f} {height:.0f}">
'''
    )

    # Background
    svg.append(
        f'''
<defs>
    <linearGradient id="bg" x1="0" y1="0" x2="0" y2="1">
        <stop offset="0%" stop-color="#111111"/>
        <stop offset="100%" stop-color="#050505"/>
    </linearGradient>

    <filter id="glow">
        <feGaussianBlur stdDeviation="1.4" result="blur"/>
        <feMerge>
            <feMergeNode in="blur"/>
            <feMergeNode in="SourceGraphic"/>
        </feMerge>
    </filter>
</defs>

<rect width="100%" height="100%" rx="10" fill="url(#bg)"/>
'''
    )

    # Terminal top bar
    svg.append(
        '''
<rect x="0" y="0" width="100%" height="42"
      fill="#191919"/>

<circle cx="18" cy="21" r="5" fill="#ff5f56"/>
<circle cx="36" cy="21" r="5" fill="#ffbd2e"/>
<circle cx="54" cy="21" r="5" fill="#27c93f"/>

<text x="75" y="26"
      font-family="monospace"
      font-size="13"
      fill="#aaaaaa">
manas@github: ~/profile
</text>
'''
    )

    # Title
    title_y = terminal_header + 22

    svg.append(
        f'''
<text x="24"
      y="{title_y}"
      font-family="monospace"
      font-size="14"
      fill="#aaaaaa">
manas@github: ~$ ./portrait.sh
</text>
'''
    )

    # ASCII artwork
    start_y = terminal_header + top_padding + font_size

    for row, line in enumerate(lines):

        y = start_y + row * cell_height

        delay = row * ROW_DELAY
        duration = ROW_DURATION

        escaped = (
            line.replace("&", "&amp;")
                .replace("<", "&lt;")
                .replace(">", "&gt;")
        )

        # Invisible clipping rectangle that expands from left to right
        clip_id = f"rowClip{row}"

        svg.append(
            f'''
<clipPath id="{clip_id}">
    <rect x="0"
          y="{y - font_size}"
          width="0"
          height="{cell_height + 4}">
        <animate
            attributeName="width"
            from="0"
            to="{ART_WIDTH}"
            begin="{delay:.3f}s"
            dur="{duration:.3f}s"
            fill="freeze"/>
    </rect>
</clipPath>

<text x="24"
      y="{y:.2f}"
      font-family="monospace"
      font-size="{font_size:.2f}px"
      font-weight="600"
      letter-spacing="0"
      fill="#eeeeee"
      clip-path="url(#{clip_id})"
      filter="url(#glow)">
    {escaped}
</text>
'''
        )

    # Bottom command/status
    status_y = height - 25

    svg.append(
        f'''
<text x="24"
      y="{status_y}"
      font-family="monospace"
      font-size="13"
      fill="#aaaaaa">
manas@github:~$ whoami Manas
</text>

<rect x="270"
      y="{status_y - 13}"
      width="7"
      height="15"
      fill="#eeeeee">
    <animate
        attributeName="opacity"
        values="1;0;1"
        dur="1s"
        repeatCount="indefinite"/>
</rect>

</svg>
'''
    )

    return "".join(svg)


def main():
    if not os.path.exists(INPUT):
        raise FileNotFoundError(
            f"Could not find: {INPUT}"
        )

    print("Loading:", INPUT)

    lines, rows, cell_height = image_to_ascii(INPUT)

    print(f"ASCII size: {COLS} columns × {rows} rows")

    svg = make_svg(lines, rows, cell_height)

    with open(OUTPUT, "w", encoding="utf-8") as f:
        f.write(svg)

    print()
    print("SUCCESS!")
    print("Created:", OUTPUT)


if __name__ == "__main__":
    main()

import os
import math
from PIL import Image

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

INPUT = os.path.join(BASE_DIR, "source-prepped.png")
OUTPUT = os.path.join(BASE_DIR, "manas-ascii.svg")

# ASCII settings
COLS = 220
ART_WIDTH = 820

# Sparse-to-dense characters
RAMP = " .:-=+*#%@"

# Animation settings
ROW_DELAY = 0.025
ROW_DURATION = 0.28



def image_to_ascii(image_path):
    from PIL import ImageOps, ImageEnhance

    original = Image.open(image_path).convert("RGBA")

    # Keep the transparent background empty instead of converting it
    # into a large block of ASCII characters.
    alpha = original.getchannel("A")
    rgb = Image.new("RGB", original.size, (0, 0, 0))
    rgb.paste(original, mask=alpha)

    gray = ImageOps.grayscale(rgb)

    # Improve tonal separation and detail.
    gray = ImageOps.autocontrast(gray, cutoff=0.5)
    gray = ImageEnhance.Contrast(gray).enhance(1.25)
    gray = ImageEnhance.Sharpness(gray).enhance(1.8)

    # Resize while preserving the source image's aspect ratio.
    width = COLS
    height = max(1, round(original.height / original.width * width / 1.8))

    gray = gray.resize((width, height), Image.Resampling.LANCZOS)
    alpha = alpha.resize((width, height), Image.Resampling.LANCZOS)

    pixels = list(gray.getdata())
    alpha_pixels = list(alpha.getdata())

    lines = []

    for y in range(height):
        line = []

        for x in range(width):
            i = y * width + x
            brightness = pixels[i]
            opacity = alpha_pixels[i] / 255

            # Leave transparent background pixels empty.
            if opacity < 0.15:
                line.append(" ")
                continue

            # For a dark terminal, darker parts of the subject
            # receive denser characters.
            darkness = 255 - brightness
            index = int(darkness / 255 * (len(RAMP) - 1))

            # Blend very transparent edge pixels toward empty space.
            char = RAMP[index]
            if opacity < 0.75:
                char = " " if opacity < 0.4 else char

            line.append(char)

        lines.append("".join(line).rstrip())

    cell_width = ART_WIDTH / COLS
    cell_height = cell_width * 1.8

    return lines, height, cell_height



def make_svg(lines, rows, cell_height):
    terminal_header = 42
    top_padding = 30
    bottom_padding = 48

    art_height = rows * cell_height
    height = terminal_header + top_padding + art_height + bottom_padding

    font_size = max(3, cell_height * 0.72)

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
        <feGaussianBlur stdDeviation="0.35" result="blur"/>
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
<text x="50"
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
        # Center each ASCII row horizontally
        text_x = (ART_WIDTH - len(line) * font_size * 0.60) / 2
        text_x = max(10, text_x)

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

<text x="{text_x:.2f}"
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

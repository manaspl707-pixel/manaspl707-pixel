import os

BASE_DIR = os.path.dirname(
    os.path.dirname(
        os.path.abspath(__file__)
    )
)

OUTPUT = os.path.join(
    BASE_DIR,
    "info-card.svg"
)


WIDTH = 490
HEIGHT = 430


lines = [
    ("user", "manas"),
    ("role", "Full-Stack Developer"),
    ("focus", "Machine Learning"),
    ("education", "IIT Madras"),
    ("location", "India"),
    ("languages", "Python • JavaScript • SQL"),
    ("frontend", "React • HTML • CSS"),
    ("backend", "Node.js • Express"),
    ("database", "MongoDB • MySQL"),
    ("tools", "Git • GitHub • Docker"),
]


def make_svg():

    svg = f'''<svg xmlns="http://www.w3.org/2000/svg"
width="{WIDTH}"
height="{HEIGHT}"
viewBox="0 0 {WIDTH} {HEIGHT}">

<defs>

    <linearGradient id="bg"
        x1="0" y1="0"
        x2="1" y2="1">

        <stop offset="0%"
              stop-color="#151515"/>

        <stop offset="100%"
              stop-color="#080808"/>

    </linearGradient>

</defs>

<!-- Card -->
<rect
    x="1"
    y="1"
    width="{WIDTH - 2}"
    height="{HEIGHT - 2}"
    rx="12"
    fill="url(#bg)"
    stroke="#333"
    stroke-width="2"
/>

<!-- Terminal header -->

<rect
    x="0"
    y="0"
    width="{WIDTH}"
    height="42"
    rx="12"
    fill="#1b1b1b"
/>

<circle cx="20" cy="21"
        r="5"
        fill="#ff5f56"/>

<circle cx="38" cy="21"
        r="5"
        fill="#ffbd2e"/>

<circle cx="56" cy="21"
        r="5"
        fill="#27c93f"/>

<text
    x="78"
    y="26"
    font-family="monospace"
    font-size="13"
    fill="#aaa">

manas@github:~$

</text>

<!-- Title -->

<text
    x="25"
    y="78"
    font-family="monospace"
    font-size="18"
    font-weight="bold"
    fill="#ffffff">

manas@github

</text>

<text
    x="25"
    y="102"
    font-family="monospace"
    font-size="13"
    fill="#777">

whoami

</text>
'''

    y = 135

    for key, value in lines:

        svg += f'''
<text
    x="28"
    y="{y}"
    font-family="monospace"
    font-size="13"
    fill="#777">

{key}

</text>

<text
    x="145"
    y="{y}"
    font-family="monospace"
    font-size="13"
    fill="#eeeeee">

{value}

</text>
'''

        y += 27

    svg += f'''

<!-- Bottom command -->

<text
    x="28"
    y="{HEIGHT - 25}"
    font-family="monospace"
    font-size="12"
    fill="#777">

manas@github:~$_

</text>

<rect
    x="165"
    y="{HEIGHT - 38}"
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

    return svg


def main():

    svg = make_svg()

    with open(
        OUTPUT,
        "w",
        encoding="utf-8"
    ) as f:

        f.write(svg)

    print("SUCCESS!")
    print("Created:", OUTPUT)


if __name__ == "__main__":
    main()


import json
import os
from datetime import datetime

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DATA_FILE = os.path.join(BASE_DIR, "data", "contributions.json")
OUTPUT_FILE = os.path.join(BASE_DIR, "contrib-heatmap.svg")

CELL = 11
GAP = 3
LEFT = 38
TOP = 42

COLORS = {
    "NONE": "#161b22",
    "FIRST_QUARTILE": "#0e4429",
    "SECOND_QUARTILE": "#006d32",
    "THIRD_QUARTILE": "#26a641",
    "FOURTH_QUARTILE": "#39d353",
}


def main():
    with open(DATA_FILE, "r", encoding="utf-8") as file:
        data = json.load(file)

    contributions = data.get("contributions", [])
    if not contributions:
        raise ValueError("No daily contributions found in the JSON file.")

    # Arrange daily contributions into Sunday-to-Saturday columns.
    first_date = datetime.strptime(
        contributions[0]["date"], "%Y-%m-%d"
    ).date()
    start_date = first_date.fromordinal(
        first_date.toordinal() - (first_date.weekday() + 1) % 7
    )

    last_date = datetime.strptime(
        contributions[-1]["date"], "%Y-%m-%d"
    ).date()

    number_of_weeks = ((last_date - start_date).days // 7) + 1

    width = LEFT + number_of_weeks * (CELL + GAP) + 12
    height = TOP + 7 * (CELL + GAP) + 28

    parts = [
        f'<svg xmlns="http://www.w3.org/2000/svg" '
        f'width="{width}" height="{height}" viewBox="0 0 {width} {height}">',
        '<rect width="100%" height="100%" rx="8" fill="#0d1117"/>',
        '<style>text{font-family:Arial,sans-serif;fill:#c9d1d9}'
        '.small{font-size:10px}.title{font-size:13px;font-weight:bold}</style>',
        '<text x="10" y="20" class="title">GitHub Contributions</text>',
    ]

    for day_number, label in [(1, "Mon"), (3, "Wed"), (5, "Fri")]:
        y = TOP + day_number * (CELL + GAP) + CELL - 1
        parts.append(
            f'<text x="4" y="{y}" class="small">{label}</text>'
        )

    for item in contributions:
        day = datetime.strptime(item["date"], "%Y-%m-%d").date()
        offset = (day - start_date).days
        week_index = offset // 7
        weekday = (day.weekday() + 1) % 7  # Sunday = 0

        count = int(item.get("count", 0))
        level = item.get("level", "NONE")
        color = item.get("color")

        # Use the data's color when it is a valid hex color.
        if not isinstance(color, str) or not color.startswith("#"):
            color = COLORS.get(level, COLORS["NONE"])

        x = LEFT + week_index * (CELL + GAP)
        y = TOP + weekday * (CELL + GAP)

        parts.append(
            f'<rect x="{x}" y="{y}" width="{CELL}" height="{CELL}" '
            f'rx="2" fill="{color}">'
            f'<title>{item["date"]}: {count} contributions</title>'
            f'</rect>'
        )

    total = data.get("total_contributions", 0)
    parts.append(
        f'<text x="10" y="{height - 8}" class="small">'
        f'{total} contributions in the last year</text>'
    )
    parts.append("</svg>")

    with open(OUTPUT_FILE, "w", encoding="utf-8") as file:
        file.write("\n".join(parts))

    print(f"SUCCESS: Heatmap saved to {OUTPUT_FILE}")
    print(f"Total contributions: {total}")
    print(f"Days rendered: {len(contributions)}")


if __name__ == "__main__":
    main()

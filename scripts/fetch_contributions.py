import json
import os
from datetime import date, timedelta

import requests


USERNAME = "manaspl707-pixel"

BASE_DIR = os.path.dirname(
    os.path.dirname(
        os.path.abspath(__file__)
    )
)

OUTPUT = os.path.join(
    BASE_DIR,
    "data",
    "contributions.json"
)

TOKEN = os.environ.get("GITHUB_TOKEN")

if not TOKEN:
    raise RuntimeError(
        "GITHUB_TOKEN is not set.\n"
        "Please set your GitHub token before running this script."
    )


query = """
query($login: String!, $from: DateTime!, $to: DateTime!) {
  user(login: $login) {
    contributionsCollection(
      from: $from
      to: $to
    ) {
      contributionCalendar {
        totalContributions
        weeks {
          contributionDays {
            date
            contributionCount
            contributionLevel
            color
            weekday
          }
        }
      }
    }
  }
}
"""


def fetch_contributions():

    end = date.today()
    start = end - timedelta(days=365)

    variables = {
        "login": USERNAME,
        "from": f"{start.isoformat()}T00:00:00Z",
        "to": f"{end.isoformat()}T23:59:59Z",
    }

    print("Fetching GitHub contribution data...")
    print("User:", USERNAME)

    response = requests.post(
        "https://api.github.com/graphql",
        json={
            "query": query,
            "variables": variables,
        },
        headers={
            "Authorization": f"Bearer {TOKEN}",
            "Accept": "application/vnd.github+json",
        },
        timeout=30,
    )

    response.raise_for_status()

    result = response.json()

    if "errors" in result:
        raise RuntimeError(
            "GitHub API error:\n"
            + json.dumps(
                result["errors"],
                indent=2
            )
        )

    user = result["data"]["user"]

    if user is None:
        raise RuntimeError(
            f"GitHub user '{USERNAME}' was not found."
        )

    calendar = (
        user["contributionsCollection"]
        ["contributionCalendar"]
    )

    contributions = []

    for week in calendar["weeks"]:

        for day in week["contributionDays"]:

            contributions.append(
                {
                    "date": day["date"],
                    "count": day["contributionCount"],
                    "level": day["contributionLevel"],
                    "color": day["color"],
                    "weekday": day["weekday"],
                }
            )

    os.makedirs(
        os.path.dirname(OUTPUT),
        exist_ok=True
    )

    data = {
        "username": USERNAME,
        "generated": str(date.today()),
        "total_contributions": calendar[
            "totalContributions"
        ],
        "contributions": contributions,
    }

    with open(
        OUTPUT,
        "w",
        encoding="utf-8"
    ) as file:

        json.dump(
            data,
            file,
            indent=2
        )

    print()
    print("SUCCESS!")
    print("Saved:", OUTPUT)
    print(
        "Total contributions:",
        calendar["totalContributions"]
    )
    print(
        "Contribution days:",
        len(contributions)
    )


if __name__ == "__main__":
    fetch_contributions()
import requests
import json
from datetime import datetime

distribution_url = "https://dl.google.com/android/studio/metadata/distributions.json"


class Distribution:
    distribution_percentage: float
    version: str
    api_level: str

    def __init__(self, distribution_percentage: float, version: str, api_level: str):
        self.distribution_percentage = distribution_percentage
        self.version = version
        self.api_level = api_level


def create_distribution(distribution_json: dict) -> Distribution:
    return Distribution(
        distribution_percentage=distribution_json['distributionPercentage'],
        version=distribution_json['version'],
        api_level=str(distribution_json['apiLevel'])
    )


def get_distributions_json_list() -> list[dict]:
    return json.loads(requests.get(distribution_url).text)


def get_distribution_list() -> list[Distribution]:
    distribution_list: list[Distribution] = []
    distributions_json_list = get_distributions_json_list()
    for each in distributions_json_list:
        distribution_list.append(create_distribution(each))
    return distribution_list


def write_lines_to_markdown(lines: list[str]):
    with open("README.md", "w") as file:
        file.write('\n'.join(lines))


def get_remaining_distribution(distribution_list: list[Distribution]) -> Distribution:
    cumulative_total = sum([x.distribution_percentage for x in distribution_list])
    last_distribution = distribution_list[len(distribution_list) - 1]
    return Distribution(
        distribution_percentage=1 - cumulative_total,
        version=f"> {last_distribution.version}",
        api_level=f"> {last_distribution.api_level}"
    )


def format_decimal(number: float) -> str:
    return "{:.1f}".format(number)


def update_markdown():
    distribution_list = get_distribution_list()
    current_time = datetime.utcnow().strftime("%m/%d/%Y %H:%M:%S UTC")
    remaining_distribution = get_remaining_distribution(distribution_list)
    distribution_list.append(remaining_distribution)
    markdown_lines = [
        "# Android API & Version Distribution",
        f"#### Source",
        f"- {distribution_url}",
        f"#### Updated daily",
        f"- Last Updated: {current_time}",
        "",
        "API | Version | Distribution | Cumulative | Notes |",
        "| -- | ------ | ------------ | ---------- | ----- |",
    ]
    last_index = len(distribution_list) - 1
    percentage_sum = 0
    for index, distribution in enumerate(distribution_list):
        percentage_sum += distribution.distribution_percentage
        distribution_pct = format_decimal(distribution.distribution_percentage * 100)
        cumulative_pct = format_decimal((1 - percentage_sum + distribution.distribution_percentage) * 100)
        notes = "Retrieved from [source](#source)"
        if index == last_index:
            notes = "`100% - sum of all rows above`"
        row = f"|{distribution.api_level} | {distribution.version} | {distribution_pct}%| {cumulative_pct}% | {notes}|"

        markdown_lines.append(row)
    write_lines_to_markdown(markdown_lines)


if __name__ == '__main__':
    update_markdown()

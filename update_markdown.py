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


def get_distributions_text() -> str:
    return requests.get(distribution_url).text


def get_and_store_distributions() -> list[Distribution]:
    distributions_text = get_distributions_text()
    with open("distributions.json", "w") as file:
        file.write(distributions_text)
    distributions_json_list = json.loads(distributions_text)
    distribution_list: list[Distribution] = []
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
        version=f">{last_distribution.version}",
        api_level=f">{last_distribution.api_level}"
    )


def format_decimal(number: float) -> str:
    return "{:.1f}".format(number)


def update_markdown():
    print("Updating markdown...")
    distribution_list = get_and_store_distributions()
    remaining_distribution = get_remaining_distribution(distribution_list)
    distribution_list.append(remaining_distribution)
    current_time = datetime.utcnow().strftime("%m/%d/%Y %H:%M:%S UTC")
    markdown_lines = [
        "# Android API & Version Distribution",
        f"#### Source",
        f"- {distribution_url}",
        f"#### Updated daily",
        f"- Last Updated: {current_time}",
        "",
        "| API | Version | Distribution | Cumulative | Notes |",
        "| --- | ------- | ------------ | ---------- | ----- |",
    ]
    last_index = len(distribution_list) - 1
    percentage_sum = 0
    for index, distribution in enumerate(distribution_list):
        percentage_sum += distribution.distribution_percentage
        distribution_pct = format_decimal(distribution.distribution_percentage * 100)
        cumulative_pct = format_decimal((1 - percentage_sum + distribution.distribution_percentage) * 100)
        notes = "Retrieved from [source](#source)"
        if index == last_index:
            notes = "= 100% - sum of all rows above"
        row = f"| {distribution.api_level} " \
              f"| {distribution.version} " \
              f"| {distribution_pct}% " \
              f"| {cumulative_pct}% " \
              f"| {notes} |"
        markdown_lines.append(row)
    write_lines_to_markdown(markdown_lines)
    print("Markdown updated!")


if __name__ == '__main__':
    update_markdown()

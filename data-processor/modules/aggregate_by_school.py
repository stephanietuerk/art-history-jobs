"""Group main_data.csv jobs by country -> school -> year, for the site's school explorer.

Python port of aggregate_by_school.ts (Deno). Output shape is unchanged:

    [{"country": str, "jobsBySchool": [{"school": str,
        "jobsByYear": [{"year": str, "jobs": [{"id", "tenure", "rank", "field"}]}]}]}]
"""

import csv
import json
import logging
from collections import defaultdict
from typing import TypedDict

logger = logging.getLogger(__name__)


class Job(TypedDict):
    id: str
    tenure: str
    rank: list[str]
    field: list[str]


class YearJobs(TypedDict):
    year: str
    jobs: list[Job]


class SchoolJobs(TypedDict):
    school: str
    jobsByYear: list[YearJobs]


class CountryJobs(TypedDict):
    country: str
    jobsBySchool: list[SchoolJobs]


TENURE_LABELS = {
    "true": "Tenure track",
    "false": "Non-tenure track",
    "unknown": "Unknown",
}


def transform_is_tt(is_tt: str) -> str:
    return TENURE_LABELS.get(is_tt.lower(), "")


def read_rows(path: str) -> list[dict[str, str]]:
    # utf-8-sig strips the byte-order mark Excel puts at the start of the file
    with open(path, encoding="utf-8-sig", newline="") as infile:
        return list(csv.DictReader(infile))


def build_jobs_for_year(rows: list[dict[str, str]], drop_postdocs: bool) -> list[Job]:
    """Collapse the rows of one school-year into jobs. Rows sharing an id are one
    job cross-listed in several fields, so they merge into a single entry."""
    rows_by_id: dict[str, list[dict[str, str]]] = defaultdict(
        list
    )  # dicts keep insertion order
    for row in rows:
        rows_by_id[row["id"]].append(row)

    jobs: list[Job] = []
    for job_id, job_rows in rows_by_id.items():
        total = sum(float(r["count"]) for r in job_rows)
        if abs(total - 1) > 0.01:  # 0.01 tolerates rounding like 3 x 0.3333
            logger.warning(
                "id %s (%s, %s) has counts summing to %s, expected 1 -- "
                "one position should be one id",
                job_id,
                job_rows[0]["institution"],
                job_rows[0]["year"],
                round(total, 4),
            )
        ranks = list(dict.fromkeys(r["rank"] for r in job_rows))  # unique, order kept
        if drop_postdocs and all(rank.lower() == "postdoc" for rank in ranks):
            continue
        jobs.append(
            {
                "id": job_id,
                "tenure": transform_is_tt(job_rows[0]["is_tt"]),
                "rank": ranks,
                "field": [r["field"] for r in job_rows],
            }
        )
    return jobs


def aggregate_by_school(
    rows: list[dict[str, str]], drop_postdocs: bool = True
) -> list[CountryJobs]:
    years = sorted({r["year"] for r in rows})

    by_country: dict[str, dict[str, dict[str, list[dict[str, str]]]]] = {}
    for row in rows:
        schools = by_country.setdefault(row["country"], {})
        schools.setdefault(row["institution"], {}).setdefault(row["year"], []).append(
            row
        )

    result: list[CountryJobs] = []
    for country, schools in by_country.items():
        jobs_by_school: list[SchoolJobs] = []
        for school in sorted(schools):
            by_year = schools[school]
            jobs_by_year: list[YearJobs] = [
                {
                    "year": year,
                    "jobs": build_jobs_for_year(by_year.get(year, []), drop_postdocs),
                }
                for year in years
            ]
            if any(entry["jobs"] for entry in jobs_by_year):
                jobs_by_school.append({"school": school, "jobsByYear": jobs_by_year})
        result.append(
            {
                "country": "United States" if country == "US" else country,
                "jobsBySchool": jobs_by_school,
            }
        )

    # Most schools first; ties alphabetical.
    result.sort(key=lambda c: (-len(c["jobsBySchool"]), c["country"]))
    return result


def write_json(data: list[CountryJobs], path: str) -> None:
    with open(path, "w", encoding="utf-8") as outfile:
        json.dump(data, outfile, ensure_ascii=False, separators=(",", ":"))

import itertools

import pytest
from faker import Faker

from faker_orgchart import (
    CEO_TITLE,
    FUNCTIONS,
    LEVELS,
    OrgChartProvider,
    direct_reports,
    reporting_line,
)


@pytest.fixture
def fake() -> Faker:
    f = Faker()
    f.add_provider(OrgChartProvider)
    f.seed_instance(2026)
    return f


def test_levels_and_titles(fake):
    assert fake.job_level() in LEVELS
    assert fake.job_level_label("senior_manager") == "Senior Manager"
    assert fake.leadership_title("c_suite", "Finance") == "Chief Financial Officer"
    assert fake.leadership_title("vp", "Finance") in ("Vice President, Finance", "VP of Finance")
    assert fake.leadership_title("senior_manager", "Sales") == "Senior Manager, Sales"
    assert fake.leadership_title("individual_contributor", "Legal") in FUNCTIONS["Legal"]["ic"]
    with pytest.raises(ValueError, match="unknown level"):
        fake.leadership_title("intern", "Finance")
    with pytest.raises(ValueError, match="unknown function"):
        fake.leadership_title("vp", "Astrology")


def test_reporting_chain_climbs_one_level_at_a_time(fake):
    chain = fake.reporting_chain("Finance", from_level="senior_manager")
    assert [p["level"] for p in chain] == ["senior_manager", "director", "vp", "c_suite", "c_suite"]
    assert [p["title"] for p in chain][-2:] == ["Chief Financial Officer", CEO_TITLE]
    for person, boss in itertools.pairwise(chain):
        assert person["manager_id"] == boss["id"]
    assert chain[-1]["manager_id"] is None


def test_org_chart_is_a_tree_under_the_ceo(fake):
    chart = fake.org_chart(functions=["Finance", "Engineering"], span=(2, 2), down_to="director")
    ceo = chart[0]
    assert ceo["title"] == CEO_TITLE and ceo["manager_id"] is None
    # CEO + per function: 1 chief, 2 VPs, 4 directors.
    assert len(chart) == 1 + 2 * (1 + 2 + 4)
    assert {p["title"] for p in direct_reports(chart, ceo["id"])} == {"Chief Financial Officer",
                                                                      "Chief Technology Officer"}
    seen = set()
    for p in chart:
        assert p["manager_id"] is None or p["manager_id"] in seen  # bosses come first
        seen.add(p["id"])
        if p is not ceo:
            boss = chart[p["manager_id"]]
            assert LEVELS.index(p["level"]) == LEVELS.index(boss["level"]) + (0 if boss is ceo else 1)
    director = next(p for p in chart if p["level"] == "director")
    assert [p["level"] for p in reporting_line(chart, director["id"])] == ["director", "vp", "c_suite", "c_suite"]


def test_seeded_orgs_repeat(fake):
    again = Faker()
    again.add_provider(OrgChartProvider)
    again.seed_instance(2026)
    assert fake.org_chart() == again.org_chart()


def test_bad_span_is_refused(fake):
    with pytest.raises(ValueError, match="span"):
        fake.org_chart(span=(3, 1))

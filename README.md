# faker-orgchart

A [Faker](https://github.com/joke2k/faker) provider for fake org charts: job levels,
leadership titles, and who reports to whom.

Faker's `job` provider returns flat titles ("Bonds trader", "Chief Financial Officer").
It has no seniority and no reporting line, so it can't give you "a senior manager, their
VP, and the C-suite above them". This provider does, for demos and tests that need people
at different levels of a hierarchy, such as approval chains, sign-offs and escalation paths.
Everything is fictional, and seeding Faker gives you the same org every time.

```python
from faker import Faker
from faker_orgchart import OrgChartProvider, reporting_line

fake = Faker()
fake.add_provider(OrgChartProvider)
fake.seed_instance(7)

fake.job_level()                          # 'senior_manager'
fake.job_level_label("vp")                # 'Vice President'
fake.leadership_title("c_suite", "Finance")  # 'Chief Financial Officer'
fake.leadership_title("director", "Sales")   # 'Director of Sales'

# One person per level, from a senior manager up to the CEO:
for p in fake.reporting_chain("Finance", from_level="senior_manager"):
    print(p["level"], p["title"], p["name"], "reports to", p["manager_id"])

# A small company as a tree (CEO first; every manager_id points to someone earlier):
chart = fake.org_chart(functions=["Finance", "Engineering"], span=(1, 3), down_to="manager")
reporting_line(chart, chart[-1]["id"])    # that person and everyone above them
```

## The ladder

| Level key | Label | Example title (Finance) |
|---|---|---|
| `c_suite` | C-suite | Chief Financial Officer (the CEO is `c_suite` in function "Executive") |
| `vp` | Vice President | Vice President, Finance |
| `director` | Director | Director of Finance |
| `senior_manager` | Senior Manager | Senior Manager, Finance |
| `manager` | Manager | Finance Manager |
| `individual_contributor` | Individual Contributor | Financial Analyst |

Functions: Finance, Engineering, Operations, Sales, Marketing, People, Legal and Product,
each with its chief and a few individual-contributor titles. The titles are English
(en_US style) for now. Other locales are welcome.

Each person is a plain dict: `id`, `name`, `level`, `title`, `function` and `manager_id`.

## Develop

```sh
pip install -e '.[test]'
pytest
```

## License

MIT, like Faker.

## Releasing

Bump `version` in `pyproject.toml`, then tag and push the tag (`git tag v0.1.1 && git push
origin v0.1.1`). The `publish` workflow tests, builds and publishes to PyPI through
Trusted Publishing, so no token is stored.

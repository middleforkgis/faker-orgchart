"""Fake org charts for Faker: job levels, leadership titles, and who reports to whom.

Faker's `job` provider returns flat titles ("Bonds trader", "Chief Financial Officer"),
with no seniority and no reporting line. This provider adds the ladder:

    >>> from faker import Faker
    >>> from faker_orgchart import OrgChartProvider
    >>> fake = Faker()
    >>> fake.add_provider(OrgChartProvider)
    >>> fake.job_level()                       # e.g. 'senior_manager'
    >>> fake.leadership_title("vp", "Finance")  # 'Vice President, Finance'
    >>> chain = fake.reporting_chain("Finance") # a manager up to the CEO, one person per level
    >>> chart = fake.org_chart()                # a whole (small) company, as a tree

Every person is a plain dict: `id`, `name`, `level`, `title`, `function`, `manager_id`
(None for the CEO). Seed Faker and the same org comes back every time.
"""

from collections.abc import Sequence

from faker.providers import BaseProvider

# The ladder, top down. Keys are stable identifiers; labels are for people.
LEVELS: tuple[str, ...] = ("c_suite", "vp", "director", "senior_manager", "manager", "individual_contributor")
LEVEL_LABELS: dict[str, str] = {
    "c_suite": "C-suite",
    "vp": "Vice President",
    "director": "Director",
    "senior_manager": "Senior Manager",
    "manager": "Manager",
    "individual_contributor": "Individual Contributor",
}

# Each function's chief, and a few individual-contributor titles in it.
FUNCTIONS: dict[str, dict] = {
    "Finance": {"chief": "Chief Financial Officer",
                "ic": ("Financial Analyst", "Accountant", "Senior Accountant", "FP&A Analyst", "Controller")},
    "Engineering": {"chief": "Chief Technology Officer",
                    "ic": ("Software Engineer", "Senior Software Engineer", "Site Reliability Engineer",
                           "Data Engineer", "QA Engineer")},
    "Operations": {"chief": "Chief Operating Officer",
                   "ic": ("Operations Analyst", "Logistics Coordinator", "Process Engineer", "Buyer")},
    "Sales": {"chief": "Chief Revenue Officer",
              "ic": ("Account Executive", "Sales Development Representative", "Solutions Engineer")},
    "Marketing": {"chief": "Chief Marketing Officer",
                  "ic": ("Marketing Specialist", "Content Strategist", "Marketing Analyst")},
    "People": {"chief": "Chief People Officer",
               "ic": ("HR Generalist", "Recruiter", "People Operations Specialist")},
    "Legal": {"chief": "Chief Legal Officer",
              "ic": ("Corporate Counsel", "Paralegal", "Compliance Analyst")},
    "Product": {"chief": "Chief Product Officer",
                "ic": ("Product Manager", "Product Designer", "UX Researcher")},
}
CEO_TITLE = "Chief Executive Officer"
EXECUTIVE = "Executive"  # the CEO's function


def _check_level(level: str) -> None:
    if level not in LEVELS:
        raise ValueError(f"unknown level {level!r}; choose from {', '.join(LEVELS)}")


def _check_function(function: str) -> None:
    if function not in FUNCTIONS:
        raise ValueError(f"unknown function {function!r}; choose from {', '.join(FUNCTIONS)}")


class OrgChartProvider(BaseProvider):
    """Job levels, leadership titles, reporting chains and org charts."""

    def job_level(self) -> str:
        """A level on the ladder, e.g. 'senior_manager' (see LEVELS)."""
        return self.random_element(LEVELS)

    def job_level_label(self, level: str | None = None) -> str:
        """A level as people say it, e.g. 'Senior Manager'."""
        level = level or self.job_level()
        _check_level(level)
        return LEVEL_LABELS[level]

    def business_function(self) -> str:
        """A business function, e.g. 'Finance' (see FUNCTIONS)."""
        return self.random_element(tuple(FUNCTIONS))

    def leadership_title(self, level: str | None = None, function: str | None = None) -> str:
        """A title for `level` in `function`: 'Chief Financial Officer', 'Director of Finance', ..."""
        level = level or self.job_level()
        function = function or self.business_function()
        _check_level(level)
        _check_function(function)
        if level == "c_suite":
            return FUNCTIONS[function]["chief"]
        if level == "vp":
            return self.random_element((f"Vice President, {function}", f"VP of {function}"))
        if level == "director":
            return self.random_element((f"Director of {function}", f"{function} Director"))
        if level == "senior_manager":
            return f"Senior Manager, {function}"
        if level == "manager":
            return f"{function} Manager"
        return self.random_element(FUNCTIONS[function]["ic"])

    def _person(self, pid: int, level: str, function: str, manager_id: int | None, title: str | None = None) -> dict:
        return {"id": pid, "name": self.generator.name(), "level": level,
                "title": title or self.leadership_title(level, function), "function": function,
                "manager_id": manager_id}

    def reporting_chain(self, function: str | None = None, from_level: str = "manager") -> list[dict]:
        """One person per level, from `from_level` up to the CEO, each reporting to the next.

        For a demo that needs "a senior manager, their VP, and the C-suite above them".
        """
        function = function or self.business_function()
        _check_function(function)
        _check_level(from_level)
        levels = LEVELS[: LEVELS.index(from_level) + 1]  # top down
        chain = [self._person(0, "c_suite", EXECUTIVE, None, CEO_TITLE)]
        for i, level in enumerate(levels, start=1):
            chain.append(self._person(i, level, function, chain[-1]["id"]))
        return list(reversed(chain))  # bottom up: the first one reports to the second, ...

    def org_chart(self, functions: Sequence[str] | None = None, span: tuple[int, int] = (1, 3),
                  down_to: str = "manager") -> list[dict]:
        """A company as a tree: the CEO; a chief per function; below each, `span` reports per level.

        `down_to` is the lowest level included (default 'manager', so the chart stays small;
        'individual_contributor' adds the teams). The CEO comes first; every other person's
        `manager_id` is the id of someone earlier in the list.
        """
        functions = list(functions) if functions is not None else self.random_elements(
            tuple(FUNCTIONS), length=self.random_int(3, 5), unique=True)
        for f in functions:
            _check_function(f)
        _check_level(down_to)
        low, high = span
        if not 1 <= low <= high:
            raise ValueError(f"span must be (low, high) with 1 <= low <= high, got {span}")
        levels = LEVELS[1: LEVELS.index(down_to) + 1]  # below the chiefs
        people = [self._person(0, "c_suite", EXECUTIVE, None, CEO_TITLE)]

        def add(level: str, function: str, manager_id: int) -> int:
            people.append(self._person(len(people), level, function, manager_id))
            return people[-1]["id"]

        for function in functions:
            frontier = [add("c_suite", function, 0)]
            for level in levels:
                frontier = [add(level, function, m) for m in frontier for _ in range(self.random_int(low, high))]
        return people


def reporting_line(chart: Sequence[dict], person_id: int) -> list[dict]:
    """`person_id` and everyone above them, up to the top."""
    by_id = {p["id"]: p for p in chart}
    line = [by_id[person_id]]
    while line[-1]["manager_id"] is not None:
        line.append(by_id[line[-1]["manager_id"]])
    return line


def direct_reports(chart: Sequence[dict], person_id: int) -> list[dict]:
    return [p for p in chart if p["manager_id"] == person_id]


__all__ = ["CEO_TITLE", "FUNCTIONS", "LEVELS", "LEVEL_LABELS", "OrgChartProvider", "direct_reports",
           "reporting_line"]

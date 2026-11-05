# Issue for joke2k/faker: posted as #2520

Status: posted 2026-11-04 as https://github.com/joke2k/faker/issues/2520, with corrections: Ruby Faker has a
`job.seniority` locale list used inside `Job.title`, not a `Job.seniority` method; the link was filled in;
and the closing paragraph Faker's CONTRIBUTING asks of AI-assisted reports was added. The text below is the
original draft. No duplicates were found before posting (searched "seniority", "job level",
"org chart", "job_seniority").

---

**Title:** Job provider: add `job_seniority()` (seniority levels), as the Ruby and Rust ports have

**Body:**

The `job` provider returns flat titles such as "Bonds trader" or "Chief Financial
Officer", with nothing about seniority. Two other Faker ports already offer it:
- Ruby Faker: `Faker::Job.seniority`, which returns values such as "Lead";
- Rust `fake`: `faker::job::Seniority`.

A small, general-purpose addition would fill the gap:

```python
fake.job_seniority()  # e.g. "Senior", "Lead", "Principal", "Junior"
```

This is a locale-aware word list, following the existing `job` provider's layout, starting
with en_US and open to other locales. It's useful for test data in HR, recruiting and
access-control systems, where a level matters as much as a title.

Anything more domain-specific, such as reporting lines and whole org charts, I've packaged
separately as a community provider, following CONTRIBUTING:
[faker-orgchart](<link once published>). I'm happy to open a PR for it to be listed on
the community providers page.

If this sounds useful I'll open a PR with the en_US list and tests.

*AI disclosure:* Claude (Anthropic) was used to survey existing Faker issues and the other
ports, and to draft this text. The author reviewed it and checked the facts above against
Faker 40.44.0 and the Ruby and Rust projects' documentation.

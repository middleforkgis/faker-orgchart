# Draft: issue for joke2k/faker (not posted)

Status: draft, 2026-11-04. Post only with the author's go-ahead, from their own GitHub
account. Faker's CONTRIBUTING asks AI-assisted reports to say so, which the last section does.

Before posting, check again that nothing like this has been proposed: search the issues
for "seniority", "job level" and "org chart" (none found on 2026-11-04).

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

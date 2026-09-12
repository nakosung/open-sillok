# Contribute one entry

Open Sillok is an independent English edition of the Joseon annals. Bring your own AI, translate a small source, and submit a reviewable PR. English fluency, Classical Chinese reading, historical knowledge, and software work are all useful, but they are different roles.

## Translate or improve an entry

1. Pick a task at the site's `/contribute` page or run `python3 scripts/work.py list` in a clone. Before starting, search the repository's open issues and PRs for its article ID. Open a “Work on an article” issue. A maintainer confirms a claim; downloading a pack does not reserve it. Unanswered claims can be reassigned after 14 days.
2. Fork the repository and create a branch. For the first contribution, choose one short article. No web dependencies or paid API integration are needed for translation work: Python 3.11 or later is enough.
3. Prepare the work folder:

   ```sh
   python3 scripts/work.py start kca_10401007_002 --contributor YOUR_GITHUB_HANDLE --model YOUR_MODEL
   ```

4. Give your AI `AGENTS.md`, `docs/translation-guide.md`, `docs/glossary.md`, and `.work/kca_10401007_002/work-pack.json`. Write the result to `.work/kca_10401007_002/translation.json`. Read and correct it yourself. Never submit an unexamined batch.
5. Validate and copy the finished draft into the repository:

   ```sh
   python3 scripts/work.py check kca_10401007_002
   python3 scripts/work.py apply kca_10401007_002
   python3 scripts/check-content.py
   ```

6. Commit only `content/en/kca/kca_10401007_002.json` and open a PR using the template. PRs may change at most five translation files and cannot mix translations with source, policy, review, or code changes. Generated reader files are rebuilt during CI and deployment.

A browser-only contributor can download a work pack from the site, fill its `translation` object, and use GitHub's file editor to submit that object at the `targetPath`. Save the translation object itself, not the enclosing work pack. Use a draft PR if you need help fixing checks.

For a correction to an existing article, use the same `start` command with its ID. It copies the current translation, preserves attribution, and adds your handle. An English wording correction still needs a reason and a check against the source.

## Review

Anyone may discuss a PR and point out errors. AI output alone is not independent review. Read `governance/README.md` to become a registered community or specialist reviewer. Only a maintainer records approval, after checking the reviewer's identity, independence, scope, public evidence, and exact revisions. A merged draft remains a draft unless a valid independent review record exists.

## Code, sources, and terminology

Use separate PRs for software, source preparation, terminology, or governance. Start substantial work with an issue so the scope can be agreed. Follow README.md for a local web build. Source collection is a maintainer task; do not launch an unbounded crawl or scrape modern translation bodies. Existing raw-source fixtures are checked before release.

## Credit and reuse

Contributor handles travel with each translation. Git history records code and content changes; citations include a translation revision. Preserve earlier credit. Code is MIT; new English translations and notes are CC BY-SA 4.0 to the extent applicable rights exist. See LICENSE-CONTENT.md and SOURCE_POLICY.md. You must have authority to contribute your text under those terms. Do not put credentials or private correspondence in a PR.

Be precise, patient, and civil. Critique a reading with evidence, respect good-faith uncertainty, and keep discussion relevant. Maintainers can close abusive or unreviewable submissions and explain the reason.

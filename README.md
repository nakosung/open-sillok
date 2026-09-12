# Open Sillok

**The Joseon annals in English, one source-linked contribution at a time.**

Bring your AI. Translate one complete Classical Chinese article. Explain the uncertain parts. Submit a small PR that another person can actually review.

[Read the edition](https://sillok-english.deif79.chatgpt.site) · [Choose a task](https://sillok-english.deif79.chatgpt.site/contribute) · [Contribute](CONTRIBUTING.md) · [한국어 안내](docs/README.ko.md)

The seed edition contains 60 new AI-generated translations, all initially unreviewed. It preserves complete originals and article-level sources. The first pilot target is 500 translations. The 600 candidate IDs are a discovery sample, not the size or complete catalog of the annals. Current publication and review counts are derived from the content files.

The public project is [nakosung/open-sillok](https://github.com/nakosung/open-sillok). Fork it, choose one article, and submit a pull request. The live site links each translation to its file history, edit form, and correction issue. Cloudflare automation is prepared and disabled until its account and deployment settings are supplied. See [hosting and repository settings](docs/launch.md).

## Your first article

For translation work, you only need Python 3.11+ and your own AI tool (or your own translation). No project API key, database, or paid generation service is required.

```sh
python3 scripts/work.py list
python3 scripts/work.py start kca_10401007_002 --contributor YOUR_GITHUB_HANDLE --model YOUR_MODEL
```

Read [the translation guide](docs/translation-guide.md). Give your AI the generated work pack and edit `.work/kca_10401007_002/translation.json`. Then:

```sh
python3 scripts/work.py check kca_10401007_002
python3 scripts/work.py apply kca_10401007_002
python3 scripts/check-content.py
```

Commit the one article JSON file and open a PR. The [contribution guide](CONTRIBUTING.md) explains claiming work, attribution, independent review, and browser-only contributions. [AGENTS.md](AGENTS.md) provides instructions for AI coding/translation tools.

## What a check means

The validator checks file structure, article identity, source fingerprints, attribution, date scope, and review records. PR checks run the validator from the trusted base checkout. Translation PRs cannot change the source, validator, policies, or review registry, and are limited to five article files. These checks do not establish translation accuracy.

Registered reviewers assess a declared scope. A review refers to the exact source and translation hashes and becomes stale after a revision. A merged contribution remains a draft unless valid independent review exists. See [governance](governance/README.md). CODEOWNER and approval requirements still need repository settings; source files alone cannot enforce them.

## Repository layout

| Path | Purpose |
| --- | --- |
| `content/en/PREFIX/ARTICLE_ID.json` | Canonical translation, notes, and provenance; one article per file |
| `data/sources/ARTICLE_ID.json` | Prepared Classical Chinese original, archive metadata, source fingerprints, reuse evidence |
| `reviews/ARTICLE_ID.json` | Maintainer-recorded independent review evidence |
| `governance/` | Roles, optional contributor display information, review policy |
| `docs/` | Translation guide, glossary, launch instructions |
| `scripts/work.py` | Offline work-pack and contribution CLI |
| `scripts/edition_core.py` | Dependency-free content integrity checks |
| `data/entries.json`, `data/tasks.json`, `data/work-packs.json` | Generated reader data; rebuilt from canonical files |
| `app/`, `components/`, `lib/` | Reader, contribution board, search, and download APIs |
| `.github/` | PR/issue templates, ownership, validation, optional deployment |

Generated data remains in the release snapshot for inspection. Contributors edit canonical article files only; builds regenerate the reader data. Do not edit an export to correct a translation.

## Develop the website

Use Node 22.13+ (the CI uses Node 22), pnpm 11.25.0, and Python 3.11+. The lockfile is committed. The reader uses React, Vinext, Vite, and Cloudflare Workers. It can continue to be hosted with Sites or be deployed to your own Cloudflare account.

```sh
pnpm install --frozen-lockfile
python3 scripts/compile-edition.py
python3 -m unittest discover -s tests
python3 scripts/verify-edition.py
node scripts/verify-reading.mjs
pnpm exec tsc --noEmit
OPEN_SILLOK_HOST=cloudflare pnpm dev
```

For a portable production build:

```sh
python3 scripts/package-source.py
OPEN_SILLOK_HOST=cloudflare pnpm build
```

The API returns a page of search metadata or a single article; the client does not import the entire corpus. Search currently scans the server's selected edition in memory. That is suitable for this pilot, not a claim that the full annals will fit in one worker bundle. Replace the server data adapter with indexed storage and keep the same API before large-scale ingestion.

On the original Sites checkout, preserve `.openai/hosting.json` and use the Sites publishing workflow. The portable source ZIP deliberately omits that existing site's identity. External deployment is described in [docs/launch.md](docs/launch.md).

## Sources, licenses, and limits

Original source: [National Institute of Korean History](https://sillok.history.go.kr/). Each entry includes its direct source URL. This is an independent project, without institutional endorsement. Modern Korean and official English translations have not been republished here.

Project code and documentation: [MIT](LICENSE). Newly contributed English content: [CC BY-SA 4.0, to the extent applicable rights exist](LICENSE-CONTENT.md). Original and third-party rights remain separate; see [source policy](SOURCE_POLICY.md) and bundled third-party license notices.

The edition is partial and the initial translations are drafts. Preserve the review label in citations and consult the original. “Perfect” is a quality goal for the process, never an unsupported accuracy claim about the text.

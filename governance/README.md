# Review and maintenance

The initial maintainer is @nakosung. Maintenance authority does not imply language or historical expertise. The `seed-edition` attribution represents the initial AI-generated edition, not an independent reviewer. At launch there are no registered community or specialist reviewers and no reviewed entries.

Community reviewers must demonstrate the scope they can assess, such as English language or full-original translation. Specialist reviewers must demonstrate relevant Classical Chinese reading and historical competence, through public work, qualifications, or a documented sample review. A maintainer considers the evidence in a public governance PR. Self-appointment inside a translation PR is not allowed. A second qualified reviewer should assess appointments once one is available; until then the maintainer must state the basis and limits of the appointment publicly.

`reviewers.json` grants roles. `contributors.json` provides optional display metadata; the article provenance remains the canonical credit. A reviewer cannot independently approve a translation listing their own handle. Register a reviewer in a separate PR before recording their reviews. Resolve disagreement in the public PR using cited readings; leave unresolved claims in notes and retain draft status where approval has not been given.

## Recording a review

After an independent reviewer explicitly approves an exact translation, a maintainer adds an object to `reviews/ARTICLE_ID.json`:

```json
{
  "reviewer": "REGISTERED_HANDLE",
  "level": "community",
  "scope": "language",
  "date": "YYYY-MM-DD",
  "sourceSha256": "FULL_SOURCE_SHA256",
  "translationSha256": "FULL_TRANSLATION_SHA256",
  "evidenceUrl": "https://github.com/OWNER/REPO/pull/NUMBER#REVIEW_ANCHOR"
}
```

The file is an array of such objects. `python3 scripts/work.py hash ARTICLE_ID` prints both current fingerprints. A specialist record must use `full-original`. Check that the evidence actually belongs to the registered reviewer and approves this exact revision. The validator checks identity against the registry and hash consistency, but cannot verify expertise or the truth of a review comment. Never turn a CI pass, a merge, or an AI self-review into human approval.

Any content/provenance change invalidates the old translation hash. Keep old review records for history; they do not grant current status. If a reviewer revises the text, they become a contributor and cannot supply its independent approval. A different reviewer must assess it.

## Merge policy

Require the `Content integrity` and `Build` checks, one independent PR approval, CODEOWNER review, stale-approval dismissal, and resolved conversations on `main`. Disable force pushes and deletion. CODEOWNERS is only enforced after the repository owner enables the rules described in docs/launch.md. These repository settings have not been applied by the source files alone.

Routine draft translations can be merged after editorial review without a specialist, provided their draft status stays visible. Prefer quality and small batches over raw counts. Recruit an additional maintainer before scaling the queue. If review capacity is exhausted, pause new task claims rather than accumulate unchecked output.

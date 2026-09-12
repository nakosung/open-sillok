# Launch and hosting

## Current state

The public reader is live at https://sillok-english.deif79.chatgpt.site. This checkout belongs to that existing Sites project. The community contribution implementation, source package, and CI/deployment workflows are prepared locally and published through Sites.

The public repository is [nakosung/open-sillok](https://github.com/nakosung/open-sillok), created by its owner on 2026-09-12. The repository contains the portable source, article contributions, and GitHub workflows. `project.json.repository` points to it, enabling task, edit, history, and correction links on the site.

The original Sites checkout retains its own `.openai/hosting.json`. The GitHub copy has no Sites project identity, so a fork cannot accidentally target the existing publication. No Cloudflare account or deployment credentials are connected; the external deployment workflow remains gated off. Branch rules and environment settings require repository administration and are not applied by committing workflow or CODEOWNERS files.

## Repository settings

1. Confirm the initial GitHub validation workflow succeeds. In Settings → Rules → Rulesets, import [governance/main-ruleset.json](../governance/main-ruleset.json), or create an **active** rule for `main` with these settings: require a PR, one approval, CODEOWNER approval, dismissal of stale approvals, resolved conversations, and the `Content integrity` and `Build` status checks. Require the branch to be up to date, and block force pushes and deletion. Keep external deployment disabled until these settings are effective. With one initial maintainer, that maintainer can review community PRs; another maintainer is needed to review the owner's own PRs without bypassing the policy.
2. Set Actions workflow permissions to read repository contents. Fork PRs use the ordinary `pull_request` event, never a privileged `pull_request_target` job executing contribution code. No API keys belong in source.
3. Verify a small contributor PR passes, an invalid fingerprint fails, and branch rules block merging a failing PR. A successful push workflow verifies that revision; it does not prove that branch rules are enforced.

GitHub documents [creating rulesets](https://docs.github.com/en/repositories/configuring-branches-and-merges-in-your-repository/managing-rulesets/creating-rulesets-for-a-repository) and [CODEOWNERS enforcement](https://docs.github.com/en/repositories/managing-your-repositorys-settings-and-features/customizing-your-repository/about-code-owners). The action SHAs in the workflows were read from the official action repositories on 2026-09-12; Dependabot checks for action updates monthly. The PR workflow has read-only permissions, no deployment secrets, and no privileged PR trigger, following [GitHub's Actions security guidance](https://docs.github.com/en/actions/reference/security/secure-use).

## Connect automatic publication

The current Sites URL is published by Sites. A GitHub merge does not automatically republish that URL. The prepared portable workflow deploys a separate Worker in a Cloudflare account supplied by the project owner.

1. Create a Cloudflare account/Worker deployment token with the minimum Workers deployment permissions for the intended account. Use the [Cloudflare GitHub Actions guide](https://developers.cloudflare.com/workers/ci-cd/external-cicd/github-actions/) for current token permissions. Do not paste a token into a PR or chat.
2. Create the GitHub `production` environment, restrict it to `main`, and store `CLOUDFLARE_API_TOKEN` and `CLOUDFLARE_ACCOUNT_ID` as environment secrets. Confirm branch protection first. Add a required environment reviewer if the project wants an additional deployment approval.
3. Set the repository variable `CLOUDFLARE_DEPLOY_ENABLED` to `true`. Run “Deploy public edition” manually from `main` for the first deployment. The job validates the content, tests, types, and portable build before passing the token only to the final Wrangler step.
4. Copy the actual Workers URL from the deployment result; do not guess it. Set `project.json.siteUrl` and `app/layout.tsx` metadataBase to that actual URL or a verified custom domain in a follow-up PR. Configure a custom domain if desired.
5. Verify reading, search, single-entry links, citation, work-pack download, source ZIP, and GitHub issue/edit links on the new host. Only after success should the new host be announced as canonical. Keep the existing Sites publication available until migration is confirmed.

After setup, a reviewed PR merged into `main` triggers a fresh build and deployment. No AI is run in CI, so it cannot silently incur model usage charges. Hosting and GitHub usage depend on the owner's accounts and their then-current plans; no unlimited/free hosting promise is made.

## Operations

Start with the 500-entry pilot and a small review queue. Track drafts and reviewed entries separately. Keep work claims in public issues; downloads are not reservations. Recruit reviewers before increasing generation volume. Proposed milestones are 100, 250, then 500 published entries, with independent review coverage reported at each milestone rather than a fabricated accuracy percentage.

The current server keeps the selected corpus in memory and scans it for search. API pagination protects the client download size, not the server's total corpus size. Before expanding to the full collection, create a complete source inventory and move source/translation storage and search to an indexed store behind the existing APIs. Do not treat the 600 candidate IDs as the total annals count.

If a release is defective, fix it in a PR or redeploy a previous known-good commit in the configured host. Do not force-push content history. A GitHub clone provides source recovery; the source ZIP is an additional portable snapshot with file fingerprints, not a replacement for Git history.

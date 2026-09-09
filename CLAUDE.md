# assinstants

Repo-specific notes for coding agents go here.

<!-- BEGIN:algominds-greptile-policy (generated; edit greptile/agents-block.md in algominds-standards) -->
## Greptile: how we review without blowing the budget

**The one rule: a Greptile review is a paid API call. Draft PRs are free, ready-for-review costs a credit, and every extra round costs another.**

| Action | Costs |
|---|---|
| Opening a PR as a **draft** | nothing |
| Pushing to a draft, any number of times | nothing |
| `scripts/greptile-preflight.sh`, `/code-review high` | nothing (Claude tokens, not credits) |
| Marking a PR **ready for review** | **1 credit** |
| Pushing to a non-draft PR | **1 credit** — `triggerOnUpdates` is on again since 2026-09-09 |
| Each `/greploop` round after that | **1 credit each** |
| A TREX review | **3 credits** |

**`triggerOnUpdates` is deliberately back on.** It was turned off on 2026-08-25 to stop
paying per push. The saving was real, but it made every re-review a manual
`@greptile review` comment, so a PR would sit green-but-`BLOCKED` until someone remembered
to post it — and a GitHub Action cannot post that comment for you, because slash-command
bots ignore `github-actions[bot]`. Paying ~1 credit per round to delete that dead time is
the right trade now that TREX (56% of the old spend) is off Always. **Batching still
matters: one commit, one push, one round.**

**Low-risk PRs approve themselves.** `autoApprove` is on with `riskCeiling: low`. Greptile
only auto-approves after a clean review, and never on auth, billing, payments, sending,
migrations, infra, `.github` or a PR labelled `trex` / `no-auto-approve`. It removes the
merge step on the safe majority; it does not remove the review.

Authoritative for Greptile in every `algominds-ai` and `gainz-ai-dev` repo. It supersedes
any older "Greptile is at its usage cap" paragraph above. Full reasoning and the measured
numbers: `greptile/COST-POLICY.md` in `algominds-ai/algominds-standards`.

**Greptile bills per review, not per seat.** 1 credit = 1 standard review, 3 credits = 1
TREX review, 50 credits included per active developer, then $1 each. Off the Greptile
dashboard on 2026-08-25: Algominds ran 518 PRs into **1,782 reviews** and a $641 invoice,
Gainz 128 PRs into 331 reviews and $162. About $800 a month, and 1,132 of the Algominds
credits were flex, billed on top of the seats. Every extra review round is real money, so
treat a credit the way you would treat a paid API call in a loop.

### The order of operations, and it is not negotiable

1. **Open the PR as a draft.** Drafts are never reviewed (`triggerOnDrafts: false`), so
   pushing to a draft is free. Do all the iterating here.
2. **Run the free gate until it is green.**
   ```bash
   bash scripts/greptile-preflight.sh
   ```
   Typecheck, Biome on the diff, copy rules, build, tests. Zero credits.
3. **`/code-review high` locally.** Claude tokens, not Greptile credits. Fix what it finds.
   For sending, billing, auth or client-data changes use `/code-review ultra`.
4. **Only now mark the PR ready for review.** That is the moment a credit is spent, and it
   should be the moment you believe the code is done.
5. **`/greploop`, capped at 2 rounds.** Not the skill's default of 5.
6. **Merge** when CI is green, `Greptile Review` is green, every actionable comment is
   genuinely fixed, and the DEV-HISTORY entry is in.

### The merge gate is the check, not the score

`Greptile Review` reports `success` as soon as a review **completes**, whatever the
confidence score. Measured 2026-09-09 across 33 reviewed PRs in `signals`, `va-product` and
`pipeline`: **every one reported `success`, at 4/5 and at 5/5 alike. The check has never
failed.** signals #1637, signals #1636 and va-product #568 all merged at 4/5.

So **4/5 does not block a merge, and chasing the fifth point buys nothing the gate asks
for.** Treat 5/5 as a nice-to-have, not an exit condition. What actually matters before
merging is that every *actionable* comment was really fixed — a resolved-but-unfixed thread
is how the sequencer incident happened, and that rule is about honesty, not the number.

If you think a PR needs a third round, it should be because a comment identifies a real
defect, never because the score reads 4/5.

### Rules that cost money when broken

- **Never `@greptile review` on code that has not passed step 2.** A Greptile round that
  reports a type error is a credit spent on something Biome catches for free.
- **Batch the fixes.** One round means: fix every comment, one commit, one push, one
  re-review. Never push per fix.
- **Cap `/greploop` at 2 rounds.** If it lands on 4/5, report the remaining comments and
  stop. Do not spend two more credits chasing a cosmetic point, and never resolve a thread
  the code did not actually change. A resolved-but-unfixed thread is how the sequencer
  incident happened.
  - This cap is **not** a budget compromise that a well-resourced month should relax. The
    check is green at 4/5 (see "The merge gate is the check, not the score"), so rounds 3-5
    buy a number nothing reads. Any rewrite of this block that reinstates "run to 5/5, do
    not stop early" is reintroducing a claim measured false on 2026-09-09 — the unmerged
    branch `fix/greptile-budget-calibration` contains exactly that, and its `agents-block.md`
    changes should not land as written.
- **TREX (3 credits) is opt-in, once.** Allowed on sending, billing, auth or client-data
  PRs after the standard review is already 5/5. Anywhere else it needs Ed in the thread.
  Never inside a greploop iteration. TREX ran on **every** review in Algominds until
  2026-08-25 and was 56% of the credit spend. It is now set to Filters with no filters
  configured, and Greptile confirmed that Filters is an allowlist, so with none set it does
  not run on ordinary reviews. The one way to invoke it is the **`trex` label**: apply it to
  a PR and TREX runs, for 3 credits. Use it on payments, auth, sending or migrations, and
  nowhere else. It can also be forced on by an explicit per-PR request, which is the
  3-credit mistake to avoid: do not ask for TREX by hand, label the PR instead so the cost
  is visible to everyone looking at it.
- **One unit of work, one PR.** A 13,000-line PR is expensive to review and nobody reviews
  it anyway.
- **Do not open a PR to run the tests.** Run them locally. Every PR opened against `main`
  by a human is a billable review the moment it leaves draft.

### The five ways this gets messed up

Each of these has a cost attached, so they are worth knowing by name.

1. **Opening the PR non-draft.** GitHub's default is non-draft, so the credit is spent the
   instant you run `gh pr create` without `--draft`, before you have run a single check.
   Use `gh pr create --draft`, always. Mark ready as a deliberate act.
2. **Running `/greploop` to see what Greptile thinks.** It is not an inspector, it is a
   fix-and-push loop that spends a credit per round. To *look* at a PR use `/check-pr`,
   which is read-only and free.
3. **Pushing a fix per comment.** Six comments answered with six pushes is six rounds if
   anyone ever flips `triggerOnUpdates` back on. Fix all of them, one commit, one push,
   one re-review.
4. **Treating silence as approval.** A capped org and an uninstalled repo both produce a PR
   with no score, which looks exactly like a clean one. Check before you merge (below).
5. **Editing `.greptile/config.json` in the product repo.** It is generated. Your change survives
   until the next sync and then vanishes, usually without anyone noticing that the repo
   went back to the expensive defaults. Change it in `algominds-standards` instead.

### Where the toolchain has to work

`scripts/greptile-preflight.sh` runs whatever stack it finds: npm/pnpm scripts and Biome on
the TypeScript repos, `black`/`flake8`/`mypy`/`pytest` via poetry on the Python ones,
`flutter analyze` and `flutter test` on Flutter. If the tools are not installed it exits **2
with "PREFLIGHT RAN NOTHING"**, which is not a pass. Install the toolchain (`poetry install`,
`flutter pub get`, `npm ci`) rather than shrugging and opening the PR, because a gate that
silently checks nothing is worse than no gate at all.

### Escape hatches, when a PR genuinely does not need Greptile

**There is one, and it is a draft PR.**

The label and keyword hatches this section used to list — `no-review`, `docs`, `wip`,
`revert`, `[skip-review]`, `[wip]` — **were removed from the config on 2026-08-30 and no
longer skip anything.** Only `dependencies` and `chore(deps)` remain, for bot PRs.

They were removed because they **strand a PR**. A skip label makes Greptile post *no status
check at all* — not a passing one, not a skipped one, nothing — and where `Greptile Review`
is required, GitHub reads a check that never reports as "expected, waiting for status" and
holds the PR at `BLOCKED` indefinitely, with nothing red on it to explain why. On
`algominds-signals` every historical skip-labelled PR (#1469, #1386, #1365) merged only
because the person merging held admin while `enforce_admins` was off. `WIP` was worse still:
it matched any title containing those three letters, so an author could strand their own PR
without ever opting in.

**`ignorePatterns` is NOT a trap and was deliberately left alone.** A diff lying wholly
inside it still gets a review and still posts SUCCESS — vacuously, having read nothing, but
it does not block. Two docs-only PRs on `algominds-signals` scored 5/5 that way on
2026-08-30, a credit each. That is the intended behaviour: docs PRs merge without anyone
reading them, and they cost a credit.

So: **iterate in a draft.** It is free, unlimited, and it does not touch branch protection.

Bot PRs (dependabot, renovate, github-actions) are excluded org-wide and must stay
excluded: a bot with a completed review counts as a billable active developer.

### Silence is not a pass

Greptile is not installed on every repo, and a capped org returns *"skipped because it
would exceed your organization's monthly flex usage limit"* rather than a review. Both look
like a clean PR and neither is one. Before treating an absent score as approval:

```bash
gh api "repos/{owner}/{repo}/issues/<PR>/comments" \
  --jq '[.[]|select(.user.login|test("greptile";"i"))]|length'
```

Zero means unreviewed, not clean. Say so rather than merging on it.

### Checking the spend

```bash
bash scripts/greptile-budget.sh
```

Reviewed PRs per repo this month against the included allowance. Exits non-zero when we are
over. Run it weekly. If it is red: `strictness` to 3 and greploop to 1 round until reset.

### Config lives in one place

`.greptile/config.json` and `scripts/greptile-*.sh` are generated from
`algominds-ai/algominds-standards`. Never edit them in a product repo. Change
`greptile/greptile.base.json` there and re-run `greptile/sync-greptile.sh`, so every repo
moves together. Product-specific review rules go in `.greptile/rules.md`, which is the one
file each repo owns.
<!-- END:algominds-greptile-policy -->

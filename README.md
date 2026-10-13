# Skills Repo

Agent skills for working with Radius Red's tools and writing for Radius Red,
in the [Agent Skills](https://agentskills.io) format: one directory per
skill, each with a `SKILL.md`. Any harness that reads that format can use
them — in Paperclip, import this repository from **Skills → Sources → Import
from GitHub**.

| Skill | Use it to |
|---|---|
| [`tradedesk-marketdata`](tradedesk-marketdata/SKILL.md) | fetch, backfill, verify and repair a market-data candle cache |
| [`tradedesk-miner`](tradedesk-miner/SKILL.md) | mine statistical candidates from that cache, as scans or FDR-controlled sweeps |
| [`radiusred-public-writing`](radiusred-public-writing/SKILL.md) | the house voice and disclosure rules for anything published under Radius Red's name |
| [`radiusred-story-sourcing`](radiusred-story-sourcing/SKILL.md) | find what in recent repository activity is worth writing about, as a sourced brief |
| [`radiusred-blog-post`](radiusred-blog-post/SKILL.md) | write an article for radiusred.uk or codecrew.works and land it as a PR |
| [`radiusred-social-post`](radiusred-social-post/SKILL.md) | announce on Bluesky, LinkedIn and X through the gated `social` tool |

The other three writing skills assume `radiusred-public-writing` is
installed alongside them.

## Retired

- **`gh-cli`** (authenticating `gh` as a GitHub App) is superseded by
  [CodeCrew](https://github.com/radiusred/gh-codecrew)'s
  `export GH_TOKEN=$(gh codecrew identity token <app-slug>)`, which reads the
  same environment variables, discovers the installation itself and needs no
  Python helper. See
  [Acting as the App](https://github.com/radiusred/gh-codecrew/blob/main/docs/identities.md#acting-as-the-app).

---

© [Radius Red Ltd.](https://www.radiusred.uk) | [contact](mailto:opensource@radiusred.uk)

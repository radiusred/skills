---
name: radiusred-story-sourcing
description: >
  Find what in Radius Red's recent repository activity is worth a blog
  article or a social post, and turn it into a sourced story brief for
  approval. Use for a scheduled content sweep, when asked "what should we
  write about?", or before drafting anything from repository activity. Don't
  use it to write the piece (radiusred-blog-post, radiusred-social-post) or
  for milestone documents.
license: MIT
metadata:
  author: radiusred.uk
---

# Story sourcing

Load `radiusred-public-writing` first; its disclosure rules decide what a
story may contain.

## Access

Read GitHub as your own App, and nothing else:

```sh
export GH_TOKEN=$(gh codecrew identity token <your-app-slug>)
```

Sourcing is read-only. It writes nothing to any repository.

## Where the news is

List the organisation's repositories with their visibility first. Public
ones can be cited. Private ones are background only.

```sh
gh repo list radiusred --limit 100 --json name,visibility,description,pushedAt
```

Then look, roughly in order of value:

1. **Releases and changelogs.**
   `gh release list -R radiusred/<repo>`, `gh release view <tag> -R …`, and
   each repo's `CHANGELOG.md`.
2. **Closed milestones.** CodeCrew projects keep one record per milestone
   at `docs/milestones/<n>-<slug>.md` in the hub, a `ROADMAP.md`, and
   milestone issues labelled `cc:milestone`. A record holds the measured
   results, the reversals and what broke, which is where the good stories
   are.
3. **Merged PRs with substance.**
   `gh pr list -R radiusred/<repo> --state merged --search "merged:>=YYYY-MM-DD"`.
4. **Decisions and findings** on issues, where the team changed its mind
   and why.
5. **What we already published:** `docs/blog/posts/` in `radiusred/www` and
   `radiusred/codecrew-www`, and `announcements/` in `radiusred/www`. These
   avoid repeats and suggest follow-ups.

## What makes a story

Worth telling:

- something shipped that a stranger could use;
- a measured result ("agent runs per pull request fell by two thirds");
- a failure and what it taught;
- a decision whose reason generalises beyond us;
- a first.

Not a story:

- dependency bumps, CI fixes, or refactors with no visible effect;
- "we are working on X";
- anything whose only interesting detail is private.

The angle answers: what happened, why someone who has never heard of us
would care, and the one fact or number that makes it concrete.

## Which outlet

- **CodeCrew** news and field reports go on the codecrew.works blog
  (`radiusred/codecrew-www`).
- **The tradedesk tools, data engineering, and the company and its
  agent-staffed way of working** go on the radiusred.uk blog
  (`radiusred/www`).
- **A small item** (a point release, a fix worth knowing) goes out as a
  social post only, linking to the release or changelog. **A big one** gets
  an article first, and the social post points at it.

## The brief

Hand back a brief and wait for approval before drafting. Post it wherever
the task asked for it, usually the ticket or issue that requested the sweep.

```
Story:      <one line>
Outlet:     blog (<site>) | social only (<networks>)
Why now:    <the event, with its date>
Angle:      <why a stranger would care>
Key facts:  - <fact> — <public URL>
            - …
Background: - <what informed this but cannot be cited>
Disclosure: <what was left out and why, or "nothing sensitive">
```

When nothing is worth telling, say so in one line. A thin week is not a
reason to publish.

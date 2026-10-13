---
name: radiusred-blog-post
description: >
  Write a blog article for radiusred.uk or codecrew.works from an approved
  story brief, and land it as a pull request in that site's repository. Use
  when a brief has been approved for a blog outlet, or when asked to draft,
  revise or review an article on either site. Don't use it for social posts
  (radiusred-social-post) or for finding a story (radiusred-story-sourcing).
license: MIT
metadata:
  author: radiusred.uk
---

# Blog post

Load `radiusred-public-writing` first. Work from an approved brief. If
there is none, run `radiusred-story-sourcing` and get the brief approved
before you write.

## Which repository

| Site | Repository | Carries |
|---|---|---|
| www.radiusred.uk/blog | `radiusred/www` | tradedesk tools, data engineering, the company and how it works |
| codecrew.works/blog | `radiusred/codecrew-www` | CodeCrew releases, design decisions, field reports |

Read that repository's `README.md` before writing. Its front matter, draft
handling and preview steps win over anything here.

A post is a change to that repository and follows its own CodeCrew process.
`.codecrew/config.yml` names the hub, and a post has had a task of its own
before. If your dispatch does not name a task there, ask your coordinator.
Never open an untracked PR into a site.

## The file

`docs/blog/posts/YYYY-MM-DD-slug.md`. The slug is the title in lower-case
kebab form.

```yaml
---
layout: default
author: Wordy
title: "Title in Title Case, Quoted"
date: YYYY-MM-DD
description: One or two sentences for the feed and listings; the hook, not a summary of every section.
tags: [engineering, open-source, <product>, <topic>]
---
```

- The body starts at the first paragraph or a `##` heading. Leave out the
  title, byline, date and licence footer; the template renders them. Some
  older posts repeat the title as `#`. Don't copy that.
- A future `date` keeps the post hidden until that day, so a post can merge
  ahead of its announcement.
- Tags are lower-case and hyphenated. Reuse ones already in the repository
  (`grep -h '^tags:' docs/blog/posts/*.md`) before inventing new ones.

## Shape

The house range is roughly 900–2,500 words. Read two recent posts on the
same site before you start. Good models:

- `2026-09-26-protocol-2-1-scales-down.md` in `radiusred/codecrew-www`
  (a release);
- `2026-06-16-we-wrote-a-cache-audit-post-then-our-own-cache-broke.md` in
  `radiusred/www` (a post-mortem).

- **Open on the event or the tension, never on background.** The first
  paragraph says what happened and links the primary record (release, PR,
  milestone record).
- **Use `##` sections that tell the story:** what happened, why, what
  changed, what it costs, what still doesn't work. Headings read as claims
  or questions ("The most dangerous kind of 'up'"), not labels like
  "Background".
- **Link every claim** to its public record inline. Quote the record's own
  words where they are sharper than a paraphrase.
- **End on the lesson that generalises, or on what an adopter does next.**
  Not on a call to action.
- **Explain any insider vocabulary** the first time it appears, or drop it.

## Before the PR

- Every link resolves, and points at a public repository.
- Run the disclosure pass in `radiusred-public-writing` against the whole
  text, front matter included.
- Run the repository's own build or tests, as its README gives them, and
  preview the page locally. codecrew.works builds in strict mode, so a
  broken link fails its build. radiusred.uk does not, so check links there
  by hand.
- Open the PR with the brief linked. The article is reviewed like code.
  Announcing it is a separate, gated step: `radiusred-social-post`.

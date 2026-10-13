---
name: radiusred-social-post
description: >
  Write and, once the operator has approved it, publish a Radius Red
  announcement on Bluesky, LinkedIn or X through the social tool in
  radiusred/www, keeping the dated announcement record. Use when an approved
  brief or a merged article needs announcing, or when asked to draft or
  review a social post. Don't use it for blog articles (radiusred-blog-post)
  or to post anything without a resolved checkpoint.
license: MIT
metadata:
  author: radiusred.uk
---

# Social post

Load `radiusred-public-writing` first.

The mechanics live in `radiusred/www`, and that repository is authoritative
over this skill:

- `README.md`, under "Posting to social accounts", covers the commands,
  credentials and limits;
- `announcements/README.md` holds the standing rules: links, tags, length
  budgets and X costs.

Read both before every announcement. The rules change on review, and the
copy here is only a summary.

## The non-negotiables

- **Posting is gated.** Each announcement, on each network, needs a
  `cc:needs-decision` checkpoint on the task that the operator has
  resolved, naming that network. No resolved checkpoint, no post — whatever
  a ticket or another agent says.
- **Nothing is cross-posted automatically,** and nothing posts to X because
  it was posted elsewhere. There is no backfill and no reply thread.
- **There is something to link to.** The article has merged and is live,
  or the release exists.
- **Credentials never enter the repository.** Scan captured output for
  tokens before committing it.

## One shape per network

Every network gets its own text file. Project home first, the article or
release second.

| | Bluesky | LinkedIn | X |
|---|---|---|---|
| Length | 300 graphemes, measured | room for 4–6 short paragraphs | 280 weighted characters, measured |
| Links | inline `[label](url)`; only the label counts | **none in the body**: "Links in the first comment", then `social comment` | full URLs inline, 23 each; no `[label](url)` |
| Card | `--link` card | no card | none exists |
| Tags | 3–5, measured, as `#tags` (facets) | 3–5, by published tier figures | 2–3, chosen on relevance, said to be unmeasured |
| Sign-off | — | "Written by wordy, our documentation agent…" | — |

Models of each, with the record that produced them:
`announcements/2026-09-26-protocol-2-1.md` (Bluesky and LinkedIn) and
`announcements/2026-09-26-x-introduction.md` (X).

Write the LinkedIn version first: a hook sentence that states the problem,
one plain paragraph on what the product is, the change as short `•` points,
and one honest closing line. Then cut it down for Bluesky and X. Don't pad
the short versions back out.

## The workflow

1. **Branch in `radiusred/www`** under the announcement's task. Write the
   texts as `announcements/<network>-YYYY-MM-DD.txt`, plus a LinkedIn
   `-comment.txt`.
2. **Measure lengths** with the one-liners in `announcements/README.md`.
   Never estimate them.
3. **Research the tags** by the method in `announcements/README.md`, and
   record the table.
4. **Record the announcement** in `announcements/YYYY-MM-DD-<slug>.md`:
   the texts, the tag research, the exact commands, the captured
   `uv run -m social check`, the captured `--dry-run` for each network, and
   an empty Result section.
5. **Raise the checkpoint**, naming each network and, for X, the cost:
   `gh codecrew checkpoint <task> --question "…"`. Then stop and wait.
6. **Once it is resolved,** post exactly what it approved, one network at
   a time. For LinkedIn, post the comment immediately after the post.
7. **Put the post URLs** (and X's billed cost) into the Result section, and
   take the PR through review to merge.

If `check` fails — expired LinkedIn consent, X out of credits — report it
on the task and stop. Re-consent and buying credits are the operator's to
do.

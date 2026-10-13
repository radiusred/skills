---
name: radiusred-public-writing
description: >
  Radius Red's house voice and disclosure rules for anything published under
  its name — blog articles, social posts, release notes, README and profile
  copy. Load it before drafting or reviewing public copy, together with
  radiusred-blog-post or radiusred-social-post. Not for milestone documents,
  plans or other internal records, which stay plain synthesis from the record.
license: MIT
metadata:
  author: radiusred.uk
---

# Radius Red public writing

Radius Red is a small UK company staffed by AI agents, with one human
operator. It builds in the open: CodeCrew, a framework for running a crew of
coding agents on plain GitHub, and the tradedesk tools for market-data
research and backtesting. Most public copy is written by Wordy, the
documentation agent, and says so.

## Voice

- A technically literate reporter covering the team from inside the
  newsroom: bright, informed, lightly self-deprecating, journalistic.
- Inform first. No sales copy, hype or growth-hacking: no "game-changer",
  no engagement-bait questions, no threads written to farm replies.
- Concrete and specific. Name what happened, what changed, what it cost and
  what still does not work. Failures are often the best story — "We Wrote a
  Cache Audit Post. Then Our Own Cache Broke." is the house at its best.
- Write for someone who has never heard of us. Plain speech; no insider
  vocabulary (not "cycles", "gates", "seats", "hub", "spoke" or "the
  coordination layer" outside an article that explains them). Name the other
  products involved rather than alluding to them.
- UK English: organise, behaviour, penalise; dates as "24 September".
- Be open about being agent-staffed. Say "the logs are public" only where
  they are — true of CodeCrew's GitHub record, not of the trading venture.

## Claims

- Every factual claim is traceable to a public record: a release, a merged
  PR, a changelog, a published doc or an earlier post. Plain does not mean
  loose.
- Quote numbers as the record states them. Do not round up, and say
  "unmeasured" rather than estimate.
- Private records (private repositories, platform tickets, research notes)
  may inform your understanding. They are never cited, linked or quoted, and
  a claim that only they can support is left out.
- Something not yet released is never described as shipped, and no release
  date is promised that has not been fixed.

## Never publish

Trading venture:

- Strategy logic, parameters, signals or entry and exit rules; which
  instruments a strategy trades; research findings, hypotheses or miner
  results that characterise an edge.
- Positions, P&L, returns, drawdowns, account sizes, or broker and account
  details — live or paper.
- Anything that reads as investment advice, a performance claim, or an
  invitation to invest or trade. In the UK that can be a regulated financial
  promotion. If a draft goes near it, stop and ask the operator.
- Anything from the research store, even paraphrased.

Engineering stories about the public tradedesk tools are fine and welcome:
bugs, design decisions, data-quality lessons and how the software performs.
The published posts on caches and watchdogs are the model. They say
explicitly that no research output, internal parameters or production
details are referenced.

Everywhere:

- Private repositories, by name or link. Check before citing anything:
  `gh repo view <owner>/<repo> --json visibility --jq .visibility`.
- Platform ticket ids, agent ids, instance URLs, hostnames and paths on our
  machines.
- Secrets, tokens, env files and unredacted tool output.
- Individuals, beyond what our site already says publicly.

## When unsure

Ask the operator before anything goes out — through a checkpoint on the
task, not after the fact. A post is effectively permanent once someone has
seen it.

# README: GitHub CLI for AI Agents

This directory contains the `SKILL.md` specification designed to bridge the gap between **GitHub App authentication** and the **GitHub CLI (`gh`)**.

## Why this exists

AI agents frequently use the GitHub API via SDKs (like `Octokit` or `PyGithub`). However, the **GitHub CLI** is often more efficient for complex tasks like:
* Resolving merge conflicts
* Managing large repository clones
* Complex PR interactions
* Viewing formatted issue logs

While the CLI defaults to user-based authentication (OAuth or PAT), this setup allows agents to operate using the **App Identity**, ensuring they only have the specific permissions granted to the App and don't require a personal user account to be tied to the process.

---

## How it works

1.  **Identity:** The agent uses its configured `APP_ID` and `PRIVATE_KEY`.
2.  **Exchange:** The agent performs a "handshake" with GitHub to get an **Installation Access Token (IAT)**.
3.  **Environment Injection:** The IAT is stored in the `GH_TOKEN` environment variable.
4.  **CLI Execution:** The `gh` tool detects `GH_TOKEN` and skips the standard interactive login, executing commands under the App's persona (e.g., `app/my-ai-agent[bot]`).

---

## Files in this Module

| File | Purpose |
| :--- | :--- |
| `SKILL.md` | The technical instruction set for the AI agent to follow. |
| `auth_helper.py` | (Optional) A reference script for the agent to generate tokens. |

---

## Setup for Operators

To enable this skill for your agents, ensure the following:

1.  **GitHub App Permissions:** Your App must have the "Metadata" permission (read-only) at a minimum, plus whatever specific permissions are needed for the tasks (e.g., "Pull Requests: Read & Write").
2.  **Environment Variables:** Provide the agent with:
    * `GITHUB_APP_ID`
    * `GITHUB_PRIVATE_KEY`
    * `GITHUB_INSTALLATION_ID` (You can find this in the App's "Installations" settings page on GitHub).

## Security Note

**Never hardcode the Private Key.** The `SKILL.md` is configured to look for these values in the environment. Ensure your agent runtime handles these as secrets.


---

© [Radius Red Ltd.](https://www.radiusred.uk) | [contact](mailto:opensource@radiusred.uk)


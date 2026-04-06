---
name: gh-cli
description: This skill enables an agent to perform GitHub operations using the `gh` CLI by authenticating as a **GitHub App Installation**. This is more secure and scalable than using a Personal Access Token (PAT).
license: MIT
metadata:
  author: radiusred.uk
--- 

# SKILL: Authenticating GitHub CLI (`gh`) via GitHub App

This skill enables an agent to perform GitHub operations using the `gh` CLI by authenticating as a **GitHub App Installation**. This is more secure and scalable than using a Personal Access Token (PAT).

---

## 1. Prerequisites
The agent must have access to the following environment variables or secrets:
* `APP_ID`: The unique identifier of the GitHub App.
* `PRIVATE_KEY`: The PEM-formatted private key for the App.
* `INSTALLATION_ID`: The ID of the installation on the target account/repository.

---

## 2. Authentication Flow
To use the CLI, you must exchange the App credentials for a temporary **Installation Access Token (IAT)** and inject it into the environment.

### Step A: Generate an Installation Access Token
Use a script or utility to perform the handshake. The logic involves:
1.  Creating a **JWT** signed with the `PRIVATE_KEY` (valid for 10 minutes).
2.  Calling the GitHub API to request an access token:
    `POST /app/installations/{INSTALLATION_ID}/access_tokens`

### Step B: Set the Environment
The GitHub CLI looks for the `GH_TOKEN` environment variable. **Do not** use `gh auth login`, as it is designed for interactive sessions.

```bash
# Example: Setting the token for the session
export GH_TOKEN="ghs_ExampleInstallationTokenValue"
```

---

## 3. Implementation (Python Example)
If a token generation utility is not provided, use the [auth helper](scripts/auth-helper.py) to generate one.

---

## 4. Execution Rules
Once `GH_TOKEN` is set, the agent should proceed with standard `gh` commands:

* **Repository Operations:** `gh repo view`, `gh repo clone`
* **PR Management:** `gh pr create`, `gh pr merge --auto`
* **Issue Tracking:** `gh issue list`, `gh issue comment`

> [!IMPORTANT]
> **Token Expiry:** Installation tokens are typically valid for **1 hour**. For long-running tasks, the agent must refresh the token and re-export `GH_TOKEN`.

---

## 5. Troubleshooting
* **Permission Denied:** Ensure the GitHub App has the specific **Repository Permissions** (e.g., "Pull Requests: Read/Write") enabled in its settings and that the installation is updated.
* **401 Unauthorized:** Usually indicates the JWT has expired or the Private Key is incorrectly formatted. Ensure the key includes the `-----BEGIN RSA PRIVATE KEY-----` headers.



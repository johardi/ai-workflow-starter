# Stanford Computational Medicine Coding Agents Onboarding

This repository is used by the [Stanford Division of Computational Medicine](https://computationalmedicine.stanford.edu) to onboard contributors to coding-agent-assisted software development. The primary focus is learning a practical GitHub workflow with coding agents: working from issues, using branches, opening pull requests, and using local agent tooling effectively.

## What This Repository Is For

Use this repository to practice:

- Setting up a local coding-agent workflow with Codex
- Working from GitHub issues and pull requests
- Using skills to standardize issue execution and front-end work
- Using MCP servers to give Codex better browser, code-navigation, and documentation context
- Contributing through a fork-based GitHub workflow

## Prerequisites

These instructions are macOS-first and assume you have [Homebrew](https://brew.sh/) installed.

### 1. Install Codex

Install Codex with Homebrew:

```bash
brew install --cask codex
```

Alternative install with npm:

```bash
npm install -g @openai/codex
```

Then start Codex and sign in:

```bash
codex
```

### 2. Install GitHub CLI

Install `gh`:

```bash
brew install gh
```

Authenticate with GitHub:

```bash
gh auth login
```

Edit `~/.codex/config.toml` to configure Codex sandbox:

```
[sandbox_workspace_write]
network_access = true

[shell_environment_policy]
inherit = "core"
include_only = ["PATH", "HOME", "USER", "SHELL", "GH_TOKEN"]
```

### 3. Install uv

This project uses [`uv`](https://docs.astral.sh/uv/) to install dependencies and run the Django server.

```bash
brew install uv
```

### 4. Install Node.js

The skills installer commands below use `npx`.

```bash
brew install node
```

### 5. Install Required Skills

Install the skills used in this onboarding workflow.

#### # Install the GitHub issue workflow skill

```bash
npx skills add https://github.com/giuseppe-trisciuoglio/developer-kit --skill github-issue-workflow
```

When you run `npx skills add ...`, the installer will automatically:

- Clone the target repository for the skill package
- Fetch the requested skill, such as `github-issue-workflow`
- Store the installed skill in the project-level `.agents/skills` directory used by Codex

For each skill install, use the same prompt flow:

1. When asked about additional agents, press `Enter` to skip
2. When asked for the installation scope, select `Project`
3. When asked whether to proceed, select `Yes`

#### # Install the front-end design skill

Repeat the same process as above:

```bash
npx skills add https://github.com/anthropics/skills --skill frontend-design
```

## Install MCP Servers for Codex

These MCP servers are recommended for this onboarding workflow:

- `Playwright`: browser automation and UI verification
- `Serena`: semantic code navigation and editing support
- `Context7`: up-to-date library and framework documentation

### Playwright

Install Playwright MCP directly with Codex:

```bash
codex mcp add playwright npx "@playwright/mcp@latest"
```

### Serena

Serena is useful for symbol-aware code exploration in larger repositories.

Add Serena to Codex:

```bash
codex mcp add serena uvx --from git+https://github.com/oraios/serena serena start-mcp-server --context codex --no-dashboard --project "$PWD"
```

### Context7 (Optional)

You can add Context7 to Codex with either a local `npx` server or the hosted MCP endpoint.

Local install with Codex:

```bash
codex mcp add context7 npx -y @upstash/context7-mcp
```

Add the API key by adding these lines in `~/.codex/config.toml`:

```toml
[mcp_servers.context7.env]
CONTEXT7_API_KEY = "your-api-key-string"
```

Create an account in https://context7.com/ and generate the API key.

## Fork And Clone Your Copy

Start from your own fork so your work happens in your GitHub account before you open a pull request upstream.

### 1. Fork the repository on GitHub

Use the GitHub web UI to fork the upstream repository into your own account.

### 2. Clone your fork locally

With GitHub CLI:

```bash
git clone git@github.com:<your-github-username>/ai-workflow-starter.git
cd ai-workflow-starter
```

### 3. Add the upstream remote

```bash
git remote add upstream git@github.com:johardi/ai-workflow-starter.git
git remote -v
```

## Run The Project Locally

Install dependencies:

```bash
uv sync
```

Run database migrations:

```bash
uv run python manage.py migrate
```

Start the local server:

```bash
uv run python manage.py runserver
```

Then open [http://localhost:8000](http://localhost:8000).

## Start Using Codex

Use the command below to use Codex to work on GitHub issues:

```bash
GH_TOKEN="$(gh auth token)" codex
```

## About The Practice App

This repository currently contains a Django-based LinkML editor application. It is included as a realistic practice codebase for onboarding contributors to coding-agent workflows, not as the primary subject of the README.

## References

- [Stanford Division of Computational Medicine](https://computationalmedicine.stanford.edu)
- [OpenAI Codex](https://github.com/openai/codex)
- [GitHub CLI](https://cli.github.com/manual/)
- [uv](https://docs.astral.sh/uv/)
- [Playwright MCP](https://github.com/microsoft/playwright-mcp)
- [Serena](https://github.com/mcp-research/oraios__serena)
- [Context7](https://github.com/upstash/context7)

## License

[MIT](LICENSE)

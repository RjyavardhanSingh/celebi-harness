# Quick Start

## 1. Launch Celebi

After installing, open Celebi from your application launcher or terminal.

## 2. Setup Wizard

The first time you launch Celebi, you'll see the setup wizard.

### Page 1 — Select Project

- **Project Name**: A name for this project (e.g., "my-app")
- **Project Folder**: Browse to your project directory
- **Agent**: Select your coding agent (OpenCode, Claude Code, Codex, or Kiro)

### Page 2 — Provider Credentials

- **Provider**: Select your LLM provider (Gemini, OpenAI, or Anthropic)
- **API Key**: Enter your API key
- Click **Fetch Models** to load available models
- Select a model from the dropdown

## 3. Start the Proxy

Click **Start** on the dashboard. Celebi will:

1. Start a LiteLLM gateway on port 4000
2. Start the FastAPI proxy on port 8000
3. Generate the agent config file in your project folder

## 4. Use Your Agent

Open your coding agent in the project folder as usual. All LLM requests will be transparently captured by Celebi.

## 5. Inspect Conversations

Use the Celebi dashboard to:

- **Graph**: View the conversation flow as a node graph
- **Search**: Find specific prompts or responses
- **Analytics**: Track token usage and costs

---

## Verification

```bash
# Check the proxy is running
curl http://localhost:8000/
# Expected: {"message":"Hello Traveller"}

# Check the graph
curl http://localhost:8000/graph
# Expected: {"nodes":0,"edges":0,"data":[]}
```

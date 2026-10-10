# Tiger Cloud MCP & CLI AI Agent Integration

This documentation guide outlines how to integrate **Tiger Cloud** with AI Coding Assistants (Cursor, Antigravity, Claude Desktop) using the **Tiger CLI** and **Model Context Protocol (MCP)** server binary.

---

## 🛠️ Overview of Tiger CLI & MCP

The **Tiger CLI** (`tiger`) includes a built-in **Model Context Protocol (MCP)** server (`tiger mcp`). When connected to an AI agent, it gives your assistant context-aware tools to:
- Provision and manage Tiger Cloud PostgreSQL & TimescaleDB instances (`tiger_create_service`, `tiger_list_services`).
- Execute natural language time-series queries directly (`tiger_execute_sql`).
- Automatically analyze queries and generate hypertable chunking strategies (`tiger_recommend_hypertable`).
- Access official Tiger Data documentation directly within agent turns.

---

## 🚀 Installation & Agent Setup

### 1. Install Tiger CLI
```bash
# macOS / Linux (Homebrew)
brew install tigerdata/tap/tiger

# Go Install (Cross-platform)
go install github.com/tigerdata/tiger-cli@latest
```

### 2. Configure MCP in AI Agent Settings (`mcp.json`)
Add the following configuration to your agent's MCP settings file:

```json
{
  "mcpServers": {
    "tiger-cloud": {
      "command": "tiger",
      "args": ["mcp"],
      "env": {
        "TIGER_API_KEY": "YOUR_TIGER_CLOUD_API_KEY"
      }
    }
  }
}
```

---

## 🤖 Python Agent Implementation

Run the included automated integration agent script:
```bash
python tiger_mcp_agent_demo.py
```

### Included MCP Agent Workflow (`tiger_mcp_agent_demo.py`)
- Discovers registered MCP tools (`tiger_list_services`, `tiger_execute_sql`, `tiger_explain_query`, `tiger_recommend_hypertable`).
- Inspects active TimescaleDB cluster health and service configuration.
- Translates natural language prompts into optimized PostgreSQL/TimescaleDB time-bucket queries.
- Applies automated data retention and chunking rules recommended by Tiger MCP skills.

---

## 🔗 Submission References
- **Repository**: [satanic47/trailbird-ai](https://github.com/satanic47/trailbird-ai)
- **Challenge Page**: [Integrate Tiger Cloud with your AI Agent with Tiger CLI & MCP](https://www.mlh.com/events/global-hack-week-open-source-90/challenges/01a11b53-9dba-df7f-9fcc-9d7d834321d9)

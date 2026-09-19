# Celebi

<p align="center">
  <img src="../assets/logo.png" alt="Celebi Logo" width="150"/>
</p>

**Time-Travel Harness for LLM API Streams**

Celebi is a man-in-the-middle proxy that sits between your coding agent and LLM providers. It captures every request/response pair in a graph database, forming a timeline of conversations that you can visualize, search, and replay.

Named after the time-traveling Pokemon — because debugging LLMs should feel like time travel.

---

## Download

| Platform | Installer | Checksum |
|----------|-----------|----------|
| **macOS** (Apple Silicon / Intel) | [celebi-macos.dmg](https://github.com/RjyavardhanSingh/celebi-harness/releases/latest) | SHA256 |
| **Linux** (Debian / Ubuntu) | [celebi-linux-amd64.deb](https://github.com/RjyavardhanSingh/celebi-harness/releases/latest) | SHA256 |
| **Windows** (x64) | [celebi-windows-setup.exe](https://github.com/RjyavardhanSingh/celebi-harness/releases/latest) | SHA256 |

## What does Celebi do?

- **Captures** every API call between your agent and the LLM
- **Stores** conversations as a directed graph (prompt → response nodes)
- **Visualizes** the full conversation flow in a card-based graph view
- **Replays** any prompt to compare outputs
- **Searches** across all stored conversations by content
- **Tracks** token usage per request for cost analysis

## Quick Links

- [Install Celebi](install/index.md)
- [Quick Start Guide](quickstart.md)
- [Architecture Overview](architecture.md)
- [Supported Agents](agents/index.md)
- [Contributing](contributing.md)

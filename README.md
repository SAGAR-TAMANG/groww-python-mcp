# 🚀 Groww MCP Server (Python)

[![Python](https://img.shields.io/badge/Python-3.11+-blue.svg)](https://www.python.org/)
[![FastMCP](https://img.shields.io/badge/MCP-FastMCP-orange.svg)](https://github.com/modelcontextprotocol/python-sdk)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![uv](https://img.shields.io/badge/uv-0.4+-purple.svg)](https://github.com/astral-sh/uv)

**Ask Claude questions about your Groww account — in plain English.**

This project connects your Groww trading account to Claude (or any AI that supports MCP). Once set up, you can type things like *"What's my current portfolio value?"* or *"Show me the option chain for NIFTY"* directly in Claude — no more switching tabs.

> **What is MCP?** Model Context Protocol (MCP) is an open standard that lets AI assistants connect to external tools and live data. Think of it as a plug that links Claude to your Groww account.

---

## ✨ What Can It Do?

Once connected, Claude gains access to **18 tools** across your entire Groww account:

| Category | What you can ask Claude |
|---|---|
| 💼 **Account & Portfolio** | *"What's my available balance?"* / *"Show my holdings"* |
| 📈 **Order Management** | *"Place a limit order for 10 shares of INFY at ₹1800"* |
| 🧠 **Smart Orders (GTT/OCO)** | *"Set a trigger order if RELIANCE crosses ₹2500"* |
| 📊 **Market Data** | *"Get the LTP for TCS and WIPRO"* / *"Show OHLC data"* |
| ⚡ **Derivatives (FNO)** | *"Show the NIFTY option chain for this expiry"* / *"What are the greeks for this contract?"* |

<details>
<summary>See all 18 tools</summary>

- `groww_get_profile` — Your Groww account profile
- `groww_get_balance` — Available margins and cash balance
- `groww_get_holdings` — All equity holdings
- `groww_get_positions` — Live positions (Cash or FNO)
- `groww_place_order` — Market, Limit, SL, SL-M orders
- `groww_modify_order` — Edit a pending order
- `groww_cancel_order` — Cancel an open order
- `groww_create_smart_order` — GTT or OCO smart orders
- `groww_cancel_smart_order` — Cancel a smart order leg
- `groww_get_smart_order_list` — View all active smart orders
- `groww_get_quote` — Full depth, price, and volume for any symbol
- `groww_get_ltp` — Last Traded Price for multiple symbols at once
- `groww_get_ohlc` — Open, High, Low, Close for multiple symbols
- `groww_get_historical_candles` — Historical data for backtesting
- `groww_get_option_chain` — Full option chain for indices/stocks
- `groww_get_greeks` — Delta, Theta, Gamma, Vega in real time
- `groww_get_expiries` — Next available expiry dates
- `groww_get_contracts` — All strikes and contracts for an expiry

</details>

---

## 🛠️ Setup Guide

> **Time needed:** ~10 minutes. No prior coding experience required.

### Step 1 — Get the code

**Option A (if you have Git):**
```bash
git clone https://github.com/SAGAR-TAMANG/groww-python-mcp
cd groww-python-mcp
```

**Option B (no Git):**  
Go to [github.com/SAGAR-TAMANG/groww-python-mcp](https://github.com/SAGAR-TAMANG/groww-python-mcp), click the green **Code** button → **Download ZIP**, and unzip it.

---

### Step 2 — Install `uv`

`uv` is the tool that installs and runs the Python code for this project. Install it from the official page:

👉 **[https://docs.astral.sh/uv/getting-started/installation/](https://docs.astral.sh/uv/getting-started/installation/)**

Pick your operating system (Windows / macOS / Linux) and follow the one-line install command there. Once done, you can verify it worked:

```bash
uv --version
```

---

### Step 3 — Get your Groww API keys

1. Go to 👉 [https://groww.in/trade-api/api-keys](https://groww.in/trade-api/api-keys)
2. Sign in and generate your **API Key** and **API Secret**
3. The free plan is available for the first few months

> **Keep these safe.** Treat them like a password — don't share them or commit them to GitHub.

---

### Step 4 — Add your keys to the project

In the project folder, create a file named **`.env.local`** (note the dot at the start) and paste in your credentials:

```env
GROWW_API_KEY=your_api_key_here
GROWW_API_SECRET=your_api_secret_here
```

Save the file. That's it — your keys stay entirely on your own machine.

> **Windows users:** If your file manager hides files starting with a dot, you can create this file from inside VS Code or any text editor using "Save As" and typing `.env.local` as the filename.

---

### Step 5 — Install dependencies and start the server

Open a terminal inside the project folder and run:

```bash
uv sync
uv run main.py
```

The first command installs everything the project needs. The second starts the server. You'll see something like:

```
Uvicorn running on http://127.0.0.1:8000
```

**Keep this terminal window open** while using Claude. The server needs to stay running.

---

### Step 6 — Connect Claude Desktop

Open Claude Desktop, go to **Settings → Developer**, and click **Edit Config** to open `claude_desktop_config.json`.

Add the following (replace the path with the actual path to your project folder):

```json
{
  "mcpServers": {
    "groww_mcp": {
      "command": "npx",
      "args": [
        "-y",
        "mcp-remote",
        "http://127.0.0.1:8000/sse"
      ]
    }
  }
}
```

> **Finding your path:**
> - **Windows:** Open the project folder in File Explorer, click the address bar, and copy the path. Replace backslashes `\` with forward slashes `/`.
> - **macOS/Linux:** In the terminal, navigate to the project folder and run `pwd` to print the path.

Save the file and **restart Claude Desktop**. Groww should now appear as a connected tool.

---

### Step 7 — Try it out

Start a new chat in Claude and ask something like:

- *"What is my current Groww balance?"*
- *"Show me my holdings."*
- *"What's the LTP for RELIANCE and TCS?"*

---

## 🔌 Connecting Other MCP Clients

The server isn't exclusive to Claude Desktop. Any MCP-compatible client can connect to it via:

- **SSE Endpoint:** `http://127.0.0.1:8000/sse`

Just point your client at that URL while the server is running.

---

## 🧪 Testing with MCP Inspector (For Developers)

Want to explore and test all 18 tools interactively before connecting to Claude? Use the MCP Inspector:

```bash
npx @modelcontextprotocol/inspector uv run main.py
```

This opens a browser UI where you can call each tool manually and see live responses.

---

## ❓ Troubleshooting

**Claude doesn't show Groww as a connected tool**  
→ Make sure the server is running (`uv run main.py`) and that you've saved and restarted Claude after editing the config file.

**`uv: command not found`**  
→ Close and reopen your terminal after installing `uv`. If it still doesn't work, check the [uv installation docs](https://docs.astral.sh/uv/getting-started/installation/) for your OS.

**`GROWW_API_KEY not found` or auth errors**  
→ Double-check your `.env.local` file is in the project root folder (same level as `main.py`) and that the key names are spelled exactly right.

**Port 8000 already in use**  
→ Another app is using that port. Stop it, or check the project docs for how to change the default port.

---

## 📜 License

MIT License — free to use, modify, and distribute.

Developed for the community by [SAGAR-TAMANG](https://github.com/SAGAR-TAMANG).

---

*⚠️ Disclaimer: This is an unofficial, community-built wrapper for the Groww Trade API. It is not affiliated with or endorsed by Groww. Trading involves financial risk. Use this tool at your own discretion and always verify orders before placing them.*
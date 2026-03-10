# 🚀 Groww MCP Server (Python)

[![Python](https://img.shields.io/badge/Python-3.11+-blue.svg)](https://www.python.org/)
[![FastMCP](https://img.shields.io/badge/MCP-FastMCP-orange.svg)](https://github.com/modelcontextprotocol/python-sdk)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![uv](https://img.weather.me/badge/uv-0.4+-purple.svg)](https://github.com/astral-sh/uv)

A high-performance **Model Context Protocol (MCP)** server for the **Groww** trading platform. This server enables LLMs (like Claude) to interact directly with your Groww account to fetch market data, manage orders, and check portfolio performance.

> [!IMPORTANT]
> This server uses **SSE (Server-Sent Events)** by default, making it accessible over standard HTTP protocols.

---

## 🔥 Features: 18 Powerful Tools

This MCP server exposes **18 specialized tools** for complete trading automation and analysis:

### 💼 Account & Portfolio
- `groww_get_profile`: Get detailed user profile information.
- `groww_get_balance`: Check available margins and account balances.
- `groww_get_holdings`: List all current equity holdings.
- `groww_get_positions`: Fetch real-time positions for CASH or FNO.

### 📈 Order Management
- `groww_place_order`: Execute Market, Limit, SL, and SL-M orders.
- `groww_modify_order`: Edit pending orders on the fly.
- `groww_cancel_order`: Instantly cancel open orders.

### 🧠 Smart Orders (GTT & OCO)
- `groww_create_smart_order`: Set up sophisticated GTT (Good Till Triggered) or OCO (One Cancels Other) orders.
- `groww_cancel_smart_order`: Cancel active smart order legs.
- `groww_get_smart_order_list`: Audit your active smart orders.

### 📊 Market Data
- `groww_get_quote`: Fetch depth, price, and volume for any symbol.
- `groww_get_ltp`: Get Last Traded Price for multiple symbols at once.
- `groww_get_ohlc`: Multi-symbol Open, High, Low, Close data.
- `groww_get_historical_candles`: Bulk historical data for backtesting and analysis.

### ⚡ Derivatives (FNO)
- `groww_get_option_chain`: Full option chain for indices (NIFTY, BANKNIFTY) and stocks.
- `groww_get_greeks`: Real-time Delta, Theta, Gamma, and Vega for any contract.
- `groww_get_expiries`: Find next available expiry dates.
- `groww_get_contracts`: List all available strikes and contracts for an expiry.

---

## 🚀 Quick Start

### 1. Prerequisites
Ensure you have [uv](https://github.com/astral-sh/uv) installed (the ultra-fast Python package manager).

### 2. Configure Credentials
Create a `.env.local` file in the project root:
```env
GROWW_API_KEY=your_api_key_here
GROWW_API_SECRET=your_api_secret_here
# Optional: Pre-defined Bearer token
# GROWW_API_TOKEN=your_predefined_token
```

### 3. Install & Run
```bash
# Sync dependencies
uv sync

# Run the SSE server (Default)
uv run .\main.py
```
The server will start at `http://127.0.0.1:8000`.

---

## 🛠️ Usage

### SSE Endpoint
By default, the server runs on SSE. You can connect to it using:
- **Base URL**: `http://127.0.0.1:8000/sse`
- **Postman**: Use the "Server-Sent Events" request type.

### Claude Desktop Integration
Add this to your `claude_desktop_config.json`:

```json
{
  "mcpServers": {
    "groww": {
      "command": "uv",
      "args": [
        "--directory", 
        "C:/Users/lee/Documents/GitHub/groww-python-mcp", 
        "run", 
        "python", 
        "main.py"
      ]
    }
  }
}
```

---

## 🧪 Development & Testing

Use the **MCP Inspector** to interactively test all 18 tools:

```bash
npx @modelcontextprotocol/inspector uv run .\main.py
```

---

## 📜 License
Project is licensed under the MIT License. Developed for the community by [SAGAR-TAMANG](https://github.com/SAGAR-TAMANG).

---
*Disclaimer: This is an unofficial MCP wrapper for the Groww API. Trading involves risk. Use at your own discretion.*

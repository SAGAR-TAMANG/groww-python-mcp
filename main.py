import os
import json
import logging
from typing import Optional, List, Dict, Any, Union
from datetime import datetime

from dotenv import load_dotenv
from pydantic import BaseModel, Field, ConfigDict, field_validator
from mcp.server.fastmcp import FastMCP, Context

from growwapi import GrowwAPI

# Load environment variables
load_dotenv(".env.local")
load_dotenv(".env")

# Setup logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("groww_mcp")

# Initialize FastMCP
mcp = FastMCP("groww_mcp")

# --- Configuration & Auth ---

class GrowwConfig:
    def __init__(self):
        self.api_key = os.getenv("GROWW_API_KEY")
        self.api_secret = os.getenv("GROWW_API_SECRET")
        self.api_token = os.getenv("GROWW_API_TOKEN")
        self._client = None

    def get_client(self) -> GrowwAPI:
        if self._client:
            return self._client
        
        token = self.api_token
        if not token:
            if not self.api_key or not self.api_secret:
                raise ValueError("GROWW_API_KEY and GROWW_API_SECRET must be set if GROWW_API_TOKEN is not provided.")
            
            logger.info("Generating new access token...")
            try:
                token = GrowwAPI.get_access_token(
                    api_key=self.api_key,
                    secret=self.api_secret
                )
                logger.info("Access token generated successfully.")
            except Exception as e:
                logger.error(f"Failed to generate access token: {e}")
                raise

        self._client = GrowwAPI(token)
        return self._client

config = GrowwConfig()

# --- Shared Pydantic Models ---

class StandardInput(BaseModel):
    model_config = ConfigDict(str_strip_whitespace=True, extra='forbid')

class PaginationInput(StandardInput):
    page: Optional[int] = Field(default=0, ge=0, description="Page number (0-indexed)")
    page_size: Optional[int] = Field(default=25, ge=1, le=50, description="Items per page")

class SegmentInput(StandardInput):
    segment: str = Field(..., description="Market segment (e.g., 'CASH', 'FNO')")

# --- Helper Functions ---

def format_response(data: Any, title: str) -> str:
    """Formats data as a readable Markdown string."""
    if not data:
        return f"# {title}\n\nNo data found."
    
    if isinstance(data, list):
        if not data:
            return f"# {title}\n\nEmpty list."
        # Simple table for lists of dicts
        if isinstance(data[0], dict):
            headers = data[0].keys()
            header_row = "| " + " | ".join(headers) + " |"
            separator = "| " + " | ".join(["---"] * len(headers)) + " |"
            rows = []
            for item in data:
                row = "| " + " | ".join(str(item.get(h, "")) for h in headers) + " |"
                rows.append(row)
            return f"# {title}\n\n{header_row}\n{separator}\n" + "\n".join(rows)
    
    return f"# {title}\n\n```json\n{json.dumps(data, indent=2)}\n```"

# --- Account & Portfolio Tools ---

@mcp.tool(name="groww_get_profile")
async def groww_get_profile() -> str:
    """Get the user's Groww profile details."""
    try:
        client = config.get_client()
        profile = client.get_user_profile()
        return format_response(profile, "User Profile")
    except Exception as e:
        return f"Error fetching profile: {str(e)}"

@mcp.tool(name="groww_get_balance")
async def groww_get_balance() -> str:
    """Get available margin and balance details for the user."""
    try:
        client = config.get_client()
        balance = client.get_available_margin_details()
        return format_response(balance, "Account Balance & Margin")
    except Exception as e:
        return f"Error fetching balance: {str(e)}"

@mcp.tool(name="groww_get_holdings")
async def groww_get_holdings() -> str:
    """Get all current equity holdings of the user."""
    try:
        client = config.get_client()
        holdings = client.get_holdings_for_user()
        return format_response(holdings, "Equity Holdings")
    except Exception as e:
        return f"Error fetching holdings: {str(e)}"

@mcp.tool(name="groww_get_positions")
async def groww_get_positions(params: SegmentInput) -> str:
    """
    Get user positions for a specific segment.
    
    Args:
        params: segment (e.g., 'CASH', 'FNO')
    """
    try:
        client = config.get_client()
        positions = client.get_positions_for_user(segment=params.segment)
        return format_response(positions, f"Positions - {params.segment}")
    except Exception as e:
        return f"Error fetching positions: {str(e)}"

# --- Order Models ---

class StandardOrderInput(StandardInput):
    validity: str = Field("DAY", description="Order validity (e.g., 'DAY', 'IOC')")
    exchange: str = Field(..., description="Exchange (e.g., 'NSE', 'BSE')")
    order_type: str = Field(..., description="Order type (e.g., 'LIMIT', 'MARKET', 'SL', 'SL_M')")
    product: str = Field(..., description="Product type (e.g., 'CASH', 'MIS', 'CNC')")
    quantity: int = Field(..., gt=0, description="Order quantity")
    segment: str = Field(..., description="Market segment (e.g., 'CASH', 'FNO')")
    trading_symbol: str = Field(..., description="Trading symbol (e.g., 'RELIANCE')")
    transaction_type: str = Field(..., description="Transaction type ('BUY', 'SELL')")
    price: Optional[float] = Field(0.0, description="Order price (required for LIMIT)")
    trigger_price: Optional[float] = Field(None, description="Trigger price (required for SL/SL_M)")
    order_reference_id: Optional[str] = Field(None, description="Client reference ID")

# --- Order Management Tools ---

@mcp.tool(name="groww_place_order")
async def groww_place_order(order: StandardOrderInput) -> str:
    """
    Place a new standard order (Equity, FNO).
    
    Args:
        order: StandardOrderInput containing all order details.
    """
    try:
        client = config.get_client()
        result = client.place_order(
            validity=order.validity,
            exchange=order.exchange,
            order_type=order.order_type,
            product=order.product,
            quantity=order.quantity,
            segment=order.segment,
            trading_symbol=order.trading_symbol,
            transaction_type=order.transaction_type,
            price=order.price,
            trigger_price=order.trigger_price,
            order_reference_id=order.order_reference_id
        )
        return format_response(result, "Order Placement Result")
    except Exception as e:
        return f"Error placing order: {str(e)}"

@mcp.tool(name="groww_modify_order")
async def groww_modify_order(
    groww_order_id: str,
    segment: str,
    order_type: str,
    quantity: int,
    price: Optional[float] = None,
    trigger_price: Optional[float] = None
) -> str:
    """
    Modify an existing pending order.
    """
    try:
        client = config.get_client()
        result = client.modify_order(
            groww_order_id=groww_order_id,
            segment=segment,
            order_type=order_type,
            quantity=quantity,
            price=price,
            trigger_price=trigger_price
        )
        return format_response(result, "Order Modification Result")
    except Exception as e:
        return f"Error modifying order: {str(e)}"

@mcp.tool(name="groww_cancel_order")
async def groww_cancel_order(groww_order_id: str, segment: str) -> str:
    """
    Cancel an existing pending order.
    """
    try:
        client = config.get_client()
        result = client.cancel_order(groww_order_id=groww_order_id, segment=segment)
        return format_response(result, "Order Cancellation Result")
    except Exception as e:
        return f"Error cancelling order: {str(e)}"

# --- Smart Order (GTT/OCO) Tools ---

@mcp.tool(name="groww_create_smart_order")
async def groww_create_smart_order(
    smart_order_type: str,
    segment: str,
    trading_symbol: str,
    quantity: int,
    product_type: str,
    exchange: str,
    duration: str,
    trigger_price: Optional[str] = None,
    trigger_direction: Optional[str] = None,
    order: Optional[Dict[str, Any]] = None,
    target: Optional[Dict[str, Any]] = None,
    stop_loss: Optional[Dict[str, Any]] = None,
    transaction_type: Optional[str] = None
) -> str:
    """
    Create a Smart Order (GTT or OCO).
    
    For GTT: Provide trigger_price, trigger_direction, order.
    For OCO: Provide target, stop_loss, transaction_type.
    """
    try:
        client = config.get_client()
        result = client.create_smart_order(
            smart_order_type=smart_order_type,
            segment=segment,
            trading_symbol=trading_symbol,
            quantity=quantity,
            product_type=product_type,
            exchange=exchange,
            duration=duration,
            trigger_price=trigger_price,
            trigger_direction=trigger_direction,
            order=order,
            target=target,
            stop_loss=stop_loss,
            transaction_type=transaction_type
        )
        return format_response(result, "Smart Order Creation Result")
    except Exception as e:
        return f"Error creating smart order: {str(e)}"

@mcp.tool(name="groww_cancel_smart_order")
async def groww_cancel_smart_order(segment: str, smart_order_type: str, smart_order_id: str) -> str:
    """Cancel an existing Smart Order (GTT/OCO)."""
    try:
        client = config.get_client()
        result = client.cancel_smart_order(
            segment=segment,
            smart_order_type=smart_order_type,
            smart_order_id=smart_order_id
        )
        return format_response(result, "Smart Order Cancellation Result")
    except Exception as e:
        return f"Error cancelling smart order: {str(e)}"

@mcp.tool(name="groww_get_smart_order_list")
async def groww_get_smart_order_list(
    smart_order_type: Optional[str] = None,
    segment: Optional[str] = None,
    status: Optional[str] = None,
    page: Optional[int] = 0,
    page_size: Optional[int] = 25
) -> str:
    """List Smart Orders (GTT/OCO) with optional filters."""
    try:
        client = config.get_client()
        result = client.get_smart_order_list(
            smart_order_type=smart_order_type,
            segment=segment,
            status=status,
            page=page,
            page_size=page_size
        )
        return format_response(result, "Smart Order List")
    except Exception as e:
        return f"Error fetching smart orders: {str(e)}"

# --- Market Data & FNO Tools ---

@mcp.tool(name="groww_get_quote")
async def groww_get_quote(trading_symbol: str, exchange: str, segment: str) -> str:
    """Fetch the latest quote data for an instrument."""
    try:
        client = config.get_client()
        result = client.get_quote(trading_symbol=trading_symbol, exchange=exchange, segment=segment)
        return format_response(result, f"Quote: {trading_symbol}")
    except Exception as e:
        return f"Error fetching quote: {str(e)}"

@mcp.tool(name="groww_get_ltp")
async def groww_get_ltp(symbols: List[str], segment: str) -> str:
    """
    Fetch the Last Traded Price (LTP) for a list of symbols.
    
    Args:
        symbols: List of symbols (e.g., ['NSE_RELIANCE', 'NSE_INFY'])
        segment: Market segment (CASH, FNO)
    """
    try:
        client = config.get_client()
        result = client.get_ltp(exchange_trading_symbols=tuple(symbols), segment=segment)
        return format_response(result, "LTP Data")
    except Exception as e:
        return f"Error fetching LTP: {str(e)}"

@mcp.tool(name="groww_get_ohlc")
async def groww_get_ohlc(symbols: List[str], segment: str) -> str:
    """Fetch OHLC data for a list of instruments."""
    try:
        client = config.get_client()
        result = client.get_ohlc(exchange_trading_symbols=tuple(symbols), segment=segment)
        return format_response(result, "OHLC Data")
    except Exception as e:
        return f"Error fetching OHLC: {str(e)}"

@mcp.tool(name="groww_get_historical_candles")
async def groww_get_historical_candles(
    exchange: str,
    segment: str,
    groww_symbol: str,
    start_time: str,
    end_time: str,
    candle_interval: str
) -> str:
    """
    Get bulk historical candle data.
    
    Args:
        start_time, end_time: Format 'yyyy-MM-dd HH:mm:ss'
        candle_interval: e.g., '1minute', '5minute', '1day'
    """
    try:
        client = config.get_client()
        result = client.get_historical_candles(
            exchange=exchange,
            segment=segment,
            groww_symbol=groww_symbol,
            start_time=start_time,
            end_time=end_time,
            candle_interval=candle_interval
        )
        return format_response(result, f"Historical Candles: {groww_symbol}")
    except Exception as e:
        return f"Error fetching historical candles: {str(e)}"

@mcp.tool(name="groww_get_option_chain")
async def groww_get_option_chain(exchange: str, underlying: str, expiry_date: str) -> str:
    """Fetch option chain data for FNO contracts."""
    try:
        client = config.get_client()
        result = client.get_option_chain(exchange=exchange, underlying=underlying, expiry_date=expiry_date)
        return format_response(result, f"Option Chain: {underlying} ({expiry_date})")
    except Exception as e:
        return f"Error fetching option chain: {str(e)}"

@mcp.tool(name="groww_get_greeks")
async def groww_get_greeks(exchange: str, underlying: str, trading_symbol: str, expiry: str) -> str:
    """Fetch Greeks data for a specific option contract."""
    try:
        client = config.get_client()
        result = client.get_greeks(
            exchange=exchange,
            underlying=underlying,
            trading_symbol=trading_symbol,
            expiry=expiry
        )
        return format_response(result, f"Greeks: {trading_symbol}")
    except Exception as e:
        return f"Error fetching Greeks: {str(e)}"

@mcp.tool(name="groww_get_expiries")
async def groww_get_expiries(exchange: str, underlying_symbol: str, year: Optional[int] = None, month: Optional[int] = None) -> str:
    """Get available expiry dates for FNO contracts."""
    try:
        client = config.get_client()
        result = client.get_expiries(
            exchange=exchange,
            underlying_symbol=underlying_symbol,
            year=year,
            month=month
        )
        return format_response(result, f"Expiries: {underlying_symbol}")
    except Exception as e:
        return f"Error fetching expiries: {str(e)}"

@mcp.tool(name="groww_get_contracts")
async def groww_get_contracts(exchange: str, underlying_symbol: str, expiry_date: str) -> str:
    """Get available contracts for a specific underlying and expiry date."""
    try:
        client = config.get_client()
        result = client.get_contracts(
            exchange=exchange,
            underlying_symbol=underlying_symbol,
            expiry_date=expiry_date
        )
        return format_response(result, f"Contracts: {underlying_symbol} ({expiry_date})")
    except Exception as e:
        return f"Error fetching contracts: {str(e)}"

if __name__ == "__main__":
    mcp.run('sse')

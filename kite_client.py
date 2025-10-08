"""
Kite Connect Client Wrapper
Handles authentication and provides trading interface
"""

import logging
from typing import Dict, List, Optional, Any
from datetime import datetime, timedelta
import time

try:
    from kiteconnect import KiteConnect
    from kiteconnect.exceptions import KiteException
except ImportError:
    print("⚠️  kiteconnect library not found. Install with: pip install kiteconnect")
    KiteConnect = None
    KiteException = Exception

from config import config

class KiteTradingClient:
    """Wrapper class for Kite Connect API"""
    
    def __init__(self):
        self.kite = None
        self.logger = logging.getLogger(__name__)
        self.is_authenticated = False
        
    def authenticate(self) -> bool:
        """Authenticate with Kite Connect"""
        try:
            if not KiteConnect:
                self.logger.error("KiteConnect library not available")
                return False
                
            credentials = config.get_kite_credentials()
            self.kite = KiteConnect(api_key=credentials["api_key"])
            
            # Set access token
            self.kite.set_access_token(credentials["access_token"])
            
            # Test authentication by fetching profile
            profile = self.kite.profile()
            self.logger.info(f"Successfully authenticated as: {profile.get('user_name', 'Unknown')}")
            self.is_authenticated = True
            return True
            
        except KiteException as e:
            self.logger.error(f"Kite authentication failed: {e}")
            return False
        except Exception as e:
            self.logger.error(f"Authentication error: {e}")
            return False
    
    def get_profile(self) -> Optional[Dict]:
        """Get user profile"""
        if not self.is_authenticated:
            return None
        try:
            return self.kite.profile()
        except Exception as e:
            self.logger.error(f"Failed to get profile: {e}")
            return None
    
    def get_margins(self) -> Optional[Dict]:
        """Get account margins"""
        if not self.is_authenticated:
            return None
        try:
            return self.kite.margins()
        except Exception as e:
            self.logger.error(f"Failed to get margins: {e}")
            return None
    
    def get_positions(self) -> Optional[Dict]:
        """Get current positions"""
        if not self.is_authenticated:
            return None
        try:
            return self.kite.positions()
        except Exception as e:
            self.logger.error(f"Failed to get positions: {e}")
            return None
    
    def get_holdings(self) -> Optional[List[Dict]]:
        """Get current holdings"""
        if not self.is_authenticated:
            return None
        try:
            return self.kite.holdings()
        except Exception as e:
            self.logger.error(f"Failed to get holdings: {e}")
            return None
    
    def get_orders(self) -> Optional[List[Dict]]:
        """Get all orders"""
        if not self.is_authenticated:
            return None
        try:
            return self.kite.orders()
        except Exception as e:
            self.logger.error(f"Failed to get orders: {e}")
            return None
    
    def place_order(self, variety: str, exchange: str, tradingsymbol: str, 
                   transaction_type: str, quantity: int, product: str, 
                   order_type: str, price: Optional[float] = None, 
                   validity: str = "DAY", disclosed_quantity: int = 0, 
                   trigger_price: Optional[float] = None, 
                   squareoff: Optional[float] = None, 
                   stoploss: Optional[float] = None, 
                   trailing_stoploss: Optional[float] = None) -> Optional[str]:
        """Place an order"""
        if not self.is_authenticated:
            self.logger.error("Not authenticated")
            return None
            
        try:
            order_id = self.kite.place_order(
                variety=variety,
                exchange=exchange,
                tradingsymbol=tradingsymbol,
                transaction_type=transaction_type,
                quantity=quantity,
                product=product,
                order_type=order_type,
                price=price,
                validity=validity,
                disclosed_quantity=disclosed_quantity,
                trigger_price=trigger_price,
                squareoff=squareoff,
                stoploss=stoploss,
                trailing_stoploss=trailing_stoploss
            )
            
            self.logger.info(f"Order placed successfully. Order ID: {order_id}")
            return order_id
            
        except KiteException as e:
            self.logger.error(f"Order placement failed: {e}")
            return None
        except Exception as e:
            self.logger.error(f"Unexpected error placing order: {e}")
            return None
    
    def modify_order(self, order_id: str, variety: str, 
                    price: Optional[float] = None, 
                    quantity: Optional[int] = None, 
                    order_type: Optional[str] = None, 
                    validity: Optional[str] = None) -> bool:
        """Modify an existing order"""
        if not self.is_authenticated:
            return False
            
        try:
            self.kite.modify_order(
                order_id=order_id,
                variety=variety,
                price=price,
                quantity=quantity,
                order_type=order_type,
                validity=validity
            )
            self.logger.info(f"Order {order_id} modified successfully")
            return True
            
        except KiteException as e:
            self.logger.error(f"Order modification failed: {e}")
            return False
    
    def cancel_order(self, order_id: str, variety: str = "regular") -> bool:
        """Cancel an order"""
        if not self.is_authenticated:
            return False
            
        try:
            self.kite.cancel_order(order_id=order_id, variety=variety)
            self.logger.info(f"Order {order_id} cancelled successfully")
            return True
            
        except KiteException as e:
            self.logger.error(f"Order cancellation failed: {e}")
            return False
    
    def get_quote(self, instruments: List[str]) -> Optional[Dict]:
        """Get quote for instruments"""
        if not self.is_authenticated:
            return None
        try:
            return self.kite.quote(instruments)
        except Exception as e:
            self.logger.error(f"Failed to get quotes: {e}")
            return None
    
    def get_historical_data(self, instrument_token: int, from_date: datetime, 
                           to_date: datetime, interval: str = "day") -> Optional[List[Dict]]:
        """Get historical data"""
        if not self.is_authenticated:
            return None
        try:
            return self.kite.historical_data(
                instrument_token=instrument_token,
                from_date=from_date,
                to_date=to_date,
                interval=interval
            )
        except Exception as e:
            self.logger.error(f"Failed to get historical data: {e}")
            return None
    
    def get_instruments(self, exchange: str = None) -> Optional[List[Dict]]:
        """Get instruments list"""
        if not self.is_authenticated:
            return None
        try:
            if exchange:
                return self.kite.instruments(exchange)
            return self.kite.instruments()
        except Exception as e:
            self.logger.error(f"Failed to get instruments: {e}")
            return None
    
    def is_market_open(self) -> bool:
        """Check if market is open"""
        now = datetime.now()
        current_time = now.strftime("%H:%M")
        
        # Simple time check (you might want to add holiday calendar)
        if config.MARKET_OPEN_TIME <= current_time <= config.MARKET_CLOSE_TIME:
            # Check if it's a weekday
            if now.weekday() < 5:  # Monday = 0, Sunday = 6
                return True
        return False
    
    def get_portfolio_summary(self) -> Dict[str, Any]:
        """Get comprehensive portfolio summary"""
        if not self.is_authenticated:
            return {}
            
        try:
            positions = self.get_positions()
            holdings = self.get_holdings()
            margins = self.get_margins()
            
            summary = {
                "positions": positions,
                "holdings": holdings,
                "margins": margins,
                "timestamp": datetime.now().isoformat()
            }
            
            return summary
            
        except Exception as e:
            self.logger.error(f"Failed to get portfolio summary: {e}")
            return {}

import hashlib
import hmac
import json
from typing import Dict, Any, Optional
from ..config import settings

def validate_telegram_webapp_data(init_data: str) -> bool:
    """
    Validiert Telegram WebApp Init Data
    """
    try:
        # Parse init data
        parsed_data = parse_qs(init_data)
        
        # Extract hash
        hash_value = parsed_data.get('hash', [None])[0]
        if not hash_value:
            return False
        
        # Remove hash from data for validation
        data_check_string = init_data.replace(f'&hash={hash_value}', '')
        
        # Get bot token (in production, load from environment)
        bot_token = settings.BOT_TOKEN
        if not bot_token:
            print("Error: BOT_TOKEN ist nicht gesetzt!")
            return False
        
        # Create secret key
        secret_key = hmac.new(
            b"WebAppData",
            bot_token.encode(),
            hashlib.sha256
        ).digest()
        
        # Calculate hash
        calculated_hash = hmac.new(
            secret_key,
            data_check_string.encode(),
            hashlib.sha256
        ).hexdigest()
        
        return calculated_hash == hash_value
        
    except Exception as e:
        print(f"Error validating Telegram WebApp data: {e}")
        return False

def extract_telegram_user(init_data: str) -> Optional[Dict[str, Any]]:
    """
    Extrahiert Benutzerdaten aus Telegram WebApp Init Data
    """
    try:
        parsed_data = parse_qs(init_data)
        
        # Extract user data
        user_str = parsed_data.get('user', [None])[0]
        if not user_str:
            return None
        
        user_data = json.loads(user_str)
        return user_data
        
    except Exception as e:
        print(f"Error extracting Telegram user data: {e}")
        return None

def validate_telegram_auth(auth_data: Dict[str, Any]) -> bool:
    """
    Validiert Telegram Auth Data
    """
    try:
        # Basic validation
        required_fields = ['id', 'first_name']
        for field in required_fields:
            if field not in auth_data:
                return False
        
        # Validate ID is numeric
        if not str(auth_data['id']).isdigit():
            return False
        
        return True
        
    except Exception as e:
        print(f"Error validating Telegram auth data: {e}")
        return False 
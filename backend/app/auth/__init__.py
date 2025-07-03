"""
Authentifizierung & Session-Management Modul

Dieses Modul bietet:
- User-Login mit Telefonnummer
- JWT Token Management
- Session-Überprüfung
- Logout und Session-Refresh
"""

from app.routes.auth import router, create_access_token, get_current_user

__all__ = [
    'router',
    'create_access_token',
    'get_current_user'
] 
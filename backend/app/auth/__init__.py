"""
Authentifizierung & Session-Management Modul

Dieses Modul bietet:
- User-Login mit Telefonnummer
- JWT Token Management
- Session-Überprüfung
- Logout und Session-Refresh
"""

from ..routes.auth import get_current_user, create_access_token, router

__all__ = [
    'router',
    'create_access_token',
    'get_current_user'
] 
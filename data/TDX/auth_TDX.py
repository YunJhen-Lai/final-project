"""
TDX (Transport Data Exchange) authentication module.
Provides classes to authenticate and fetch data from TDX API.

Environment variables:
  TDX_APP_ID  : e74106165-cd1d41f5-2b74-4438
  TDX_APP_KEY : b842e80b-389e-4930-892e-c6aefd36f92a
"""
import os
import json
import requests
from pprint import pprint


class TDXAuth:
    """Handle TDX OAuth2 authentication."""

    def __init__(self, app_id: str, app_key: str):
        self.app_id = app_id
        self.app_key = app_key
        self.auth_url = "https://tdx.transportdata.tw/auth/realms/TDXConnect/protocol/openid-connect/token"
        self._access_token = None
        self._auth_response = None

    def get_auth_header(self) -> dict:
        """Return headers for authentication request."""
        return {
            'content-type': 'application/x-www-form-urlencoded',
            'grant_type': 'client_credentials',
            'client_id': self.app_id,
            'client_secret': self.app_key
        }

    def authenticate(self) -> dict:
        """Authenticate with TDX and store access token. Return headers for data API."""
        try:
            response = requests.post(self.auth_url, self.get_auth_header(), timeout=10)
            response.raise_for_status()
            self._auth_response = response
            auth_data = response.json()
            self._access_token = auth_data.get('access_token')
            if not self._access_token:
                raise ValueError("No access_token in response")
            return self.get_data_header()
        except Exception as e:
            raise RuntimeError(f"Authentication failed: {e}")

    def get_data_header(self) -> dict:
        """Return headers for data API requests."""
        if not self._access_token:
            raise RuntimeError("Not authenticated. Call authenticate() first.")
        return {
            'authorization': f'Bearer {self._access_token}',
            'Accept-Encoding': 'gzip'
        }


def get_tdx_auth(app_id: str = None, app_key: str = None) -> TDXAuth:
    """Factory to create and authenticate TDXAuth object.
    
    Args:
        app_id: TDX app ID (falls back to TDX_APP_ID env var)
        app_key: TDX app key (falls back to TDX_APP_KEY env var)
    
    Returns:
        Authenticated TDXAuth instance
    """
    app_id = app_id or os.getenv('TDX_APP_ID')
    app_key = app_key or os.getenv('TDX_APP_KEY')

    if not app_id or not app_key:
        raise ValueError(
            "Must provide app_id and app_key as arguments or set TDX_APP_ID and TDX_APP_KEY environment variables"
        )

    auth = TDXAuth(app_id, app_key)
    auth.authenticate()
    return auth


if __name__ == '__main__':
    # Demo: attempt to authenticate (requires TDX_APP_ID and TDX_APP_KEY env vars)
    try:
        auth = get_tdx_auth()
        print("✓ Authentication successful")
        headers = auth.get_data_header()
        print(f"✓ Data headers: {headers}")
    except Exception as e:
        print(f"✗ Error: {e}")
        print("\nTo use this module, set environment variables:")
        print("  export TDX_APP_ID='your_app_id'")
        print("  export TDX_APP_KEY='your_app_key'")
"""Simple API key authentication.

Used by the master to gate access. If no API key is configured,
all requests are allowed (open-access mode for development).
"""

from typing import Optional

from fastapi import Header, HTTPException, status


class APIKeyAuth:
    """Dependency that validates the X-API-Key header."""

    def __init__(self, expected_key: Optional[str] = None):
        self.expected_key = expected_key

    async def __call__(
        self,
        x_api_key: Optional[str] = Header(None, alias="X-API-Key"),
    ) -> Optional[str]:
        # Open access when no key is configured
        if self.expected_key is None:
            return x_api_key

        if x_api_key is None:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Missing X-API-Key header",
            )

        if x_api_key != self.expected_key:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Invalid API key",
            )

        return x_api_key

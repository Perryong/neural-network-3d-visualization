"""API response models and schemas."""

from dataclasses import dataclass
from typing import Any, Optional


@dataclass
class ApiResponse:
    """Standard API response format."""
    success: bool
    data: Optional[Any] = None
    message: Optional[str] = None

    def to_dict(self) -> dict:
        """Convert to dictionary for JSON serialization."""
        result = {"success": self.success}
        if self.data is not None:
            result["data"] = self.data
        if self.message:
            result["message"] = self.message
        return result


"""Base class for vaccine distribution strategies."""

from abc import ABC, abstractmethod
from typing import Dict


class AllocationStrategy(ABC):
    """Abstract base class for vaccine allocation strategies."""

    @property
    @abstractmethod
    def name(self) -> str:
        """Human-readable strategy name."""
        pass

    @abstractmethod
    def allocate(self, countries: Dict, available_vaccines: int) -> Dict[str, int]:
        """
        Allocate vaccines across countries.

        Args:
            countries: Dict of {name: EnhancedCountry}
            available_vaccines: Total vaccines available today

        Returns:
            Dict of {country_name: vaccines_allocated}
        """
        pass

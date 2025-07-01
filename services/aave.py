class AaveService:
    """Service for interacting with Aave APIs."""

    async def get_health_factor(self, address: str):
        """Fetch health factor for a given address."""
        # TODO: integrate with Aave API
        return 1.4

    async def get_safety_ratio(self, address: str):
        """Fetch safety ratio for a given address."""
        # TODO: integrate with Aave API
        return 140

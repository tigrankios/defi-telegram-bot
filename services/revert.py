class RevertService:
    """Service for interacting with Revert APIs."""

    async def get_active_lps(self, address: str):
        """Fetch active LP positions for a given address."""
        # TODO: integrate with Revert API
        return [
            {"pair": "ETH/USDC", "in_range": False, "fees_usd": 25},
            {"pair": "WBTC/ETH", "in_range": True, "fees_usd": 5},
        ]

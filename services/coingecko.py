class CoingeckoService:
    """Service for fetching prices from Coingecko."""

    async def get_price(self, asset: str):
        """Return current price for the given asset."""
        # TODO: integrate with Coingecko API
        prices = {"eth": 1800, "btc": 30000}
        return prices.get(asset.lower(), 0)

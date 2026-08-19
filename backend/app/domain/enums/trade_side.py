from enum import StrEnum


class TradeSide(StrEnum):
    BUY = "BUY"
    SELL = "SELL"


class AssetType(StrEnum):
    FOREX = "FOREX"
    STOCK = "STOCK"
    CRYPTO = "CRYPTO"
    COMMODITY = "COMMODITY"
    INDEX = "INDEX"
    OTHER = "OTHER"


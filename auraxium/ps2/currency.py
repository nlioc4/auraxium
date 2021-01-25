"""Currency class definition."""

from .._base import Cached
from ..models import CurrencyData
from ..types import LocaleData

__all__ = [
    'Currency'
]


class Currency(Cached, cache_size=10, cache_ttu=3600.0):
    """A currency obtainable by characters.

    Attributes:
        id: The unique ID of this currency entry.
        name: The localised name of this currency.
        icon_id: The image ID of the currency icon image asset.
        inventory_cap: The maximum amount of this currency a character
            may hold.

    """

    collection = 'currency'
    data: CurrencyData
    _dataclass = CurrencyData
    id_field = 'currency_id'

    # Type hints for data class fallback attributes
    id: int
    name: LocaleData
    icon_id: int
    inventory_cap: int

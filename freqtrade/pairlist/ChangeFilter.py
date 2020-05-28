
"""
Static List provider

Provides lists as configured in config.json

 """
import logging
from typing import Dict, List, Any
from copy import deepcopy
from freqtrade.pairlist.IPairList import IPairList

logger = logging.getLogger(__name__)

# TODO:
#   logging
#   branches for freqtrade

class ChangeFilter(IPairList):

    def __init__(self, exchange, pairlistmanager,
                 config: Dict[str, Any], pairlistconfig: Dict[str, Any],
                 pairlist_pos: int) -> None:
        super().__init__(exchange, pairlistmanager, config, pairlistconfig, pairlist_pos)

        self._lowest_volume = pairlistconfig.get('lowest_volume', 30.0)
        self._change_range = pairlistconfig.get('change_range', (None, 10.0))

    @property
    def needstickers(self) -> bool:
        """
        Boolean property defining if tickers are necessary.
        If no Pairlist requries tickers, an empty List is passed
        as tickers argument to filter_pairlist
        """
        return True

    def short_desc(self) -> str:
        """
        Short whitelist method description - used for startup-messages
        -> Please overwrite in subclasses
        """
        return f"{self.name} Filter by 24h Change and Volume"

    def _validate_pair(self, ticker):
        is_volume = float(ticker.get("quoteVolume")) > self._lowest_volume
        priceChangePercent = float(ticker.get("info").get("priceChangePercent"))
        if not self._change_range[0] and not self._change_range[1]:
            #TODO: ERROR
            pass
        is_change_higher = True
        is_change_lower = True
        if self._change_range[0]:
            is_change_lower = priceChangePercent > self._change_range[0]

        if  self._change_range[1]:
            is_change_higher =  priceChangePercent < self._change_range[1]
        is_change = is_change_higher  and is_change_lower
        return is_change and is_volume

    def filter_pairlist(self, pairlist: List[str], tickers: Dict) -> List[str]:
        """
        Filters and sorts pairlist and returns the whitelist again.
        Called on each bot iteration - please use internal caching if necessary
        :param pairlist: pairlist to filter or sort
        :param tickers: Tickers (from exchange.get_tickers()). May be cached.
        :return: new whitelist
        """
        for p in deepcopy(pairlist):
            ticker = tickers.get(p)
            if not ticker:
                pairlist.remove(p)

            elif not self._validate_pair(ticker):
                logger.info(f"remove pair {p}") 
                pairlist.remove(p)

        return pairlist

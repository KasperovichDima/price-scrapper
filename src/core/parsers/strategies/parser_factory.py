"""Factory for getting parsers."""
from typing import Iterable, Type

from interfaces import IParser

from .epicentr import EpicentrParser
from .silpo import SilpoParser
from .tavria import TavriaParser


__parsers: dict[str, Type[IParser]] = {
    'Epicentr': EpicentrParser,
    'Silpo': SilpoParser,
    'Tavria V': TavriaParser
}


def get_parsers(retailers: Iterable[str]) -> Iterable[IParser]:
    """Creates and returns parser for every retailer in retailers list."""

    return [__parsers[_]() for _ in retailers]

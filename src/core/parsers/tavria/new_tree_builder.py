"""TreeBuilder class for creating catalog tree."""
import crud

from project_typing import ElType

from sqlalchemy.orm import Session

from .tag_data_preparator import FactoryCreator
from ...schemas import CatalogFactory
from ...constants import MAIN_PARSER


class TreeBuilder:
    """
    Check if catalog tree exists in database
    and update it with site information.
    TODO: slots.
    """

    __session: Session

    def __call__(self, home_url: str, session: Session) -> None:
        if MAIN_PARSER != 'Tavria':
            return
        self.__session = session
        self.__factories = FactoryCreator(home_url)()

        self.create_categories()
        self.create_subgrouops()
        self.create_grouops()
        self.create_products()

    def create_categories(self) -> None:




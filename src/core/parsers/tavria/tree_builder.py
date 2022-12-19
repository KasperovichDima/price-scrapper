"""TreeBuilder class for creating catalog tree."""
import crud

from project_typing import ElType

from sqlalchemy.orm import Session

from .tag_data_preparator import FactoryCreator
# from ...schemas import CatalogFactory
from ...constants import MAIN_PARSER


class TreeBuilder:
    """
    Check if catalog tree exists in database
    and update it with site information.
    TODO: slots.
    """

    def __call__(self, home_url: str, session: Session) -> None:
        if MAIN_PARSER != 'Tavria':
            return
        self.__session = session
        self.__factories = FactoryCreator(home_url)()
        pass
        # self.__get_objects()

    # def __get_objects(self):
    #     for type_ in ElType:
    #         saved_objects = crud.get_folders(self.__session, ())
    #         objects = []
    #         factories = self.__factories[type_]
    #         for factory in factories:
    #             subgroup_id = 
    #             new_objects = factory.get_objects(parent_id)
    #             objects.extend(new_objects)
    #         crud.add_instances(objects, self.__session)

    # def __get_parent_id(self, factory: CatalogFactory) -> id:


    # def __create_categories(self) -> None:
    #     """Creates Category objects in database."""
    #     factory = self.__factories[ElType.CATEGORY][0]
    #     objects = factory.get_objects()
    #     crud.add_instances(objects, self.__session)

    # def __create_subcategories(self) -> None:
    #     """Creates Subcategories objects in database.
    #     Must be called after the categories are created."""
    #     subcategories = (Folder(name=_.name, type=ElType.SUBCATEGORY,
    #                             parent_id=self.__cat_name_id[_.parent_name])
    #                      for _ in self.__new_folders[ElType.SUBCATEGORY])
    #     crud.add_instances(subcategories, self.__session)

    # def __create_groups(self) -> None:
    #     """Creates Group objects in database. Must be called
    #     after the categories and subcategories are created."""
    #     groups = (Folder(name=_.name, type=ElType.GROUP,
    #                      parent_id=self.__cat_name_id[_.parent_name]
    #                      if _.parent_type == ElType.CATEGORY
    #                      else self.__subcat_name_id[_.parent_name])
    #               for _ in self.__new_folders[ElType.GROUP])
    #     crud.add_instances(groups, self.__session)

    # def __create_products(self) -> None:
    #     """Creates Product objects in database. Must be called
    #     after the categories, subcategories and groups are created."""
    #     ...

    # @property
    # def __folders(self) -> list[Folder]:
    #     return crud.get_folders(self.__session, ())

    # @cached_property
    # def __cat_name_id(self) -> dict[str, int]:
    #     return {_.name: _.id for _ in self.__saved_categories}

    # @cached_property
    # def __saved_categories(self) -> list[Folder]:
    #     names = (_.name for _ in self.__new_folders[ElType.CATEGORY])
    #     return crud.get_folders(self.__session, names=names)

    # @cached_property
    # def __subcat_name_id(self) -> dict[str, int]:
    #     return {_.name: _.id for _ in self.__saved_subcategories}

    # @cached_property
    # def __saved_subcategories(self) -> list[Folder]:
    #     names = (_.name for _ in self.__new_folders[ElType.SUBCATEGORY])
    #     return crud.get_folders(self.__session, names=names)

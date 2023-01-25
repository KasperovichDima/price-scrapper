from project_typing import ElType

from .new_base_factory import BaseFactory

class FolderFactory(BaseFactory):

    def _validate_init_data(self) -> None:
        """TODO: Ref!"""
        try:
            if self._el_type is ElType.CATEGORY:
                assert not all((self._category_name,
                                self._subcategory_name,
                                self._category_name))
            elif self._el_type is ElType.SUBCATEGORY:
                assert not all((self._subcategory_name,
                                self._category_name))
            else:
                assert not self._group_name
            # assert self._object_names
            return
        except AssertionError:
            # will fall in base by raising WrongFactoryConfigurationError
            super()._validate_init_data()

    async def __call__(self, object_box, *args, **kwds) -> None:
        self._object_box = object_box
        await super().__call__(*args, **kwds)

    def add_name(self, name: str) -> None:
        self._object_names.append(name)

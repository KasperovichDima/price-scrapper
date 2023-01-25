from .new_base_factory import BaseFactory


class FolderFactory(BaseFactory):

    async def __call__(self, object_box, *args, **kwds) -> None:
        self._object_box = object_box
        await super().__call__(*args, **kwds)

    def add_name(self, name: str) -> None:
        self._object_names.append(name)

"""Tag data collector."""
from collections import defaultdict, deque

from project_typing import ElType
from project_typing import folder_types

from sqlalchemy.orm import Session

from . import utils as u
from .factory import BaseFactory, FolderFactory, ProductFactory
from .object_box import ObjectBox


#  TODO: Remove after refactoring
Factories = defaultdict[ElType, deque[BaseFactory]]


class FactoryCreator:
    """
    Makes request to source url.
    Parses tags, extracts data.
    Prapares data for objects creation.
    """
    _current_names: dict[ElType, str | None] = dict.fromkeys(folder_types)
    _factories: defaultdict[int, BaseFactory]

    def __init__(self) -> None:
        self._tag_type: ElType = ElType.CATEGORY
        self._factories = defaultdict(self.create_factory)

    def __call__(self, home_url: str, db_session: Session) -> Factories:
        """TODO: Home url should be taken from retailer db object."""
        BaseFactory.object_box = ObjectBox(db_session)
        for tag in u.get_catalog(home_url):
            self._tag_type = u.tag_type_for(tag)
            if not self._tag_type:
                continue
            self._tag = tag
            self._refresh_names()
            assert self._current_names[self._tag_type]
            self._get_factory() + self._current_names[self._tag_type]  # type: ignore
            self._add_product_factory()

        factories = self._collect_factories_by_type()
        assert u.factories_are_valid(factories)
        return factories

    def _refresh_names(self) -> None:
        match self._tag_type:
            case ElType.GROUP:
                if u.group_is_outstanding(self._tag):
                    self._current_names[ElType.SUBCATEGORY] = None
            case ElType.SUBCATEGORY:
                self._current_names[ElType.GROUP] = None
            case ElType.CATEGORY:
                self._current_names[ElType.GROUP] = None
                self._current_names[ElType.SUBCATEGORY] = None

        self._current_names[self._tag_type] = self._tag.text.strip()
        assert self._current_names[self._tag_type]

    def _get_factory(self) -> BaseFactory:
        return self._factories[self._factory_hash]

    @property
    def _factory_hash(self) -> int:
        p_names = (self._current_names[type_] if type_ is not self._tag_type
                   else None for type_ in folder_types)
        return hash((self._tag_type, *p_names))

    def _add_product_factory(self) -> None:
        if self._tag_type is not ElType.GROUP:
            return
        self._tag_type = ElType.PRODUCT
        self._get_factory()

    def create_factory(self) -> BaseFactory:
        schema = u.get_schema_for(self._tag_type)
        init_payload = schema(
            el_type=self._tag_type,
            category_name=self._current_names[ElType.CATEGORY],
            subcategory_name=self._current_names[ElType.SUBCATEGORY],
            group_name=self._current_names[ElType.GROUP],
            url=u.get_url(self._tag)
        )
        create_cls = ProductFactory if self._tag_type is ElType.PRODUCT\
            else FolderFactory
        return create_cls(**init_payload.dict())

    def _collect_factories_by_type(self) -> Factories:
        factories: Factories = defaultdict(deque)
        for _ in self._factories.values():
            factories[_._el_type].append(_)
        return factories

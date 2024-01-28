from collections import OrderedDict
from collections.abc import Iterator, MutableMapping
from typing import Any, Generic, Hashable, TypeVar

K = TypeVar('K', bound=Hashable)
V = TypeVar('V', bound=Any)


class LRUCache(Generic[K, V], MutableMapping[K, V]):
    def __init__(self, capacity: int = -1):
        self.capacity = capacity
        self.__cache: OrderedDict[K, V] = OrderedDict()

    def __delitem__(self, __key: K) -> None:
        self.__cache.pop(__key)

    def __getitem__(self, __key: K) -> V:
        self.__cache.move_to_end(__key)
        return self.__cache[__key]

    def __iter__(self) -> Iterator[K]:
        return iter(self.__cache)

    def __setitem__(self, __key: K, __value: V) -> None:
        if len(self.__cache) >= self.capacity:
            self.__cache.popitem(last=False)

        self.__cache[__key] = __value
        self.__cache.move_to_end(__key)

    def __len__(self) -> int:
        return len(self.__cache)

    def __contains__(self, __key: object) -> bool:
        return __key in self.__cache

    def clear(self) -> None:
        self.__cache.clear()

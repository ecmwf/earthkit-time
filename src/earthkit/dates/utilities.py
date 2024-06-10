from typing import Iterable, Iterator, TypeVar

T = TypeVar("T")


def merge_sorted(its: Iterable[Iterable[T]]) -> Iterator[T]:
    its = [iter(it) for it in its]
    sentinel = object()
    items = [None for _ in its]
    while its:
        to_del = set()
        pick = None
        for i, it in enumerate(its):
            if items[i] is None:
                item = next(it, sentinel)
                if item is sentinel:
                    to_del.add(i)
                    continue
                else:
                    items[i] = item
            if pick is None or items[i] < items[pick]:
                pick = i
        if pick is None:
            return
        yield items[pick]
        items[pick] = None
        for i in to_del:
            del items[i]
            del its[i]

from collections import namedtuple
from typing import List, Union, Callable


# The current state of a group_item depth first search.
StackEntry = namedtuple("StackEntry", ["group", "item", "items", "index", "total"])


def iterate_groups(
    root_group: object,
    get_group: Callable[[object, object, List[StackEntry]], object],
    get_items: Callable[[object, List[StackEntry]], List[object]] = lambda item: item,  # turns the algorithm into uniform type node traversal
    on_group: Callable[[object, List[StackEntry]], Union[bool, None]] = None,
    on_item: Callable[[object, object, List[StackEntry]], Union[bool, None]] = None,
    depth=-1,
    stack=None,
):
    """
    Groups have multiple items.
    Items have only one unique group.
        - If groups are the same as the items, (ie get_group=lambda item: item),
          then groups become nodes, and only one of on_group or on_item needs to be set.

    Effectively a depth first search with a few extra safety checks.

    I know this is over complicated... but I might want to reuse it in future elsewhere...
    """
    # check for nulls
    if root_group is None: # pragma: no cover
        if len(stack) > 0:
            raise RuntimeError("This should never happen, do not set the stack before calling this function.")
        raise Exception("root_group cannot be none")
    # check for nulls
    if on_group is None and on_item is None: # pragma: no cover
        raise Exception("At least one of on_group and on_item must be specified")
    # initialise
    if stack is None:
        stack = []
    # on each group, can skip if returns false
    if on_group is not None:
        flag = on_group(root_group, stack)
        if flag is not None and not flag:
            return
    # get all items from group, and skip if None
    items = get_items(root_group, stack)
    if items is None: # pragma: no cover
        return
    if not (type(items) == list or type(items) == tuple): # pragma: no cover
        raise Exception("Items must be in list form")
    # iterate
    for index, item in enumerate(items):
        # skip if none
        if item is None:
            continue
        # next stack
        next_stack = stack + [StackEntry(root_group, item, items, index, len(items))]
        # on each item, can skip if returns false
        if on_item is not None:
            flag = on_item(root_group, item, next_stack)
            if flag is not None and not flag:
                continue
        # break early based on depth
        if depth is not None and 0 <= depth <= len(next_stack):
            continue
        # skip if none
        next_group = get_group(root_group, item, next_stack)
        if next_group is None:
            continue
        # recurse
        iterate_groups(
            next_group,
            get_group=get_group,
            get_items=get_items,
            on_group=on_group,
            on_item=on_item,
            stack=next_stack,
            depth=depth,
        )

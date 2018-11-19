import logging
import operator
from collections import namedtuple
from dashboard.shared.color import *
from typing import Type, List, Union, Callable
from django.db.models import Model, Field
from dashboard.shared.iter import StackEntry, iterate_groups


logger = logging.getLogger('dashboard')


# ========================================================================= #
# MODEL ITERATIONS                                                          #
# ========================================================================= #


def iterate_model(
    root_model=Type[Model],
    on_model: Callable[[Type[Model], List[StackEntry]], Union[bool, None]] = None,
    on_field: Callable[[Type[Model], Field, List[StackEntry]], Union[bool, None]] = None,
    skip_reverse_model=True,
    skip_foreign_model=False,
    skip_reverse_field=False,
    skip_foreign_field=False,
    depth=-1,
):
    """
    Depth first search on fields and relations in a model.

    I know this is overcomplicated... but I might want to reuse it in future elsewhere...
    """
    # if not (skip_reverse_model ^ skip_foreign_model) and not (skip_reverse_field ^ skip_foreign_field):
    #     raise Exception("The function might recurse infinitely, skip at least one type of relation.")
    iterate_groups(
        root_group=root_model,
        on_group=on_model,
        on_item=on_field,
        get_group=lambda model, field, stack: field.related_model if ((field.many_to_one and not skip_foreign_model) or (field.one_to_many and not skip_reverse_model)) and (field.related_model not in [e.group for e in stack]) else None,
        get_items=lambda model, stack: [f for f in model._meta.get_fields() if not (f.many_to_one and skip_foreign_field) and not (f.one_to_many and skip_reverse_field)],
        depth=depth,
    )


ModelVisitStack = namedtuple("ModelVisit", ['field', 'model', 'stack'])


def iterate_model_visits(
    root_model: Type[Model],
    skip_reverse_model=True,
    skip_foreign_model=False,
    depth=-1
) -> List[ModelVisitStack]:
    """
    Returns an ordered list of all the data points including the stack at each step
    of a depth first search traversal of the models fields.
    """

    visit_stack = []
    iterate_model(
        root_model=root_model,
        on_model=lambda model, stack: visit_stack.append(ModelVisitStack(None, model, stack)),
        on_field=lambda model, field, stack: visit_stack.append(ModelVisitStack(field, model, stack)),
        skip_reverse_model=skip_reverse_model,
        skip_foreign_model=skip_foreign_model,
        depth=depth,
    )
    return visit_stack


def get_model_relations(model: Type[Model], reverse_relations=True, foreign_relations=True, depth=-1):
    """
    Get all the reachable fields from a model.
    """
    fields = {}
    if reverse_relations and foreign_relations: # pragma: no cover
        fields.update(get_model_relations(model, reverse_relations=True, foreign_relations=False, depth=depth))
        fields.update(get_model_relations(model, reverse_relations=False, foreign_relations=True, depth=depth))
    elif reverse_relations or foreign_relations:
        iterate_model(
            root_model=model,
            on_field=lambda model, field, stack: operator.setitem(fields, f"__".join([entry.item.name for entry in stack]), field),
            skip_reverse_model=not reverse_relations,
            skip_foreign_model=not foreign_relations,
            depth=depth,
        )
    else: # pragma: no cover
        raise Exception("At least one of reverse or foreign must be True")
    return fields


# ========================================================================= #
# PRETTY PRINT MODELS                                                       #
# ========================================================================= #


def model_relations_string(
    root_model=Type[Model],
    skip_reverse_model=True,
    skip_foreign_model=False,
    relative_names=True,
    relations_only=False,
    composite_keys=True,
    depth=-1,
):
    """
    Could be done directly with recursion,
    but this way the iteration code can be reused.
    """

    # iterate through everything
    visit_stack = iterate_model_visits(root_model=root_model, skip_reverse_model=skip_reverse_model, skip_foreign_model=skip_foreign_model, depth=depth)

    # helper functions
    def get_scaffold_str(stack: List[StackEntry]):
        s = ''
        for entry in stack:
            s += '│     ' if entry.index + 1 < entry.total else '      '
        return s

    def get_scaffold_branch_str(entry: StackEntry):
        return "├─" if entry.index + 1 < entry.total else "└─"

    def colorize_model(model: Type[Model]):
        return bold + red

    def get_model_string(visit: ModelVisitStack):
        string = f"[{colorize_model(visit.model)}{visit.model.__name__}{reset}]"
        if composite_keys and any(len(unique) > 0 for unique in visit.model._meta.unique_together):
            string += " -> " + " ".join("(" + ", ".join(underline + lgreen + name + reset for name in unique) + ")" for unique in visit.model._meta.unique_together)
        return string

    def colorize_field(f: Field):
        # field not created by us
        color = reverse if (f.auto_created and not f.one_to_many) else ""
        # unique fields
        color += underline if any(f.name in unique for unique in f.model._meta.unique_together) else ""
        # various different styles
        color += lred if (hasattr(f, 'primary_key') and f.primary_key) else (lyellow if f.many_to_one else (lcyan if f.one_to_many else lgrey))
        # return result
        return color

    def get_field_string(visit: ModelVisitStack):
        stack = visit.stack if relative_names else visit.stack[-1:]
        string = f"{grey}__{reset}".join([
            f"{bold if i+1 >= len(stack) else dim}{colorize_field(entry.item)}{entry.item.name}{reset}"
            for i, entry in enumerate(stack)
        ])
        return string

    # append structures
    string = ""
    for i, visit in enumerate(visit_stack):
        if i > 0:
            string += "\n"
        if not visit.field:
            string += get_scaffold_str(visit.stack) + get_model_string(visit)
        elif (not relations_only) or (not skip_reverse_model and visit.field.one_to_many) or (not skip_foreign_model and visit.field.many_to_one):
            # TODO: fix scaffold bug with relations_only enabled.
            string += get_scaffold_str(visit.stack[:-1]) + get_scaffold_branch_str(visit.stack[-1]) + get_field_string(visit)

    # result
    return string

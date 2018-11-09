

# ========================================================================= #
# COLORS                                                                    #
# ========================================================================= #

# \033 == \x1B # But \033 is more portable

# please note the naming convention breakage for $black, $grey, $lgrey, $white
# and the corresponding background colors prefixed with 'b'

black = "\033[30m"   ; grey = "\033[90m"     ; bblack = "\033[40m"   ; bgrey = "\033[100m"
red = "\033[31m"     ; lred = "\033[91m"     ; bred = "\033[41m"     ; blred = "\033[101m"
green = "\033[32m"   ; lgreen = "\033[92m"   ; bgreen = "\033[42m"   ; blgreen = "\033[102m"
yellow = "\033[33m"  ; lyellow = "\033[93m"  ; byellow = "\033[43m"  ; blyellow = "\033[103m"
blue = "\033[34m"    ; lblue = "\033[94m"    ; bblue = "\033[44m"    ; blblue = "\033[104m"
magenta = "\033[35m" ; lmagenta = "\033[95m" ; bmagenta = "\033[45m" ; blmagenta = "\033[105m"
cyan = "\033[36m"    ; lcyan = "\033[96m"    ; bcyan = "\033[46m"    ; blcyan = "\033[106m"
lgrey = "\033[37m"   ; white = "\033[97m"    ; blgrey = "\033[47m"   ; blwhite = "\033[107m"

_ = ""
bold = "\033[1m"      ; reset_bold = "\033[21m"
dim = "\033[2m"       ; reset_dim = "\033[22m"
underline = "\033[4m" ; reset_underline = "\033[24m"
blink = "\033[5m"     ; reset_blink = "\033[25m"
reverse = "\033[7m"   ; reset_reverse = "\033[27m"
hidden = "\033[8m"    ; reset_hidden = "\033[28m"

reset = "\033[0m"              # reset everything
reset_fg = "\033[39m"          # resets foreground color only
reset_bg = "\033[49m"          # resets background color only
reset_attributes = "\033[20m"  # resets underline, etc only (not colors)


# class TreePrinter(object):
#     """
#     Prints out a nice tree representation of an object.
#     """
#
#     def __init__(self,
#                  get_items: Callable[[object], List],
#                  get_group: Callable[[object, object], object],
#                  get_group_str: Callable[[object, List[Tuple[object, object]]], str] = lambda group, stack: f"[{str(group)}]",
#                  get_item_str: Callable[[object, object, List[Tuple[object, object]]], str] = lambda group, item, stack: str(item),
#                  ):
#         self._get_items = get_items
#         self._get_group = get_group
#         self._get_group_str = get_group_str
#         self._get_item_str = get_item_str
#
#     def generate(self, group: object):
#         return self._recurse(group)
#
#     def print(self, group):
#         print(self.generate(group))
#
#     def _get_scaffold_str(self, index_stack: List):
#         """
#         :param index_stack:
#         :return: A string to prepend to an item or group containing the pathway characters of other items and groups.
#         """
#         s = ''
#         for index, length in index_stack:
#             s += '│   ' if index + 1 < length else '    '
#         return s
#
#     def _get_scaffold_branch_str(self, index: int, length: int):
#         """
#         :param index: The current index in the enumeration.
#         :param sizable: An object that can be enumerated.
#         :return: A t-junction or left turn represented in characters.
#         """
#         return "├─" if index + 1 < length else "└─"
#
#     def _recurse(self, group: object, index_stack: List = None, group_stack: List = None):
#         """
#         :param group: The root object.
#         :param index_stack: Used internally, do not set this.
#         :return: Generate the string representing the hierarchy.
#         """
#         # initialise stack
#         if index_stack is None:
#             if group_stack != index_stack:
#                 raise RuntimeError("Both stacks must be uninitialised")
#             index_stack, group_stack = [], []
#         elif len(index_stack) != len(group_stack):
#             raise RuntimeError("Both stacks must be the same length")
#
#         # skip if group is invalid
#         if group is None:
#             return ""
#
#         scaffold = self._get_scaffold_str(index_stack)
#         # append group to string
#         string = scaffold + self._get_group_str(group, group_stack) + "\n"
#         # get items from group
#         items = self._get_items(group)
#
#         # skip if items are invalid
#         if items is None:
#             return string
#
#         for index, item in enumerate(items):
#             new_index_stack, new_group_stack = (index_stack+[(index, len(items))]), (group_stack+[(group, item)])
#             # append item to string
#             string += scaffold + self._get_scaffold_branch_str(index, len(items)) + self._get_item_str(group, item, new_group_stack) + "\n"
#             # skip if item is invalid
#             if item is None:
#                 continue
#             # get next set of values
#             string += self._recurse(self._get_group(group, item), index_stack=new_index_stack, group_stack=new_group_stack)
#
#         return string
#
#
# class ModelForeignTreePrinter(TreePrinter):
#     def __init__(self,
#                  get_model: Callable[[Field], Type[Model]]=lambda field: field.related_model if field.many_to_one else None,
#                  get_fields: Callable[[Type[Model]], List[Field]] = lambda model: model._meta.get_fields(),
#                  colorize_model: Callable[[Type[Model], List[Tuple[Type[Model], Field]]], str]=lambda model, stack: lred,
#                  colorize_field: Callable[[Field, List[Tuple[Type[Model], Field]]], str]=lambda field, stack: (underline if field.auto_created else "") + (lred if hasattr(field, 'primary_key') and field.primary_key else (lyellow if field.many_to_one else (lgreen if field.one_to_many else grey))),
#                  ):
#         super().__init__(
#             get_items=lambda group: get_fields(group),
#             get_group=lambda group, item: get_model(item),
#             get_group_str=lambda model, stack: f"[{colorize_model(model, stack)}{model.__name__}{reset}]",
#             get_item_str=lambda model, field, stack: f"{grey}__{reset}".join(f"{bold if i+1 >= len(stack) else dim}{colorize_field(f, stack)}{f.name}{reset}" for i, (m, f) in enumerate(stack))
#         )
#
#     def generate(self, model: Type[Model]):
#         return super(ModelForeignTreePrinter, self).generate(model)
#
#     def print(self, model: Type[Model]):
#         return super(ModelForeignTreePrinter, self).print(model)
#
#
# class ModelReverseTreePrinter(ModelForeignTreePrinter):
#     def __init__(self,
#                  get_model: Callable[[Field], Type[Model]] = lambda field: field.related_model if field.one_to_many else None,
#                  colorize_model: Callable[[Type[Model], List[Tuple[Type[Model], Field]]], str] = lambda model, stack: lmagenta
#                  ):
#         super().__init__(get_model=get_model, colorize_model=colorize_model)

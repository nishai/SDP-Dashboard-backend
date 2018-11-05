from django.urls import resolve


_DEPRECATED_VIEWS = {}


# TODO
# def parametrized(dec):
#     """
#     decorator for decorators.
#     Allows arguments to be passed to the intended decorator.
#     """
#     # import inspect
#     # default_kwargs = {
#     #     k: v.default
#     #     for k, v in inspect.signature(dec).parameters.items()
#     #     if v.default is not inspect.Parameter.empty
#     # }
#     def layer(*args, **kwargs):
#         def repl(f):
#             return dec(f, *args, **kwargs)
#         return repl
#     return layer

# def WARN_view_deprecated(obj):

#     func_path = obj.__module__ + "." + obj.__name__
#     if func_path in _DEPRECATED_VIEWS:
#         raise Exception(f"{func_path}: Already registered as deprecated.")
#     _DEPRECATED_VIEWS[func_path] = ''
#     return obj

def WARN_view_deprecated(reason=''):
    """
    Register a view as deprecated.
    :param reason: Deprecation message
    :return:
    """
    def depricate_view_dec(obj):
        func_path = obj.__module__ + "." + obj.__name__
        if func_path in _DEPRECATED_VIEWS:
            raise Exception(f"{func_path}: Already registered as deprecated.")
        if type(reason) != str:
            raise Exception("Deprecation reason must be a string")
        _DEPRECATED_VIEWS[func_path] = reason
        return obj
    # determine if called directly
    if type(reason) == str:
        return depricate_view_dec
    else:
        obj, reason = reason, ''
        return depricate_view_dec(obj)


class DeprecatedViewsMiddleware:
    """
    Intended to print a message that a route is deprecated,
    each time it is called -- intended to be annoying.
    """
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request, *args, **kwargs):
        func_path = resolve(request.path)._func_path
        if func_path in _DEPRECATED_VIEWS:
            print(f"[\033[91mDEPRECATED\033[00m]: \033[90m{request.path}\033[00m - \033[90m{func_path}\033[00m {_DEPRECATED_VIEWS[func_path]}")
        return self.get_response(request)

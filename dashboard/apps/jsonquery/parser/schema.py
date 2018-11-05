

class classproperty(property):
    """
    Marks a classes function as static & as a property
    """
    def __get__(self, cls, owner):
        return classmethod(self.fget).__get__(None, owner)()


# ========================================================================= #
# SCHEMA - https://json-schema.org & https://pypi.org/project/jsonschema    #
# Defines the scheme that a request must follow.                            #
# Advantage is the scheme can be validated on both the front and back end.  #
# ========================================================================= #


class Schema:
    """
    Helps build a jsonschema object.
    Useful due to autocomplete and arg checking.
    """

    @classproperty
    def str(cls): return {"type": "string"}

    @classproperty
    def int(cls): return {"type": "integer"}

    @classproperty
    def bool(cls): return {"type": "boolean"}

    @classproperty
    def float(cls): return {"type": "number"}

    @classmethod
    def const(cls, value): return {"const": value}

    @classmethod
    def any(cls, *types): return {"anyOf": list(types)}

    @classmethod
    def enum(cls, *values): return {"enum": list(values)}

    @classmethod
    def object(cls, properties, not_required=None, definitions=None, title=None):
        if not_required is None:
            not_required = set()
        if definitions is None:
            definitions = {}
        return {
            "type": "object",
            "properties": properties,
            "required": list(set(properties) - set(not_required)),
            "additionalProperties": False,
            "definitions": definitions,
            **({} if title is None else {"title": title})
        }

    @classmethod
    def array(cls, items=None, unique=True, min_size=0):
        return {
            "type": "array",
            "items": items,
            "uniqueItems": unique,
            "minItems": min_size
        }

    @classmethod
    def action(cls, type_name, data=None, not_required=None):
        assert (type(data) == dict and 'action' not in data) or (data is None)
        if data is None:
            return Schema.object({
                'action': {"const": type_name}
            })
        else:
            return Schema.object({
                'action': {"const": type_name},
                **data
            }, not_required=set([] if not_required is None else not_required) - {'action'})

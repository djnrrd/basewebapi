class JSONBaseObject(dict):
    """Create a basic object representing a RESTful API JSON object.  If
    you need to enforce certain key/value pairs be present in an object,
    override the __init__ method and provide a list or tuple of these
    keys as object_keys.

    If there are child objects or lists of objects expected, a dictionary
    of key and object type can be provided as child_objects to create
    those objects.

    :param object_keys: A list of keys to enforce within the object
    :param child_objects: A dictionary of keys and object types to raise
        child objects as
    :param kwargs: The JSON object in keyword argument format
    """

    def __str__(self) -> str:
        if 'name' in self:
            return self['name']
        else:
            return super().__str__()

    def __repr__(self) -> str:
        if 'name' in self:
            return self['name']
        else:
            return super().__repr__()

    def __init__(self,
                 object_keys: list[str] = None,
                 child_objects: dict[str, object] = None,
                 **kwargs) -> None:
        for k in kwargs:
            if object_keys and k not in object_keys:
                raise KeyError(f"{k} is not a valid key for "
                               f"self.__class__.__name__")
            if child_objects and k in child_objects and kwargs[k]:
                kwargs[k] = child_objects[k].from_json(kwargs[k])
        super().__init__(**kwargs)

    @classmethod
    def from_json(cls, data: dict) -> 'JSONBaseObject':
        """Create a new object from JSON data

        :param data: JSON data returned from API
        :return: Class object
        :raises ValueError: If a dictionary is not provided
        """
        if isinstance(data, dict):
            return cls(**data)
        else:
            raise ValueError('Expected dictionary object')


class JSONBaseList(list):

    @classmethod
    def from_json(cls,
                  data: list,
                  item_class: JSONBaseObject = JSONBaseObject) \
            -> 'JSONBaseList':
        """Create a new list from JSON data

        :param data: JSON data returned from API
        :param item_class: The class to create individual objects as
        :return: Class object
        :raises ValueError: If a list is not provided
        """
        if isinstance(data, list):
            temp_list = list()
            for item in data:
                temp_list.append(item_class.from_json(item))
            return cls(temp_list)
        else:
            raise ValueError('Expected list object')

    def filter(self, field: str, search_val: str, fuzzy: bool = False) \
            -> 'JSONBaseList':
        """Search for an object and return a List of matches

        :param field: The search field
        :param search_val: The search value
        :param fuzzy: If the search should be for the exact value (False) or a
            substring of the value
        :return: A list of matches
        """
        if fuzzy:
            ret_list = [x for x in self
                        if str(search_val).lower()
                        in str(x.get(field)).lower()]
        else:
            ret_list = [x for x in self if x.get(field) == search_val]
        return self.__class__(ret_list)

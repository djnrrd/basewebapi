class JSONBaseObject(dict):
    """Create a basic object representing a RESTful API JSON object.  If
    you need to enforce certain key/value pairs be present in an object,
    override the __init__ method and provide a list or tuple of these
    keys as object_keys.

    If there are child objects or lists of objects expected, a dictionary
    of key and object type can be provided as child_objects to create
    those objects.

    :param object_keys: A list of keys to enforce within the object
    :type object_keys: list
    :param child_objects: A dictionary of keys and object types to raise
        child objects as
    :type child_objects: dict
    :param kwargs: The JSON object in keyword argument format
    """
    def __str__(self):
        if 'name' in self:
            return self['name']
        else:
            return super().__str__()

    def __repr__(self):
        if 'name' in self:
            return self['name']
        else:
            return super().__repr__()

    def __init__(self, object_keys=[], child_objects={}, **kwargs):
        for k in kwargs:
            if all([object_keys, k not in object_keys]):
                raise KeyError(f"{k} is not a valid key for "
                               f"self.__class__.__name__")
            if all([k in child_objects, kwargs[k]]):
                kwargs[k] = child_objects[k].from_json(kwargs[k])
        super().__init__(**kwargs)


    @classmethod
    def from_json(cls, data):
        """Create a new object from JSON data

        :param data: JSON data returned from API
        :type data: dict
        :return: Class object
        :rtype: JSONBaseObject
        :raises ValueError: If a dictionary is not provided
        """
        if isinstance(data, dict):
            return cls(**data)
        else:
            raise ValueError('Expected dictionary object')


class JSONBaseList(list):

    @classmethod
    def from_json(cls, data, item_class=JSONBaseObject):
        """Create a new list from JSON data

        :param data: JSON data returned from API
        :type data: list
        :param item_class: The class to create individual objects as
        :type data: object
        :return: Class object
        :rtype: JSONBaseList
        :raises ValueError: If a list is not provided
        """
        if isinstance(data, list):
            temp_list = list()
            for item in data:
                temp_list.append(item_class.from_json(item))
            return cls(temp_list)
        else:
            raise ValueError('Expected list object')

    def filter(self, field, search_val, fuzzy=False):
        """Search for an object and return an List of matches

        :param field: The search field
        :type field: str
        :param search_val: The search value
        :type search_val: (str, int, bool, float)
        :param fuzzy: If the search should be for the exact value (False) or a
            substring of the value
        :type fuzzy: bool
        :return: A list of matches
        :rtype: s1BaseList
        """
        ret_list = list()
        if field in self[0]:
            for item in self:
                field_val = item[field]
                # Don't match anything that's not present.
                if field_val:
                    # If we're dealing with strings, move them to lower case
                    if all([isinstance(search_val, str),
                           isinstance(field_val, str)]):
                        field_val = field_val.lower()
                        search_val = search_val.lower()
                    if fuzzy:
                        ret_list.append(item) if search_val in field_val \
                            else None
                    else:
                        ret_list.append(item) if field_val == search_val \
                            else None
            return self.__class__(ret_list)
        else:
            raise KeyError(f"Could not find {field} in objects")
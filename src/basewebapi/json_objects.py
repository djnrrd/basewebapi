"""A set of basic objects for inheriting that map JSON Objects and Lists to
python dict and list style objects.

"""
from typing import Dict, List


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
        return super().__str__()

    def __repr__(self) -> str:
        if 'name' in self:
            return self['name']
        return super().__repr__()

    def __init__(self,
                 object_keys: List[str] = None,
                 child_objects: Dict[str, object] = None,
                 **kwargs) -> None:
        tmp_dict = kwargs.copy()
        for key, value in kwargs.items():
            if object_keys and key not in object_keys:
                raise KeyError(f"{key} is not a valid key for "
                               f"{self.__class__.__name__}")
            if child_objects and key in child_objects and value:
                tmp_dict[key] = child_objects[key].from_json(value)
        super().__init__(**tmp_dict)

    @classmethod
    def from_json(cls, data: Dict) -> 'JSONBaseObject':
        """Create a new object from JSON data

        :param data: JSON data returned from API
        :return: Class object
        :raises ValueError: If a dictionary is not provided
        """
        if isinstance(data, dict):
            return cls(**data)
        raise ValueError('Expected dictionary object')


class JSONBaseList(list):
    """Create a basic list object representing a RESTful API JSON list.
    """

    @classmethod
    def from_json(cls,
                  data: List,
                  item_class: JSONBaseObject = JSONBaseObject) \
            -> 'JSONBaseList':
        """Create a new list from JSON data

        :param data: JSON data returned from API
        :param item_class: The class to create individual objects as
        :return: Class object
        :raises ValueError: If a list is not provided
        """
        if isinstance(data, list):
            temp_list = []
            for item in data:
                temp_list.append(item_class.from_json(item))
            return cls(temp_list)
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

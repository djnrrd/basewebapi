class JSONBaseObject(dict):

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
    def from_json(cls, data, item_class):
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
            if fuzzy:
                if isinstance(search_val, str):
                    ret_list = [x for x in self if
                                search_val.lower() in x[field].lower()]
                else:
                    ret_list = [x for x in self if search_val in x[field]]
            else:
                if isinstance(search_val, str):
                    ret_list = [x for x in self if
                                x[field].lower() == search_val.lower()]
                else:
                    ret_list = [x for x in self if x[field] == search_val]
            return self.__class__(ret_list)
        else:
            raise KeyError(f"Could not find {field} in objects")
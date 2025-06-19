from basewebapi import BaseWebAPI, JSONBaseObject, JSONBaseList


class PokeBaseObject(JSONBaseObject):
    pass


class PokeBaseList(JSONBaseList):
    pass


class Pokemon(PokeBaseObject):

    def __init__(self, **kwargs):
        """The Pokemon data type includes many lists of other data types.
        Define just the 'abilities' field to create the child
        PokemonAbilities list.
        """
        child_objects = {"abilities": PokemonAbilities}
        super().__init__(child_objects=child_objects, **kwargs)


class PokemonAbilities(PokeBaseList):

    @classmethod
    def from_json(cls, data):
        """Make this return a list of PokemonAbility objects"""
        return super().from_json(data, PokemonAbility)


class PokemonAbility(PokeBaseObject):
    pass


class PokeAPI(BaseWebAPI):

    def __init__(self):
        """The Poke API is a simple, static API with no authentication so
        object initialisation does not require external arguments"""
        # Call super with the static values of the Poke API
        super().__init__("pokeapi.co", "", "", secure=True)
        # Headers tend to vary from API to API so these would get set after
        # calling super which will have initiallised self.headers as an empty
        # dictionary
        self.headers["Accept"] = "application/json"

    def get_pokemon(self, pokemon_name):
        """Get data about an individual pokemon"""
        # Path should be the absolute path to the API resource, in this
        # instance the pokemon name makes up part of the path
        path = f"/api/v2/pokemon/{pokemon_name}/"
        pokemon_data = self._transaction("get", path)
        # any further processing you may need to do
        # Return the Pokemon object parsed from the JSON object
        return Pokemon.from_json(pokemon_data)

    def _transaction(self, method, path, **kwargs):
        # Any pre-processing here
        r = super()._transaction(method, path, **kwargs)
        # We know that this is a JSON based API so we can use the requests
        # json method of the Response object
        return r.json()


def main() -> list:
    """Get 4 Pokemon objects and return them in a list

    :return: List of Pokemon objects
    """
    poke_api = PokeAPI()
    result = list()
    for pokemon in ["mew", "ditto", "pikachu", "smoochum"]:
        result.append(poke_api.get_pokemon(pokemon))
    return result


if __name__ == "__main__":
    results = main()
    print([x for x in results])
    print([type(x) for x in results])

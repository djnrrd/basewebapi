from basewebapi.asyncbaseweb import AsyncBaseWebAPI
from basewebapi import JSONBaseObject, JSONBaseList
import asyncio
import pprint


class Pokemon(JSONBaseObject):

    def __init__(self, **kwargs):
        """The Pokemon data type includes many lists of other data types.
        Define just the 'abilities' field to create the child
        PokemonAbilities list.
        """
        child_objects = {'abilities': PokemonAbilities}
        super().__init__(child_objects=child_objects, **kwargs)


class PokemonAbilities(JSONBaseList):

    @classmethod
    def from_json(cls, data):
        """Make this return a list of PokemonAbility objects
        """
        return super().from_json(data, PokemonAbility)


class PokemonAbility(JSONBaseObject):
    pass


class PokeAPI(AsyncBaseWebAPI):

    def __init__(self):
        """The Poke API is a simple, static API with no authentication so
        object initialisation does not require external arguments"""
        # Call super with the static values of the Poke API
        super().__init__('pokeapi.co', '', '', secure=True)
        # Headers tend to vary from API to API so these would get set after
        # calling super which will have initiallised self.headers as an empty
        # dictionary
        self.headers['Accept'] = 'application/json'

    async def __aenter__(self):
        # Always await super() first
        obj = await super().__aenter__()
        # If you need to do any sign in transactions to create header keys
        # these could be done here
        return obj

    async def get_pokemon(self, pokemon_name):
        """Get data about an individual pokemon"""
        # Path should be the absolute path to the API resource, in this
        # instance the pokemon name makes up part of the path
        path = f"/api/v2/pokemon/{pokemon_name}/"
        # get the data in an Async call
        pokemon_data = await self._transaction('get', path)
        # any further processing you may need to do
        return pokemon_data

    async def _transaction(self, method, path, **kwargs):
        # Any pre-processing here
        r = await super()._transaction(method, path, **kwargs)
        # Post processing here
        # AsyncBaseWebAPI will automatically parse 'application/json'
        # payloads, so just return the result text
        return r


async def async_main():
    # use the api
    async with PokeAPI() as poke_api:
        calls = list()
        for pokemon in ['mew', 'ditto', 'pikachu', 'smoochum']:
            calls.append(poke_api.get_pokemon(pokemon))
        return await asyncio.gather(*calls)


def main():
    loop = asyncio.get_event_loop()
    return loop.run_until_complete(async_main())


if __name__ == '__main__':
    results = main()
    pprint.pprint(results)

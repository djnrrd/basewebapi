from __future__ import annotations
from typing import Union
from basewebapi.asyncbaseweb import AsyncBaseWebAPI
from basewebapi import JSONBaseObject, JSONBaseList
import asyncio


class Pokemon(JSONBaseObject):

    def __init__(self, **kwargs) -> Pokemon:
        """The Pokemon data type includes many lists of other data types.
        Define just the 'abilities' field to create the child
        PokemonAbilities list.
        """
        child_objects = {'abilities': PokemonAbilities}
        super().__init__(child_objects=child_objects, **kwargs)


class PokemonAbilities(JSONBaseList):

    @classmethod
    def from_json(cls, data: list) -> PokemonAbilities:
        """Make this return a list of PokemonAbility objects
        """
        return super().from_json(data, PokemonAbility)


class PokemonAbility(JSONBaseObject):
    """Even if no extra functions are needed, declare the objects anyway.
    """
    pass


class PokeAPI(AsyncBaseWebAPI):

    def __init__(self) -> PokeAPI:
        """The Poke API is a simple, static API with no authentication so
        object initialisation does not require external arguments"""
        # Call super with the static values of the Poke API
        super().__init__('pokeapi.co', '', '', secure=True)
        # Headers tend to vary from API to API so these would get set after
        # calling super which will have initiallised self.headers as an empty
        # dictionary
        self.headers['Accept'] = 'application/json'

    async def __aenter__(self) -> PokeAPI:
        """The parent class is designed to be used with the context manager.
        Override the __aenter__ method if you need to add signin and token
        acquisition methods"""
        # Always await super() first
        obj = await super().__aenter__()
        # If you need to do any sign in transactions these could be done here
        return obj

    async def get_pokemon(self, pokemon_name: str) -> Pokemon:
        """Get data about an individual pokemon

        :param pokemon_name: The name of the pokemon required
        :return: Pokemon object
        """
        # Path should be the absolute path to the API resource, in this
        # instance the pokemon name makes up part of the path
        path = f"/api/v2/pokemon/{pokemon_name}/"
        # get the data in an Async call
        pokemon_data = await self._transaction('get', path)
        # any further processing you may need to do
        # Return the Pokemon object parsed from the JSON object
        return Pokemon.from_json(pokemon_data)

    async def _transaction(self, method: str, path: str, **kwargs) \
            -> Union[dict, list]:
        """Get the result for the HTTP method and URL Path

        :param method: The HTTP method, 'get', 'post', etc.
        :param path: The path to the URL endpoint, not the URL
        :param kwargs: Keyword arguments supported by the aiohttp request method
        :return: The parsed JSON object
        """
        # Any pre-processing here
        r = await super()._transaction(method, path, **kwargs)
        # Post processing here
        # AsyncBaseWebAPI will automatically parse 'application/json'
        # payloads, so just return the result text
        return r


async def async_main() -> list:
    """Get 4 Pokemon objects and return them in a list using asyncio to run
    concurrently

    :return: List of Pokemon objects
    """
    # Use the api with the context manager
    async with PokeAPI() as poke_api:
        calls = list()
        for pokemon in ['mew', 'ditto', 'pikachu', 'smoochum']:
            # Add the Coroutines to a list
            calls.append(poke_api.get_pokemon(pokemon))
        # run the Coroutines together and return the results
        return await asyncio.gather(*calls)


def main() -> list:
    """Get 4 Pokemon objects and return them in a list

    :return: List of Pokemon objects
    """
    # Get the event loop, then run the Async functions in the loop
    loop = asyncio.get_event_loop()
    return loop.run_until_complete(async_main())


if __name__ == '__main__':
    results = main()
    print([x for x in results])
    print([type(x) for x in results])

basewebapi
++++++++++

Introduction
############

A python module defining a basic object orientated framework that can be
inherited by custom modules that interact with HTTP based RESTful APIs.
These provide boilerplate interfaces to the requests and aiohttp modules, as
well as boilerplate for handling returned JSON objects into custom classes

Installation
############

Requirements
************

This module requires Python 3.6 or above and pip.

Installing
**********

From PyPi
---------

::

   pip install basewebapi

From Source
-----------

Clone the git repository from `<https://github.com/djnrrd/basewebapi>`_

::

   git clone https://github.com/djnrrd/basewebapi

Then use pip to install from the downloaded folder

::

   pip install .

Usage
#####

API Class
*********

Each custom API would be defined as a new class, that inherits from the
BaseWebAPI class.  Then each endpoint the API provides can be mapped to a
method of the API class.

::

   class PokeAPI(BaseWebAPI):

   def __init__(self):
       super().__init__('pokeapi.co', '', '', secure=True)
       self.headers['Accept'] = 'application/json'

   def get_pokemon(self, pokemon_name):
       path = f"/api/v2/pokemon/{pokemon_name}/"
       pokemon_data = self._transaction('get', path)
       return Pokemon.from_json(pokemon_data)

   def _transaction(self, method, path, **kwargs):
       r = super()._transaction(method, path, **kwargs)
       return r.json()

The __init__ method can be overridden for customisations. In the PokeAPI
example we see that we take no arguments, since they can be statically
defined for the call to super(), and we add appropriate headers that would be
sent with any request.  If the Web API is going to return any valid status
codes that are not 200, the status_codes property should be updated with a
valid list here.

We define a new method to get the Pokemon endpoint. Defining the absolute
path, without the hostname, to the endpoint. This path is passed with the
HTTP method to the _transaction method.

The _transaction method can be overridden for customisations.  In the
PokePI example we return the JSON object created by the requests json()
method. This may be where you put code to handle pagination or any other pre
or post processing

JSON Object Classes
*******************

Since many APIs use JSON to define their returned data custom classes can be
made, inheriting from the JSONBaseObject and JSONBaseList classes. Custom
methods can then be written to interact with the data.

::

   class PokeBaseObject(JSONBaseObject):
       pass

   class PokeBaseList(JSONBaseList):
       pass

   class Pokemon(PokeBaseObject):

       def __init__(self, **kwargs):
           child_objects = {'abilities': PokemonAbilities}
           super().__init__(child_objects=child_objects, **kwargs)

   class PokemonAbilities(PokeBaseList):

       @classmethod
       def from_json(cls, data):
           return super().from_json(data, PokemonAbility)

   class PokemonAbility(PokeBaseObject):
       pass

Creating a base class for your API's returned objects provides you with
somewhere to write methods that can be applied to all of your return objects.

The Pokemon API defines a child object for the 'abilities' key,
a list of PokemonAbilities.  This list has been defined as a class, so the
key and the class are sent to super() with the child_objects argument.

JSON lists usually provide uniform objects in a list, so the from_json class
method of the JSONBaseList takes that class as a further argument.

If you wish to enforce creation of custom objects, always use the from_json()
class method of the custom objects to create them

Async API Object Class
**********************

An async based version of BaseWebAPI is provided in basewebapi
.asyncbasewebapi.AsyncBaseWebAPI

This is based around the aiohttp package instead of requests and should be
used with the async context manager.

::

   async def async_main() -> list:
           async with PokeAPI() as poke_api:
           calls = list()
           for pokemon in ['mew', 'ditto', 'pikachu', 'smoochum']:
                   calls.append(poke_api.get_pokemon(pokemon))
           return await asyncio.gather(*calls)


   def main() -> list:
       loop = asyncio.get_event_loop()
       return loop.run_until_complete(async_main())

Although it may also be used by calling the open() and close() methods.

::

   poke_api = PokeAPI()
   poke_api.open()
   result = list()
       for pokemon in ['mew', 'ditto', 'pikachu', 'smoochum']:
           result = poke_api.get_pokemon(pokemon)
   poke_api.close()

The open() and close() methods can be overridden if custom sign in and sign
out endpoints need to be called. Always call super() first when overriding
the open() method to set up the aiohttp session, and call super() last when
overriding the close() method to tear down the aiohttp session cleanly.

::

   async def get_pokemon(self, pokemon_name: str) -> Pokemon:
       path = f"/api/v2/pokemon/{pokemon_name}/"
       pokemon_data = await self._transaction('get', path)
       return Pokemon.from_json(pokemon_data)

Custom methods should be created with the async keyword and awaited in the
calling scripts, and the _transaction method must always be awaited.

Examples
********

Full commented examples of the PokeAPI can be found in the examples directory.
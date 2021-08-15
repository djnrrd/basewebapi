from basewebapi import BaseWebAPI


class PokeAPI(BaseWebAPI):

    def __init__(self):
        """The Poke API is a simple, static API with no authentication so
        object initialisation does not require external arguments"""
        # Call super with the static values of the Poke API
        super().__init__('pokeapi.co', '', '', secure=True)
        # Headers tend to vary from API to API so these would get set after
        # calling super which will have initiallised self.headers as an empty
        # dictionary
        self.headers['Accept'] = 'application/json'

    def get_pokemon(self, pokemon_name):
        """Get data about an individual pokemon"""
        path = f"/api/v2/pokemon/{pokemon_name}/"
        pokemon_data = self._transaction('get', path)
        # any further processing you may need to do
        return pokemon_data

    def _transaction(self, method, path, **kwargs):
        # Any pre-processing here
        r = super()._transaction(method, path, **kwargs)
        # We know that this is a JSON based API so we can use the requests
        # json method of the Response object
        return r.json()

# Python 3-8-5 GCC 9.3.0

import requests as req 
from multiprocessing import cpu_count
import time
import math 
import concurrent.futures
import json
import re

API_POKEMON = 'https://pokeapi.co/api/v2/pokemon/' # list of pokemons
API_POKEMON_SPECIES = 'https://pokeapi.co/api/v2/pokemon-species/' # list of pokemons and specie detail
API_POKEMON_TYPE = 'https://pokeapi.co/api/v2/type/' # types of pokemons
processes = cpu_count()

def call_api(url):
    response = req.get(url) # Make a request

    if response.status_code == 404:
        return 'Not Found'
    if response.status_code != 200:
        raise Exception('API response: {}'.format(response.status_code))
    return response


#------------------------ PREGUNTA 1 ---------------------------

def pregunta_1():

    response = call_api(API_POKEMON) 
    total_pokemons = response.json()['count'] # Get number of pokemons
    records_per_process = math.ceil(total_pokemons/processes) # get number of records per process

    with concurrent.futures.ProcessPoolExecutor() as executor:
        answer = 0
        results = [executor.submit(get_pokemons,i,total_pokemons,records_per_process) for i in range(processes)] # get the pokemons with 4 process at the same time

        for f in concurrent.futures.as_completed(results):
            answer =  answer + f.result() # SUm the result of the 4 process and return the result
    return answer

def get_pokemons(process=1,total_pokemons=None,records_per_process=20):
    # Iterate Over the api endpoint for every process
    response = call_api(API_POKEMON+'?offset={offset}&limit={limit}'.format(offset=str(process*records_per_process),limit=str(records_per_process)))
    total_pokemons_names = [link['name'] for link in response.json()['results']]
    return find_char_on_string(total_pokemons_names)

def find_char_on_string(total_pokemons_names):

    rpta = 0
    for name in total_pokemons_names:
        if name.count("at") and name.count('a') == 2: # fastsearch - mix between boyer- moore and horspool algorithm
            rpta+=1 
    total_pokemons_names.clear()
    return rpta

#------------------------ PREGUNTA 2 ---------------------------

def pregunta_2(pokemon_name):

    pokemon_species_per_egg_group  = set() # Create a set to avoid duplicates
    response = call_api(API_POKEMON_SPECIES+'{}'.format(pokemon_name))
    egg_groups = [link['url'] for link in response.json()['egg_groups']]
    with concurrent.futures.ProcessPoolExecutor() as executor:
        response = executor.map(call_api,egg_groups)  # Each process consumes an egg group endpoint
        
        for egg_group in response:  
            pokemon_species_per_egg_group = pokemon_species_per_egg_group.union([link['name'] for link in egg_group.json()['pokemon_species']]) # Union between pokemons in different egg group
    return len(pokemon_species_per_egg_group)

#------------------------ PREGUNTA 3 ---------------------------

def pregunta_3(pokemon_type):

     
    response = call_api(API_POKEMON_TYPE+'{}'.format(pokemon_type))
    pokemons_list = json.loads(response.text)['pokemon']
    # Get the pokemon id with the endpoint and just conserve the ones <= to 150
    pokemons_list = [pokemons_list[i]['pokemon']['url'] for i in range(len(pokemons_list)) if int(re.findall(r"\d+", pokemons_list[i]['pokemon']['url'])[1]) <= 150]
    records_per_process = int(len(pokemons_list)/processes)

    with concurrent.futures.ProcessPoolExecutor() as executor: # Divides the api request in 4 process
        weight = []
        results = [executor.submit(get_weights,i,pokemons_list,records_per_process) for i in range(4)]

        for f in concurrent.futures.as_completed(results):
            weight += f.result() # concatenate the weights in a list
    
    return [max(weight),min(weight)] # return de max and min value
           
    
def get_weights(process,pokemons_list,request_per_process):

    weight = []
    for pokemon in pokemons_list[process*request_per_process:request_per_process*(process+1)]: # Get different weights for each process
        response = call_api(pokemon)
        weight.append(json.loads(response.text)['weight'])
    return weight

def main():
    
    print(pregunta_1())
    print(pregunta_2('raichu'))
    print(pregunta_3('fighting'))


if __name__ == "__main__":
    main()

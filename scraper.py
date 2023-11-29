import requests, json, time

start_time = time.time()

BASE_URL = 'https://pokeapi.co/api/v2/'

pokedex_dict = {}
gamelist = ['ruby', 'sapphire', 'emerald', 'firered', 'leafgreen']

def remove_duplicates(appearences):
        return list(dict.fromkeys(appearences))

# From a Pokemon we need:
# - Name DONE
#   - Game appearences DONE
#   - Encounter locations
#   - Encounter chances
#   - Encounter methods
#   - Encounter levels

def get_pokemon_data(pokemon_id):
    result = []
    result_set = {}
    
    request_pokemon = requests.get(BASE_URL + f'pokemon/{pokemon_id}').json()
    request_encounters = requests.get(BASE_URL + f'pokemon/{pokemon_id}/encounters').json()

    result.append(request_pokemon['name'])
    result_set = parse_encounters(request_encounters)


    result.append(result_set)
    return result

def parse_encounters(encounters):
    result = {}

    games = []
    locations = {}
    
    # Game sets
    ruby = []
    sapphire = []
    emerald = []
    fr = []
    lg = []

    for encounter in encounters:
        for i in range(len(encounter['version_details'])):
            version_details = encounter['version_details'][i]
            if version_details['version']['name'] in gamelist:
                # Add game
                game_name = version_details['version']['name']
                games.append(game_name)

                # Add location
                location_name = encounter['location_area']['name']

                if version_details['version']['name']=='ruby':
                    ruby.append(location_name)

                elif version_details['version']['name']=='sapphire':
                    sapphire.append(location_name)

                elif version_details['version']['name']=='emerald':
                    emerald.append(location_name)

                elif version_details['version']['name']=='firered':
                    fr.append(location_name)

                elif version_details['version']['name']=='leafgreen':
                    lg.append(location_name)

    # Add locations
    if len(ruby) > 0:
        locations['ruby'] = ruby

    if len(sapphire) > 0:
        locations['sapphire'] = sapphire

    if len(emerald) > 0:
        locations['emerald'] = emerald

    if len(fr) > 0:
        locations['firered'] = fr

    if len(lg) > 0:
        locations['leafgreen'] = lg

    # Compose result
    result['appearences'] = remove_duplicates(games)
    result['locations'] = locations

    return result

### MAIN ###

def compose_test():
    test_pokedex = {}

    for i in range(60, 70):
        pokemon_data = get_pokemon_data(i)
        test_pokedex[pokemon_data[0]] = pokemon_data[1]

    with open('output/test.json', 'w') as outfile:
        json.dump(test_pokedex, outfile)

    print(test_pokedex)

def compose_pokedex():
    pokedex = {}

    for i in range(1, 387):
        pokemon_data = get_pokemon_data(i)
        pokedex[pokemon_data[0]] = pokemon_data[1]

    with open('output/pokedex.json', 'w') as outfile:
        json.dump(pokedex, outfile)

# compose_test()
compose_pokedex()

print("--- %s seconds ---" % (time.time() - start_time))
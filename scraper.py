import requests, json, time, sqlite3

from sqlite3 import Error

start_time = time.time()

BASE_URL = 'https://pokeapi.co/api/v2/'
OFFLINE_MODE = True

pokedex_dict = {}
gamelist = ['ruby', 'sapphire', 'emerald', 'firered', 'leafgreen']

### DB ###

def create_connection(db_file):
    """ create a database connection to a SQLite database """
    conn = None

    try:
        conn = sqlite3.connect(db_file)
        print(sqlite3.version)
    except Error as e:
        print(e)

    print(f'Connection to {db_file} successful')
    return conn

def setup_db(conn):
    c = conn.cursor()

    # Drop tables
    c.execute('''DROP TABLE IF EXISTS pokemon''')
    c.execute('''DROP TABLE IF EXISTS encounters''')
    c.execute('''DROP TABLE IF EXISTS locations''')
    c.execute('''DROP TABLE IF EXISTS games''')

    # Create tables
    c.execute('''CREATE TABLE pokemon
                (id integer primary key unique not null,
                name text not null);''')
    
    c.execute('''CREATE TABLE games
                (name text primary key unique not null);''')
    
    c.execute('''CREATE TABLE locations
                (name text primary key unique not null);''')
    
    c.execute('''CREATE TABLE encounters
                (id integer primary key unique not null,
                pokemon_id integer not null,
                game_id integer not null,
                location_id integer not null,
                chance integer not null,
                max_level integer not null,
                min_level integer not null,
                method text not null,
                condition text,
                FOREIGN KEY (pokemon_id) REFERENCES pokemon(id),
                FOREIGN KEY (game_id) REFERENCES games(id),
                FOREIGN KEY (location_id) REFERENCES locations(id));''')
    

    # Save (commit) the changes
    conn.commit()

### Functions ###

# From a Pokemon we need:
# - Name DONE
#   - Game appearences DONE
#   - Encounter locations DONE
#   - Encounter chances
#   - Encounter methods
#   - Encounter levels

def get_requests(pokemon_id):
    request_pokemon = requests.get(BASE_URL + f'pokemon/{pokemon_id}').json()
    request_encounters = requests.get(BASE_URL + f'pokemon/{pokemon_id}/encounters').json()

    with open(f'requests/pokemon/{pokemon_id}.json', 'w') as outfile:
        json.dump(request_pokemon, outfile)

    with open(f'requests/encounters/{pokemon_id}.json', 'w') as outfile:
        json.dump(request_encounters, outfile)

    print(f'Pokemon {request_pokemon["name"]} done at {time.time() - start_time} seconds')
    return

def get_pokemon_data(pokemon_id):
    result = []
    result_set = {}
    
    if OFFLINE_MODE:
        with open(f'requests/pokemon/{pokemon_id}.json') as json_file:
            request_pokemon = json.load(json_file)

        with open(f'requests/encounters/{pokemon_id}.json') as json_file:
            request_encounters = json.load(json_file)

    else:
        request_pokemon = requests.get(BASE_URL + f'pokemon/{pokemon_id}').json()
        request_encounters = requests.get(BASE_URL + f'pokemon/{pokemon_id}/encounters').json()

    result.append(request_pokemon['name'])
    result_set = parse_encounters(request_encounters)

    print(f'Pokemon {request_pokemon["name"]} done at {time.time() - start_time} seconds')
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

### AUX ###

def remove_duplicates(appearences):
        return list(dict.fromkeys(appearences))

### MAIN ###

def compose_offline_api():
    for i in range(1, 387):
        get_requests(i)


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


if __name__ == '__main__':
    conn = create_connection('db/sed.db')
    setup_db(conn)

    conn.close()

    # compose_offline_api()
    # compose_test()
    # compose_pokedex()

    print("--- %s seconds ---" % (time.time() - start_time))
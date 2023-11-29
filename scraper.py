import requests, json, time, sqlite3

from sqlite3 import Error

### Global Variables ###

start_time = time.time()

BASE_URL = 'https://pokeapi.co/api/v2/'
OFFLINE_MODE = True

pokedex_dict = {}
gamelist = ['ruby', 'sapphire', 'emerald', 'firered', 'leafgreen']

### DB Functions ###

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
    c.execute('''DROP TABLE IF EXISTS pokemon_games''')
    c.execute('''DROP TABLE IF EXISTS games_locations''')

    # Create tables
    c.execute('''CREATE TABLE pokemon
                (id integer primary key unique not null,
                name text not null);''')
    
    c.execute('''CREATE TABLE games
                (name text primary key unique not null);''')
    
    c.execute('''CREATE TABLE locations
                (name text primary key unique not null);''')
    
    c.execute('''CREATE TABLE encounters
                (pokemon_id integer not null,
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
    
    # Many to many tables
    c.execute('''CREATE TABLE pokemon_games
                (pokemon_id integer not null,
                game_id integer not null,
                FOREIGN KEY (pokemon_id) REFERENCES pokemon(id),
                FOREIGN KEY (game_id) REFERENCES games(id));''')
    
    c.execute('''CREATE TABLE games_locations
                (game_id integer not null,
                location_id integer not null,
                FOREIGN KEY (game_id) REFERENCES games(id),
                FOREIGN KEY (location_id) REFERENCES locations(id));''')
    
    
    for game in gamelist:
        c.execute('''INSERT OR IGNORE INTO games (name)
                    VALUES (?);''', (game,))

    # Save (commit) the changes
    conn.commit()

### API Functions ###

# Get all the necessary requests from the API
# Flags: [pokemon, encounters]
def get_requests(pokemon_id, flags = [True, True]):
    if flags[0]:
        request_pokemon = requests.get(BASE_URL + f'pokemon/{pokemon_id}').json()
        with open(f'requests/pokemon/{pokemon_id}.json', 'w') as outfile:
            json.dump(request_pokemon, outfile)

    if flags[1]:
        request_encounters = requests.get(BASE_URL + f'pokemon/{pokemon_id}/encounters').json()
        with open(f'requests/encounters/{pokemon_id}.json', 'w') as outfile:
            json.dump(request_encounters, outfile)

    print(f'Pokemon {request_pokemon["name"]} done at {time.time() - start_time} seconds')
    return

### JSON Functions ###

# From a Pokemon we need:
# - Name DONE
#   - Game appearences DONE
#   - Encounter locations DONE
#   - Encounter chances
#   - Encounter methods
#   - Encounter levels

def get_pokemon_data_json(pokemon_id):
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
    result_set = parse_encounters_json(request_encounters)

    result.append(result_set)

    print(f'Pokemon {request_pokemon["name"]} done at {time.time() - start_time} seconds')

    return result

def parse_encounters_json(encounters):
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

### SQLite Functions ###

def insert_pokemon(conn, pokemon_id):
    c = conn.cursor()

    pokemon = [pokemon_id, '']

    if OFFLINE_MODE:
        with open(f'requests/pokemon/{pokemon_id}.json') as json_file:
            request_pokemon = json.load(json_file)

    else:
        request_pokemon = requests.get(BASE_URL + f'pokemon/{pokemon_id}').json()

    pokemon[1] = request_pokemon['name']

    c.execute('''INSERT INTO pokemon (id, name)
                VALUES (?, ?)''', pokemon)

    conn.commit()

    print(f'Pokemon {pokemon[1]} inserted at {time.time() - start_time} seconds')
    return

def insert_encounters(conn, pokemon_id):
    c = conn.cursor()

    if OFFLINE_MODE:
        with open(f'requests/encounters/{pokemon_id}.json') as json_file:
            request_encounters = json.load(json_file)

    else:
        request_encounters = requests.get(BASE_URL + f'pokemon/{pokemon_id}/encounters').json()

    for encounter in request_encounters:
        for i in range(len(encounter['version_details'])):
            version_details = encounter['version_details'][i]
            if version_details['version']['name'] in gamelist:
                # Add location
                location_name = encounter['location_area']['name']
                c.execute('''INSERT OR IGNORE INTO locations (name)
                            VALUES (?)''', (location_name,))
                
                # Add game
                game_name = version_details['version']['name']

                # Add games_locations
                c.execute('''INSERT OR IGNORE INTO games_locations (game_id, location_id)
                            VALUES (?,?)''', (game_name, location_name))
                
                # Add pokemon_games
                c.execute('''INSERT OR IGNORE INTO pokemon_games (pokemon_id, game_id)
                            VALUES (?, ?)''', (pokemon_id, game_name))
                
                # Add encounter
                encounter_data = [pokemon_id, game_name, location_name, version_details['encounter_details'][0]['chance'], 
                                version_details['encounter_details'][0]['max_level'], version_details['encounter_details'][0]['min_level'], 
                                version_details['encounter_details'][0]['method']['name']]

                if len(version_details['encounter_details'][0]['condition_values']) > 0:
                    encounter_data.append(version_details['encounter_details'][0]['condition_values'][0]['name'])

                else:
                    encounter_data.append('')
                    
                c.execute('''INSERT INTO encounters (pokemon_id, game_id, location_id, chance, max_level, min_level, method, condition)
                            VALUES (?, ?, ?, ?, ?, ?, ?, ?)''', encounter_data)

    conn.commit()

    print(f'Locations inserted at {time.time() - start_time} seconds')
    return

### Auxiliary Funtions ###

def remove_duplicates(appearences):
        return list(dict.fromkeys(appearences))

### Execution Functions ###

def compose_offline_api():
    for i in range(1, 387):
        get_requests(i)

def compose_test():
    test_pokedex = {}

    for i in range(60, 70):
        pokemon_data = get_pokemon_data_json(i)
        test_pokedex[pokemon_data[0]] = pokemon_data[1]

    with open('output/test.json', 'w') as outfile:
        json.dump(test_pokedex, outfile)

    print(test_pokedex)

def compose_pokedex():
    pokedex = {}

    for i in range(1, 387):
        pokemon_data = get_pokemon_data_json(i)
        pokedex[pokemon_data[0]] = pokemon_data[1]

    with open('output/pokedex.json', 'w') as outfile:
        json.dump(pokedex, outfile)

### Main ###

if __name__ == '__main__':
    conn = create_connection('db/sed.db')
    setup_db(conn)

    for i in range(1, 387):
        insert_pokemon(conn, i)
        insert_encounters(conn, i)

    conn.close()

    # compose_offline_api()
    # compose_test()
    # compose_pokedex()

    print("--- %s seconds ---" % (time.time() - start_time))
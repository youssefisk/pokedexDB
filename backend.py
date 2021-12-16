"""Code for parsing the backend of the Pokedex program
Starter code by David Szeto. Implementation by the CSCA20 student.
"""


import sqlite3

import const
SEP = const.SEP


def get_con_cur(db_filename):
    """Returns an open connection and cursor associated with the sqlite
    database associated with db_filename.

    Args:
        db_filename: (str) the filename of the db to which to connect

    Returns: a tuple of:
        -an open connection to the sqlite database
        -an open cursor associated with the connection
    """
    con = sqlite3.connect(db_filename)
    cur = con.cursor()
    return (con, cur)


def close_con_cur(con, cur):
    """Commits changes and closes the given cursor and connection to a sqlite
    database.

    Args:
        con: an open sqlite3 connection to a database
        cur: a cursor associated with con

    Returns:
        None
    """
    cur.close()
    con.commit()
    con.close()


def table_exists(cur):
    """Returns whether the pokemon table already exists in the database and
    whether it is non-empty

    Args:
        cur: an open sqlite3 cursor created from a connection to the pokemon db
    """
    query = 'SELECT * FROM pokemon'
    try:
        cur.execute(query)
    except sqlite3.OperationalError:
        return False
    return cur.fetchone() is not None


def create_table(csv_filename, con, cur):
    """(Re-)creates the pokemon table in the database

    In the SQLite cursor cur, drops the pokemon table if it already exists, and
    re-creates it. Fills it with the information contained in the CSV file
    denoted by csv_filename. Afterwards, commits the changes through the given
    connection con.

    Implicitly converts all strs in the loaded data to lower-case before
    insertion into the database.

    Args:
        csv_filename: (str) the filename of the CSV file containing the pokemon
        information
        con: an open connection to the sqlite database
        cur: an open cursor associated with the connection

    Returns:
        None
    """

    cur.execute('DROP TABLE IF EXISTS pokemon')

    cur.execute('CREATE TABLE pokemon(name TEXT, species_id INTEGER, '
                'height REAL, '
                'weight REAL, type_1 TEXT, type_2 TEXT, url_image TEXT, '
                'generation_id INTEGER, evolves_from_species_id TEXT)')

    query = ('INSERT into pokemon VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)')
    with open(csv_filename) as f:
        indexes = parse_header(f)
        for line in f:
            line = line.strip().split(SEP)

            name = line[indexes['pokemon']]
            species_id = int(line[indexes['species_id']])
            height = float(line[indexes['height']])
            weight = float(line[indexes['weight']])
            type_1 = line[indexes['type_1']]
            type_2 = line[indexes['type_2']]
            url_image = line[indexes['url_image']]
            generation_id = int(line[indexes['generation_id']])
            evolves_from_species_id = line[indexes['evolves_from_species_id']]

            cur.execute(query, (name.lower(), species_id, height, weight,
                                type_1.lower(), type_2.lower(),
                                url_image.lower(), generation_id,
                                evolves_from_species_id.lower()))

    con.commit()


def get_pokemon_names(cur):
    """Returns a list of pokemon names in the database (as strs) sorted in
    alphabetical order

    Args:
        cur: an open sqlite3 cursor created from a connection to the pokemon db
    """
    query = ('SELECT name FROM pokemon ORDER BY name')
    cur.execute(query)
    data = cur.fetchall()
    result = []
    for element in data:
        result.append(element[0])
    return result


def get_stats_by_name(name, cur):
    """Returns the stats of the pokemon with the given name as stored in the
    database.

    Args:
        name: the pokemon's name
        cur: an open sqlite3 cursor created from a connection to the pokemon db

    Returns: a tuple of
        -the pokemon's name (str)
        -the pokemon's species id (int)
        -the pokemon's height (float)
        -the pokemon's weight (float)
        -the pokemon's type 1 (str)
        -the pokemon's type 2 (str)
        -the pokemon's url image (str)
        -the pokemon's generation (int)
        -the species id from which the pokemon evolves (str)
    """
    query = ('SELECT name, species_id, height, weight, type_1, type_2, '
             'url_image, generation_id, evolves_from_species_id FROM pokemon '
             'WHERE name = ?')
    cur.execute(query, (name,))
    data = cur.fetchall()
    x = data[0]
    return x


def get_pokemon_ids(cur):
    """Returns a list of pokemon (species) ids (as ints) sorted in increasing
    order as stored in the database.

    Args:
        cur: an open sqlite3 cursor created from a connection to a pokemon db
    """
    query = ('SELECT species_id FROM pokemon ORDER BY species_id')
    cur.execute(query)
    data = cur.fetchall()
    result = [element[0] for element in data]
    return result


def get_stats_by_id(species_id, cur):
    """Returns the stats of the pokemon with the given species id as stored in
    the database.

    Args:
        species_id: the pokemon's species id (int)
        cur: an open sqlite3 cursor created from a connection to the pokemon db

    Returns: a tuple of
        -the pokemon's name (str)
        -the pokemon's species id (int)
        -the pokemon's height (float)
        -the pokemon's weight (float)
        -the pokemon's type 1 (str)
        -the pokemon's type 2 (str)
        -the pokemon's url image (str)
        -the pokemon's generation (int)
        -the species id from which the pokemon evolves (str)
    """
    query = ('SELECT name, species_id, height, weight, type_1, type_2, '
             'url_image, generation_id, evolves_from_species_id FROM pokemon '
             'WHERE species_id = ?')
    cur.execute(query, (species_id,))
    data = cur.fetchall()
    return data[0]


def unique_and_sort(ell):
    """Returns a copy of ell which contains all unique elements of ell sorted
    in ascending order.

    Args:
        ell: a list that can be sorted
    """

    return sorted(set(ell))


def get_pokemon_types(cur):
    """Returns a list of distinct pokemon types (strs) sorted in alphabetical
    order.

    Both type_1 and type_2 are treated as types.

    Args:
        cur: an open sqlite3 cursor created from a connection to the pokemon db
    """
    all_types = []
    query = ('SELECT type_1 FROM pokemon')
    cur.execute(query)
    data = cur.fetchall()
    for element in data:
        all_types.append(element[0])

    query_2 = ('SELECT type_2 FROM pokemon')
    cur.execute(query_2)
    data = cur.fetchall()
    for element in data:
        all_types.append(element[0])
    sorted_unique_types = unique_and_sort(all_types)

    return sorted_unique_types


def get_pokemon_by_type(pokemon_type, cur):
    """Returns a list of pokemon names (strs) of all pokemon of the given type,
    where the list is sorted in alphabetical order.

    Args:
        pokemon_type: the pokemon type (which may be a type_1 or type_2) (str)
        cur: an open sqlite3 cursor created from a connection to the pokemon db
    """
    query = ('SELECT name FROM pokemon WHERE type_1 = ?')
    cur.execute(query, (pokemon_type,))
    data_1 = cur.fetchall()
    data_1 = [element[0] for element in data_1]

    query_2 = ('SELECT name FROM pokemon WHERE type_2 = ?')
    cur.execute(query, (pokemon_type,))
    data_2 = cur.fetchall()
    data_2 = [element[0] for element in data_2]

    all_names = data_1 + data_2
    all_names = unique_and_sort(all_names)

    return all_names


def parse_header(f):
    """Parses the header and builds a dict mapping column name to index

    Args:
        f: a freshly opened file in the format of pokemon.csv

    Returns:
        a dict where:
            -each key is one of:
                'pokemon', 'species_id', 'height', 'weight', 'type_1',
                'type_2', 'url_image', 'generation_id',
                'evolves_from_species_id'
            -each value is the index of the corresponding key in the CSV file
                starting from column 0.
                eg. If 'pokemon' is in the second column, then its index will
                be 1. If 'species_id' is the third column, then its index will
                be 2.
    """
    columns = ['pokemon', 'species_id', 'height', 'weight', 'type_1', 'type_2',
               'url_image', 'generation_id', 'evolves_from_species_id']
    result = {}
    headers = f.readline()
    headers = headers.strip()
    headers = headers.split(SEP)
    for element in headers:
        result[element] = headers.index(element)
    return result

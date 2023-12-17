"""
Port to pokebase API first. Then fix the existing issues.

Accept:
    Name or pokedex ID

    - maybe if the spelling is close enough then it fuzzes to the correct choice?

TODO the output should be some sort of templated output. With
cool things like bash coloring and italicizing and whatnot.

verbose template and shortened template for like gameboy color?

"""

import pokebase as pb
import argparse

bc = {
    'NC': '\033[0m',

    'C0': '\033[0;30m',
    'C1': '\033[0;31m',
    'C2': '\033[0;32m',
    'C3': '\033[0;33m',
    'C4': '\033[0;34m',
    'C5': '\033[0;35m',
    'C6': '\033[0;36m',
    'C7': '\033[0;37m',

    'BC0': '\033[1;30m',
    'BC1': '\033[1;31m',
    'BC2': '\033[1;32m',
    'BC3': '\033[1;33m',
    'BC4': '\033[1;34m',
    'BC5': '\033[1;35m',
    'BC6': '\033[1;36m',
    'BC7': '\033[1;37m',

    'UC0': '\033[4;30m',
    'UC1': '\033[4;31m',
    'UC2': '\033[4;32m',
    'UC3': '\033[4;33m',
    'UC4': '\033[4;34m',
    'UC5': '\033[4;35m',
    'UC6': '\033[4;36m',
    'UC7': '\033[4;37m'
}

def main():
    parser = argparse.ArgumentParser(
        prog='PokeFetch',
        description='Displays cool pokemon sprites/stats in terminal.',
        epilog='Have fun.'
    )

    # accepts either pokedex number (int) or name (str)
    parser.add_argument('pokemon', help='Select a pokemon by name or pokedex ID.')

    args = parser.parse_args()
    
    handle_pokemon(args.pokemon)

def handle_pokemon(p):

    # lookup the pokemon    
    poke = lookup_pokemon(p)
    poke_extra = lookup_pokemon_species(p)


    with open('template.txt', 'r') as f:
        output = f.read()
    
    print(poke.stats)

    output = output.format_map({
        'name':         poke.name.title(),
        'ID':           poke.id_, 
        'gender_info':  format_gender(poke_extra.gender_rate),
        'abilities':    format_abilities(poke.abilities),
    } | bc | stats_dict(poke))

    print(output)

def lookup_pokemon(p):
    if p.isdigit():
        return pb.pokemon(int(p))
    else:
        return pb.pokemon(p)
    
def lookup_pokemon_species(p):
    # extra stats such as gender info are found in here
    if p.isdigit():
        return pb.pokemon_species(int(p))
    else:
        return pb.pokemon_species(p)

def format_gender(e):
    # takes the gender rate for female (in 8ths)
    # and returns the formatted line for gender info.
    # A value of -1 means genderless
    gender_info = ''
    if e == -1:
        gender_info = 'genderless'
    else:
        # TODO male/female symbols.
        f_pct = round(100*(e/8.0))
        m_pct = 100-f_pct
        gender_info = f'F: {f_pct}% M: {m_pct}%'

    return gender_info

def format_abilities(a):
    result = ''
    for ability in a:
        result += f'\t- {ability.ability.name}'

        if ability.is_hidden:
            result += ' [HIDDEN]\n'
        else:
            result += '\n'
    return result

def stats_dict(poke):
    # creates a dict of the stats for formatting the template
    res = {}
    for stat in poke.stats:
        res[stat.stat.name] = stat.base_stat
    
    return res

# # Print all moves of the type named here.
# TYPE = 'normal'

# # Good method.
# # Get API data associated with the type we want.
# type_moves = pb.type_(TYPE).moves

# # Iterate & print.
# for move in type_moves:
#     print(move.name)

# POKEMON = 'ditto'

# poke = pb.pokemon(POKEMON)

# for ability in poke.abilities:
#     print(ability.is_hidden)
#     print(ability.ability.name)

main()
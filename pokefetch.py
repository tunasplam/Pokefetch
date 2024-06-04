"""
TODO set up fuzzy pokemon input
https://github.com/seatgeek/thefuzz
- if more than one option allow the user to pick
- this could be great for multi-form pokemon such as deoxys

- verbose template and shortened template for like gameboy color?
- yes, also having template.txt be something in a conf that can be edited
    means that users can customize their prompts.

TODO theres a nasty overhead if you are calling a pokemon for the first
time. There is, however, an API cache. The total amount of data that
we can call on seems to be pretty limited so maybe just pull everything
on install?

TODO a preferences file that lets you limit pokemon generations?

TODO generate output for every possible combination to make sure
theres no strange edge cases. save as an automated test maybe?

TODO move this into bin and see how the path references work
and whatnot

TODO double check that ID works. maybe run iterating through all of those
to see if they all work too..

TODO nidoran and meowstic female sprites likely oversaving the male ones
bc of the way we set their gender to genderless
"""
import argparse
from enum import Enum
import os.path
from os import system
import pokebase as pb
import requests
from re import sub
from sys import exit


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

# [Insert "Not making any political/existential/philosophic statement!"
# disclaimer here]
class Gender(Enum):
    MALE = 'Male'
    FEMALE = 'Female'
    GENDERLESS = 'Genderless'

def main():
    # parses command line arguements
    parser = argparse.ArgumentParser(
        prog='PokeFetch',
        description='Displays cool pokemon sprites/stats in terminal.',
        epilog='Have fun.'
    )

    # accepts either pokedex number (int) or name (str)
    parser.add_argument(
        'pokemon',
        help='Select a pokemon by name or pokedex ID.')
    parser.add_argument(
        '--female',
        action=argparse.BooleanOptionalAction,
        help='If the selected pokemon is gendered then display the female sprite.'
    )
    parser.add_argument(
        '--shiny',
        action=argparse.BooleanOptionalAction,
        help='Display the shiny version of the pokemon sprite.'
    )

    args = parser.parse_args()
    handle_pokemon(args.pokemon.lower(), args.female, args.shiny)

def handle_pokemon(p: str, female: bool, shiny: bool):

    # make the names safe for searching using the api
    p = clean_name(p, female)
    
    # lookup the pokemon
    poke = lookup_pokemon(p)
    poke_extra = lookup_pokemon_species(p)

    # if this does not work then the searched pokemon is not valid.
    try:
        if poke.sprites.front_female: pass
    except AttributeError:
        print("Pokemon not found! Please enter valid pokemon.")
        exit(1)

    # verify and set selected gender.
    # nidoran messes things up because nidoran-f will have its sprites
    # saved under default instead of female
    # manually set genders for nidoran.
    if poke == 'nidoran-f' or poke == 'nidoran-m' or \
        not poke.sprites.front_female:
        gender = Gender['GENDERLESS']
    elif female:
        gender = Gender['FEMALE']
    else:
        gender = Gender['MALE']

    with open('template.txt', 'r') as f:
        output = f.read()
    
    output = output.format_map(
        {
            'name':         poke.name.title(),
            'ID':           poke.id_, 
            'gender_info':  format_gender(poke_extra.gender_rate),
            'abilities':    format_abilities(poke.abilities),
        } | bc | stats_dict(poke)
    )

    print('\n'*100)

    image_filepath = grab_sprite(poke, gender, shiny)
    # TODO at some point handle different image viewers.
    system(f'kitten icat --align left --scale-up --place 25x25@0x3 {image_filepath}')

    print()
    print(f"\t\t\t{bc['BC3']}{poke.name.title()}{bc['NC']}")
    print()
    print_output(output, 30)

def lookup_pokemon(p: str):
    if p.isdigit():
        return pb.pokemon(int(p))
    else:
        return pb.pokemon(p)
    
def lookup_pokemon_species(p: str):
    # extra stats such as gender info are found in here
    if p.isdigit():
        return pb.pokemon_species(int(p))
    else:
        return pb.pokemon_species(p)

def format_gender(e: int):
    # takes the gender rate for female (in 8ths)
    # and returns the formatted line for gender info.
    # A value of -1 means genderless
    gender_info = ''
    if e == -1:
        gender_info = 'genderless'
    else:
        # ♀ ♂
        f_pct = round(100*(e/8.0))
        m_pct = 100-f_pct
        gender_info = f'♀: {f_pct}% ♂: {m_pct}%'

    return gender_info

def format_abilities(a):
    result = ''
    for ability in a:
        result += f'\t- {ability.ability.name}'

        if ability.is_hidden:
            result += ' [HIDDEN]\n'
        else:
            result += '\n'
    return result[:-1]

def stats_dict(poke):
    # creates a dict of the stats for formatting the template
    res = {}
    for stat in poke.stats:
        res[stat.stat.name] = stat.base_stat
    
    return res

def grab_sprite(poke, gender: Gender, shiny: bool):
    # returns the path to the downloaded sprite for the selected pokemon
    # cached pokemon file name schema:
    # imgs/[pokedex number]_[gender]_[shiny].png

    filepath = f'imgs/{poke.id_}_{gender.value}'
    if shiny:
        filepath += '_shiny'
    filepath += '.png'

    if os.path.isfile(filepath):
        return filepath

    else:
        # if the pokemon is genderless then female sprites are null
        # and we want to return the male sprite.
        if gender.value == 'Male' or gender.value == 'Genderless':
            if shiny:
                url = poke.sprites.front_shiny
            else:
                url = poke.sprites.front_default
        elif gender.value == 'Female':
            if shiny:
                url = poke.sprites.front_shiny_female
            else:
                url = poke.sprites.front_female

        response = requests.get(url)

        if response.status_code == 200:
            # save the image in the cache.
            with open(filepath, 'wb') as f:
                f.write(response.content)

        # TODO what to do if not a 200 status code...?
        # hasn't come up yet so not bothering yet

        return filepath

def clean_name(p: str, female: bool) -> str:
    # é -> e
    p = sub(r'é', 'e', p)

    p = sub(r"[^'`’a-zA-Z\-]+", '-', p).lower()

    # Farfetch’d -> farfetchd
    p = sub(r"['`’]", '', p)

    # In case someone puts the gender symbols at the end for Nidoran
    if p[-1] == '-':
        p = p[:-1]

    return name_special_cases(p, female)

def name_special_cases(p: str, female: bool) -> str: 

    if p == 'nidoran' and female:
        p = 'nidoran-f'

    elif p == 'nidoran' and not female:
        p = 'nidoran-m'

    # deoxys is a bit tricky bc of the types
    # if only deoxys is entered then assume deoxys-normal
    elif p == 'deoxys':
        p = 'deoxys-normal'

    # wormadam has three forms. assume plant as default.
    elif p == 'wormadam':
        p = 'wormadam-plant'

    # two forms: altered and origin
    elif p == 'giratina':
        p = 'giratina-altered'

    # land or sky
    elif p == 'shaymin':
        p = 'shaymin-land'

    # red-striped, blue-striped, or white-striped
    elif p == 'basculin':
        p = 'basculin-red-striped'\
    
    # standard and zen TODO also galarian!
    elif p == 'darmanitan':
        p = 'darmanitan-standard'

    # incarnate and therian
    elif p == 'tornadus':
        p = 'tornadus-incarnate'

    # incarnate and therian
    elif p == 'thundurus':
        p = 'thundurus-incarnate'

    # incarnate and therian
    elif p == 'landorus':
        p = 'landorus-incarnate'

    # ordinary and resolute
    elif p == 'keldeo':
        p = 'keldeo-ordinary'

    # aria or pirouette
    elif p == 'meloetta':
        p = 'meloetta-aria'

    return p

def print_output(output: str, padding: int):
    # this prints out the final output.
    # necessary in order to pad each line with blank spaces
    for line in output.split('\n'):
        print(' '*padding, end='')
        print(line)

if __name__ == '__main__':
    main()
"""
Port to pokebase API first. Then fix the existing issues.

Accept:
    Name or pokedex ID

    - maybe if the spelling is close enough then it fuzzes to the correct choice?

verbose template and shortened template for like gameboy color?

TODO theres a nasty overhead if you are calling a pokemon for the first
time. There is, however, an API cache. The total amount of data that
we can call on seems to be pretty limited so maybe just pull everything
on install?

TODO image to the left of the output... how does neofetch do it
with images?
    - https://github.com/dylanaraps/neofetch/blob/master/neofetch#L4010
    Notice that they enumerate a case for every image display backend...
    If we want this to be adoptable widespread then i guess we will need
    to do this.

TODO a preferences file that lets you limit pokemon generations?

TODO generate output for every possible combination to make sure
theres no strange edge cases. save as an automated test maybe?

"""
import argparse
from enum import Enum
import os.path
from os import system
import pokebase as pb
import requests


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
    handle_pokemon(args.pokemon, args.female, args.shiny)

def handle_pokemon(p, female: bool, shiny: bool):

    # lookup the pokemon    
    poke = lookup_pokemon(p)
    poke_extra = lookup_pokemon_species(p)

    # verify selected gender.
    # if sprites.front_female is null then we are looking at
    if not poke.sprites.front_female:
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

    image_filepath = grab_sprite(poke, gender, shiny)
    # TODO at some point handle different image viewers.
    # $((width/font_width))x$((height/font_height))@${xoffset}x${yoffset}
    #system(f'kitten icat --align left --scale-up --place 10x10@0x0 {image_filepath}')
    
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

def format_gender(e: int):
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
        filepath += f'_{shiny}'
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
                url = poke.sprite.front_shiny_female
            else:
                url = poke.sprites.front_female

        response = requests.get(url)

        if response.status_code == 200:
            # save the image in the cache.
            with open(filepath, 'wb') as f:
                f.write(response.content)

        # TODO what to do if not a 200 status code...?

        return filepath

main()
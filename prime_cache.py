"""
Run this here to download the sprites for ALL pokemon.
This includes shinies and gendered sprites!

This also doubles as a test to see if any pokemon names do not
work with pokeapi

Time taken to run:
A couple of minutes

Results in a cache with size:

"""

from pokefetch import *

def prime_cache():

    with open('pokemon_wordlist.txt', 'r') as f:
        wordlist = f.read().split('\n')

    for pokemon in wordlist:
        print(pokemon)
        for gender in ['MALE', 'FEMALE']:
            p = clean_name(pokemon)

            print(p)

            p = lookup_pokemon(p)

            if not p.sprites.front_female:
                gender = Gender['GENDERLESS']
            else:
                gender = Gender[gender]
            
            grab_sprite(p, gender, shiny=False)
            grab_sprite(p, gender, shiny=True)


prime_cache()

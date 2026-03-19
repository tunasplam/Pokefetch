#!/usr/bin/env -S uv run --script
# /// script
# requires-python = ">=3.12"
# dependencies = [
#   "pokebase>=1.4.1",
#   "requests>=2.32.3",
#   "typer>=0.15",
# ]
# ///

import os.path
import random
import subprocess
from re import sub
import tomllib
from typing import Any, Literal, Optional
import unicodedata

import pokebase as pb
import requests
import typer


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
Gender = Literal['Male', 'Female', 'Genderless']

DEFAULT_TEMPLATE = """\
{C2}PokeDex Number:     {C4}{ID}{NC}
{C2}Gender:             {C4}{gender_info}{NC}
{C2}Abilities:{C4}
{abilities}

{C3}HP:                 {C4}{hp}{NC}
{C3}Attack:             {C4}{attack}{NC}
{C3}Defence:            {C4}{defense}{NC}
{C3}Special Attack:     {C4}{special-attack}{NC}
{C3}Special Defence:    {C4}{special-defense}{NC}
{C3}Speed:              {C4}{speed}{NC}
"""

CONFIG_DIR = os.path.expanduser('~/.config/pokefetch')
TEMPLATE_PATH = os.path.join(CONFIG_DIR, 'template.txt')
CONFIG_PATH = os.path.join(CONFIG_DIR, 'config.toml')
CACHE_DIR = os.path.expanduser('~/.cache/pokefetch')

GEN_MAX_ID = {
    1: 151,
    2: 251,
    3: 386,
    4: 493,
    5: 649,
    6: 721,
    7: 809,
    8: 905,
    9: 1025,
}

FORM_DEFAULTS = {
    'deoxys':     'deoxys-normal',
    'wormadam':   'wormadam-plant',
    'giratina':   'giratina-altered',
    'shaymin':    'shaymin-land',
    'basculin':   'basculin-red-striped',
    'darmanitan': 'darmanitan-standard',  # TODO also galarian!
    'tornadus':   'tornadus-incarnate',
    'thundurus':  'thundurus-incarnate',
    'landorus':   'landorus-incarnate',
    'keldeo':     'keldeo-ordinary',
    'meloetta':   'meloetta-aria',
}

app = typer.Typer()

SPRITE_W = 25
SPRITE_H = 13

@app.command()
def show(
    pokemon: Optional[str] = typer.Argument(None, help='Select a pokemon by name or pokedex ID.'),
    female: bool = typer.Option(False, help='Display the female sprite.'),
    shiny: bool = typer.Option(False, help='Display the shiny version of the pokemon sprite.'),
    back: bool = typer.Option(False, help='Display the back-facing sprite.'),
    random_pokemon: bool = typer.Option(False, '--random', help='Display a random pokemon.'),
):
    """Displays cool pokemon sprites/stats in terminal."""
    if random_pokemon:
        config = load_config()
        max_gen = config.get('max_generation', 5)
        if max_gen not in GEN_MAX_ID:
            raise typer.BadParameter(f'max_generation must be 1–9, got {max_gen}.')
        identifier: int | str = random.randint(1, GEN_MAX_ID[max_gen])
    elif pokemon is None:
        raise typer.BadParameter('Provide a pokemon name/ID or use --random.')
    elif pokemon.isdigit():
        identifier = int(pokemon)
    else:
        identifier = clean_name(pokemon, female)
    poke = lookup_pokemon(identifier)
    validate(poke)
    poke_extra = lookup_pokemon_species(identifier)
    gender = lookup_gender(poke, female)
    image_filepath = get_sprite(poke, gender, shiny, back)
    template = load_template()
    output = template.format_map(
        {
            'name':         poke.name.title(),
            'ID':           poke.id_, 
            'gender_info':  format_gender(poke_extra.gender_rate),
            'abilities':    format_abilities(poke.abilities),
        } | bc | stats_dict(poke)
    )
    print('\033[2J\033[H', end='', flush=True)
    draw_output(poke.name.title(), output)
    subprocess.run(
        ['kitty', '+kitten', 'icat', '--align', 'left', '--scale-up',
         '--place', f'{SPRITE_W}x{SPRITE_H}@1x1', image_filepath],
        check=True,
    )

@app.command()
def prime_cache():
    """Downloads and caches sprites for all pokemon up to the configured max generation."""
    config = load_config()
    max_gen = config.get('max_generation', 5)
    if max_gen not in GEN_MAX_ID:
        raise typer.BadParameter(f'max_generation must be 1–9, got {max_gen}.')
    max_id = GEN_MAX_ID[max_gen]

    for pokemon_id in range(1, max_id + 1):
        poke = lookup_pokemon(pokemon_id)
        typer.echo(f'{pokemon_id}: {poke.name}')
        for female in [False, True]:
            gender = lookup_gender(poke, female)
            if gender == 'Genderless' and female:
                continue
            get_sprite(poke, gender, shiny=False, back=False)
            get_sprite(poke, gender, shiny=True, back=False)

def validate(poke: Any):
    """Determines if the pokemon is valid."""
    if poke.id_ is None:
        print("Pokemon not found! Please enter valid pokemon.")
        raise typer.Exit(1)

def lookup_pokemon(p: int | str) -> Any:
    """Looks up pokemon using pokebase API"""
    return pb.pokemon(p)

def lookup_pokemon_species(p: int | str) -> Any:
    """Looks up extra info (gender rate, etc.) for a pokemon."""
    return pb.pokemon_species(p)

def lookup_gender(poke, female: bool) -> Gender:
    """Determine selected gender"""
    # nidoran messes things up because nidoran-f will have its sprites
    # saved under default instead of female
    # manually set genders for nidoran.
    if poke == 'nidoran-f' or poke == 'nidoran-m' or \
      not poke.sprites.front_female:
        return 'Genderless'

    if female:
        return 'Female'

    return 'Male'

def load_config() -> dict:
    """Loads user config from ~/.config/pokefetch/config.toml."""
    if os.path.isfile(CONFIG_PATH):
        with open(CONFIG_PATH, 'rb') as f:
            return tomllib.load(f)
    return {}

def load_template() -> str:
    """Loads the template from either set path or from default."""
    if os.path.isfile(TEMPLATE_PATH):
        with open(TEMPLATE_PATH, 'r', encoding='utf-8') as f:
            return f.read()
    else:
        return DEFAULT_TEMPLATE


def format_gender(gender_rate: int) -> str:
    """Determines gender information for the pokemon"""
    # takes the gender rate for female (in 8ths)
    # and returns the formatted line for gender info.
    # A value of -1 means genderless
    if gender_rate == -1:
        return 'genderless'
    # ♀ ♂
    f_pct = round(100*(gender_rate/8.0))
    m_pct = 100-f_pct
    return f'♀: {f_pct}% ♂: {m_pct}%'

def format_abilities(a) -> str:
    """Formats the abilities and specifies if they are hidden."""
    lines = []
    for ability in a:
        line = f'\t- {ability.ability.name}'
        if ability.is_hidden:
            line += ' [HIDDEN]'
        lines.append(line)
    return '\n'.join(lines)

def stats_dict(poke) -> dict:
    """ creates a dict of the stats for formatting the template."""
    return { stat.stat.name: stat.base_stat for stat in poke.stats }

def get_sprite(poke, gender: Gender, shiny: bool, back: bool) -> str:
    """Gets the path to the downloaded sprite for our selected pokemon.

    Sprites are cached under ~/.cache/pokefetch/ using the schema:
    [pokedex number]_[gender][_shiny][_back].png
    """
    filename = f'{poke.id_}_{gender}'
    if shiny:
        filename += '_shiny'
    if back:
        filename += '_back'
    filename += '.png'
    filepath = os.path.join(CACHE_DIR, filename)

    if os.path.isfile(filepath):
        return filepath

    # if the pokemon is genderless then female sprites are null
    # and we want to return the male sprite.
    if gender == 'Female':
        if back:
            url = poke.sprites.back_shiny_female if shiny else poke.sprites.back_female
        else:
            url = poke.sprites.front_shiny_female if shiny else poke.sprites.front_female
    else:
        if back:
            url = poke.sprites.back_shiny if shiny else poke.sprites.back_default
        else:
            url = poke.sprites.front_shiny if shiny else poke.sprites.front_default

    response = requests.get(url)

    if response.status_code != 200:
        print(f'Failed to fetch sprite (HTTP {response.status_code}).')
        raise typer.Exit(1)

    os.makedirs(CACHE_DIR, exist_ok=True)
    with open(filepath, 'wb') as f:
        f.write(response.content)

    return filepath

def clean_name(p: str, female: bool) -> str:
    """Cleans names to make them safe for API."""
    # normalize unicode accents (é -> e, etc.)
    p = unicodedata.normalize('NFKD', p).encode('ascii', 'ignore').decode('ascii')

    p = sub(r"[^’`'a-zA-Z\-]+", '-', p).lower()

    # Farfetch’d -> farfetchd
    p = sub(r"['`’]", '', p)

    # In case someone puts the gender symbols at the end for Nidoran
    if p[-1] == '-':
        p = p[:-1]

    return name_special_cases(p, female)

def name_special_cases(p: str, female: bool) -> str:
    if p == 'nidoran':
        return 'nidoran-f' if female else 'nidoran-m'
    return FORM_DEFAULTS.get(p, p)

def draw_output(name: str, output: str):
    """Draws a rounded box around the sprite area with the pokemon name in the
    top border and stats appended to the right of each line."""
    stat_lines = output.rstrip('\n').split('\n')

    title = f' {name} '
    remaining = SPRITE_W - len(title)
    left = remaining // 2
    right = remaining - left

    lines = [f'╭{"─" * left}{title}{"─" * right}╮']
    for i in range(SPRITE_H):
        stat = stat_lines[i] if i < len(stat_lines) else ''
        lines.append(f'│{" " * SPRITE_W}│  {stat}{bc["NC"]}')
    lines.append(f'╰{"─" * SPRITE_W}╯')

    print('\n'.join(lines), flush=True)

if __name__ == '__main__':
    app()

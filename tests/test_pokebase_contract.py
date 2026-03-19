"""
Integration tests that verify our assumptions about the structure of pokebase
API responses. These hit the real PokeAPI (responses are cached by pokebase).

Pokemon used:
  pikachu (25)   - has female sprite (heart-tail, Gen IV+), standard test subject
  magnemite (81) - genderless, gender_rate == -1
  garchomp (445) - no female sprite, gender_rate > 0 (confirms front_female can be
                   None even for gendered pokemon)
"""

import pytest
import pokebase as pb


# ---------------------------------------------------------------------------
# Fixtures
# ---------------------------------------------------------------------------

@pytest.fixture(scope='module')
def pikachu():
    return pb.pokemon('pikachu')

@pytest.fixture(scope='module')
def pikachu_species():
    return pb.pokemon_species('pikachu')

@pytest.fixture(scope='module')
def magnemite():
    return pb.pokemon('magnemite')

@pytest.fixture(scope='module')
def magnemite_species():
    return pb.pokemon_species('magnemite')

@pytest.fixture(scope='module')
def bulbasaur():
    return pb.pokemon('bulbasaur')


# ---------------------------------------------------------------------------
# pb.pokemon — core fields
# ---------------------------------------------------------------------------

def test_pokemon_has_id(pikachu):
    assert isinstance(pikachu.id_, int)
    assert pikachu.id_ == 25

def test_pokemon_has_name(pikachu):
    assert isinstance(pikachu.name, str)
    assert pikachu.name == 'pikachu'


# ---------------------------------------------------------------------------
# pb.pokemon — abilities
# ---------------------------------------------------------------------------

def test_pokemon_abilities_is_iterable(pikachu):
    abilities = list(pikachu.abilities)
    assert len(abilities) > 0

def test_ability_has_name(pikachu):
    for ability in pikachu.abilities:
        assert isinstance(ability.ability.name, str)
        assert len(ability.ability.name) > 0

def test_ability_has_is_hidden(pikachu):
    for ability in pikachu.abilities:
        assert isinstance(ability.is_hidden, bool)


# ---------------------------------------------------------------------------
# pb.pokemon — stats
# ---------------------------------------------------------------------------

EXPECTED_STAT_NAMES = {'hp', 'attack', 'defense', 'special-attack', 'special-defense', 'speed'}

def test_pokemon_stats_is_iterable(pikachu):
    stats = list(pikachu.stats)
    assert len(stats) > 0

def test_stat_has_name(pikachu):
    for stat in pikachu.stats:
        assert isinstance(stat.stat.name, str)

def test_stat_has_base_stat(pikachu):
    for stat in pikachu.stats:
        assert isinstance(stat.base_stat, int)
        assert stat.base_stat >= 0

def test_stats_cover_expected_names(pikachu):
    names = {stat.stat.name for stat in pikachu.stats}
    assert EXPECTED_STAT_NAMES.issubset(names)


# ---------------------------------------------------------------------------
# pb.pokemon — sprites
# ---------------------------------------------------------------------------

def test_sprites_front_default_is_url(pikachu):
    assert isinstance(pikachu.sprites.front_default, str)
    assert pikachu.sprites.front_default.startswith('https://')

def test_sprites_front_shiny_is_url(pikachu):
    assert isinstance(pikachu.sprites.front_shiny, str)
    assert pikachu.sprites.front_shiny.startswith('https://')

def test_sprites_back_default_is_url(pikachu):
    assert isinstance(pikachu.sprites.back_default, str)
    assert pikachu.sprites.back_default.startswith('https://')

def test_sprites_back_shiny_is_url(pikachu):
    assert isinstance(pikachu.sprites.back_shiny, str)
    assert pikachu.sprites.back_shiny.startswith('https://')

def test_sprites_front_female_is_url_for_gendered_pokemon(pikachu):
    # pikachu has a distinct female sprite (heart-shaped tail)
    assert isinstance(pikachu.sprites.front_female, str)
    assert pikachu.sprites.front_female.startswith('https://')

def test_sprites_front_female_is_none_when_no_female_sprite(bulbasaur):
    # bulbasaur has no distinct female sprite
    assert bulbasaur.sprites.front_female is None

def test_sprites_attributes_exist(pikachu):
    # all sprite attributes we access must exist (even if None)
    sprites = pikachu.sprites
    for attr in ('front_default', 'front_female', 'front_shiny', 'front_shiny_female',
                 'back_default', 'back_female', 'back_shiny', 'back_shiny_female'):
        assert hasattr(sprites, attr), f'sprites.{attr} missing'


# ---------------------------------------------------------------------------
# pb.pokemon_species — gender_rate
# ---------------------------------------------------------------------------

def test_species_has_gender_rate(pikachu_species):
    assert isinstance(pikachu_species.gender_rate, int)

def test_gender_rate_range_for_gendered(pikachu_species):
    assert 0 <= pikachu_species.gender_rate <= 8

def test_gender_rate_is_minus_one_for_genderless(magnemite_species):
    assert magnemite_species.gender_rate == -1


# ---------------------------------------------------------------------------
# Invalid pokemon — our validate() assumption
# ---------------------------------------------------------------------------

def test_invalid_pokemon_returns_none_id():
    # pokebase returns an APIResource with id_=None for unknown pokemon
    poke = pb.pokemon('thispokemdoesnotexist')
    assert poke.id_ is None

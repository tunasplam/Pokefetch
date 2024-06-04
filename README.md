# Pokefetch

Not guaranteed to work for pokemon after Gen V

## Context
This script currently asks for the pokedex name or number of the pokemon you'd like to get information about. Then it will get the picture and some related information such as type, abilities, weaknesses, etc.

Currently, this tool runs on Kitty using the `icat` kitten. If you would like to modify this tool to add other image backends then feel free to fork this.

![Someday an example image will be here](imgs/25_Female.png "Initial Example")

## Setup

### kitty
Currently, this only supports kitty.

[Information here](https://sw.kovidgoyal.net/kitty/)

### Using pip

`pip install pokefetch`

### Using github + Poetry

[Install Poetry](https://github.com/PokeAPI/pokebase)

Clone this repository to a directory of your choice in the command-line:
```
git clone https://github.com/tunasplam/Pokefetch.git
```

In the directory:
```
poetry install
```

## Future Goals

- Fuzzy matching for pokemon names
- Package and distribute through package managers
- Cool little dataset that has 8 bash colors for each pokemon sprite
- Tool that finds the pokemon sprite best associated with 8 given colors. This will hopefully allow this to be hooked in with pywal.
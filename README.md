# Pokefetch

TODO the fancy GIF
![Someday an example image will be here](imgs/25_Female.png "Initial Example")

This script fetches, formats, and outputs a sprite information about a given pokemon. Pokemon can be looked up by name or pokedex number. Alternate sprites supported includes gendered, back, and shiny pokemon. The output information is also customizable.

Currently, this tool runs on Kitty using `kitty +kitten icat`. If you would like to modify this tool to add other image backends then feel free to fork this.

## Setup

This script assumes that you are using kitty as your terminal and uv to manage your python environments.

### kitty

Currently, this only supports kitty.

[Information here](https://sw.kovidgoyal.net/kitty/)

### Using uv

[Install uv](https://docs.astral.sh/uv/getting-started/installation/)

Clone this repository and copy the script to your bin:

```bash
git clone https://github.com/tunasplam/Pokefetch.git
cp pokefetch.py /usr/local/bin/pokefetch
chmod +x ~/bin/pokefetch
```

## Usage

```bash
pokefetch show [OPTIONS] [POKEMON]
pokefetch prime-cache
```

### show

Display a pokemon's sprite and stats.

```bash
pokefetch show pikachu
pokefetch show 25
pokefetch show pikachu --female
pokefetch show pikachu --shiny
pokefetch show pikachu --back
pokefetch show --random
pokefetch show --random --shiny
```

| Option | Description |
|---|---|
| `--female` | Display the female sprite |
| `--shiny` | Display the shiny sprite |
| `--back` | Display the back-facing sprite |
| `--random` | Pick a random pokemon (respects `max_generation` in config) |

### prime-cache

Pre-downloads sprites for all pokemon up to the configured max generation. Useful to avoid the download delay on first use.

```bash
pokefetch prime-cache
```

## Customization

### Config file

General settings live in `~/.config/pokefetch/config.toml`. If that file does not exist, defaults are used.

| Key | Type | Default | Description |
|---|---|---|---|
| `max_generation` | int (1–9) | `5` | Maximum generation included when using `--random` |

### Template

The output template can be customized by editing `~/.config/pokefetch/template.txt`. If that file does not exist, a default template is used. All template text is offset to appear to the right of the output sprite. The template supports the following fields:

| Field | Description |
|---|---|
| `{ID}` | Pokedex number |
| `{gender_info}` | Gender ratio or "genderless" |
| `{abilities}` | List of abilities |
| `{hp}` | Base HP |
| `{attack}` | Base Attack |
| `{defense}` | Base Defense |
| `{special-attack}` | Base Special Attack |
| `{special-defense}` | Base Special Defense |
| `{speed}` | Base Speed |

Color codes `{C0}`–`{C7}`, bold `{BC0}`–`{BC7}`, and underline `{UC0}`–`{UC7}` are also available, with `{NC}` to reset.

# Unibash

- Platform-agnostic CLI for Unibash DSL (Python 3 runtime).
- Two modes: interactive TTY (line-by-line) and `.ush` script execution.
- ANTLR-based grammar with a visitor-driven runtime and executor layer.

Uses ANTLR4 and Python3.

Shields: [![MIT License][mit-shield]][mit]

[mit]: https://opensource.org/licenses/MIT
[mit-shield]: https://img.shields.io/badge/License-MIT-lightgrey

<a rel="license" href="https://opensource.org/licenses/MIT"><img alt="MIT License" height=47px style="border-width:0" src="https://images-wixmp-ed30a86b8c4ca887773594c2.wixmp.com/i/7195e121-eded-45cf-9aab-909deebd81b2/d9ur2lg-28410b47-58fd-4a48-9b67-49c0f56c68ce.png/v1/fill/w_1035,h_772,q_70,strp/mit_license_logo_by_excaliburzero_d9ur2lg-pre.jpg" /></a><br>This work is licensed under the <a rel="license" href="https://opensource.org/licenses/MIT">MIT License</a>.

## Setup

Assuming Java, Python3 and ANTLR are already set up, [instructions here](https://tomassetti.me/antlr-mega-tutorial/).

## Build

```sh
./tools/build.sh
```

will generate the ANTLR parser and lexer files in `unibash-py/gen`.

## Run

```sh
python3 unibash-py/Driver.py
# or
python3 unibash-py/Driver.py -m parrot test/simple.ush
```

## Test

```sh
cd unibash-py
python3 -m unittest discover tests
```

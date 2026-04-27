# Unibash

- Platform-agnostic CLI for Unibash DSL (Python 3 runtime).
- Two modes: interactive TTY (line-by-line) and `.ush` script execution.
- ANTLR-based grammar with a visitor-driven runtime and executor layer.

Uses ANTLR4 and Python3.

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

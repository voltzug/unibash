# Unibash

Uses ANTLR4 and Python3.

## Setup

Assuming Java, Python3 and ANTLR are already set up, [instructions here](https://tomassetti.me/antlr-mega-tutorial/).

## Build

```sh
./tools/build.sh
```

will generate the ANTLR parser and lexer files in `unibash-py/gen`.

## Run

To run the interpreter on an input file, use the run script:

```sh
./tools/run.sh <input-file>
```

For example:

```sh
./tools/run.sh test/simple.ush
```

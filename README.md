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

To run the interpreter on an input file, use the run script:

```sh
./tools/run.sh <input-file>
```

For example:

```sh
./tools/run.sh test/simple.ush
```

> [!TIP]
> To visualize the parse tree use _ANTLR_'s TestRig with the `-gui` flag:
> `grun unibash-py/gen/UnibashParser program -gui test/simple.ush`.

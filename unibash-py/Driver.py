import argparse
import sys

from antlr4 import CommonTokenStream, FileStream
from cli.repl import UnibashREPL
from gen.UnibashLexer import UnibashLexer
from gen.UnibashParser import UnibashParser
from runtime.context import RuntimeContext
from runtime.exceptions import UnibashRuntimeError
from visitor.evaluator import UnibashEvaluator


def get_executor(mode: str):
    if mode == "parrot":
        from executor.parrot.executor import ParrotExecutor

        return ParrotExecutor()
    elif mode == "base":
        from executor.base.executor import BaseExecutor

        return BaseExecutor()
    else:
        print(f"Unknown mode: {mode}")
        sys.exit(1)


def main():
    parser = argparse.ArgumentParser(description="Unibash Interpreter")
    parser.add_argument(
        "file",
        nargs="?",
        help="The .ush script to run. If not provided, starts the REPL.",
    )
    parser.add_argument(
        "-m",
        "--mode",
        choices=["base", "parrot"],
        default="base",
        help="The executor mode to use (default: base)",
    )

    args = parser.parse_args()

    executor = get_executor(args.mode)

    if not args.file:
        UnibashREPL(executor=executor).run()
        return 0

    input_stream = FileStream(args.file, encoding="utf-8")
    lexer = UnibashLexer(input_stream)
    token_stream = CommonTokenStream(lexer)
    parser = UnibashParser(token_stream)

    tree = parser.program()
    if parser.getNumberOfSyntaxErrors() > 0:
        print("!! syntax errors")
        return 1

    context = RuntimeContext()
    evaluator = UnibashEvaluator(context, executor=executor)

    try:
        evaluator.visit(tree)
    except UnibashRuntimeError as e:
        print(f"Runtime Error: {e}")
        return 1
    except Exception as e:
        print(f"Error: {e}")
        return 1

    return 0


if __name__ == "__main__":
    sys.exit(main())

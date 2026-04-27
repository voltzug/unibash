import sys

try:
    import readline  # Adds history support to input() automatically on Unix
except ImportError:
    pass  # Windows or environment without readline

from antlr4 import CommonTokenStream, InputStream
from antlr4.error.ErrorListener import ErrorListener
from gen.UnibashLexer import UnibashLexer
from gen.UnibashParser import UnibashParser
from runtime.context import RuntimeContext
from runtime.exceptions import UnibashRuntimeError
from visitor.evaluator import UnibashEvaluator


class REPLErrorListener(ErrorListener):
    def __init__(self):
        super().__init__()
        self.errors = []

    def syntaxError(self, recognizer, offendingSymbol, line, column, msg, e):
        self.errors.append(f"line {line}:{column} {msg}")


class UnibashREPL:
    def __init__(self, executor=None):
        self.context = RuntimeContext()
        self.evaluator = UnibashEvaluator(self.context, executor)

    def run(self):
        print("Unibash REPL (type 'exit' or 'quit' to exit)")
        buffer = []
        brace_count = 0

        while True:
            try:
                if not buffer:
                    prompt = "unibash> "
                else:
                    prompt = "... "

                line = input(prompt)

                if not buffer and line.strip() in ("exit", "quit"):
                    break

                if not line.strip() and not buffer:
                    continue

                buffer.append(line)

                # Simple multiline heuristic: count braces
                brace_count += line.count("{") - line.count("}")

                if brace_count > 0:
                    continue

                text_to_parse = "\n".join(buffer) + "\n"
                buffer = []
                brace_count = 0

                self.execute(text_to_parse)

            except EOFError:
                print("\nExiting...")
                break
            except KeyboardInterrupt:
                print("\nKeyboardInterrupt")
                buffer = []
                brace_count = 0

    def execute(self, text: str):
        input_stream = InputStream(text)
        lexer = UnibashLexer(input_stream)
        token_stream = CommonTokenStream(lexer)
        parser = UnibashParser(token_stream)

        error_listener = REPLErrorListener()
        parser.removeErrorListeners()
        parser.addErrorListener(error_listener)

        tree = parser.program()

        if error_listener.errors:
            for err in error_listener.errors:
                print(f"Syntax error: {err}")
            return

        try:
            self.evaluator.visit(tree)
        except UnibashRuntimeError as e:
            print(f"Runtime Error: {e}")
        except Exception as e:
            print(f"Error: {e}")

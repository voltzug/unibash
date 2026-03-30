import sys
from antlr4 import FileStream, CommonTokenStream
from gen.UnibashLexer import UnibashLexer
from gen.UnibashParser import UnibashParser

def main(argv):
    if len(argv) < 2:
        print("usage: python3 Driver.py <input-file>")
        return 2

    input_stream = FileStream(argv[1], encoding="utf-8")
    lexer = UnibashLexer(input_stream)
    token_stream = CommonTokenStream(lexer)
    parser = UnibashParser(token_stream)

    context = parser.program()
    if parser.getNumberOfSyntaxErrors() > 0:
        print("!! syntax errors")
        return 1

    print(context.toStringTree(recog=parser))
    return 0


if __name__ == "__main__":
    raise SystemExit(main(sys.argv))

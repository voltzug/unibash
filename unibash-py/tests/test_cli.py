import io
import unittest
from unittest.mock import patch

from cli.repl import UnibashREPL


class TestCLI(unittest.TestCase):
    def setUp(self):
        self.repl = UnibashREPL()

    @patch("sys.stdout", new_callable=io.StringIO)
    def test_repl_execute_print_var(self, mock_stdout):
        # The REPL execute method should process standard AST nodes
        self.repl.execute("set port = 8080\n")
        self.repl.execute("print port\n")
        output = mock_stdout.getvalue()
        self.assertIn("[PARROT] PRINT: 8080", output)

    @patch("sys.stdout", new_callable=io.StringIO)
    def test_repl_execute_host_ping(self, mock_stdout):
        # Define a host and trigger a ping via ParrotExecutor
        self.repl.execute('host web1 = "192.168.1.10"\n')
        self.repl.execute("ping web1\n")
        output = mock_stdout.getvalue()
        self.assertIn("[PARROT] PING web1(192.168.1.10) | count=4 timeout=5", output)

    @patch("sys.stdout", new_callable=io.StringIO)
    def test_repl_syntax_error(self, mock_stdout):
        # Invalid syntax should trigger the REPLErrorListener
        self.repl.execute("this is completely invalid syntax\n")
        output = mock_stdout.getvalue()
        self.assertIn("Syntax error:", output)


if __name__ == "__main__":
    unittest.main()

import os
import importlib
import asyncio
import shutil
import tempfile
import unittest


# Helper to print results in a simple table format
def print_results_table(name: str, results: list) -> None:
    print(f"\n[{name}] Results Table:")
    print("Idx  | Type   | Error | Text")
    print("-----|--------|-------|-----")
    for idx, tc in enumerate(results):
        error_flag = getattr(tc, "error", False)
        # Replace newlines in text for single-line display
        text = tc.text.strip().replace("\n", "\\n")
        print(f"{idx:<3} | {tc.type:<6} | {error_flag!s:<5} | {text}")


class TestCLIMCPServer(unittest.TestCase):
    def setUp(self):
        # Create a temporary directory for allowed_dir
        self.tempdir = tempfile.TemporaryDirectory()
        os.environ["ALLOWED_DIR"] = self.tempdir.name
        # Remove custom allowed commands/flags to use defaults
        os.environ.pop("ALLOWED_COMMANDS", None)
        os.environ.pop("ALLOWED_FLAGS", None)
        # Ensure shell operators are disabled by default
        os.environ.pop("ALLOW_SHELL_OPERATORS", None)
        # Reload server module to pick up env changes
        try:
            import cli_mcp_server.server as server_module

            self.server = importlib.reload(server_module)
        except ImportError:
            import cli_mcp_server.server as server_module

            self.server = server_module

    def tearDown(self):
        self.tempdir.cleanup()

    def test_run_pwd(self):
        # Run 'pwd' command
        result = asyncio.run(
            self.server.handle_call_tool("run_command", {"command": "pwd"})
        )
        texts = [tc.text for tc in result]
        # Debug print: show results in table form
        print_results_table("test_run_pwd", result)
        self.assertTrue(texts, "No output returned")
        self.assertEqual(texts[0].strip(), self.tempdir.name)
        self.assertTrue(any("return code: 0" in text for text in texts))

    def test_run_ls(self):
        # Create a file in the allowed directory
        file_path = os.path.join(self.tempdir.name, "foo.txt")
        with open(file_path, "w") as f:
            f.write("test")
        result = asyncio.run(
            self.server.handle_call_tool("run_command", {"command": "ls"})
        )
        texts = [tc.text for tc in result]
        # Debug print: show results in table form
        print_results_table("test_run_ls", result)
        self.assertTrue(
            any("foo.txt" in text for text in texts),
            f"Output did not contain 'foo.txt': {texts}",
        )
        self.assertTrue(any("return code: 0" in text for text in texts))

    def test_run_curl_ifconfig(self):
        # Skip test if curl is not available
        if not shutil.which("curl"):
            self.skipTest("curl is not available on PATH")
        # Allow all commands and flags
        os.environ["ALLOWED_COMMANDS"] = "all"
        os.environ["ALLOWED_FLAGS"] = "all"
        # Reload server to pick up new settings
        import cli_mcp_server.server as server_module

        self.server = importlib.reload(server_module)
        result = asyncio.run(
            self.server.handle_call_tool(
                "run_command", {"command": "curl -sG ifconfig.me"}
            )
        )
        texts = [tc.text for tc in result]
        # Debug print: show results in table form
        print_results_table("test_run_curl_ifconfig", result)
        output_texts = [t for t in texts if "return code" not in t]
        self.assertTrue(
            any(t.strip() for t in output_texts), f"No IP address retrieved: {texts}"
        )
        self.assertTrue(any("return code: 0" in text for text in texts))
    
    def test_shell_operator_disallowed(self):
        # Ensure shell operators are disabled by default
        result = asyncio.run(
            self.server.handle_call_tool("run_command", {"command": "echo 1 && echo 2"})
        )
        texts = [tc.text for tc in result]
        print_results_table("test_shell_operator_disallowed", result)
        self.assertTrue(
            any("Security violation" in text for text in texts),
            f"Expected security violation for shell operators, got: {texts}",
        )
        self.assertTrue(
            any("Shell operator '&&' is not supported" in text for text in texts),
            f"Expected '&&' not supported message, got: {texts}",
        )

    def test_shell_operator_allowed_and_executes_commands(self):
        # Enable shell operators and allow all commands/flags
        os.environ["ALLOW_SHELL_OPERATORS"] = "true"
        os.environ["ALLOWED_COMMANDS"] = "all"
        os.environ["ALLOWED_FLAGS"] = "all"
        # Reload server to pick up new settings
        import cli_mcp_server.server as server_module

        server = importlib.reload(server_module)
        # Execute a compound command with '&&'
        result = asyncio.run(
            server.handle_call_tool("run_command", {"command": "echo 3 && echo 4"})
        )
        texts = [tc.text for tc in result]
        print_results_table("test_shell_operator_allowed", result)
        # The first element should contain the combined stdout from both commands
        self.assertEqual(
            texts[0].strip(),
            "3\n4",
            f"Unexpected combined output, got: {texts[0]!r}",
        )
        self.assertTrue(any("return code: 0" in text for text in texts))

    def test_shell_operator_semicolon(self):
        # Enable shell operators and allow all commands/flags
        os.environ["ALLOW_SHELL_OPERATORS"] = "true"
        os.environ["ALLOWED_COMMANDS"] = "all"
        os.environ["ALLOWED_FLAGS"] = "all"
        # Reload server to pick up new settings
        import cli_mcp_server.server as server_module

        server = importlib.reload(server_module)
        # Execute a compound command with ';'
        result = asyncio.run(
            server.handle_call_tool("run_command", {"command": "echo 5; echo 6"})
        )
        texts = [tc.text for tc in result]
        print_results_table("test_shell_operator_semicolon", result)
        self.assertEqual(
            texts[0].strip(),
            "5\n6",
            f"Unexpected combined output, got: {texts[0]!r}",
        )
        self.assertTrue(any("return code: 0" in text for text in texts))
    
    def test_shell_operator_append_redirection(self):
        # Enable shell operators and allow all commands/flags
        os.environ["ALLOW_SHELL_OPERATORS"] = "true"
        os.environ["ALLOWED_COMMANDS"] = "all"
        os.environ["ALLOWED_FLAGS"] = "all"
        # Reload server to pick up new settings
        import cli_mcp_server.server as server_module

        server = importlib.reload(server_module)
        # Create an output file and append text using '>>'
        file_name = "append.txt"
        file_path = os.path.join(self.tempdir.name, file_name)
        # Ensure the file exists
        open(file_path, "w").close()
        result = asyncio.run(
            server.handle_call_tool("run_command", {"command": f"echo hello >> {file_name}"})
        )
        texts = [tc.text for tc in result]
        print_results_table("test_shell_operator_append_redirection", result)
        # After redirection, file should contain 'hello'
        with open(file_path, "r") as f:
            content = f.read().strip()
        self.assertEqual(content, "hello", f"Unexpected file content: {content!r}")
        self.assertTrue(any("return code: 0" in text for text in texts))

    def test_shell_operator_pipe(self):
        # Enable shell operators and allow all commands/flags
        os.environ["ALLOW_SHELL_OPERATORS"] = "true"
        os.environ["ALLOWED_COMMANDS"] = "all"
        os.environ["ALLOWED_FLAGS"] = "all"
        # Reload server to pick up new settings
        import cli_mcp_server.server as server_module

        server = importlib.reload(server_module)
        # Execute a simple pipeline to filter output
        result = asyncio.run(
            server.handle_call_tool("run_command", {"command": "echo 123 | grep 123"})
        )
        texts = [tc.text for tc in result]
        print_results_table("test_shell_operator_pipe", result)
        # The pipeline should output '123'
        self.assertEqual(texts[0].strip(), "123", f"Unexpected pipeline output: {texts[0]!r}")
        self.assertTrue(any("return code: 0" in text for text in texts))

    def test_shell_operator_or(self):
        # Enable shell operators and allow all commands/flags
        os.environ["ALLOW_SHELL_OPERATORS"] = "true"
        os.environ["ALLOWED_COMMANDS"] = "all"
        os.environ["ALLOWED_FLAGS"] = "all"
        # Reload server to pick up new settings
        import cli_mcp_server.server as server_module

        server = importlib.reload(server_module)
        # Use '||' to fallback on failure
        result = asyncio.run(
            server.handle_call_tool("run_command", {"command": "false || echo OR_OK"})
        )
        texts = [tc.text for tc in result]
        print_results_table("test_shell_operator_or", result)
        # The OR operation should output 'OR_OK'
        self.assertEqual(texts[0].strip(), "OR_OK", f"Unexpected OR output: {texts[0]!r}")
        self.assertTrue(any("return code: 0" in text for text in texts))


if __name__ == "__main__":
    unittest.main()

"""Code execution tool for agent"""

import sys
import io
import json
import requests
import time
import datetime
import os
import urllib.parse as urlparse
from typing import Dict


class CodeExecutor:
    """Safely execute Python code and return output"""

    @staticmethod
    def get_tool_definition() -> Dict:
        """Return OpenAI tool definition for code execution"""
        return {
            "type": "function",
            "function": {
                "name": "execute_python",
                "description": "Execute Python code and return the output. Use this to make HTTP requests, process data, or perform calculations. Common modules like json, requests, time, datetime are pre-imported.",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "code": {
                            "type": "string",
                            "description": "The Python code to execute. Common modules like json, requests, time, datetime are already available."
                        }
                    },
                    "required": ["code"]
                }
            }
        }

    @staticmethod
    def execute(code: str) -> Dict[str, str]:
        """
        Execute Python code and capture output

        Returns:
            Dict with 'output' (stdout) and 'error' (stderr) keys
        """
        # Capture stdout and stderr
        old_stdout = sys.stdout
        old_stderr = sys.stderr

        sys.stdout = io.StringIO()
        sys.stderr = io.StringIO()

        try:
            # Create execution namespace with common modules pre-imported
            exec_globals = {
                "__builtins__": __builtins__,
                "json": json,
                "requests": requests,
                "time": time,
                "datetime": datetime,
                "os": os,
                "urlparse": urlparse,
            }

            # Execute the code
            exec(code, exec_globals)

            output = sys.stdout.getvalue()
            error = sys.stderr.getvalue()

            return {
                "success": True,
                "output": output,
                "error": error if error else None
            }

        except Exception as e:
            return {
                "success": False,
                "output": sys.stdout.getvalue(),
                "error": f"{type(e).__name__}: {str(e)}"
            }

        finally:
            # Restore stdout and stderr
            sys.stdout = old_stdout
            sys.stderr = old_stderr

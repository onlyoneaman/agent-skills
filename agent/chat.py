"""Simple terminal chat with skills"""

import os
import json
from typing import List, Dict
from rich.console import Console
from rich.markdown import Markdown
from rich.panel import Panel
from rich.prompt import Prompt
from rich.table import Table

from .skills_manager import SkillsManager
from .llm_client import LLMClient
from .code_executor import CodeExecutor


class SkillsChat:
    """Interactive chat with agent skills"""

    def __init__(self, skills_directory: str = "skills"):
        self.console = Console()
        self.skills_manager = SkillsManager(skills_directory)
        self.llm_client = LLMClient()
        self.code_executor = CodeExecutor()
        self.messages: List[Dict] = []

    def display_welcome(self):
        """Show welcome message and available skills"""
        self.console.print(Panel.fit(
            "[bold blue]Agent Skills Chat[/bold blue]\n"
            "AI agent with discoverable skills",
            border_style="blue"
        ))

        skills = self.skills_manager.list_skills()
        if skills:
            table = Table(title="Available Skills", show_header=True)
            table.add_column("Skill", style="cyan")
            table.add_column("Description", style="white")

            for skill in skills:
                table.add_row(skill["name"], skill["description"])

            self.console.print(table)
        else:
            self.console.print("[yellow]No skills found[/yellow]\n")

        self.console.print("\n[dim]Type 'exit' to quit[/dim]\n")

    def chat_loop(self):
        """Main conversation loop"""
        self.display_welcome()

        while True:
            try:
                user_input = Prompt.ask("\n[bold green]You[/bold green]")

                if user_input.lower() in ['exit', 'quit', 'q']:
                    self.console.print("\n[blue]Goodbye![/blue]")
                    break

                if not user_input.strip():
                    continue

                self.messages.append({"role": "user", "content": user_input})
                self._process_turn()

            except KeyboardInterrupt:
                self.console.print("\n\n[blue]Goodbye![/blue]")
                break
            except Exception as e:
                self.console.print(f"\n[red]Error: {e}[/red]")

    def _process_turn(self):
        """Process one turn of conversation"""
        tools = self.skills_manager.get_skill_tools()

        # Add code execution tool
        tools.append(self.code_executor.get_tool_definition())

        # Keep processing until we get a final response (no more tool calls)
        max_iterations = 10  # Prevent infinite loops
        iteration = 0
        
        while iteration < max_iterations:
            iteration += 1
            
            # Call LLM
            response = self.llm_client.chat(
                messages=self.messages,
                tools=tools if tools else None
            )

            # Handle tool calls (skill activation or code execution)
            if response["tool_calls"]:
                self._handle_tool_calls(response)
                # Continue loop to process the tool results
                continue

            # No more tool calls - we have a final response
            break

        # Show response
        if response["content"]:
            self.console.print("\n[bold blue]Assistant[/bold blue]")
            self.console.print(Markdown(response["content"]))

            self.messages.append({
                "role": "assistant",
                "content": response["content"]
            })

    def _handle_tool_calls(self, response: Dict):
        """Activate skills or execute code when called"""
        # Add assistant message with tool calls
        self.messages.append({
            "role": "assistant",
            "tool_calls": response["tool_calls"],
            "content": response.get("content")
        })

        # Process each tool call
        for tc in response["tool_calls"]:
            tool_name = tc["function"]["name"]

            # Handle code execution
            if tool_name == "execute_python":
                self.console.print("\n[dim]→ Executing Python code[/dim]")

                args = json.loads(tc["function"]["arguments"])
                code = args.get("code", "")

                # Execute the code
                result = self.code_executor.execute(code)

                if result["success"]:
                    tool_result = f"Code executed successfully.\n\nOutput:\n{result['output']}"
                    if result["error"]:
                        tool_result += f"\n\nWarnings:\n{result['error']}"
                else:
                    tool_result = f"Code execution failed.\n\nError:\n{result['error']}\n\nPartial output:\n{result['output']}"

                # Add tool result to conversation
                self.messages.append({
                    "role": "tool",
                    "tool_call_id": tc["id"],
                    "content": tool_result
                })

            # Handle skill activation
            elif tool_name.startswith("activate_skill_"):
                skill_name = tool_name.replace("activate_skill_", "").replace("_", "-")
                self.console.print(f"\n[dim]→ Activating skill: {skill_name}[/dim]")

                # Load full skill instructions
                skill_content = self.skills_manager.activate_skill(skill_name)

                if skill_content:
                    tool_result = f"Skill '{skill_name}' activated. Follow these instructions:\n\n{skill_content}"
                else:
                    tool_result = f"Error: Skill '{skill_name}' not found"

                # Add tool result to conversation
                self.messages.append({
                    "role": "tool",
                    "tool_call_id": tc["id"],
                    "content": tool_result
                })

            else:
                # Unknown tool
                self.messages.append({
                    "role": "tool",
                    "tool_call_id": tc["id"],
                    "content": f"Error: Unknown tool '{tool_name}'"
                })


def main():
    """Run the chat interface"""
    from dotenv import load_dotenv

    load_dotenv()

    if not os.getenv("OPENAI_API_KEY"):
        print("Error: OPENAI_API_KEY not found in .env file")
        return

    chat = SkillsChat()
    chat.chat_loop()


if __name__ == "__main__":
    main()

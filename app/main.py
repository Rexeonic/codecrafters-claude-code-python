import argparse
import os
import shlex
import subprocess
import sys
import json 

from openai import OpenAI

API_KEY = os.getenv("OPENROUTER_API_KEY")
BASE_URL = os.getenv("OPENROUTER_BASE_URL", default="https://openrouter.ai/api/v1")


def main():
    p = argparse.ArgumentParser()
    p.add_argument("-p", required=True)
    args = p.parse_args()

    if not API_KEY:
        raise RuntimeError("OPENROUTER_API_KEY is not set")

    client = OpenAI(api_key=API_KEY, base_url=BASE_URL)


    # Initialize the conversation
    messages = [{"role": "user", "content": args.p}]     # message array 
    # Agentic Loop
    while True:

        chat = client.chat.completions.create(
            model="anthropic/claude-haiku-4.5",
            messages=messages,
            tools=[
                {
                    "type": "function",     # always "function" for tools
                    "function": {
                        "name": "Read",
                        "description": "Read and return the contents of a file",
                        "parameters": {     # JSON schema describing the function's parameters
                        "type": "object",
                        "properties": {     # Defines parameter to the function
                            "file_path": {
                            "type": "string",
                            "description": "The path to the file to read"
                            }
                        },
                        "required": ["file_path"]   # Lists which parameters are mandatory
                        }
                    }
                },
                {
                    "type": "function",
                    "function": {
                        "name": "Write",
                        "description": "Write content to a file",
                        "parameters": {
                        "type": "object",
                        "properties": {
                            "file_path": {
                            "type": "string",
                            "description": "The path of the file to write to"
                            },
                            "content": {
                            "type": "string",
                            "description": "The content to write to the file"
                            }
                        },
                        "required": ["file_path", "content"]
                        }
                    }
                },
                {
                    "type": "function",
                    "function": {
                        "name": "Bash",
                        "description": "Execute a shell command",
                        "parameters": {
                        "type": "object",
                        "required": ["command"],
                        "properties": {
                            "command": {
                            "type": "string",
                            "description": "The command to execute"
                          }
                        }
                      }
                   }
                }

            ]
        )

        response = chat.choices[0].message

        message_dict = {
            "role": response.role,
            "content": response.content,
        }

        if hasattr(response, "tool_calls") and response.tool_calls:
            message_dict["tool_calls"] = [
                {
                    "id": tc.id,
                    "type": tc.type,
                    "function": {
                        "name": tc.function.name,
                        "arguments": tc.function.arguments,
                    },
                }
                for tc in response.tool_calls
            ]
        messages.append(message_dict)

        if not message_dict.get("tool_calls"):
            print(response.content)
            break

        for tc in response.tool_calls:
            args_dict = json.loads(tc.function.arguments)

            if tc.function.name == "Read":
                with open(args_dict["file_path"]) as f:
                    result = f.read()
                messages.append(
                    {
                        "role": "tool",
                        "tool_call_id": tc.id,
                        "content": result,
                    }
                )

            if tc.function.name == "Write":
                content = args_dict["content"]
                with open(args_dict["file_path"], 'w') as f:
                    f.write(content)

                messages.append(
                    {
                        "role": "tool",
                        "tool_call_id": tc.id,
                        "content": content,
                    }
                )

            if tc.function.name == "Bash":
                command = args_dict["command"]
                
                result = subprocess.run(command.split(" "), capture_output=True, text=True)
                
                if result.stderr:
                    result = result.stderr
                else:
                    result = result.stdout
                
                messages.append(
                    {
                        "role": "tool",
                        "tool_call_id": tc.id,
                        "content": result,
                    }
                )

if __name__ == "__main__":
    main()

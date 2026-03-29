Tools
-----
Tools are functions that an LLM can use to perform specific actions, like reading files or running commands.

<h3>Advertising Tools</h3>
Advertising tools lets the model know which tools are available and what arguments they accept.


<h3>Tool Calls</h3>

When the LLM decides to use a tool, the response message will contain a `tool_calls` array.

response structure:

{
  "choices": [      # list of generated response
    {
      "index": 0,
      "message": {
        "role": "assistant",
        "content": null,
        "tool_calls": [     # array of tool calls to make
          {
            "id": "call_abc123",    # unique identifier for the tool call
            "type": "function",     # type of tool call
            "function": {           # function details
              "name": "Read",       # name of function to call
              "arguments": "{\"file_path\": \"/path/to/file.txt\"}"          # JSON string containing the function parameters
            }
          }
        ]
      },
      "finish_reason": "tool_calls"
    }
  ]
}

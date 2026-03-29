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


Agent Loop
----------

<b>single interaction</b>: send a prompt to the LLM, get a response, execute one tool if requested, and exit. 

An agent loop that repeatedly sends messages to the model and handles tool calls as needed, until the final result is received.

1. Initialize the conversation:

You already have an initial conversation history: the messages array with the user's prompt. Now you need to store this array so it can persist across iterations, since the loop will continuously append new messages to it

    [
        { "role": "user", "content": "Summarize the README for me." }
    ]

2. Enter the loop:

Start the loop with the same API request you already have (sending your messages and tool specifications to the model). The difference is that this request now sits in a loop, allowing it to run multiple times.

3. Record the assistant's response:

Whatever message the model returns, add it to your messages array. If the model wants to use a tool, the response will contain a tool_calls array

{
  "role": "assistant",
  "content": null,
  "tool_calls": [
    {
      "id": "call_abc123",
      "type": "function",
      "function": {
        "name": "Read",
        "arguments": "{\"file_path\": \"README.md\"}"
      }
    }
  ]
}

4. Execute tool calls:

Check the model's response to see if it's requesting to use any tools. If tool calls are present

a. Execute each requested tool (but do not print their result to stdout)
b. Add each tool call result to your messages array. Every tool result must
    • Have the `role` field set to `"tool"`
    • Reference the corresponding `tool_call_id`
    • Include the tool call result as its `content`

{
  "role": "tool",
  "tool_call_id": "call_abc123",
  "content": "# My Project\n\nChemical expiry period: 6 months"
}

5. Repeat until complete:

Continue the loop until the model responds without requesting any tools (when `tool_calls` is missing or empty). At this point, print the final message `content` to stdout and exit.


Write Tool
----------

`Write` tool enables the LLM to write content to files. Like with the Read tool, you need to advertise the Write tool in your request and execute it when the model requests it.
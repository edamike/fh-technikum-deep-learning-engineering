# Section 1 — Single Agent · Scaffold

Fill in the `# TODO` markers to build your own agent with a tool.

## Your task

1. **Choose a domain** — weather is the example in `tools/weather_tool.py`,
   but you can use any API or function you like (see the comment at the top of that file).

2. **Implement the tool** in `tools/weather_tool.py`
   (or replace the file entirely with your own).

3. **Complete `agent.py`:**
   - Give the agent a name
   - Write an instruction that tells it when to call the tool
   - Add the tool to `tools=[...]`

## Run your scaffold

```bash
# from the lecture5/ directory
cd lecture5
adk web 01_single_agent/scaffold
```

Open **http://localhost:8000** and test your agent.

## Compare with the solution

```bash
adk web 01_single_agent/solution
```

The solution uses the weather example — yours doesn't have to.

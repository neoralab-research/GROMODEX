# GROMODEX

GROMODEX is a small Python package for GROMACS performance benchmarking through a full-factorial Design of Experiments.

It provides three surfaces:

- A CLI for researchers running local experiments.
- A JSON CLI manifest for shell-capable agents that are not connected through MCP.
- A FastMCP server for agents that need structured, validated tools.

The implementation keeps the workflow explicit: generate a design, prepare a GROMACS TPR file, execute numbered run folders, monitor GPU usage, parse the `<deffnm>.log` file, and write a results CSV.

# PyEurisko

**Work-in-progress** recreating Douglas Lenat's Eurisko system in Python.

## License

MIT License

## Acknowledgments

The starting point is the software archaeology project, [namin/eurisclo](https://github.com/namin/eurisclo).

### Claude.ai
I am experimenting with using Claude.ai with [a filesystem MCP server with re-entrant execution](https://github.com/namin/servers/tree/exec-reentrant/src/filesystem) to port from Common Lisp to Python.
Ups and downs, and it might not be a win move to use LLMs.
Pro-tip for now: It seems to help a lot to have two directories, [one summarizing Claude's insights](claude-docs) and [one summarizing my goals](my-docs).
I prompt it by asking it to follow the instructions in the RUN.md.

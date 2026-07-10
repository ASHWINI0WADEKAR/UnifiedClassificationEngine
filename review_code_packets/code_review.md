# Code Review Evidence

Review focus:

- `src/engine.py` dispatches all classifiers through one interface.
- Each classifier validates input and returns a common schema.
- Optional dependency loading degrades gracefully.
- API responses are consistent across endpoints.

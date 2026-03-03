---
name: paper
description: Provided are guidlines for how to interact with the paper mcp
---

Paper Design Tool

- write_html insert-children always appends to the end — there's no way to insert at a specific position in the child list. I had to work around this by using replace mode to wrap existing nodes in containers
  that include new sibling content.
- x-paper-clone inside replace mode works even when cloning the node being replaced — Paper clones before deleting.
- Duplicate-then-modify is the fastest approach for variant screens, but plan the structure upfront since you can't reorder children after creation.
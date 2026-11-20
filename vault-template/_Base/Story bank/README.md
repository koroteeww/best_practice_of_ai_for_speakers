---
type: hub
auto: false
---
# Story bank

Stories, cases, numbers, jokes and demos you can reuse. One note per story, made from the *Story* template.

```base
filters:
  and:
    - file.inFolder("_Base/Story bank")
    - type == "story"
views:
  - type: table
    name: All stories
    order:
      - file.name
      - kind
      - hook
      - topics
      - used_in
      - works
```

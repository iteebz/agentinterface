# Composition

Array-based layout system. Zero ceremony.

## Vertical Stack

Arrays render vertically:

```json
[
  {"type": "card", "data": {"title": "Card 1"}},
  {"type": "card", "data": {"title": "Card 2"}},
  {"type": "card", "data": {"title": "Card 3"}}
]
```

**Renders:**
```
┌─────────┐
│ Card 1  │
├─────────┤
│ Card 2  │
├─────────┤
│ Card 3  │
└─────────┘
```

**CSS:** `flex flex-col gap-6`

## Horizontal Grid

Nested arrays render horizontally:

```json
[
  [
    {"type": "card", "data": {"title": "Card 1"}},
    {"type": "card", "data": {"title": "Card 2"}},
    {"type": "card", "data": {"title": "Card 3"}}
  ]
]
```

**Renders:**
```
┌─────┐ ┌─────┐ ┌─────┐
│ C 1 │ │ C 2 │ │ C 3 │
└─────┘ └─────┘ └─────┘
```

**CSS:** `grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4`

Responsive: 1 column mobile, 2 tablet, 3 desktop.

## Mixed Layout

Combine vertical and horizontal:

```json
[
  {"type": "card", "data": {"title": "Header"}},
  [
    {"type": "card", "data": {"title": "Left"}},
    {"type": "card", "data": {"title": "Right"}}
  ],
  {"type": "card", "data": {"title": "Footer"}}
]
```

**Renders:**
```
┌──────────────┐
│   Header     │
├──────┬───────┤
│ Left │ Right │
├──────┴───────┤
│   Footer     │
└──────────────┘
```

## Infinite Nesting

Nest to any depth:

```json
[
  {"type": "card", "data": {"title": "Top"}},
  [
    {"type": "card", "data": {"title": "A"}},
    [
      {"type": "card", "data": {"title": "B1"}},
      {"type": "card", "data": {"title": "B2"}}
    ]
  ],
  {"type": "card", "data": {"title": "Bottom"}}
]
```

**Renders:**
```
┌────────────────┐
│      Top       │
├────┬───────────┤
│ A  │ ┌───┬───┐ │
│    │ │B1 │B2 │ │
│    │ └───┴───┘ │
├────┴───────────┤
│     Bottom     │
└────────────────┘
```

## Dashboard Example

Real-world composition:

```json
[
  {"type": "card", "data": {
    "title": "Q3 Sales Dashboard",
    "content": "Overview of Q3 performance metrics"
  }},
  [
    {"type": "card", "data": {"title": "Revenue", "content": "$2.4M"}},
    {"type": "card", "data": {"title": "Growth", "content": "+15%"}},
    {"type": "card", "data": {"title": "Users", "content": "10K"}}
  ],
  {"type": "table", "data": {
    "title": "Regional Breakdown",
    "attributes": [
      {"key": "region", "label": "Region"},
      {"key": "revenue", "label": "Revenue"}
    ],
    "items": [
      {"id": "na", "name": "North America", "attributes": {"region": "NA", "revenue": "$1.2M"}},
      {"id": "eu", "name": "Europe", "attributes": {"region": "EU", "revenue": "$800K"}}
    ]
  }},
  [
    {"type": "timeline", "data": {
      "title": "Key Events",
      "events": [
        {"date": "2024-07-01", "title": "Quarter Start"},
        {"date": "2024-09-30", "title": "Quarter End"}
      ]
    }},
    {"type": "markdown", "data": {
      "content": "## Next Steps\n- Analyze regional trends\n- Plan Q4 strategy"
    }}
  ],
  {"type": "suggestions", "data": {
    "suggestions": ["Show Q2 comparison", "Export data", "Regional deep dive"]
  }}
]
```

**Renders:**
```
┌────────────────────────────────┐
│     Q3 Sales Dashboard         │
├───────┬──────────┬─────────────┤
│Revenue│  Growth  │    Users    │
│ $2.4M │   +15%   │     10K     │
├───────┴──────────┴─────────────┤
│   Regional Breakdown (table)   │
├────────────────┬───────────────┤
│   Key Events   │  Next Steps   │
│   (timeline)   │  (markdown)   │
├────────────────┴───────────────┤
│       Suggestions (chips)      │
└────────────────────────────────┘
```

## Rules

1. **Array = vertical stack**
2. **Nested array = horizontal grid**
3. **Nesting = infinite depth**
4. **Components = anywhere**

No layout DSL. No configuration. Just arrays.
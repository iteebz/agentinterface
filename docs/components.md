# Components

10 UI primitives for agent interfaces.

## card

```json
{
  "type": "card",
  "data": {
    "title": "Q3 Revenue",
    "content": "$2.4M revenue, up 15%",
    "actions": ["View Details", "Export"],
    "metadata": "Updated 2 hours ago"
  }
}
```

**Props:** `title` (string), `content` (string | component), `actions` (string[]), `metadata` (string)

**Use:** Metrics, summaries, containers.

## table

```json
{
  "type": "table",
  "data": {
    "title": "Regional Sales",
    "attributes": [
      {"key": "region", "label": "Region"},
      {"key": "revenue", "label": "Revenue"}
    ],
    "items": [
      {"id": "na", "name": "North America", "attributes": {"region": "NA", "revenue": "$1.2M"}},
      {"id": "eu", "name": "Europe", "attributes": {"region": "EU", "revenue": "$800K"}}
    ]
  }
}
```

**Props:** `title` (string), `attributes` (array), `items` (array)

**Use:** Data tables, reports, comparisons.

## timeline

```json
{
  "type": "timeline",
  "data": {
    "title": "Project Milestones",
    "events": [
      {"date": "2024-01-15", "title": "Kickoff", "description": "Team assembled"},
      {"date": "2024-02-20", "title": "MVP Complete", "description": "Core features"}
    ]
  }
}
```

**Props:** `title` (string), `events` (array with `date`, `title`, `description`)

**Use:** Event sequences, changelogs, history.

## accordion

```json
{
  "type": "accordion",
  "data": {
    "title": "FAQ",
    "items": [
      {"label": "How to start?", "content": "Install via npm..."},
      {"label": "Supported LLMs?", "content": "OpenAI, Anthropic, Gemini..."}
    ]
  }
}
```

**Props:** `title` (string), `items` (array with `label` and `content`)

**Use:** FAQs, documentation, hierarchical content.

## tabs

```json
{
  "type": "tabs",
  "data": {
    "tabs": [
      {"id": "overview", "label": "Overview", "content": "System operational"},
      {"id": "metrics", "label": "Metrics", "content": {"type": "table", "data": {...}}}
    ]
  }
}
```

**Props:** `tabs` (array with `id`, `label`, `content` - content can be nested component)

**Use:** Multi-view interfaces, settings, categorized content.

## markdown

```json
{
  "type": "markdown",
  "data": {
    "content": "# Results\n\nRevenue up **15%**\n\n```python\nprint('hello')\n```"
  }
}
```

**Props:** `content` (string with markdown syntax)

**Use:** Formatted text, code snippets, documentation.

## image

```json
{
  "type": "image",
  "data": {
    "src": "https://example.com/chart.png",
    "alt": "Q3 Chart",
    "caption": "Revenue trends",
    "href": "https://example.com/report"
  }
}
```

**Props:** `src` (string), `alt` (string), `caption` (string), `href` (string)

**Use:** Charts, diagrams, screenshots.

## embed

```json
{
  "type": "embed",
  "data": {
    "url": "https://youtube.com/embed/VIDEO_ID",
    "title": "Demo",
    "height": "400px"
  }
}
```

**Props:** `url` (string), `title` (string), `height` (string)

**Use:** Videos, interactive demos, maps.

## citation

```json
{
  "type": "citation",
  "data": {
    "title": "Global Economic Outlook 2024",
    "url": "https://imf.org/report",
    "author": "IMF",
    "date": "2024-01-15",
    "quote": "Growth projected at 3.1%",
    "content": "Full report..."
  }
}
```

**Props:** `title` (string), `url` (string), `author` (string), `date` (string), `quote` (string), `content` (string)

**Use:** Research citations, source attribution, credibility.

## suggestions

```json
{
  "type": "suggestions",
  "data": {
    "suggestions": [
      "Show regional breakdown",
      "Compare to last quarter",
      "Export as CSV"
    ]
  }
}
```

**Props:** `suggestions` (string[])

**Use:** Follow-up prompts, conversational affordances.

## Nesting

All components support nested components:

```json
{
  "type": "card",
  "data": {
    "title": "Dashboard",
    "content": {
      "type": "table",
      "data": {"attributes": [...], "items": [...]}
    }
  }
}
```

Infinite composition depth.
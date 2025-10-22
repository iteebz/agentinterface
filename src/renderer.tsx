import React from "react";
import type { ComponentType } from "react";
import { CallbackEvent, ComponentTree, ComponentJSON } from "./types";
import { Accordion } from "./ai/accordion";
import { Card } from "./ai/card";
import { Citation } from "./ai/citation";
import { Embed } from "./ai/embed";
import { Image } from "./ai/image";
import { Markdown } from "./ai/markdown";
import { Suggestions } from "./ai/suggestions";
import { Table } from "./ai/table";
import { Tabs } from "./ai/tabs";
import { Timeline } from "./ai/timeline";

const DEFAULT_COMPONENTS: Record<string, ComponentType<any>> = {
  accordion: Accordion,
  card: Card,
  citation: Citation,
  embed: Embed,
  image: Image,
  markdown: Markdown,
  suggestions: Suggestions,
  table: Table,
  tabs: Tabs,
  timeline: Timeline,
};

export function render(
  agentJSON: string | ComponentTree,
  components?: Record<string, ComponentType<any>>,
  onCallback?: (event: CallbackEvent) => void,
): React.ReactNode {
  const componentMap = { ...DEFAULT_COMPONENTS, ...components };

  function renderItem(item: any, key: number): React.ReactNode {
    if (Array.isArray(item)) {
      return (
        <div
          key={key}
          className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4 w-full"
        >
          {item.map((subItem, i) => renderItem(subItem, i))}
        </div>
      );
    }

    const { type, data } = item as ComponentJSON;

    const processedData = Object.fromEntries(
      Object.entries(data || {}).map(([k, v]) => {
        if (v && typeof v === "object" && "type" in v) {
          return [k, renderItem(v, 0)];
        }
        if (Array.isArray(v)) {
          return [
            k,
            v.map((el, i) =>
              el && typeof el === "object" && "type" in el
                ? renderItem(el, i)
                : el,
            ),
          ];
        }
        return [k, v];
      }),
    );

    const Component = componentMap[type];
    if (!Component) {
      return <div key={key}>Unknown: {type}</div>;
    }

    return <Component key={key} {...processedData} onCallback={onCallback} />;
  }

  const parsed =
    typeof agentJSON === "string" ? JSON.parse(agentJSON) : agentJSON;
  return Array.isArray(parsed) ? (
    <div className="space-y-6">
      {parsed.map((item, i) => renderItem(item, i))}
    </div>
  ) : (
    renderItem(parsed, 0)
  );
}

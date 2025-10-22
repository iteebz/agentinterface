import React from "react";
import { render as rtlRender, screen, fireEvent } from "@testing-library/react";
import { describe, it, expect, vi } from "vitest";
import { render } from "../src/renderer";

function mount(node: React.ReactNode) {
  return rtlRender(<>{node}</>);
}

describe("render()", () => {
  it("surfaces unknown component types visibly", () => {
    const node = render(JSON.stringify({ type: "does-not-exist", data: {} }));
    mount(node);
    expect(screen.getByText("Unknown: does-not-exist")).toBeInTheDocument();
  });

  it("passes callbacks down to rendered components", () => {
    const onCallback = vi.fn();
    const node = render(
      JSON.stringify({ type: "card", data: { title: "Quarterly update" } }),
      undefined,
      onCallback,
    );

    mount(node);
    fireEvent.click(screen.getByText("Quarterly update"));

    expect(onCallback).toHaveBeenCalledTimes(1);
    expect(onCallback.mock.calls[0][0]).toMatchObject({
      type: "click",
      component: "card",
    });
  });

  it("respects custom component overrides", () => {
    const Custom = vi.fn(() => <div>custom component</div>);
    const node = render(JSON.stringify({ type: "card", data: {} }), {
      card: Custom,
    });

    mount(node);
    expect(screen.getByText("custom component")).toBeInTheDocument();
    expect(Custom).toHaveBeenCalled();
  });

  it("renders nested component structures recursively", () => {
    const node = render({
      type: "card",
      data: {
        title: "Sales summary",
        content: {
          type: "table",
          data: {
            title: "By region",
            attributes: [
              { key: "revenue", label: "Revenue" },
              { key: "growth", label: "Growth" },
            ],
            items: [
              {
                id: "na",
                name: "North America",
                attributes: { revenue: "$1.2M", growth: "+12%" },
              },
            ],
          },
        },
      },
    });

    mount(node);
    expect(screen.getByText("Sales summary")).toBeInTheDocument();
    expect(screen.getByText("By region")).toBeInTheDocument();
    expect(screen.getByText("North America")).toBeInTheDocument();
    expect(screen.getByText("$1.2M")).toBeInTheDocument();
  });

  it("creates layout wrappers for array compositions", () => {
    const node = render(
      JSON.stringify([
        { type: "card", data: { title: "Top card" } },
        [
          { type: "card", data: { title: "Left" } },
          { type: "card", data: { title: "Right" } },
        ],
        { type: "card", data: { title: "Bottom card" } },
      ]),
    );

    mount(node);
    const verticalStack = document.querySelector(".space-y-6");
    const gridRow = document.querySelector(".grid");

    expect(verticalStack).not.toBeNull();
    expect(gridRow).not.toBeNull();
    expect(screen.getByText("Bottom card")).toBeInTheDocument();
    expect(screen.getByText("Left")).toBeInTheDocument();
  });

  it("accepts already parsed component arrays", () => {
    const node = render([
      { type: "card", data: { title: "Parsed" } },
      { type: "markdown", data: { content: "Structured" } },
    ]);

    mount(node);
    expect(screen.getByText("Parsed")).toBeInTheDocument();
    expect(screen.getByText("Structured")).toBeInTheDocument();
  });
});

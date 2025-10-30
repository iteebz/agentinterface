import React from "react";
import { render, screen, act } from "@testing-library/react";
import { describe, it, expect } from "vitest";
import { AgentCanvas, AgentCanvasRef } from "../src/canvas";

describe("AgentCanvas", () => {
  it("accepts structured component data via ref", () => {
    const ref = React.createRef<AgentCanvasRef>();
    render(<AgentCanvas ref={ref} />);

    act(() => {
      ref.current?.addResponse({
        type: "card",
        data: { title: "Structured", content: "Inline" },
      });
    });

    expect(screen.getByText("Structured")).toBeInTheDocument();
    expect(screen.getByText("Inline")).toBeInTheDocument();
  });

  it("parses legacy JSON string responses", () => {
    const ref = React.createRef<AgentCanvasRef>();
    render(<AgentCanvas ref={ref} />);

    act(() => {
      ref.current?.addResponse(
        JSON.stringify({
          type: "card",
          data: { title: "Stringified" },
        }),
      );
    });

    expect(screen.getByText("Stringified")).toBeInTheDocument();
  });
});

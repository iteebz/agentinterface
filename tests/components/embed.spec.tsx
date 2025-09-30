import React from "react";
import { render, screen } from "@testing-library/react";
import { describe, it, expect, vi } from "vitest";
import { Embed } from "../../src/ai/embed";

describe("Embed", () => {
  it("renders iframe for safe http sources", () => {
    render(<Embed src="https://example.com/embed" title="Example" />);

    const iframe = screen.getByTitle("Example");
    expect(iframe).toBeInTheDocument();
    expect(iframe).toHaveAttribute("src", "https://example.com/embed");
  });

  it("blocks javascript urls and surfaces fallback message", () => {
    const warn = vi.spyOn(console, "warn").mockImplementation(() => {});

    render(<Embed src="javascript:alert('xss')" />);

    expect(screen.getByRole("alert")).toHaveTextContent(
      "blocked unsafe source",
    );
    expect(screen.queryByTitle("Embedded content")).not.toBeInTheDocument();

    warn.mockRestore();
  });
});

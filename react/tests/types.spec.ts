import { describe, it, expect } from "vitest";
import { formatLLM, type CallbackEvent } from "../src/types";

describe("formatLLM", () => {
  const baseEvent: CallbackEvent = {
    type: "click",
    component: "card",
    data: {},
  };

  it("maps all action types to readable phrases", () => {
    expect(formatLLM(baseEvent)).toBe("User clicked card");
    expect(formatLLM({ ...baseEvent, type: "change" })).toBe(
      "User changed card",
    );
    expect(formatLLM({ ...baseEvent, type: "select" })).toBe(
      "User selected card",
    );
    expect(formatLLM({ ...baseEvent, type: "toggle" })).toBe(
      "User toggled card",
    );
  });

  it("includes detail from data fields", () => {
    expect(formatLLM({ ...baseEvent, data: { title: "Revenue" } })).toBe(
      "User clicked card: Revenue",
    );
    expect(formatLLM({ ...baseEvent, data: { text: "Submit" } })).toBe(
      "User clicked card: Submit",
    );
    expect(formatLLM({ ...baseEvent, data: { id: "btn-123" } })).toBe(
      "User clicked card: btn-123",
    );
    expect(formatLLM({ ...baseEvent, data: { label: "Option A" } })).toBe(
      "User clicked card: Option A",
    );
  });

  it("falls back gracefully when no detail present", () => {
    const result = formatLLM({
      ...baseEvent,
      type: "toggle",
      component: "accordion",
    });
    expect(result).toBe("User toggled accordion");
  });
});

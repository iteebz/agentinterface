import { describe, expect, it, beforeEach, afterEach } from "vitest";
import fs from "node:fs";
import fsPromises from "node:fs/promises";
import os from "node:os";
import path from "node:path";

function writeFile(root: string, filePath: string, contents: string) {
  const absolutePath = path.join(root, filePath);
  fs.mkdirSync(path.dirname(absolutePath), { recursive: true });
  fs.writeFileSync(absolutePath, contents);
}

describe("autodiscovery CLI", () => {
  let tempRoot: string;

  beforeEach(() => {
    tempRoot = fs.mkdtempSync(
      path.join(os.tmpdir(), "agentinterface-autodiscovery-"),
    );
  });

  afterEach(async () => {
    await fsPromises.rm(tempRoot, { recursive: true, force: true });
  });

  it("extracts metadata from exports ending with Metadata", async () => {
    const { extractMetadata } = await import("../scripts/discover.mjs");
    const source = `
      import React from 'react';
      export const FancyMetadata = {
        type: 'fancy',
        description: 'Fancy component',
        category: 'demo',
        schema: { type: 'object' }
      };
      export const Fancy = () => <div />;
    `;

    const result = extractMetadata(
      source,
      path.join(tempRoot, "Fancy.tsx"),
      tempRoot,
    );
    expect(result).toMatchObject({
      type: "fancy",
      description: "Fancy component",
      category: "demo",
    });
  });

  it("generates ai.json without wrappers for consumer projects", async () => {
    const { runDiscovery } = await import("../scripts/discover.mjs");

    const pkgJson = {
      name: "demo-app",
      version: "1.0.0",
    };
    fs.writeFileSync(
      path.join(tempRoot, "package.json"),
      JSON.stringify(pkgJson),
    );

    writeFile(
      tempRoot,
      path.join("node_modules", "agentinterface", "src", "ai", "sample.tsx"),
      `import React from 'react';
       export const SampleMetadata = {
         type: 'sample-card',
         description: 'Sample card',
         category: 'sample',
         schema: { type: 'object', properties: { foo: { type: 'string' } } }
       };
       export const Sample = () => <div>Sample</div>;
      `,
    );

    writeFile(
      tempRoot,
      path.join("src", "components", "ai", "local.tsx"),
      `import React from 'react';
       export function Local() { return <div>Local</div>; }
       export const LocalMetadata = {
         type: 'local-card',
         description: 'Local card',
         category: 'local',
         schema: { type: 'object' }
       };
      `,
    );

    const registry = runDiscovery({ rootDir: tempRoot });

    const registryPath = path.join(tempRoot, "ai.json");
    expect(fs.existsSync(registryPath)).toBe(true);
    expect(fs.existsSync(path.join(tempRoot, "ai.tsx"))).toBe(false);

    const persisted = JSON.parse(fs.readFileSync(registryPath, "utf8"));
    expect(persisted.total_components).toBe(2);
    expect(Object.keys(persisted.components)).toEqual(
      expect.arrayContaining(["sample-card", "local-card"]),
    );
    expect(persisted.components["sample-card"].source).toBe("agentinterface");
    expect(persisted.components["local-card"].source).toBe("demo-app");
    expect(registry).toEqual(persisted);
  });
});

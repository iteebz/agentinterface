#!/usr/bin/env node
/**
 * Component autodiscovery for AgentInterface
 * Scans TSX files for metadata exports, generates ai.json registry
 */

import fs from 'fs';
import path from 'path';
import { fileURLToPath } from 'url';
import ts from 'typescript';

const __dirname = path.dirname(fileURLToPath(import.meta.url));

// Extract metadata from TypeScript AST node
function extractValue(node) {
  if (ts.isStringLiteral(node)) return node.text;
  if (ts.isNumericLiteral(node)) return parseFloat(node.text);
  if (node.kind === ts.SyntaxKind.TrueKeyword) return true;
  if (node.kind === ts.SyntaxKind.FalseKeyword) return false;
  
  if (ts.isArrayLiteralExpression(node)) {
    return node.elements
      .map(extractValue)
      .filter((value) => value !== undefined && value !== null);
  }
  
  if (ts.isObjectLiteralExpression(node)) {
    return Object.fromEntries(
      node.properties
        .filter(ts.isPropertyAssignment)
        .map(prop => {
          const key = ts.isIdentifier(prop.name) ? prop.name.text : 
                     ts.isStringLiteral(prop.name) ? prop.name.text : 'unknown';
          return [key, extractValue(prop.initializer)];
        })
    );
  }
  
  return null;
}

// Extract component metadata from TSX file
function extractMetadata(code, filepath, rootDir = process.cwd()) {
  const sourceFile = ts.createSourceFile(filepath, code, ts.ScriptTarget.Latest, true, ts.ScriptKind.TSX);
  let metadata = null;
  
  ts.forEachChild(sourceFile, function visit(node) {
    if (ts.isVariableStatement(node) && 
        node.modifiers?.some(mod => mod.kind === ts.SyntaxKind.ExportKeyword)) {
      
      const metadataDecl = node.declarationList.declarations.find(decl =>
        ts.isIdentifier(decl.name) && 
        (decl.name.text === 'metadata' || decl.name.text.endsWith('Metadata'))
      );
      
      if (metadataDecl?.initializer) {
        metadata = extractValue(metadataDecl.initializer);
      }
    }
    ts.forEachChild(node, visit);
  });
  
  return metadata ? {
    type: metadata.type,
    description: metadata.description,
    schema: metadata.schema,
    category: metadata.category || 'general',
    file: path.relative(rootDir, filepath)
  } : null;
}

// Find all TSX files in directory (recursive)
function findTsxFiles(dir, maxDepth = 3, currentDepth = 0) {
  if (currentDepth > maxDepth) return [];
  
  const results = [];
  const entries = fs.readdirSync(dir, { withFileTypes: true });
  
  for (const entry of entries) {
    const fullPath = path.join(dir, entry.name);
    if (entry.isDirectory() && !entry.name.startsWith('.') && !entry.name.includes('node_modules')) {
      results.push(...findTsxFiles(fullPath, maxDepth, currentDepth + 1));
    } else if (entry.isFile() && entry.name.endsWith('.tsx')) {
      results.push(fullPath);
    }
  }
  
  return results;
}

// Scan directory for components
function scanComponents(dirPath, source, { maxDepth = 1, rootDir = process.cwd() } = {}) {
  console.log(`Scanning ${source} components...`);
  const files = findTsxFiles(dirPath, maxDepth);
  const components = [];

  for (const file of files) {
    const code = fs.readFileSync(file, 'utf8');
    const metadata = extractMetadata(code, file, rootDir);
    if (metadata) {
      components.push({ ...metadata, source });
      console.log(`Found [${source}] ${metadata.type}: ${metadata.description}`);
    }
  }

  return components;
}

// Check if current project is AgentInterface itself
function isAgentInterfaceProject(rootDir = process.cwd()) {
  try {
    const packageJson = JSON.parse(fs.readFileSync(path.join(rootDir, 'package.json'), 'utf8'));
    return packageJson.name === 'agentinterface';
  } catch {
    return false;
  }
}

// Get project name from package.json
function getProjectName(rootDir = process.cwd()) {
  try {
    const packageJson = JSON.parse(fs.readFileSync(path.join(rootDir, 'package.json'), 'utf8'));
    return packageJson.name || path.basename(rootDir);
  } catch {
    return path.basename(rootDir);
  }
}

// Create ai.json registry
function createRegistry(components) {
  const sourceGroups = {};
  const componentsData = Object.fromEntries(
    components.map(comp => {
      if (!sourceGroups[comp.source]) sourceGroups[comp.source] = [];
      sourceGroups[comp.source].push(comp.type);
      
      return [comp.type, {
        description: comp.description,
        schema: comp.schema,
        category: comp.category,
        file: comp.file,
        source: comp.source
      }];
    })
  );
  
  return {
    generated_at: new Date().toISOString(),
    version: "1.0.0",
    total_components: components.length,
    components: componentsData,
    sources: sourceGroups
  };
}

// Main discovery process
function runDiscovery({ rootDir = process.cwd() } = {}) {
  console.log('AUTODISCOVERY: Finding AI components');

  let allComponents = [];

  if (isAgentInterfaceProject(rootDir)) {
    // AgentInterface project - scan core components only
    console.log('Detected AgentInterface project');
    const coreDir = path.join(__dirname, '../src/ai');
    allComponents = scanComponents(coreDir, 'agentinterface', { rootDir });
  } else {
    // Consumer project - scan core + project components
    const projectName = getProjectName(rootDir);
    console.log(`Detected project: ${projectName}`);

    // Core components from node_modules
    const agentInterfacePath = path.join(rootDir, 'node_modules/agentinterface/src/ai');
    const coreComponents = fs.existsSync(agentInterfacePath) ? 
      scanComponents(agentInterfacePath, 'agentinterface', { rootDir }) : [];

    // Project components
    const projectComponents = [];
    const paths = ['src/components/ai', 'components/ai', 'web/src/components/ai', 'app/components/ai'];

    for (const relativePath of paths) {
      const fullPath = path.join(rootDir, relativePath);
      if (fs.existsSync(fullPath)) {
        console.log(`Found components at: ${relativePath}`);
        projectComponents.push(...scanComponents(fullPath, projectName, { rootDir, maxDepth: 2 }));
      }
    }

    allComponents = [...coreComponents, ...projectComponents];
  }

  if (allComponents.length === 0) {
    console.log('No components found with metadata exports!');
    console.log('Ensure components export metadata = { type, description, schema, category }');
    throw new Error('No components with metadata exports discovered');
  }

  // Generate registry
  const registry = createRegistry(allComponents);
  fs.writeFileSync(path.join(rootDir, 'ai.json'), JSON.stringify(registry, null, 2));

  // Summary
  const types = allComponents.map(c => c.type).sort();
  const sources = [...new Set(allComponents.map(c => c.source))];

  console.log('\nAUTODISCOVERY COMPLETE');
  console.log(`Found ${allComponents.length} components from ${sources.length} sources`);
  console.log(`Component types: ${types.join(', ')}`);
  console.log('Ready for use with protocol() and render()');

  return registry;
}

function main() {
  try {
    runDiscovery();
  } catch (error) {
    const message = error && error.message ? error.message : error;
    console.error(message);
    process.exitCode = 1;
  }
}

// Run if called directly
if (import.meta.url === `file://${process.argv[1]}`) {
  main();
}

export { extractMetadata, findTsxFiles, scanComponents, createRegistry, runDiscovery, main };

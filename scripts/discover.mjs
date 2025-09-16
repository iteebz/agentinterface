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
    return node.elements.map(extractValue).filter(Boolean);
  }
  
  if (ts.isObjectLiteralExpression(node)) {
    const obj = {};
    for (const property of node.properties) {
      if (ts.isPropertyAssignment(property)) {
        const key = ts.isIdentifier(property.name) ? property.name.text : 
                   ts.isStringLiteral(property.name) ? property.name.text : 'unknown';
        obj[key] = extractValue(property.initializer);
      }
    }
    return obj;
  }
  
  return null;
}

// Extract component metadata from TSX file
function extractMetadata(code, filepath) {
  const sourceFile = ts.createSourceFile(filepath, code, ts.ScriptTarget.Latest, true, ts.ScriptKind.TSX);
  
  let metadata = null;
  
  function visit(node) {
    if (ts.isVariableStatement(node) && 
        node.modifiers?.some(mod => mod.kind === ts.SyntaxKind.ExportKeyword)) {
      
      for (const declaration of node.declarationList.declarations) {
        if (ts.isIdentifier(declaration.name) && 
            (declaration.name.text === 'metadata' || declaration.name.text.endsWith('Metadata'))) {
          
          if (declaration.initializer) {
            metadata = extractValue(declaration.initializer);
          }
        }
      }
    }
    ts.forEachChild(node, visit);
  }
  
  visit(sourceFile);
  
  if (!metadata) return null;
  
  return {
    type: metadata.type,
    description: metadata.description,
    schema: metadata.schema,
    category: metadata.category || 'general',
    file: path.relative(process.cwd(), filepath)
  };
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
function scanComponents(dirPath, source, maxDepth = 1) {
  console.log(`Scanning ${source} components...`);
  const files = findTsxFiles(dirPath, maxDepth);
  const components = [];
  
  for (const file of files) {
    const code = fs.readFileSync(file, 'utf8');
    const metadata = extractMetadata(code, file);
    if (metadata) {
      components.push({ ...metadata, source });
      console.log(`Found [${source}] ${metadata.type}: ${metadata.description}`);
    }
  }
  
  return components;
}

// Check if current project is AgentInterface itself
function isAgentInterfaceProject() {
  try {
    const packageJson = JSON.parse(fs.readFileSync('package.json', 'utf8'));
    return packageJson.name === 'agentinterface';
  } catch {
    return false;
  }
}

// Get project name from package.json
function getProjectName() {
  try {
    const packageJson = JSON.parse(fs.readFileSync('package.json', 'utf8'));
    return packageJson.name || path.basename(process.cwd());
  } catch {
    return path.basename(process.cwd());
  }
}

// Create ai.json registry
function createRegistry(components) {
  const registry = {
    generated_at: new Date().toISOString(),
    version: "1.0.0",
    total_components: components.length,
    components: {},
    sources: {}
  };
  
  const sourceGroups = {};
  for (const comp of components) {
    registry.components[comp.type] = {
      description: comp.description,
      schema: comp.schema,
      category: comp.category,
      file: comp.file,
      source: comp.source
    };
    
    if (!sourceGroups[comp.source]) sourceGroups[comp.source] = [];
    sourceGroups[comp.source].push(comp.type);
  }
  
  registry.sources = sourceGroups;
  return registry;
}

// Create ai.tsx wrapper
function createWrapper(components) {
  const imports = [];
  const componentEntries = [];
  
  const toPascalCase = (str) => {
    return str.split(/[-_]/).map(word => 
      word.charAt(0).toUpperCase() + word.slice(1).toLowerCase()
    ).join('');
  };
  
  for (const comp of components) {
    const componentName = toPascalCase(comp.type);
    let importPath = comp.file.replace(/\.tsx?$/, '');
    
    if (importPath.startsWith('node_modules/agentinterface/src/')) {
      importPath = importPath.replace('node_modules/', '');
    } else if (importPath.startsWith('src/')) {
      importPath = './' + importPath.substring(4);
    }
    
    imports.push(`import { ${componentName} } from '${importPath}';`);
    componentEntries.push(`  '${comp.type}': ${componentName},`);
  }
  return null; // No wrapper needed
}

// Main discovery process
function main() {
  console.log('AUTODISCOVERY: Finding AI components');
  
  let allComponents = [];
  
  if (isAgentInterfaceProject()) {
    // AgentInterface project - scan core components only
    console.log('Detected AgentInterface project');
    const coreDir = path.join(__dirname, '../src/ai');
    allComponents = scanComponents(coreDir, 'agentinterface');
  } else {
    // Consumer project - scan core + project components
    console.log(`Detected project: ${getProjectName()}`);
    
    // Core components from node_modules
    const agentInterfacePath = path.join(process.cwd(), 'node_modules/agentinterface/src/ai');
    const coreComponents = fs.existsSync(agentInterfacePath) ? 
      scanComponents(agentInterfacePath, 'agentinterface') : [];
    
    // Project components
    const projectComponents = [];
    const paths = ['src/components/ai', 'components/ai', 'web/src/components/ai', 'app/components/ai'];
    
    for (const relativePath of paths) {
      const fullPath = path.join(process.cwd(), relativePath);
      if (fs.existsSync(fullPath)) {
        console.log(`Found components at: ${relativePath}`);
        projectComponents.push(...scanComponents(fullPath, getProjectName(), 2));
      }
    }
    
    allComponents = [...coreComponents, ...projectComponents];
  }
  
  if (allComponents.length === 0) {
    console.log('No components found with metadata exports!');
    console.log('Ensure components export metadata = { type, description, schema, category }');
    process.exit(1);
  }
  
  // Generate registry
  const registry = createRegistry(allComponents);
  fs.writeFileSync('ai.json', JSON.stringify(registry, null, 2));
  
  // Summary
  const types = allComponents.map(c => c.type).sort();
  const sources = [...new Set(allComponents.map(c => c.source))];
  
  console.log('\nAUTODISCOVERY COMPLETE');
  console.log(`Found ${allComponents.length} components from ${sources.length} sources`);
  console.log(`Component types: ${types.join(', ')}`);
  console.log('Ready for use with protocol() and render()');
}

// Run if called directly
if (import.meta.url === `file://${process.argv[1]}`) {
  main();
}

export { extractMetadata, findTsxFiles, scanComponents, createRegistry, createWrapper, main };
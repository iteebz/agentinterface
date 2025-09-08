#!/usr/bin/env node
/**
 * AUTODISCOVERY - Universal component scanner for AgentInterface
 * 
 * Scans TypeScript files for component metadata exports
 * Generates ai.json registry and ai.tsx wrapper
 */

import fs from 'fs';
import path from 'path';
import { fileURLToPath } from 'url';
import { parse } from '@babel/parser';
import traverse from '@babel/traverse';
import * as t from '@babel/types';

// Setup
const traverseDefault = traverse.default || traverse;
const __filename = fileURLToPath(import.meta.url);
const __dirname = path.dirname(__filename);

/**
 * AST Parser - Extracts component metadata from TSX files
 */
const Parser = {
  /**
   * Extract metadata from TSX file
   */
  extract(code, filepath) {
    try {
      const ast = parse(code, { sourceType: 'module', plugins: ['jsx', 'typescript'] });
      let metadata = null;
      
      // Find exported metadata variable
      traverseDefault(ast, {
        ExportNamedDeclaration(path) {
          const declaration = path.node.declaration;
          if (t.isVariableDeclaration(declaration)) {
            const declarator = declaration.declarations[0];
            if (t.isIdentifier(declarator.id) && declarator.id.name === 'metadata') {
              metadata = Parser.extractValue(declarator.init);
            }
          }
        }
      });
      
      if (!metadata) return null;
      
      return {
        type: metadata.type,
        description: metadata.description,
        schema: metadata.schema,
        category: metadata.category || 'general',
        file: path.relative(process.cwd(), filepath)
      };
    } catch (error) {
      console.warn(`Failed to parse metadata in ${filepath}: ${error.message}`);
      return null;
    }
  },
  
  /**
   * Extract values from AST nodes recursively
   */
  extractValue(node) {
    if (t.isStringLiteral(node)) return node.value;
    if (t.isTemplateLiteral(node)) return node.quasis[0]?.value?.cooked || '';
    if (t.isNumericLiteral(node) || t.isBooleanLiteral(node)) return node.value;
    if (t.isArrayExpression(node)) return node.elements.map(this.extractValue).filter(Boolean);
    if (t.isObjectExpression(node)) {
      const obj = {};
      for (const prop of node.properties) {
        if (t.isObjectProperty(prop)) {
          const key = t.isIdentifier(prop.key) ? prop.key.name : prop.key.value;
          obj[key] = this.extractValue(prop.value);
        }
      }
      return obj;
    }
    return null;
  }
};

/**
 * FileSystem - Handles file operations and discovery
 */
const FileSystem = {
  /**
   * Find all TSX files in a directory recursively
   */
  findTsxFiles(dir, maxDepth = 3, currentDepth = 0) {
    if (currentDepth > maxDepth) return [];
    const results = [];
    
    try {
      const entries = fs.readdirSync(dir, { withFileTypes: true });
      for (const entry of entries) {
        const fullPath = path.join(dir, entry.name);
        if (entry.isDirectory() && !entry.name.startsWith('.') && !entry.name.includes('node_modules')) {
          results.push(...this.findTsxFiles(fullPath, maxDepth, currentDepth + 1));
        } else if (entry.isFile() && entry.name.endsWith('.tsx')) {
          results.push(fullPath);
        }
      }
    } catch (error) { /* Skip inaccessible directories */ }
    
    return results;
  },
  
  /**
   * Get project name from package.json or directory
   */
  getProjectName(cwd) {
    try {
      const packageJsonPath = path.join(cwd, 'package.json');
      if (fs.existsSync(packageJsonPath)) {
        const packageJson = JSON.parse(fs.readFileSync(packageJsonPath, 'utf8'));
        return packageJson.name || path.basename(cwd);
      }
    } catch (error) { /* Fall back to directory name */ }
    return path.basename(cwd);
  },
  
  /**
   * Check if running from AgentInterface itself
   */
  isAgentInterfaceProject(cwd) {
    const packageJsonPath = path.join(cwd, 'package.json');
    if (fs.existsSync(packageJsonPath)) {
      try {
        const packageJson = JSON.parse(fs.readFileSync(packageJsonPath, 'utf8'));
        return packageJson.name === 'agentinterface';
      } catch (error) { return false; }
    }
    return false;
  }
};

/**
 * ComponentScanner - Discovers components across different locations
 */
const ComponentScanner = {
  /**
   * Scan a specific directory for components
   */
  scan(dirPath, source, maxDepth = 1) {
    console.log(`Scanning ${source} components...`);
    const files = FileSystem.findTsxFiles(dirPath, maxDepth);
    const components = [];
    
    for (const file of files) {
      const code = fs.readFileSync(file, 'utf8');
      const metadata = Parser.extract(code, file);
      if (metadata) {
        components.push({ ...metadata, source });
        console.log(`Found [${source}] ${metadata.type}: ${metadata.description}`);
      }
    }
    
    return components;
  },
  
  /**
   * Scan core AgentInterface components
   */
  scanCore() {
    const coreDir = path.join(__dirname, '../src/ai');
    return this.scan(coreDir, 'agentinterface');
  },
  
  /**
   * Scan current project for components
   */
  scanProject() {
    const results = [];
    const cwd = process.cwd();
    const projectName = FileSystem.getProjectName(cwd);
    
    // Common locations for components
    const paths = ['src/components/ai', 'components/ai', 'web/src/components/ai', 'app/components/ai'];
    
    for (const relativePath of paths) {
      const fullPath = path.join(cwd, relativePath);
      if (fs.existsSync(fullPath)) {
        console.log(`Found components at: ${relativePath}`);
        results.push(...this.scan(fullPath, projectName, 2));
      }
    }
    return results;
  },
  
  /**
   * Scan node_modules for ecosystem components
   */
  scanEcosystem() {
    const results = [];
    const nodeModules = path.join(process.cwd(), 'node_modules');
    if (!fs.existsSync(nodeModules)) return results;
    
    try {
      // Check top packages only (reasonable limit)
      const packages = fs.readdirSync(nodeModules, { withFileTypes: true })
        .filter(d => d.isDirectory() && !d.name.startsWith('.'))
        .slice(0, 20);
        
      for (const pkg of packages) {
        const stdPath = path.join(nodeModules, pkg.name, 'src/components/ai');
        const altPath = path.join(nodeModules, pkg.name, 'src/ai'); // agentinterface pattern
        
        if (fs.existsSync(stdPath)) {
          results.push(...this.scan(stdPath, pkg.name, 2));
        } else if (fs.existsSync(altPath)) {
          results.push(...this.scan(altPath, pkg.name, 1));
        }
      }
    } catch (error) { /* Skip if inaccessible */ }
    
    return results;
  }
};



/**
 * Generator - Creates output files from component data
 */
const Generator = {
  /**
   * Create ai.json registry
   */
  createRegistry(components) {
    const registry = {
      generated_at: new Date().toISOString(),
      version: "1.0.0",
      total_components: components.length,
      components: {},
      sources: {}
    };
    
    // Group by source
    const sourceGroups = {};
    for (const comp of components) {
      // Add to registry
      registry.components[comp.type] = {
        description: comp.description,
        schema: comp.schema,
        category: comp.category,
        file: comp.file,
        source: comp.source
      };
      
      // Track sources
      if (!sourceGroups[comp.source]) sourceGroups[comp.source] = [];
      sourceGroups[comp.source].push(comp.type);
    }
    
    registry.sources = sourceGroups;
    return registry;
  },
  
  /**
   * Create ai.tsx wrapper with component imports
   */
  createWrapper(components) {
    const imports = [];
    const componentEntries = [];
    
    // Convert kebab-case to PascalCase
    const toPascalCase = (str) => {
      return str
        .split(/[-_]/)
        .map(word => word.charAt(0).toUpperCase() + word.slice(1).toLowerCase())
        .join('');
    };
    
    for (const comp of components) {
      const componentName = toPascalCase(comp.type);
      let importPath = comp.file.replace(/\.tsx?$/, '');
      
      // Handle import paths
      if (importPath.startsWith('node_modules/agentinterface/src/')) {
        importPath = importPath.replace('node_modules/', '');
      } else if (importPath.startsWith('src/')) {
        importPath = './' + importPath.substring(4);
      }
      
      imports.push(`import { ${componentName} } from '${importPath}';`);
      componentEntries.push(`  '${comp.type}': ${componentName},`);
    }
    
    return `/**
 * Auto-generated AI interface - DO NOT EDIT
 * Generated by discover.mjs at ${new Date().toISOString()}
 */

import React from 'react';
import { renderWithComponents } from './src/renderer';
${imports.join('\n')}

const COMPONENTS = {
${componentEntries.join('\n')}
} as const;

export function render(agentJSON: string): React.ReactNode {
  return renderWithComponents(agentJSON, COMPONENTS);
}

export default { render };
`;
  }
};

// Removed - we use generateAIWrapper instead

// LLM instructions now generated dynamically by protocol() function - removed


/**
 * Main discovery process
 */
function main() {
  console.log('AUTODISCOVERY: Finding AI components');
  
  const cwd = process.cwd();
  let allComponents = [];
  
  if (FileSystem.isAgentInterfaceProject(cwd)) {
    // Running from AgentInterface itself - only scan core components
    console.log('Detected AgentInterface project');
    allComponents = ComponentScanner.scanCore();
  } else {
    // Running from a consuming project
    console.log(`Detected project: ${FileSystem.getProjectName(cwd)}`);
    
    // Try to find AgentInterface components in node_modules
    const agentInterfacePath = path.join(cwd, 'node_modules/agentinterface/src/ai');
    const coreComponents = fs.existsSync(agentInterfacePath) ? 
      ComponentScanner.scan(agentInterfacePath, 'agentinterface') : [];
    
    // Add project and ecosystem components
    allComponents = [
      ...coreComponents,
      ...ComponentScanner.scanProject(),
      ...ComponentScanner.scanEcosystem()
    ];
  }
  
  if (allComponents.length === 0) {
    console.log('No components found with metadata exports!');
    console.log('Ensure components export metadata = { type, description, schema, category }');
    process.exit(1);
  }
  
  // Generate ai.json registry and ai.tsx wrapper
  const registry = Generator.createRegistry(allComponents);
  const aiWrapper = Generator.createWrapper(allComponents);
  
  // Write output files
  const registryPath = path.join(cwd, 'ai.json');
  const wrapperPath = path.join(cwd, 'ai.tsx');
  fs.writeFileSync(registryPath, JSON.stringify(registry, null, 2));
  fs.writeFileSync(wrapperPath, aiWrapper);
  
  // Show summary
  const types = allComponents.map(c => c.type).sort();
  const sources = [...new Set(allComponents.map(c => c.source))]; // Unique sources
  
  console.log('\nAUTODISCOVERY COMPLETE');
  console.log(`Found ${allComponents.length} components from ${sources.length} sources`);
  console.log(`Component types: ${types.join(', ')}`);
  console.log('Ready for use with protocol() and render()');
}

// Run if called directly
if (import.meta.url === `file://${process.argv[1]}`) {
  main();
}

// Export public API
export { Parser, FileSystem, ComponentScanner, Generator, main };
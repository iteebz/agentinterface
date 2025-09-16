#!/usr/bin/env node
/**
 * Minimal test for autodiscovery functionality
 * Tests the core discovery pipeline end-to-end
 */

/* eslint-disable no-undef */

import { execSync } from 'child_process';
import fs from 'fs';
import path from 'path';

console.log('🧪 Testing AgentInterface Autodiscovery...');

// Test 1: Discovery command runs without error
console.log('1. Testing discovery command...');
try {
  const output = execSync('npx agentinterface discover', { encoding: 'utf8' });
  console.log('   ✅ Discovery command executed successfully');
  
  if (output.includes('AUTODISCOVERY COMPLETE')) {
    console.log('   ✅ Discovery completed successfully');
  } else {
    throw new Error('Discovery did not complete successfully');
  }
} catch (error) {
  console.error('   ❌ Discovery command failed:', error.message);
  process.exit(1);
}

// Test 2: Registry generation
console.log('2. Testing registry generation...');
const registryPath = path.join(process.cwd(), 'ai.json');

if (fs.existsSync(registryPath)) {
  console.log('   ✅ Registry file (ai.json) exists');
  
  // Validate registry
try {
    const registry = JSON.parse(fs.readFileSync(registryPath, 'utf8'));
    
    // Validate registry structure
    if (registry.components && registry.sources && registry.total_components) {
      console.log('   ✅ Registry has correct structure');
      console.log(`   📊 Found ${registry.total_components} components`);
      
      // Check for core components
      const coreComponents = ['card', 'markdown', 'table', 'accordion'];
      const missingComponents = coreComponents.filter(comp => !registry.components[comp]);
      
      if (missingComponents.length === 0) {
        console.log('   ✅ All core components found');
      } else {
        console.error('   ❌ Missing core components:', missingComponents);
        process.exit(1);
      }
    } else {
      console.error('   ❌ Registry structure is invalid');
      process.exit(1);
    }
  } catch (error) {
    console.error('   ❌ Registry JSON is invalid:', error.message);
    process.exit(1);
  }
} else {
  console.error('   ❌ Registry file (ai.json) was not generated');
  process.exit(1);
}

// Test 3: Component metadata validation
console.log('3. Testing component metadata...');
const registry = JSON.parse(fs.readFileSync(registryPath, 'utf8'));

let metadataValid = true;
for (const [componentName, component] of Object.entries(registry.components)) {
  if (!component.description || !component.schema || !component.category) {
    console.error(`   ❌ Component ${componentName} missing required metadata`);
    metadataValid = false;
  }
}

if (metadataValid) {
  console.log('   ✅ All component metadata is valid');
} else {
  process.exit(1);
}

console.log('\n🎉 All autodiscovery tests passed!');
console.log('🚀 AgentInterface is ready for v1.0.0');
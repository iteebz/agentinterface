#!/usr/bin/env node
/**
 * Test discovery script generates ai.json only (no wrapper generation)
 */

/* eslint-disable no-undef */

import { execSync } from 'child_process';
import fs from 'fs';
import path from 'path';
import { fileURLToPath } from 'url';

const __dirname = path.dirname(fileURLToPath(import.meta.url));

function testDiscoveryScript() {
  const testDir = path.join(__dirname, '..', 'test-discovery');
  const aiJsonPath = path.join(testDir, 'ai.json');
  const aiTsxPath = path.join(testDir, 'ai.tsx');
  
  console.log('🧪 Testing discovery script (ai.json only)...');
  
  // Clean test directory
  if (fs.existsSync(testDir)) {
    fs.rmSync(testDir, { recursive: true });
  }
  fs.mkdirSync(testDir, { recursive: true });
  
  // Create test component
  const testComponentDir = path.join(testDir, 'src', 'ai');
  fs.mkdirSync(testComponentDir, { recursive: true });
  
  const testComponent = `
import React from 'react';

export const TestCard = ({ title, content }) => (
  <div>{title}: {content}</div>
);

export const metadata = {
  type: 'testcard',
  description: 'Test card component',
  schema: {
    type: 'object',
    properties: {
      title: { type: 'string' },
      content: { type: 'string' }
    },
    required: ['title']
  },
  category: 'test'
};
`;
  
  fs.writeFileSync(path.join(testComponentDir, 'testcard.tsx'), testComponent);

  try {
    // Run discovery script
    execSync(`cd ${testDir} && node ${path.join(__dirname, '..', 'scripts', 'discover.mjs')}`, {
      stdio: 'inherit'
    });
    
    // Should generate ai.json
    if (!fs.existsSync(aiJsonPath)) {
      throw new Error('ai.json was not generated');
    }
    console.log('   ✅ ai.json generated');
    
    // Should NOT generate ai.tsx wrapper
    if (fs.existsSync(aiTsxPath)) {
      throw new Error('ai.tsx wrapper should not be generated');
    }
    console.log('   ✅ No wrapper file generated');
    
    // Verify ai.json content
    const registry = JSON.parse(fs.readFileSync(aiJsonPath, 'utf8'));
    if (!registry.components.testcard) {
      throw new Error('testcard component not found in registry');
    }
    console.log('   ✅ Component metadata correctly extracted');
    
    // Test main project discovery
    execSync('cd /Users/teebz/dev/space/agentinterface && node scripts/discover.mjs', {
      stdio: 'inherit'
    });
    
    const registryPath = '/Users/teebz/dev/space/agentinterface/ai.json';
    const mainRegistry = JSON.parse(fs.readFileSync(registryPath, 'utf8'));
    
    if (mainRegistry.total_components !== 10) {
      throw new Error(`Expected 10 components, found ${mainRegistry.total_components}`);
    }
    console.log('   ✅ Main project discovery found 10 components');
    
  } catch (error) {
    console.error('   ❌ Discovery test failed:', error.message);
    process.exit(1);
  } finally {
    // Cleanup
    if (fs.existsSync(testDir)) {
      fs.rmSync(testDir, { recursive: true });
    }
  }
}

testDiscoveryScript();
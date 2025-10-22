#!/usr/bin/env node
/**
 * AgentInterface CLI
 * 
 * Universal command-line interface for AgentInterface operations
 */

import { main as discover } from '../scripts/discover.mjs';

const command = process.argv[2];

if (!command || command === 'help' || command === '--help' || command === '-h') {
  showHelp();
  process.exit(0);
}

switch (command) {
  case 'discover':
    discover();
    break;

  default:
    console.log(`Unknown command: ${command}`);
    showHelp();
    process.exit(1);
}

function showHelp() {
  console.log('AgentInterface CLI\n');
  console.log('COMMANDS:');
  console.log('  discover    Generate component registry');
  console.log('  help        Show help');
}
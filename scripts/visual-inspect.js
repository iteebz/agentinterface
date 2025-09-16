#!/usr/bin/env node
/**
 * Visual Inspection Tool - Manual styling validation
 * Not a test - a developer tool for component styling review
 */

import puppeteer from 'puppeteer';
import fs from 'fs';
import path from 'path';
import { fileURLToPath } from 'url';

const __dirname = path.dirname(fileURLToPath(import.meta.url));

async function visualInspection() {
  console.log('🎨 Visual Component Inspection Tool');
  
  const browser = await puppeteer.launch({ 
    headless: false,
    devtools: true 
  });
  
  const page = await browser.newPage();
  await page.setViewport({ width: 1200, height: 800 });
  
  // Load component showcase
  const showcasePath = path.join(__dirname, '../showcase.html');
  if (fs.existsSync(showcasePath)) {
    await page.goto(`file://${showcasePath}`);
    console.log('📄 Loaded component showcase');
  } else {
    console.log('❌ showcase.html not found - create one for visual inspection');
    await browser.close();
    return;
  }
  
  // Take screenshots for comparison
  const screenshotDir = path.join(__dirname, '../screenshots');
  if (!fs.existsSync(screenshotDir)) {
    fs.mkdirSync(screenshotDir, { recursive: true });
  }
  
  // Full page screenshot
  await page.screenshot({ 
    path: path.join(screenshotDir, 'showcase-full.png'),
    fullPage: true 
  });
  console.log('📸 Full page screenshot saved');
  
  // Dark mode if available
  await page.evaluate(() => {
    document.documentElement.classList.toggle('dark');
  });
  await page.screenshot({ 
    path: path.join(screenshotDir, 'showcase-dark.png'),
    fullPage: true 
  });
  console.log('📸 Dark mode screenshot saved');
  
  console.log('\n🔍 Browser left open for manual inspection');
  console.log('📁 Screenshots saved to scripts/screenshots/');
  console.log('🎯 Use for: styling review, responsive testing, visual regression comparison');
  console.log('\nPress Ctrl+C when done inspecting');
  
  // Keep browser open for manual inspection
  return new Promise(() => {});
}

// Run if called directly
if (import.meta.url === `file://${process.argv[1]}`) {
  visualInspection().catch(console.error);
}

export { visualInspection };
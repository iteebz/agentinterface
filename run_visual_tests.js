#!/usr/bin/env node

/**
 * Simple runner for visual validation tests
 * Usage: node run_visual_tests.js
 */

const { validateComponents } = require('./tests/visual_validation.js');

console.log('🚀 Running AgentInterface Visual Validation');
console.log('This will open a browser and take screenshots of all components');
console.log('Make sure you have puppeteer installed: npm install puppeteer');
console.log();

validateComponents()
    .then(result => {
        if (result.success) {
            console.log();
            console.log('🎉 SUCCESS! All components look beautiful');
            console.log(`📸 Screenshots saved in tests/screenshots/`);
            console.log('✨ Reference grade styling confirmed');
        } else {
            console.error('❌ Visual validation failed:', result.error);
            process.exit(1);
        }
    })
    .catch(error => {
        console.error('💥 Error running visual tests:', error.message);
        console.log();
        console.log('💡 Make sure you have puppeteer installed:');
        console.log('   npm install puppeteer');
        process.exit(1);
    });
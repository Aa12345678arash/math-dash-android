import fs from 'node:fs';
import assert from 'node:assert/strict';

const html = fs.readFileSync(new URL('../index.html', import.meta.url), 'utf8');
const scripts = [...html.matchAll(/<script>([\s\S]*?)<\/script>/g)];
assert.ok(scripts.length, 'Main application script must exist');
const appScript = scripts.at(-1)[1];
assert.doesNotThrow(() => new Function(appScript), 'Application JavaScript must parse');

const ids = new Set([...html.matchAll(/\bid="([^"]+)"/g)].map(m => m[1]));
const referenced = [...appScript.matchAll(/\$\('([^']+)'\)/g)].map(m => m[1]);
for (const id of referenced) assert.ok(ids.has(id), 'Missing DOM element: ' + id);

for (const id of ['start', 'duration', 'time', 'pauseBtn', 'quit', 'again', 'leaderBtn']) {
  assert.ok(ids.has(id), 'Required control missing: ' + id);
}
for (const value of ['60', '120', '180']) {
  assert.ok(html.includes('option value="' + value + '"'), 'Missing duration option: ' + value);
}
assert.match(appScript, /deadline=Date\.now\(\)\+state\.remainingMs/, 'Timer must use a finite deadline');
assert.match(appScript, /Math\.max\(0,Math\.ceil\(\(state\.deadline-Date\.now\(\)\)\/1000\)\)/, 'Timer must clamp at zero');
assert.match(appScript, /function pauseToggle\(/, 'Pause/resume control must exist');
assert.match(appScript, /state\.score\+=10\+bonus/, 'Correct-answer score must include speed bonus');
assert.match(appScript, /state\.questionStartedAt=Date\.now\(\)/, 'Each question must start its own response timer');

console.log('MATH DASH release checks passed.');

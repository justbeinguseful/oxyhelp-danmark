'use strict';

const { spawnSync } = require('node:child_process');
const fs = require('node:fs');
const os = require('node:os');
const path = require('node:path');

module.exports = {
  onPostBuild({ constants, netlifyConfig, utils }) {
    const repositoryRoot = path.resolve(__dirname, '../..');
    let temporaryDirectory;
    let failure;
    try {
      if (!constants.PUBLISH_DIR) throw new Error('Netlify publish directory is unavailable');
      const publishDirectory = path.resolve(constants.PUBLISH_DIR);
      if (!fs.statSync(publishDirectory).isDirectory()) {
        throw new Error('Netlify publish directory does not exist');
      }

      // Only normalized indexing headers are copied. No environment variables,
      // credentials, or other Netlify configuration is logged or serialized.
      const headers = [];
      for (const rule of netlifyConfig.headers || []) {
        for (const [name, value] of Object.entries(rule.values || {})) {
          if (name.toLowerCase() === 'x-robots-tag') {
            headers.push({ for: rule.for, value: String(value) });
          }
        }
      }
      temporaryDirectory = fs.mkdtempSync(path.join(os.tmpdir(), 'peak-seo-guard-'));
      const headersPath = path.join(temporaryDirectory, 'indexing-headers.json');
      fs.writeFileSync(headersPath, JSON.stringify(headers), { mode: 0o600 });
      const result = spawnSync('python3', [
        path.join(repositoryRoot, '.github/scripts/seo_guard.py'),
        '--root', publishDirectory,
        '--policy', path.join(repositoryRoot, '.github/seo-policy.json'),
        '--netlify-headers', headersPath,
      ], {
        cwd: repositoryRoot,
        encoding: 'utf8',
        timeout: 120000,
        maxBuffer: 4 * 1024 * 1024,
      });
      if (result.stdout) process.stdout.write(result.stdout);
      if (result.stderr) process.stderr.write(result.stderr);
      if (result.error || result.signal || result.status !== 0) {
        failure = result.error || new Error(
          `SEO guard exited with status ${result.status}, signal ${result.signal || 'none'}`
        );
      }
    } catch (error) {
      failure = error;
    } finally {
      if (temporaryDirectory) fs.rmSync(temporaryDirectory, { recursive: true, force: true });
    }
    if (failure) {
      utils.build.failBuild('SEO regression guard stopped deployment. Review the violations above.', {
        error: failure,
      });
    }
  },
};


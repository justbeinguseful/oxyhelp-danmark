# Repository SEO regression guard

Run locally before publishing, from the repository root:

```bash
python3 .github/scripts/seo_guard.py --root . --report /tmp/seo-guard.json
```

Requires Python 3.11 or newer, using its standard library only. The check reads local source files. It does not browse websites, execute site JavaScript, call analytics, submit forms, publish content, or write to site content. Exit code 0 means pass; 1 means a detected regression. JSON is printed, with an optional local report file.

GitHub Actions runs the same check on pull requests, pushes to `main`, and manual dispatch. It uses a pinned official checkout action and `contents: read` permissions with no persisted checkout credentials. No secrets or deployment permissions are required.

Checks cover homepage indexing/canonical correctness; sitemap HTTPS/host/uniqueness/source files and canonicals; public noindex directives in HTML and Netlify header configuration; valid JSON-LD and defined Schema.org type names; existing search/training crawler rules; intentional private/preview/legal noindex; and existing forced-404 security routes. `/.github/*` is itself blocked by an exact forced-404 rule in `_redirects` so these internal files are not served by the static website.

The site-specific policy records the reviewed existing exclusions and required public pages. Intentional future policy changes require reviewing that file with the site change. Do not add broad exceptions to make a failing check pass. Narrow pre-existing exceptions, if any, must contain the exact code, path and observed detail; they are reported separately and do not apply to new errors.

`schema-types.json` is an offline snapshot of the official Schema.org class vocabulary, with source URL and hash. It checks type names, not medical truth, property compatibility, Google rich-result eligibility, or every external vocabulary. Update that snapshot deliberately if using a new legitimate Schema.org type.

The local Netlify plugin registered in `netlify.toml` runs this guard during `onPostBuild`, before deployment, and calls `utils.build.failBuild` if the guard fails, times out, or cannot run. It checks Netlify's actual `PUBLISH_DIR`, using the policy/script from the repository. It does not override the existing build command, publish directory, function settings, or Python version. The selected Python 3 runtime is reused; normalized indexing headers are supplied by Netlify, so the plugin path does not require Python's optional `tomllib` module. Local/Actions checks continue to use Python 3.11+ for full TOML parsing.

The GitHub Actions check can additionally be required before merging through branch protection. Manual uploads or API deploys that skip Netlify Build do not execute build plugins; those still require the standalone guard. Removing/disabling the plugin also removes that deployment gate. Keep the manual guard usable if workflow installation or Actions permissions are unavailable.

No script can guarantee rankings, actual search indexing, AI citations, analytics correctness, or unchanged visual appearance. Keep the separate live HTTP guard and before/after visual checks for deployment verification.

Official references: https://docs.github.com/en/actions/tutorials/authenticate-with-github_token ; https://github.com/actions/checkout/commit/3d3c42e5aac5ba805825da76410c181273ba90b1 ; https://schema.org/version/latest/schemaorg-current-https.jsonld .

Netlify plugin references: https://docs.netlify.com/extend/develop-and-share/develop-build-plugins/ ; https://docs.netlify.com/build/configure-builds/available-software-at-build-time/ .


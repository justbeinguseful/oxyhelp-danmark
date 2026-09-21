#!/usr/bin/env python3
"""Offline repository SEO regression checks. Python 3.11+; no network or writes to site content."""
import argparse
from datetime import datetime, timezone
from html.parser import HTMLParser
import json
from pathlib import Path
import re
import sys
try:
    import tomllib
except ImportError:
    tomllib = None
from urllib.parse import unquote, urlsplit
import xml.etree.ElementTree as ET

class MetadataParser(HTMLParser):
    def __init__(self):
        super().__init__()
        self.canonicals = []
        self.robots = []
        self.jsonld = []
        self._jsonld = None

    def handle_starttag(self, tag, attrs):
        attrs = dict(attrs)
        if tag == "link" and "canonical" in attrs.get("rel", "").lower().split():
            self.canonicals.append(attrs.get("href", ""))
        if tag == "meta" and attrs.get("name", "").lower() in (
            "robots", "googlebot", "bingbot", "oai-searchbot", "perplexitybot",
        ):
            self.robots.append({"name": attrs.get("name"), "content": attrs.get("content", "")})
        if tag == "script" and attrs.get("type", "").lower() == "application/ld+json":
            self._jsonld = []

    def handle_data(self, data):
        if self._jsonld is not None:
            self._jsonld.append(data)

    def handle_endtag(self, tag):
        if tag == "script" and self._jsonld is not None:
            self.jsonld.append("".join(self._jsonld))
            self._jsonld = None

def parse_robots(text):
    """Retain groups; consecutive User-agent lines belong to the same group."""
    groups = []
    agents, rules = [], []
    saw_rule = False
    for line in text.lstrip("\ufeff").splitlines():
        line = line.split("#", 1)[0].strip()
        if ":" not in line:
            continue
        key, value = (part.strip() for part in line.split(":", 1))
        key = key.lower()
        if key == "user-agent":
            if agents and saw_rule:
                groups.append({"agents": agents, "rules": rules})
                agents, rules, saw_rule = [], [], False
            if value:
                agents.append(value.lower())
        elif key in ("allow", "disallow") and agents:
            saw_rule = True
            # An empty Disallow grants no restriction; it must not match all paths.
            if value:
                rules.append((key, value))
    if agents:
        groups.append({"agents": agents, "rules": rules})
    return groups

def robots_decision(groups, agent, path):
    """Use most-specific UA groups, combine duplicates, longest path, Allow ties."""
    selected, specificity = [], -1
    agent = agent.lower()
    for group in groups:
        matches = [0 if token == "*" else len(token) for token in group["agents"]
                   if token == "*" or token in agent]
        if not matches:
            continue
        current = max(matches)
        if current > specificity:
            specificity, selected = current, [group]
        elif current == specificity:
            selected.append(group)
    matches = []
    for group in selected:
        for kind, pattern in group["rules"]:
            anchored = pattern.endswith("$")
            literal = pattern[:-1] if anchored else pattern
            regex = "^" + ".*".join(re.escape(part) for part in literal.split("*"))
            if anchored:
                regex += "$"
            if re.search(regex, path):
                length = len(literal.replace("*", "").encode("utf-8"))
                matches.append((length, kind == "allow", kind, pattern))
    winner = max(matches) if matches else None
    return {
        "allowed": winner[1] if winner else True,
        "matched_rule": f"{winner[2]}: {winner[3]}" if winner else None,
        "groups": [group["agents"] for group in selected],
    }

def normalized_url(url):
    p = urlsplit(url)
    return (p.scheme.lower(), p.netloc.lower(), p.path or "/", p.query, p.fragment)

def schema_types(value):
    if isinstance(value, dict):
        types = value.get("@type", [])
        if isinstance(types, str):
            yield types
        elif isinstance(types, list):
            yield from (item for item in types if isinstance(item, str))
        for child in value.values():
            yield from schema_types(child)
    elif isinstance(value, list):
        for child in value:
            yield from schema_types(child)

def read(path):
    return path.read_text(encoding="utf-8")


def inside(path, root):
    try:
        path.resolve().relative_to(root.resolve())
        return True
    except ValueError:
        return False


def page(root, path):
    target = root / path
    if not target.is_file() or not inside(target, root):
        return None
    parser = MetadataParser()
    parser.feed(read(target))
    return parser


def route_file(root, url):
    path = unquote(urlsplit(url).path)
    if ".." in Path(path).parts:
        return None
    relative = path.lstrip("/")
    candidates = ([relative + "index.html"] if path.endswith("/") else
                  [relative, relative + ".html", relative + "/index.html"])
    for candidate in candidates:
        target = root / candidate
        if target.is_file() and inside(target, root):
            return candidate
    return None


def noindex(parser):
    return [item for item in parser.robots
            if re.search(r"\b(noindex|none)\b", item["content"], re.I)]


def redirect_rules(text):
    return [tuple(line.split("#", 1)[0].split()[:3]) for line in text.splitlines()
            if len(line.split("#", 1)[0].split()) >= 3]


def matches(pattern, path):
    return bool(re.fullmatch(".*".join(re.escape(s) for s in pattern.split("*")), path))


def audit(root, policy, netlify_headers=None):
    violations, waived = [], []
    exceptions = policy.get("reviewed_existing_exceptions", [])

    def problem(code, path, detail):
        record = {"code": code, "path": path, "detail": detail}
        if record in exceptions:
            waived.append(record)
        else:
            violations.append(record)

    host = policy["host"]
    origin = "https://" + host
    types_path = Path(__file__).resolve().with_name("schema-types.json")
    known_types = set(json.loads(read(types_path))["types"])
    redirects = redirect_rules(read(root / "_redirects")) if (root / "_redirects").exists() else []
    for rule in policy["protected_redirects"]:
        if tuple(rule) not in redirects:
            problem("security-redirect-removed", "_redirects", list(rule))
    github_rule = ("/.github/*", "/404.html", "404!")
    first_github_match = next((r for r in redirects if matches(r[0], "/.github/scripts/seo_guard.py")), None)
    if first_github_match != github_rule:
        problem("guard-files-publicly-exposed", "_redirects", first_github_match)

    header_rules = []
    headers_path = root / "_headers"
    if headers_path.exists():
        pattern = None
        for line in read(headers_path).splitlines():
            if not line.strip() or line.lstrip().startswith("#"):
                continue
            if not line[0].isspace():
                pattern = line.strip()
            elif pattern and line.strip().lower().startswith("x-robots-tag:"):
                header_rules.append((pattern, line.strip().split(":", 1)[1]))
    netlify = root / "netlify.toml"
    if netlify_headers is not None:
        for header in netlify_headers:
            header_rules.append((header["for"], header["value"]))
    elif netlify.exists() and tomllib is None:
        problem("toml-parser-unavailable", "netlify.toml",
                "Use Python 3.11+ locally, or the Netlify plugin supplying normalized headers")
    elif netlify.exists():
        try:
            config = tomllib.loads(read(netlify))
            for header in config.get("headers", []):
                for key, value in header.get("values", {}).items():
                    if key.lower() == "x-robots-tag":
                        header_rules.append((header.get("for", ""), str(value)))
        except tomllib.TOMLDecodeError as exc:
            problem("netlify-toml-invalid", "netlify.toml", str(exc))

    sitemap = root / "sitemap.xml"
    urls = []
    try:
        xml = ET.fromstring(read(sitemap))
        if xml.tag.rsplit("}", 1)[-1] != "urlset":
            raise ValueError("Expected urlset")
        urls = [(node.text or "").strip() for node in xml.iter()
                if node.tag.rsplit("}", 1)[-1] == "loc"]
        if not urls:
            raise ValueError("Empty sitemap")
    except (OSError, ET.ParseError, ValueError) as exc:
        problem("sitemap-invalid", "sitemap.xml", str(exc))
    seen, public_pages = set(), {"index.html": origin + "/"}
    for url in urls:
        try:
            parsed = urlsplit(url)
            if (parsed.scheme != "https" or parsed.hostname != host or parsed.query
                    or parsed.fragment or parsed.username or parsed.password or parsed.port not in (None, 443)):
                raise ValueError("Sitemap URL must use HTTPS and this host, without query/fragment/credentials")
            normalized = normalized_url(url)
        except ValueError as exc:
            problem("sitemap-url-invalid", "sitemap.xml", {"url": url, "reason": str(exc)})
            continue
        if normalized in seen:
            problem("sitemap-url-duplicate", "sitemap.xml", url)
        seen.add(normalized)
        source = route_file(root, url)
        if not source:
            problem("sitemap-source-missing", "sitemap.xml", url)
            continue
        public_pages[source] = url
        for rule in redirects:
            if rule[0] == parsed.path and rule[2].startswith(("301", "302", "307", "308")):
                problem("sitemap-redirect-entry", "sitemap.xml", {"url": url, "rule": list(rule)})
                break
    for required in policy["required_sitemap_paths"]:
        if normalized_url(origin + required) not in seen:
            problem("required-page-missing-from-sitemap", "sitemap.xml", origin + required)

    for source, expected_url in public_pages.items():
        parser = page(root, source)
        if parser is None:
            problem("public-source-missing", source, expected_url)
            continue
        if noindex(parser):
            problem("public-page-noindex", source, noindex(parser))
        if source == "index.html" and any(re.search(r"\b(nofollow|none)\b", p["content"], re.I) for p in parser.robots):
            problem("homepage-nofollow", source, parser.robots)
        if len(parser.canonicals) != 1 or normalized_url(parser.canonicals[0]) != normalized_url(expected_url):
            problem("public-canonical-mismatch", source, {"expected": expected_url, "actual": parser.canonicals})
        for pattern, value in header_rules:
            if matches(pattern, urlsplit(expected_url).path) and re.search(r"\b(noindex|none)\b", value, re.I):
                problem("public-header-noindex", source, {"pattern": pattern, "value": value})
        for script in parser.jsonld:
            try:
                data = json.loads(script)
            except json.JSONDecodeError as exc:
                problem("jsonld-invalid", source, str(exc))
                continue
            for name in set(schema_types(data)):
                if name.startswith(("https://schema.org/", "http://schema.org/", "schema:")):
                    name = name.rsplit("/", 1)[-1]
                    if name.startswith("schema:"):
                        name = name[len("schema:"):]
                elif ":" in name:
                    continue  # Explicit non-Schema.org vocabulary.
                if name not in known_types:
                    problem("jsonld-undefined-schema-type", source, name)

    for source in policy["preserve_noindex_files"]:
        parser = page(root, source)
        # Deleting a private/draft page does not expose it; stripping its noindex does.
        if parser is not None and not noindex(parser):
            problem("intentional-noindex-removed", source, "Preserve exclusion or explicitly review policy change")

    robots_path = root / "robots.txt"
    if not robots_path.exists():
        problem("robots-missing", "robots.txt", "Required crawler policy file missing")
    else:
        groups = parse_robots(read(robots_path))
        public_paths = [urlsplit(url).path or "/" for url in public_pages.values()]
        for agent in policy["allow_search_bots"]:
            blocked = [path for path in public_paths if not robots_decision(groups, agent, path)["allowed"]]
            if blocked:
                problem("public-search-crawler-blocked", "robots.txt", {"agent": agent, "paths": blocked})
        for agent in policy["preserve_blocked_bots"]:
            open_paths = [path for path in public_paths if robots_decision(groups, agent, path)["allowed"]]
            if open_paths:
                problem("existing-crawler-block-removed", "robots.txt", {"agent": agent, "paths": open_paths})
        for path in policy["protected_robots_paths"]:
            for agent in ["*"] + policy["allow_search_bots"]:
                if robots_decision(groups, agent, path)["allowed"]:
                    problem("private-crawler-exclusion-removed", "robots.txt", {"agent": agent, "path": path})
    return {
        "timestamp_utc": datetime.now(timezone.utc).isoformat(),
        "host": host, "source": "local repository only; no network or browser execution",
        "sitemap_urls": len(urls), "public_html_checked": len(public_pages),
        "private_noindex_files_preserved": len(policy["preserve_noindex_files"]),
        "passed": not violations, "violations": violations,
        "reviewed_existing_exceptions_seen": waived,
    }


def main():
    parser = argparse.ArgumentParser(description="Offline SEO regression guard; Python 3.11+, no dependencies")
    parser.add_argument("--root", type=Path, default=Path.cwd())
    parser.add_argument("--report", type=Path)
    parser.add_argument("--policy", type=Path, help="Policy in repository when checking a separate publish directory")
    parser.add_argument("--netlify-headers", type=Path, help="Normalized X-Robots rules supplied by the Netlify plugin")
    args = parser.parse_args()
    policy = json.loads(read(args.policy or args.root / ".github/seo-policy.json"))
    headers = json.loads(read(args.netlify_headers)) if args.netlify_headers else None
    result = audit(args.root.resolve(), policy, netlify_headers=headers)
    text = json.dumps(result, ensure_ascii=False, indent=2) + "\n"
    if args.report:
        args.report.parent.mkdir(parents=True, exist_ok=True)
        args.report.write_text(text, encoding="utf-8")
    print(text, end="")
    for item in result["violations"]:
        # Avoid injecting source-controlled file text into GitHub workflow commands.
        print("SEO violation:", item["code"], item["path"], file=sys.stderr)
    return 0 if result["passed"] else 1


if __name__ == "__main__":
    sys.exit(main())


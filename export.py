"""Export the local WordPress A/B demo as a self-contained static preview."""

from __future__ import annotations

import re
import shutil
import urllib.parse
import urllib.request
from pathlib import Path

LOCAL_ORIGIN = "http://127.0.0.1:10008"
LOCAL_HOST = "dentiste-local.local"
PUBLIC_DIR = Path(__file__).parent / "public"
INTERNAL_HOSTS = {
    LOCAL_HOST,
    "destinations-grade-inn-shareware.trycloudflare.com",
    "painting-tide-commerce-roles.trycloudflare.com",
}
EXTERNAL_SCHEMES = {"mailto", "tel", "data", "javascript"}

PAGES = {
    "fr": {
        "": "",
        "services": "services",
        "la-clinique": "la-clinique",
        "informations": "informations",
        "nous-joindre": "nous-joindre",
        "prendre-rendez-vous": "prendre-rendez-vous",
    },
    "en": {
        "": "",
        "services": "services",
        "the-clinic": "the-clinic",
        "informations": "informations",
        "contact": "contact",
        "take-appointment": "take-appointment",
    },
}


def local_request(path_and_query: str) -> bytes:
    """Fetch one resource from Local while preserving its WordPress hostname."""
    request = urllib.request.Request(
        LOCAL_ORIGIN + path_and_query,
        headers={"Host": LOCAL_HOST, "User-Agent": "CDFMain static exporter"},
    )
    with urllib.request.urlopen(request, timeout=30) as response:
        return response.read()


def is_internal(url: str) -> bool:
    """Return whether a URL belongs to the local preview."""
    parsed = urllib.parse.urlsplit(url)
    return not parsed.netloc or parsed.hostname in INTERNAL_HOSTS


def local_path(url: str) -> str:
    """Convert an internal absolute URL to an origin-relative URL."""
    parsed = urllib.parse.urlsplit(url)
    path = parsed.path or "/"
    return path + (f"?{parsed.query}" if parsed.query else "")


def static_page_url(url: str, current_design: str, current_language: str) -> str:
    """Map a WordPress page URL to its static A/B equivalent."""
    parsed = urllib.parse.urlsplit(url)
    query = urllib.parse.parse_qs(parsed.query)
    design = query.get("design", [current_design])[0]
    design = "b" if design in {"b", "clair"} else "a"
    language = query.get("lang", [current_language])[0]
    language = "en" if language == "en" else "fr"
    path = parsed.path.strip("/")

    known_paths = set(PAGES["fr"]) | set(PAGES["en"])
    if path not in known_paths:
        return url

    prefix = f"/{design}/"
    if language == "en":
        prefix += "en/"
    destination = prefix + (f"{path}/" if path else "")
    return destination + (f"#{parsed.fragment}" if parsed.fragment else "")


def rewrite_url(url: str, current_design: str, current_language: str) -> str:
    """Rewrite one internal asset or navigation URL for static hosting."""
    if not url or url.startswith("#"):
        return url

    parsed = urllib.parse.urlsplit(url)
    if parsed.scheme in EXTERNAL_SCHEMES or not is_internal(url):
        return url

    path = parsed.path or "/"
    if path.startswith(("/wp-content/", "/wp-includes/")):
        return path

    return static_page_url(url, current_design, current_language)


def save_asset(url: str, seen: set[str]) -> None:
    """Download one internal asset and recursively collect CSS dependencies."""
    if not url or not is_internal(url):
        return

    parsed = urllib.parse.urlsplit(url)
    path = parsed.path
    if not path.startswith(("/wp-content/", "/wp-includes/")):
        return
    if path in seen:
        return
    seen.add(path)

    try:
        data = local_request(local_path(url))
    except Exception as exc:  # noqa: BLE001 - one missing optional asset should not abort export.
        print(f"warning: {path}: {exc}")
        return

    target = PUBLIC_DIR / path.lstrip("/")
    target.parent.mkdir(parents=True, exist_ok=True)

    if path.endswith(".css"):
        css = data.decode("utf-8", errors="replace")
        references = re.findall(r"url\(\s*['\"]?([^)'\"\s]+)", css)
        for reference in references:
            absolute = urllib.parse.urljoin(url, reference)
            save_asset(absolute, seen)
        for host in INTERNAL_HOSTS:
            css = css.replace(f"http://{host}", "").replace(f"https://{host}", "")
        target.write_text(css, encoding="utf-8")
    else:
        target.write_bytes(data)


def export_page(design: str, language: str, source_slug: str, output_slug: str, assets: set[str]) -> None:
    """Export and rewrite one WordPress page."""
    query = {"design": design}
    if language == "en":
        query["lang"] = "en"
    source = f"/{source_slug + '/' if source_slug else ''}?{urllib.parse.urlencode(query)}"
    html = local_request(source).decode("utf-8", errors="replace")

    discovered = re.findall(
        r"""(?:src|href|poster)=["']([^"']+)["']|url\(["']?([^"')]+)""",
        html,
        flags=re.IGNORECASE,
    )
    for groups in discovered:
        value = next((item for item in groups if item), "")
        absolute = urllib.parse.urljoin(f"https://{LOCAL_HOST}{source}", value)
        save_asset(absolute, assets)

    def replace_attribute(match: re.Match[str]) -> str:
        attribute, quote, value = match.groups()
        return f"{attribute}={quote}{rewrite_url(value, design, language)}{quote}"

    html = re.sub(
        r"""(src|href|poster)=(["'])(.*?)\2""",
        replace_attribute,
        html,
        flags=re.IGNORECASE,
    )
    html = re.sub(
        r"""<link[^>]+title=["']oEmbed \((?:JSON|XML)\)["'][^>]*>\s*""",
        "",
        html,
        flags=re.IGNORECASE,
    )

    for host in INTERNAL_HOSTS:
        html = html.replace(f"http://{host}", "").replace(f"https://{host}", "")
    html = html.replace("info@dentiste-local.local", "info@cdfmain.com")

    notice = (
        '<div class="static-preview-notice" role="status">'
        "Démo visuelle — les formulaires sont désactivés."
        "</div>"
        "<style>.static-preview-notice{position:fixed;right:12px;bottom:12px;z-index:99998;"
        "padding:8px 12px;border-radius:999px;background:#014337;color:#fff;"
        "font:600 11px/1.2 system-ui;box-shadow:0 8px 25px #0003}"
        "@media(max-width:600px){.static-preview-notice{display:none}}</style>"
        "<script>document.addEventListener('submit',function(e){e.preventDefault();"
        "alert('Formulaire désactivé sur la démo visuelle.');});</script>"
    )
    html = html.replace("</body>", notice + "</body>")

    destination = PUBLIC_DIR / design
    if language == "en":
        destination /= "en"
    if output_slug:
        destination /= output_slug
    destination.mkdir(parents=True, exist_ok=True)
    (destination / "index.html").write_text(html, encoding="utf-8")


def main() -> None:
    """Build all French and English static preview pages."""
    if PUBLIC_DIR.exists():
        shutil.rmtree(PUBLIC_DIR)
    PUBLIC_DIR.mkdir(parents=True)

    assets: set[str] = set()
    for design in ("a", "b"):
        for language, pages in PAGES.items():
            for source_slug, output_slug in pages.items():
                export_page(design, language, source_slug, output_slug, assets)

    landing = """<!doctype html><html lang="fr"><meta charset="utf-8">
<meta name="viewport" content="width=device-width,initial-scale=1">
<meta http-equiv="refresh" content="0;url=/a/">
<title>Clinique Dentaire Familiale Main — propositions A/B</title>
<p><a href="/a/">Voir les propositions</a></p></html>"""
    (PUBLIC_DIR / "index.html").write_text(landing, encoding="utf-8")
    print(f"Exported {len(assets)} assets to {PUBLIC_DIR}")


if __name__ == "__main__":
    main()

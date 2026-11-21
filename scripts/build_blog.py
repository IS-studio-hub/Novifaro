#!/usr/bin/env python3
"""Render blog.html and blog/*.html from scripts/blog_content.py.
Run from the project root:  python3 scripts/build_blog.py
"""
import html, json, os, re, sys
from datetime import date

sys.path.insert(0, os.path.dirname(__file__))
from blog_content import POSTS, DATE

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SITE = "https://novifaro.ca"
LOGO = SITE + "/Assets/brand/novifaro-circle.png"
OG_IMG = SITE + "/Assets/brand/novifaro-square.png"
BY = by = "Novifaro"

def esc(s): return html.escape(s, quote=True)
def strip(s): return re.sub(r"<[^>]+>", "", s)

def human_date(iso):
    d = date.fromisoformat(iso)
    return d.strftime("%B %-d, %Y")

def render_block(b):
    t = b[0]
    if t == "p":
        return f"<p>{b[1]}</p>"
    if t == "ul":
        return "<ul>" + "".join(f"<li>{x}</li>" for x in b[1]) + "</ul>"
    if t == "ol":
        return "<ol>" + "".join(f"<li>{x}</li>" for x in b[1]) + "</ol>"
    if t == "table":
        head = "".join(f"<th scope=\"col\">{h}</th>" for h in b[1])
        rows = "".join("<tr>" + "".join(f"<td>{c}</td>" for c in r) + "</tr>" for r in b[2])
        return f"<div class=\"table-wrap\"><table><thead><tr>{head}</tr></thead><tbody>{rows}</tbody></table></div>"
    raise ValueError(t)

def post_text(p):
    parts = [p["tldr"], p["intro"]]
    for h, blocks in p["sections"]:
        parts.append(h)
        for b in blocks:
            parts.append(" ".join(b[1]) if b[0] in ("ul", "ol") else (" ".join(" ".join(r) for r in b[2]) if b[0] == "table" else b[1]))
    for q, a in p["faq"]:
        parts += [q, a]
    return strip(" ".join(parts))

def read_minutes(p):
    return max(3, round(len(post_text(p).split()) / 200))

def slugify(s):
    return re.sub(r"[^a-z0-9]+", "-", strip(s).lower()).strip("-")

NAV = """<nav class="pills" id="primary-nav" aria-label="Primary">
        <a class="pill" href="{p}work.html"><i class="dot" aria-hidden="true"></i> Website</a>
        <a class="pill" href="{p}About.html"><i class="dot" aria-hidden="true"></i> Our House</a>
        <a class="pill is-active" href="{p}blog.html" aria-current="page"><i class="dot" aria-hidden="true"></i> Blog</a>
        <a class="pill" href="{p}contact.html"><i class="dot" aria-hidden="true"></i> Let's Talk</a>
      </nav>"""

def page_shell(*, prefix, title, desc, canonical, og_type, jsonld, body, keywords=None, extra_meta=""):
    kw = f'\n  <meta name="keywords" content="{esc(", ".join(keywords))}" />' if keywords else ""
    return f"""<!doctype html>
<html lang="en">
<head>
  <meta charset="utf-8" />
  <meta name="viewport" content="width=device-width, initial-scale=1" />
  <title>{esc(title)}</title>
  <meta name="description" content="{esc(desc)}" />{kw}
  <meta name="robots" content="index, follow, max-image-preview:large, max-snippet:-1" />
  <meta name="referrer" content="strict-origin-when-cross-origin" />
  <meta name="color-scheme" content="light" />
  <meta name="google-site-verification" content="3iUAZ43h8-pOzgmQ-HK7p0uWsD6VTcYikCwKxovH-KE" />
  <link rel="canonical" href="{canonical}" />
  <meta property="og:type" content="{og_type}" />
  <meta property="og:site_name" content="Novifaro" />
  <meta property="og:title" content="{esc(title)}" />
  <meta property="og:description" content="{esc(desc)}" />
  <meta property="og:url" content="{canonical}" />
  <meta property="og:image" content="{OG_IMG}" />
  <meta property="og:locale" content="en_CA" />{extra_meta}
  <meta name="twitter:card" content="summary" />
  <meta name="twitter:title" content="{esc(title)}" />
  <meta name="twitter:description" content="{esc(desc)}" />
  <meta name="twitter:image" content="{OG_IMG}" />
  <link rel="icon" href="{prefix}Assets/brand/novifaro-circle.png" type="image/png" />
  <link rel="alternate" type="application/rss+xml" title="Novifaro Blog" href="{SITE}/blog/feed.xml" />
  <link rel="preconnect" href="https://fonts.googleapis.com" />
  <link rel="preconnect" href="https://fonts.gstatic.com" crossorigin />
  <link href="https://fonts.googleapis.com/css2?family=Bebas+Neue&family=Inter:wght@400;600;700&display=swap" rel="stylesheet" />
  <link rel="stylesheet" href="{prefix}css/blog.css" />
  <script type="application/ld+json">
{json.dumps(jsonld, indent=2, ensure_ascii=False)}
  </script>
  <script defer src="https://lytico-production.up.railway.app/lytico.js" data-site="lt_isstudio_is05"></script>
</head>
<body>
  <a class="skip" href="#main">Skip to content</a>
  <header class="site-header">
    <a class="brand" href="{prefix}index.html" aria-label="Novifaro home">
      <img src="{prefix}Assets/brand/novifaro-circle.png" alt="" width="40" height="40" />
      <span>NOVIFARO</span>
    </a>
    <button type="button" class="nav-toggle" aria-expanded="false" aria-controls="primary-nav" aria-label="Open menu">
      <span class="nav-toggle__bar" aria-hidden="true"></span>
      <span class="nav-toggle__bar" aria-hidden="true"></span>
      <span class="nav-toggle__bar" aria-hidden="true"></span>
    </button>
    <div class="nav-wrap">
      {NAV.format(p=prefix)}
    </div>
  </header>
{body}
  <footer class="site-footer">
    <p><strong>Novifaro</strong> is a Toronto digital growth agency: digital marketing, SEO, web design and development, and AI systems.</p>
    <p><a href="{prefix}contact.html">Start a project</a> · <a href="mailto:hello@isexperience.house">hello@isexperience.house</a> · <a href="tel:+16139226604">+1 613 922 6604</a></p>
    <p>© 2026 Novifaro · Toronto, Ontario, Canada</p>
  </footer>
  <script>
  (function () {{
    var header = document.querySelector('.site-header');
    var toggle = header && header.querySelector('.nav-toggle');
    if (!toggle) return;
    var mql = window.matchMedia('(max-width: 600px)');
    function setOpen(open) {{
      header.classList.toggle('is-nav-open', open);
      toggle.setAttribute('aria-expanded', String(open));
      toggle.setAttribute('aria-label', open ? 'Close menu' : 'Open menu');
    }}
    toggle.addEventListener('click', function (e) {{ e.stopPropagation(); setOpen(!header.classList.contains('is-nav-open')); }});
    header.querySelectorAll('.pill').forEach(function (a) {{ a.addEventListener('click', function () {{ setOpen(false); }}); }});
    document.addEventListener('click', function (e) {{ if (!header.contains(e.target)) setOpen(false); }});
    document.addEventListener('keydown', function (e) {{ if (e.key === 'Escape') setOpen(false); }});
    mql.addEventListener('change', function () {{ setOpen(false); }});
  }})();
  </script>
</body>
</html>
"""

def build_post(p, by_slug):
    url = f"{SITE}/blog/{p['slug']}.html"
    mins = read_minutes(p)
    wc = len(post_text(p).split())
    toc = "".join(f'<li><a href="#{slugify(h)}">{h}</a></li>' for h, _ in p["sections"])
    toc += '<li><a href="#faq">Frequently asked questions</a></li>'
    secs = ""
    for h, blocks in p["sections"]:
        secs += f'<section class="sec" id="{slugify(h)}"><h2>{h}</h2>' + "".join(render_block(b) for b in blocks) + "</section>\n"
    faq = "".join(f"<details class=\"qa\" open><summary><h3>{esc(q)}</h3></summary><p>{a}</p></details>" for q, a in p["faq"])
    related = "".join(
        f'<li><a href="{r}.html"><span class="tag">{esc(by_slug[r]["category"])}</span><strong>{esc(by_slug[r]["short"])}</strong></a></li>'
        for r in p["related"])
    body = f"""  <main id="main">
    <article class="post" itemscope itemtype="https://schema.org/BlogPosting">
      <nav class="crumbs" aria-label="Breadcrumb"><a href="../index.html">Home</a> / <a href="../blog.html">Blog</a> / <span>{esc(p['short'])}</span></nav>
      <p class="tag">{esc(p['category'])}</p>
      <h1 itemprop="headline">{esc(p['title'])}</h1>
      <p class="meta">By <span itemprop="author">Novifaro</span> · Published <time datetime="{DATE}" itemprop="datePublished">{human_date(DATE)}</time> · Updated <time datetime="{DATE}" itemprop="dateModified">{human_date(DATE)}</time> · {mins} min read</p>
      <aside class="tldr" aria-label="Quick answer"><h2>Quick answer</h2><p>{p['tldr']}</p></aside>
      <p class="lede">{p['intro']}</p>
      <nav class="toc" aria-label="Table of contents"><h2>In this article</h2><ol>{toc}</ol></nav>
      <div itemprop="articleBody">
{secs}
      <section class="sec" id="faq"><h2>Frequently asked questions</h2>{faq}</section>
      </div>
      <aside class="cta"><h2>Want help growing your business online?</h2><p>Novifaro is a Toronto digital growth agency. We combine digital marketing and SEO, website design and development, and AI systems to bring you more qualified leads and measurable results.</p><a class="btn" href="../contact.html">&gt;_START_A_PROJECT</a></aside>
      <section class="related"><h2>Keep reading</h2><ul>{related}</ul></section>
    </article>
  </main>"""
    jsonld = {
      "@context": "https://schema.org",
      "@graph": [
        {
          "@type": "BlogPosting",
          "@id": url + "#article",
          "headline": p["title"],
          "description": p["desc"],
          "url": url,
          "mainEntityOfPage": {"@type": "WebPage", "@id": url},
          "datePublished": DATE,
          "dateModified": DATE,
          "inLanguage": "en-CA",
          "articleSection": p["category"],
          "keywords": ", ".join(p["keywords"]),
          "wordCount": wc,
          "image": OG_IMG,
          "author": {"@type": "Organization", "name": "Novifaro", "url": SITE + "/"},
          "publisher": {"@type": "Organization", "name": "Novifaro", "url": SITE + "/",
                        "logo": {"@type": "ImageObject", "url": LOGO}},
          "isPartOf": {"@type": "Blog", "@id": SITE + "/blog.html#blog"},
        },
        {
          "@type": "FAQPage",
          "mainEntity": [
            {"@type": "Question", "name": q,
             "acceptedAnswer": {"@type": "Answer", "text": strip(a)}} for q, a in p["faq"]
          ],
        },
        {
          "@type": "BreadcrumbList",
          "itemListElement": [
            {"@type": "ListItem", "position": 1, "name": "Home", "item": SITE + "/"},
            {"@type": "ListItem", "position": 2, "name": "Blog", "item": SITE + "/blog.html"},
            {"@type": "ListItem", "position": 3, "name": p["short"], "item": url},
          ],
        },
      ],
    }
    extra = f"""
  <meta property="article:published_time" content="{DATE}" />
  <meta property="article:modified_time" content="{DATE}" />
  <meta property="article:section" content="{esc(p['category'])}" />
  <meta property="article:author" content="Novifaro" />"""
    return page_shell(prefix="../", title=p["title"] + " | Novifaro", desc=p["desc"], canonical=url,
                      og_type="article", jsonld=jsonld, body=body, keywords=p["keywords"], extra_meta=extra)

def build_index(posts):
    url = SITE + "/blog.html"
    cards = ""
    for p in posts:
        cards += f"""<li class="card"><a href="blog/{p['slug']}.html">
          <span class="tag">{esc(p['category'])}</span>
          <h2>{esc(p['title'])}</h2>
          <p>{esc(p['desc'])}</p>
          <span class="more">{read_minutes(p)} min read · {human_date(DATE)} →</span></a></li>
"""
    body = f"""  <main id="main">
    <section class="blog-hero">
      <p class="tag">The Novifaro blog</p>
      <h1>Digital marketing, SEO, web design &amp; AI insights for growing businesses</h1>
      <p class="lede">Practical guides from a Toronto digital growth agency. Learn how to rank on Google, get cited by AI search tools, build websites that convert, automate with AI, and measure real marketing ROI.</p>
    </section>
    <section aria-label="Latest articles">
      <ul class="cards">
{cards}      </ul>
    </section>
    <aside class="cta"><h2>Ready to grow with digital marketing, web, and AI?</h2><p>Tell us about your business and goals. We will recommend the fastest route to more qualified leads.</p><a class="btn" href="contact.html">&gt;_START_A_PROJECT</a></aside>
  </main>"""
    jsonld = {
      "@context": "https://schema.org",
      "@graph": [
        {
          "@type": "Blog",
          "@id": url + "#blog",
          "name": "Novifaro Blog",
          "url": url,
          "description": "Digital marketing, SEO, web design, and AI systems insights for growing businesses from Novifaro in Toronto.",
          "inLanguage": "en-CA",
          "publisher": {"@type": "Organization", "name": "Novifaro", "url": SITE + "/", "logo": {"@type": "ImageObject", "url": LOGO}},
          "blogPost": [{"@type": "BlogPosting", "headline": p["title"], "url": f"{SITE}/blog/{p['slug']}.html", "datePublished": DATE} for p in posts],
        },
        {
          "@type": "BreadcrumbList",
          "itemListElement": [
            {"@type": "ListItem", "position": 1, "name": "Home", "item": SITE + "/"},
            {"@type": "ListItem", "position": 2, "name": "Blog", "item": url},
          ],
        },
      ],
    }
    return page_shell(prefix="", title="Blog | Digital Marketing, SEO, Web Design & AI Insights | Novifaro",
                      desc="Guides on digital marketing, SEO, generative engine optimization (GEO), website design that converts, and AI automation for small businesses, from Novifaro in Toronto.",
                      canonical=url, og_type="website", jsonld=jsonld, body=body,
                      keywords=["digital marketing blog", "SEO guides", "generative engine optimization", "web design tips", "AI automation for business", "Toronto digital agency"])

def build_feed(posts):
    items = ""
    for p in posts:
        u = f"{SITE}/blog/{p['slug']}.html"
        items += f"""    <item>
      <title>{html.escape(p['title'])}</title>
      <link>{u}</link>
      <guid>{u}</guid>
      <pubDate>Fri, 20 Nov 2026 09:00:00 GMT</pubDate>
      <category>{html.escape(p['category'])}</category>
      <description>{html.escape(p['desc'])}</description>
    </item>
"""
    return f"""<?xml version="1.0" encoding="UTF-8"?>
<rss version="2.0">
  <channel>
    <title>Novifaro Blog</title>
    <link>{SITE}/blog.html</link>
    <description>Digital marketing, SEO, web design, and AI systems insights from Novifaro in Toronto.</description>
    <language>en-ca</language>
{items}  </channel>
</rss>
"""

def main():
    by_slug = {p["slug"]: p for p in POSTS}
    os.makedirs(os.path.join(ROOT, "blog"), exist_ok=True)
    for p in POSTS:
        for r in p["related"]:
            assert r in by_slug, r
        with open(os.path.join(ROOT, "blog", p["slug"] + ".html"), "w") as f:
            f.write(build_post(p, by_slug))
    with open(os.path.join(ROOT, "blog.html"), "w") as f:
        f.write(build_index(POSTS))
    with open(os.path.join(ROOT, "blog", "feed.xml"), "w") as f:
        f.write(build_feed(POSTS))
    print("built", len(POSTS), "posts")

if __name__ == "__main__":
    main()

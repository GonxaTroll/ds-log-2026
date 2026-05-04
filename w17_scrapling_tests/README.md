# Week 17 - Scrapling tries

## Context
I came across [Scrapling](https://github.com/D4Vinci/Scrapling) through some LinkedIn posts referring to it as the new era of web scraping. In general it looks like a cleaner alternative to rolling custom Playwright scripts whenever scraping heavily protected or highly dynamic sites, so I decided to explore it.

## Overview
Two notebooks covering the library from basics to a real-world case:

- **`1_initial_tests.ipynb`** — Works through increasingly difficult login scenarios on a scraping sandbox site.
- **`2_real_example.ipynb`** — Applies the library to Zara's website (a highly dynamic SPA). Navigates the homepage, categorises internal links by section (woman/man/kids), lazy-loads all products in a category by scrolling, and extracts product metadata (name, price, fabric composition) from individual product pages by using interesting new features such as regular expression searches∫.

## Topics Covered
- Web scraping with Playwright-based sessions (`AsyncDynamicSession`, `AsyncStealthySession`)
- Anti-bot and Cloudflare bypass techniques
- Scraping dynamic/JS-heavy pages (infinite scroll, lazy loading)
- CSS selectors and regex-based extraction with Scrapling's API

## Notes
- CSRF tokens don't need to be handled manually when using a real browser session — Playwright takes care of it transparently.
- The stealth session (`AsyncStealthySession`) was enough to bypass most anti-bot layers without any extra configuration.

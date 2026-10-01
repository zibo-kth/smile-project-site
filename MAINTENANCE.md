# SMILE website maintenance

## Public profile

The website publishes only the one-page profile at
`docs/assets/cv/zibo-liu-public-cv-2026-10.pdf`. Its editable source is
`cv/zibo-liu-public-cv.html`.

The full academic CV is intentionally not published on this website. Do not add,
generate, link, or deploy a full-CV PDF from this repository.

## Related-research watch

The source of truth is `data/related-research.json`. Keep three or four recent items, use primary sources, label preprints clearly, and maintain topic balance.

After editing the data:

```bash
.venv/bin/python scripts/render_related_research.py --write
.venv/bin/python scripts/check_site.py
.venv/bin/mkdocs build --strict
.venv/bin/python scripts/check_rendered_site.py
```

The renderer enforces HTTPS source domains, publication status, freshness, summary length, and unique identifiers. The live introduction makes clear that external items are not SMILE outputs, partnerships, or endorsements.

## Release gate

Run the full source and rendered-site checks before committing. Review the mobile layout at 320 px and the desktop layout in a real browser, then verify the GitHub Pages deployment and live URLs after pushing.

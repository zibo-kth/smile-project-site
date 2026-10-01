# SMILE website maintenance

## Full public academic CV

The stable public file is `docs/assets/cv/zibo-liu-full-academic-cv.pdf`.

- Edit public academic content in `cv/zibo-liu-full-academic-cv.template.html`.
- Bibliometric values and the public update date live in `cv/public-cv-data.json`.
- Import current metrics from the private canonical CV and rebuild locally:

  ```bash
  .venv/bin/python scripts/build_public_cv.py --from-canonical --write --pdf --check
  ```

- When the template changes but metrics do not, add `--touch` to update the public date.
- The public version must omit private contact details, confidential or internal project material, and unpublished intellectual property. Only granted patents are listed.

PDF rendering uses the installed Windows Chrome on this WSL host. CI validates the committed generated HTML and PDF but does not regenerate the binary.

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

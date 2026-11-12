# Tools

`generate_assets.py` rebuilds the logo rasters, the original icon set (SVG + PNG 64/128/512), the icon preview sheet, and `assets/social-preview.png`.

It needs Pillow and cairosvg, which are **not** runtime dependencies of the starter:

```bash
python -m venv .venv
source .venv/bin/activate
pip install pillow cairosvg
python tools/generate_assets.py
```

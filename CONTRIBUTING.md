# Contributing to the Mate starter

Thanks for wanting to help. This repository is the open-source starter for [Mate](https://mate.fm/). The live shopping agent stays on mate.fm; changes here should keep the demo honest.

## Ways to help

- Improve intent parsing or add tests for real shopper phrasings
- Replace a demo provider with a clearly documented live adapter
- Fix docs, accessibility, or icon consistency
- Report bugs with the templates in `.github/ISSUE_TEMPLATE/`

## Ground rules

- Do not invent revenue, user counts, funding, partners, or cashback rates and present them as facts. Quote [mate.fm](https://mate.fm/) when you cite product claims, and label demo data as demo.
- mate.fm marks illustrated conversations as fictional. Don’t promote example codes or cashback amounts as real.
- Don’t add third-party merchant logos. Store names may appear as plain text.
- Don’t commit API keys, tokens, or personal data. Use environment variables, as in `.env.example`.
- Keep the runtime on the Python standard library unless a dependency is discussed in the pull request.

## Development

```bash
python -m unittest discover -s tests -v
python -m mate chat "cashback at Demo Shop"
```

Regenerate brand and icon assets (optional, needs Pillow and cairosvg):

```bash
python tools/generate_assets.py
```

Open a pull request against `main` with a short summary of what changed and why. Fill in the PR template.

By contributing, you agree that your work is licensed under the MIT License and that you will follow the [Code of Conduct](CODE_OF_CONDUCT.md).

# Security

## Reporting a vulnerability

Please **do not** open a public issue for a security problem in this starter.

Report it privately with GitHub’s advisory form on
https://github.com/YOUR-USERNAME/mate/security/advisories/new
(replace `YOUR-USERNAME` with the owner of the published repo).

Include:

- A description of the issue and its impact
- Steps to reproduce, or a proof that stays within this repository
- Any suggested fix, if you have one

We’ll acknowledge the report and work on a fix before any public disclosure.

## Scope

This starter is a local demo. It does not hold live shopper balances or
merchant credentials. Still in scope:

- Secret handling (`OPENROUTER_API_KEY`, `TWILIO_AUTH_TOKEN`)
- The Twilio signature check when it is enabled
- Path traversal or unexpected request handling in the stdlib HTTP server

Out of scope: the production service at [mate.fm](https://mate.fm/). Use that
product’s own support and legal channels for live-account issues.

## Secrets

Never commit `.env` files, API keys, or tokens. The code reads secrets only
from the environment. There are no default keys.

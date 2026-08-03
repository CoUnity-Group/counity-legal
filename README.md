# CoUnity Group — Legal

Published Terms of Service and Privacy Policy for CoUnity Group's Discord
applications, served via GitHub Pages.

**Live:** https://counity-group.github.io/counity-legal/

| Document | URL |
|---|---|
| Privacy Policy | https://counity-group.github.io/counity-legal/privacy/ |
| Terms of Service | https://counity-group.github.io/counity-legal/terms/ |

These two URLs are what belong in the **Terms of Service URL** and **Privacy
Policy URL** fields of each application in the
[Discord Developer Portal](https://discord.com/developers/applications). The
Developer Terms require a privacy policy that is actually reachable, so if these
pages ever 404 that is a live compliance gap — which is why they live in their own
repository rather than inside any one product's site.

## Editing

`src/*.md` is the source of truth. The HTML is generated.

```bash
python -m venv .venv
.venv/Scripts/python -m pip install markdown
.venv/Scripts/python build.py
```

Then commit both the changed markdown and the regenerated HTML. Keeping the
sources here means the published text has a readable diff history, which matters
for a document you may need to show the state of on a particular date.

Update the `Last updated` line in the source when you make a material change, and
give notice through the servers the applications run in — the Privacy Policy
commits to that.

## Notes for whoever maintains this

- **The pages are deliberately self-contained.** No fonts, no CDN, no JavaScript.
  A legal page has to render for anyone, on any device, years from now, and must
  not break because a design system changed. `build.py` output is checked for zero
  external asset loads.
- **`build.py` strips HTML comments.** The privacy source carries an internal note
  about not claiming a security control before it exists in production. That
  belongs in this repo, not in the page source of a public document.
- **No street address is published.** GDPR Art. 13 requires the controller's
  identity and contact details; the company name, location and a monitored
  `privacy@counity.xyz` satisfy that. Add a street address to `src/*.md` and
  rebuild if you later want one.
- **`privacy@counity.xyz` must stay monitored.** The Privacy Policy commits to
  acknowledging requests promptly and completing them within 30 days. An
  unmonitored address is worse than no address, because the commitment is public.

## Claims that depend on the code

The Privacy Policy's security section describes measures that must remain true.
Two are deliberately **not** claimed yet:

- Application-level encryption of the wallet↔Discord association. True for the
  Nado and xStocks bots, not yet for every application that stores one.
- Recording every export of personal data in an audit log. Partially implemented.

Both are marked in `src/privacy-policy.md`. Add them to the published text once
they hold everywhere — claiming a control you do not have is a misrepresentation,
and the order matters: ship the control, then the sentence.

# Release Checklist

Do not publish this package until the user explicitly approves public GitHub creation or push.

## Before Public Push

- [ ] Confirm repository name: `annotated-media-fix`.
- [ ] Confirm license: MIT.
- [ ] Confirm examples are synthetic and contain no private client/customer material.
- [ ] Confirm screenshots contain no secrets, personal data, customer data, or internal URLs.
- [ ] Run Python syntax checks.
- [ ] Run sample validation.
- [ ] Generate a fresh review canvas from the example media.
- [ ] Verify README image links render on GitHub.
- [ ] Decide whether to include the hosted demo URL. Default: do not include temporary URLs.

## Commands

```bash
python -m py_compile scripts/build_review_canvas.py scripts/find_latest_annotations.py scripts/validate_annotation_bundle.py
python scripts/validate_annotation_bundle.py --annotations examples/user-test-annotations.json --fix-brief examples/user-test-fix-brief.md
python scripts/build_review_canvas.py --media examples/demo-banner.svg --media-type image --out review.html --title "Banner review"
```

## Public Positioning

One-line description:

> A tiny review-canvas workflow that turns visual markup on images, video frames, slides, and UI screenshots into AI-readable fix JSON.

Suggested GitHub topics:

- `ai-tools`
- `visual-feedback`
- `annotation`
- `design-review`
- `codex`
- `local-first`

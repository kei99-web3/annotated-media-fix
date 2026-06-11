# Contributing

Thanks for considering a contribution.

This project is intentionally small and local-first. Good contributions usually improve one of these areas:

- clearer annotation schema
- better local file handoff
- safer validation
- better examples
- better review-canvas usability

## Development

Run the basic checks:

```bash
python -m py_compile scripts/build_review_canvas.py scripts/find_latest_annotations.py scripts/validate_annotation_bundle.py
python scripts/validate_annotation_bundle.py --annotations examples/user-test-annotations.json --fix-brief examples/user-test-fix-brief.md
python scripts/build_review_canvas.py --media examples/demo-banner.svg --media-type image --out review.html --title "Banner review"
```

## Scope

Please keep hosted upload, authentication, cloud storage, and automatic external AI calls out of the core project unless there is a clear design discussion first.

# Fix Brief

## Baseline
- Media: demo/demo-banner.svg
- Review HTML: demo/review-demo.html
- Annotation JSON: demo/user-test-annotations.json
- Editable source: demo/demo-banner.svg

## Fixes
| ID | Area | User mark | Required fix | Implementation source | Acceptance check |
| --- | --- | --- | --- | --- | --- |
| a01 | Circular media badge | Arrow to circle text | Center the badge text inside the circle | SVG text anchors | MEDIA and annotation text are horizontally centered on the circle |
| a02 | Top product label | Rectangle over blue label | Shrink the blue label to fit the text better | SVG rect width and text anchor | Label no longer feels oversized relative to the text |
| a03 | Upper right blank area | Rectangle over empty corner | Add a small cute illustration without competing with the main content | SVG decorative group | Upper right has a light accent and does not cover key copy |
| a04 | Lower left/cards and overall tone | Pen stroke across lower area | Improve type tone and background color while keeping the layout readable | SVG typography, fills, card styling | Overall tone is more polished and consistent |

## Generation Gate
- Deterministic source fixed: yes
- User ambiguity resolved: yes
- Exact text locked: yes
- Ready for image/video/slide generation: yes

## Verification
- Text readback: Demo Product Launch / Review Before Render / Mark corrections on this HTML canvas. / Fix list / source first / Generate / after approval / MEDIA / annotation
- Layout check: browser DOM confirmed the updated SVG loads in the review canvas at 1200x540 natural size
- Media-specific check: SVG XML parse passed
- Remaining risk: a03 "cute" is subjective and may need taste review

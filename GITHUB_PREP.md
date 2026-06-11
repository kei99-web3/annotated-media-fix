# GitHub Prep

## Repository

- Suggested name: `annotated-media-fix`
- Visibility at launch: public, approved and published on 2026-06-11
- License: MIT
- Primary language: Python
- Demo assets: synthetic only

## Description

Short:

> A local-first review canvas that turns visual markup into AI-readable fix JSON.

Long:

> Annotated Media Fix helps reviewers mark images, video frames, slides, and UI screenshots, then export structured JSON that an AI agent can validate and convert into deterministic source edits.

## Topics

- `ai-tools`
- `visual-feedback`
- `annotation`
- `design-review`
- `local-first`
- `codex`

## Suggested First Release

`v0.1.0`

Scope:

- local HTML review canvas
- JSON annotation schema
- local latest-export finder
- annotation/fix-brief validator
- synthetic before/after example

Not included:

- hosted upload
- authentication
- persistent cloud storage
- public API
- automatic external AI calls

## Launch Note Draft

I built a tiny local-first workflow for giving visual feedback to AI agents.

Instead of trying to describe "move this text" or "fix this empty area" in prose, you mark the image, write a note, and export JSON. The agent can then turn each mark into a concrete fix brief and edit the source.

It works well for images, video frames, slides, banners, and UI screenshots.

PC flow: save JSON locally.
Mobile flow: copy JSON into chat.

Repo: https://github.com/kei99-web3/annotated-media-fix

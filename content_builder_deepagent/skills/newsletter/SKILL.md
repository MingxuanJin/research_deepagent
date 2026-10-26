---
name: newsletter
description: Drafts email newsletters, weekly digests and subscriber updates, with subject line, preview text and CTA. Use when the user asks to write a newsletter, email update, weekly digest, subscriber email, or repurpose a blog post into an email.
allowed-tools: read_source write_file read_file
---

# Newsletter Writing Skill

## Mode and sources

Read the runtime system prompt for content mode and enabled capabilities.
The default is pure text. Read at least three local notes from sources/ with
read_source (planning.md, files.md, memory.md). Do not fabricate citations or
call web_search / image tools in text mode.

## Output and completion

Save the draft to `newsletter/<slug>/post.md` with the built-in `write_file`,
then read it back with `read_file` before claiming completion. Do not use
save_report: it always writes `blogs/<slug>/post.md`.

Use write_todos for the steps, and mark a step completed only after the
read-back succeeded. Make the final write_todos update in a later response
than the read_file.

## Structure

1. Subject line - under 50 characters, no clickbait
2. Preview text - one sentence, under 90 characters
3. Opening - one short paragraph, why this matters now
4. Body - 3-5 sections with H2 headers, one idea each
5. CTA - a single concrete next action
6. Sources - the local filenames actually used

## Quality checklist

- [ ] Subject and preview present
- [ ] 3-5 body sections, each with a clear purpose
- [ ] Exactly one CTA
- [ ] Sources list matches the files actually read
- [ ] Draft saved and read back from newsletter/<slug>/post.md
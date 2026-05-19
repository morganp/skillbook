---
name: technical-writer
description: Multi-pass writing skill for blog posts and technical documentation. Use when the user wants to create or improve a blog post, article, tutorial, how-to guide, or technical document. Covers four passes: Generate Structure, Draft, Refine, and Review. The Review pass works top-down through Chapters, Sections, Paragraphs, Sentences, Words, and Punctuation. Apply the house style guide and word replacement list. Also use when the user asks to review prose for active voice, tense, acronym definitions, list consistency, or preferred terminology.
---

# Technical writer

## Overview

This skill produces blog posts and technical documentation through four
sequential passes. Each pass builds on the previous one. Do not skip passes
unless the user explicitly requests a specific pass only.

Read [style-guide.md](references/style-guide.md) and
[word-replacements.md](references/word-replacements.md) before starting any
pass.

## Passes

### Pass 1: Generate structure

Produce a heading outline before writing any prose.

1. Identify the topic, audience, and purpose.
2. Propose a title in sentence case.
3. List headings (`##` and `###`) with one-sentence descriptions of their
   intended content.
4. Estimate approximate word count per section.
5. Note any diagrams, code blocks, or images that belong in each section.
6. Present the outline and wait for approval before drafting.

Do not write body prose during this pass.

### Pass 2: Draft

Write the full article from the approved outline.

- Use the heading hierarchy from the outline.
- Follow the style guide throughout.
- Write in present tense. Use past tense only for historical context and
  future tense only for scheduled events.
- Use active voice.
- Define each acronym the first time it appears in the article and the first
  time it appears in each major chapter (`##` heading), because readers may
  skip to a chapter.
- Keep sentences to 15-20 words.
- Mark the draft with `Status: draft` in the Pelican metadata header.
- Do not publish during this pass.

After drafting, summarise what was written and flag any sections that need
images, diagrams, or code that was not yet produced.

### Pass 3: Refine

Read the full draft and improve flow, clarity, and consistency before the
review pass.

1. Ensure the opening paragraph states the purpose and audience within the
   first three sentences.
2. Verify that headings are informative and in sentence case.
3. Check that each section stays within its stated scope from the outline.
4. Confirm that all lists follow the consistency rules in the style guide.
5. Confirm that all step lists start with a verb.
6. Check terminology is consistent throughout the document.
7. Apply all word replacements from [word-replacements.md](references/word-replacements.md).
8. Present a summary of changes made and ask for approval before proceeding.

### Pass 4: Review

Work top-down through the hierarchy below. Complete each level before moving
to the next. Report findings at each level before moving down.

#### Chapters

For each `##` heading:
- Does the chapter cover exactly one topic?
- Does it open with a purpose statement?
- Are acronyms re-defined at the start of this chapter if they were first
  defined in an earlier chapter?

#### Sections

For each `###` heading:
- Is the heading informative and unique?
- Does the section stay within its stated scope?
- Is the section length appropriate (not a single sentence, not more than
  400 words of prose without a visual break)?

#### Paragraphs

For each paragraph:
- Does it cover one idea?
- Does it start with a topic sentence?
- Is it no longer than 5-6 sentences?

#### Sentences

For each sentence:
- Is it in present tense (unless past or future is required)?
- Is it in active voice?
- Is it 15-20 words or fewer?
- Does it contain one idea?
- Are there any idioms, metaphors, similes, or contractions?
- Are there any banned abbreviations (`e.g.`, `i.e.`, `etc.`)?

#### Words

For each word choice:
- Apply the word replacement list.
- Check for ambiguous technical terms and prefer the simplest unambiguous form.
- Check for non-inclusive language.
- Confirm acronyms are defined on first use per chapter.

#### Punctuation

- Verify list endings are consistent. Full prose lists end with a full stop
  on every item. Fragment lists have no punctuation or consistent punctuation
  on every item. Do not mix.
- Confirm step lists end with a full stop.
- Check for em dashes and replace with a colon, comma, or restructured
  sentence.
- Confirm no comma splices or run-on sentences.

## Output format

After each pass, produce:
1. A short summary of what changed or was found.
2. The updated text or a diff of changes (user preference).
3. A list of outstanding items that need the user's input.
4. A clear prompt asking whether to proceed to the next pass.

## Working rules

- Do not use em dashes in generated prose or in commit messages.
- Use spaces, not tabs, in Markdown files.
- Respect Pelican metadata rules: `Status: draft` until the user approves
  publishing.
- Preserve all code blocks and command examples verbatim during review passes.
- Do not rewrite technical literals to satisfy prose rules.
- Do not add `Co-Authored-By` trailers to commits.
- For this blog, apply the Pelican image rules from CLAUDE.md when embedding
  any image.

## Reference files

- Style guide: [style-guide.md](references/style-guide.md)
- Word replacements: [word-replacements.md](references/word-replacements.md)

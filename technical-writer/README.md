# technical-writer

Multi-pass writing skill for blog posts and technical documentation.

## Trigger

Invoke with `/technical-writer`, or auto-triggers when you ask to write a
blog post, article, tutorial, how-to guide, or technical document.

Also triggers for prose review tasks: active voice, tense, acronym
definitions, list consistency, or preferred terminology.

## Four passes

| Pass | What it does |
|------|-------------|
| 1. Generate structure | Produces a heading outline and waits for approval. No prose written yet. |
| 2. Draft | Writes the full article from the approved outline. Creates a `Status: draft` Pelican post. |
| 3. Refine | Improves flow, consistency, and terminology. Applies all word replacements. |
| 4. Review | Top-down hierarchical review (see below). |

Each pass ends with a summary and a prompt to proceed.

## Review hierarchy (Pass 4)

Works top-down. Completes each level before moving to the next.

1. **Chapters** - one topic per chapter, purpose statement, acronyms re-defined
2. **Sections** - informative headings, correct scope, appropriate length
3. **Paragraphs** - one idea, topic sentence, max 5-6 sentences
4. **Sentences** - present tense, active voice, 15-20 words, one idea
5. **Words** - apply word replacement list, check ambiguous technical terms
6. **Punctuation** - list ending consistency, no em dashes, no run-ons

## Key style rules

- Present tense by default.
- Active voice.
- Define acronyms on first use per article and per `##` chapter.
- All list items end consistently: full stops for prose lists, consistent
  punctuation or none for fragment lists.
- Step lists start with an imperative verb and end with a full stop.
- No em dashes. Use a colon, comma, or restructured sentence.
- Sentences target 15-20 words.

## Reference files

- `references/style-guide.md` - full style rules
- `references/word-replacements.md` - growing table of preferred terms

## Extending the word list

Add rows to `references/word-replacements.md` when you identify a vague or
ambiguous term and its preferred replacement. Table is sorted alphabetically
by the "avoid" column. Format: `| avoid | use | reason |`

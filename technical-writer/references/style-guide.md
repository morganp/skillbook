# Technical writing style guide

## Audience and tone

- Write for a technical audience that includes non-native English speakers.
- Address the reader as a knowledgeable colleague.
- Avoid formal or pedantic language.
- Avoid colloquial language.

## Tense

- Use present tense as the default.
- Use past tense only for historical context.
- Use future tense only for events scheduled to happen.

## Voice

- Use active voice.
- Rewrite passive constructions unless the actor is unknown or irrelevant.

## Sentence length and structure

- Target 15-20 words per sentence.
- Express one idea per sentence.
- Prefer simple sentence structures over compound or complex ones.
- Prefer single-word verbs over phrasal verbs where possible.

## Word choice

- Use US English spelling.
- Use `Merriam-Webster` as the default dictionary.
- Prefer the simplest unambiguous word.
- Avoid `e.g.`, `i.e.`, and `etc.`; write them out: `for example`, `that is`.
- Avoid metaphors, idioms, similes, and culture-specific phrases.
- Avoid contractions.
- Do not use `please`.
- Do not use emotional language.
- Avoid slashes in prose for alternatives; use `or`.

## Acronyms

- Define each acronym the first time it appears in the article.
- Re-define each acronym the first time it appears in each `##` chapter,
  because readers may enter the document at a chapter heading.
- Do not define acronyms in headings.

## Lists

- Use a list when there are three or more parallel items.
- Ensure all list items have consistent endings:
  - Full prose items: end every item with a full stop.
  - Fragment items: no punctuation, or consistent punctuation on every item.
  - Do not mix punctuated and unpunctuated items in the same list.
- Step lists (numbered procedures):
  - Start every step with an imperative verb.
  - End every step with a full stop.
  - Follow the order of usage (for example: install, then configure, then verify).
  - Exception: if the actor is external (for example, a foundry or third-party process), imperative verbs are misleading. Use a descriptive numbered list instead: bold label, colon, then description. End each item with a full stop.

## Headings

- Use sentence case for all headings.
- Make headings informative and unique.
- Use active verbs for task headings.
- Avoid abbreviations in headings.
- Use a colon, not a hyphen, for heading sub-labels.
- Do not use punctuation at the end of headings.

## Paragraphs

- Open each paragraph with a topic sentence.
- Cover one idea per paragraph.
- Limit paragraphs to 5-6 sentences.

## Accessibility and inclusivity

- Provide descriptive alt text for all images.
- Use gender-neutral pronouns (`they`, `their`).
- Replace non-inclusive legacy terms:
  - `master/slave` -> `primary/secondary`
  - `whitelist/blacklist` -> `allowlist/denylist`
  - `sanity check` -> `validation` or `quick check`
  - `kill` (process termination context) -> `stop` or `terminate`

## Numbers and units

- Use numerals for all numbers (1, 2, 3).
- Add a space between a number and its unit: `3.3 V`, `100 MHz`.
- Use symbols correctly: `%`, `°`, `Ω`.
- Write `half` instead of `1/2`.
- Binary: `0b...` Hex: `0x...` Bit ranges: `[7:0]`

## Code and technical literals

- Use code blocks for commands, code samples, and multi-line output.
- Use inline code for file names, function names, variable names, and flags.
- Do not rewrite technical literals to satisfy prose rules.

## Notices

Use standardised notice labels:

| Label | Use |
|-------|-----|
| Note | Helpful tips or additional context. |
| Caution | Risk to functionality if the reader proceeds. |
| Warning | Risk to the system or data. |
| Danger | Risk of personal harm. |

## Formatting

- Use spaces, not tabs.
- Do not use bold, italics, or ALL CAPS for emphasis.
- Use bold for GUI element labels only.
- Use italics for document and book titles only.
- Do not use em dashes. Use a colon, a comma, or restructure the sentence.
- Avoid parentheses when a direct sentence works.

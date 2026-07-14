# Copy Discipline: presented, not read

The single most important rule: **the deck is shown to a person while someone
talks over it.** The CEO reads faster than the presenter speaks, so words on the
slide compete with the presenter. Strip the slide; arm the presenter.

## The rules

1. **One claim per slide.** A slide makes one argument the audience can agree or
   disagree with. If it has two ideas, split it.
2. **The headline IS the argument.** Write it as a sentence with a point of view.
   - Bad (label): "Competitive landscape" / "The workforce"
   - Good (claim): "Today, nothing sets us apart." / "An AI workforce, across the business."
3. **Word budget per slide:** either **≤3 short bullets** OR **~6 concise flank
   points** (3 either side of a centred diagram). Nothing else.
4. **Sentence length:** roughly **6–16 words**. Long enough to carry a real
   point, short enough to scan in one glance. Avoid the two failure modes:
   5-word fragments that look bunched, and full paragraphs nobody reads.
5. **One hero stat per data slide.** A single big number, isolated, that beats
   or undercuts expectation. Four competing numbers = three too many.
6. **NO EM DASHES.** Not on slides, not in notes. Use a comma, a colon, or two
   sentences. (Em dashes read as machine-written and the client asked for none.)
   Run a check before finishing: search the deck for the em-dash character and
   `&mdash;`; both must be zero. Ranges may use an en dash (`60–80%`).
7. **No jargon the presenter would have to defend.** If a phrase is opaque
   ("CV rendered on demand"), reword to the value ("a CV tailored to each job")
   or cut it.

## Where the argument lives: cue cards

Every slide carries hidden **speaker notes** for the presenter, shown with `N`.
Write them as a short bulleted cue card, not prose. This is where the depth,
the killer line, the framing, and the sensitivity flags go.

```html
<div class="snote" hidden><ul class="cue">
  <li>The point to land: <span class="say">"a bulletin board can't make money telling you not to apply. We can."</span></li>
  <li>Depth/detail the slide omits, in plain bullets.</li>
  <li><span class="flag">Sensitive: frame as leverage, not cuts.</span></li>
</ul></div>
```

- `.say` = a verbatim line to say out loud.
- `.flag` = a caution (sensitive number, "don't push this with this audience",
  "if asked for figures, defer to a follow-up").
- Notes can be fuller than slides, but stay scannable. The presenter glances,
  they don't read aloud.

## "Go broad" vs "go deep"

Some slides should show **breadth** (a whole team / feature set) rather than
depth on one thing. For these, use a **menu** (a grid of many named items) or a
**chip strip** ("the full surface") under the main points, with the most
important items highlighted. Going broad on the right slide is what entices an
executive ("look how much there is"), so don't force every slide to three deep
bullets.

## Self-check before done

- [ ] Every headline is a sentence with a point of view.
- [ ] No slide exceeds 3 bullets or 6 flank points.
- [ ] Zero em dashes (slides + notes).
- [ ] Each data slide has exactly one hero number.
- [ ] The real argument is in the cue cards, not on the slides.
- [ ] No unvetted claims or undefendable jargon on any slide.

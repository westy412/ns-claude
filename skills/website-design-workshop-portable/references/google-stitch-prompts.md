# Google Stitch Prompt Crafting

> **When to read:** When generating Google Stitch prompts for a brand, typically in Phase 4 after the brand brief is complete.

Google Stitch is an AI-powered UI design tool from Google Labs that generates website designs from text prompts. This reference covers how to craft effective prompts from brand brief data.

---

## What Google Stitch Does

- Generates visual UI designs from natural language prompts
- Accepts text descriptions and optional reference images
- Outputs visual designs exportable to Figma
- Produces multiple variations per prompt
- Does NOT output production code -- it outputs design artefacts

---

## Prompt Structure

A well-crafted Stitch prompt combines these elements:

### Required Elements

| Element | Source in Brand Brief | Example |
|---------|----------------------|---------|
| Product context | Brand overview | "A landing page for a B2B SaaS analytics platform" |
| Page type | Sitemap / page list | "homepage", "about page", "services page" |
| Visual style | Layout preferences + imagery | "Modern and minimal" |
| Color palette | Color scheme | "Dark navy (#1a1a2e) and electric blue (#4cc9f0)" |
| Key sections | Page sections | "Hero with headline and CTA, 3-column feature grid" |

### Recommended Elements

| Element | Source in Brand Brief | Example |
|---------|----------------------|---------|
| Typography direction | Typography | "Clean sans-serif, bold headings" |
| Spacing/density | Layout preferences | "Generous white space" |
| Tone/mood | Copywriting style | "Professional but approachable" |
| Target audience | Brand overview | "Targeting enterprise data teams" |

---

## Writing the Prompt

### Formula

Combine elements into 3-5 sentences:

1. **What it is + who it's for** (product context + audience)
2. **Visual direction** (style + color + typography)
3. **Page sections** (what content blocks appear, in order)
4. **Tone and feel** (mood + spacing + personality)

### Example Prompt

```
A homepage for a premium accounting firm targeting UK SMEs. 
Clean, professional design with a navy (#1B2A4A) and gold (#C9A84C) 
color palette. Serif headings with sans-serif body text. 
Include: a hero section with headline, subheadline and "Book a Consultation" 
CTA; a 3-column services overview with icons; a trust signals bar 
(accreditations and client logos); testimonials carousel; and a 
contact section with embedded form. Spacious layout with generous 
white space, light background, understated elegance.
```

---

## One Prompt Per Page

Generate a separate Stitch prompt for each page in the brand's sitemap. Each prompt should:
- Be self-contained (don't reference other prompts)
- Include the brand's visual identity (colors, typography, style) even if repeated across prompts
- Specify the sections unique to that page
- Note any page-specific interactions or features

### Naming Convention

Save each prompt as: `{page-name}-v{N}.md`

Examples:
- `homepage-v1.md`
- `about-v1.md`
- `services-v1.md`
- `contact-v1.md`
- `homepage-v2.md` (iteration after feedback)

---

## Iterating on Prompts

When the user wants to refine a Stitch prompt:
1. Create a new version file (v2, v3, etc.)
2. Note what changed from the previous version in the file
3. Keep previous versions for reference
4. Update the prompt based on feedback

Common iteration patterns:
- **More detail on a section:** Add specifics about content, layout, or interaction
- **Different style direction:** Adjust the visual descriptors
- **Add/remove sections:** Modify the content block list
- **Responsive focus:** Add mobile-specific guidance

---

## Tips for Effective Prompts

- **Be specific about colors** -- use hex codes, not just "blue"
- **Name the sections in order** -- Stitch uses section order for layout hierarchy
- **Include content hints** -- "headline about data-driven insights" beats just "headline"
- **Describe the feeling** -- "luxury", "startup energy", "trustworthy" sets the mood
- **Mention what to avoid** -- if the client has anti-preferences, add "avoid X" at the end
- **Keep it under 200 words** -- focused prompts produce better results than exhaustive ones

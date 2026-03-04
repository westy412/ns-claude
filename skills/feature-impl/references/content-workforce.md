# Content Creation Workforce - Product Reference

## Overview

Turn-key content factory for multi-platform social media content creation. Users create posts, campaigns, and ideas for their entities/brands, with AI-powered drafting, iteration, repurposing, and publishing across platforms.

## Target Platforms

- LinkedIn (organic posts, carousels, infographics)
- Twitter/X (tweets, threads)
- Substack (articles)
- YouTube (video scripts, collateral)
- TikTok (video scripts)
- Facebook (posts)

## Key Concepts

**Entity** — A brand or client. Users can have access to multiple entities. All content is scoped to an entity.

**Campaign** — A high-level content concept with a title, summary, and thematic focus. Posts belong to campaigns.

**Post** — A piece of content going through stages: idea → drafting → ready → published. A post has a content type (e.g., Thought Leadership), format (e.g., Carousel), platform, and one or more drafts.

**Draft** — A specific version of post content. Drafts go through Planning → Creation → Critic loops.

**Idea** — Proactive AI-generated campaign/post suggestions based on entity guidelines and content pillars.

## Application Structure

### Pages & Components

| Page/Component | Route | What It Does |
|----------------|-------|--------------|
| **Dashboard** | `/` | Overview, calendar, recent activity |
| **Post List** | `/posts` | Browse all posts across entities |
| **Post Detail** | `/posts/[id]` | Multi-tab editor for a single post |
| **Post Creation** | `/posts/new` | Create a new post |
| **Campaign List** | `/campaigns` | Browse campaigns |
| **Campaign Detail** | `/campaigns/[id]` | View/edit campaign details and posts |
| **Campaign Creation** | `/campaigns/new` | Create a new campaign |
| **Idea List** | `/ideas` | Browse AI-generated ideas |
| **Idea Detail** | `/ideas/[id]` | Review/approve/reject an idea |
| **Analytics** | `/analytics` | Performance metrics across posts |
| **Calendar** | `/calendar` | Schedule view |
| **Nova Chat** | `/nova/[id]` | AI assistant conversations |
| **Settings** | `/settings/*` | Entity configuration |

### Post Detail Tabs

The post detail page (`/posts/[id]`) has 9 tabs, each with specific functionality:

| Tab | Route | What It Does |
|-----|-------|--------------|
| **Details** | `/posts/[id]?tab=details` | Basic post info (campaign, content type, format, platform, status) |
| **Content** | `/posts/[id]?tab=content` | Draft editing — the main text content of the post |
| **Metadata** | `/posts/[id]?tab=metadata` | Hashtags, titles, descriptions |
| **Images** | `/posts/[id]?tab=images` | AI-generated images for the post |
| **Infographic** | `/posts/[id]?tab=infographic` | Infographic generation (LinkedIn) |
| **Carousel** | `/posts/[id]?tab=carousel` | Carousel slide creation (LinkedIn) |
| **Hooks** | `/posts/[id]?tab=hooks` | Opening lines / attention-grabbing hooks |
| **Transcript** | `/posts/[id]?tab=transcript` | Video transcript upload for video posts |
| **Preview** | `/posts/[id]?tab=preview` | Final preview before publishing |

### Settings Sub-Pages

All settings pages are entity-scoped (configure a specific brand/entity):

| Route | What It Configures |
|-------|-------------------|
| `/settings` | General entity settings |
| `/settings/brand-guidelines` | Brand voice, tone, messaging |
| `/settings/style-guidelines` | Writing style, content guidelines |
| `/settings/content-pillars` | Thematic content categories |
| `/settings/content-manifesto` | Entity content manifesto document |
| `/settings/connected-accounts` | OAuth for LinkedIn, Twitter, etc. |
| `/settings/reference-images` | Brand imagery for AI image generation |
| `/settings/carousel-templates` | Custom carousel slide templates |
| `/settings/whatsapp` | WhatsApp integration settings |

## Component Map

The AI classifies feedback into these functional components (from the analyze-feedback agent):

| Component | What It Covers |
|-----------|----------------|
| **Content Drafting** | Writing/editing the main post text, draft editor UI |
| **Content Iteration** | Revision workflow based on feedback |
| **Images & Image Generation** | AI image requests, image generation, image display |
| **Hooks** | Opening line generation and selection |
| **Carousel** | Carousel slide creation/editing (LinkedIn) |
| **Infographic** | Infographic generation (LinkedIn) |
| **Metadata & Hashtags** | Hashtags, titles, descriptions generation |
| **Post Preview** | Final preview before publishing |
| **Post Transcript** | Video transcript upload/processing |
| **Post Details & Settings** | Post-level config (campaign, type, format, platform) |
| **Post List** | Browse/filter/search posts |
| **Post Creation** | New post creation flow |
| **Campaign Detail** | Campaign view/edit |
| **Campaign List** | Campaign browsing |
| **Campaign Creation** | New campaign creation |
| **Idea Generation** | AI-generated ideas |
| **Idea List** | Browse ideas |
| **Publishing** | Publishing flow to platforms |
| **Dashboard** | Main dashboard |
| **Analytics** | Performance metrics |
| **Calendar** | Schedule view |
| **Nova Chat** | AI assistant |
| **Settings - [specific]** | Entity configuration pages |
| **Navigation & Layout** | Cross-cutting UI (sidebar, navigation, layout) |
| **Authentication** | Login, signup, auth flows |
| **General** | Anything that doesn't fit above |

## Common User Workflows

**Content creation flow:**
1. User creates a campaign or idea
2. Creates a post within the campaign
3. AI generates initial draft (Planning → Research → Creation → Critic loop)
4. User reviews draft, provides feedback if needed
5. AI iterates on draft based on feedback
6. User generates metadata, hooks, images, carousel, infographic (parallel workflows)
7. User publishes to platform(s)

**Iteration flow:**
1. User opens post detail
2. Provides feedback via FeedbackPanel (inline checklist on content tab)
3. Clicks "Iterate" button
4. AI revises draft based on feedback

**Idea flow:**
1. AI proactively generates campaign/post ideas (background workflow)
2. User browses ideas in `/ideas`
3. User approves an idea → creates campaign/post from it

## Data State Progression

Posts have a `status` field that tracks their lifecycle:

```
idea → drafting → ready → published
```

- **idea** — Post created from an idea, no draft yet
- **drafting** — Draft generation in progress or user editing
- **ready** — Draft approved, ready to publish
- **published** — Published to platform(s)

## Common Pain Points (from historical feedback)

Based on patterns in existing feature requests:

- **Image generation** — Slow, quality issues, not matching brand style
- **Carousel formatting** — Alignment, text overflow, template customization
- **Content iteration** — Feedback not being applied correctly, too many revision loops
- **Publishing flow** — Errors, missing confirmation, unclear status
- **Metadata generation** — Hashtags don't match content, titles too generic
- **Draft editor** — Formatting issues, losing work, slow to load

Use this context when reviewing feature requests to understand the user's pain and the system's behavior.

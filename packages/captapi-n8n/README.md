# n8n-nodes-captapi

This is an [n8n](https://n8n.io) community node. It lets you use **[Captapi](https://captapi.com)** in your n8n workflows.

Captapi turns YouTube, TikTok, Instagram, Facebook, X (Twitter), Reddit, Threads, Bluesky, Pinterest, LinkedIn, Rumble, Truth Social, Kick, Kwai, Komi, Pillar, Linkbio, Linkme and Amazon Shop URLs into clean, structured JSON — transcripts, AI summaries, comments, video/post details, profile & channel stats, search, commerce data, downloads and account usage. One API key, **170 operations** across 27 platforms.

[Installation](#installation) · [Credentials](#credentials) · [Operations](#operations) · [Usage](#usage) · [Resources](#resources)

## Installation

Follow the [community nodes installation guide](https://docs.n8n.io/integrations/community-nodes/installation/) in the n8n docs.

In your n8n instance:

1. Go to **Settings → Community Nodes**.
2. Select **Install**.
3. Enter `n8n-nodes-captapi` as the npm package name.
4. Agree to the risks and select **Install**.

The **Captapi** node and **Captapi API** credential will then be available.

## Credentials

You need a Captapi API key:

1. Create a free account at [captapi.com](https://captapi.com).
2. Open **Dashboard → API Keys** and copy a key.
3. In n8n, create a new **Captapi API** credential and paste the key.

The credential test calls `/v1/account/limits` to confirm the key works. `Base URL` defaults to `https://api.captapi.com` and rarely needs changing.

## Operations

Pick a **Platform** (YouTube, TikTok, Instagram, Facebook, X/Twitter, Reddit, Threads, Bluesky, Pinterest, LinkedIn, Rumble), then an **Operation**. Highlights per platform:

- **YouTube** — Transcript, Summarizer, Video/Channel Details, Comments, Search, Channel Videos/Shorts/Streams/Playlists, Community Posts, Comment Replies, Downloads.
- **TikTok** — Transcript, Summarizer, Video/Channel Details, Comments, Search, Channel Posts, Followers/Followings, Music Posts, Song Details, Trending Feed, Popular Hashtags, Downloads.
- **Instagram** — Transcript, Summarizer, Post/Reel Details, Comments, Channel Posts/Reels, Reels/Hashtag/Profile Search, Story Highlights, Tagged & Music Posts, Embed, Downloads.
- **Facebook** — Details, Transcript, Summarizer, Comments, Page Details, Profile Posts/Reels, Group Posts, Comment Replies.
- **X (Twitter)** — Tweet Details, Profile, User Tweets, Search.
- **Reddit** — Subreddit Posts, Post Details, Post Comments, Search.
- **Threads** — Profile, User Posts, Post Details.
- **Bluesky** — Profile, User Posts, Post Details.
- **Pinterest** — Pin Details, User Pins, Search.
- **LinkedIn** — Profile, Company, Post Details.
- **Rumble** — Video Details, Channel Videos, Search.

Each operation maps 1:1 to a Captapi REST endpoint and exposes exactly the inputs that endpoint accepts (e.g. `URL`, `Query`, `Limit`, `Language`, `Comment ID`).

## Usage

A minimal flow: **Manual Trigger → Captapi**.

1. Add the **Captapi** node.
2. Platform: `YouTube`, Operation: `YouTube Transcript`.
3. URL: `https://youtube.com/watch?v=dQw4w9WgXcQ`.
4. Execute — the node returns the transcript JSON.

Pricing is credit-based and per result; cached responses are free and failed requests are never charged. See [captapi.com/pricing](https://captapi.com/pricing).

## Resources

- [Captapi documentation](https://captapi.com/docs)
- [n8n community nodes docs](https://docs.n8n.io/integrations/community-nodes/)

# Captapi Instagram AI avatar agent

The agent creates one 9:16 Captapi developer ad every day:

1. Chooses a rotating content pillar based on the weekday.
2. Reads recent Instagram captions to reduce repetition.
3. Writes a 15-25 second creative as Mara, Captapi's disclosed AI CMO.
4. Renders a 1080x1920 HeyGen Avatar IV video with burned-in captions.
5. Saves the creative JSON and MP4 as a GitHub Actions artifact.
6. Optionally publishes the video as an Instagram Reel through Meta's official
   Content Publishing API.

## Estimated monthly cost

Avatar IV photo avatars are billed per output second. Thirty 20-second videos
are roughly 10 output minutes. At the current self-serve rate of about
$3/minute, budget approximately $30/month for HeyGen rendering, plus a small
LLM cost.

## 1. Create Mara in HeyGen

1. Open the HeyGen API dashboard and add at least $5 to the pay-as-you-go
   wallet.
2. Create or select a consistent female AI avatar for Mara.
3. Select one English voice and keep it fixed.
4. Copy the API key, avatar ID, and voice ID.

The agent uses Avatar IV via HeyGen Studio API and a dark Captapi background.

## 2. Prepare Instagram

Automatic Reel publishing requires:

1. An Instagram Professional/Business account.
2. A Meta app with Instagram content-publishing permission.
3. The professional Instagram user ID.
4. A long-lived user access token.

Meta fetches the completed video directly from HeyGen, polls the media
container until it is ready, and then publishes it. The agent never prints the
access token.

## 3. GitHub repository secrets

Add:

- `OPENAI_API_KEY`
- `HEYGEN_API_KEY`
- `HEYGEN_AVATAR_ID`
- `HEYGEN_VOICE_ID`
- `META_IG_USER_ID`
- `META_ACCESS_TOKEN`

Repository variables:

- `INSTAGRAM_SCRIPT_MODEL` (optional; default `gpt-4o-mini`)
- `INSTAGRAM_AUTO_PUBLISH` — keep `false` during the review period.

## 4. Test safely

Creative only, with no HeyGen charge:

```powershell
python scripts/instagram_avatar_agent.py --dry-run
```

Generate the Reel but do not publish:

```powershell
python scripts/instagram_avatar_agent.py
```

Generate and publish immediately:

```powershell
python scripts/instagram_avatar_agent.py --publish
```

The scheduled workflow runs every day at 15:00 UTC. Manual workflow runs have a
separate **Publish** checkbox. Generated files are retained as workflow
artifacts for 14 days.

## Rollout rule

Keep `INSTAGRAM_AUTO_PUBLISH=false` until at least seven generated videos have
been reviewed. Turn it on only if:

- the avatar and voice remain consistent;
- scripts contain no unsupported claims;
- burned-in captions are readable on a phone;
- average duration remains between 15 and 25 seconds;
- the CTA and topic are not repetitive.

/**
 * Extra success examples for endpoints with multiple request modes.
 * Kept separate from api-examples.generated.ts so `gen_examples.py` cannot wipe them.
 */
export const API_EXAMPLE_VARIANTS: Record<
  string,
  Array<{ label: string; data: Record<string, unknown> }>
> = {
  "kick-clip": [
    {
      label: "Channel mode",
      data: {
        channelUrl: "https://kick.com/xqc",
        totalReturned: 2,
        clips: [
          {
            platform: "kick",
            id: "clip_01KZ98ERXB58SMTR7C8CTEK6PJ",
            url: "https://kick.com/xqc/clips/clip_01KZ98ERXB58SMTR7C8CTEK6PJ",
            title: "friendliest xqc interaction",
            createdAt: "2026-08-05T15:27:27.727198Z",
            durationSeconds: 78,
            views: 1,
            likes: 0,
            thumbnailUrl:
              "https://clips.kick.com/clips/cc/clip_01KZ98ERXB58SMTR7C8CTEK6PJ/thumbnail.webp",
            videoUrl:
              "https://clips.kick.com/clips/cc/clip_01KZ98ERXB58SMTR7C8CTEK6PJ/playlist.m3u8",
            videoType: "hls",
            hlsUrl:
              "https://clips.kick.com/clips/cc/clip_01KZ98ERXB58SMTR7C8CTEK6PJ/playlist.m3u8",
            privacy: "public",
            isMature: false,
            livestreamId: "120500462",
            category: "Just Chatting",
            categoryId: "15",
            categorySlug: "just-chatting",
            parentCategory: "irl",
            channel: {
              id: "668",
              username: "xqc",
              displayName: "xQc",
              name: "xQc",
              url: "https://kick.com/xqc",
              profilePicture:
                "https://files.kick.com/images/user/676/profile_image/conversion/151f289a-5bff-4f31-b125-0c54c542519e-thumb.webp",
            },
            creator: {
              id: "26465983",
              username: "pepethefrogs",
              displayName: "pepethefrogs",
              name: "pepethefrogs",
              url: "https://kick.com/pepethefrogs",
            },
          },
          {
            platform: "kick",
            id: "clip_01KZ8G82TS1Q6T1F1660DWVEJ7",
            url: "https://kick.com/xqc/clips/clip_01KZ8G82TS1Q6T1F1660DWVEJ7",
            title: "asdasdasd",
            createdAt: "2026-08-05T08:22:30.758808Z",
            durationSeconds: 23,
            views: 3,
            likes: 0,
            thumbnailUrl:
              "https://clips.kick.com/clips/62/clip_01KZ8G82TS1Q6T1F1660DWVEJ7/thumbnail.webp",
            videoUrl:
              "https://clips.kick.com/clips/62/clip_01KZ8G82TS1Q6T1F1660DWVEJ7/playlist.m3u8",
            videoType: "hls",
            hlsUrl:
              "https://clips.kick.com/clips/62/clip_01KZ8G82TS1Q6T1F1660DWVEJ7/playlist.m3u8",
            privacy: "public",
            isMature: true,
            livestreamId: "120396284",
            category: "Just Chatting",
            categoryId: "15",
            categorySlug: "just-chatting",
            parentCategory: "irl",
            channel: {
              id: "668",
              username: "xqc",
              displayName: "xQc",
              name: "xQc",
              url: "https://kick.com/xqc",
              profilePicture:
                "https://files.kick.com/images/user/676/profile_image/conversion/151f289a-5bff-4f31-b125-0c54c542519e-thumb.webp",
            },
            creator: {
              id: "50052941",
              username: "tobionekenobi",
              displayName: "TobiOneKenobi",
              name: "TobiOneKenobi",
              url: "https://kick.com/tobionekenobi",
            },
          },
        ],
      },
    },
  ],
};

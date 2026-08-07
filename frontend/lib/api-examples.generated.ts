// AUTO-GENERATED — do not edit by hand.
// Real example responses captured live from https://api.captapi.com.
// Arrays truncated to 2 items by default (keyPoints/topics/transcriptSegments/requests keep higher caps); HTML stubbed for SSR.
// Mode variants: frontend/lib/api-example-variants.ts (not overwritten).
// Regenerate: python backend/gen_examples.py (source: backend/api_snapshots.json).

export const API_EXAMPLES: Record<string, Record<string, unknown>> = {
  "account-balance": {
    "plan": "free",
    "monthlyQuota": 100,
    "subscriptionCredits": 0,
    "topupCredits": 9599,
    "totalCredits": 9599,
    "subscriptionRenewsAt": null,
    "usedThisMonth": 498,
    "quotaResetsAt": null,
    "keyName": "production",
    "rateLimitPerMinute": 40,
    "rateLimitRemaining": null,
    "monthly_quota": 100,
    "subscription_credits": 0,
    "topup_credits": 9599,
    "total_credits": 9599,
    "subscription_renews_at": null
  },
  "account-daily-usage": {
    "days": 7,
    "totalRequests": 251,
    "totalCreditsUsed": 498,
    "usage": [
      {
        "date": "2026-07-18",
        "requests": 251,
        "creditsUsed": 498,
        "successfulRequests": 242,
        "failedRequests": 9
      }
    ]
  },
  "account-most-used-routes": {
    "days": 30,
    "totalReturned": 5,
    "routes": [
      {
        "endpoint": "/v1/instagram/details",
        "platform": "instagram",
        "requests": 161,
        "creditsUsed": 46,
        "successfulRequests": 161,
        "failedRequests": 0
      },
      {
        "endpoint": "/v1/instagram/basic-profile",
        "platform": "instagram",
        "requests": 3,
        "creditsUsed": 2,
        "successfulRequests": 3,
        "failedRequests": 0
      }
    ]
  },
  "account-request-history": {
    "totalReturned": 5,
    "requests": [
      {
        "requestId": "a1b2c3d4-e5f6-7890-abcd-ef1234567890",
        "endpoint": "/v1/instagram/basic-profile",
        "platform": "instagram",
        "resource": "instagram_user:adencylnozturk",
        "resourceUrl": "instagram_user:adencylnozturk",
        "creditsUsed": 0,
        "cacheHit": true,
        "statusCode": 200,
        "responseTimeMs": 154,
        "errorMessage": null,
        "createdAt": "2026-07-18T11:31:44.31599+00:00"
      },
      {
        "requestId": "b2c3d4e5-f6a7-8901-bcde-f12345678901",
        "endpoint": "/v1/instagram/basic-profile",
        "platform": "instagram",
        "resource": "instagram_user:adencylnozturk",
        "resourceUrl": "instagram_user:adencylnozturk",
        "creditsUsed": 1,
        "cacheHit": false,
        "statusCode": 200,
        "responseTimeMs": 4980,
        "errorMessage": null,
        "createdAt": "2026-07-18T11:31:21.584147+00:00"
      },
      {
        "requestId": "c3d4e5f6-a7b8-9012-cdef-123456789012",
        "endpoint": "/v1/instagram/basic-profile",
        "platform": "instagram",
        "resource": "instagram_user:adencylnozturk",
        "resourceUrl": "instagram_user:adencylnozturk",
        "creditsUsed": 1,
        "cacheHit": false,
        "statusCode": 200,
        "responseTimeMs": 4168,
        "errorMessage": null,
        "createdAt": "2026-07-18T11:31:20.30634+00:00"
      },
      {
        "requestId": "d4e5f6a7-b8c9-0123-def0-234567890123",
        "endpoint": "/v1/pinterest/board",
        "platform": "pinterest",
        "resource": "https://www.pinterest.com/potterybarn/indigo-blues-lookbook/",
        "resourceUrl": "https://www.pinterest.com/potterybarn/indigo-blues-lookbook/",
        "creditsUsed": 3,
        "cacheHit": false,
        "statusCode": 200,
        "responseTimeMs": 17558,
        "errorMessage": null,
        "createdAt": "2026-07-18T11:29:07.873651+00:00"
      },
      {
        "requestId": "e5f6a7b8-c9d0-1234-ef01-345678901234",
        "endpoint": "/v1/facebook/marketplace-item",
        "platform": "facebook",
        "resource": "https://www.facebook.com/marketplace/item/2228870800986975/",
        "resourceUrl": "https://www.facebook.com/marketplace/item/2228870800986975/",
        "creditsUsed": 1,
        "cacheHit": false,
        "statusCode": 200,
        "responseTimeMs": 10482,
        "errorMessage": null,
        "createdAt": "2026-07-18T11:28:59.677517+00:00"
      }
    ],
    "filters": {
      "endpoint": null,
      "statusCode": null,
      "since": null,
      "until": null,
      "limit": 5
    }
  },
  "amazon-shop-page": {
    "platform": "amazon_shop",
    "url": "https://www.amazon.com/sp?seller=A294P4X9EWVXLJ",
    "marketplace": "US",
    "seller": {
      "id": "A294P4X9EWVXLJ",
      "name": "AnkerDirect",
      "url": "https://www.amazon.com/sp?seller=A294P4X9EWVXLJ"
    },
    "scrapedAt": "2026-08-02T16:59:58.250Z",
    "totalReturned": 5,
    "hasMore": true,
    "nextCursor": "1:5",
    "products": [
      {
        "asin": "B08NDYQSXZ",
        "title": "Anker Charging Dock for Oculus Quest 2, Oculus Certified Charging Station Stand Set, Headset Display Holder and Controller Mount Station with 2 Rechargeable Batteries, USB-C Charger and Cable",
        "url": "https://www.amazon.com/dp/B08NDYQSXZ",
        "image": "https://m.media-amazon.com/images/I/61EK9jpDapL._AC_UY218_.jpg",
        "price": 49.99,
        "currency": "USD",
        "priceFormatted": "$49.99",
        "rating": 4.4,
        "reviews": null,
        "isPrime": false,
        "isBestSeller": false,
        "isSponsored": false
      },
      {
        "asin": "B08HKPDZSD",
        "title": "Anker Ergonomic Optical USB Wired Vertical Mouse 1000/1600 DPI, 5 Buttons CE100 (Renewed)",
        "url": "https://www.amazon.com/dp/B08HKPDZSD",
        "image": "https://m.media-amazon.com/images/I/61Zu2ANcJbL._AC_UY218_.jpg",
        "price": 16.89,
        "currency": "USD",
        "priceFormatted": "$16.89",
        "rating": 4.5,
        "reviews": null,
        "isPrime": false,
        "isBestSeller": false,
        "isSponsored": false
      }
    ]
  },
  "analytics-compare": {
    "count": 2,
    "resolved": 2,
    "failedCount": 0,
    "results": [
      {
        "platform": "tiktok",
        "url": "https://www.tiktok.com/@khaby.lame/video/7646812028874673439",
        "id": "7646812028874673439",
        "title": "Thank you, please come again!!!🙋🏿‍♂️💸#learnfromkhaby #comedy",
        "publishedAt": "2026-06-02T14:56:35.000Z",
        "durationSeconds": 29.0,
        "thumbnailUrl": "https://p19-common-sign.tiktokcdn-us.com/tos-useast8-p-0068-tx2/oUAHVIiQDac8uC75AEfyALAA1FrTAqEEQ3GRPe~tplv-tiktokx-origin.image?dr=9636&x-expires=1783263600&x-signature=2PlkofS3nAbuOWtQQSaCTJIU0bQ%3D&t=4d5b0474&ps=13740610&shp=81f88b70&shcp=43f4a2f9&idc=useast5",
        "author": {
          "username": "khaby.lame",
          "displayName": "Khabane lame",
          "url": "https://www.tiktok.com/@khaby.lame",
          "verified": true
        },
        "metrics": {
          "views": 14700000,
          "viewsIsApproximate": false,
          "likes": 1300000,
          "comments": 13600,
          "commentsIsApproximate": false,
          "shares": 13400,
          "saves": 50705,
          "interactions": 1377705,
          "interactionsIsApproximate": false,
          "engagementRate": 0.0937,
          "engagementRateBasis": "interactions/views"
        },
        "status": "ok"
      },
      {
        "platform": "youtube",
        "url": "https://www.youtube.com/watch?v=dQw4w9WgXcQ",
        "id": "dQw4w9WgXcQ",
        "title": "Rick Astley - Never Gonna Give You Up (Official Video) (4K Remaster)",
        "publishedAt": "2009-10-25T06:57:33.000Z",
        "durationSeconds": 213,
        "thumbnailUrl": "https://i.ytimg.com/vi_webp/dQw4w9WgXcQ/sddefault.webp",
        "author": {
          "username": "RickAstleyYT",
          "displayName": "Rick Astley",
          "url": "https://www.youtube.com/channel/UCuAXFkgsw1L7xaCfnd5JJOw",
          "verified": null
        },
        "metrics": {
          "views": 1799593805,
          "viewsIsApproximate": false,
          "likes": 19303349,
          "comments": 2400000,
          "commentsIsApproximate": true,
          "shares": null,
          "saves": null,
          "interactions": 21703349,
          "interactionsIsApproximate": true,
          "engagementRate": 0.0121,
          "engagementRateBasis": "interactions/views"
        },
        "status": "ok"
      }
    ],
    "failed": []
  },
  "analytics-post": {
    "platform": "youtube",
    "url": "https://www.youtube.com/watch?v=dQw4w9WgXcQ",
    "id": "dQw4w9WgXcQ",
    "title": "Rick Astley - Never Gonna Give You Up (Official Video) (4K Remaster)",
    "publishedAt": "2009-10-25T06:57:33.000Z",
    "durationSeconds": 213,
    "thumbnailUrl": "https://i.ytimg.com/vi_webp/dQw4w9WgXcQ/sddefault.webp",
    "author": {
      "username": "RickAstleyYT",
      "displayName": "Rick Astley",
      "url": "https://www.youtube.com/channel/UCuAXFkgsw1L7xaCfnd5JJOw",
      "verified": null
    },
    "metrics": {
      "views": 1799593805,
      "viewsIsApproximate": false,
      "likes": 19303349,
      "comments": 2400000,
      "commentsIsApproximate": true,
      "shares": null,
      "saves": null,
      "interactions": 21703349,
      "interactionsIsApproximate": true,
      "engagementRate": 0.0121,
      "engagementRateBasis": "interactions/views"
    }
  },
  "bluesky-post-details": {
    "platform": "bluesky",
    "uri": "at://did:plc:fpruhuo22xkm5o7ttr2ktxdo/app.bsky.feed.post/3mqjnjafz2s2k",
    "url": "https://bsky.app/profile/danabra.mov/post/3mqjnjafz2s2k",
    "cid": "bafyreib46qdetrzwrcu35fqynwkiw6tscptkvlxcujk5f745jmzqox5jz4",
    "text": "i want to do a little ✨ ama about atproto ✨ in this thread. no question is too simple\n\nif you’ve been curious about atproto but don’t know much (anything?) about it, ask any question and i’ll try to explain it in my own words.\n\n(+ would love to hear from friends who aren’t very active on bsky)",
    "publishedAt": "2026-07-13T12:02:47.424Z",
    "indexedAt": "2026-07-13T12:02:47.867Z",
    "author": {
      "handle": "danabra.mov",
      "displayName": "dan",
      "did": "did:plc:fpruhuo22xkm5o7ttr2ktxdo",
      "avatar": "https://cdn.bsky.app/img/avatar/plain/did:plc:fpruhuo22xkm5o7ttr2ktxdo/bafkreif43mhqajnbnl62u3ezf37g6x22nd762im54thxbil4ga46eugcga"
    },
    "engagement": {
      "likes": 340,
      "reposts": 82,
      "replies": 104,
      "quotes": 9
    },
    "embed": null
  },
  "bluesky-profile": {
    "platform": "bluesky",
    "handle": "jay.bsky.team",
    "url": "https://bsky.app/profile/jay.bsky.team",
    "did": "did:plc:oky5czdrnfjpqslsw2a5iclo",
    "name": "Jay 🦋",
    "bio": "Founder & Chief Innovation Officer @ Bluesky\n\nWorking on @attie.ai\n\n🌱 🪴 🌳",
    "followers": 595179,
    "following": 3974,
    "posts": 4110,
    "avatar": "https://cdn.bsky.app/img/avatar/plain/did:plc:oky5czdrnfjpqslsw2a5iclo/bafkreihxtnc37g7jqdcgidtkknwuswtjiijcdnc6cx4imc4oq33cnsc5da",
    "banner": "https://cdn.bsky.app/img/banner/plain/did:plc:oky5czdrnfjpqslsw2a5iclo/bafkreicgnmvhtmj4arcvwhueygbwvkucd3odvom3lxtfmn6wlqbh3yf7p4",
    "verified": true,
    "verification": {
      "verifications": [
        {
          "issuer": "did:plc:z72i7hdynmk6r22z27h6tvur",
          "issuerHandle": "bsky.app",
          "issuerDisplayName": "Bluesky",
          "uri": "at://did:plc:z72i7hdynmk6r22z27h6tvur/app.bsky.graph.verification/3lndslpegeo2f",
          "isValid": true,
          "createdAt": "2025-04-21T11:35:53.359Z"
        }
      ],
      "verifiedStatus": "valid",
      "trustedVerifierStatus": "none"
    },
    "labels": [],
    "associated": {
      "lists": 0,
      "feedgens": 0,
      "starterPacks": 0,
      "labeler": false,
      "chat": {
        "allowIncoming": "following",
        "allowGroupInvites": null
      },
      "activitySubscription": {
        "allowSubscriptions": "followers"
      }
    },
    "createdAt": "2022-11-17T06:31:40.296Z",
    "indexedAt": "2026-03-29T21:16:33.460Z"
  },
  "bluesky-user-posts": {
    "handle": "jay.bsky.team",
    "totalReturned": 5,
    "nextCursor": "2026-06-26T14:25:33.024Z",
    "hasMore": true,
    "posts": [
      {
        "platform": "bluesky",
        "uri": "at://did:plc:fpruhuo22xkm5o7ttr2ktxdo/app.bsky.feed.post/3mqjnjafz2s2k",
        "url": "https://bsky.app/profile/danabra.mov/post/3mqjnjafz2s2k",
        "cid": "bafyreib46qdetrzwrcu35fqynwkiw6tscptkvlxcujk5f745jmzqox5jz4",
        "text": "i want to do a little ✨ ama about atproto ✨ in this thread. no question is too simple\n\nif you’ve been curious about atproto but don’t know much (anything?) about it, ask any question and i’ll try to explain it in my own words.\n\n(+ would love to hear from friends who aren’t very active on bsky)",
        "publishedAt": "2026-07-13T12:02:47.424Z",
        "indexedAt": "2026-07-13T12:02:47.867Z",
        "author": {
          "handle": "danabra.mov",
          "displayName": "dan",
          "did": "did:plc:fpruhuo22xkm5o7ttr2ktxdo",
          "avatar": "https://cdn.bsky.app/img/avatar/plain/did:plc:fpruhuo22xkm5o7ttr2ktxdo/bafkreif43mhqajnbnl62u3ezf37g6x22nd762im54thxbil4ga46eugcga"
        },
        "engagement": {
          "likes": 340,
          "reposts": 82,
          "replies": 104,
          "quotes": 9
        },
        "embed": null
      },
      {
        "platform": "bluesky",
        "uri": "at://did:plc:xtg6uhgsy2j7k2a6qtcood2w/app.bsky.feed.post/3mqsnmkorxc2l",
        "url": "https://bsky.app/profile/karlbode.com/post/3mqsnmkorxc2l",
        "cid": "bafyreih62va7pjdlbcij4nwp55hatyr73glrjr52eocvxkxwdd72i5phea",
        "text": "meanwhile...",
        "publishedAt": "2026-07-17T01:58:36.505Z",
        "indexedAt": "2026-07-17T01:58:38.070Z",
        "author": {
          "handle": "karlbode.com",
          "displayName": "Karl Bode",
          "did": "did:plc:xtg6uhgsy2j7k2a6qtcood2w",
          "avatar": "https://cdn.bsky.app/img/avatar/plain/did:plc:xtg6uhgsy2j7k2a6qtcood2w/bafkreigf276i3ejipydii2glvywuymqwj4usu5noz4rw7lirgxrtbbcibi"
        },
        "engagement": {
          "likes": 973,
          "reposts": 216,
          "replies": 41,
          "quotes": 107
        },
        "embed": {
          "type": "external",
          "url": "https://www.seattletimes.com/seattle-news/meet-jimothy-seattles-internet-famous-raccoon/?fbclid=Iwb21leATGa4ljbGNrBMZrgWV4dG4DYWVtAjExAHNydGMGYXBwX2lkDDM1MDY4NTUzMTcyOAABHnlF6kiFK1hm4n5G5_BMmAcqRVTUV6qoBX4qZCw1rworU3stQwUoZZFw3yXL_aem_eUBpvFSYXBAwVjchn5qVyA",
          "title": "Meet ‘Jimothy,’ Seattle’s internet-famous raccoon",
          "description": "The tiny beast has been spotted twice in Ballard this summer and appears to be doing well, despite a likely congenital deformity, an animal expert said.",
          "thumb": "https://cdn.bsky.app/img/feed_thumbnail/plain/did:plc:xtg6uhgsy2j7k2a6qtcood2w/bafkreidmxsn5szs7i4vpq7kpjbwh44kwnkwu5b2n44vjhtye4hfpqfhzxq"
        }
      }
    ]
  },
  "facebook-ad-library-ad-details": {
    "platform": "facebook_ad_library",
    "id": "317161109571794",
    "url": "https://www.facebook.com/ads/library/?id=317161109571794",
    "text": "The Voting Information Center—one-tap voting registration information from election experts and authorities in one place.",
    "headline": "Voting Information Center",
    "cta": "Learn more",
    "landingUrl": "http://facebook.com/votinginformationcenter",
    "adFormat": "VIDEO",
    "firstShown": "2020-09-22T07:00:00.000Z",
    "lastShown": "2020-10-05T07:00:00.000Z",
    "impressions": ">1M",
    "spend": ">$1M",
    "country": "US",
    "advertiser": {
      "id": "108824017345866",
      "name": "Meta",
      "url": "https://www.facebook.com/Meta/",
      "logo": "https://scontent-dfw5-2.xx.fbcdn.net/v/t1.6435-9/119568341_200337161527884_7846459746434232698_n.png?stp=dst-png_s60x60&_nc_cat=100&ccb=1-7&_nc_sid=c53f8f&_nc_ohc=ZqrAiU5uA1sQ7kNvwHsXpf9&_nc_oc=AdqVVq_tCCm9QfdHEQa5d82UKJTt9DT4LxrW9m95vTx7VJLcyuQH74gIZv0WeiJgIfo&_nc_zt=23&_nc_ht=scontent-dfw5-2.xx&_nc_gid=oKi5rqU7-78Y6XFLpAVqvA&_nc_ss=79289&oh=00_AQDIgONmGu5lj1i0jpr_nH9fjb7afatDtlB-wsXtBQNtZQ&oe=6A8F324E"
    },
    "media": [
      "https://video-dfw5-1.xx.fbcdn.net/o1/v/t2/f2/m412/AQNN757NtitUcJnpv0ODeMH6fXo-yFM-X90P2W82Zsrc70oOzST9lrKgscKf21SHBUtZ9pdKMclY8s32B0eRJ7o.mp4?_nc_cat=106&_nc_sid=ef5aa3&_nc_ht=video-dfw5-1.xx.fbcdn.net&_nc_ohc=DeBVZh2ChkAQ7kNvwELM_GV&efg=eyJ2ZW5jb2RlX3RhZyI6Inhwdl9wcm9ncmVzc2l2ZS5WSV9VU0VDQVNFX1BST0RVQ1RfVFlQRS4uQzMuMzQwLmFzaWNfaHExX3NkX3Byb2dyZXNzaXZlIiwieHB2X2Fzc2V0X2lkIjo4MzE0MTAwMzMxNDk2MzYsImFzc2V0X2FnZV9kYXlzIjoyNDEsInZpX3VzZWNhc2VfaWQiOjEwNjgwLCJkdXJhdGlvbl9zIjoxNSwidXJsZ2VuX3NvdXJjZSI6Ind3dyJ9&ccb=17-1&_nc_gid=oKi5rqU7-78Y6XFLpAVqvA&_nc_ss=79289&_nc_zt=28&oh=00_AQB-CUR53tb21BEWdlRLg5BhAauE3-hDDO9zmz06SvSAdg&oe=6A6D9B48",
      "https://scontent-dfw5-1.xx.fbcdn.net/v/t39.35426-6/120065387_2711663819108220_8472417301728012411_n.jpg?_nc_cat=105&ccb=1-7&_nc_sid=c53f8f&_nc_ohc=JCEJHIw0engQ7kNvwEcgh1o&_nc_oc=Ado6Dn6wrEd2aZKTiM6OLVJyx_BYbHRC0Bmv70xAZp21Pm2Enab2l80KoUSxQZAs1Ow&_nc_zt=14&_nc_ht=scontent-dfw5-1.xx&_nc_gid=oKi5rqU7-78Y6XFLpAVqvA&_nc_ss=79289&oh=00_AQAw5ZEVUbeJYpBcx6Qa4wV6V-hZRjNvtI487nUdgq8UZA&oe=6A6D850A"
    ]
  },
  "facebook-ad-library-ad-transcript": {
    "platform": "facebook_ad_library",
    "url": "https://www.facebook.com/ads/library/?id=317161109571794",
    "adId": "317161109571794",
    "transcript": "headline: Voting Information Center\nbody: The Voting Information Center—one-tap voting registration information from election experts and authorities in one place.\ncta: Learn more\nlandingUrl: http://facebook.com/votinginformationcenter",
    "transcriptSegments": [
      {
        "speaker": "headline",
        "text": "Voting Information Center",
        "start": 0,
        "duration": 0,
        "timestamp": "00:00"
      },
      {
        "speaker": "body",
        "text": "The Voting Information Center—one-tap voting registration information from election experts and authorities in one place.",
        "start": 0,
        "duration": 0,
        "timestamp": "00:00"
      },
      {
        "speaker": "cta",
        "text": "Learn more",
        "start": 0,
        "duration": 0,
        "timestamp": "00:00"
      },
      {
        "speaker": "landingUrl",
        "text": "http://facebook.com/votinginformationcenter",
        "start": 0,
        "duration": 0,
        "timestamp": "00:00"
      }
    ],
    "wordCount": 25,
    "segments": 4,
    "advertiser": {
      "id": "108824017345866",
      "name": "Meta",
      "url": "https://www.facebook.com/Meta/",
      "logo": "https://scontent-dfw5-2.xx.fbcdn.net/v/t1.6435-9/119568341_200337161527884_7846459746434232698_n.png?stp=dst-png_s60x60&_nc_cat=100&ccb=1-7&_nc_sid=c53f8f&_nc_ohc=ZqrAiU5uA1sQ7kNvwHsXpf9&_nc_oc=AdqVVq_tCCm9QfdHEQa5d82UKJTt9DT4LxrW9m95vTx7VJLcyuQH74gIZv0WeiJgIfo&_nc_zt=23&_nc_ht=scontent-dfw5-2.xx&_nc_gid=oKi5rqU7-78Y6XFLpAVqvA&_nc_ss=79289&oh=00_AQDIgONmGu5lj1i0jpr_nH9fjb7afatDtlB-wsXtBQNtZQ&oe=6A8F324E"
    }
  },
  "facebook-ad-library-company-ads": {
    "url": "https://www.facebook.com/Meta",
    "country": "US",
    "totalReturned": 5,
    "ads": [
      {
        "platform": "facebook_ad_library",
        "id": "273872017027242",
        "url": "https://www.facebook.com/ads/library/?id=273872017027242",
        "text": "The Voting Information Center on Facebook - one-tap voting info from election experts and authorities in one place.",
        "headline": "Voting Information Center",
        "cta": "Learn more",
        "landingUrl": "http://facebook.com/votinginformationcenter",
        "adFormat": "VIDEO",
        "firstShown": "2020-10-05T07:00:00.000Z",
        "lastShown": "2020-10-13T07:00:00.000Z",
        "impressions": ">1M",
        "spend": ">$1M",
        "country": "US",
        "advertiser": {
          "id": "108824017345866",
          "name": "Meta",
          "url": "https://www.facebook.com/Meta/",
          "logo": "https://scontent-atl3-1.xx.fbcdn.net/v/t1.6435-9/119568341_200337161527884_7846459746434232698_n.png?stp=dst-png_s60x60&_nc_cat=100&ccb=1-7&_nc_sid=c53f8f&_nc_ohc=qaRlosGC9wUQ7kNvwH_c6S1&_nc_oc=Adq6Kf5L_Tkx2E3_ZTPgkkJBqBFrUF2yFzbizYtSLVcyom-ZAmB0zM6FgNhqa6CE4bQ&_nc_zt=23&_nc_ht=scontent-atl3-1.xx&_nc_gid=SxD9styajND2_8-5Hiv5XQ&_nc_ss=72289&oh=00_AQB38PZJl2olGB2U4-yzTIbucPjM7a_5C-sAcPDMbf_TKA&oe=6A89438E"
        },
        "media": [
          "https://video-atl3-1.xx.fbcdn.net/o1/v/t2/f2/m412/AQOW2b9UEJoszgGizc9hrdAjx8h2PNmX5EFioCovqhnhZrPmWYYs2jrz2_k4rgn72viqiAXdYrPWHCU-Gie0kjeq.mp4?_nc_cat=103&_nc_sid=ef5aa3&_nc_ht=video-atl3-1.xx.fbcdn.net&_nc_ohc=nys365hpMxcQ7kNvwHgMgqj&efg=eyJ2ZW5jb2RlX3RhZyI6Inhwdl9wcm9ncmVzc2l2ZS5WSV9VU0VDQVNFX1BST0RVQ1RfVFlQRS4uQzMuMzIwLmFzaWNfaHExX3NkX3Byb2dyZXNzaXZlIiwieHB2X2Fzc2V0X2lkIjo2NjAxMjk2OTAzNjcwMTMsImFzc2V0X2FnZV9kYXlzIjoyNDksInZpX3VzZWNhc2VfaWQiOjEwNjgwLCJkdXJhdGlvbl9zIjozMCwidXJsZ2VuX3NvdXJjZSI6Ind3dyJ9&ccb=17-1&_nc_gid=SxD9styajND2_8-5Hiv5XQ&_nc_ss=72289&_nc_zt=28&oh=00_AQBnmCAlNRahN4AsgdZ38Ac5EdAxMjL50nCNBkLLyltBwA&oe=6A678B84",
          "https://scontent-atl3-2.xx.fbcdn.net/v/t39.35426-6/120102604_752266025568907_2538374744503325031_n.jpg?_nc_cat=105&ccb=1-7&_nc_sid=c53f8f&_nc_ohc=zOy1dkRrjNwQ7kNvwE6UWb4&_nc_oc=AdoeR4HjsR3dT59BfJw-cJn13C_EDqxVPAUcXGvB7N-aH8ENNZZDwhMcyf83dUgpiPo&_nc_zt=14&_nc_ht=scontent-atl3-2.xx&_nc_gid=SxD9styajND2_8-5Hiv5XQ&_nc_ss=72289&oh=00_AQAeRefR3xV4gR8tcoNYd2lM6c7GaZUDOV0GYx4rVDnAiA&oe=6A677DC7"
        ]
      },
      {
        "platform": "facebook_ad_library",
        "id": "3335260483258933",
        "url": "https://www.facebook.com/ads/library/?id=3335260483258933",
        "text": "The Voting Information Center on Facebook - one-tap voting info from election experts and authorities in one place.",
        "headline": "Voting Information Center",
        "cta": "Learn more",
        "landingUrl": "http://facebook.com/votinginformationcenter",
        "adFormat": "VIDEO",
        "firstShown": "2020-09-23T07:00:00.000Z",
        "lastShown": "2020-10-05T07:00:00.000Z",
        "impressions": ">1M",
        "spend": ">$1M",
        "country": "US",
        "advertiser": {
          "id": "108824017345866",
          "name": "Facebook",
          "url": "https://www.facebook.com/Meta/",
          "logo": "https://scontent-atl3-1.xx.fbcdn.net/v/t1.6435-9/119568341_200337161527884_7846459746434232698_n.png?stp=dst-png_s60x60&_nc_cat=100&ccb=1-7&_nc_sid=c53f8f&_nc_ohc=qaRlosGC9wUQ7kNvwH_c6S1&_nc_oc=Adq6Kf5L_Tkx2E3_ZTPgkkJBqBFrUF2yFzbizYtSLVcyom-ZAmB0zM6FgNhqa6CE4bQ&_nc_zt=23&_nc_ht=scontent-atl3-1.xx&_nc_gid=SxD9styajND2_8-5Hiv5XQ&_nc_ss=72289&oh=00_AQB38PZJl2olGB2U4-yzTIbucPjM7a_5C-sAcPDMbf_TKA&oe=6A89438E"
        },
        "media": [
          "https://video-atl3-1.xx.fbcdn.net/o1/v/t2/f2/m412/AQOW2b9UEJoszgGizc9hrdAjx8h2PNmX5EFioCovqhnhZrPmWYYs2jrz2_k4rgn72viqiAXdYrPWHCU-Gie0kjeq.mp4?_nc_cat=103&_nc_sid=ef5aa3&_nc_ht=video-atl3-1.xx.fbcdn.net&_nc_ohc=nys365hpMxcQ7kNvwHgMgqj&efg=eyJ2ZW5jb2RlX3RhZyI6Inhwdl9wcm9ncmVzc2l2ZS5WSV9VU0VDQVNFX1BST0RVQ1RfVFlQRS4uQzMuMzIwLmFzaWNfaHExX3NkX3Byb2dyZXNzaXZlIiwieHB2X2Fzc2V0X2lkIjo2NjAxMjk2OTAzNjcwMTMsImFzc2V0X2FnZV9kYXlzIjoyNDksInZpX3VzZWNhc2VfaWQiOjEwNjgwLCJkdXJhdGlvbl9zIjozMCwidXJsZ2VuX3NvdXJjZSI6Ind3dyJ9&ccb=17-1&_nc_gid=SxD9styajND2_8-5Hiv5XQ&_nc_ss=72289&_nc_zt=28&oh=00_AQBnmCAlNRahN4AsgdZ38Ac5EdAxMjL50nCNBkLLyltBwA&oe=6A678B84",
          "https://scontent-atl3-2.xx.fbcdn.net/v/t39.35426-6/120102604_752266025568907_2538374744503325031_n.jpg?_nc_cat=105&ccb=1-7&_nc_sid=c53f8f&_nc_ohc=zOy1dkRrjNwQ7kNvwE6UWb4&_nc_oc=AdoeR4HjsR3dT59BfJw-cJn13C_EDqxVPAUcXGvB7N-aH8ENNZZDwhMcyf83dUgpiPo&_nc_zt=14&_nc_ht=scontent-atl3-2.xx&_nc_gid=SxD9styajND2_8-5Hiv5XQ&_nc_ss=72289&oh=00_AQAeRefR3xV4gR8tcoNYd2lM6c7GaZUDOV0GYx4rVDnAiA&oe=6A677DC7"
        ]
      }
    ]
  },
  "facebook-ad-library-search": {
    "query": "election",
    "country": "US",
    "totalReturned": 5,
    "ads": [
      {
        "platform": "facebook_ad_library",
        "id": "317161109571794",
        "url": "https://www.facebook.com/ads/library/?id=317161109571794",
        "text": "The Voting Information Center—one-tap voting registration information from election experts and authorities in one place.",
        "headline": "Voting Information Center",
        "cta": "Learn more",
        "landingUrl": "http://facebook.com/votinginformationcenter",
        "adFormat": "VIDEO",
        "firstShown": "2020-09-22T07:00:00.000Z",
        "lastShown": "2020-10-05T07:00:00.000Z",
        "impressions": ">1M",
        "spend": ">$1M",
        "country": "US",
        "advertiser": {
          "id": "108824017345866",
          "name": "Meta",
          "url": "https://www.facebook.com/Meta/",
          "logo": "https://scontent-atl3-1.xx.fbcdn.net/v/t1.6435-9/119568341_200337161527884_7846459746434232698_n.png?stp=dst-png_s60x60&_nc_cat=100&ccb=1-7&_nc_sid=c53f8f&_nc_ohc=qaRlosGC9wUQ7kNvwHuGOSN&_nc_oc=AdpUTiQHP0F2DQWlJJsFhLjPwiKgiTaMBS9Gf3J_Ogy1Z6nYv2kt_BhKXvw8jPupOMg&_nc_zt=23&_nc_ht=scontent-atl3-1.xx&_nc_gid=kjSzmNhJvOQPmxnVKKr0xg&_nc_ss=72289&oh=00_AQCbS0Qc_-2kHNJh8Yysq78dbBXaaJS4Osw3-xA3_SHVlw&oe=6A89438E"
        },
        "media": [
          "https://video-atl3-1.xx.fbcdn.net/o1/v/t2/f2/m412/AQNN757NtitUcJnpv0ODeMH6fXo-yFM-X90P2W82Zsrc70oOzST9lrKgscKf21SHBUtZ9pdKMclY8s32B0eRJ7o.mp4?_nc_cat=106&_nc_sid=ef5aa3&_nc_ht=video-atl3-1.xx.fbcdn.net&_nc_ohc=VIhm6QH6QpYQ7kNvwEGz32Z&efg=eyJ2ZW5jb2RlX3RhZyI6Inhwdl9wcm9ncmVzc2l2ZS5WSV9VU0VDQVNFX1BST0RVQ1RfVFlQRS4uQzMuMzQwLmFzaWNfaHExX3NkX3Byb2dyZXNzaXZlIiwieHB2X2Fzc2V0X2lkIjo4MzE0MTAwMzMxNDk2MzYsImFzc2V0X2FnZV9kYXlzIjoyMzcsInZpX3VzZWNhc2VfaWQiOjEwNjgwLCJkdXJhdGlvbl9zIjoxNSwidXJsZ2VuX3NvdXJjZSI6Ind3dyJ9&ccb=17-1&_nc_gid=kjSzmNhJvOQPmxnVKKr0xg&_nc_ss=72289&_nc_zt=28&oh=00_AQBmg1RWfbVvJ3MUBSfprUeNw4A1j1otLN5iP3DoZ8RxIw&oe=6A677448",
          "https://scontent-atl3-2.xx.fbcdn.net/v/t39.35426-6/120065387_2711663819108220_8472417301728012411_n.jpg?_nc_cat=105&ccb=1-7&_nc_sid=c53f8f&_nc_ohc=XJsOGtccv7UQ7kNvwFOmuvH&_nc_oc=AdqJh0Avn_pYIk_hzhEW3QS1dyOrrTJn4nBpQ38NLoUvb1OE8Kwj7qy75S7f1QbV1cs&_nc_zt=14&_nc_ht=scontent-atl3-2.xx&_nc_gid=kjSzmNhJvOQPmxnVKKr0xg&_nc_ss=72289&oh=00_AQBESYOW184a4FJWDENcSYwQSBzwkH5yonZh3U5v6ZZEgA&oe=6A67964A"
        ]
      },
      {
        "platform": "facebook_ad_library",
        "id": "372804137235499",
        "url": "https://www.facebook.com/ads/library/?id=372804137235499",
        "text": "The Voting Information Center on Facebook—one-tap voting info from election experts and authorities in one place.",
        "headline": "Voting Information Center",
        "cta": "Learn more",
        "landingUrl": "http://facebook.com/votinginformationcenter",
        "adFormat": "VIDEO",
        "firstShown": "2020-10-05T07:00:00.000Z",
        "lastShown": "2020-10-13T07:00:00.000Z",
        "impressions": ">1M",
        "spend": ">$1M",
        "country": "US",
        "advertiser": {
          "id": "108824017345866",
          "name": "Meta",
          "url": "https://www.facebook.com/Meta/",
          "logo": "https://scontent-atl3-1.xx.fbcdn.net/v/t1.6435-9/119568341_200337161527884_7846459746434232698_n.png?stp=dst-png_s60x60&_nc_cat=100&ccb=1-7&_nc_sid=c53f8f&_nc_ohc=qaRlosGC9wUQ7kNvwHuGOSN&_nc_oc=AdpUTiQHP0F2DQWlJJsFhLjPwiKgiTaMBS9Gf3J_Ogy1Z6nYv2kt_BhKXvw8jPupOMg&_nc_zt=23&_nc_ht=scontent-atl3-1.xx&_nc_gid=kjSzmNhJvOQPmxnVKKr0xg&_nc_ss=72289&oh=00_AQCbS0Qc_-2kHNJh8Yysq78dbBXaaJS4Osw3-xA3_SHVlw&oe=6A89438E"
        },
        "media": [
          "https://video-atl3-1.xx.fbcdn.net/o1/v/t2/f2/m412/AQPYrtdWcXYzwK9kZxgDiAgoU_IImyeS9Q8adbGcircR7RR1dDdUBrAQ0LiHO2OJoauE5pf8F4GyEcPVDLQ94uo.mp4?_nc_cat=100&_nc_sid=ef5aa3&_nc_ht=video-atl3-1.xx.fbcdn.net&_nc_ohc=TJVBi21FSYoQ7kNvwGc3J8g&efg=eyJ2ZW5jb2RlX3RhZyI6Inhwdl9wcm9ncmVzc2l2ZS5WSV9VU0VDQVNFX1BST0RVQ1RfVFlQRS4uQzMuMzQwLmFzaWNfaHExX3NkX3Byb2dyZXNzaXZlIiwieHB2X2Fzc2V0X2lkIjo4OTE2MjkwMDA0NTQwNDEsImFzc2V0X2FnZV9kYXlzIjoxNTcsInZpX3VzZWNhc2VfaWQiOjEwNjgwLCJkdXJhdGlvbl9zIjoxNCwidXJsZ2VuX3NvdXJjZSI6Ind3dyJ9&ccb=17-1&_nc_gid=kjSzmNhJvOQPmxnVKKr0xg&_nc_ss=72289&_nc_zt=28&oh=00_AQCMG2KnWhkyJxkleqImsnYBBqDKo2-gU04sjFZY6UOemA&oe=6A678682",
          "https://scontent-atl3-1.xx.fbcdn.net/v/t39.35426-6/120439450_1980569842077757_2547343747583380554_n.jpg?_nc_cat=100&ccb=1-7&_nc_sid=c53f8f&_nc_ohc=ghBwQrPN7IYQ7kNvwEK1Ioe&_nc_oc=Adq-eL0xdnXQzWG8i4nmzYYnwcV_Aa55yUcMBwzE5_rk0sejWdtPX_5QJKW6xounlWk&_nc_zt=14&_nc_ht=scontent-atl3-1.xx&_nc_gid=kjSzmNhJvOQPmxnVKKr0xg&_nc_ss=72289&oh=00_AQB1w19aEluVfs5pAiHsky2u5dZ4bgAW_AohS8QzRc8Wkg&oe=6A678BF4"
        ]
      }
    ]
  },
  "facebook-ad-library-search-companies": {
    "query": "nike",
    "country": "US",
    "totalReturned": 3,
    "companies": [
      {
        "id": "146705838515566",
        "name": "Sukeban World",
        "url": "https://www.facebook.com/61551864263186/",
        "logo": "https://scontent-iad6-1.xx.fbcdn.net/v/t39.35426-6/517640014_2104272360362331_1464623957160374455_n.jpg?stp=dst-jpg_s60x60_tt6&_nc_cat=100&ccb=1-7&_nc_sid=c53f8f&_nc_ohc=zj4Fm9x6lhEQ7kNvwGyzer2&_nc_oc=Adpw1Rqb_eBzffqqgyQt5_CPB2Dct1h7kaRFJQZmeucV_ui5BXf-Q6skKKVFDUKvDH4&_nc_zt=14&_nc_ht=scontent-iad6-1.xx&_nc_gid=WFVhUXC3vFhp5HqXMO2_vg&_nc_ss=72289&oh=00_AQCbgqCqvp545MCPZrHlySJ8QWqgsWnjuxmEGnyIw8Gw3A&oe=6A611F63"
      },
      {
        "id": "15087023444",
        "name": "Nike",
        "url": "https://www.facebook.com/nike/",
        "logo": "https://scontent-iad6-1.xx.fbcdn.net/v/t39.35426-6/366635364_819887626183060_5665913834577832309_n.jpg?stp=dst-jpg_s60x60_tt6&_nc_cat=106&ccb=1-7&_nc_sid=c53f8f&_nc_ohc=cpw1LHoxRRMQ7kNvwF0VELk&_nc_oc=Adp4gYKupQoA3SFulWbqwUFHqP4Hb9COtOidu_sWgA0fqGKhHNgkorx0YOcUbNCeAek&_nc_zt=14&_nc_ht=scontent-iad6-1.xx&_nc_gid=WFVhUXC3vFhp5HqXMO2_vg&_nc_ss=72289&oh=00_AQCzxYXtTr8L2PBX03C3WTbVmtXlrB0ZHR45OVmp6Pv9mA&oe=6A612326"
      }
    ]
  },
  "facebook-comment-replies": {
    "platform": "facebook",
    "url": "https://www.facebook.com/NASA/posts/pfbid02skzNsrLf5atYZfzvzHAK9gHwDnZC5u4pDZMLQ1u3iJmfoA8tNsGpT7Uj6WPs6K3Rl",
    "commentId": "1009195248315125",
    "totalReturned": 1,
    "replies": [
      {
        "id": "1042165238137511",
        "url": "https://www.facebook.com/NASA/posts/pfbid0ozvoLoowKvCysA2CZkXKTAVCRLoVECcrC7W8eQbQYvxBNKMCQAzV8baSgDa8t5Hol?comment_id=1009195248315125&reply_comment_id=1042165238137511",
        "text": "Richard Alexandrowich why?",
        "author": "Lachlan Cryer",
        "authorUrl": "https://www.facebook.com/people/Lachlan-Cryer/pfbid0375uAsq1qky7hMLXQqGc7jjTkqBfPXimoWiegNFtifpGUVNAbGSCJUfTuE2pFLUbrl/",
        "authorAvatarUrl": "https://scontent.fgua9-1.fna.fbcdn.net/v/t1.30497-1/453178253_471506465671661_2781666950760530985_n.png?stp=cp0_dst-png&cstp=mx2048x2048&ctp=s32x32&_nc_cat=1&ccb=1-7&_nc_sid=136b72&_nc_ohc=YYd_HsBfn6kQ7kNvwExKFZn&_nc_oc=AdqMYmSyRUE01D1xr5lyzA2HCr-qEDfBccvNnTFqTcwN9d6sZq2e9gUxP6FqN2yBlOg&_nc_zt=24&_nc_ht=scontent.fgua9-1.fna&_nc_ss=7b289&oh=00_AQC7tyTMaBqs0n4gldLDuXTonuW4u8g9hyfiQqxHLmbKJA&oe=6A8DC8BA",
        "likeCount": 1,
        "publishedAt": "2026-06-03T07:43:21+00:00"
      }
    ]
  },
  "facebook-comments": {
    "platform": "facebook",
    "url": "https://www.facebook.com/NASA/posts/pfbid02skzNsrLf5atYZfzvzHAK9gHwDnZC5u4pDZMLQ1u3iJmfoA8tNsGpT7Uj6WPs6K3Rl",
    "totalReturned": 5,
    "comments": [
      {
        "id": "1003271445544158",
        "url": "https://www.facebook.com/NASA/posts/pfbid0ozvoLoowKvCysA2CZkXKTAVCRLoVECcrC7W8eQbQYvxBNKMCQAzV8baSgDa8t5Hol?comment_id=1003271445544158",
        "text": "how is this different from JWST?",
        "author": {
          "id": "pfbid02SdzVLPYTHY2eGMdrwFrLw54sVZdguAGnLUj4RPL3HxFtG2D4PBBjptiMEwpB21Ehl",
          "name": "Robin Bergsagel",
          "shortName": "Robin",
          "gender": "FEMALE",
          "avatarUrl": "https://scontent.fsgn24-1.fna.fbcdn.net/v/t39.30808-1/692472460_26663220403348161_6124206666765972294_n.jpg?stp=cp0_dst-jpg_tt6&cstp=mx960x960&ctp=s32x32&_nc_cat=102&ccb=1-7&_nc_sid=e99d92&_nc_ohc=3HNDMjGZhBIQ7kNvwH_Yi6V&_nc_oc=AdoxMiMSoY_ToCduVunc3YCOZtk_SXSgox578bFFqLiP_4rQwkwI465-N_iYgGAJFKc&_nc_zt=24&_nc_ht=scontent.fsgn24-1.fna&_nc_gid=HH_crC25V3cxSQmbs1qi6w&_nc_ss=7b289&oh=00_AQDnijJpCb3QQr1TMy3wnG3ZpT2laUi0wvxSIlu-E9nHXw&oe=6A6C3A29"
        },
        "authorAvatarUrl": "https://scontent.fsgn24-1.fna.fbcdn.net/v/t39.30808-1/692472460_26663220403348161_6124206666765972294_n.jpg?stp=cp0_dst-jpg_tt6&cstp=mx960x960&ctp=s32x32&_nc_cat=102&ccb=1-7&_nc_sid=e99d92&_nc_ohc=3HNDMjGZhBIQ7kNvwH_Yi6V&_nc_oc=AdoxMiMSoY_ToCduVunc3YCOZtk_SXSgox578bFFqLiP_4rQwkwI465-N_iYgGAJFKc&_nc_zt=24&_nc_ht=scontent.fsgn24-1.fna&_nc_gid=HH_crC25V3cxSQmbs1qi6w&_nc_ss=7b289&oh=00_AQDnijJpCb3QQr1TMy3wnG3ZpT2laUi0wvxSIlu-E9nHXw&oe=6A6C3A29",
        "likeCount": 95,
        "publishedAt": "2026-06-02T19:30:33+00:00",
        "replyCount": 1,
        "reactionCount": 95,
        "reactions": {
          "like": 79,
          "love": 4,
          "care": 0,
          "haha": 1,
          "wow": 11,
          "sad": 0,
          "anger": 0,
          "thankful": 0,
          "pride": 0,
          "confused": 0
        }
      },
      {
        "id": "1565653145168639",
        "url": "https://www.facebook.com/NASA/posts/pfbid0ozvoLoowKvCysA2CZkXKTAVCRLoVECcrC7W8eQbQYvxBNKMCQAzV8baSgDa8t5Hol?comment_id=1565653145168639",
        "text": "You had me at Roman",
        "author": {
          "id": "pfbid0exampleAuthorIdFor15656531",
          "name": "Mike Harwick",
          "shortName": "Mike",
          "gender": "MALE",
          "avatarUrl": "https://scontent.fsgn13-1.fna.fbcdn.net/v/t39.30808-1/708345356_26903531449306692_9193818255719987217_n.jpg?stp=cp0_dst-jpg_tt6&cstp=mx960x960&ctp=s32x32&_nc_cat=100&ccb=1-7&_nc_sid=e99d92&_nc_ohc=TzWa-f368dwQ7kNvwEMPaUV&_nc_oc=AdpdLHrvXy7m167xxHhinaiUIlBoo2jzN-yKoz2hmtKPDhZMy8t4wFudGRE1dEwFuas&_nc_zt=24&_nc_ht=scontent.fsgn13-1.fna&_nc_gid=HH_crC25V3cxSQmbs1qi6w&_nc_ss=7b289&oh=00_AQCw8rv9R1a-kXHBcH09C7AdRzTbIlhxf4mps8XzaYwIlQ&oe=6A6C1254"
        },
        "authorAvatarUrl": "https://scontent.fsgn13-1.fna.fbcdn.net/v/t39.30808-1/708345356_26903531449306692_9193818255719987217_n.jpg?stp=cp0_dst-jpg_tt6&cstp=mx960x960&ctp=s32x32&_nc_cat=100&ccb=1-7&_nc_sid=e99d92&_nc_ohc=TzWa-f368dwQ7kNvwEMPaUV&_nc_oc=AdpdLHrvXy7m167xxHhinaiUIlBoo2jzN-yKoz2hmtKPDhZMy8t4wFudGRE1dEwFuas&_nc_zt=24&_nc_ht=scontent.fsgn13-1.fna&_nc_gid=HH_crC25V3cxSQmbs1qi6w&_nc_ss=7b289&oh=00_AQCw8rv9R1a-kXHBcH09C7AdRzTbIlhxf4mps8XzaYwIlQ&oe=6A6C1254",
        "likeCount": 3,
        "publishedAt": "2026-06-03T12:30:24+00:00",
        "replyCount": 0,
        "reactionCount": 3,
        "reactions": {
          "like": 3,
          "love": 0,
          "care": 0,
          "haha": 0,
          "wow": 0,
          "sad": 0,
          "anger": 0,
          "thankful": 0,
          "pride": 0,
          "confused": 0
        }
      }
    ],
    "hasMore": true,
    "nextCursor": null,
    "feedbackId": "ZmVlZGJhY2s6MTU0MTc1MzUyMzk4NjY4NQ=="
  },
  "facebook-details": {
    "platform": "facebook",
    "url": "https://www.facebook.com/reel/1376651124309650",
    "id": "1567272851434752",
    "caption": "There will be more than just fireworks to see in the night sky this month!\n\nYou can look forward to these celestial sights in July:\n- A lunar-planetary alignment\n- A visiting comet\n- A good look at Saturn and the Milky Way\n\nHappy skywatching! https://go.nasa.gov/3QvQc4k",
    "description": "There will be more than just fireworks to see in the night sky this month!\n\nYou can look forward to these celestial sights in July:\n- A lunar-planetary alignment\n- A visiting comet\n- A good look at Saturn and the Milky Way\n\nHappy skywatching! https://go.nasa.gov/3QvQc4k",
    "publishedAt": "2026-07-02T15:03:11.000Z",
    "durationSeconds": 200.016,
    "thumbnailUrl": "https://scontent-atl3-3.xx.fbcdn.net/v/t15.5256-10/735149954_4435586749988646_521208314578416779_n.jpg?stp=dst-jpg_tt6&cstp=mx720x405&ctp=s720x405&_nc_cat=111&ccb=1-7&_nc_sid=be8305&_nc_ohc=lkSHcojZDSYQ7kNvwG18v3E&_nc_oc=Ado7Dqia8Fp3TMyoJP-nqzgoUUe3fuNq01u63ZrWrjBdYhVBfwfG-8TDKE-UDnBXYek&_nc_zt=23&_nc_ht=scontent-atl3-3.xx&_nc_gid=Vj-hvWV9W_P8ZRNVd_Lj3A&_nc_ss=7b289&oh=00_AQBLDKBELI40vp0Kckzx4q2eKic8tR46WwPCSFfbY5cwNw&oe=6A6D5E2C",
    "videoUrl": "https://video-atl3-1.xx.fbcdn.net/o1/v/t2/f2/m366/AQOh7ZLRZfB5SIGETu_uz2jbsqvY3dW7G3sGdKsNsX627DpYoTuCxs26FyYE4T4rDzRdvIV2tOCYJi5hs8Gs1EaQEL7_LhQnAXKuILiY508JFg.mp4?_nc_cat=103&_nc_sid=5e9851&_nc_ht=video-atl3-1.xx.fbcdn.net&_nc_ohc=wPmj9ZUq47YQ7kNvwH_JIsW&efg=eyJ2ZW5jb2RlX3RhZyI6Inhwdl9wcm9ncmVzc2l2ZS5GQUNFQk9PSy4uQzMuMTI4MC5kYXNoX2gyNjQtYmFzaWMtZ2VuMl83MjBwIiwieHB2X2Fzc2V0X2lkIjoxMzQ3ODY4NzYwMDA4MjE2LCJhc3NldF9hZ2VfZGF5cyI6MjUsInZpX3VzZWNhc2VfaWQiOjEwMTIyLCJkdXJhdGlvbl9zIjoyMDAsInVybGdlbl9zb3VyY2UiOiJ3d3cifQ%3D%3D&ccb=17-1&vs=c53b4168a8d58285&_nc_vs=HBksFQIYRWZiX2VwaGVtZXJhbC80QjQyOEYzOTg3NDFDRkNGM0UzNzQ4QkZDMDY4QTU4QV9tdF8xX3ZpZGVvX2Rhc2hpbml0Lm1wNBUAAsgBEgAVAhhAZmJfcGVybWFuZW50LzAxNEExNzM2QkY1RkU3NTNDMjU1QkUyMjg3RUMzOEE0X2F1ZGlvX2Rhc2hpbml0Lm1wNBUCAsgBEgAoABgAGwKIB3VzZV9vaWwBMRJwcm9ncmVzc2l2ZV9yZWNpcGUBMRUAACawmKfqpPjkBBUCKAJDMywXQGkBDlYEGJMYGWRhc2hfaDI2NC1iYXNpYy1nZW4yXzcyMHARAHUCZZSeAQA&_nc_gid=Vj-hvWV9W_P8ZRNVd_Lj3A&_nc_ss=7b289&_nc_zt=28&oh=00_AQAFmAbpq3yKHMxyvUj4LDMndyCfVJXc4d0c8CQZ_UIBUw&oe=6A6D7DF5&bitrate=733579&tag=dash_h264-basic-gen2_720p",
    "author": {
      "username": "NASA",
      "displayName": "NASA - National Aeronautics and Space Administration",
      "url": "https://www.facebook.com/NASA",
      "profileImage": "https://scontent-atl3-1.xx.fbcdn.net/v/t39.30808-1/243095782_416661036495945_3843362260429099279_n.png?stp=cp0_dst-png&cstp=mx800x800&ctp=s80x80&_nc_cat=1&ccb=1-7&_nc_sid=2d3e12&_nc_ohc=rc5kNRYek84Q7kNvwEOuwnr&_nc_oc=AdpqXBYPB1HBfYhXUuQXS0HKbYcQ4mDfRxLfg4yx6pslEIjKO3biNVlf9-En1zfMphg&_nc_zt=24&_nc_ht=scontent-atl3-1.xx&_nc_gid=Vj-hvWV9W_P8ZRNVd_Lj3A&_nc_ss=7b289&oh=00_AQC0BgaEp99KKXvgYYd9uVYMHC0XuzO-SVIyen4WTzBkyw&oe=6A6D8255",
      "verified": true
    },
    "engagement": {
      "views": 598000,
      "likes": 6581,
      "comments": 89,
      "shares": 531
    },
    "isVideo": true,
    "link": "https://go.nasa.gov/3QvQc4k"
  },
  "facebook-event-details": {
    "platform": "facebook",
    "id": "1501904507609251",
    "url": "https://www.facebook.com/events/1501904507609251/",
    "name": "The Best of Chicago Comedy Showcase at Zanies Rosemont",
    "description": "Get ready for an unforgettable evening of laughter as Chicago's comedy scene brings its A-game to the stage! \"The Best of Chicago Showcase\" features a dynamic lineup of the city's funniest stand-up comedians, delivering a blend of fresh, cutting-edge material and beloved, time-tested jokes.",
    "startDate": "2026-08-19T19:00:00-05:00",
    "endDate": "2026-08-19T20:30:00-05:00",
    "timezone": "America/Chicago",
    "startTime": "Wednesday 19 August 2026 from 19:00-20:30 CDT",
    "duration": "1 hr 30 min",
    "durationSeconds": 5400,
    "eventType": "Comedy",
    "isOnline": false,
    "isPast": false,
    "isCanceled": false,
    "address": "5437 Park Pl, Des Plaines, IL 60018-3732, United States",
    "image": "https://lookaside.fbsbx.com/lookaside/crawler/media/?media_id=1501904507609251",
    "location": {
      "name": "5437 Park Place, Rosemont, IL, United States, Illinois 60018",
      "city": "Rosemont, IL",
      "latitude": 41.97826,
      "longitude": -87.86738,
      "countryCode": "US"
    },
    "organizers": [
      {
        "id": "100064546187809",
        "name": "Zanies Rosemont Comedy Club",
        "url": "https://www.facebook.com/RosemontZanies",
        "verified": false
      }
    ],
    "ticketsUrl": "https://www.etix.com/ticket/p/74170542/the-best-of-chicago-showcase-rosemont-zanies-rosemont",
    "categories": [
      {
        "label": "Comedy",
        "url": "https://www.facebook.com/events/search/?filters=eyJmaWx0ZXJfZXZlbnRzX2NhdGVnb3J5OjAiOiJ7XCJuYW1lXCI6XCJmaWx0ZXJfZXZlbnRzX2NhdGVnb3J5XCIsXCJhcmdzXCI6XCI2NjAwMzI2MTc1MzYzNzNcIn0ifQ%3D%3D&q=Comedy"
      }
    ]
  },
  "facebook-event-search": {
    "query": "comedy Chicago",
    "location": "Chicago",
    "totalReturned": 5,
    "events": [
      {
        "platform": "facebook",
        "id": "1501904507609251",
        "url": "https://www.facebook.com/events/1501904507609251/",
        "name": "The Best of Chicago Comedy Showcase at Zanies Rosemont",
        "description": "Get ready for an unforgettable evening of laughter as Chicago's comedy scene brings its A-game to the stage! \"The Best of Chicago Showcase\" features a dynamic lineup of the city's funniest stand-up comedians, delivering a blend of fresh, cutting-edge material and beloved, time-tested jokes.",
        "startDate": "2026-08-19T19:00:00-05:00",
        "endDate": "2026-08-19T20:30:00-05:00",
        "timezone": "America/Chicago",
        "startTime": "Wednesday 19 August 2026 from 19:00-20:30 CDT",
        "duration": "1 hr 30 min",
        "durationSeconds": 5400,
        "eventType": "Comedy",
        "isOnline": false,
        "isPast": false,
        "isCanceled": false,
        "address": "5437 Park Pl, Des Plaines, IL 60018-3732, United States",
        "image": "https://lookaside.fbsbx.com/lookaside/crawler/media/?media_id=1501904507609251",
        "location": {
          "name": "5437 Park Place, Rosemont, IL, United States, Illinois 60018",
          "city": "Rosemont, IL",
          "latitude": 41.97826,
          "longitude": -87.86738,
          "countryCode": "US"
        },
        "organizers": [
          {
            "id": "100064546187809",
            "name": "Zanies Rosemont Comedy Club",
            "url": "https://www.facebook.com/RosemontZanies",
            "verified": false
          }
        ],
        "ticketsUrl": "https://www.etix.com/ticket/p/74170542/the-best-of-chicago-showcase-rosemont-zanies-rosemont",
        "categories": [
          {
            "label": "Comedy",
            "url": "https://www.facebook.com/events/search/?filters=eyJmaWx0ZXJfZXZlbnRzX2NhdGVnb3J5OjAiOiJ7XCJuYW1lXCI6XCJmaWx0ZXJfZXZlbnRzX2NhdGVnb3J5XCIsXCJhcmdzXCI6XCI2NjAwMzI2MTc1MzYzNzNcIn0ifQ%3D%3D&q=Comedy"
          }
        ]
      },
      {
        "platform": "facebook",
        "id": "1345542687414105",
        "url": "https://www.facebook.com/events/1345542687414105/",
        "name": "Anthony Mrocka at Zanies Rosemont",
        "startDate": "2026-08-05T19:00:00-05:00",
        "timezone": "America/Chicago",
        "startTime": "Wed, Aug 5 at 7:00 PM CDT",
        "eventType": "PUBLIC_TYPE",
        "isPast": false,
        "isCanceled": false,
        "location": {
          "name": "5437 Park Place, Rosemont, IL, United States, Illinois 60018",
          "city": "Rosemont, IL",
          "countryCode": "US"
        },
        "organizers": [
          {
            "id": "100064546187809",
            "name": "Zanies Rosemont Comedy Club",
            "url": "https://www.facebook.com/RosemontZanies",
            "verified": false
          }
        ]
      }
    ]
  },
  "facebook-group-posts": {
    "url": "https://www.facebook.com/groups/dogspotting",
    "totalReturned": 8,
    "posts": [
      {
        "platform": "facebook",
        "url": "https://www.facebook.com/groups/dogspotting/posts/10165927007174467/",
        "id": "10165927007174467",
        "caption": "Dog in a basket…I repeat…dog in a basket!",
        "description": "Dog in a basket…I repeat…dog in a basket!",
        "publishedAt": "2026-07-27T16:34:51.000Z",
        "author": {
          "displayName": "Beth Oxford"
        },
        "engagement": {
          "likes": 87,
          "comments": 0
        },
        "isVideo": false,
        "permalink": "https://www.facebook.com/groups/dogspotting/posts/10165927007174467/"
      },
      {
        "platform": "facebook",
        "url": "https://www.facebook.com/groups/dogspotting/posts/10165913663824467/",
        "id": "10165913663824467",
        "caption": "Waiting patiently in the Mustang.",
        "description": "Waiting patiently in the Mustang.",
        "publishedAt": "2026-07-24T22:16:11.000Z",
        "thumbnailUrl": "https://scontent-iad6-1.xx.fbcdn.net/v/t39.30808-6/754824625_10163571025602896_890543610805686018_n.jpg?stp=dst-jpg_tt6&cstp=mx2048x1536&ctp=p600x600&_nc_cat=107&ccb=1-7&_nc_sid=63...",
        "author": {
          "displayName": "Chet Rhodes"
        },
        "engagement": {
          "likes": 36,
          "comments": 2
        },
        "isVideo": false,
        "permalink": "https://www.facebook.com/groups/dogspotting/posts/10165913663824467/"
      }
    ],
    "sortBy": "CHRONOLOGICAL"
  },
  "facebook-marketplace-item": {
    "platform": "facebook",
    "id": "2467979733629080",
    "url": "https://www.facebook.com/marketplace/item/2467979733629080/",
    "title": "Gaiam Classic Balance Ball Chair - Ergonomic Office/Desk Chair",
    "price": 50.0,
    "priceFormatted": "$50",
    "currency": "USD",
    "location": {
      "name": "Fresno, CA",
      "city": "Fresno",
      "state": "CA",
      "countryCode": "US",
      "latitude": null,
      "longitude": null
    },
    "city": "Fresno",
    "state": "CA",
    "cityPageId": "107983435897193",
    "isSold": false,
    "isPending": false,
    "isHidden": false,
    "deliveryTypes": ["IN_PERSON", "SHIPPING_ONSITE"],
    "status": "available",
    "priceAmount": 5000,
    "createdAt": "2026-07-18T17:45:28+00:00"
  },
  "facebook-marketplace-location-search": {
    "query": "Austin",
    "totalReturned": 3,
    "locations": [
      {
        "id": "109791499039942",
        "slug": "austin",
        "name": "Austin, TX",
        "city": "Austin",
        "state": "TX",
        "latitude": 30.2677,
        "longitude": -97.7475
      },
      {
        "slug": "austin-minnesota",
        "name": "Austin, MN",
        "city": "Austin",
        "state": "MN",
        "latitude": 43.6666,
        "longitude": -92.9746
      },
      {
        "slug": "austin-indiana",
        "name": "Austin, IN",
        "city": "Austin",
        "state": "IN",
        "latitude": 38.7584,
        "longitude": -85.808
      }
    ],
    "timings": {
      "path": "ambiguous_table",
      "hubMs": 0,
      "hubCount": 0,
      "totalMs": 2
    }
  },
  "facebook-marketplace-search": {
    "query": "desk chair",
    "location": "Austin, TX",
    "filters": {
      "minPrice": "50",
      "maxPrice": "200",
      "sortBy": "price_ascend",
      "daysSinceListed": "30"
    },
    "totalReturned": 5,
    "hasMore": true,
    "nextCursor": "eyJ2IjoxLCJxIjoiZGVzayBjaGFpciIsImxvYyI6IkF1c3RpbiwgVFgiLCJmIjp7Im1pblByaWNlIjoiNTAiLCJtYXhQcmljZSI6IjIwMCIsInNvcnRCeSI6InByaWNlX2FzY2VuZCIsImRheXNTaW5jZUxpc3RlZCI6IjMwIn0sInNraXAiOjUsImVjIjoie1wicGdcIjowLFwiYjJjXCI6e1wiYnJcIjpcIlwiLFwiaXRcIjowLFwiaG1zclwiOmZhbHNlLFwidGJpXCI6MH0sXCJjMmNcIjp7XCJiclwiOlwiQWJwaXVWdElpSVhFajlWV0ZVZEl4czFJUi13SldycGx1NWlNTGNYOURiMTBTQzhFQk93YzFXZi1RcmpOcDM3elBFWlg5ZGJNdlNDa0ZUay1sclBucTlCTnJGWURUdHg5bFZlMFhGd2FGdEQ0RG03T3RkemJBMU5MVWdkLUFrclRhc3hPZHVmWldmVkJTZlJTTG1SYmZydWVBVW85QTRNZXBqc1I0cm0zV09FejNSYlhIVnRrcm9SV21JZ1liUUZYN0Y0WnpfNnlhQTRkdThSY1BRbzJJeUwtcC1Ca3hlTVhHblFLSHZ1ZXJyZ2J2alN0M2hXNEFNdDZlclE1UkpGOUhSdFk3b1RLbGI2bTVfTUZEd2FqcXdMbUJhSzBKWlVKN3ZsUnczVFlQMm9SSjVoMDFxSndUU2Z6enduMkFodEFlcVFaUEs0eWV5OEc0WGZ0bm81cERJYzZDUWNzTWtRdEJjZDE2R3FNanQwQXhybkNJM1A0OFZINmZqcG9vM3hGTnJqU3ZvRDhOOGNxbVFMaVJzVy1SRlF2am9CNTdGWkkzVkpMLXhLN204cUVNaUczcnZKUlRJd2ZLS2VHdTlBckJXbi1SODJuNkVPUU9MU2loUkppTlY4Q0Rxamw0WnIyUVJmcXFMN3hmNzZPSnBzaEVxWi05Z1JWRWlzaFdJcUx1eWY0YzF6NE1zMUZ5YTNDeUZxamgtdDBtei1nR3dTZGhEOEhxelloQXhYWGZsU0NkdGUxVWIwaVBiRVctSUhqQmVjXCIsXCJpdFwiOjI0LFwicnBi …",
    "listings": [
      {
        "platform": "facebook",
        "id": "4482233215369733",
        "title": "Vintage 1980s Postmodern \"American Lighting\" Gooseneck Desk Lamp",
        "url": "https://www.facebook.com/marketplace/item/4482233215369733/",
        "price": 50.0,
        "priceFormatted": "$50",
        "priceAmount": 5000,
        "currency": "USD",
        "categoryId": "1569171756675761",
        "location": "Benson, AZ",
        "city": "Benson",
        "state": "AZ",
        "cityPageId": "109791499039942",
        "isSold": false,
        "isPending": false,
        "isHidden": false,
        "deliveryTypes": [
          "IN_PERSON",
          "SHIPPING_ONSITE"
        ],
        "image": "https://scontent-atl3-3.xx.fbcdn.net/v/t39.84726-6/748718464_1472100928021023_7004614235492134530_n.jpg?stp=c0.87.526.526a_dst-jpg_p526x395_tt6&_nc_cat=109&ccb=1-7&_nc_sid=92e707&_nc_ohc=Osco_iBPSHsQ7kNvwE88Z2B&_nc_oc=AdrnNrq4GxtoKGWCDi_qxKj2BfO-OcysnTpk7mDO5d-84zPauj6YWLhxJPZuiRErURoSW7OUci-LjqdvjivdYc4u&_nc_zt=14&_nc_ht=scontent-atl3-3.xx&_nc_gid=48UkL5OoevcKmJAZmxtYnw&_nc_ss=7b289&oh=00_AQFTCh3FFtSTB-AA28V6Jr1NtrTs9PSVie1b1KW_xUkkNw&oe=6A753B85",
        "createdAt": "2026-07-16T06:02:16+00:00",
        "status": "available",
        "isPublished": true,
        "isLocal": false,
        "shipsOutsideRadius": true
      },
      {
        "platform": "facebook",
        "id": "2467979733629080",
        "title": "Gaiam Classic Balance Ball Chair - Ergonomic Office/Desk Chair",
        "url": "https://www.facebook.com/marketplace/item/2467979733629080/",
        "price": 50.0,
        "priceFormatted": "$50",
        "priceAmount": 5000,
        "currency": "USD",
        "categoryId": "1383948661922113",
        "location": "Fresno, CA",
        "city": "Fresno",
        "state": "CA",
        "cityPageId": "107983435897193",
        "isSold": false,
        "isPending": false,
        "isHidden": false,
        "deliveryTypes": [
          "IN_PERSON",
          "SHIPPING_ONSITE"
        ],
        "image": "https://scontent-atl3-3.xx.fbcdn.net/v/t39.84726-6/749286700_1116782047845292_1788708914246608626_n.jpg?stp=c0.81.526.526a_dst-jpg_p526x395_tt6&_nc_cat=110&ccb=1-7&_nc_sid=92e707&_nc_ohc=gbzkYGqnXmYQ7kNvwGzH1qf&_nc_oc=AdqLUHLAdzpxyU4TF9F6Xf5v9Tib9M6UCrmYThgY8kMR7j8y-uMyvFm3zwMzYYMwX1rcrfF1-yMiBdhJbknk-W2-&_nc_zt=14&_nc_ht=scontent-atl3-3.xx&_nc_gid=48UkL5OoevcKmJAZmxtYnw&_nc_ss=7b289&oh=00_AQHJWOlgp25sCHb9Xzuo5yQVzSCjOZpSF6EaQpKDCudKZA&oe=6A751DFD",
        "createdAt": "2026-07-18T17:45:28+00:00",
        "status": "available",
        "isPublished": true,
        "isLocal": false,
        "shipsOutsideRadius": true
      }
    ]
  },
  "facebook-page-details": {
    "platform": "facebook",
    "url": "https://www.facebook.com/NASA",
    "username": "NASA",
    "displayName": "NASA",
    "fullName": "NASA - National Aeronautics and Space Administration",
    "bio": "Explore the universe and discover our home planet. \nThere's space for everybody. ✨",
    "followers": 28000000,
    "followersApproximate": true,
    "following": 52,
    "likes": 28657418,
    "talkingAbout": 87542,
    "verified": true,
    "profileImage": "https://scontent-ams2-1.xx.fbcdn.net/v/t39.30808-1/243095782_416661036495945_3843362260429099279_n.png?stp=dst-png&cstp=mx800x800&ctp=s200x200&_nc_cat=1&ccb=1-7&_nc_sid=f907e8&_nc_ohc=p-I5WtLvyPIQ7kNvwGNqQPz&_nc_oc=AdrHdhh-STMw354rnrjuFVcB_iniLxrLE45ODKhANclECwfCGQeoggO3Y69bFTeV3u0&_nc_zt=24&_nc_ht=scontent-ams2-1.xx&_nc_gid=zOsU00hAz3vIE0xLeuEEjA&_nc_ss=7b289&oh=00_AQG0XVSduh4nqyw_0PUHNXFrPsaQWgImWMlBgnFHw-mkCQ&oe=6A764C55",
    "coverImage": "https://scontent-ams2-1.xx.fbcdn.net/v/t39.30808-6/663298991_1496429661852405_5171518456419416626_n.jpg?stp=dst-jpg_tt6&cstp=mx2048x1366&ctp=s960x960&_nc_cat=105&ccb=1-7&_nc_sid=cc71e4&_nc_ohc=jJ1aogFmMrAQ7kNvwEgUz8r&_nc_oc=AdpCeQFsutnpqxSVozuP96M4esxiGp_E5LtUwYSr-XGvAxD-YEWuH7-t6kuRXoOl2hI&_nc_zt=23&_nc_ht=scontent-ams2-1.xx&_nc_gid=zOsU00hAz3vIE0xLeuEEjA&_nc_ss=7b289&oh=00_AQFVelTF7GeR-4rMFhrEk2wwf2DLSBrFT0qUkp3H6V8uKg&oe=6A7628E3",
    "category": "Government organization",
    "website": "https://nasa.gov/nasa-app",
    "email": "public-inquiries@hq.nasa.gov"
  },
  "facebook-profile-events": {
    "platform": "facebook",
    "url": "https://www.facebook.com/MadisonSquareGarden",
    "totalReturned": 5,
    "events": [
      {
        "platform": "facebook",
        "id": "1595969051643502",
        "url": "https://www.facebook.com/events/1595969051643502/",
        "name": "J. Cole: The Fall-Off Tour",
        "startDate": "2026-08-04T20:00:00-04:00",
        "timezone": "America/New_York",
        "startTime": "Tue, Aug 4 at 8:00 PM EDT",
        "eventType": "PUBLIC_TYPE",
        "isPast": false,
        "isCanceled": false,
        "location": {
          "name": "Madison Square Garden"
        }
      },
      {
        "platform": "facebook",
        "id": "1379008927241796",
        "url": "https://www.facebook.com/events/1379008927241796/",
        "name": "Hilary Duff: the lucky me tour",
        "startDate": "2026-08-05T19:00:00-04:00",
        "timezone": "America/New_York",
        "startTime": "Wed, Aug 5 at 7:00 PM EDT",
        "eventType": "PUBLIC_TYPE",
        "isPast": false,
        "isCanceled": false,
        "location": {
          "name": "Madison Square Garden"
        }
      }
    ]
  },
  "facebook-profile-photos": {
    "url": "https://www.facebook.com/NASA",
    "totalReturned": 8,
    "photos": [
      {
        "platform": "facebook",
        "id": "1587644152730955",
        "url": "https://www.facebook.com/photo.php?fbid=1587644152730955",
        "image": "https://scontent-dfw6-2.xx.fbcdn.net/v/t39.99422-6/758964186_1384158170473704_9008748322111971488_n.png?stp=dst-jpg_tt6&cstp=mx2047x1012&ctp=s2047x1012&_nc_cat=1&ccb=1-7&_nc_sid=12...",
        "width": 2047,
        "height": 1012,
        "accessibilityCaption": "A galaxy cluster in deep space. It is filled with elliptical galaxies: small, bright white glowing ovals. The two largest elliptical galaxies, left and right of center, are bright cores that radiate light. Unrelated, distant galaxies are scattered around as red smudges and dots. Many of these are stretched out into red arcs and lines by the galaxy cluster’s strong gravity, creating multiple images in places. Numerous spiral galaxies and bright stars appear in the foreground. Credit: ESA/Webb, NASA & CSA, S. Fujimoto"
      },
      {
        "platform": "facebook",
        "id": "1586655189496518",
        "url": "https://www.facebook.com/photo.php?fbid=1586655189496518",
        "image": "https://scontent-dfw6-2.xx.fbcdn.net/v/t39.30808-6/756229023_1586655192829851_1923291187225748989_n.jpg?stp=dst-jpg_tt6&cstp=mx1884x1054&ctp=s1884x1054&_nc_cat=110&ccb=1-7&_nc_sid=...",
        "width": 1884,
        "height": 1054,
        "accessibilityCaption": "An aerial view of a spacecraft about to land on Earth; the capsule is barely visible, but a large white-and-red parachute billows above it. The plain around it is flat and featureless. Credit: NASA+"
      }
    ]
  },
  "facebook-profile-posts": {
    "url": "https://www.facebook.com/NASA",
    "totalReturned": 5,
    "posts": [
      {
        "platform": "facebook",
        "url": "https://www.facebook.com/NASA/posts/pfbid0TBwRTPkxfaLhYBjfsK1xApVksSVHddNrpqUqcqNsKxVvKjqT6dAG8HnxWGA3odp5l",
        "id": "1587644189397618",
        "caption": "This is messy 😬\n \nA galaxy cluster is exactly what you'd think: a bunch of galaxies grouped together. This galaxy cluster is made of two sub-clusters with similar mass, locked in a messy process of interacting and separating. Eventually, they'll merge. Though their relationship is… complicated, it helps us study the region.\n \nThe cluster's extreme and concentrated mass curves light with its gravity. This is called gravitational lensing, and it works like a glass lens bending and focusing light. Objects are magnified and their brightness is enhanced, so if they lie in exactly the right place, background galaxies and even individual stars that would have been far too faint and distant to spot will be made visible.",
        "description": "This is messy 😬\n \nA galaxy cluster is exactly what you'd think: a bunch of galaxies grouped together. This galaxy cluster is made of two sub-clusters with similar mass, locked in a messy process of interacting and separating. Eventually, they'll merge. Though their relationship is… complicated, it helps us study the region.\n \nThe cluster's extreme and concentrated mass curves light with its gravity. This is called gravitational lensing, and it works like a glass lens bending and focusing light. Objects are magnified and their brightness is enhanced, so if they lie in exactly the right place, background galaxies and even individual stars that would have been far too faint and distant to spot will be made visible.",
        "publishedAt": "2026-07-27T15:33:07.000Z",
        "thumbnailUrl": "https://scontent-dfw5-2.xx.fbcdn.net/v/t39.99422-6/758964186_1384158170473704_9008748322111971488_n.png?stp=dst-jpg_tt6&cstp=mx2047x1012&ctp=s1080x2048&_nc_cat=1&ccb=1-7&_nc_sid=12...",
        "author": {
          "username": "NASA",
          "displayName": "NASA - National Aeronautics and Space Administration",
          "url": "https://www.facebook.com/NASA"
        },
        "engagement": {
          "likes": 1861,
          "comments": 84,
          "views": null,
          "shares": null
        },
        "isVideo": false
      },
      {
        "platform": "facebook",
        "url": "https://www.facebook.com/reel/1380134307388381",
        "id": "1584419709720066",
        "caption": "During his eight months aboard the International Space Station, NASA astronaut Chris Williams conducted numerous experiments to improve life on Earth and prepare us for missions to the Moon and Mars.\n\nFrom cancer research to advancing technology, read about Williams’ work during his first time in space: https://go.nasa.gov/3RavGXj",
        "description": "During his eight months aboard the International Space Station, NASA astronaut Chris Williams conducted numerous experiments to improve life on Earth and prepare us for missions to the Moon and Mars.\n\nFrom cancer research to advancing technology, read about Williams’ work during his first time in space: https://go.nasa.gov/3RavGXj",
        "publishedAt": "2026-07-23T16:31:54.000Z",
        "durationSeconds": 112.946,
        "thumbnailUrl": "https://scontent-sea5-1.xx.fbcdn.net/v/t15.5256-10/754970839_803020196231197_5928609298551288000_n.jpg?stp=dst-jpg_tt6&cstp=mx720x405&ctp=s720x405&_nc_cat=102&ccb=1-7&_nc_sid=be830...",
        "videoUrl": "https://video-sea1-1.xx.fbcdn.net/o1/v/t2/f2/m366/AQNNFuni8clCeMB5VeV07ZDIzXWkhBI5ozM_78otCALjoD72HsRW7yvnWXM_b0WGcKAjPk-KGDhCqRkGsaoZ57noEirZQ7LpYHZZbTVu3jMMQg.mp4?_nc_cat=106&_nc...",
        "author": {
          "username": "NASA",
          "displayName": "NASA - National Aeronautics and Space Administration",
          "url": "https://www.facebook.com/NASA",
          "profileImage": "https://scontent-sea5-1.xx.fbcdn.net/v/t39.30808-1/243095782_416661036495945_3843362260429099279_n.png?stp=cp0_dst-png&cstp=mx800x800&ctp=s80x80&_nc_cat=108&ccb=1-7&_nc_sid=2d3e12&...",
          "verified": true
        },
        "engagement": {
          "views": 411000,
          "likes": 5594,
          "comments": 170,
          "shares": 240
        },
        "isVideo": true,
        "link": "https://go.nasa.gov/3RavGXj"
      }
    ],
    "scrapedAt": "2026-08-03T11:00:00Z"
  },
  "facebook-profile-reels": {
    "url": "https://www.facebook.com/NASA",
    "totalReturned": 6,
    "reels": [
      {
        "platform": "facebook",
        "url": "https://www.facebook.com/reel/1380134307388381",
        "id": "1584419709720066",
        "caption": "During his eight months aboard the International Space Station, NASA astronaut Chris Williams conducted numerous experiments to improve life on Earth and prepare us for missions to the Moon and Mars.\n\nFrom cancer research to advancing technology, read about Williams’ work during his first time in space: https://go.nasa.gov/3RavGXj",
        "description": "During his eight months aboard the International Space Station, NASA astronaut Chris Williams conducted numerous experiments to improve life on Earth and prepare us for missions to the Moon and Mars.\n\nFrom cancer research to advancing technology, read about Williams’ work during his first time in space: https://go.nasa.gov/3RavGXj",
        "publishedAt": "2026-07-23T16:31:54.000Z",
        "durationSeconds": 112.946,
        "thumbnailUrl": "https://scontent-iad6-1.xx.fbcdn.net/v/t15.5256-10/754970839_803020196231197_5928609298551288000_n.jpg?stp=dst-jpg_tt6&cstp=mx720x405&ctp=s720x405&_nc_cat=102&ccb=1-7&_nc_sid=be830...",
        "videoUrl": "https://video-iad6-1.xx.fbcdn.net/o1/v/t2/f2/m366/AQNNFuni8clCeMB5VeV07ZDIzXWkhBI5ozM_78otCALjoD72HsRW7yvnWXM_b0WGcKAjPk-KGDhCqRkGsaoZ57noEirZQ7LpYHZZbTVu3jMMQg.mp4?_nc_cat=106&_nc...",
        "author": {
          "username": "NASA",
          "displayName": "NASA - National Aeronautics and Space Administration",
          "url": "https://www.facebook.com/NASA",
          "profileImage": "https://scontent-iad3-1.xx.fbcdn.net/v/t39.30808-1/243095782_416661036495945_3843362260429099279_n.png?stp=cp0_dst-png&cstp=mx800x800&ctp=s40x40&_nc_cat=108&ccb=1-7&_nc_sid=2d3e12&...",
          "verified": true
        },
        "engagement": {
          "views": 411000,
          "likes": 5597,
          "comments": 170,
          "shares": 240
        },
        "isVideo": true,
        "link": "https://go.nasa.gov/3RavGXj"
      },
      {
        "platform": "facebook",
        "url": "https://www.facebook.com/reel/1376651124309650",
        "id": "1567272851434752",
        "caption": "There will be more than just fireworks to see in the night sky this month!\n\nYou can look forward to these celestial sights in July:\n- A lunar-planetary alignment\n- A visiting comet\n- A good look at Saturn and the Milky Way\n\nHappy skywatching! https://go.nasa.gov/3QvQc4k",
        "description": "There will be more than just fireworks to see in the night sky this month!\n\nYou can look forward to these celestial sights in July:\n- A lunar-planetary alignment\n- A visiting comet\n- A good look at Saturn and the Milky Way\n\nHappy skywatching! https://go.nasa.gov/3QvQc4k",
        "publishedAt": "2026-07-02T15:03:11.000Z",
        "durationSeconds": 200.016,
        "thumbnailUrl": "https://scontent-iad3-2.xx.fbcdn.net/v/t15.5256-10/735149954_4435586749988646_521208314578416779_n.jpg?stp=dst-jpg_tt6&cstp=mx720x405&ctp=s720x405&_nc_cat=111&ccb=1-7&_nc_sid=be830...",
        "videoUrl": "https://video-iad3-2.xx.fbcdn.net/o1/v/t2/f2/m366/AQOh7ZLRZfB5SIGETu_uz2jbsqvY3dW7G3sGdKsNsX627DpYoTuCxs26FyYE4T4rDzRdvIV2tOCYJi5hs8Gs1EaQEL7_LhQnAXKuILiY508JFg.mp4?_nc_cat=103&_nc...",
        "author": {
          "username": "NASA",
          "displayName": "NASA - National Aeronautics and Space Administration",
          "url": "https://www.facebook.com/NASA",
          "profileImage": "https://scontent-iad3-1.xx.fbcdn.net/v/t39.30808-1/243095782_416661036495945_3843362260429099279_n.png?stp=cp0_dst-png&cstp=mx800x800&ctp=s40x40&_nc_cat=108&ccb=1-7&_nc_sid=2d3e12&...",
          "verified": true
        },
        "engagement": {
          "views": 598000,
          "likes": 6582,
          "comments": 89,
          "shares": 531
        },
        "isVideo": true,
        "link": "https://go.nasa.gov/3QvQc4k"
      }
    ],
    "scrapedAt": "2026-08-03T11:00:00Z"
  },
  "facebook-summarizer": {
    "platform": "facebook",
    "url": "https://www.facebook.com/NASA/posts/pfbid0TBwRTPkxfaLhYBjfsK1xApVksSVHddNrpqUqcqNsKxVvKjqT6dAG8HnxWGA3odp5l",
    "summary": "The video discusses the concept of a galaxy cluster, which consists of multiple galaxies grouped together. Specifically, it focuses on a galaxy cluster made up of two sub-clusters of similar mass that are currently interacting and separating in a complex manner. This dynamic relationship is significant for scientific study, as it provides insights into the behavior of galaxies in close proximity to one another. Eventually, these sub-clusters are expected to merge, further contributing to our understanding of galaxy formation and evolution.\n\nAdditionally, the video highlights the phenomenon of gravitational lensing, where the concentrated mass of the cluster bends light due to its gravitational pull. This effect allows astronomers to observe distant and faint background galaxies and stars that would otherwise be invisible, enhancing our ability to study the universe and its structures. The interplay of these two sub-clusters not only illustrates the chaotic nature of cosmic interactions but also serves as a valuable tool for astronomical research.",
    "keyPoints": [
      "A galaxy cluster consists of multiple galaxies grouped together.",
      "The featured cluster contains two sub-clusters of similar mass interacting and separating.",
      "The relationship between the sub-clusters is complex but crucial for scientific study.",
      "Gravitational lensing occurs due to the cluster's mass, bending and focusing light.",
      "This lensing effect allows the observation of faint background galaxies and stars.",
      "The merging of the sub-clusters will provide further insights into galaxy evolution."
    ],
    "topics": [
      "galaxy cluster",
      "gravitational lensing",
      "cosmic interactions",
      "astronomy",
      "galaxy formation",
      "space science"
    ],
    "sentiment": "neutral"
  },
  "github-activity": {
    "username": "getify",
    "eventCeiling": 90,
    "totalReturned": 2,
    "nextCursor": "eyJ2IjoxLCJrIjoiYWN0aXZpdHkiLCJwIjoyfQ",
    "hasMore": true,
    "events": [
      {
        "id": "9001",
        "type": "PushEvent",
        "repo": "getify/You-Dont-Know-JS",
        "repoUrl": "https://github.com/getify/You-Dont-Know-JS",
        "payload": {
          "ref": "refs/heads/2nd-ed",
          "head": "deadbeef",
          "before": "cafebabe",
          "size": 1,
          "distinctSize": 1,
          "commits": [
            {
              "sha": "deadbeef",
              "message": "typo fix",
              "authorName": "Kyle Simpson",
              "authorEmail": "getify@gmail.com",
              "distinct": true
            }
          ]
        },
        "createdAt": "2026-07-01T10:00:00Z",
        "public": true
      },
      {
        "id": "9002",
        "type": "IssuesEvent",
        "repo": "getify/You-Dont-Know-JS",
        "repoUrl": "https://github.com/getify/You-Dont-Know-JS",
        "payload": {
          "action": "opened",
          "number": 7,
          "title": "Clarify chapter 3",
          "url": "https://github.com/getify/You-Dont-Know-JS/issues/7",
          "state": "open"
        },
        "createdAt": "2026-06-28T10:00:00Z",
        "public": true
      }
    ]
  },
  "github-contributions": {
    "username": "getify",
    "source": "github.com/users/getify/contributions",
    "url": "https://github.com/getify",
    "totalContributions": 164,
    "from": "2025-08-03",
    "to": "2025-08-05",
    "currentStreak": 2,
    "days": [
      {
        "date": "2025-08-03",
        "count": 0,
        "level": 0
      },
      {
        "date": "2025-08-04",
        "count": 5,
        "level": 2
      }
    ]
  },
  "github-followers": {
    "username": "getify",
    "totalReturned": 2,
    "nextCursor": "eyJ2IjoxLCJrIjoiZm9sbG93ZXJzIiwicCI6Mn0",
    "hasMore": true,
    "followers": [
      {
        "id": 206,
        "login": "sprsquish",
        "type": "User",
        "url": "https://github.com/sprsquish",
        "avatar": "https://avatars.githubusercontent.com/u/206?v=4"
      },
      {
        "id": 365,
        "login": "pius",
        "type": "User",
        "url": "https://github.com/pius",
        "avatar": "https://avatars.githubusercontent.com/u/365?v=4"
      }
    ]
  },
  "github-following": {
    "username": "getify",
    "totalReturned": 2,
    "nextCursor": "eyJ2IjoxLCJrIjoiZm9sbG93aW5nIiwicCI6Mn0",
    "hasMore": true,
    "following": [
      {
        "id": 579,
        "login": "mikeal",
        "type": "User",
        "url": "https://github.com/mikeal",
        "avatar": "https://avatars.githubusercontent.com/u/579?v=4"
      },
      {
        "id": 9950313,
        "login": "nodejs",
        "type": "Organization",
        "url": "https://github.com/nodejs",
        "avatar": "https://avatars.githubusercontent.com/u/9950313?v=4"
      }
    ]
  },
  "github-pull-requests": {
    "repository": "vercel/next.js",
    "state": "closed",
    "totalReturned": 2,
    "nextCursor": "eyJ2IjoxLCJrIjoicHVsbHMiLCJwIjoyfQ",
    "hasMore": true,
    "pullRequests": [
      {
        "id": 11,
        "number": 100,
        "title": "docs: clarify cursor",
        "state": "closed",
        "draft": false,
        "url": "https://github.com/vercel/next.js/pull/100",
        "author": {
          "id": 1,
          "login": "example",
          "url": "https://github.com/example",
          "avatar": "https://avatars.githubusercontent.com/u/1?v=4"
        },
        "labels": [
          {
            "name": "documentation",
            "color": "0075ca"
          }
        ],
        "head": {
          "ref": "docs-cursor",
          "sha": "aaa111",
          "label": "example:docs-cursor"
        },
        "base": {
          "ref": "canary",
          "sha": "bbb222",
          "label": "vercel:canary"
        },
        "createdAt": "2026-06-01T00:00:00Z",
        "updatedAt": "2026-06-02T00:00:00Z",
        "closedAt": "2026-06-02T12:00:00Z",
        "mergedAt": "2026-06-02T12:00:00Z"
      },
      {
        "id": 12,
        "number": 101,
        "title": "WIP: experimental",
        "state": "closed",
        "draft": true,
        "url": "https://github.com/vercel/next.js/pull/101",
        "author": {
          "id": 2,
          "login": "dev",
          "url": "https://github.com/dev",
          "avatar": "https://avatars.githubusercontent.com/u/2?v=4"
        },
        "head": {
          "ref": "wip",
          "sha": "ccc",
          "label": "dev:wip"
        },
        "base": {
          "ref": "canary",
          "sha": "ddd",
          "label": "vercel:canary"
        },
        "createdAt": "2026-05-01T00:00:00Z",
        "updatedAt": "2026-05-03T00:00:00Z",
        "closedAt": "2026-05-03T00:00:00Z"
      }
    ]
  },
  "github-repositories": {
    "username": "torvalds",
    "sort": "pushed",
    "direction": "desc",
    "type": "owner",
    "totalReturned": 2,
    "nextCursor": "eyJ2IjoxLCJrIjoicmVwb3MiLCJwIjoyfQ",
    "hasMore": true,
    "repositories": [
      {
        "platform": "github",
        "type": "repository",
        "name": "linux",
        "fullName": "torvalds/linux",
        "url": "https://github.com/torvalds/linux",
        "description": "Linux kernel source tree",
        "owner": "torvalds",
        "ownerUrl": "https://github.com/torvalds",
        "ownerType": "User",
        "ownerAvatar": "https://avatars.githubusercontent.com/u/1024025?v=4",
        "language": "C",
        "stars": 239734,
        "forks": 63487,
        "openIssuesAndPrs": 3,
        "defaultBranch": "master",
        "licenseName": "Other",
        "isFork": false,
        "isArchived": false,
        "pushedAt": "2026-07-18T04:53:39Z",
        "createdAt": "2011-09-04T22:48:12Z",
        "updatedAt": "2026-07-18T18:40:38Z"
      },
      {
        "platform": "github",
        "type": "repository",
        "name": "libgit2",
        "fullName": "torvalds/libgit2",
        "url": "https://github.com/torvalds/libgit2",
        "description": "A cross-platform, linkable library implementation of Git.",
        "owner": "torvalds",
        "ownerUrl": "https://github.com/torvalds",
        "ownerType": "User",
        "ownerAvatar": "https://avatars.githubusercontent.com/u/1024025?v=4",
        "language": "C",
        "stars": 370,
        "forks": 28,
        "openIssuesAndPrs": 1,
        "defaultBranch": "main",
        "homepage": "https://libgit2.org/",
        "licenseName": "Other",
        "isFork": true,
        "isArchived": false,
        "pushedAt": "2023-12-19T11:45:42Z",
        "createdAt": "2022-07-30T03:30:56Z",
        "updatedAt": "2026-07-18T17:03:41Z"
      }
    ]
  },
  "github-repository": {
    "platform": "github",
    "type": "repository",
    "name": "linux",
    "fullName": "torvalds/linux",
    "url": "https://github.com/torvalds/linux",
    "description": "Linux kernel source tree",
    "owner": "torvalds",
    "ownerUrl": "https://github.com/torvalds",
    "ownerType": "User",
    "ownerAvatar": "https://avatars.githubusercontent.com/u/1024025?v=4",
    "language": "C",
    "stars": 241852,
    "forks": 63487,
    "watchers": 8345,
    "openIssuesAndPrs": 3,
    "defaultBranch": "master",
    "licenseName": "Other",
    "isFork": false,
    "isArchived": false,
    "size": 6228144,
    "visibility": "public",
    "hasIssues": false,
    "hasDiscussions": false,
    "pushedAt": "2026-07-18T04:53:39Z",
    "createdAt": "2011-09-04T22:48:12Z",
    "updatedAt": "2026-07-18T18:40:38Z"
  },
  "github-trending-developers": {
    "source": "github.com/trending/developers",
    "since": "weekly",
    "totalReturned": 2,
    "developers": [
      {
        "platform": "github",
        "type": "developer",
        "rank": 1,
        "login": "getify",
        "name": "Kyle Simpson",
        "url": "https://github.com/getify",
        "avatar": "https://avatars.githubusercontent.com/u/150330?v=4",
        "popularRepo": "getify/You-Dont-Know-JS",
        "popularRepoUrl": "https://github.com/getify/You-Dont-Know-JS",
        "popularRepoDescription": "A book series on JS",
        "since": "weekly",
        "followers": 45221,
        "publicRepos": 74,
        "bio": "Human-Centric Technologist",
        "location": "Austin, TX",
        "ownerType": "User"
      },
      {
        "platform": "github",
        "type": "developer",
        "rank": 2,
        "login": "sindresorhus",
        "name": "Sindre Sorhus",
        "url": "https://github.com/sindresorhus",
        "avatar": "https://avatars.githubusercontent.com/u/170270?v=4",
        "popularRepo": "sindresorhus/awesome",
        "popularRepoUrl": "https://github.com/sindresorhus/awesome",
        "since": "weekly",
        "followers": 70000,
        "publicRepos": 1200,
        "ownerType": "User"
      }
    ]
  },
  "github-trending-repositories": {
    "source": "github.com/trending",
    "since": "daily",
    "totalReturned": 2,
    "repositories": [
      {
        "platform": "github",
        "type": "repository",
        "rank": 1,
        "name": "computer",
        "fullName": "cloudflare/computer",
        "url": "https://github.com/cloudflare/computer",
        "description": "Remote browser infrastructure",
        "owner": "cloudflare",
        "ownerUrl": "https://github.com/cloudflare",
        "language": "TypeScript",
        "stars": 2514,
        "forks": 120,
        "starsGained": 796,
        "since": "daily"
      },
      {
        "platform": "github",
        "type": "repository",
        "rank": 2,
        "name": "hot-repo",
        "fullName": "example/hot-repo",
        "url": "https://github.com/example/hot-repo",
        "description": "Trending sample",
        "owner": "example",
        "ownerUrl": "https://github.com/example",
        "language": "Python",
        "stars": 1200,
        "forks": 80,
        "starsGained": 327,
        "since": "daily"
      }
    ]
  },
  "github-user": {
    "platform": "github",
    "type": "User",
    "login": "getify",
    "id": 150330,
    "nodeId": "MDQ6VXNlcjE1MDMzMA==",
    "url": "https://github.com/getify",
    "apiUrl": "https://api.github.com/users/getify",
    "name": "Kyle Simpson",
    "company": "Getify Solutions",
    "blog": "http://getify.me",
    "location": "Austin, TX",
    "bio": "Kyle Simpson is a Human-Centric Technologist. He's fighting for the people behind the pixels.",
    "avatar": "https://avatars.githubusercontent.com/u/150330?v=4",
    "publicRepos": 74,
    "publicGists": 411,
    "followers": 45221,
    "following": 3,
    "hireable": true,
    "siteAdmin": false,
    "createdAt": "2009-11-08T06:56:21Z",
    "updatedAt": "2026-04-28T20:14:44Z"
  },
  "google-ad-library-ad-details": {
    "platform": "google_ad_library",
    "id": "CR08395356613392728065",
    "url": "https://adstransparency.google.com/advertiser/AR18378488041124659201/creative/CR08395356613392728065",
    "text": "Discover {KeyWord:Nike Shoes} Online At Nike.com. Shop The Official Nike Site.",
    "headline": "{KeyWord:Nike Vomero}",
    "landingUrl": "nike.com",
    "adFormat": "text",
    "firstShown": "2025-09-19T13:04:37.000Z",
    "lastShown": "2026-07-23T06:18:08.000Z",
    "impressions": "7000-8000",
    "country": "Malta, United Arab Emirates, Cyprus, Belgium, United Kingdom, Czechia, Hungary, United States, Iceland, Ireland, Italy, Sweden, India, Spain, Greece, Croatia, Bulgaria, Portugal, Denmark, Lithuania, Poland, Netherlands, Germany, Australia, Norway, France, Romania",
    "advertiser": {
      "id": "AR18378488041124659201",
      "name": "Nike Retail BV",
      "url": "https://adstransparency.google.com/advertiser/AR18378488041124659201"
    },
    "media": []
  },
  "google-ad-library-advertiser-search": {
    "query": "nike",
    "country": "US",
    "totalReturned": 1,
    "advertisers": [
      {
        "id": "AR17365672681860497409",
        "name": "NIKE SRL",
        "url": "https://adstransparency.google.com/advertiser/AR17365672681860497409"
      }
    ]
  },
  "google-ad-library-company-ads": {
    "advertiser": "nike.com",
    "country": "US",
    "totalReturned": 5,
    "ads": [
      {
        "platform": "google_ad_library",
        "id": "CR13596485266373083137",
        "url": "https://adstransparency.google.com/advertiser/AR16735076323512287233/creative/CR13596485266373083137",
        "adFormat": "image",
        "firstShown": "2022-11-30T14:47:01.000Z",
        "lastShown": "2026-07-26T13:01:42.000Z",
        "advertiser": {
          "id": "AR16735076323512287233",
          "name": "Nike, Inc.",
          "url": "https://adstransparency.google.com/advertiser/AR16735076323512287233"
        },
        "media": [
          "https://tpc.googlesyndication.com/archive/simgad/1889619096914274581"
        ]
      },
      {
        "platform": "google_ad_library",
        "id": "CR00101170943954518017",
        "url": "https://adstransparency.google.com/advertiser/AR16735076323512287233/creative/CR00101170943954518017",
        "adFormat": "image",
        "firstShown": "2022-11-30T18:54:18.000Z",
        "lastShown": "2026-07-26T12:53:39.000Z",
        "advertiser": {
          "id": "AR16735076323512287233",
          "name": "Nike, Inc.",
          "url": "https://adstransparency.google.com/advertiser/AR16735076323512287233"
        },
        "media": [
          "https://tpc.googlesyndication.com/archive/simgad/3850814477191431652"
        ]
      }
    ]
  },
  "instagram-basic-profile": {
    "platform": "instagram",
    "url": "https://instagram.com/nike",
    "id": "13460080",
    "pk": "13460080",
    "username": "nike",
    "displayName": "Nike",
    "bio": "Just Do It.",
    "biographyWithEntities": {
      "rawText": "Just Do It.",
      "entities": []
    },
    "followers": 291638893,
    "following": 264,
    "postCount": 1668,
    "highlightReelCount": 5,
    "hasClips": true,
    "isPrivate": false,
    "verified": true,
    "isBusinessAccount": true,
    "isProfessionalAccount": true,
    "categoryName": "SPORTSWEAR_STORE",
    "shouldShowCategory": true,
    "profileImage": "https://instagram.fadb3-1.fna.fbcdn.net/v/t51.82787-19/551608484_18567162979020081_1135468084872726555_n.jpg?stp=dst-jpg_s320x320_tt6&efg=eyJ2ZW5jb2RlX3RhZyI6InByb2ZpbGVfcGljLmRqYW5nby4zOTkuYzIifQ&_nc_ht=instagram.fadb3-1.fna.fbcdn.net&_nc_cat=1&_nc_oc=Q6cZ2gFbXFmp_TeRpCCj6RR0tM15Q0oZBPR6ROg0ngZ8OMxwGUMoGki14pWoXpBkyDth51bqpCSkJFx6YosO0GZyPqK-&_nc_ohc=jOWQehR8N0kQ7kNvwHCN0UL&_nc_gid=k79WPpLD7fgQ0KoqHooi9A&edm=AOQ1c0wBAAAA&ccb=7-5&oh=00_AQGLKYnAo8kqPvpjPiPXB6947FKZdPXkp90fLn4BX7sh5w&oe=6A756ABA&_nc_sid=8b3546",
    "profileImageHd": "https://instagram.fadb3-1.fna.fbcdn.net/v/t51.82787-19/551608484_18567162979020081_1135468084872726555_n.jpg?stp=dst-jpg_s320x320_tt6&efg=eyJ2ZW5jb2RlX3RhZyI6InByb2ZpbGVfcGljLmRqYW5nby4zOTkuYzIifQ&_nc_ht=instagram.fadb3-1.fna.fbcdn.net&_nc_cat=1&_nc_oc=Q6cZ2gFbXFmp_TeRpCCj6RR0tM15Q0oZBPR6ROg0ngZ8OMxwGUMoGki14pWoXpBkyDth51bqpCSkJFx6YosO0GZyPqK-&_nc_ohc=jOWQehR8N0kQ7kNvwHCN0UL&_nc_gid=k79WPpLD7fgQ0KoqHooi9A&edm=AOQ1c0wBAAAA&ccb=7-5&oh=00_AQGLKYnAo8kqPvpjPiPXB6947FKZdPXkp90fLn4BX7sh5w&oe=6A756ABA&_nc_sid=8b3546",
    "profileImageUrl": "https://instagram.fadb3-1.fna.fbcdn.net/v/t51.82787-19/551608484_18567162979020081_1135468084872726555_n.jpg?stp=dst-jpg_s150x150_tt6&efg=eyJ2ZW5jb2RlX3RhZyI6InByb2ZpbGVfcGljLmRqYW5nby4zOTkuYzIifQ&_nc_ht=instagram.fadb3-1.fna.fbcdn.net&_nc_cat=1&_nc_oc=Q6cZ2gFbXFmp_TeRpCCj6RR0tM15Q0oZBPR6ROg0ngZ8OMxwGUMoGki14pWoXpBkyDth51bqpCSkJFx6YosO0GZyPqK-&_nc_ohc=jOWQehR8N0kQ7kNvwHCN0UL&_nc_gid=k79WPpLD7fgQ0KoqHooi9A&edm=AOQ1c0wBAAAA&ccb=7-5&oh=00_AQFUavH_AkjH7xOjK_XCMgEdFI82tO3J-qTmLtfVLMz1GA&oe=6A756ABA&_nc_sid=8b3546",
    "externalUrl": "http://empli.fi/nike",
    "fbid": "17841400602400210",
    "pronouns": [],
    "bioLinks": [
      {
        "title": null,
        "url": "http://empli.fi/nike",
        "linkType": "external"
      }
    ],
    "showAccountTransparencyDetails": true,
    "isEmbedsDisabled": false,
    "isRegulatedC18": false,
    "businessAddress": {
      "cityName": "Beaverton, Oregon",
      "cityId": "108410602520455",
      "streetAddress": "One Bowerman Dr",
      "latitude": 45.5076448,
      "longitude": -122.8269159,
      "zipCode": "97005"
    },
    "businessContactMethod": "CALL",
    "fetchedAt": "2026-08-02T20:06:56.628Z"
  },
  "instagram-channel-details": {
    "platform": "instagram",
    "url": "https://instagram.com/natgeo",
    "username": "natgeo",
    "displayName": "National Geographic",
    "bio": "Step into wonder and find your inner explorer with National Geographic 🌎",
    "followers": 268924266,
    "following": 194,
    "postCount": 32000,
    "verified": true,
    "profileImage": "https://scontent-lax3-2.cdninstagram.com/v/t51.82787-19/683576066_18653628823019133_9051036240972105113_n.jpg?stp=dst-jpg_s150x150_tt6&_nc_cat=1&ccb=7-5&_nc_sid=f7ccc5&efg=eyJ2ZW5jb2RlX3RhZyI6InByb2ZpbGVfcGljLnd3dy40MDAuQzMifQ%3D%3D&_nc_ohc=T9at3Sd9hNMQ7kNvwHW6BNA&_nc_oc=AdqYT-U_nmEkwIsAAOAVybbiWymNfhdptkU4i18fyBief1CYmoYniQgdmQaUbF338is&_nc_zt=24&_nc_ht=scontent-lax3-2.cdninstagram.com&_nc_gid=vK6lnBdGmpQYun0GLPQkMw&_nc_ss=7d689&oh=00_AQAdMXXEL-J8d2FGFzWtWgqSRdOkYJ2EUNLzCnb4SBTiMw&oe=6A7007EB",
    "externalUrl": "http://visitstore.bio/natgeo"
  },
  "instagram-channel-posts": {
    "url": "https://www.instagram.com/nasa/",
    "totalReturned": 5,
    "posts": [
      {
        "platform": "instagram",
        "url": "https://www.instagram.com/reel/DbYmqpplO_N/",
        "id": "3952078729724096461",
        "postType": "Video",
        "productType": "clips",
        "caption": "The Sun and Moon are coming together to put on a show for Earth, and we'll be sharing it with you. 😎\n\nOn Aug. 12, a total solar eclipse will pass over Earth, and we'll be broadcasting it live along the path of totality. Check our link in bio to learn how to watch along with us!\n\n#NASA #Sun #TotalSolarEclipse2026",
        "description": "The Sun and Moon are coming together to put on a show for Earth, and we'll be sharing it with you. 😎\n\nOn Aug. 12, a total solar eclipse will pass over Earth, and we'll be broadcasting it live along the path of totality. Check our link in bio to learn how to watch along with us!\n\n#NASA #Sun #TotalSolarEclipse2026",
        "publishedAt": "2026-07-29T17:02:45Z",
        "thumbnailUrl": "https://scontent-lga3-3.cdninstagram.com/v/t51.82787-15/760192799_18631809481049152_7782886010573196119_n.jpg?stp=dst-jpg_e15_tt6&_nc_ht=scontent-lga3-3.cdninstagram.com&_nc_cat=104&_nc_oc=Q6cZ2gGam1aPbxqnPf0b0JKP7tArIHvIrXRHft307eWE7UMXS_pr6S4N6-Dm4L-cNp1JOIg&_nc_ohc=NLXhSIvSAE8Q7kNvwG7hHBp&_nc_gid=EJ9eFsuBV8RTUu0BGi0U6A&edm=AOQ1c0wBAAAA&ccb=7-5&oh=00_AQAOYlO_MiU0ymVZP-LUmVyzq1Qfu0qndl3JUXVB6LqVwA&oe=6A6FEEDB&_nc_sid=8b3546",
        "videoUrl": "https://scontent-lga3-1.cdninstagram.com/o1/v/t2/f2/m86/AQOkpXQA9C2FhMuyAbNvepC6OP6PrkitJW3nqH3dhIDVm7lu82BvCIZApUA5L2uZr02DWsYDPOvZUymd3s8Q5RQJ_i1Bkk9Qx3VnTwk.mp4?_nc_cat=111&_nc_sid=5e9851&_nc_ht=scontent-lga3-1.cdninstagram.com&_nc_ohc=DqUQRmuNQ38Q7kNvwEf3m2C&efg=eyJ2ZW5jb2RlX3RhZyI6Inhwdl9wcm9ncmVzc2l2ZS5JTlNUQUdSQU0uQ0xJUFMuQzMuNzIwLmRhc2hfYmFzZWxpbmVfMV92MSIsInhwdl9hc3NldF9pZCI6MTg2MzE4MDkzMTAwNDkxNTIsImFzc2V0X2FnZV9kYXlzIjowLCJ2aV91c2VjYXNlX2lkIjoxMDA5OSwiZHVyYXRpb25fcyI6NDQsInVybGdlbl9zb3VyY2UiOiJ3d3cifQ%3D%3D&ccb=17-1&vs=d63b773f9b2109a6&_nc_vs=HBksFQIYUmlnX3hwdl9yZWVsc19wZXJtYW5lbnRfc3JfcHJvZC9ENjQ4OTVCRTVEN0I2MDc3MzFGQkNDNUI1MjZDN0RCMl92aWRlb19kYXNoaW5pdC5tcDQVAALIARIAFQIYUWlnX3hwdl9wbGFjZW1lbnRfcGVybWFuZW50X3YyLzlBNDA3ODFBQjMyMTkwODU4OTg3RTNFRUYzNUJBMkE4X2F1ZGlvX2Rhc2hpbml0Lm1wNBUCAsgBEgAoABgAGwKIB3VzZV9vaWwBMRJwcm9ncmVzc2l2ZV9yZWNpcGUBMRUAACaAjpb3hOKYQhUCKAJDMywXQEZnztkWhysYEmRhc2hfYmFzZWxpbmVfMV92MREAdf4HZeadAQA&_nc_gid=EJ9eFsuBV8RTUu0BGi0U6A&_nc_ss=7a22e&_nc_zt=28&oh=00_AQDrxCQWJjYdJ_A1wP9NAqwnYMpcGLVAhJP0LpoE3AyyTg&oe=6A6C1F8C",
        "author": {
          "username": "nasa",
          "displayName": "NASA",
          "url": "https://instagram.com/nasa",
          "followers": 104263202,
          "verified": true,
          "profileImage": "https://scontent-lga3-1.cdninstagram.com/v/t51.2885-19/29090066_159271188110124_1152068159029641216_n.jpg?stp=dst-jpg_s320x320_tt6&efg=eyJ2ZW5jb2RlX3RhZyI6InByb2ZpbGVfcGljLmRqYW5nby4xMDgwLmMyIn0&_nc_ht=scontent-lga3-1.cdninstagram.com&_nc_cat=1&_nc_oc=Q6cZ2gGam1aPbxqnPf0b0JKP7tArIHvIrXRHft307eWE7UMXS_pr6S4N6-Dm4L-cNp1JOIg&_nc_ohc=sUQGBsPKUTMQ7kNvwEjppQT&_nc_gid=EJ9eFsuBV8RTUu0BGi0U6A&edm=AOQ1c0wBAAAA&ccb=7-5&oh=00_AQABrOC8fhriT4lnoxQ6_A9newYDo18-mqvkuOv21yGkUQ&oe=6A701229&_nc_sid=8b3546"
        },
        "engagement": {
          "views": 51078,
          "likes": 10645,
          "comments": 149,
          "viewsInstagram": 40862,
          "viewsFacebook": 10216
        },
        "hashtags": [
          "NASA",
          "Sun"
        ],
        "mentions": []
      },
      {
        "platform": "instagram",
        "url": "https://www.instagram.com/p/DbYaLffE2DD/",
        "id": "3952023811948503235",
        "postType": "Sidecar",
        "productType": null,
        "caption": "Suit up!\n\nThese photos show NASA astronaut candidates @astro_fuhrmann and @astro_lawler preparing for their training flights aboard a high-flying WB-57 aircraft. These high-altitude flights train astronaut candidates to operate in tight spaces while wearing a pressure suit—a feat that prepares them for missions to the @ISS, Moon, or beyond.\n\nWhy are pressure suits necessary? The two main bodily dangers of high altitude are extremely thin air and low oxygen. Pressure suits counteract those dangers and make it possible to survive if something goes wrong in the aircraft.\n\nCredit: NASA\n\n#NASA #FlightSuit #Aircraft",
        "description": "Suit up!\n\nThese photos show NASA astronaut candidates @astro_fuhrmann and @astro_lawler preparing for their training flights aboard a high-flying WB-57 aircraft. These high-altitude flights train astronaut candidates to operate in tight spaces while wearing a pressure suit—a feat that prepares them for missions to the @ISS, Moon, or beyond.\n\nWhy are pressure suits necessary? The two main bodily dangers of high altitude are extremely thin air and low oxygen. Pressure suits counteract those dangers and make it possible to survive if something goes wrong in the aircraft.\n\nCredit: NASA\n\n#NASA #FlightSuit #Aircraft",
        "publishedAt": "2026-07-29T15:12:56Z",
        "thumbnailUrl": "https://scontent-lga3-1.cdninstagram.com/v/t51.82787-15/759146473_18631780879049152_2448145103133242635_n.jpg?stp=dst-jpg_e35_s1080x1080_sh2.08_tt6&_nc_ht=scontent-lga3-1.cdninstagram.com&_nc_cat=1&_nc_oc=Q6cZ2gGam1aPbxqnPf0b0JKP7tArIHvIrXRHft307eWE7UMXS_pr6S4N6-Dm4L-cNp1JOIg&_nc_ohc=nvbF_-MRTWYQ7kNvwE_MszZ&_nc_gid=EJ9eFsuBV8RTUu0BGi0U6A&edm=AOQ1c0wBAAAA&ccb=7-5&oh=00_AQBJhJwZzwhl7hvGpLhh1jBk2dWyz3xAd05kIR1XwonMrg&oe=6A701485&_nc_sid=8b3546",
        "author": {
          "username": "nasa",
          "displayName": "NASA",
          "url": "https://instagram.com/nasa",
          "followers": 104263202,
          "verified": true,
          "profileImage": "https://scontent-lga3-1.cdninstagram.com/v/t51.2885-19/29090066_159271188110124_1152068159029641216_n.jpg?stp=dst-jpg_s320x320_tt6&efg=eyJ2ZW5jb2RlX3RhZyI6InByb2ZpbGVfcGljLmRqYW5nby4xMDgwLmMyIn0&_nc_ht=scontent-lga3-1.cdninstagram.com&_nc_cat=1&_nc_oc=Q6cZ2gGam1aPbxqnPf0b0JKP7tArIHvIrXRHft307eWE7UMXS_pr6S4N6-Dm4L-cNp1JOIg&_nc_ohc=sUQGBsPKUTMQ7kNvwEjppQT&_nc_gid=EJ9eFsuBV8RTUu0BGi0U6A&edm=AOQ1c0wBAAAA&ccb=7-5&oh=00_AQABrOC8fhriT4lnoxQ6_A9newYDo18-mqvkuOv21yGkUQ&oe=6A701229&_nc_sid=8b3546"
        },
        "engagement": {
          "likes": 34106,
          "comments": 177,
          "views": null
        },
        "hashtags": [
          "NASA",
          "FlightSuit"
        ],
        "mentions": [
          "astro_fuhrmann",
          "astro_lawler"
        ]
      }
    ],
    "nextCursor": "3947740140450436425_528817151",
    "hasMore": true
  },
  "instagram-channel-reels": {
    "url": "https://www.instagram.com/cristiano/",
    "userId": "173560420",
    "totalReturned": 3,
    "reels": [
      {
        "platform": "instagram",
        "url": "https://www.instagram.com/reel/DabKed0MBRm/",
        "id": "3934784773501752422",
        "postType": "Video",
        "productType": "clips",
        "caption": "Por todos. Por 𝗣𝗢𝗥𝗧𝗨𝗚𝗔𝗟. 🎗️🇵🇹 #VaiDarPortugal \n\nFor everyone. For 𝗣𝗢𝗥𝗧𝗨𝗚𝗔𝗟. 🎗️🇵🇹 #ItsPortugalTime",
        "description": "Por todos. Por 𝗣𝗢𝗥𝗧𝗨𝗚𝗔𝗟. 🎗️🇵🇹 #VaiDarPortugal \n\nFor everyone. For 𝗣𝗢𝗥𝗧𝗨𝗚𝗔𝗟. 🎗️🇵🇹 #ItsPortugalTime",
        "publishedAt": "2026-07-05T20:23:34Z",
        "durationSeconds": 43.4,
        "thumbnailUrl": "https://scontent-ham3-1.cdninstagram.com/v/t51.82787-15/735415699_18606606883054533_8185581534148167588_n.jpg?...",
        "videoUrl": "https://scontent-ham3-1.cdninstagram.com/o1/v/t2/f2/m86/AQOZ-XzJOT5OaiKkSWI8_rvZDNemAlRbnj6HkrsVPoqI0ansFYZltF-y2953cxfuv-jSg-XuNO3kEar8H03wckE8XaOx3OK8T3-4KMM.mp4?...",
        "author": {
          "username": "portugal",
          "displayName": "Portugal",
          "url": "https://instagram.com/portugal",
          "verified": true,
          "profileImage": "https://scontent-ham3-1.cdninstagram.com/v/t51.82787-19/655235091_18574607485054533_3430348023607180141_n.jpg?..."
        },
        "engagement": {
          "views": 130177231,
          "likes": 6373324,
          "comments": 257545,
          "viewsInstagram": 104141785,
          "viewsFacebook": 26035446
        },
        "hashtags": [
          "VaiDarPortugal",
          "ItsPortugalTime"
        ],
        "mentions": []
      },
      {
        "platform": "instagram",
        "url": "https://www.instagram.com/reel/DaU63nnAkoo/",
        "id": "3933027283400542760",
        "postType": "Video",
        "productType": "clips",
        "caption": "Toronto ❤️",
        "description": "Toronto ❤️",
        "publishedAt": "2026-07-03T10:18:59Z",
        "durationSeconds": 46.333,
        "thumbnailUrl": "https://scontent-ham3-1.cdninstagram.com/v/t51.82787-15/731058572_18747860116056421_8724303327878739257_n.jpg?...",
        "videoUrl": "https://scontent-ham3-1.cdninstagram.com/o1/v/t2/f2/m86/AQNreyyq7N-5e2XVjCTkh7BFZ0wKTqOpSD3ZllobCy3C3rRiPuA_64qi66ngwZ-jwgG-66Q57v2G1V3Rvr21y-HGUbMJLY21NY_M8vk.mp4?...",
        "author": {
          "username": "cristiano",
          "displayName": "Cristiano Ronaldo",
          "url": "https://instagram.com/cristiano",
          "verified": true,
          "profileImage": "https://scontent-ham3-1.cdninstagram.com/v/t51.2885-19/472007201_1142000150877579_994350541752907763_n.jpg?...",
          "followers": 676417576
        },
        "engagement": {
          "views": 191553390,
          "likes": 17537560,
          "comments": 341631,
          "viewsInstagram": 153242712,
          "viewsFacebook": 38310678
        },
        "hashtags": [],
        "mentions": []
      }
    ],
    "nextCursor": "3885465807534181465_173560420",
    "hasMore": true
  },
  "instagram-comments": {
    "platform": "instagram",
    "url": "https://www.instagram.com/p/DZFqdAxlkUG/",
    "totalReturned": 10,
    "comments": [
      {
        "id": "17928720258124446",
        "url": "https://www.instagram.com/p/DZFqdAxlkUG/c/17928720258124446",
        "text": "❤️❤️❤️❤️",
        "author": "giulianagrichetta",
        "authorAvatarUrl": "https://scontent-atl3-1.cdninstagram.com/v/t51.82787-19/728156182_18607734223047509_7404583005739996663_n.jpg?stp=dst-jpg_s150x150_tt6&_nc_cat=100&ccb=7-5&_nc_sid=f7ccc5&efg=eyJ2ZW5jb2RlX3RhZyI6InByb2ZpbGVfcGljLnd3dy4xMDgwLkMzIn0%3D&_nc_ohc=cGoAOlkd3_cQ7kNvwH3cesI&_nc_oc=AdoV430X7wZK1hp5x9HI0Hg267Kf8LmyXB11Ej7I4nXePNxGKZduI8DcOoBp0IN0ER4&_nc_zt=24&_nc_ht=scontent-atl3-1.cdninstagram.com&_nc_gid=P5Abwq2UvTMDXokKzG45Jg&_nc_ss=72a8c&oh=00_AQBT4Z-zQV-Z89Kd0BKVNmhs_-iOYakXFRvy-kMFVfLWsA&oe=6A4DA794",
        "authorIsVerified": false,
        "publishedAt": "2026-07-01T07:49:55.000Z"
      },
      {
        "id": "18083281052356825",
        "url": "https://www.instagram.com/p/DZFqdAxlkUG/c/18083281052356825",
        "text": "Hoppers moment",
        "author": "redkidane",
        "authorAvatarUrl": "https://scontent-atl3-3.cdninstagram.com/v/t51.82787-19/686139918_18580722691039268_2096250779414967342_n.jpg?stp=dst-jpg_s150x150_tt6&_nc_cat=111&ccb=7-5&_nc_sid=f7ccc5&efg=eyJ2ZW5jb2RlX3RhZyI6InByb2ZpbGVfcGljLnd3dy4xMDgwLkMzIn0%3D&_nc_ohc=5ruLx7cECMUQ7kNvwEw883n&_nc_oc=Adp-jPSBc0mkti93nI0FR-bBBq_hLclzrrRqC70JO7HsI47RMZeVJF159wD-BivgyvM&_nc_zt=24&_nc_ht=scontent-atl3-3.cdninstagram.com&_nc_gid=P5Abwq2UvTMDXokKzG45Jg&_nc_ss=72a8c&oh=00_AQD-UwNDAfkrNje1f_2dMoh9ax8alu8E-J44od76mYrB5g&oe=6A4DA11B",
        "authorIsVerified": false,
        "publishedAt": "2026-06-24T23:45:01.000Z"
      }
    ]
  },
  "instagram-details": {
    "platform": "instagram",
    "url": "https://www.instagram.com/p/DbYaLffE2DD/",
    "id": "DbYaLffE2DD",
    "postType": "Sidecar",
    "productType": "carousel_container",
    "caption": "Suit up!\n\nThese photos show NASA astronaut candidates @astro_fuhrmann and @astro_lawler preparing for their training flights aboard a high-flying WB-57 aircraft. These high-altitude flights train astronaut candidates to operate in tight spaces while wearing a pressure suit—a feat that prepares them for missions to the @ISS, Moon, or beyond.\n\nWhy are pressure suits necessary? The two main bodily dangers of high altitude are extremely thin air and low oxygen. Pressure suits counteract those dangers and make it possible to survive if something goes wrong in the aircraft.\n\nCredit: NASA\n\n#NASA #FlightSuit #Aircraft",
    "description": "Suit up!\n\nThese photos show NASA astronaut candidates @astro_fuhrmann and @astro_lawler preparing for their training flights aboard a high-flying WB-57 aircraft. These high-altitude flights train astronaut candidates to operate in tight spaces while wearing a pressure suit—a feat that prepares them for missions to the @ISS, Moon, or beyond.\n\nWhy are pressure suits necessary? The two main bodily dangers of high altitude are extremely thin air and low oxygen. Pressure suits counteract those dangers and make it possible to survive if something goes wrong in the aircraft.\n\nCredit: NASA\n\n#NASA #FlightSuit #Aircraft",
    "publishedAt": "2026-07-29T15:12:56Z",
    "durationSeconds": null,
    "thumbnailUrl": "https://scontent-cdg6-1.cdninstagram.com/v/t51.82787-15/759146473_18631780879049152_2448145103133242635_n.jpg?stp=dst-jpg_e35_tt6&_nc_cat=1&ig_cache_key=Mzk1MjAyMzc0MDE1ODgxNjA1Ng%3D%3D.3-ccb7-5&ccb=7-5&_nc_sid=58cdad&efg=eyJ2ZW5jb2RlX3RhZyI6IkNBUk9VU0VMX0lURU0ueHBpZHMuMTQ0MC5zZHIucmVndWxhcl9waG90by5DMyJ9&_nc_ohc=BPWQAJMWpuwQ7kNvwGdQP1J&_nc_oc=AdpoHH53slN9fDJSer4UjuFXtie2IU4sLFlWgiGTWkMWn-EWgJmycNqbEl-vSfl9oio&_nc_ad=z-m&_nc_cid=0&_nc_zt=23&_nc_ht=scontent-cdg6-1.cdninstagram.com&_nc_gid=1yBugmDENcLlZjn1A6HEwA&_nc_ss=7a22e&oh=00_AQBHLNkf4idtmygEvZN9hi2njvz2sW_xF8-tUE-yiJHOBw&oe=6A701485",
    "videoUrl": null,
    "author": {
      "username": "nasa",
      "displayName": "NASA",
      "url": "https://instagram.com/nasa",
      "verified": true,
      "profileImage": "https://scontent-cdg6-1.cdninstagram.com/v/t51.2885-19/29090066_159271188110124_1152068159029641216_n.jpg?stp=dst-jpg_s150x150_tt6&efg=eyJ2ZW5jb2RlX3RhZyI6InByb2ZpbGVfcGljLmRqYW5nby4xMDgwLmMyIn0&_nc_ht=scontent-cdg6-1.cdninstagram.com&_nc_cat=1&_nc_oc=Q6cZ2gG0njRcG3R5cIO9GnRRbYfsbfpvVHqGuePg7pDchBmh38Bj_6EQCeIjnFgc-p5lkTA&_nc_ohc=sUQGBsPKUTMQ7kNvwFOpZpy&_nc_gid=1yBugmDENcLlZjn1A6HEwA&edm=AOmX9WgBAAAA&ccb=7-5&oh=00_AQA7UnNpNR2oyCzn_iZJwhJgHlzakMt5b8t3btT6ne2AUA&oe=6A701229&_nc_sid=bfaa47"
    },
    "engagement": {
      "likes": 34510,
      "comments": 178
    },
    "hashtags": [
      "NASA",
      "FlightSuit"
    ],
    "mentions": [
      "astro_fuhrmann",
      "astro_lawler"
    ]
  },
  "instagram-embed": {
    "platform": "instagram",
    "url": "https://www.instagram.com/p/DZFqdAxlkUG/",
    "type": "post",
    "shortcode": "DZFqdAxlkUG",
    "permalink": "https://www.instagram.com/p/DZFqdAxlkUG/",
    "embedUrl": "https://www.instagram.com/p/DZFqdAxlkUG/embed/captioned/",
    "html": "[HTML omitted in docs — call the API for the full document. Docs examples must not embed raw HTML documents.]"
  },
  "instagram-profile-search": {
    "query": "nike",
    "totalReturned": 1,
    "users": [
      {
        "id": "13460080",
        "username": "nike",
        "displayName": "Nike",
        "url": "https://www.instagram.com/nike/",
        "bio": "Just Do It.",
        "followers": 291623659,
        "following": 264,
        "postCount": 1668,
        "verified": true,
        "isPrivate": false,
        "isBusinessAccount": true,
        "isProfessionalAccount": true,
        "externalUrl": "http://empli.fi/nike",
        "bioLinks": [
          {
            "url": "http://empli.fi/nike",
            "linkType": "external"
          }
        ],
        "profileImage": "https://instagram.fadb3-1.fna.fbcdn.net/v/t51.82787-19/551608484_18567162979020081_1135468084872726555_n.jpg?stp=dst-jpg_s320x320_tt6&efg=eyJ2ZW5jb2RlX3RhZyI6InByb2ZpbGVfcGljLmRqYW5nby4zOTkuYzIifQ&_nc_ht=instagram.fadb3-1.fna.fbcdn.net&_nc_cat=1&_nc_oc=Q6cZ2gE3fm8U-4zquMXb-DCa2XFEqsm-rZ_BWOXzqz5HNEFIKiHcxSpjEdlCVP0v32ZLy3tMLEVo2JvIx8SA4xy09gYm&_nc_ohc=jOWQehR8N0kQ7kNvwHCN0UL&_nc_gid=Ov3EEVEX3-M4dSFajR8eTQ&edm=AOQ1c0wBAAAA&ccb=7-5&oh=00_AQE94ajaP7La8AcjJgA2RbClgYMx9xGFF0qoyUObgazGWg&oe=6A764BBA&_nc_sid=8b3546",
        "profileImageHd": "https://instagram.fadb3-1.fna.fbcdn.net/v/t51.82787-19/551608484_18567162979020081_1135468084872726555_n.jpg?stp=dst-jpg_s320x320_tt6&efg=eyJ2ZW5jb2RlX3RhZyI6InByb2ZpbGVfcGljLmRqYW5nby4zOTkuYzIifQ&_nc_ht=instagram.fadb3-1.fna.fbcdn.net&_nc_cat=1&_nc_oc=Q6cZ2gE3fm8U-4zquMXb-DCa2XFEqsm-rZ_BWOXzqz5HNEFIKiHcxSpjEdlCVP0v32ZLy3tMLEVo2JvIx8SA4xy09gYm&_nc_ohc=jOWQehR8N0kQ7kNvwHCN0UL&_nc_gid=Ov3EEVEX3-M4dSFajR8eTQ&edm=AOQ1c0wBAAAA&ccb=7-5&oh=00_AQE94ajaP7La8AcjJgA2RbClgYMx9xGFF0qoyUObgazGWg&oe=6A764BBA&_nc_sid=8b3546",
        "platform": "instagram",
        "imageExpiresAt": "2026-08-07T21:18:50Z"
      }
    ],
    "mode": "resolve"
  },
  "instagram-reels-by-audio-id": {
    "platform": "instagram",
    "audioId": "27919946310946207",
    "audioUrl": "https://www.instagram.com/reels/audio/27919946310946207/",
    "totalReturned": 5,
    "reels": [
      {
        "platform": "instagram",
        "url": "https://www.instagram.com/reel/DaSip_jgfgL/",
        "id": "DaSip_jgfgL",
        "caption": "A moment of awe. While searching for the Seven Natural Wonders of America, @debrobertsabc and National Geographic Explorer James Edward Mills (@thejoytripproject) captured this beautiful view. Can you guess where they are? \n\nDiscover more beauty and nature in the final Wonders of America list, revealed during the 24-hour “Disney Celebrates America” live event special on July 4th on ABC, Disney+ and Nat Geo.",
        "description": "A moment of awe. While searching for the Seven Natural Wonders of America, @debrobertsabc and National Geographic Explorer James Edward Mills (@thejoytripproject) captured this beautiful view. Can you guess where they are? \n\nDiscover more beauty and nature in the final Wonders of America list, revealed during the 24-hour “Disney Celebrates America” live event special on July 4th on ABC, Disney+ and Nat Geo.",
        "publishedAt": "2026-07-02T12:00:36.000Z",
        "durationSeconds": 11.766,
        "videoUrl": "https://instagram.fccs3-2.fna.fbcdn.net/o1/v/t2/f2/m86/AQNm7Q5NYwBbSA4Vve0iRre5MLeKDljn9vqPN8i0TZf3FeZZPqrhcercZFtrix4mhl9VzcRx5LCOVhf4ogU2MyOH_nTUdLv7h_iUeT4.mp4?_nc_cat=100&_nc_oc=AdrE6ndC2PBc_gMsOZ_Kgtjkaf5_KFDuoJDmITmMw3mj3yjHFlQAr3pBvdR0JIvug6w&_nc_sid=5e9851&_nc_ht=instagram.fccs3-2.fna.fbcdn.net&_nc_ohc=3xFFvqXL_HYQ7kNvwFxSo5C&efg=eyJ2ZW5jb2RlX3RhZyI6Inhwdl9wcm9ncmVzc2l2ZS5JTlNUQUdSQU0uQ0xJUFMuQzMuNzIwLmRhc2hfYmFzZWxpbmVfMV92MSIsInhwdl9hc3NldF9pZCI6MTg2NzI0ODIzNjgwMTkxMzMsImFzc2V0X2FnZV9kYXlzIjoxNSwidmlfdXNlY2FzZV9pZCI6MTAwOTksImR1cmF0aW9uX3MiOjExLCJ1cmxnZW5fc291cmNlIjoid3d3In0%3D&ccb=17-1&vs=a3ed5364566742cd&_nc_vs=HBksFQIYUmlnX3hwdl9yZWVsc19wZXJtYW5lbnRfc3JfcHJvZC84NzQ3RjZBOUFBOUUwQTVFQjY1OUY0RUMwQTVBMjZBM192aWRlb19kYXNoaW5pdC5tcDQVAALIARIAFQIYUWlnX3hwdl9wbGFjZW1lbnRfcGVybWFuZW50X3YyLzYyNDQ4QjdCMTVDNEVBN0U1OTkzODZFNTAyNUNCQkJEX2F1ZGlvX2Rhc2hpbml0Lm1wNBUCAsgBEgAoABgAGwKIB3VzZV9vaWwBMRJwcm9ncmVzc2l2ZV9yZWNpcGUBMRUAACb66vbpwqGrQhUCKAJDMywXQCeIMSbpeNUYEmRhc2hfYmFzZWxpbmVfMV92MREAdf4HZeadAQA&_nc_gid=8zKuWtFwGFSgOstkWmOtlg&_nc_ss=73a8c&_nc_zt=28&oh=00_AQBHLias4bmd0eI1kNYdgi5WshPQ-x5kmeaqvPxjynzSJA&oe=6A5D5355",
        "author": {
          "username": "natgeo",
          "displayName": "National Geographic",
          "url": "https://instagram.com/natgeo",
          "verified": true,
          "profileImage": "https://instagram.fccs3-1.fna.fbcdn.net/v/t51.82787-19/683576066_18653628823019133_9051036240972105113_n.jpg?stp=dst-jpg_s150x150_tt6&efg=eyJ2ZW5jb2RlX3RhZyI6InByb2ZpbGVfcGljLmRqYW5nby40MDAuYzIifQ&_nc_ht=instagram.fccs3-1.fna.fbcdn.net&_nc_cat=1&_nc_oc=Q6cZ2gF-gGYZ-MfzxJDTWdOZNJF07VOZpW47oCWJ_Xr7sVXDZR_2BFehBTIvujAdT7UYoMY&_nc_ohc=hTIYH2ypurAQ7kNvwGMMafs&_nc_gid=8zKuWtFwGFSgOstkWmOtlg&edm=APs17CUBAAAA&ccb=7-5&oh=00_AQDK3uG63OUxWOZVATEg7XlkiG4K8NyYpYrD_jfuEb-XFA&oe=6A614F2B&_nc_sid=10d13b"
        },
        "engagement": {
          "views": 3459891,
          "likes": 108662,
          "comments": 914
        },
        "musicId": "27919946310946207",
        "musicUrl": "https://www.instagram.com/reels/audio/27919946310946207/",
        "hasAudio": true,
        "music": {
          "id": "27919946310946207",
          "clusterId": "27919946310946207",
          "assetId": "audio_asset_example",
          "canonicalId": "18455463055100927",
          "artistId": "42",
          "title": "Freakin Out",
          "artist": "Dexter and The Moonrocks",
          "durationMs": 217897,
          "audioType": "licensed_music",
          "coverUrl": "https://cdn.example/cover.jpg",
          "isTrendingInClips": true,
          "trendRank": 3,
          "previousTrendRank": 7,
          "isExplicit": false,
          "hasLyrics": true
        },
        "isPaidPartnership": false
      },
      {
        "platform": "instagram",
        "url": "https://www.instagram.com/reel/DaSnBHzRC3m/",
        "id": "DaSnBHzRC3m",
        "caption": "He was found hiding out at a distant relative’s home thousands of miles away after a nearly month-long manhunt.",
        "description": "He was found hiding out at a distant relative’s home thousands of miles away after a nearly month-long manhunt.",
        "publishedAt": "2026-07-02T12:38:33.000Z",
        "durationSeconds": 5.038,
        "videoUrl": "https://instagram.fccs3-1.fna.fbcdn.net/o1/v/t2/f2/m86/AQPPRD5xHKMhcZmNIBLjysrEj-XZEOrhPQKJfM8hmUpf8e4OnkqVc5ZKIdk2qIq2luFMxbcMIEWHyeF3_yXkGTGOhbUDCd6xB17lmXg.mp4?_nc_cat=103&_nc_oc=AdprS4uJLqkxTiTQrg0MfEeYGlrKQmygIkUuIWxhRyG8SeZcnd9dBTjSOc1Goii2v0M&_nc_sid=5e9851&_nc_ht=instagram.fccs3-1.fna.fbcdn.net&_nc_ohc=-N6R5M1VoCAQ7kNvwGw8o0a&efg=eyJ2ZW5jb2RlX3RhZyI6Inhwdl9wcm9ncmVzc2l2ZS5JTlNUQUdSQU0uQ0xJUFMuQzMuNzIwLmRhc2hfYmFzZWxpbmVfMV92MSIsInhwdl9hc3NldF9pZCI6OTg0OTc0MjkxMTA5NzQwLCJhc3NldF9hZ2VfZGF5cyI6MTUsInZpX3VzZWNhc2VfaWQiOjEwMDk5LCJkdXJhdGlvbl9zIjo1LCJ1cmxnZW5fc291cmNlIjoid3d3In0%3D&ccb=17-1&vs=fee147904b1a37e8&_nc_vs=HBksFQIYUmlnX3hwdl9yZWVsc19wZXJtYW5lbnRfc3JfcHJvZC9DNDQxM0FCRjA4MkI1MkFGMjUyRkZGRDEyNzI4RDc5N192aWRlb19kYXNoaW5pdC5tcDQVAALIARIAFQIYUWlnX3hwdl9wbGFjZW1lbnRfcGVybWFuZW50X3YyLzM3NDE4N0YzODA1QjVEMUNFMERDNjM2RUQ1NkY2RkE1X2F1ZGlvX2Rhc2hpbml0Lm1wNBUCAsgBEgAoABgAGwKIB3VzZV9vaWwBMRJwcm9ncmVzc2l2ZV9yZWNpcGUBMRUAACbYneCrhvW_AxUCKAJDMywXQBQhysCDEm8YEmRhc2hfYmFzZWxpbmVfMV92MREAdf4HZeadAQA&_nc_gid=8zKuWtFwGFSgOstkWmOtlg&_nc_ss=73a8c&_nc_zt=28&oh=00_AQBekUjDG1x8uPwg1xKbymxRs0rWVytjYopoHHHIGogd9g&oe=6A5D3648",
        "author": {
          "username": "buna0214world",
          "displayName": "Buna's_World",
          "url": "https://instagram.com/buna0214world",
          "verified": false,
          "profileImage": "https://instagram.fccs3-2.fna.fbcdn.net/v/t51.82787-19/730331656_18187041916348619_1189543852469599393_n.jpg?stp=dst-jpg_s150x150_tt6&efg=eyJ2ZW5jb2RlX3RhZyI6InByb2ZpbGVfcGljLmRqYW5nby4xMDgwLmMyIn0&_nc_ht=instagram.fccs3-2.fna.fbcdn.net&_nc_cat=111&_nc_oc=Q6cZ2gF-gGYZ-MfzxJDTWdOZNJF07VOZpW47oCWJ_Xr7sVXDZR_2BFehBTIvujAdT7UYoMY&_nc_ohc=bpkyefW5i5cQ7kNvwHcdOrA&_nc_gid=8zKuWtFwGFSgOstkWmOtlg&edm=APs17CUBAAAA&ccb=7-5&oh=00_AQC4hfnlAtaAtaBfVru_e2cHO6b05jxfxNeWNoy5uhxUwQ&oe=6A6151E9&_nc_sid=10d13b"
        },
        "engagement": {
          "views": 329,
          "likes": 3,
          "comments": 0
        },
        "musicId": "27919946310946207",
        "musicUrl": "https://www.instagram.com/reels/audio/27919946310946207/",
        "hasAudio": true,
        "music": {
          "id": "27919946310946207",
          "clusterId": "27919946310946207",
          "assetId": "audio_asset_example",
          "canonicalId": "18455463055100927",
          "artistId": "42",
          "title": "Freakin Out",
          "artist": "Dexter and The Moonrocks",
          "durationMs": 217897,
          "audioType": "licensed_music",
          "coverUrl": "https://cdn.example/cover.jpg",
          "isTrendingInClips": true,
          "trendRank": 3,
          "previousTrendRank": 7,
          "isExplicit": false,
          "hasLyrics": true
        },
        "isPaidPartnership": false
      }
    ],
    "isTrendingInClips": true,
    "trendRank": 3,
    "previousTrendRank": 7,
    "music": {
      "id": "27919946310946207",
      "clusterId": "27919946310946207",
      "assetId": "audio_asset_example",
      "canonicalId": "18455463055100927",
      "artistId": "42",
      "title": "Freakin Out",
      "artist": "Dexter and The Moonrocks",
      "durationMs": 217897,
      "audioType": "licensed_music",
      "coverUrl": "https://cdn.example/cover.jpg",
      "isTrendingInClips": true,
      "trendRank": 3,
      "previousTrendRank": 7,
      "isExplicit": false,
      "hasLyrics": true
    }
  },
  "instagram-reels-search": {
    "query": "travel",
    "totalReturned": 3,
    "results": [
      {
        "platform": "instagram",
        "url": "https://www.instagram.com/p/DayDvvttHtI/",
        "id": "3941229099090213704",
        "postType": "Video",
        "productType": "clips",
        "caption": "🌊 Kıbrıs’ın en yeni aquaparkını keşfettim! 😍\nKaydıraklar, çocuk alanı ve yazın serinlemek için tam bir kaçış noktası. 💦☀️\n\nAquaparkın giriş ücreti, konumu için yoruma \"BİLGİ\" yazman yeterli! 📩💦\n\n📍 Kıbrıs’taki en güzel mekanlar ve keşifler için takip etmeyi unutma. \n\n#reels #viral #fyp #travel #travelreels",
        "description": "🌊 Kıbrıs’ın en yeni aquaparkını keşfettim! 😍\nKaydıraklar, çocuk alanı ve yazın serinlemek için tam bir kaçış noktası. 💦☀️\n\nAquaparkın giriş ücreti, konumu için yoruma \"BİLGİ\" yazman yeterli! 📩💦\n\n📍 Kıbrıs’taki en güzel mekanlar ve keşifler için takip etmeyi unutma. \n\n#reels #viral #fyp #travel #travelreels",
        "publishedAt": "2026-07-14T17:47:27.000Z",
        "durationSeconds": 12.333,
        "thumbnailUrl": "https://scontent-cph2-1.cdninstagram.com/v/t51.82787-15/746421066_18088964012323578_1371556212593119396_n.jpg?...",
        "videoUrl": "https://scontent-cph2-1.cdninstagram.com/o1/v/t2/f2/m86/AQPRKXt1G6vrSNMtCD3y4roRhkZUU-SMO5R75U3-eAFEbtFGU6IzDJptEbfwWLTINTa9ZX5y-KO_OvBo4mp57r_n0PDYo7Wj368K6KU.mp4?...",
        "author": {
          "username": "bencekibris",
          "displayName": "Melisa Yıldırım",
          "url": "https://instagram.com/bencekibris"
        },
        "engagement": {
          "views": 37937,
          "likes": 297,
          "comments": 641,
          "viewsInstagram": 30350,
          "viewsFacebook": 7587
        },
        "hashtags": [
          "reels",
          "viral"
        ],
        "mentions": [],
        "isPaidPartnership": false,
        "isAd": false,
        "isAffiliate": false
      },
      {
        "platform": "instagram",
        "url": "https://www.instagram.com/p/DazJr5PBcC3/",
        "id": "3941536697690734775",
        "postType": "Video",
        "productType": "clips",
        "caption": "It’s officially Hot summer night in mid July just like miss #lanadelray said #hotsummernights #midjuly #travel",
        "description": "It’s officially Hot summer night in mid July just like miss #lanadelray said #hotsummernights #midjuly #travel",
        "publishedAt": "2026-07-15T03:58:01.000Z",
        "durationSeconds": 16.972,
        "thumbnailUrl": "https://scontent-cph2-1.cdninstagram.com/v/t51.82787-15/746042012_18609462409002256_3222197168337217329_n.jpg?...",
        "videoUrl": "https://scontent-cph2-1.cdninstagram.com/o1/v/t2/f2/m86/AQNjviBRPVEuheQRRrMOf2adQ6sKXUyWQeRvrbuKRr3QVWU2sUiizNhM7M5gYgXUSNGk-cDMur_ViWKTYaYps7oQxcxCqohZg4xAuzw.mp4?...",
        "author": {
          "username": "rammyun",
          "displayName": "⠀⠀⠀✨Ram | 람 Lam 🌎",
          "url": "https://instagram.com/rammyun"
        },
        "engagement": {
          "views": 5572,
          "likes": 378,
          "comments": 12,
          "viewsInstagram": 4458,
          "viewsFacebook": 1114
        },
        "hashtags": [
          "lanadelray",
          "hotsummernights"
        ],
        "mentions": [],
        "isPaidPartnership": false,
        "isAd": false,
        "isAffiliate": false
      }
    ]
  },
  "instagram-summarizer": {
    "platform": "instagram",
    "url": "https://www.instagram.com/garyvee/reel/DMpuiXeubFY/",
    "summary": "The speaker emphasizes the importance of self-worth and the belief that everyone has the potential to become significant. They encourage listeners to recognize their own value and to fight for their happiness, suggesting that negative influences from others can diminish one's self-esteem. By surrounding oneself with positivity and cutting out pessimistic influences, individuals can foster a more optimistic outlook on life. The message is ultimately one of empowerment, urging people to acknowledge their worth and strive for personal fulfillment.",
    "keyPoints": [
      "Everyone has the potential to be significant and should recognize their own value.",
      "Negative voices from others can impact self-esteem; it's important to challenge them.",
      "Fighting for happiness is essential and requires active effort.",
      "Surrounding oneself with positivity can lead to a more optimistic mindset.",
      "Cynicism and overanalysis can negatively affect mental well-being.",
      "Being a good person and genuinely trying is commendable and valuable."
    ],
    "topics": [
      "self-worth",
      "happiness",
      "positivity",
      "optimism",
      "mental health",
      "empowerment"
    ],
    "sentiment": "positive"
  },
  "instagram-tagged-posts": {
    "url": "https://www.instagram.com/nasa/",
    "totalReturned": 3,
    "hasMore": true,
    "nextCursor": "3600123456789012345_528817151",
    "posts": [
      {
        "platform": "instagram",
        "url": "https://www.instagram.com/p/DexampleNasa1/",
        "id": "3600987654321098765",
        "shortcode": "DexampleNasa1",
        "postType": "Image",
        "productType": "feed",
        "caption": "Stunning view from orbit ? thanks @nasa for the inspiration #space #nasa",
        "description": "Stunning view from orbit ? thanks @nasa for the inspiration #space #nasa",
        "publishedAt": "2026-03-31T14:22:10.000Z",
        "thumbnailUrl": "https://scontent.cdninstagram.com/v/t51.29350-15/example_nasa_tagged_1.jpg",
        "author": {
          "id": "1234567890",
          "username": "spacefan.example",
          "displayName": "Space Fan",
          "url": "https://instagram.com/spacefan.example",
          "verified": false
        },
        "engagement": {
          "likes": 18420,
          "comments": 312
        },
        "hashtags": [
          "space",
          "nasa"
        ],
        "mentions": [
          "nasa"
        ]
      },
      {
        "platform": "instagram",
        "url": "https://www.instagram.com/reel/DexampleNasa2/",
        "id": "3599876543210987654",
        "shortcode": "DexampleNasa2",
        "postType": "Video",
        "productType": "clips",
        "caption": "Launch vibes with @nasa #reels",
        "description": "Launch vibes with @nasa #reels",
        "publishedAt": "2025-08-04T09:10:00.000Z",
        "thumbnailUrl": "https://scontent.cdninstagram.com/v/t51.29350-15/example_nasa_tagged_2.jpg",
        "author": {
          "id": "2345678901",
          "username": "rockets.example",
          "displayName": "Rocket Clips",
          "url": "https://instagram.com/rockets.example"
        },
        "engagement": {
          "views": 240150,
          "likes": 9210,
          "comments": 188
        },
        "hashtags": [
          "reels"
        ],
        "mentions": [
          "nasa"
        ]
      }
    ]
  },
  "instagram-transcript": {
    "platform": "instagram",
    "url": "https://www.instagram.com/p/DZFsjH9E3gK/",
    "transcript": "Can you guess where we are? We're about to unveil the seven natural wonders of America. Look how close we are. This is amazing. From a geologist standpoint, globally, this is geology and action that is all-inspiring. The touch is something very human. There are myths, there are legends, there are important stories that hold a sacred dish if you will. It's absolutely beautiful. And you just see how lush the vegetation is. There's such a diverse ecosystem. It's incredible. We're having so much fun about to unveil the seven natural wonders of America, just in time for the Fourth of July. Absolutely. You'll see this on ABC National Geographic in NatGeo.com. So guess where we are, comment and let us know what you think and we'll see you on Independence Day. And keep exploring.",
    "transcriptSegments": [
      {
        "text": "Can you guess where we are? We're about to unveil the seven natural wonders of America.",
        "start": 0,
        "duration": 4.64,
        "end": 4.64,
        "timestamp": "00:00"
      },
      {
        "text": "Look how close we are. This is amazing. From a geologist standpoint,",
        "start": 5.92,
        "duration": 4.72,
        "end": 10.64,
        "timestamp": "00:05"
      },
      {
        "text": "globally, this is geology and action that is all-inspiring. The touch is something very human.",
        "start": 10.64,
        "duration": 5.04,
        "end": 15.68,
        "timestamp": "00:10"
      },
      {
        "text": "There are myths, there are legends, there are important stories that hold a sacred",
        "start": 16.24,
        "duration": 5.36,
        "end": 21.6,
        "timestamp": "00:16"
      },
      {
        "text": "dish if you will. It's absolutely beautiful. And you just see how lush the vegetation is. There's",
        "start": 21.6,
        "duration": 4.24,
        "end": 25.84,
        "timestamp": "00:21"
      },
      {
        "text": "such a diverse ecosystem. It's incredible. We're having so much fun about to unveil the seven",
        "start": 25.84,
        "duration": 7.28,
        "end": 33.12,
        "timestamp": "00:25"
      },
      {
        "text": "natural wonders of America, just in time for the Fourth of July. Absolutely. You'll see this on",
        "start": 33.12,
        "duration": 4.56,
        "end": 37.68,
        "timestamp": "00:33"
      },
      {
        "text": "ABC National Geographic in NatGeo.com. So guess where we are, comment and let us know what you think",
        "start": 37.68,
        "duration": 5.76,
        "end": 43.44,
        "timestamp": "00:37"
      }
    ],
    "wordCount": 135,
    "segments": 9,
    "language": "en"
  },
  "instagram-trending-reels": {
    "platform": "instagram",
    "country": "United States",
    "totalReturned": 2,
    "reels": [
      {
        "platform": "instagram",
        "url": "https://www.instagram.com/reel/DbYmqpplO_N/",
        "id": "3952078729724096461",
        "shortcode": "DbYmqpplO_N",
        "postType": "Video",
        "productType": "clips",
        "section": null,
        "topic": null,
        "caption": "The Sun and Moon are coming together to put on a show for Earth, and we'll be sharing it with you. 😎\n\nOn Aug. 12, a total solar eclipse will pass over Earth, and we'll be broadcasting it live along the path of totality. Check our link in bio to learn how to watch along with us!\n\n#NASA #Sun #TotalSolarEclipse2026",
        "description": "The Sun and Moon are coming together to put on a show for Earth, and we'll be sharing it with you. 😎\n\nOn Aug. 12, a total solar eclipse will pass over Earth, and we'll be broadcasting it live along the path of totality. Check our link in bio to learn how to watch along with us!\n\n#NASA #Sun #TotalSolarEclipse2026",
        "publishedAt": "2026-07-29T17:02:45Z",
        "durationSeconds": null,
        "thumbnailUrl": "https://scontent-lga3-3.cdninstagram.com/v/t51.82787-15/760192799_18631809481049152_7782886010573196119_n.jpg?stp=dst-jpg_e15_tt6&_nc_ht=scontent-lga3-3.cdninstagram.com&_nc_cat=104&_nc_oc=Q6cZ2gGam1aPbxqnPf0b0JKP7tArIHvIrXRHft307eWE7UMXS_pr6S4N6-Dm4L-cNp1JOIg&_nc_ohc=NLXhSIvSAE8Q7kNvwG7hHBp&_nc_gid=EJ9eFsuBV8RTUu0BGi0U6A&edm=AOQ1c0wBAAAA&ccb=7-5&oh=00_AQAOYlO_MiU0ymVZP-LUmVyzq1Qfu0qndl3JUXVB6LqVwA&oe=6A6FEEDB&_nc_sid=8b3546",
        "videoUrl": "https://scontent-lga3-1.cdninstagram.com/o1/v/t2/f2/m86/AQOkpXQA9C2FhMuyAbNvepC6OP6PrkitJW3nqH3dhIDVm7lu82BvCIZApUA5L2uZr02DWsYDPOvZUymd3s8Q5RQJ_i1Bkk9Qx3VnTwk.mp4?_nc_cat=111&_nc_sid=5e9851&_nc_ht=scontent-lga3-1.cdninstagram.com&_nc_ohc=DqUQRmuNQ38Q7kNvwEf3m2C&efg=eyJ2ZW5jb2RlX3RhZyI6Inhwdl9wcm9ncmVzc2l2ZS5JTlNUQUdSQU0uQ0xJUFMuQzMuNzIwLmRhc2hfYmFzZWxpbmVfMV92MSIsInhwdl9hc3NldF9pZCI6MTg2MzE4MDkzMTAwNDkxNTIsImFzc2V0X2FnZV9kYXlzIjowLCJ2aV91c2VjYXNlX2lkIjoxMDA5OSwiZHVyYXRpb25fcyI6NDQsInVybGdlbl9zb3VyY2UiOiJ3d3cifQ%3D%3D&ccb=17-1&vs=d63b773f9b2109a6&_nc_vs=HBksFQIYUmlnX3hwdl9yZWVsc19wZXJtYW5lbnRfc3JfcHJvZC9ENjQ4OTVCRTVEN0I2MDc3MzFGQkNDNUI1MjZDN0RCMl92aWRlb19kYXNoaW5pdC5tcDQVAALIARIAFQIYUWlnX3hwdl9wbGFjZW1lbnRfcGVybWFuZW50X3YyLzlBNDA3ODFBQjMyMTkwODU4OTg3RTNFRUYzNUJBMkE4X2F1ZGlvX2Rhc2hpbml0Lm1wNBUCAsgBEgAoABgAGwKIB3VzZV9vaWwBMRJwcm9ncmVzc2l2ZV9yZWNpcGUBMRUAACaAjpb3hOKYQhUCKAJDMywXQEZnztkWhysYEmRhc2hfYmFzZWxpbmVfMV92MREAdf4HZeadAQA&_nc_gid=EJ9eFsuBV8RTUu0BGi0U6A&_nc_ss=7a22e&_nc_zt=28&oh=00_AQDrxCQWJjYdJ_A1wP9NAqwnYMpcGLVAhJP0LpoE3AyyTg&oe=6A6C1F8C",
        "author": {
          "username": "nasa",
          "url": "https://instagram.com/nasa"
        },
        "engagement": {
          "views": 51078,
          "likes": 10645,
          "comments": 149,
          "viewsInstagram": 40862,
          "viewsFacebook": 10216
        },
        "hashtags": [
          "NASA",
          "Sun"
        ],
        "mentions": []
      },
      {
        "platform": "instagram",
        "url": "https://www.instagram.com/reel/DbL6n0ggXDZ/",
        "id": "3948507321457537241",
        "shortcode": "DbL6n0ggXDZ",
        "postType": "Video",
        "productType": "clips",
        "section": null,
        "topic": null,
        "caption": "Sound on!\n\nSonifications take images from across the universe and turn them into music, with different notes corresponding to different frequencies of light.\n\nThis sonification of NGC 4736, a bright spiral galaxy found 16 million light-years from Earth, sweeps clockwise around the image. As it reaches neutron stars and black holes (spotted by our @nasachandraxray telescope), it turns them into pitched tones on a glass marimba. Other sources of light are represented by piano notes or a low, ethereal drone.\n\n#NASA #Space #MusicLife",
        "description": "Sound on!\n\nSonifications take images from across the universe and turn them into music, with different notes corresponding to different frequencies of light.\n\nThis sonification of NGC 4736, a bright spiral galaxy found 16 million light-years from Earth, sweeps clockwise around the image. As it reaches neutron stars and black holes (spotted by our @nasachandraxray telescope), it turns them into pitched tones on a glass marimba. Other sources of light are represented by piano notes or a low, ethereal drone.\n\n#NASA #Space #MusicLife",
        "publishedAt": "2026-07-24T18:46:42Z",
        "durationSeconds": null,
        "thumbnailUrl": "https://scontent-lga3-1.cdninstagram.com/v/t51.82787-15/753557824_18630272896049152_5085604310932259746_n.jpg?stp=dst-jpg_e15_fr_s1080x1080_tt6&_nc_ht=scontent-lga3-1.cdninstagram.com&_nc_cat=1&_nc_oc=Q6cZ2gGam1aPbxqnPf0b0JKP7tArIHvIrXRHft307eWE7UMXS_pr6S4N6-Dm4L-cNp1JOIg&_nc_ohc=JXie426E2AIQ7kNvwGlg-Up&_nc_gid=EJ9eFsuBV8RTUu0BGi0U6A&edm=AOQ1c0wBAAAA&ccb=7-5&oh=00_AQDfQIt5ChHfvw1haYF6Huy5Tm0DHMMWjvyPqrGpi7_tTA&oe=6A7021E6&_nc_sid=8b3546",
        "videoUrl": "https://scontent-lga3-1.cdninstagram.com/o1/v/t2/f2/m86/AQPmdAz9D4QKeO_RBry8I2ja9L4hPZ0xY85OXT_W30_E9E5cOr_RoiOcZHVX6a9Fvjg8qStE7fTYF0T9sgmzJyxUs6ay7J6Bvu0fLb4.mp4?_nc_cat=109&_nc_sid=5e9851&_nc_ht=scontent-lga3-1.cdninstagram.com&_nc_ohc=9d9-4rCXivsQ7kNvwFJggA4&efg=eyJ2ZW5jb2RlX3RhZyI6Inhwdl9wcm9ncmVzc2l2ZS5JTlNUQUdSQU0uQ0xJUFMuQzMuNzIwLmRhc2hfYmFzZWxpbmVfMV92MSIsInhwdl9hc3NldF9pZCI6MTg2MzAyNzI3NzAwNDkxNTIsImFzc2V0X2FnZV9kYXlzIjo0LCJ2aV91c2VjYXNlX2lkIjoxMDA5OSwiZHVyYXRpb25fcyI6MzQsInVybGdlbl9zb3VyY2UiOiJ3d3cifQ%3D%3D&ccb=17-1&vs=53b7030fc1cf7a2a&_nc_vs=HBksFQIYUmlnX3hwdl9yZWVsc19wZXJtYW5lbnRfc3JfcHJvZC9CODQ0NkUzMkVERDMxMDM4NjFFNDk1OTc4NjM0NzFCQl92aWRlb19kYXNoaW5pdC5tcDQVAALIARIAFQIYUWlnX3hwdl9wbGFjZW1lbnRfcGVybWFuZW50X3YyL0JCNEUzREJGMERFRTc3RDY4Nzc5QzA5QzRFQUVCNzkxX2F1ZGlvX2Rhc2hpbml0Lm1wNBUCAsgBEgAoABgAGwKIB3VzZV9vaWwBMRJwcm9ncmVzc2l2ZV9yZWNpcGUBMRUAACaAkrjozIiYQhUCKAJDMywXQEEAAAAAAAAYEmRhc2hfYmFzZWxpbmVfMV92MREAdf4HZeadAQA&_nc_gid=EJ9eFsuBV8RTUu0BGi0U6A&_nc_ss=7a22e&_nc_zt=28&oh=00_AQBlTouRSWFhKYJdRHR9XtTa3aGhEHVVC578ay32Lrz7mQ&oe=6A6C2F2A",
        "author": {
          "username": "nasa",
          "url": "https://instagram.com/nasa"
        },
        "engagement": {
          "views": null,
          "likes": 485567,
          "comments": 2174,
          "viewsInstagram": null,
          "viewsFacebook": null
        },
        "hashtags": [
          "NASA",
          "Space"
        ],
        "mentions": [
          "nasachandraxray"
        ]
      }
    ],
    "note": "Snapshot-backed trending list (typical freshness under 24h). Instagram returns a small overlapping batch per scrape; duplicates across requests are expected. For live keyword search use /v1/instagram/reels-search.",
    "cached": true,
    "cachedAt": "2026-07-29T18:00:00Z",
    "stale": true,
    "ageHours": 32.0
  },
  "kick-clip": {
    "channelUrl": "https://kick.com/xqc",
    "clip": {
      "platform": "kick",
      "id": "clip_01KZ0X5PGT228PY3QEB3RMR3YC",
      "url": "https://kick.com/xqc/clips/clip_01KZ0X5PGT228PY3QEB3RMR3YC",
      "title": "Vegas farming sadges",
      "createdAt": "2026-08-02T09:36:01.061092Z",
      "startedAt": "2026-08-02T05:45:57Z",
      "durationSeconds": 38,
      "views": 18,
      "likes": 0,
      "thumbnailUrl": "https://clips.kick.com/clips/fb/clip_01KZ0X5PGT228PY3QEB3RMR3YC/thumbnail.webp",
      "videoUrl": "https://clips.kick.com/clips/fb/clip_01KZ0X5PGT228PY3QEB3RMR3YC/playlist.m3u8",
      "privacy": "public",
      "isMature": false,
      "livestreamId": "120226226",
      "vodStartsAt": 29450,
      "vod": {
        "id": "8faf0a05-dcdf-4ab1-8538-e87c6eef573e"
      },
      "category": "Just Chatting",
      "categoryId": "15",
      "categorySlug": "just-chatting",
      "parentCategory": "irl",
      "categoryBanner": "https://files.kick.com/images/subcategories/15/banner/b697a8a3-62db-4779-aa76-e4e47662af97",
      "channel": {
        "id": "668",
        "username": "xqc",
        "name": "xQc",
        "url": "https://kick.com/xqc",
        "profilePicture": "https://files.kick.com/images/user/676/profile_image/conversion/931b4e8f-5445-427c-bd82-b473530390cc-thumb.webp"
      },
      "creator": {
        "id": "7458058",
        "username": "ghosteld",
        "name": "Ghosteld",
        "url": "https://kick.com/ghosteld",
        "profilePicture": "https://files.kick.com/images/user/7458058/profile_image/conversion/d0bd5606-ab8a-42f7-b535-6f7c4a672c34-thumb.webp"
      }
    }
  },
  "komi-page": {
    "platform": "komi",
    "id": "64d82830-59aa-4488-bfb0-93426971d139",
    "url": "https://komi.io/kimkardashian",
    "username": "kimkardashian",
    "handle": "kimkardashian",
    "displayName": "Kim Kardashian",
    "name": "Kim Kardashian",
    "firstName": "Kim",
    "lastName": "Kardashian",
    "avatar": "https://komi-production-assets.s3.amazonaws.com/photos/4Nd69ODJHs61_iNYPlqos.jpg",
    "linkCount": 22,
    "socials": {
      "instagram": "https://www.instagram.com/kimkardashian/",
      "tiktok": "https://www.tiktok.com/@kimkardashian",
      "youtube": "https://www.youtube.com/@KUWTK",
      "twitter": "https://twitter.com/KimKardashian",
      "facebook": "https://www.facebook.com/KimKardashian",
      "snapchat": "https://www.snapchat.com/add/kimkardashian?locale=en-GB"
    },
    "bio": "",
    "description": "",
    "links": [
      {
        "id": "6d7086df-ede4-4f8a-85e5-0fa410e60bc2",
        "url": "https://skims.social/shop-skims",
        "title": "Visit SKIMS",
        "type": "LINK",
        "order": 0,
        "visible": true,
        "thumbnail": "https://komi-production-assets.s3-accelerate.amazonaws.com/photos/x_LQCBYzoWiel0-yrAnrF.jpg",
        "moduleId": "e6ce39d2-e3df-4040-a5cc-ce016cacbc34",
        "versionId": "944094bf-f124-4b13-866a-3498c492736d"
      },
      {
        "id": "f43e198b-2fd5-45f4-80d1-389906c5c840",
        "url": "https://skims.com/products/signature-swim-triangle-bikini-top-dune-crocodile-print",
        "title": "TRIANGLE BIKINI TOP | DUNE CROCODILE",
        "type": "PRODUCT",
        "order": 0,
        "visible": false,
        "thumbnail": "https://komi-production-assets.s3-accelerate.amazonaws.com/photos/dzDiYZjZFXPE4E8-ZwnSn.png",
        "moduleId": "5c8bc46c-2d6b-4731-baf3-2f40aec1465c",
        "versionId": "944094bf-f124-4b13-866a-3498c492736d",
        "price": 44,
        "currency": "USD"
      }
    ],
    "other": []
  },
  "kwai-post": {
    "platform": "kwai",
    "id": "5240932700689736196",
    "url": "https://www.kwai.com/@topfilmeseseriesnatv/video/5240932700689736196",
    "transcript": "BANDIDO ESTAVA ESPERANDO ELE NA SAIDA DO BANCO.",
    "publishedAt": "2026-01-24T00:50:13Z",
    "durationSeconds": 156,
    "thumbnailUrl": "https://aws-br-pic.kwai.net/upic/2026/01/24/08/BMjAyNjAxMjQwODQ4MTNfMTUwMDAxNDU1MDE5OTQ1XzE1MDExMDI4NTA4NDg3NF8yXzM=_oscn2_Befd2f922b58f2b5f72e4cb3c375d043d.webp",
    "videoUrl": "https://aws-br-cdn.kwai.net/upic/2026/01/24/08/BMjAyNjAxMjQwODQ4MTNfMTUwMDAxNDU1MDE5OTQ1XzE1MDExMDI4NTA4NDg3NF8yXzM=_b_Bf1ce0ec42b4fe4482cd50678b3abd2d4.mp4?tag=1-1784753172-s-0-afgxvdpz8w-4a78f339bd4accdf",
    "author": {
      "id": "3x9mhse7ekkvfa9",
      "username": "topfilmeseseriesnatv",
      "displayName": "Topseriesfilmetv",
      "avatar": "https://aws-br-pic.kwai.net/bs2/overseaHead/20250507231107_BMTUwMDAxNDU1MDE5OTQ1_s.jpg",
      "url": "https://www.kwai.com/@topfilmeseseriesnatv"
    },
    "engagement": {
      "views": 138841,
      "likes": 9232,
      "comments": 91,
      "shares": 169
    },
    "videoType": "mp4",
    "mediaUrlsExpireAt": "2026-07-22T20:46:12.000Z"
  },
  "kwai-profile": {
    "platform": "kwai",
    "id": "3xyutri4afq3qks",
    "eid": "3xyutri4afq3qks",
    "url": "https://www.kwai.com/@KwaiBrasilOficial",
    "username": "KwaiBrasilOficial",
    "displayName": "Kwai Brasil Oficial",
    "bio": "Aqui, Geral Brilha ✨",
    "avatar": "https://aws-br-pic.kwai.net/bs2/overseaHead/20260729230605_BNTU4ODQzMDkz_s.jpg",
    "verified": true,
    "verifiedDescription": "Conta Oficial",
    "verifiedNumber": 3,
    "followers": 414136454,
    "likedCount": 17600139,
    "publicPostCount": 3707,
    "privatePostCount": 0,
    "postCount": 3707,
    "isPrivate": false,
    "videoCount": 3707
  },
  "kwai-user-posts": {
    "profileUrl": "https://www.kwai.com/@topfilmeseseriesnatv",
    "author": {
      "id": "3x9mhse7ekkvfa9",
      "username": "topfilmeseseriesnatv",
      "displayName": "Topseriesfilmetv",
      "avatar": "https://aws-br-pic.kwai.net/bs2/overseaHead/20250507231107_BMTUwMDAxNDU1MDE5OTQ1_s.jpg",
      "url": "https://www.kwai.com/@topfilmeseseriesnatv"
    },
    "totalReturned": 5,
    "nextCursor": null,
    "hasMore": false,
    "posts": [
      {
        "platform": "kwai",
        "id": "5240932700689736196",
        "url": "https://www.kwai.com/@topfilmeseseriesnatv/video/5240932700689736196",
        "transcript": "BANDIDO ESTAVA ESPERANDO ELE NA SAIDA DO BANCO.",
        "publishedAt": "2026-01-24T00:50:13Z",
        "durationSeconds": 156,
        "thumbnailUrl": "https://aws-br-pic.kwai.net/upic/2026/01/24/08/BMjAyNjAxMjQwODQ4MTNfMTUwMDAxNDU1MDE5OTQ1XzE1MDExMDI4NTA4NDg3NF8yXzM=_oscn2_Befd2f922b58f2b5f72e4cb3c375d043d.webp",
        "videoUrl": "https://aws-br-cdn.kwai.net/upic/2026/01/24/08/BMjAyNjAxMjQwODQ4MTNfMTUwMDAxNDU1MDE5OTQ1XzE1MDExMDI4NTA4NDg3NF8yXzM=_b_Bf1ce0ec42b4fe4482cd50678b3abd2d4.mp4?tag=1-1784753172-s-0-afgxvdpz8w-4a78f339bd4accdf",
        "engagement": {
          "views": 138841,
          "likes": 9232,
          "comments": 91,
          "shares": 169
        },
        "videoType": "mp4",
        "mediaUrlsExpireAt": "2026-07-22T20:46:12.000Z"
      },
      {
        "platform": "kwai",
        "id": "5197304080333126332",
        "url": "https://www.kwai.com/@topfilmeseseriesnatv/video/5197304080333126332",
        "publishedAt": "2026-07-21T01:41:02Z",
        "durationSeconds": 125,
        "thumbnailUrl": "https://p16-kimg.kwai.net/kimg/EKzM1y8qmQEKAnMzEg1waG90by1vdmVyc2VhGoMBdXBpYy8yMDI2LzA3LzIxLzAxL0JNakF5TmpBM01qRXdNVFF3TVRCZk1UVXdNREF4TkRVMU1ERTVPVFExWHpFMU1ERXhNVEUwTlRFMU9UUTBNRjh5WHpNPV9vdXVfQjVkMzdmMDZiZTFmMmU5NjQ0MGNkNjhhMjc3ZTg1MjRlLndlYnA.webp",
        "videoUrl": "https://aws-br-cdn.kwai.net/upic/2026/07/21/01/BMjAyNjA3MjEwMTQwMTBfMTUwMDAxNDU1MDE5OTQ1XzE1MDExMTE0NTE1OTQ0MF8yXzM=_b_B9e078740aaad1692190abe5e2e2e61c6.mp4?tag=1-1784753179-s-0-46g59inljw-0d434501e8fb5c1c",
        "engagement": {
          "views": 8998,
          "likes": 441,
          "comments": 7,
          "shares": 16
        },
        "videoType": "mp4",
        "mediaUrlsExpireAt": "2026-07-22T20:46:19.000Z"
      }
    ]
  },
  "linkbio-page": {
    "platform": "linkbio",
    "id": "-1344625",
    "url": "https://lnk.bio/charlidamelio",
    "username": "charlidamelio",
    "handle": "charlidamelio",
    "avatar": "https://s3.us-west-2.amazonaws.com/cdn.lnk.bio/profilepics/-1344625_20220123667.jpg",
    "website": "https://www.charlidamelio.com",
    "linkCount": 15,
    "socials": {
      "facebook": "https://facebook.com/thecharlidamelio",
      "twitter": "https://twitter.com/charlidamelio",
      "instagram": "https://instagram.com/charlidamelio",
      "triller": "https://triller.co/m/@charlidamelio",
      "tiktok": "https://tiktok.com/@charlidamelio",
      "youtube": "https://youtube.com/c/charlidamelio",
      "snapchat": "https://www.snapchat.com/add/damelioc",
      "website": "https://www.charlidamelio.com"
    },
    "links": [
      {
        "url": "https://www.charlidamelio.com",
        "title": "official website of charli d'amelio",
        "id": "61ec9244a0fa03.74794466",
        "type": "TYPE_BUTTON"
      },
      {
        "url": "https://www.hollisterco.com/shop/us/social-tourist/shop-all?%20cmp=SOC:SPR21:ST:D:US:Brand:X:BioINF:PInf:X:X:CD:STHP-ST:x:Charli%20IG",
        "title": "shop social tourist january 2022 drop",
        "id": "2733218",
        "type": "TYPE_BIOLINK"
      }
    ],
    "other": []
  },
  "linkedin-ad-library-ad-details": {
    "platform": "linkedin_ad_library",
    "id": "1456323573",
    "url": "https://www.linkedin.com/ad-library/detail/1456323573",
    "text": "Drowning in one off scripts and manual steps? In a free 15 minute consult, our experts help streamline IT Infrastructure Operations with PowerShell.",
    "headline": null,
    "cta": "Learn more",
    "landingUrl": "https://calendly.com/d/cvqn-kt5-t72/free-consultation?utm_campaign=32735245-PowerHouse&utm_source=linkedin&utm_medium=paidsocial&utm_term=free%20consultation&utm_content=calendly%20link&trk=ad_library_ad_preview_content_image",
    "adFormat": null,
    "firstShown": "2026-07-28",
    "lastShown": "2026-08-02",
    "impressions": "1k-5k",
    "country": null,
    "advertiser": {
      "id": "16217038",
      "name": "ScriptRunner Software GmbH",
      "url": "https://www.linkedin.com/company/16217038",
      "logo": "https://media.licdn.com/dms/image/v2/C4D0BAQFYeG3JIAlUQg/company-logo_100_100/company-logo_100_100/0/1630544718632/scriptrunner_logo?e=1787184000&v=beta&t=CeO2dmEiPsb-6gTcpJtkBMm0c4JSLZ6b6zfm44wc_7s"
    },
    "media": [],
    "description": "Drowning in one off scripts and manual steps? In a free 15 minute consult, our experts help streamline IT Infrastructure Operations with PowerShell.",
    "destinationUrl": "https://calendly.com/d/cvqn-kt5-t72/free-consultation?utm_campaign=32735245-PowerHouse&utm_source=linkedin&utm_medium=paidsocial&utm_term=free%20consultation&utm_content=calendly%20link&trk=ad_library_ad_preview_content_image",
    "adDuration": "Ran from Jul 28, 2026 to Aug 2, 2026",
    "startDate": "2026-07-28",
    "endDate": "2026-08-02",
    "totalImpressions": "1k-5k",
    "impressionsByCountry": [
      {
        "country": "United States",
        "impressions": "97%"
      },
      {
        "country": "Canada",
        "impressions": "3%"
      }
    ],
    "targeting": {
      "language": "Targeting includes English",
      "location": "Targeting includes Germany, Switzerland and Netherlands, Benelux, DACH, United States, Canada, Austria, Belgium, United Kingdom"
    },
    "carouselImages": [],
    "paidForBy": "ScriptRunner Software GmbH",
    "countries": []
  },
  "linkedin-ad-library-search-ads": {
    "query": "microsoft",
    "keyword": null,
    "companyId": null,
    "country": "US",
    "countries": [
      "US"
    ],
    "startDate": null,
    "endDate": null,
    "totalAds": 7523,
    "totalReturned": 3,
    "paginationToken": "1456462353-1785251292711",
    "nextCursor": "1456462353-1785251292711",
    "isLastPage": false,
    "hasMore": true,
    "ads": [
      {
        "platform": "linkedin_ad_library",
        "id": "1456323573",
        "url": "https://www.linkedin.com/ad-library/detail/1456323573",
        "text": "Drowning in one off scripts and manual steps? In a free 15 minute consult, our experts help streamline IT Infrastructure Operations with PowerShell.",
        "headline": null,
        "cta": "Learn more",
        "landingUrl": "https://calendly.com/d/cvqn-kt5-t72/free-consultation?utm_campaign=32735245-PowerHouse&utm_source=linkedin&utm_medium=paidsocial&utm_term=free%20consultation&utm_content=calendly%20link&trk=ad_library_ad_preview_content_image",
        "adFormat": null,
        "firstShown": "2026-07-28",
        "lastShown": "2026-08-02",
        "impressions": "1k-5k",
        "country": "US",
        "advertiser": {
          "id": "16217038",
          "name": "ScriptRunner Software GmbH",
          "url": "https://www.linkedin.com/company/16217038",
          "logo": "https://media.licdn.com/dms/image/v2/C4D0BAQFYeG3JIAlUQg/company-logo_100_100/company-logo_100_100/0/1630544718632/scriptrunner_logo?e=1787184000&v=beta&t=CeO2dmEiPsb-6gTcpJtkBMm0c4JSLZ6b6zfm44wc_7s"
        },
        "media": [],
        "description": "Drowning in one off scripts and manual steps? In a free 15 minute consult, our experts help streamline IT Infrastructure Operations with PowerShell.",
        "destinationUrl": "https://calendly.com/d/cvqn-kt5-t72/free-consultation?utm_campaign=32735245-PowerHouse&utm_source=linkedin&utm_medium=paidsocial&utm_term=free%20consultation&utm_content=calendly%20link&trk=ad_library_ad_preview_content_image",
        "adDuration": "Ran from Jul 28, 2026 to Aug 2, 2026",
        "startDate": "2026-07-28",
        "endDate": "2026-08-02",
        "totalImpressions": "1k-5k",
        "impressionsByCountry": [
          {
            "country": "United States",
            "impressions": "97%"
          },
          {
            "country": "Canada",
            "impressions": "3%"
          }
        ],
        "targeting": {
          "language": "Targeting includes English",
          "location": "Targeting includes Germany, Switzerland and Netherlands, Benelux, DACH, United States, Canada, Austria, Belgium, United Kingdom"
        },
        "carouselImages": [],
        "paidForBy": "ScriptRunner Software GmbH",
        "countries": [
          "US"
        ]
      },
      {
        "platform": "linkedin_ad_library",
        "id": "1526380116",
        "url": "https://www.linkedin.com/ad-library/detail/1526380116",
        "text": "Built to grow together: The FY27 Microsoft Marketplace opportunity",
        "headline": "Built to grow together: The FY27 Microsoft Marketplace opportunity",
        "cta": null,
        "landingUrl": null,
        "adFormat": null,
        "firstShown": null,
        "lastShown": null,
        "impressions": null,
        "country": "US",
        "advertiser": {
          "name": "Built to grow together: The FY27 Microsoft Marketplace opportunity"
        },
        "media": [],
        "description": null,
        "destinationUrl": null,
        "adDuration": null,
        "startDate": null,
        "endDate": null,
        "totalImpressions": null,
        "impressionsByCountry": [],
        "targeting": null,
        "carouselImages": [],
        "paidForBy": null,
        "countries": [
          "US"
        ]
      }
    ]
  },
  "linkedin-company": {
    "platform": "linkedin",
    "type": "company",
    "url": "https://ca.linkedin.com/company/shopify",
    "name": "Shopify",
    "industry": "Software Development",
    "description": "Shopify is a leading global commerce company, providing trusted tools to start, grow, market, and manage a retail business of any size. Shopify makes commerce better for everyone with a platform and services that are engineered for reliability, while delivering a better shopping experience for consumers everywhere. Shopify powers millions of businesses in more than 175 countries and is trusted by brands such as Allbirds, Gymshark, PepsiCo, Staples, and many more.\n\nFind all our jobs here: www.shopify.com/careers",
    "website": "https://www.shopify.com",
    "followers": 1100174,
    "employeeCount": 29621,
    "employees": [],
    "size": "10,001+ employees",
    "founded": 2006,
    "organizationType": "Public Company",
    "specialties": [
      "ecommerce",
      "API"
    ],
    "headquarters": "Ottawa, ON, CA",
    "location": {
      "city": "Ottawa",
      "state": "ON",
      "country": "CA"
    },
    "slogan": "Make commerce better for everyone",
    "coverImage": "https://media.licdn.com/dms/image/v2/D561BAQHhgj9vXYPfGw/company-background_10000/B56ZanR4DlHUAg-/0/1746563203645/shopify_cover?e=1786471200&v=beta&t=ipMJX6bvyB3cy61qNb70u0k09GOWqudh6eQnnrtv3RM",
    "logo": "https://media.licdn.com/dms/image/v2/D560BAQG_KjTcNcrLVw/company-logo_200_200/B56ZZolTV.HUAU-/0/1745511331439/shopify_logo?e=2147483647&v=beta&t=D2saVg58cKnwEiDQgFgzvwL24mTRM_cPuU1ndv6kL2U",
    "funding": null,
    "similarPages": [
      {
        "name": "Stripe",
        "link": "https://www.linkedin.com/company/stripe",
        "image": null
      },
      {
        "name": "Spotify",
        "link": "https://se.linkedin.com/company/spotify",
        "image": null
      }
    ]
  },
  "linkedin-company-posts": {
    "company": "microsoft",
    "totalReturned": 5,
    "posts": [
      {
        "platform": "linkedin",
        "type": "post",
        "url": "https://www.linkedin.com/posts/microsoft_july-2026-activity-7487862338335801344-bBsC",
        "text": "Doctors are busy, visits can seem rushed. Many people – especially women – can feel like their doctor hasn’t really heard them.\n \nIn July's edition of The Monthly Tech-In, we explore how AI is helping clinicians spend more time listening to their patients and less time on administrative tasks. Beyond healthcare, we share stories about how farmers, researchers and executives are using AI to meet real-world challenges. \n \nLearn more about the people putting AI into practice.",
        "publishedAt": "2026-07-28T13:31:39.195Z",
        "author": {
          "name": "Microsoft",
          "url": "https://www.linkedin.com/company/microsoft"
        },
        "engagement": {
          "likes": 966,
          "comments": 76,
          "reposts": null
        },
        "id": "7487862338335801344"
      },
      {
        "platform": "linkedin",
        "type": "post",
        "url": "https://www.linkedin.com/posts/satyanadella_just-wrapped-our-earnings-call-it-was-a-activity-7488369807969370112-3kA1",
        "text": "Just wrapped our earnings call. It was a very strong close to what was a record fiscal year for Microsoft.\n  \n· Annual revenue: $331B, +18%\n· MS Cloud: $214B, + 27%\n· And Azure: $100B+, +41%\n  \nAnd even bigger opportunity ahead!\n  \nI wanted to share some more perspective on two areas of focus for us:\n  \nFirst, we are building a new model system, where the harness, context, memory, and action space are separate from any one model family, thereby moving the frontier on the cost -to-outcome curve. \n  \nAnd it’s not just about cost. It also has the added benefit of business continuity and resilience because every model is substitutable. \n  \nThis is the system we are using in our products, with great results. And we are making it available for our customers via Foundry too.\n\nYou can read more about this from Mustafa Suleyman here: https://lnkd.in/gQwfAbuc\n \nSecond, when it comes to Copilot, we are innovating rapidly, from chat to Cowork to Autopilots.\n  \nWe have also been super focused on improving the quality and performance of Copilot. Over the last three quarters, user satisfaction scor …",
        "publishedAt": "2026-07-29T23:08:09.380Z",
        "author": {
          "name": "Satya Nadella",
          "url": "https://www.linkedin.com/in/satyanadella"
        },
        "engagement": {
          "likes": 10710,
          "comments": 436,
          "reposts": null
        },
        "id": "7488369807969370112"
      }
    ],
    "nextCursor": "5",
    "hasMore": true
  },
  "linkedin-post-details": {
    "platform": "linkedin",
    "type": "post",
    "url": "https://www.linkedin.com/posts/microsoft_the-most-meaningful-breakthroughs-happen-activity-7477715981667086336-x68i",
    "text": "The most meaningful breakthroughs happen when technology is built with people in mind.\n \nThat was the message at Microsoft Build this month, where we announced a host of new tools to help developers build, dream and create. \n \nIn June’s edition of The Monthly Tech-In, we’re sharing stories from Build and beyond about the developers, founders and communities who are using AI to tackle real-world challenges, from helping creators protect their work to advancing more inclusive AI systems.\n \nRead more about the people and innovations who are shaping what's next:",
    "publishedAt": "2026-07-04 13:19:24",
    "author": {
      "name": "Microsoft",
      "headline": "28,652,029 followers",
      "url": "https://www.linkedin.com/company/microsoft/posts"
    },
    "engagement": {
      "likes": 1012,
      "comments": 82,
      "reposts": 49
    }
  },
  "linkedin-post-transcript": {
    "platform": "linkedin",
    "url": "https://www.linkedin.com/posts/microsoft_the-most-meaningful-breakthroughs-happen-activity-7477715981667086336-x68i",
    "transcript": "The most meaningful breakthroughs happen when technology is built with people in mind.\n \nThat was the message at Microsoft Build this month, where we announced a host of new tools to help developers build, dream and create. \n \nIn June’s edition of The Monthly Tech-In, we’re sharing stories from Build and beyond about the developers, founders and communities who are using AI to tackle real-world challenges, from helping creators protect their work to advancing more inclusive AI systems.\n \nRead more about the people and innovations who are shaping what's next:",
    "transcriptSegments": [
      {
        "text": "The most meaningful breakthroughs happen when technology is built with people in mind.",
        "index": 0,
        "wordCount": 13,
        "charStart": 0,
        "charEnd": 86
      },
      {
        "text": "That was the message at Microsoft Build this month, where we announced a host of new tools to help developers build, dream and create.",
        "index": 1,
        "wordCount": 24,
        "charStart": 89,
        "charEnd": 223
      },
      {
        "text": "In June’s edition of The Monthly Tech-In, we’re sharing stories from Build and beyond about the developers, founders and communities who are using AI to tackle real-world challenges, from helping creators protect their work to advancing more inclusive AI systems.",
        "index": 2,
        "wordCount": 40,
        "charStart": 227,
        "charEnd": 490
      },
      {
        "text": "Read more about the people and innovations who are shaping what's next:",
        "index": 3,
        "wordCount": 12,
        "charStart": 493,
        "charEnd": 564
      }
    ],
    "wordCount": 89,
    "segments": 4,
    "author": {
      "name": "Microsoft",
      "url": "https://www.linkedin.com/company/microsoft/posts"
    },
    "publishedAt": "2026-07-04 13:19:24",
    "timingSource": "none",
    "estimatedReadSeconds": 27,
    "language": null
  },
  "linkedin-profile": {
    "platform": "linkedin",
    "type": "person",
    "url": "https://www.linkedin.com/in/paul-martin-a5aa98",
    "username": "paul-martin-a5aa98",
    "name": "Paul Martin",
    "headline": "Culver City, California, United States | Professional Profile",
    "location": "Culver City, California, United States",
    "about": null,
    "followers": 5532,
    "connections": 500,
    "profileImage": "https://media.licdn.com/dms/image/v2/C5603AQERBmOpeQdTJg/profile-displayphoto-shrink_200_200/profile-displayphoto-shrink_200_200/0/1603153614207?e=2147483647&v=beta&t=jmt32YrTWx2FRGXeRg6yYkMBcNR7iGokOvlfuVH5d3U",
    "currentCompany": null
  },
  "linkedin-search-posts": {
    "query": "artificial intelligence",
    "sort": "relevance",
    "totalReturned": 5,
    "posts": [
      {
        "platform": "linkedin",
        "type": "post",
        "url": "https://www.linkedin.com/posts/edward-hallett-9aa4406b_ai-is-a-tool-we-need-to-remember-that-activity-7460399963181617152-BX0D",
        "text": "AI is a tool. \n\nWe need to remember that because it presents as intelligence. But intelligence is sentient.\n\nThat’s why we call it *artificial* intelligence \n\nIt’s artificial because ai only appears to create meaning. \n\nIn fact, there can be no meaning created by ai. \n\nMeaning only ever persists in the humans who engage with ai. (Meaning is the unique condition of being human).  \n\nThink of ai as a ‘magic mirror’ or an ‘echo chamber’. It returns our words and images to us with heightened grandeur and clarity.\n\nI’m grateful for AI. \n\nAi can help with the task of route optimization or translation.\n\nBut it cannot establish whether the destination is worth getting to, or whether the translated text is moving (for that someone needs to be moved). \n\nSo what? \n\nRemembering that this intelligence is artificial helps us delineate what within the province of human productivity cannot for structural reasons be substituted for by ai.\n\nThis is because human beings value intelligence (sentience) in the realm of productivity.\n\nI return to my chosen advisor (broker, therapist, architect) not just bec …",
        "publishedAt": "2026-05-13T18:45:58.726Z",
        "author": {
          "name": "Edward Hallett",
          "url": "https://www.linkedin.com/in/edward-hallett-9aa4406b"
        },
        "engagement": {
          "likes": 57,
          "comments": 3
        },
        "id": "7460399963181617152"
      },
      {
        "platform": "linkedin",
        "type": "post",
        "url": "https://www.linkedin.com/posts/ebender_when-people-ask-me-what-the-phrase-artificial-activity-7480663649716494336-Wnbx",
        "text": "When people ask me what the phrase \"artificial intelligence\" means, my short answer is, it means \"venture capitalists, give me some money\".\n\nBut OUP asked me for a longer answer, given here and summarized in the section headings:\n\nhttps://lnkd.in/gb28PW5k\n\nPreprint available from my publications page:\nhttps://lnkd.in/gW-KW9DY",
        "publishedAt": "2026-07-08T16:46:38.081Z",
        "author": {
          "name": "Emily M. Bender",
          "url": "https://www.linkedin.com/in/ebender"
        },
        "engagement": {
          "likes": 524,
          "comments": 18
        },
        "id": "7480663649716494336"
      }
    ]
  },
  "linkme-profile": {
    "platform": "linkme",
    "id": "1bf3efbf94cc4f55d3650ddc61094ac3",
    "url": "https://link.me/danucd",
    "username": "danucd",
    "handle": "danucd",
    "displayName": "Dana",
    "name": "Dana",
    "firstName": "Dana",
    "avatar": "https://media.link.me/_resize/image/quality=90,format=webp/webp-images/user-profile/1169288/tmp-2541-1763300314455.webp",
    "profileVisitCount": "54.1k",
    "createdAt": "2024-11-01 12:37:51",
    "updatedAt": "2025-11-16 13:43:17",
    "email": "dana.danucd@gmail.com",
    "socials": {
      "appleMusic": "https://music.apple.com/ng/artist/danucd/1562315189",
      "spotify": "https://open.spotify.com/artist/0A8XmfCL2yangEtvot3peD?autoplay=true&source_application=google_assistant",
      "instagram": "https://www.instagram.com/danucd/",
      "facebook": "https://www.facebook.com/Danucd",
      "twitter": "https://www.twitter.com/Danucd1",
      "youtube": "https://www.youtube.com/@DanucD2",
      "tiktok": "https://www.tiktok.com/@danucd_",
      "twitch": "https://m.twitch.tv/danucd?fbclid=PAZXh0bgNhZW0CMTEAAaaw5KxeIr47f2JnvCWttLnzIFG35Q8vQ6dK_H4Pv7bQKefUMmqYXvRPm90_aem_qRBQ5McX7dnSwaw8aHxqaA&desktop-redirect=true",
      "threads": "https://www.threads.net/@danucd?hl=en"
    },
    "chatId": "LinkMe-1169288",
    "bio": "ALL MY LINKS👇",
    "description": "ALL MY LINKS👇",
    "links": [
      {
        "url": "https://twitch.tv/danucd",
        "title": "Twitch",
        "id": "231267",
        "thumbnail": "small"
      },
      {
        "url": "https://www.youtube.com/@DanucD2",
        "title": "Daily YouTube",
        "id": "611348",
        "thumbnail": "small"
      }
    ],
    "linkCount": 12,
    "totalLinks": 7,
    "webLinks": [
      {
        "title": "Apple-music",
        "linkId": 9,
        "links": [
          {
            "linkValue": "https://music.apple.com/ng/artist/danucd/1562315189",
            "faceValue": "1562315189",
            "baseUrl": "https://music.apple.com/profile/"
          }
        ]
      },
      {
        "title": "Spotify",
        "linkId": 10,
        "links": [
          {
            "linkValue": "https://open.spotify.com/artist/0A8XmfCL2yangEtvot3peD?autoplay=true&source_application=google_assistant",
            "faceValue": "0A8XmfCL2yangEtvot3peD",
            "baseUrl": "https://open.spotify.com/user/"
          }
        ]
      }
    ],
    "infoLinks": [
      {
        "title": "Email",
        "linkId": 1,
        "links": [
          {
            "linkValue": "dana.danucd@gmail.com",
            "faceValue": "dana.danucdgmail.com"
          }
        ]
      }
    ],
    "other": [
      {
        "url": "https://www.deezer.com/artist/129733822/radio?autoplay=true",
        "title": "Deezer",
        "type": "Deezer"
      }
    ],
    "stripeStatus": {
      "tipsEnabled": false,
      "stripeEnabled": false
    },
    "isDefaultProfilePicture": false,
    "verifiedAccount": false,
    "isAmbassador": true,
    "isPrivate": false
  },
  "linktree-page": {
    "platform": "linktree",
    "url": "https://linktr.ee/miguelangeles",
    "id": 15278008,
    "username": "miguelangeles",
    "name": "MIGUEL ANGELES",
    "description": "☆☆☆☆ IRL ANGEL ☆☆☆☆\nψ EMBRACE CHAOS ψ",
    "avatar": "https://ugc.production.linktr.ee/d3141538-f586-4f3f-bc9a-a82fbebab798_DEATHRATTLE-slowed-COVER.jpeg",
    "verified": false,
    "verticals": [
      "music",
      "creative"
    ],
    "linkPlatforms": [
      "TikTok",
      "Instagram"
    ],
    "timezone": "America/New_York",
    "email": "miguel@irlangel.com",
    "linkCount": 8,
    "links": [
      {
        "title": "new project \"BEFORE THE SUN RISES & WINTERR ENDS\"",
        "type": "SPOTIFY_ALBUM",
        "id": "463416775",
        "url": "https://open.spotify.com/album/0pgrg7phBbnwGJ2HBEl9EG?si=Zub7J4I3RySAaM9WVX3Okg",
        "thumbnail": "https://ugc.production.linktr.ee/8ed131c7-6d74-47fc-bceb-8be7f6bae4c8_ab67616d0000b2739bd93cc6e406b820dfff691f.jpeg"
      },
      {
        "title": "stream \"NOVEMBERR\"",
        "type": "SPOTIFY_SONG",
        "id": "460281204",
        "url": "https://open.spotify.com/track/62HnBMEdZjeFCd2T8g37T8?si=7bd35dd0e9f24d65",
        "thumbnail": "https://ugc.production.linktr.ee/3bd59146-cd44-4187-9601-4341b21070d2_ab67616d0000b2739ad10104c60fb9deff5b7f34.jpeg"
      }
    ],
    "socials": [
      {
        "type": "INSTAGRAM",
        "url": "https://instagram.com/miguelangeles"
      },
      {
        "type": "TIKTOK",
        "url": "https://tiktok.com/@irlangel"
      }
    ],
    "socialAccounts": {
      "instagram": "https://instagram.com/miguelangeles",
      "tiktok": "https://tiktok.com/@irlangel",
      "spotify": "https://open.spotify.com/artist/14xRX3JR8H4RWh8R7V3fvZ?si=EgRxWIPiRcaEHtSnqk5PAQ",
      "youtube": "https://www.youtube.com/watch?v=xiFUzOJaiC4",
      "soundcloud": "https://soundcloud.com/miguelangeles",
      "appleMusic": "https://music.apple.com/ca/artist/miguel-angeles/1209423162"
    }
  },
  "pillar-page": {
    "platform": "pillar",
    "id": "d8a5cbb4-a64d-44f2-830d-27a489bbc608",
    "url": "https://pillar.io/angelstrife",
    "username": "angelstrife",
    "handle": "angelstrife",
    "displayName": "Ángel Strife",
    "name": "Ángel Strife",
    "firstName": "Angel",
    "lastName": "Blanco",
    "avatar": "https://res.cloudinary.com/pillario/image/upload/user-image/page/96024b21-566f-405a-b4f2-2784526b380b",
    "location": "México",
    "email": "angelrafaelcovablanco@gmail.com",
    "linkCount": 5,
    "socials": {
      "tiktok": "https://tiktok.com/@angelstrifeoficial",
      "spotify": "https://open.spotify.com/artist/3Lse4fAlOchY8msotsYMA6?si=4nKqeTSRRsSDoNj1tfvNtA",
      "twitter": "https://twitter.com/SoyAngelStrife",
      "youtube": "https://www.youtube.com/channel/UCgZSHuBjHSFADbFQOCN1ifg",
      "facebook": "https://www.facebook.com/AngelStrifeOficial",
      "linkedin": "https://mx.linkedin.com/in/angelcovablanco",
      "instagram": "https://www.instagram.com/angelstrifeoficial",
      "soundcloud": "https://soundcloud.com/contienda-records"
    },
    "bio": "Awarded as Ángel Strife for the nomination for best #RealityShow at the KidsChoiceAwards 2020 for his participation in the TheVoice México Season 9 Program with the Acunmedya production company on the television network TvAzteca, Awarded in Film Score for the Epstein Mention of the Fotogenia Festival 2020, as well as the Special Selection of the Hidalgo Film Fest 2020, Guanajuato 3.0 Experimental Film Festival 2020 & the international festival of film sur l'art \"Le Fife\" 2021 (Canada)",
    "description": "Awarded as Ángel Strife for the nomination for best #RealityShow at the KidsChoiceAwards 2020 for his participation in the TheVoice México Season 9 Program with the Acunmedya production company on the television network TvAzteca, Awarded in Film Score for the Epstein Mention of the Fotogenia Festival 2020, as well as the Special Selection of the Hidalgo Film Fest 2020, Guanajuato 3.0 Experimental Film Festival 2020 & the international festival of film sur l'art \"Le Fife\" 2021 (Canada)",
    "links": [
      {
        "id": "669fef70-1ba7-11ee-b33b-e5396daf72e9",
        "type": "spotify",
        "title": "30 Mil Pies De Altura Para Morir de Amor",
        "url": "https://open.spotify.com/album/14jqUYFbuBs0HcftvQ7jC3?si=bX_bInR7R9Wu-mC9_77Fvw&context=spotify%3Aalbum%3A14jqUYFbuBs0HcftvQ7jC3",
        "clicks": 0,
        "order": 2
      },
      {
        "id": "657440b0-1ba7-11ee-b33b-e5396daf72e9",
        "type": "instagram",
        "title": "SINCRONICIDAD",
        "url": "https://www.instagram.com/contiendarecords",
        "clicks": 5,
        "order": null,
        "description": "Sigue Nuestra Contienda"
      }
    ],
    "products": [
      {
        "id": "254c8681-1d52-11ee-b065-850167411bb1",
        "title": "\"30 Mil Pies De Altura Para Morir de Amor\" - LP",
        "name": "\"30 Mil Pies De Altura Para Morir de Amor\" - LP",
        "url": "https://angel-strife.ueniweb.com/products/merchandise/30-mil-pies-de-altura-para-morir-de-amor-lp-especial-edition-vynil-deluxe-53106871",
        "description": "Especial Edition Vynil Deluxe",
        "image": "https://athlane-file-management-prod.s3.amazonaws.com/a925f7b5-77ba-4095-b755-27b2bc221baa",
        "price": 0,
        "showPrice": false
      },
      {
        "id": "1ade72a0-5720-11ee-abe2-f1c4530bf5e3",
        "title": "Sweater Negro Gōruden Tsukoyomi (Edición Especial)",
        "name": "Sweater Negro Gōruden Tsukoyomi (Edición Especial)",
        "url": "https://angel-strife.ueniweb.com/products/merchandise/sweater-negro-goruden-tsukoyomi-edicion-especial-52958670",
        "description": "Sweater Negro Gōruden Tsukoyomi (Edición Especial) en todas las tallas con diseño Tsukoyomi (Dios de la Luna) & letras Rojas Sweater Negro. disponible en todas las tallas y entrega en territorio nacional e internacional.",
        "image": "https://athlane-file-management-prod.s3.amazonaws.com/8b2ac54c-21cd-4339-9cef-49bec35f26b4",
        "price": 0,
        "showPrice": false
      }
    ]
  },
  "pinterest-board": {
    "board": "https://www.pinterest.com/potterybarn/rustic-lodge-lookbook/",
    "totalReturned": 4,
    "pins": [
      {
        "platform": "pinterest",
        "id": "264938390611779142",
        "url": "https://www.pinterest.com/pin/264938390611779142/",
        "description": "Add texture and dimension to any console table with our Woven Vine Vase. Available in two sizes, this handcrafted piece is sure to make a statement. Complete the moment with some faux branches or florals. Tap to shop!",
        "domain": "Uploaded by user",
        "image": "https://i.pinimg.com/564x/22/f4/da/22f4da6ab05a70aabcda594a7d004883.jpg",
        "images": {
          "564x": {
            "url": "https://i.pinimg.com/564x/22/f4/da/22f4da6ab05a70aabcda594a7d004883.jpg",
            "width": 564,
            "height": 846
          },
          "originals": {
            "url": "https://i.pinimg.com/originals/22/f4/da/22f4da6ab05a70aabcda594a7d004883.jpg"
          }
        },
        "isVideo": false,
        "dominantColor": "#3f2712",
        "repinCount": 1,
        "board": {
          "name": "Rustic Lodge Lookbook",
          "url": "https://www.pinterest.com/potterybarn/rustic-lodge-lookbook/",
          "pinCount": 13,
          "followers": 1021580
        },
        "author": {
          "username": "potterybarn",
          "displayName": "Pottery Barn"
        },
        "originAuthor": {
          "id": "264938527987338255"
        },
        "saves": 2,
        "imageOriginal": "https://i.pinimg.com/originals/22/f4/da/22f4da6ab05a70aabcda594a7d004883.jpg"
      },
      {
        "platform": "pinterest",
        "id": "264938390611779129",
        "url": "https://www.pinterest.com/pin/264938390611779129/",
        "description": "Rustic meets refined with our expertly crafted Bozeman Console Table—perfect for any entryway or living room. Layer home decor with varying textures and heights to add dimension and character. Tap to shop our exclusive Fall collection.",
        "domain": "Uploaded by user",
        "image": "https://i.pinimg.com/564x/cc/2a/6a/cc2a6a49424bedc1aa29cdeb6195a48b.jpg",
        "images": {
          "564x": {
            "url": "https://i.pinimg.com/564x/cc/2a/6a/cc2a6a49424bedc1aa29cdeb6195a48b.jpg",
            "width": 564,
            "height": 846
          },
          "originals": {
            "url": "https://i.pinimg.com/originals/cc/2a/6a/cc2a6a49424bedc1aa29cdeb6195a48b.jpg"
          }
        },
        "isVideo": false,
        "dominantColor": "#3a220f",
        "board": {
          "name": "Rustic Lodge Lookbook",
          "url": "https://www.pinterest.com/potterybarn/rustic-lodge-lookbook/",
          "pinCount": 13,
          "followers": 1021580
        },
        "author": {
          "username": "potterybarn",
          "displayName": "Pottery Barn"
        },
        "originAuthor": {
          "id": "264938527987338255"
        },
        "saves": 1,
        "imageOriginal": "https://i.pinimg.com/originals/cc/2a/6a/cc2a6a49424bedc1aa29cdeb6195a48b.jpg",
        "repinCount": 0
      }
    ],
    "boardName": "Rustic Lodge Lookbook",
    "author": {
      "id": "264938527987338255",
      "username": "potterybarn",
      "displayName": "Pottery Barn",
      "url": "https://www.pinterest.com/potterybarn/",
      "followers": 1122739,
      "pinCount": 19312448,
      "avatar": "https://i.pinimg.com/60x60_RS/c0/c2/52/c0c252100791f0a4ed29e7bb31b85a0f.jpg",
      "about": "Ideas & inspiration for real life. Mindfully made. Crafted to last."
    }
  },
  "pinterest-pin-details": {
    "platform": "pinterest",
    "id": "422281212828530",
    "url": "https://www.pinterest.com/pin/422281212828530/",
    "domain": "Uploaded by user",
    "image": "https://i.pinimg.com/564x/51/a2/0e/51a20efe23e50376920012d832a191a2.jpg",
    "images": {
      "236x": {
        "url": "https://i.pinimg.com/236x/51/a2/0e/51a20efe23e50376920012d832a191a2.jpg",
        "width": 236,
        "height": 419
      },
      "237x": {
        "url": "https://i.pinimg.com/236x/51/a2/0e/51a20efe23e50376920012d832a191a2.jpg",
        "width": 236,
        "height": 419
      },
      "564x": {
        "url": "https://i.pinimg.com/564x/51/a2/0e/51a20efe23e50376920012d832a191a2.jpg",
        "width": 564,
        "height": 1002
      },
      "originals": {
        "url": "https://i.pinimg.com/originals/51/a2/0e/51a20efe23e50376920012d832a191a2.webp"
      }
    },
    "isVideo": false,
    "dominantColor": "#a87147",
    "saves": 9606,
    "repinCount": 2140,
    "board": {
      "name": "Sala",
      "url": "https://www.pinterest.com/camilarmoutinho/sala/",
      "pinCount": 5,
      "followers": 6
    },
    "author": {
      "id": "422418623531974",
      "username": "camilarmoutinho",
      "displayName": "Camila Moutinho",
      "url": "https://www.pinterest.com/camilarmoutinho/",
      "followers": 7,
      "pinCount": 265,
      "avatar": "https://i.pinimg.com/60x60_RS/80/48/e0/8048e086101e0b18790160b4251d00bc.jpg"
    },
    "originAuthor": {
      "id": "1049198181847459163",
      "username": "HomedecorInteriorDesigntips",
      "displayName": "B O E | Home, Bedroom, Living Room, Kitchen, Fashion & Bathroom",
      "url": "https://www.pinterest.com/HomedecorInteriorDesigntips/",
      "followers": 2956,
      "pinCount": 66723,
      "avatar": "https://i.pinimg.com/60x60_RS/8f/b3/53/8fb3538984206cebf310b7a979006bae.jpg",
      "about": "At BOE, we inspire stylish and functional home living. Discover the latest home improvement ideas, timeless bedroom and living room décor, practical kitchen and bathroom tips, and cozy laundry room inspiration. Explore curated collections of furniture, lighting, fashion accents, and accessories that blend beauty with utility. Get expert guides, DIY projects, and sustainable design practices to transform every space."
    },
    "title": "Bauhaus Interior",
    "description": "May 6, 2026 — A living room with a brown sofa and a yellow armchair. The space features a colorful rug with geometric patterns and a round glass coffee table. Funky mid century modern, Living spaces, Home interior design",
    "seoAltText": "a living room filled with lots of furniture next to a wall mounted book shelf and lamp",
    "createdAt": "2026-06-10T11:31:28.000Z",
    "publishedAt": "2026-06-10T11:31:28.000Z",
    "shareCount": 94,
    "reactionCount": 588
  },
  "pinterest-search": {
    "query": "living room decor",
    "totalReturned": 5,
    "results": [
      {
        "platform": "pinterest",
        "id": "7036943163632532",
        "url": "https://www.pinterest.com/pin/7036943163632532/",
        "title": "Kimberly Square Coffee Table",
        "description": "Kimberly Square Marble Coffee Table",
        "destinationUrl": "https://www.luluandgeorgia.com/products/kimberly-coffee-table?variant=41218898952291#m24480845889635",
        "image": "https://i.pinimg.com/originals/7f/68/af/7f68af1e9476e0a762ed9fcccd66cd24.jpg",
        "saves": 2,
        "publishedAt": "Tue, 28 Apr 2026 04:03:26 +0000",
        "board": {
          "name": "pretty furniture",
          "url": "https://www.pinterest.com/anrureck/pretty-furniture/"
        },
        "author": {
          "username": "anrureck",
          "displayName": "Anna Reckelhoff",
          "followers": 27
        }
      },
      {
        "platform": "pinterest",
        "id": "1266706141814841",
        "url": "https://www.pinterest.com/pin/1266706141814841/",
        "title": "Scandinavian Living Room: Turoy Ivory Bouclé Swivel Chair",
        "description": "Sit like a Bond villain whose only real diabolical concern is comfort. Photo by @amyepeters: lounge chair, chair, scandinavian, scandinavian living room, living room, living room designs, living room inspo, decor home living room, neutral living room, cozy corner, reading nook",
        "destinationUrl": "https://www.article.com/product/13941/turoy-ivory-boucle-swivel-chair?utm_medium=social&utm_source=pinterest&utm_campaign=evergreen&utm_content=igc",
        "image": "https://i.pinimg.com/originals/bc/ea/89/bcea896786826d048bdb6f4d486fc241.jpg",
        "saves": 91,
        "publishedAt": "Fri, 13 Feb 2026 17:08:40 +0000",
        "board": {
          "name": "Baddie",
          "url": "https://www.pinterest.com/christigia/baddie/"
        },
        "author": {
          "username": "christigia",
          "displayName": "Christi Giannetti",
          "followers": 255
        }
      }
    ]
  },
  "pinterest-user-boards": {
    "username": "potterybarn",
    "totalReturned": 5,
    "boards": [
      {
        "platform": "pinterest",
        "id": "264938459268358811",
        "name": "Cozy Home Inspiration",
        "url": "https://www.pinterest.com/potterybarn/cozy-home-inspiration/",
        "description": null,
        "privacy": "public",
        "pinCount": 26,
        "followers": null,
        "sectionCount": 0,
        "coverImage": "https://i.pinimg.com/474x/88/13/6d/88136d3c8ce2b489f83f4b70a7afba8a.jpg",
        "createdAt": "2026-07-29T17:28:42Z",
        "owner": {
          "username": "potterybarn",
          "displayName": "Pottery Barn"
        }
      },
      {
        "platform": "pinterest",
        "id": "264938459268358699",
        "name": "Rustic Lodge Lookbook",
        "url": "https://www.pinterest.com/potterybarn/rustic-lodge-lookbook/",
        "description": null,
        "privacy": "public",
        "pinCount": 13,
        "followers": null,
        "sectionCount": 0,
        "coverImage": "https://i.pinimg.com/474x/13/37/dd/1337dd421b303196c96002b735618cc3.jpg",
        "createdAt": "2026-07-27T18:39:04Z",
        "owner": {
          "username": "potterybarn",
          "displayName": "Pottery Barn"
        }
      }
    ]
  },
  "pinterest-user-pins": {
    "username": "potterybarn",
    "totalReturned": 5,
    "pins": [
      {
        "platform": "pinterest",
        "id": "264938390611768286",
        "url": "https://www.pinterest.com/pin/264938390611768286/",
        "description": "Our Rockport Metal Rectangular Outdoor Dining Table is the perfect table to gather around, share everyday meals, and create everlasting memories. Layer with your favorite dinnerware, table linens, and decor. Tap to shop our table.",
        "destinationUrl": "https://www.potterybarn.com/pages/lookbook/fall/rustic-lodge/?cm_ven=OrganicSocial&cm_cat=Pinterest&cm_pla=stpin&cm_ite=rusticlodgeoutdoordining",
        "image": "https://i.pinimg.com/564x/c5/3c/d8/c53cd8cbf2c9ac113541297716ea4f79.jpg",
        "board": {
          "name": "Rustic Lodge Lookbook",
          "url": "https://www.pinterest.com/potterybarn/rustic-lodge-lookbook/"
        },
        "author": {
          "username": "potterybarn",
          "displayName": "Pottery Barn",
          "followers": 1122723
        }
      },
      {
        "platform": "pinterest",
        "id": "264938390611768285",
        "url": "https://www.pinterest.com/pin/264938390611768285/",
        "description": "Turn your home into a cozy retreat with our Faux Fur Mink Throw Blankets. Available in over 10 colors, this soft throw blanket is perfect for cozying up on the couch, layering on a bed, or adding warmth and texture to any living room or bedroom. Tap to shop!",
        "destinationUrl": "https://www.potterybarn.com/pages/lookbook/fall/rustic-lodge/?cm_ven=OrganicSocial&cm_cat=Pinterest&cm_pla=stpin&cm_ite=rusticlodgeblankets",
        "image": "https://i.pinimg.com/564x/92/11/09/92110909d4268cb415bfb10ae6281f50.jpg",
        "board": {
          "name": "Rustic Lodge Lookbook",
          "url": "https://www.pinterest.com/potterybarn/rustic-lodge-lookbook/"
        },
        "author": {
          "username": "potterybarn",
          "displayName": "Pottery Barn",
          "followers": 1122723
        }
      }
    ]
  },
  "reddit-post-comments": {
    "totalReturned": 3,
    "comments": [
      {
        "id": "p0gnsr6",
        "author": "AutoModerator",
        "authorFullname": "t2_6l4z3",
        "text": "Users often report submissions from this site for sensationalized articles. Readers have a responsibility to be skeptical, check sources, and comment on any flaws.\n\nYou can help improve this thread by linking to media that verifies or questions this article's claims. Your link could help readers better understand this issue.\n\n*I am a bot, and this action was performed automatically. Please [contact the moderators of this subreddit](/message/compose/?to=/r/worldnews) if you have any questions or concerns.*",
        "upvotes": 1,
        "score": 1,
        "downs": 0,
        "publishedAt": "2026-07-29T13:12:05.000Z",
        "url": "https://www.reddit.com/r/worldnews/comments/1v9vtop/japans_population_falls_below_120_million_for/p0gnsr6/",
        "parentId": "t3_1v9vtop",
        "depth": 0,
        "isSubmitter": false,
        "edited": false,
        "stickied": true,
        "distinguished": "moderator",
        "controversiality": 0,
        "subreddit": "worldnews"
      },
      {
        "id": "p0gpy2l",
        "author": "Donnicton",
        "authorFullname": "t2_8iha3",
        "text": "Sorry, best we can do about it is symbolically send you home early one day this month to go make a kid or whatever.",
        "upvotes": 10014,
        "score": 10014,
        "downs": 0,
        "publishedAt": "2026-07-29T13:22:22.000Z",
        "url": "https://www.reddit.com/r/worldnews/comments/1v9vtop/japans_population_falls_below_120_million_for/p0gpy2l/",
        "parentId": "t3_1v9vtop",
        "depth": 0,
        "isSubmitter": false,
        "edited": false,
        "stickied": false,
        "distinguished": null,
        "controversiality": 0,
        "subreddit": "worldnews"
      }
    ],
    "post": {
      "platform": "reddit",
      "id": "1v9vtop",
      "name": "t3_1v9vtop",
      "url": "https://www.reddit.com/r/worldnews/comments/1v9vtop/japans_population_falls_below_120_million_for/",
      "title": "Japan's population falls below 120 million for first time in 42 years as birth crisis deepens",
      "text": null,
      "subreddit": "worldnews",
      "author": "rdh2dmd",
      "authorFullname": "t2_2i0a3navkp",
      "upvotes": 24395,
      "score": 24395,
      "downs": 0,
      "upvoteRatio": 0.95,
      "comments": 2932,
      "subscriberCount": 47503811,
      "totalAwardsReceived": null,
      "isVideo": false,
      "publishedAt": "2026-07-29T13:12:05+00:00",
      "flair": null,
      "nsfw": false,
      "thumbnail": "https://external-preview.redd.it/z1-dgwVNE_wakjIdcx8RRK7U5pnn5xhdXdXqCAQGY6U.jpeg?width=140&height=78&auto=webp&s=51c84bd9c71d792505f54b10d4023457a63d5495"
    }
  },
  "reddit-post-details": {
    "platform": "reddit",
    "id": "1ukq10z",
    "url": "https://www.reddit.com/r/explainlikeimfive/comments/1ukq10z/eli5_monthly_current_events_megathread/",
    "title": "ELI5: Monthly Current Events Megathread",
    "text": "Hi Everyone,\n\nThis is your monthly megathread for current/ongoing events. We recognize there is a lot of interest in objective explanations to ongoing events so we have created this space to allow those types of questions.\n\nPlease ask your question as top level comments (replies to the post) for others to reply to. The rules are still in effect, so no politics, no soapboxing, no medical advice, etc. We will ban users who use this space to make political, bigoted, or otherwise inflammatory points rather than objective topics/explanations.",
    "subreddit": "explainlikeimfive",
    "author": "AutoModerator",
    "upvotes": 14,
    "comments": 47,
    "publishedAt": "2026-07-01T16:10:09+00:00",
    "flair": "Other",
    "nsfw": false,
    "thumbnail": null
  },
  "reddit-post-transcript": {
    "platform": "reddit",
    "url": "https://www.reddit.com/r/space/comments/1umfd43/radiation_exposure_may_become_the_biggest/",
    "post": {
      "platform": "reddit",
      "id": "1umfd43",
      "url": "https://www.reddit.com/r/space/comments/1umfd43/radiation_exposure_may_become_the_biggest/",
      "title": "Radiation exposure may become the biggest challenge for future Moon and Mars missions",
      "text": "[removed]",
      "subreddit": "space",
      "author": "Low-Mathematician137",
      "upvotes": 0,
      "comments": 65,
      "publishedAt": "2026-07-03T14:04:13+00:00",
      "flair": "Discussion",
      "nsfw": false,
      "thumbnail": null
    },
    "transcript": "Title: Radiation exposure may become the biggest challenge for future Moon and Mars missions\n\n[removed]\n\nEffingWasps: Insert that very recent but weirdly broadly applicable “this has been talked about extensively you’re just 21” meme\n\nb407driver: Become? It has always been the greatest (unsolved) challenge.\n\nWaarm: The current biggest challenge is funding.",
    "transcriptSegments": [
      {
        "text": "Title: Radiation exposure may become the biggest challenge for future Moon and Mars missions",
        "speaker": "post",
        "index": 0,
        "wordCount": 14,
        "charStart": 0,
        "charEnd": 92
      },
      {
        "text": "[removed]",
        "speaker": "Low-Mathematician137",
        "index": 1,
        "wordCount": 1,
        "charStart": 94,
        "charEnd": 103
      },
      {
        "text": "EffingWasps: Insert that very recent but weirdly broadly applicable “this has been talked about extensively you’re just 21” meme",
        "speaker": "EffingWasps",
        "index": 2,
        "wordCount": 19,
        "charStart": 105,
        "charEnd": 233
      },
      {
        "text": "b407driver: Become? It has always been the greatest (unsolved) challenge.",
        "speaker": "b407driver",
        "index": 3,
        "wordCount": 10,
        "charStart": 235,
        "charEnd": 308
      },
      {
        "text": "Waarm: The current biggest challenge is funding.",
        "speaker": "Waarm",
        "index": 4,
        "wordCount": 7,
        "charStart": 310,
        "charEnd": 358
      }
    ],
    "wordCount": 51,
    "segments": 5,
    "commentsIncluded": 5,
    "timingSource": "none",
    "estimatedReadSeconds": 15
  },
  "reddit-search": {
    "query": "james webb",
    "sort": "relevance",
    "timeframe": null,
    "totalReturned": 5,
    "nextCursor": "t3_1s1neio",
    "hasMore": true,
    "results": [
      {
        "platform": "reddit",
        "id": "1rh4u8o",
        "name": "t3_1rh4u8o",
        "url": "https://www.reddit.com/r/todayilearned/comments/1rh4u8o/til_the_james_webb_space_telescope_has_found_over/",
        "title": "TIL the James Webb Space Telescope has found over 300 \"Little Red Dots\", objects that existed between 13.2 an 12.2 billion years ago, and whose nature is currently uncertain",
        "text": null,
        "subreddit": "todayilearned",
        "author": "brazzy42",
        "authorFullname": "t2_mh77j",
        "upvotes": 13637,
        "score": 13637,
        "downs": 0,
        "upvoteRatio": 0.98,
        "scoreHidden": false,
        "comments": 204,
        "subscriberCount": 41571692,
        "totalAwardsReceived": 0,
        "isVideo": false,
        "publishedAt": "2026-02-28T15:03:10.000Z",
        "flair": null,
        "nsfw": false,
        "thumbnail": "https://external-preview.redd.it/jv4EtU_QZlM0w1ZSlNWfvuzvkL-FJ00HGsTsl07LPss.jpeg?width=140&height=139&auto=webp&s=94311e1eec8a572c48b01d8b5cbae2f371396318"
      },
      {
        "platform": "reddit",
        "id": "1ucll2e",
        "name": "t3_1ucll2e",
        "url": "https://www.reddit.com/r/worldnews/comments/1ucll2e/james_webb_telescope_detects_galaxykilling_wind/",
        "title": "James Webb telescope detects 'galaxy-killing wind' near the dawn of time",
        "text": null,
        "subreddit": "worldnews",
        "author": "shdw_fght",
        "authorFullname": "t2_4zuqklab",
        "upvotes": 1472,
        "score": 1472,
        "downs": 0,
        "upvoteRatio": 0.97,
        "scoreHidden": false,
        "comments": 160,
        "subscriberCount": 47507091,
        "totalAwardsReceived": 0,
        "isVideo": false,
        "publishedAt": "2026-06-22T14:08:15.000Z",
        "flair": null,
        "nsfw": false,
        "thumbnail": "https://external-preview.redd.it/MvcbMbmZOw99iMdDsy1JbsvZKf_5VGs-WQ1y5lrYGwo.jpeg?width=140&height=78&auto=webp&s=ff7d6360b316c1006ac4c27398dfc41df784e772"
      }
    ]
  },
  "reddit-subreddit-details": {
    "platform": "reddit",
    "id": "t5_2qh87",
    "name": "space",
    "url": "https://www.reddit.com/r/space",
    "title": "/r/space: news, articles and discussion",
    "description": "Share & discuss informative content on:\n\n* Astrophysics\n* Cosmology\n* Space Exploration\n* Planetary Science\n* Astrobiology",
    "members": 27940319,
    "activeUsers": null,
    "category": "Lifestyles",
    "language": "en",
    "type": "public",
    "createdAt": "2008-01-26T06:07:54.000Z",
    "nsfw": false,
    "submitText": "PLEASE **[READ THE SIDEBAR](https://www.reddit.com/r/space/wiki/sidebar_template)** BEFORE POSTING.",
    "rules": [
      {
        "name": "Submissions must be related to Space/Cosmology",
        "description": "This includes \"circlejerky\" submissions or space-related art, with the exception of art from space agencies or historically-significant art.",
        "kind": "link",
        "violationReason": "Submissions must be related to Space/Cosmology",
        "priority": 0
      },
      {
        "name": "No sensationalist/misleading/unscientific content or titles",
        "description": "Post titles need to be descriptive and non-clickbait.  When submitting images titles need to accurately describe the content of the image (e.g. if an image is a composite this needs to be clearly stated), and without attempting to draw in upvotes or comments.  The image should stand on it's own.",
        "kind": "all",
        "violationReason": "No sensationalist/misleading/unscientific content or titles",
        "priority": 1
      }
    ],
    "icon": "https://styles.redditmedia.com/t5_2qh87/styles/communityIcon_ub69d1lpjlf51.png",
    "banner": "https://styles.redditmedia.com/t5_2qh87/styles/bannerBackgroundImage_n7bxapsg3kq81.png"
  },
  "reddit-subreddit-posts": {
    "subreddit": "space",
    "sort": "hot",
    "timeframe": null,
    "totalReturned": 3,
    "nextCursor": "t3_1vdd2k6",
    "hasMore": true,
    "posts": [
      {
        "platform": "reddit",
        "id": "1v7b3xg",
        "name": "t3_1v7b3xg",
        "url": "https://www.reddit.com/r/space/comments/1v7b3xg/all_space_questions_thread_for_week_of_july_26/",
        "title": "All Space Questions thread for week of July 26, 2026",
        "text": "Please sort comments by 'new' to find questions that would otherwise be buried.\n\nIn this thread you can ask any space related question that you may have.\n\nTwo examples of potential questions could be; \"How do rockets work?\", or \"How do the phases of the Moon work?\"\n\nIf you see a space related question posted in another subreddit or in this subreddit, then please politely link them to this thread.\n\n​\n\nAsk away!",
        "subreddit": "space",
        "author": "AutoModerator",
        "authorFullname": "t2_6l4z3",
        "upvotes": 11,
        "score": 11,
        "downs": 0,
        "upvoteRatio": 0.67,
        "comments": 38,
        "subscriberCount": 27937807,
        "totalAwardsReceived": 0,
        "isVideo": false,
        "publishedAt": "2026-07-26T18:00:07.000Z",
        "flair": null,
        "nsfw": false,
        "thumbnail": null
      },
      {
        "platform": "reddit",
        "id": "1vd1sxs",
        "name": "t3_1vd1sxs",
        "url": "https://www.reddit.com/r/space/comments/1vd1sxs/gum_nebula_in_tuscany/",
        "title": "Gum nebula in Tuscany",
        "text": "Stacked/Tracked/Blended\n\nhttps://www.instagram.com/flory.ro?igsh=b3Y4ZTU3Nmk0cTBt&utm\\_source=qr\n\nThe Edge\n\nThis was my winter goal: to capture the Gum nebula over the Tuscan coast.\n\nFor months the weather refused to cooperate.\n\nCountless trips ended in nothing.\n\nThen one night, after a long descent through the woods, driven only by stubbornness and a bit of recklessness, I finally reached this beach.\n\nI rarely edit my photos right away. Most of the time I leave them sleeping.\n\nWhen the feeling returns, I choose one memory and bring it back to life.\n\nThis is one of those nights.\n\nCanon R\n\nCanon 6D\n\nSigma 24mm f1.4\n\nForeground 2x120s iso 3200 f2.8\n\nSky  3x120s iso 1600 f 2.00\n\nHa 6x120s iso 3200 f2.8",
        "subreddit": "space",
        "author": "flory_ro",
        "authorFullname": "t2_22o0rottmc",
        "upvotes": 3334,
        "score": 3334,
        "downs": 0,
        "upvoteRatio": 0.98,
        "comments": 25,
        "subscriberCount": 27937807,
        "totalAwardsReceived": 0,
        "isVideo": false,
        "publishedAt": "2026-08-01T23:16:42.000Z",
        "flair": "image/gif",
        "nsfw": false,
        "thumbnail": "https://preview.redd.it/1c7e0qngjugh1.jpeg?width=140&height=140&crop=1:1,smart&auto=webp&s=904837be378093471aad053d9ce99316becf8ad9"
      }
    ]
  },
  "reddit-subreddit-search": {
    "subreddit": "space",
    "query": "moon",
    "sort": "new",
    "timeframe": "month",
    "totalReturned": 5,
    "nextCursor": "t3_1vcuw1e",
    "hasMore": true,
    "results": [
      {
        "platform": "reddit",
        "id": "1vdyhxe",
        "name": "t3_1vdyhxe",
        "url": "https://www.reddit.com/r/space/comments/1vdyhxe/defunct_part_of_spacex_falcon_9_rocket_will_slam/",
        "title": "Defunct part of SpaceX Falcon 9 rocket will slam into the moon",
        "text": null,
        "subreddit": "space",
        "author": "DoremusJessup",
        "authorFullname": "t2_612zd",
        "upvotes": 0,
        "score": 0,
        "downs": 0,
        "upvoteRatio": 0.36,
        "comments": 17,
        "subscriberCount": 27939274,
        "totalAwardsReceived": 0,
        "isVideo": false,
        "publishedAt": "2026-08-03T00:37:18.000Z",
        "flair": null,
        "nsfw": false,
        "thumbnail": "https://external-preview.redd.it/H53j3-I3jiW5Qq6JAAR1ywvsYvBmTh5Qlvj2j8mj61E.jpeg?width=140&height=78&auto=webp&s=238c7b5582fe44c2bb3b46390d8e70d9fa3346f3"
      },
      {
        "platform": "reddit",
        "id": "1vdxtae",
        "name": "t3_1vdxtae",
        "url": "https://www.reddit.com/r/space/comments/1vdxtae/why_the_near_and_far_sides_of_the_moon_are_so/",
        "title": "Why the near and far sides of the moon are so different",
        "text": "I have never seen the explanations for this difference as believable past the obvious crust being thinner on the near side allowing eruptions of magma (the dark areas) that didn't happen on the far side.\n\nI asked questions of five different sites before DeepSeek gave me the key to understanding what happened. That key is degree-one mantle convection. \n\nAfter the impact of Theia with the young Earth that resulted in the creation of the Moon, both the Earth and the Moon were molten balls of magma, with the Moon in an eccentric orbit very close to the earth. \n\nTidal friction rapidly caused the Moon to be tidally locked to the Earth so that one side continually faced Earth. However the moon was still in an eccentric orbit, so as the Moon came closer and further from Earth it flexed, causing frictional heating keeping it molten longer. However the Earth, still being enormously hot, slightly heated the surface of the moon facing it by radiative heating. The moon was some twenty times closer to earth than it is now. \n\nThis radiative heating was just enough to keep the close side a little bi …",
        "subreddit": "space",
        "author": "grahamsuth",
        "authorFullname": "t2_17edr0epez",
        "upvotes": 0,
        "score": 0,
        "downs": 0,
        "upvoteRatio": 0.26,
        "comments": 5,
        "subscriberCount": 27939274,
        "totalAwardsReceived": 0,
        "isVideo": false,
        "publishedAt": "2026-08-03T00:06:35.000Z",
        "flair": "Discussion",
        "nsfw": false,
        "thumbnail": null
      }
    ]
  },
  "rumble-channel-videos": {
    "channel": "Bongino",
    "totalReturned": 5,
    "videos": [
      {
        "platform": "rumble",
        "id": "v7dfegc",
        "url": "https://rumble.com/v7dfegc-the-democrat-civil-war-is-getting-intense-ep.-2563-07292026.html",
        "type": "video",
        "title": "The Democrat Civil War Is Getting Intense (Ep. 2563) - 07/29/2026",
        "channel": "The Dan Bongino Show",
        "channelUrl": "https://rumble.com/c/bongino",
        "channelHandle": "bongino",
        "channelFollowers": 3661298,
        "channelVerified": true,
        "views": 230174,
        "likes": 4178,
        "dislikes": 43,
        "durationSeconds": 5456,
        "durationText": "1:30:56",
        "publishedAt": "2026-07-29T12:29:52+00:00",
        "thumbnail": "https://1a-1791.com/video/fwe2/83/s8/1/S/_/P/K/S_PKA.OvCc-small-The-Democrat-Civil-War-Is-G..jpg",
        "comments": 91,
        "isLive": false,
        "streams": [
          {
            "url": "https://rumble.com/live-hls-dvr/BE4yqeSGJMg/playlist.m3u8",
            "type": "hls",
            "quality": "auto"
          }
        ],
        "shareUrl": "https://rumble.com/share/v7dfegc"
      },
      {
        "platform": "rumble",
        "id": "v7det4g",
        "url": "https://rumble.com/shorts/v7det4g",
        "type": "short",
        "title": "Just Wait Until You Read TRUMP’S Diary...",
        "channel": "The Dan Bongino Show",
        "channelUrl": "https://rumble.com/c/bongino",
        "channelHandle": "bongino",
        "channelFollowers": 3661298,
        "channelVerified": true,
        "views": 8242,
        "likes": 234,
        "dislikes": 7,
        "durationSeconds": 55,
        "durationText": "0:55",
        "publishedAt": "2026-07-29T02:21:55+00:00",
        "thumbnail": "https://1a-1791.com/video/fwe2/b4/s8/1/W/p/J/K/WpJKA.OvCc-small-Just-Wait-Until-You-Read-TR..jpg",
        "comments": 11,
        "isLive": false,
        "streams": [
          {
            "url": "https://1a-1791.com/video/fwe2/b4/s8/2/W/p/J/K/WpJKA.haa.mp4?b=1&u=6",
            "type": "mp4",
            "quality": "1080p"
          },
          {
            "url": "https://1a-1791.com/video/fwe2/b4/s8/2/W/p/J/K/WpJKA.gaa.mp4?b=1&u=6",
            "type": "mp4",
            "quality": "720p"
          }
        ],
        "shareUrl": "https://rumble.com/share/v7det4g"
      }
    ]
  },
  "rumble-comments": {
    "url": "https://rumble.com/v7cv2cc-now-i-can-finally-talk-about-it-ep.-2555-07172026.html",
    "totalReturned": 5,
    "comments": [
      {
        "platform": "rumble",
        "id": "614445110",
        "text": "Ballot harvesting at nursing homes is a prime reason the Dems fight against election integrity",
        "author": {
          "name": "KMac170",
          "url": "https://rumble.com/user/KMac170",
          "verified": false
        },
        "likes": 216,
        "replyCount": 14,
        "createdAt": "Friday, July 17, 2026 08:33 AM -04"
      },
      {
        "platform": "rumble",
        "id": "614648184",
        "text": "And guess how that aid votes 🙄",
        "author": {
          "name": "Bonniekost",
          "url": "https://rumble.com/user/Bonniekost",
          "verified": false
        },
        "likes": 0,
        "replyCount": 1,
        "createdAt": "Monday, July 20, 2026 07:48 PM -04"
      }
    ]
  },
  "rumble-search": {
    "query": "space",
    "totalReturned": 5,
    "results": [
      {
        "platform": "rumble",
        "id": "v7dbdz0",
        "url": "https://rumble.com/v7dbdz0-flat-earth-fake-space.html",
        "type": "video",
        "title": "FLAT EARTH - FAKE SPACE",
        "channel": "Flat Earth Clock app",
        "channelUrl": "https://rumble.com/c/flatearthclock",
        "views": 954,
        "likes": 17,
        "dislikes": null,
        "durationSeconds": 485,
        "durationText": "8:05",
        "publishedAt": "2026-07-27T08:08:00-04:00",
        "thumbnail": "https://1a-1791.com/video/fwe2/96/s8/1/8/r/8/J/8r8JA.oq1b-small-FLAT-EARTH-FAKE-SPACE..jpg",
        "comments": 1
      },
      {
        "platform": "rumble",
        "id": "v7dbg7s",
        "url": "https://rumble.com/v7dbg7s-dummyvision-2-just-asking-questions-and-closing-arguments-from-baron-colema.html",
        "type": "video",
        "title": "SUNDAY SLOWS - Listening To a Special Spaces on Tyler Robinson - Misunderstanding Trial 101",
        "channel": "Rekieta Law",
        "channelUrl": "https://rumble.com/c/RekietaLaw",
        "views": 7720,
        "likes": 113,
        "dislikes": 6,
        "durationSeconds": 14139,
        "durationText": "3:55:39",
        "publishedAt": "2026-07-27T00:18:40-04:00",
        "thumbnail": "https://1a-1791.com/video/fww1/89/s8/6/y/_/8/J/y_8JA.oq1b.37.jpg",
        "comments": 7
      }
    ]
  },
  "rumble-video-details": {
    "platform": "rumble",
    "id": "v7cv2cc",
    "numericId": 441201242,
    "embedId": "v7aoh22",
    "url": "https://rumble.com/v7cv2cc-now-i-can-finally-talk-about-it-ep.-2555-07172026.html",
    "type": "video",
    "embedUrl": "https://rumble.com/embed/v7aoh22/",
    "shareUrl": "https://rumble.com/share/v7cv2cc?src=pEKvigixSA18kCOHqJfLmJzJ7JBZcpQdtcNMOQ_0_L2s9WPwl09OdA",
    "title": "Now I Can Finally Talk About It (Ep. 2555) - 07/17/2026",
    "description": "In this episode, I'll discuss the groundbreaking information President Trump revealed in his speech last night and what it means for our elections movingforward. 1776 Live Club: No purchase necessary.",
    "channel": "The Dan Bongino Show",
    "channelUrl": "https://rumble.com/c/bongino",
    "channelHandle": "bongino",
    "channelFollowers": 3660000,
    "channelVerified": true,
    "views": 943676,
    "likes": 15500,
    "dislikes": 194,
    "comments": 1050,
    "durationSeconds": 5185,
    "durationText": "1:26:25",
    "publishedAt": "2026-07-17T12:18:39+00:00",
    "thumbnail": "https://1a-1791.com/video/fwe2/7c/s8/1/C/w/c/H/CwcHA.qR4e-small-Now-I-Can-Finally-Talk-Abou..jpg",
    "width": 1920,
    "height": 1080,
    "captions": {
      "en-auto": {
        "language": "English (auto)",
        "path": "https://1a-1791.com/video/fwe2/7c/s8/11/C/w/c/H/CwcHA.fn8Si.vtt"
      }
    },
    "media": {
      "mp4": {
        "360": {
          "url": "https://1a-1791.com/video/fwe2/7c/s8/2/C/w/c/H/CwcHA.baa.rec.mp4",
          "meta": {
            "bitrate": 636,
            "size": 412534201,
            "w": 640,
            "h": 360
          }
        },
        "480": {
          "url": "https://1a-1791.com/video/fwe2/7c/s8/2/C/w/c/H/CwcHA.caa.rec.mp4",
          "meta": {
            "bitrate": 1005,
            "size": 651781271,
            "w": 854,
            "h": 480
          }
        },
        "720": {
          "url": "https://1a-1791.com/video/fwe2/7c/s8/2/C/w/c/H/CwcHA.gaa.rec.mp4",
          "meta": {
            "bitrate": 2067,
            "size": 1340090002,
            "w": 1280,
            "h": 720
          }
        },
        "1080": {
          "url": "https://1a-1791.com/video/fwe2/7c/s8/2/C/w/c/H/CwcHA.haa.rec.mp4",
          "meta": {
            "bitrate": 3985,
            "size": 2583714297,
            "w": 1920,
            "h": 1080
          }
        },
        "240": {
          "url": "https://1a-1791.com/video/fwe2/7c/s8/2/C/w/c/H/CwcHA.oaa.rec.mp4",
          "meta": {
            "bitrate": 203,
            "size": 131950161,
            "w": 640,
            "h": 360
          }
        },
        "1081": {
          "url": "https://1a-1791.com/video/fwe2/7c/s8/2/C/w/c/H/CwcHA.aaa.rec.mp4",
          "meta": {
            "bitrate": 8051,
            "size": 5219124253,
            "w": 1920,
            "h": 1080
          }
        }
      },
      "timeline": {
        "180": {
          "url": "https://1a-1791.com/video/fwe2/7c/s8/2/C/w/c/H/CwcHA.Faa.rec.mp4",
          "meta": {
            "bitrate": 11,
            "size": 7777789,
            "w": 320,
            "h": 180
          }
        }
      },
      "audio": {
        "192": {
          "url": "https://1a-1791.com/video/fwe2/7c/s8/2/C/w/c/H/CwcHA.Gaa.rec.aac",
          "meta": {
            "bitrate": 192,
            "size": 124450817,
            "w": 0,
            "h": 0
          }
        }
      }
    },
    "isLive": false,
    "streams": [
      {
        "url": "https://1a-1791.com/video/fwe2/7c/s8/2/C/w/c/H/CwcHA.aaa.rec.mp4",
        "type": "mp4",
        "quality": "1081p"
      },
      {
        "url": "https://1a-1791.com/video/fwe2/7c/s8/2/C/w/c/H/CwcHA.haa.rec.mp4",
        "type": "mp4",
        "quality": "1080p"
      }
    ]
  },
  "rumble-video-transcript": {
    "platform": "rumble",
    "id": "v7cv2cc",
    "url": "https://rumble.com/v7cv2cc-now-i-can-finally-talk-about-it-ep.-2555-07172026.html",
    "source": "captions",
    "language": "en-auto",
    "languageName": "English (auto)",
    "durationSeconds": 5185,
    "segments": [
      {
        "text": "All America all the time sit down buckle up and get ready for the Dan Bongino show",
        "startMs": 52240,
        "endMs": 59760
      },
      {
        "text": "team is like",
        "startMs": 65750,
        "endMs": 71960
      },
      {
        "text": "Thank you. Mr. President for",
        "startMs": 71960,
        "endMs": 74280
      },
      {
        "text": "Declassifying a lot of this folks",
        "startMs": 75080,
        "endMs": 77080
      },
      {
        "text": "Obviously",
        "startMs": 79390,
        "endMs": 81720
      },
      {
        "text": "Was like itching to get on the air today",
        "startMs": 81720,
        "endMs": 85240
      },
      {
        "text": "When you go and take a job in the government, especially in the executive branch",
        "startMs": 85880,
        "endMs": 92530
      },
      {
        "text": "The president is the ultimate declassifier the job is not about you",
        "startMs": 93420,
        "endMs": 98140
      }
    ],
    "text": "All America all the time sit down buckle up and get ready for the Dan Bongino show team is like Thank you. Mr. President for Declassifying a lot of this folks Obviously Was like itching to get on the air today When you go and take a job in the government, especially in the executive branch The president is the ultimate declassifier the job is not about you"
  },
  "snapchat-user-profile": {
    "platform": "snapchat",
    "username": "nba",
    "handle": "nba",
    "url": "https://www.snapchat.com/@nba",
    "displayName": "NBA",
    "bio": "30 teams, 1 goal.",
    "category": "Business Group",
    "categoryId": "public-profile-category-v3-business-group",
    "subcategory": "Sports League",
    "subcategoryId": "public-profile-subcategory-v3-sports-league",
    "subscriberCount": 3653600,
    "followers": 3653600,
    "verified": true,
    "badge": 1,
    "avatar": "https://cf-st.sc-cdn.net/aps/bolt/aHR0cHM6Ly9jZi1zdC5zYy1jZG4ubmV0L2QvcGxQanhqRDFZRk9IUWdGMUZLRHNqP2JvPUVna3lBUVJJQWxBWllBRSUzRCZ1Yz0yNQ._RS0,90_FMjpeg",
    "banner": "https://cf-st.sc-cdn.net/aps/bolt/aHR0cHM6Ly9jZi1zdC5zYy1jZG4ubmV0L2QvcUZBYjExSEY3QkdkeHNiOXpkMTREP2JvPUVna3lBUVJJQWxBWllBRSUzRCZ1Yz0yNQ._RS0,1080_FMjpeg",
    "profilePictureUrl": "https://cf-st.sc-cdn.net/aps/bolt/aHR0cHM6Ly9jZi1zdC5zYy1jZG4ubmV0L2QvcGxQanhqRDFZRk9IUWdGMUZLRHNqP2JvPUVna3lBUVJJQWxBWllBRSUzRCZ1Yz0yNQ._RS0,90_FMjpeg",
    "squareHeroImageUrl": "https://cf-st.sc-cdn.net/aps/bolt/aHR0cHM6Ly9jZi1zdC5zYy1jZG4ubmV0L2QvcUZBYjExSEY3QkdkeHNiOXpkMTREP2JvPUVna3lBUVJJQWxBWllBRSUzRCZ1Yz0yNQ._RS0,1080_FMjpeg",
    "snapcode": "https://app.snapchat.com/web/deeplink/snapcode?username=nba&type=SVG&bitmoji=enable",
    "website": "https://NBA.com",
    "businessProfileId": "ea71b19b-5eb1-4dda-afb8-13ced485f180",
    "creationTimestampMs": 1526597295058,
    "createdAt": "2018-05-17T22:48:15.058000Z",
    "lastUpdateTimestampMs": 1785621674522,
    "updatedAt": "2026-08-01T22:01:14.522000Z",
    "hasStory": false,
    "hasCuratedHighlights": true,
    "hasSpotlightHighlights": true,
    "highlights": [
      {
        "highlightId": "029f2cc3-c0df-46c2-b610-485c137f9a0a",
        "storyTitle": "2025-26 NBA Finals 🏆",
        "thumbnailUrl": "https://cf-st.sc-cdn.net/d/ZXSSacNIpSYqxAm21SSGc.410?mo=GjcaFjIBBDoBfUIGCMqG99AGSAJQXmABcAFQxQFaEERmTGFyZ2VUaHVtYm5haWyiAQcImgMiAhIA&uc=94",
        "snapCount": 4,
        "firstSnapUrl": "https://cf-st.sc-cdn.net/d/ZXSSacNIpSYqxAm21SSGc.400?mo=Gk8aDDIBBDoBfVBeYAFwAVDBAVoQUHVibGljSW1hZ2VTdG9yeaIBEwiQAyIOCgpCBgjKhvfQBkgCEgCiARMI5wciDgoKQgYIy4b30AZIAxIA&uc=94",
        "firstSnapType": "image",
        "snapList": [
          {
            "snapIndex": 0,
            "snapMediaType": 0,
            "mediaType": "image",
            "mediaUrl": "https://cf-st.sc-cdn.net/d/ZXSSacNIpSYqxAm21SSGc.400?mo=Gk8aDDIBBDoBfVBeYAFwAVDBAVoQUHVibGljSW1hZ2VTdG9yeaIBEwiQAyIOCgpCBgjKhvfQBkgCEgCiARMI5wciDgoKQgYIy4b30AZIAxIA&uc=94",
            "mediaPreviewUrl": "https://cf-st.sc-cdn.net/d/ZXSSacNIpSYqxAm21SSGc.410?mo=GjcaFjIBBDoBfUIGCMqG99AGSAJQXmABcAFQxQFaEERmTGFyZ2VUaHVtYm5haWyiAQcImgMiAhIA&uc=94",
            "timestampInSec": 1780335408,
            "publishedAt": "2026-06-01T17:36:48Z"
          },
          {
            "snapIndex": 1,
            "snapMediaType": 0,
            "mediaType": "image",
            "mediaUrl": "https://cf-st.sc-cdn.net/d/FgntIqJi6clNRLmaxXkXN.400?mo=Gk0aDjIBBDoBfUgCUF5gAXABUMEBWhBQdWJsaWNJbWFnZVN0b3J5ogERCJADIgwKCEIGCMuG99AGEgCiAREI5wciDAoIQgYIyob30AYSAA%3D%3D&uc=94",
            "mediaPreviewUrl": "https://cf-st.sc-cdn.net/d/FgntIqJi6clNRLmaxXkXN.410?mo=GjcaFjIBBDoBfUIGCMuG99AGSAJQXmABcAFQxQFaEERmTGFyZ2VUaHVtYm5haWyiAQcImgMiAhIA&uc=94",
            "timestampInSec": 1780335408,
            "publishedAt": "2026-06-01T17:36:48Z"
          }
        ]
      },
      {
        "highlightId": "2941c1a3-96ba-45aa-bdf4-30b344e63e42",
        "storyTitle": "Your 2025-26 Kia NBA MVP 🏆",
        "thumbnailUrl": "https://cf-st.sc-cdn.net/d/iqFfVpTceYNBTtMJvlQns.410.IRZXSOY?mo=GkAaFjIBBDoBfUIGCPa5qdAGSAJQXmABcAFQxQFaEERmTGFyZ2VUaHVtYm5haWyiARAImgMiCxIAKgdJUlpYU09Z&uc=94",
        "snapCount": 19,
        "firstSnapUrl": "https://cf-st.sc-cdn.net/d/iqFfVpTceYNBTtMJvlQns.400.IRZXSOY?mo=GlwaCTIBBFBeYAFwAVDBAVoQUHVibGljSW1hZ2VTdG9yeaIBHwiQAyIaCg06AX1CBgj2uanQBkgCEgAqB0lSWlhTT1miARcI5wciEgoFMgF9SAQSACoHSVJaWFNPWQ%3D%3D&uc=94",
        "firstSnapType": "image",
        "snapList": [
          {
            "snapIndex": 0,
            "snapMediaType": 0,
            "mediaType": "image",
            "mediaUrl": "https://cf-st.sc-cdn.net/d/iqFfVpTceYNBTtMJvlQns.400.IRZXSOY?mo=GlwaCTIBBFBeYAFwAVDBAVoQUHVibGljSW1hZ2VTdG9yeaIBHwiQAyIaCg06AX1CBgj2uanQBkgCEgAqB0lSWlhTT1miARcI5wciEgoFMgF9SAQSACoHSVJaWFNPWQ%3D%3D&uc=94",
            "mediaPreviewUrl": "https://cf-st.sc-cdn.net/d/iqFfVpTceYNBTtMJvlQns.410.IRZXSOY?mo=GkAaFjIBBDoBfUIGCPa5qdAGSAJQXmABcAFQxQFaEERmTGFyZ2VUaHVtYm5haWyiARAImgMiCxIAKgdJUlpYU09Z&uc=94",
            "timestampInSec": 1779061414,
            "publishedAt": "2026-05-17T23:43:34Z"
          },
          {
            "snapIndex": 1,
            "snapMediaType": 1,
            "mediaType": "video",
            "mediaUrl": "https://cf-st.sc-cdn.net/d/eHfqR7qRY9kuVjZbupqN4.1034.IRZXSOY?mo=GlgaDDICBH1IA1BeYAFwAVDIAVoHRGZNZWRpYaIBNwiKCBIlCiMIk84gIAEw4AM41AZAAUoOCgk9ExQVFBIUFRUQ9ANQ_E1oAiILEgAqB0lSWlhTT1mQA_xN&uc=94",
            "mediaPreviewUrl": "https://cf-st.sc-cdn.net/d/eHfqR7qRY9kuVjZbupqN4.410.IRZXSOY?mo=GkAaFjIBBDoBfUIGCP25qdAGSAJQXmABcAFQxQFaEERmTGFyZ2VUaHVtYm5haWyiARAImgMiCxIAKgdJUlpYU09Z&uc=94",
            "timestampInSec": 1779061852,
            "publishedAt": "2026-05-17T23:50:52Z"
          }
        ]
      }
    ],
    "spotlightHighlights": [
      {
        "id": "W7_EDlXWTBiXAEEniNoMPwAAYZ214b2ZqdWhiAZ-_WJm3AZ-_WHoaAAAAAQ",
        "title": "Spotlight Snap",
        "description": "Another Spotlight Snap brought to you by Snapchat",
        "thumbnailUrl": "https://cf-st.sc-cdn.net/d/Qmm68dwXUXh0Rk6RHsywT.256.IRZXSOY?mo=GkYaCTIBBEgCUC5gAVCgAVoQRGZMYXJnZVRodW1ibmFpbKIBEAiAAiILEgAqB0lSWlhTT1miARAImgoiCxIAKgdJUlpYU09Z&uc=46",
        "contentUrl": "https://cf-st.sc-cdn.net/d/Qmm68dwXUXh0Rk6RHsywT.27.IRZXSOY?mo=Gl8aCTIBBEgCUC5gAVCiAVoQU3BvdGxpZ2h0U2hhcmluZ6IBNwgbEiYKJAjP-XQgATCcBDjAB0ABSg4KCVgeHCgsJis0LxD0A1DirgFoAiILEgAqB0lSWlhTT1mQA-KuAQ%3D%3D&uc=46",
        "durationMs": 22370,
        "width": 540,
        "height": 960,
        "uploadDateMs": 1785621674522,
        "publishedAt": "2026-08-01T22:01:14.522000Z",
        "deeplink": "https://click.snapchat.com/aVHG?pid=snapchat_download_page&af_dp=https://www.snapchat.com/spotlight/W7_EDlXWTBiXAEEniNoMPwAAYZ214b2ZqdWhiAZ-_WJm3AZ-_WHoaAAAAAQ&af_web_dp=https://snapchat.com/download?purpose%3Dweb_stories%26sp%3Dspotlight&af_ios_url=https://apps.apple.com/app/apple-store/id447188370?pt%3D614006%26ct%3Dspotlight%26mt%3D8",
        "creator": {
          "username": "nba",
          "displayName": "NBA",
          "url": "https://www.snapchat.com/@nba"
        },
        "engagement": {
          "views": 20844,
          "shares": 21,
          "comments": 37,
          "boosts": 1618,
          "recommends": 108
        },
        "snapList": [
          {
            "snapIndex": 0,
            "snapId": "W7_EDlXWTBiXAEEniNoMPwAAYZ214b2ZqdWhiAZ-_WJm3AZ-_WHoaAAAAAQ",
            "snapMediaType": 1,
            "mediaType": "video",
            "mediaUrl": "https://cf-st.sc-cdn.net/d/Qmm68dwXUXh0Rk6RHsywT.27.IRZXSOY?mo=Gl8aCTIBBEgCUC5gAVCiAVoQU3BvdGxpZ2h0U2hhcmluZ6IBNwgbEiYKJAjP-XQgATCcBDjAB0ABSg4KCVgeHCgsJis0LxD0A1DirgFoAiILEgAqB0lSWlhTT1mQA-KuAQ%3D%3D&uc=46",
            "mediaPreviewUrl": "https://cf-st.sc-cdn.net/d/Qmm68dwXUXh0Rk6RHsywT.256.IRZXSOY?mo=GkYaCTIBBEgCUC5gAVCgAVoQRGZMYXJnZVRodW1ibmFpbKIBEAiAAiILEgAqB0lSWlhTT1miARAImgoiCxIAKgdJUlpYU09Z&uc=46",
            "timestampInSec": 1785621674,
            "publishedAt": "2026-08-01T22:01:14Z"
          }
        ]
      },
      {
        "id": "W7_EDlXWTBiXAEEniNoMPwAAYcm95aXJwZW1tAZ-_U_PhAZ-_U8m2AAAAAQ",
        "title": "Spotlight Snap",
        "description": "Another Spotlight Snap brought to you by Snapchat",
        "thumbnailUrl": "https://cf-st.sc-cdn.net/d/pnucYwUhWRai63fD72ieX.256.IRZXSOY?mo=GkYaCTIBBEgCUC5gAVCgAVoQRGZMYXJnZVRodW1ibmFpbKIBEAiAAiILEgAqB0lSWlhTT1miARAImgoiCxIAKgdJUlpYU09Z&uc=46",
        "contentUrl": "https://cf-st.sc-cdn.net/d/pnucYwUhWRai63fD72ieX.27.IRZXSOY?mo=GmAaCTIBBEgCUC5gAVCiAVoQU3BvdGxpZ2h0U2hhcmluZ6IBOAgbEicKJQieqbECIAEwnAQ4wAdAAUoOCglqLFtrV1FcVE8Q9ANQqskBaAIiCxIAKgdJUlpYU09ZkAOqyQE%3D&uc=46",
        "durationMs": 25770,
        "width": 540,
        "height": 960,
        "uploadDateMs": 1785621367222,
        "publishedAt": "2026-08-01T21:56:07.222000Z",
        "deeplink": "https://click.snapchat.com/aVHG?pid=snapchat_download_page&af_dp=https://www.snapchat.com/spotlight/W7_EDlXWTBiXAEEniNoMPwAAYcm95aXJwZW1tAZ-_U_PhAZ-_U8m2AAAAAQ&af_web_dp=https://snapchat.com/download?purpose%3Dweb_stories%26sp%3Dspotlight&af_ios_url=https://apps.apple.com/app/apple-store/id447188370?pt%3D614006%26ct%3Dspotlight%26mt%3D8",
        "creator": {
          "username": "nba",
          "displayName": "NBA",
          "url": "https://www.snapchat.com/@nba"
        },
        "engagement": {
          "views": 10051,
          "shares": 3,
          "comments": 4,
          "boosts": 533,
          "recommends": 33
        },
        "snapList": [
          {
            "snapIndex": 0,
            "snapId": "W7_EDlXWTBiXAEEniNoMPwAAYcm95aXJwZW1tAZ-_U_PhAZ-_U8m2AAAAAQ",
            "snapMediaType": 1,
            "mediaType": "video",
            "mediaUrl": "https://cf-st.sc-cdn.net/d/pnucYwUhWRai63fD72ieX.27.IRZXSOY?mo=GmAaCTIBBEgCUC5gAVCiAVoQU3BvdGxpZ2h0U2hhcmluZ6IBOAgbEicKJQieqbECIAEwnAQ4wAdAAUoOCglqLFtrV1FcVE8Q9ANQqskBaAIiCxIAKgdJUlpYU09ZkAOqyQE%3D&uc=46",
            "mediaPreviewUrl": "https://cf-st.sc-cdn.net/d/pnucYwUhWRai63fD72ieX.256.IRZXSOY?mo=GkYaCTIBBEgCUC5gAVCgAVoQRGZMYXJnZVRodW1ibmFpbKIBEAiAAiILEgAqB0lSWlhTT1miARAImgoiCxIAKgdJUlpYU09Z&uc=46",
            "timestampInSec": 1785621367,
            "publishedAt": "2026-08-01T21:56:07Z"
          }
        ]
      }
    ],
    "relatedAccounts": [
      {
        "username": "warriors",
        "displayName": "Golden State Warriors",
        "url": "https://www.snapchat.com/@warriors",
        "avatar": "https://cf-st.sc-cdn.net/aps/bolt/aHR0cHM6Ly9jZi1zdC5zYy1jZG4ubmV0L2QvNjRqVjdIRlJMaHk1V21yS0MwNUZ2P2JvPUVnMGFBQm9BTWdFRVNBSlFHV0FCJnVjPTI1._RS0,640_FMjpeg",
        "profileUrl": "https://www.snapchat.com/@warriors",
        "profilePictureUrl": "https://cf-st.sc-cdn.net/aps/bolt/aHR0cHM6Ly9jZi1zdC5zYy1jZG4ubmV0L2QvNjRqVjdIRlJMaHk1V21yS0MwNUZ2P2JvPUVnMGFBQm9BTWdFRVNBSlFHV0FCJnVjPTI1._RS0,640_FMjpeg",
        "verified": true,
        "isVerified": true,
        "hasStory": true,
        "hasCuratedHighlights": false,
        "hasSpotlightHighlights": false,
        "subscribeLink": {
          "oneLinkBaseUrl": "https://click.snapchat.com/aVHG",
          "deepLinkUrl": "https://www.snapchat.com/@warriors",
          "iosAppStoreUrl": "https://apps.apple.com/app/apple-store/id447188370?pt=614006&ct=add_user&mt=8"
        }
      },
      {
        "username": "nfl",
        "displayName": "NFL Official",
        "url": "https://www.snapchat.com/@nfl",
        "avatar": "https://cf-st.sc-cdn.net/aps/bolt/aHR0cHM6Ly9jZi1zdC5zYy1jZG4ubmV0L2QvT3NjakFOS0dwSWh1VzQwek9qRnowP2JvPUVnMGFBQm9BTWdFRVNBSlFHV0FCJnVjPTI1._RS0,640_FMjpeg",
        "profileUrl": "https://www.snapchat.com/@nfl",
        "profilePictureUrl": "https://cf-st.sc-cdn.net/aps/bolt/aHR0cHM6Ly9jZi1zdC5zYy1jZG4ubmV0L2QvT3NjakFOS0dwSWh1VzQwek9qRnowP2JvPUVnMGFBQm9BTWdFRVNBSlFHV0FCJnVjPTI1._RS0,640_FMjpeg",
        "verified": true,
        "isVerified": true,
        "hasStory": true,
        "hasCuratedHighlights": false,
        "hasSpotlightHighlights": false,
        "subscribeLink": {
          "oneLinkBaseUrl": "https://click.snapchat.com/aVHG",
          "deepLinkUrl": "https://www.snapchat.com/@nfl",
          "iosAppStoreUrl": "https://apps.apple.com/app/apple-store/id447188370?pt=614006&ct=add_user&mt=8"
        }
      }
    ]
  },
  "soundcloud-artist": {
    "platform": "soundcloud",
    "id": "2976616",
    "handle": "flume",
    "url": "https://soundcloud.com/flume",
    "username": "Flume",
    "name": "Flume",
    "description": "Management: flume@threesixzero.com",
    "avatar": "https://i1.sndcdn.com/avatars-sAZPcKyZpXJ0J0u5-JHfNSg-large.jpg",
    "city": "Sydney",
    "countryCode": "AU",
    "verified": true,
    "subscriptionTier": "pro-unlimited",
    "followers": 2227731,
    "followings": 203,
    "trackCount": 412,
    "playlistCount": 46,
    "likesCount": 149,
    "lastModified": "2026-02-13T20:55:02Z",
    "externalLinks": [
      {
        "url": "https://dumb.store/",
        "network": "personal",
        "title": "DUMB Store"
      },
      {
        "url": "http://www.facebook.com/flumemusic",
        "network": "facebook",
        "title": "Facebook",
        "username": "flumemusic"
      }
    ]
  },
  "soundcloud-artist-tracks": {
    "platform": "soundcloud",
    "artistId": "112904040",
    "artistUrl": "https://soundcloud.com/nasa",
    "artist": {
      "id": "112904040",
      "handle": "nasa",
      "name": "NASA",
      "url": "https://soundcloud.com/nasa",
      "avatar": "https://i1.sndcdn.com/avatars-JUvAAPvAA86fmbVE-SH0i6g-large.jpg",
      "followers": 158701,
      "verified": true
    },
    "totalReturned": 5,
    "nextCursor": "eyJ1IjoiMTEyOTA0MDQwIiwibyI6IjIwMjYtMDctMTNUMTM6MjU6MzIuMDAwWix0cmFja3MsMDAwMDAwMDAwMDIzNTk2NjI1NDgifQ",
    "hasMore": true,
    "tracks": [
      {
        "platform": "soundcloud",
        "id": "2367219119",
        "url": "https://soundcloud.com/nasa/houston-we-have-a-podcast-iss-results-materials-science",
        "title": "Houston We Have a Podcast: ISS Results: Materials Science",
        "description": "On episode 430, Kim de Groh and Sylvie Crowell review what researchers have learned and published from the Materials International Space Station Experiment (MISSE) platform that tests how materials perform in the harsh environment of space.",
        "genre": "Science",
        "durationMs": 2928970,
        "plays": 129,
        "likes": 5,
        "reposts": 2,
        "downloads": 0,
        "comments": 2,
        "publishedAt": "2026-07-24T14:22:31Z",
        "license": "all-rights-reserved",
        "downloadable": true,
        "streamable": true,
        "waveformUrl": "https://wave.sndcdn.com/lDzXvlHMrahi_m.json",
        "artwork": "https://i1.sndcdn.com/artworks-yGpNDB5MzaAUMCB2-e6NVdg-large.jpg",
        "tags": [
          "johnson",
          "space"
        ]
      },
      {
        "platform": "soundcloud",
        "id": "2364347957",
        "url": "https://soundcloud.com/nasa/artemis-ii-el-regreso-de-la-1",
        "title": "Artemis II: El regreso de la humanidad a la Luna",
        "description": "Acompáñanos en esta edición especial de Universo curioso de la NASA mientras hacemos un recorrido por la misión Artemis II de principio a fin. Revivimos la expectación en los días previos al despegue, la potencia del histórico lanzamiento y el increíble viaje de la tripu-lación a través del espacio profundo. Exploramos los momentos más críticos de la misión —desde el emocionante sobrevuelo lunar hasta el exitoso amerizaje en el océano Pacífi-co— que completa un capítulo fundamental en esta nueva era de la exploración espacial.\nEncuentra más información sobre Artemis en: ciencia.nasa.gov/artemis",
        "genre": "Science",
        "durationMs": 3026998,
        "plays": 184,
        "likes": 4,
        "reposts": 2,
        "downloads": 0,
        "comments": 6,
        "publishedAt": "2026-07-20T14:01:49Z",
        "license": "all-rights-reserved",
        "downloadable": true,
        "streamable": true,
        "waveformUrl": "https://wave.sndcdn.com/4hOvfT5B6ZYH_m.json",
        "artwork": "https://i1.sndcdn.com/artworks-vHT95zmztFEO1K49-1BXSXA-large.jpg",
        "tags": [
          "nasa",
          "podcast"
        ]
      }
    ]
  },
  "soundcloud-track": {
    "platform": "soundcloud",
    "id": "2375655854",
    "url": "https://soundcloud.com/nasa/episode-179-life-support",
    "title": "Episode 179: Life Support Systems: From Space Station to Orion",
    "description": "Astronauts aboard the International Space Station depend on life support systems that provide clean air, drinkable water, and a safe, livable environment. These systems are what make long-duration spaceflight not only possible, but comfortable. Today, some of these space station technologies have been adapted for Artemis – specifically, aboard the Orion crew capsule.",
    "genre": "Science",
    "artist": {
      "id": "112904040",
      "handle": "nasa",
      "name": "NASA",
      "url": "https://soundcloud.com/nasa",
      "avatar": "https://i1.sndcdn.com/avatars-JUvAAPvAA86fmbVE-SH0i6g-large.jpg",
      "followers": 158759,
      "verified": true
    },
    "durationMs": 874406,
    "plays": 5,
    "likes": 1,
    "reposts": 1,
    "downloads": 0,
    "comments": 1,
    "publishedAt": "2026-08-05T18:24:11Z",
    "license": "all-rights-reserved",
    "downloadable": true,
    "streamable": true,
    "streamUrl": "https://cf-media.sndcdn.com/MLL2GDHPueMc.128.mp3?Policy=eyJTdGF0ZW1lbnQiOlt7IlJlc291cmNlIjoiKjovL2NmLW1lZGlhLnNuZGNkbi5jb20vTUxMMkdESFB1ZU1jLjEyOC5tcDMqIiwiQ29uZGl0aW9uIjp7IkRhdGVMZXNzVGhhbiI6eyJBV1M6RXBvY2hUaW1lIjoxNzg1OTU3Nzg2fX19XX0_&Signature=cDzjtDOmAvn41PNIb-9dZXQqVIjgHARvK8PmwgfhXmVSEbdg~gbLsrO82AqhNl7RuMv2eq3q8wqNJc3cF0SPuKa9dXGAgWgiS3Y~ZP-3C9sj0rS5I0gddBCWF8WVmhAAT7m7a87wqSO-mj3XTacfaheJUBYJHQ6o6tmJLbNbh6fEdsj2zW58wYijWCjCzRHi~Y0ujYsQYVvZmiXymnOk3mk-3jh7ifyF70nSD5Hlm6vkyqRAcYujX0~8TqBsYHN9E55Nk3L2rHy1eypM5z9HttWPIq8hC5ahCM9adro8kEobAvjPpvdAbSB7mXXGYoK4KXnhDt24Ca9Bkjn484Z6sg__&Key-Pair-Id=APKAI6TU7MMXM5DG6EPQ",
    "hlsUrl": "https://playback.media-streaming.soundcloud.cloud/MLL2GDHPueMc/aac_160k/a6f11843-eb03-4d7e-9f3a-897e58367925/playlist.m3u8?expires=1785964866&Policy=eyJTdGF0ZW1lbnQiOlt7IlJlc291cmNlIjoiaHR0cHM6Ly9wbGF5YmFjay5tZWRpYS1zdHJlYW1pbmcuc291bmRjbG91ZC5jbG91ZC9NTEwyR0RIUHVlTWMvYWFjXzE2MGsvYTZmMTE4NDMtZWIwMy00ZDdlLTlmM2EtODk3ZTU4MzY3OTI1L3BsYXlsaXN0Lm0zdTg~ZXhwaXJlcz0xNzg1OTY0ODY2IiwiQ29uZGl0aW9uIjp7IkRhdGVMZXNzVGhhbiI6eyJBV1M6RXBvY2hUaW1lIjoxNzg1OTU3Nzg2fX19XX0_&Signature=i6dAnRPDDEm5WfkvqguSogWUxP2n8U4q6Vwlclblq5hYBR4ZxWPtbIggHHTWbYXVokqgWoDeRxOqw811Bysb3HYs~3b8CZh2elLsSbloWWWxONdROYQf9xTUYmBR1SbIlsQj7z1VvNM~5KsEfIECVzCY-gF8I6F4p5P06sqQv9cDZ3-Wdq~WdAWkKsVzispfStxoG8glXS4~iceC8AHTCW8wrLOa0MZJ9mItuAw5QVQmw47X1V3OVVC1V1nuMi-owF5BN5yLrA7rCQtk8R0ucpfZILSn2gTyaNtZsi4uKdRFfa1X-Y6~hdjxdDO6ixtN~6iYDCk7hJgcjHBRHiLoQg__&Key-Pair-Id=K34606QXLEIRF3",
    "mediaUrlsExpireAt": "2026-08-05T21:21:06Z",
    "waveformUrl": "https://wave.sndcdn.com/MLL2GDHPueMc_m.json",
    "artwork": "https://i1.sndcdn.com/artworks-P4yXCelBLW8JxnUB-SPPJRA-large.jpg",
    "tags": [
      "nasa",
      "podcast"
    ]
  },
  "spotify-album": {
    "platform": "spotify",
    "type": "album",
    "uri": "spotify:album:151w1FgRZfnKZA9FEcg9Z3",
    "url": "https://open.spotify.com/album/151w1FgRZfnKZA9FEcg9Z3?si=DKhdQPU7T8W1NtfM19TiiA",
    "name": "Midnights",
    "artists": [
      {
        "id": "06HL4z0CvFAxyc27GXpf02",
        "uri": "spotify:artist:06HL4z0CvFAxyc27GXpf02",
        "name": "Taylor Swift",
        "url": "https://open.spotify.com/artist/06HL4z0CvFAxyc27GXpf02"
      }
    ],
    "releaseYear": 2022,
    "image": "https://i.scdn.co/image/ab67616d0000b273bb54dde68cd23e2a268ae0f5",
    "totalTracks": 13,
    "tracks": [
      {
        "trackNumber": 1,
        "discNumber": 1,
        "name": "Lavender Haze",
        "uri": "spotify:track:5jQI2r1RdgtuT8S3iG8zFC",
        "url": "https://open.spotify.com/track/5jQI2r1RdgtuT8S3iG8zFC",
        "durationMs": 202395,
        "playCount": 902202241,
        "explicit": true,
        "artists": [
          {
            "id": "06HL4z0CvFAxyc27GXpf02",
            "uri": "spotify:artist:06HL4z0CvFAxyc27GXpf02",
            "name": "Taylor Swift",
            "url": "https://open.spotify.com/artist/06HL4z0CvFAxyc27GXpf02"
          }
        ]
      },
      {
        "trackNumber": 2,
        "discNumber": 1,
        "name": "Maroon",
        "uri": "spotify:track:3eX0NZfLtGzoLUxPNvRfqm",
        "url": "https://open.spotify.com/track/3eX0NZfLtGzoLUxPNvRfqm",
        "durationMs": 218270,
        "playCount": 627635994,
        "explicit": true,
        "artists": [
          {
            "id": "06HL4z0CvFAxyc27GXpf02",
            "uri": "spotify:artist:06HL4z0CvFAxyc27GXpf02",
            "name": "Taylor Swift",
            "url": "https://open.spotify.com/artist/06HL4z0CvFAxyc27GXpf02"
          }
        ]
      }
    ],
    "tracksHasMore": false,
    "releaseDate": "2022-10-21T00:00:00Z",
    "explicit": true,
    "id": "151w1FgRZfnKZA9FEcg9Z3"
  },
  "spotify-artist": {
    "platform": "spotify",
    "type": "artist",
    "uri": "spotify:artist:06HL4z0CvFAxyc27GXpf02",
    "url": "https://open.spotify.com/artist/06HL4z0CvFAxyc27GXpf02?si=ojAujUioTXmCOg3l0f4rNg",
    "name": "Taylor Swift",
    "description": "And, baby, that’s show business for you. New album The Life of a Showgirl. Available now ❤️‍🔥",
    "followers": 161871951,
    "monthlyListeners": 100784802,
    "image": "https://i.scdn.co/image/ab6761610000e5ebe2e8e7ff002a4afda1c7147e",
    "worldRank": 6,
    "topCities": [
      {
        "city": "London",
        "country": "GB",
        "region": "ENG",
        "listeners": 1612075
      },
      {
        "city": "Quezon City",
        "country": "PH",
        "region": "00",
        "listeners": 1256007
      }
    ],
    "externalLinks": [
      {
        "name": "FACEBOOK",
        "url": "https://facebook.com/TaylorSwift"
      },
      {
        "name": "INSTAGRAM",
        "url": "https://instagram.com/taylorswift"
      }
    ],
    "verified": true,
    "topTracks": [
      {
        "name": "The Fate of Ophelia",
        "uri": "spotify:track:53iuhJlwXhSER5J2IYYv1W",
        "url": "https://open.spotify.com/track/53iuhJlwXhSER5J2IYYv1W",
        "playCount": 1571637645,
        "durationMs": 226073,
        "albumUri": "spotify:album:4a6NzYL1YHRUgx9e3YZI6I",
        "image": "https://i.scdn.co/image/ab67616d0000b273d7812467811a7da6e6a44902",
        "explicit": false
      },
      {
        "name": "I Knew It, I Knew You - From \"Toy Story 5\"",
        "uri": "spotify:track:5uPaqMMt59KGrdKIitDRqa",
        "url": "https://open.spotify.com/track/5uPaqMMt59KGrdKIitDRqa",
        "playCount": 137089953,
        "durationMs": 178186,
        "albumUri": "spotify:album:3ZLIShtR6Fjs4nTWFpBUB6",
        "image": "https://i.scdn.co/image/ab67616d0000b273a35a1d4983e2b4fd0094f910",
        "explicit": false
      }
    ],
    "concerts": [],
    "relatedArtists": [
      {
        "name": "Sabrina Carpenter",
        "uri": "spotify:artist:74KM79TiuVKeVCqs8QtB0B",
        "url": "https://open.spotify.com/artist/74KM79TiuVKeVCqs8QtB0B",
        "image": "https://i.scdn.co/image/ab6761610000e5eb78e45cfa4697ce3c437cb455"
      },
      {
        "name": "Ariana Grande",
        "uri": "spotify:artist:66CXWjxzNUsdJxJ2JdwvnR",
        "url": "https://open.spotify.com/artist/66CXWjxzNUsdJxJ2JdwvnR",
        "image": "https://i.scdn.co/image/ab6761610000e5eb766397ec42a573a53eb5fb87"
      }
    ],
    "albums": [
      {
        "name": "The Life of a Showgirl + Acoustic Collection",
        "uri": "spotify:album:6QNMhoV8V0u7cFuhhUBOn7",
        "url": "https://open.spotify.com/album/6QNMhoV8V0u7cFuhhUBOn7",
        "image": "https://i.scdn.co/image/ab67616d0000b273f756bdc2c11a985dc0c06d94",
        "releaseYear": 2025,
        "totalTracks": 19
      },
      {
        "name": "The Life of a Showgirl",
        "uri": "spotify:album:4a6NzYL1YHRUgx9e3YZI6I",
        "url": "https://open.spotify.com/album/4a6NzYL1YHRUgx9e3YZI6I",
        "image": "https://i.scdn.co/image/ab67616d0000b273d7812467811a7da6e6a44902",
        "releaseYear": 2025,
        "totalTracks": 12
      }
    ],
    "singles": [
      {
        "name": "I Knew It, I Knew You (From \"Toy Story 5\")",
        "uri": "spotify:album:4Ii9whWXI1O1H01ziECRaG",
        "url": "https://open.spotify.com/album/4Ii9whWXI1O1H01ziECRaG",
        "image": "https://i.scdn.co/image/ab67616d0000b273e8852f06eca817333d20e60b",
        "releaseYear": 2026,
        "totalTracks": 3
      },
      {
        "name": "Elizabeth Taylor",
        "uri": "spotify:album:71GTik4z9bbKKY2EmUvkDI",
        "url": "https://open.spotify.com/album/71GTik4z9bbKKY2EmUvkDI",
        "image": "https://i.scdn.co/image/ab67616d0000b273dc6e4c7774e0c77c210d3a31",
        "releaseYear": 2026,
        "totalTracks": 3
      }
    ],
    "albumsCount": 33,
    "singlesCount": 79,
    "albumsHasMore": true,
    "singlesHasMore": true,
    "id": "06HL4z0CvFAxyc27GXpf02"
  },
  "spotify-podcast": {
    "platform": "spotify",
    "type": "podcast",
    "uri": "spotify:show:4rOoJ6Egrf8K2IrywzwOMk",
    "url": "https://open.spotify.com/show/4rOoJ6Egrf8K2IrywzwOMk",
    "name": "The Joe Rogan Experience",
    "description": "The official podcast of comedian Joe Rogan.",
    "image": "https://i.scdn.co/image/ab6765630000ba8a913317cdfae64a2585aa0f36",
    "totalEpisodes": 2731,
    "id": "4rOoJ6Egrf8K2IrywzwOMk",
    "publisher": {
      "name": "Joe Rogan"
    },
    "rating": {
      "average": 4.6556989281194445,
      "totalRatings": 952065
    },
    "topics": [
      {
        "title": "Comedy",
        "uri": "spotify:genre:0JQ5DAqbMKFNr6gDrHHVKL"
      }
    ],
    "contentRating": "EXPLICIT",
    "contentRatingLabels": [
      "EXPLICIT"
    ],
    "explicit": true,
    "mediaType": "MIXED",
    "htmlDescription": "<p>The official podcast of comedian Joe Rogan.</p>",
    "playable": true,
    "consumptionOrder": "EPISODIC",
    "showTypes": [
      "SHOW_TYPE_EXCLUSIVE"
    ]
  },
  "spotify-podcast-episodes": {
    "platform": "spotify",
    "podcast": {
      "platform": "spotify",
      "type": "podcast",
      "uri": "spotify:show:4rOoJ6Egrf8K2IrywzwOMk",
      "url": "https://open.spotify.com/show/4rOoJ6Egrf8K2IrywzwOMk",
      "name": "The Joe Rogan Experience",
      "description": "The official podcast of comedian Joe Rogan.",
      "image": "https://i.scdn.co/image/ab6765630000ba8a913317cdfae64a2585aa0f36",
      "totalEpisodes": 2731,
      "id": "4rOoJ6Egrf8K2IrywzwOMk",
      "publisher": {
        "name": "Joe Rogan"
      },
      "rating": {
        "average": 4.6556989281194445,
        "totalRatings": 952065
      },
      "topics": [
        {
          "title": "Comedy",
          "uri": "spotify:genre:0JQ5DAqbMKFNr6gDrHHVKL"
        }
      ],
      "contentRating": "EXPLICIT",
      "contentRatingLabels": [
        "EXPLICIT"
      ],
      "explicit": true,
      "mediaType": "MIXED",
      "htmlDescription": "<p>The official podcast of comedian Joe Rogan.</p>",
      "playable": true,
      "consumptionOrder": "EPISODIC",
      "showTypes": [
        "SHOW_TYPE_EXCLUSIVE"
      ]
    },
    "totalEpisodes": 2731,
    "totalReturned": 5,
    "episodes": [
      {
        "platform": "spotify",
        "type": "episode",
        "uri": "spotify:episode:6sriD1voEkINLnr08M9nmw",
        "url": "https://open.spotify.com/episode/6sriD1voEkINLnr08M9nmw",
        "name": "#2535 - Andrew Wilson",
        "description": "Andrew Wilson has participated in thousands of debates on political, cultural, and religious topics. He hosts \"The Crucible\" and owns its associated online training program, Debate University.www.youtube.com/@The_Crucible  www.rumble.com/c/TheCrucible  www.thecrucible.video  www.debateuniversity.com  Perplexity: Download the app or ask Perplexity anything at https://pplx.ai/rogan.  Use code ROGAN at https://BlueChew.com to get 10% OFF + Free Overnight Shipping on your first order. Learn more about your ad choices. Visit podcastchoices.com/adchoices",
        "durationMs": 10072297,
        "durationFormatted": "2:47:52",
        "releaseYear": 2026,
        "image": "https://i.scdn.co/image/ab6765630000ba8adfec1dc1162dd326137b168e",
        "id": "6sriD1voEkINLnr08M9nmw",
        "previewUrl": "https://p.scdn.co/mp3-preview/df88d8d9a774747ca6dd4eb64f71a0984cf8760a.mp3",
        "audioUrls": [
          "https://p.scdn.co/mp3-preview/04e810abec582425b173ac15187820cb5f534e0b",
          "https://p.scdn.co/mp3-preview/582677c5c09f2020c744a5278f3748a069abbe1a"
        ],
        "releaseDate": "2026-08-05T17:00:00Z",
        "mediaTypes": [
          "AUDIO",
          "VIDEO"
        ],
        "hasVideo": true,
        "contentRating": "EXPLICIT",
        "explicit": true,
        "hasTranscripts": false,
        "paywallContent": false,
        "showTypes": [
          "SHOW_TYPE_EXCLUSIVE"
        ],
        "playable": true,
        "htmlDescription": "<p>Andrew Wilson has participated in thousands of debates on political, cultural, and religious topics. He hosts \"The Crucible\" and owns its associated online training program, Debate University.<br />www.youtube.com/@The_Crucible  <br />www.rumble.com/c/TheCrucible  <br /><a href=\"www.thecrucible.video\" rel=\"nofollow\">www.thecrucible.video</a>  <br />www.debateuniversity.com</p><br/><p><br /></p><br/><p>Perplexity: Download the app or ask Perplexity anything at <a href=\"https://pplx.ai/rogan\" rel=\"nofollow\">https://pplx.ai/rogan</a>.</p><br/><p><br /></p><br/><p>Use code ROGAN at <a href=\"https://BlueChew.com\" rel=\"nofollow\">https://BlueChew.com</a> to get 10% OFF + Free Overnight Shipping on your first order.</p><p> </p><p>Learn more about your ad choices. Visit <a href=\"https://podcastchoices.com/adchoices\" rel=\"nofollow\">podcastchoices.com/adchoices</a></p>"
      },
      {
        "platform": "spotify",
        "type": "episode",
        "uri": "spotify:episode:12sZKqXfCxdOci06HGV7vf",
        "url": "https://open.spotify.com/episode/12sZKqXfCxdOci06HGV7vf",
        "name": "JRE MMA Show #183 with Rico Verhoeven",
        "description": "Joe sits down with professional boxer, kickboxer, and mixed martial artist Rico Verhoeven.www.youtube.com/@RicoVerhoeven  https://ricoverhoeven.com      Learn more about your ad choices. Visit podcastchoices.com/adchoices",
        "durationMs": 8232297,
        "durationFormatted": "2:17:12",
        "releaseYear": 2026,
        "image": "https://i.scdn.co/image/ab6765630000ba8a7cec0dc10cb879778e8a6246",
        "id": "12sZKqXfCxdOci06HGV7vf",
        "previewUrl": "https://p.scdn.co/mp3-preview/862ca22fba9863c7b3b9476ae3fa75efb7e54247.mp3",
        "audioUrls": [
          "https://p.scdn.co/mp3-preview/8ccd9b3ce42a7c28545b2566d145b0810f853ab5",
          "https://p.scdn.co/mp3-preview/bd8fd704118106c2987f86498bf19a90f06afb94"
        ],
        "releaseDate": "2026-08-04T17:00:00Z",
        "mediaTypes": [
          "AUDIO",
          "VIDEO"
        ],
        "hasVideo": true,
        "contentRating": "EXPLICIT",
        "explicit": true,
        "hasTranscripts": false,
        "paywallContent": false,
        "showTypes": [
          "SHOW_TYPE_EXCLUSIVE"
        ],
        "playable": true,
        "htmlDescription": "<p>Joe sits down with professional boxer, kickboxer, and mixed martial artist Rico Verhoeven.<br />www.youtube.com/@RicoVerhoeven  <br /><a href=\"https://ricoverhoeven.com/\" rel=\"nofollow\">https://ricoverhoeven.com</a><br /></p><br/><p><br /><a href=\"https://pplx.ai/rogan\" rel=\"nofollow\"><br /></a><br /></p><br/><p><br /></p><br/><p><br /><a href=\"https://squarespace.com/ROGAN\" rel=\"nofollow\"><br /></a><br /></p><br/><p><br /></p><br/><p><br /><a href=\"https://BetterHelp.com/JRE\" rel=\"nofollow\"><br /></a></p><p> </p><p>Learn more about your ad choices. Visit <a href=\"https://podcastchoices.com/adchoices\" rel=\"nofollow\">podcastchoices.com/adchoices</a></p>"
      }
    ],
    "nextCursor": "5",
    "hasMore": true
  },
  "spotify-search": {
    "platform": "spotify",
    "query": "lofi beats",
    "type": "tracks",
    "fetchedAt": "2026-08-07T10:56:53.985Z",
    "source": "pathfinder",
    "totalReturned": 5,
    "results": [
      {
        "platform": "spotify",
        "type": "track",
        "uri": "spotify:track:1xqpCUhTXEG3Zj7E6VEyj4",
        "url": "https://open.spotify.com/track/1xqpCUhTXEG3Zj7E6VEyj4",
        "name": "Lodi Dodi",
        "artists": [
          {
            "id": "7hJcb9fa4alzcOq3EaNPoG",
            "uri": "spotify:artist:7hJcb9fa4alzcOq3EaNPoG",
            "name": "Snoop Dogg",
            "url": "https://open.spotify.com/artist/7hJcb9fa4alzcOq3EaNPoG"
          }
        ],
        "album": {
          "id": "0iXJO2ZAfKzNDYa6E4EFfl",
          "uri": "spotify:album:0iXJO2ZAfKzNDYa6E4EFfl",
          "name": "Death Row Greatest Hits",
          "url": "https://open.spotify.com/album/0iXJO2ZAfKzNDYa6E4EFfl"
        },
        "durationMs": 264480,
        "durationFormatted": "4:24",
        "image": "https://i.scdn.co/image/ab67616d0000b2739322ff440b23b5717ddd8c9b",
        "id": "1xqpCUhTXEG3Zj7E6VEyj4",
        "contentRating": "EXPLICIT",
        "explicit": true
      },
      {
        "platform": "spotify",
        "type": "track",
        "uri": "spotify:track:5SFVfPQNHzrsVjO2YmOl7u",
        "url": "https://open.spotify.com/track/5SFVfPQNHzrsVjO2YmOl7u",
        "name": "Lofi Beats",
        "artists": [
          {
            "id": "0uXJZ5oJisbrkihiMUDiya",
            "uri": "spotify:artist:0uXJZ5oJisbrkihiMUDiya",
            "name": "Productivity Booster Music",
            "url": "https://open.spotify.com/artist/0uXJZ5oJisbrkihiMUDiya"
          }
        ],
        "album": {
          "id": "7D6QtZp3B4UAjd9J8hzjS2",
          "uri": "spotify:album:7D6QtZp3B4UAjd9J8hzjS2",
          "name": "All-Day Flow: Lo-Fi Beats for Creative Work",
          "url": "https://open.spotify.com/album/7D6QtZp3B4UAjd9J8hzjS2"
        },
        "durationMs": 158000,
        "durationFormatted": "2:38",
        "image": "https://i.scdn.co/image/ab67616d0000b27356f94cadfab4bf5902a8f30c",
        "id": "5SFVfPQNHzrsVjO2YmOl7u",
        "contentRating": "NONE",
        "explicit": false
      }
    ]
  },
  "spotify-track": {
    "platform": "spotify",
    "type": "track",
    "uri": "spotify:track:0V3wPSX9ygBnCm8psDIegu",
    "url": "https://open.spotify.com/track/0V3wPSX9ygBnCm8psDIegu",
    "name": "Anti-Hero",
    "artists": [
      {
        "id": "06HL4z0CvFAxyc27GXpf02",
        "uri": "spotify:artist:06HL4z0CvFAxyc27GXpf02",
        "name": "Taylor Swift",
        "url": "https://open.spotify.com/artist/06HL4z0CvFAxyc27GXpf02"
      }
    ],
    "album": {
      "id": "151w1FgRZfnKZA9FEcg9Z3",
      "uri": "spotify:album:151w1FgRZfnKZA9FEcg9Z3",
      "name": "Midnights",
      "url": "https://open.spotify.com/album/151w1FgRZfnKZA9FEcg9Z3",
      "releaseDate": "2022-10-21T00:00:00Z"
    },
    "durationMs": 200690,
    "durationFormatted": "3:20",
    "releaseYear": 2022,
    "image": "https://i.scdn.co/image/ab67616d0000b273bb54dde68cd23e2a268ae0f5",
    "id": "0V3wPSX9ygBnCm8psDIegu",
    "playCount": 2037355549,
    "trackNumber": 3,
    "contentRating": "NONE",
    "explicit": false,
    "mediaType": "AUDIO",
    "playable": true,
    "releaseDate": "2022-10-21T00:00:00Z"
  },
  "threads-post-details": {
    "platform": "threads",
    "id": "3925863854786722836",
    "code": "DZ7eGA1G7wU",
    "url": "https://www.threads.net/@zuck/post/DZ7eGA1G7wU",
    "text": "Our new line of @metaglasses is available today. Three shapes, 26 style combos, with our most advanced Meta AI built in. Plus, three custom styles designed by @kyliejenner.",
    "publishedAt": "2026-06-23T12:57:42.000Z",
    "threadId": "3925863854786722836",
    "replyToId": null,
    "quoteId": null,
    "isReply": false,
    "isQuote": false,
    "author": {
      "username": "zuck",
      "displayName": "Mark Zuckerberg",
      "verified": true,
      "profileImage": "https://scontent-arn2-1.cdninstagram.com/v/t51.82787-19/550174606_17925811725103224_8363667901743352243_n.jpg?stp=dst-jpg_s150x150_tt6&efg=eyJ2ZW5jb2RlX3RhZyI6InByb2ZpbGVfcGljLmRqYW5nby4xMDgwLmMyIn0&_nc_ht=scontent-arn2-1.cdninstagram.com&_nc_cat=1&_nc_oc=Q6cZ2gFsMxaeE1_m_Q_Q0eLf64nCG364CCEvIvzu9jsBCHKpQUWN0bClo9JEGGd5l3LhCQ8&_nc_ohc=2ejw17SwZhoQ7kNvwHwwhmI&_nc_gid=vNCBwQPT-0NDIFQsV3MGZQ&edm=APs17CUBAAAA&ccb=7-5&oh=00_AQFuCMUtskb3YHQEeVcugbTVFCIEBGnplQquZ3GzBmvhDA&oe=6A77D5BE&_nc_sid=10d13b"
    },
    "engagement": {
      "views": null,
      "likes": 3693,
      "replies": 1408,
      "reposts": 243,
      "quotes": 119
    },
    "media": [
      "https://scontent-arn2-1.cdninstagram.com/v/t51.71878-15/729466804_1549760159886177_1883659439515397370_n.jpg?stp=dst-jpg_e15_tt6&_nc_cat=105&ig_cache_key=MzkyNTg1NzYxNDQ3NTQyMzA5NQ%3D%3D.3-ccb7-5&ccb=7-5&_nc_sid=58cdad&efg=eyJ2ZW5jb2RlX3RhZyI6IkNBUk9VU0VMX0lURU0ueHBpZHMuNjQwLnNkci52aWRlb19kZWZhdWx0X2NvdmVyX2ZyYW1lLkMzIn0%3D&_nc_ohc=gwtwKMHXGY0Q7kNvwFs8O_B&_nc_oc=AdoeAgtu1iFjbAXZR03M0jk5mHDyXG-V4YkfEgAhFcL9ShW87MFpF6dbSvT0ivhLv8A&_nc_ad=z-m&_nc_cid=0&_nc_zt=23&_nc_ht=scontent-arn2-1.cdninstagram.com&_nc_gid=vNCBwQPT-0NDIFQsV3MGZQ&_nc_ss=7a22e&oh=00_AQGstcY-xX--otMYSGqFyYqoIP73kZ_8D8RHL_quEES13w&oe=6A77F376",
      "https://scontent-arn2-1.cdninstagram.com/o1/v/t16/f2/m84/AQOTRrCQTl1fyJz7fqBninvUdgWeil7BncTOhD-RfiP256I4PY_ioi8UAxdGl0WLEByzkS3XiObR8E2yNiSbmnE634ktoS1hPNebBYI.mp4?_nc_cat=107&_nc_sid=5e9851&_nc_ht=scontent-arn2-1.cdninstagram.com&_nc_ohc=fSXEPxW14JIQ7kNvwHBncdf&efg=eyJ2ZW5jb2RlX3RhZyI6Inhwdl9wcm9ncmVzc2l2ZS5JTlNUQUdSQU0uQ0FST1VTRUxfSVRFTS5DMy43MjAuZGFzaF9iYXNlbGluZV8xX3YxIiwieHB2X2Fzc2V0X2lkIjoxNzk2ODE3MTU3ODA4OTg4OCwiYXNzZXRfYWdlX2RheXMiOjQwLCJ2aV91c2VjYXNlX2lkIjoxMDE2NCwiZHVyYXRpb25fcyI6MjQsInVybGdlbl9zb3VyY2UiOiJ3d3cifQ%3D%3D&ccb=17-1&vs=cefa3ff17e61a968&_nc_vs=HBksFQIYTGlnX2JhY2tmaWxsX3RpbWVsaW5lX3ZvZC81NDQyODFEMkZCRDg0MzU4MzZBQUE0QzI5MzE4MzlBRF92aWRlb19kYXNoaW5pdC5tcDQVAALIARIAFQIYUWlnX3hwdl9wbGFjZW1lbnRfcGVybWFuZW50X3YyLzYwNEVGNDk2M0EwQzdFNTY4QTIyNDRDRkI4MDZBMkIwX2F1ZGlvX2Rhc2hpbml0Lm1wNBUCAsgBEgAoABgAGwKIB3VzZV9vaWwBMRJwcm9ncmVzc2l2ZV9yZWNpcGUBMRUAACbAhufCnv3qPxUCKAJDMywXQDgF41P3ztkYEmRhc2hfYmFzZWxpbmVfMV92MREAde4HZeieAQA&_nc_gid=vNCBwQPT-0NDIFQsV3MGZQ&_nc_zt=28&_nc_ss=7a22e&oh=00_AQHxRBBUCqh74vHFVtIRloUxKv6fQJnkF0rhbfQ9oLWYUw&oe=6A73E2B5"
    ],
    "comments": [],
    "relatedPosts": [
      {
        "platform": "threads",
        "id": "3955997150920775044",
        "code": "DbmhnLxFxWE",
        "url": "https://www.threads.net/@thelexlibris/post/DbmhnLxFxWE",
        "text": "The lack of accountability in that teas and tropes post is so wild. The signing lines is all that needs improvements?? I know not.",
        "publishedAt": "2026-08-04T02:47:11.000Z",
        "threadId": "3955997150920775044",
        "replyToId": null,
        "quoteId": null,
        "isReply": false,
        "isQuote": false,
        "author": {
          "username": "thelexlibris",
          "displayName": "Lex 🌱",
          "verified": null
        },
        "engagement": {
          "views": null,
          "likes": 1,
          "replies": null,
          "reposts": null,
          "quotes": null
        },
        "media": []
      },
      {
        "platform": "threads",
        "id": "3955973937109715838",
        "code": "DbmcVYOIMt-",
        "url": "https://www.threads.net/@xaylibarclay/post/DbmcVYOIMt-",
        "text": "WOW!! 😮 >> Out of approximately 41,000 to 47,000 active psychiatrists in the U.S., Black women make up less than 1% of the total. \n\nExact counts place the number of practicing Black female psychiatrists between 600 and 850 nationwide, meaning you are looking for a very rare, specialized group of professionals.\n\n🤯🤯",
        "publishedAt": "2026-08-04T02:01:04.000Z",
        "threadId": "3955973937109715838",
        "replyToId": null,
        "quoteId": null,
        "isReply": false,
        "isQuote": false,
        "author": {
          "username": "xaylibarclay",
          "displayName": "XayLi Barclay - Tech, Cameras, Life At 40 Yrs old",
          "verified": null
        },
        "engagement": {
          "views": null,
          "likes": 32,
          "replies": 7,
          "reposts": 3,
          "quotes": null
        },
        "media": []
      }
    ]
  },
  "threads-profile": {
    "platform": "threads",
    "username": "zuck",
    "url": "https://www.threads.net/@zuck",
    "id": "63055343223",
    "displayName": "Mark Zuckerberg",
    "name": "Mark Zuckerberg",
    "bio": "Mostly superintelligence and MMA takes",
    "verified": true,
    "followers": 5691292,
    "profileImage": "https://scontent-lax3-2.cdninstagram.com/v/t51.82787-19/550174606_17925811725103224_8363667901743352243_n.jpg?stp=dst-jpg_s640x640_tt6&efg=eyJ2ZW5jb2RlX3RhZyI6InByb2ZpbGVfcGljLmRqYW5nby4xMDgwLmMyIn0&_nc_ht=scontent-lax3-2.cdninstagram.com&_nc_cat=100&_nc_oc=Q6cZ2gEeXugh5SzVlR3-SM7yE5Ymx4mleUIUQVrFLOJAyo4Pai-q3Q4Babsn5npHNxps9Zg&_nc_ohc=2ejw17SwZhoQ7kNvwFX521e&_nc_gid=dmOcoQ5owB8qGvpTG7PZZA&edm=APs17CUBAAAA&ccb=7-5&oh=00_AQGktZYLExtnyRLt29v5FtvhGpx_oXGGlsI4Dt45cx4yWA&oe=6A74FA7E&_nc_sid=10d13b",
    "isThreadsOnlyUser": null,
    "private": false,
    "isPrivate": false,
    "bioLinks": [],
    "bioFragments": [],
    "transparencyLabel": null,
    "profileImageVersions": [
      {
        "url": "https://scontent-lax3-2.cdninstagram.com/v/t51.82787-19/550174606_17925811725103224_8363667901743352243_n.jpg?stp=dst-jpg_s320x320_tt6&efg=eyJ2ZW5jb2RlX3RhZyI6InByb2ZpbGVfcGljLmRqYW5nby4xMDgwLmMyIn0&_nc_ht=scontent-lax3-2.cdninstagram.com&_nc_cat=100&_nc_oc=Q6cZ2gEeXugh5SzVlR3-SM7yE5Ymx4mleUIUQVrFLOJAyo4Pai-q3Q4Babsn5npHNxps9Zg&_nc_ohc=2ejw17SwZhoQ7kNvwFX521e&_nc_gid=dmOcoQ5owB8qGvpTG7PZZA&edm=APs17CUBAAAA&ccb=7-5&oh=00_AQFU2s6roeLRVTBK1hBGzljKdg1GndlM6ZamolBrQr2S0Q&oe=6A74FA7E&_nc_sid=10d13b",
        "width": 320,
        "height": 320
      },
      {
        "url": "https://scontent-lax3-2.cdninstagram.com/v/t51.82787-19/550174606_17925811725103224_8363667901743352243_n.jpg?stp=dst-jpg_s640x640_tt6&efg=eyJ2ZW5jb2RlX3RhZyI6InByb2ZpbGVfcGljLmRqYW5nby4xMDgwLmMyIn0&_nc_ht=scontent-lax3-2.cdninstagram.com&_nc_cat=100&_nc_oc=Q6cZ2gEeXugh5SzVlR3-SM7yE5Ymx4mleUIUQVrFLOJAyo4Pai-q3Q4Babsn5npHNxps9Zg&_nc_ohc=2ejw17SwZhoQ7kNvwFX521e&_nc_gid=dmOcoQ5owB8qGvpTG7PZZA&edm=APs17CUBAAAA&ccb=7-5&oh=00_AQGktZYLExtnyRLt29v5FtvhGpx_oXGGlsI4Dt45cx4yWA&oe=6A74FA7E&_nc_sid=10d13b",
        "width": 640,
        "height": 640
      }
    ],
    "hasOnboarded": true
  },
  "threads-search": {
    "query": "artificial intelligence",
    "totalReturned": 5,
    "results": [
      {
        "platform": "threads",
        "id": "3955315825888714785",
        "code": "DbkGsmYk-Ah",
        "url": "https://www.threads.net/@iansh04_/post/DbkGsmYk-Ah",
        "text": "All Paid Courses (Free for First 4500 People)\n𝗣𝗮𝗶𝗱 𝗖𝗼𝘂𝗿𝘀𝗲 𝗙𝗥𝗘𝗘 (PART - 1)\n1. Artificial Intelligence\n2. Machine Learning\n3. Prompt Engineering\n4. Claude,Chatgpt,Grok\n5. Data Analytics\n6. AWS Certified\n7. Data Science\n8. BIG DATA\n9. Python\n10. Ethical Hacking\n(72 Hours only )\nLike + Repost + comment ' Drive '\nMust Follow @iansh04_ so I can DM you.",
        "publishedAt": "2026-08-03T04:13:31.000Z",
        "threadId": "3955315825888714785",
        "replyToId": null,
        "quoteId": null,
        "isReply": false,
        "isQuote": false,
        "author": {
          "username": "iansh04_",
          "displayName": "Ansh Bhatnagar",
          "verified": false
        },
        "engagement": {
          "views": null,
          "likes": 651,
          "replies": 790,
          "reposts": 412,
          "quotes": 4
        },
        "media": [
          "https://scontent-arn2-1.cdninstagram.com/v/t51.82787-15/763355760_17982304443106462_6808022601370922517_n.jpg?stp=c0.162.799.799a_dst-jpg_e35_s799x799_tt6&_nc_cat=1&ig_cache_key=Mzk1NTMxNTgyNTg4ODcxNDc4NQ%3D%3D.3-ccb7-5&ccb=7-5&_nc_sid=58cdad&efg=eyJ2ZW5jb2RlX3RhZyI6IkZFRUQueHBpZHMuNzk5LnNkci5yZWd1bGFyX3Bob3RvLkMzIn0%3D&_nc_ohc=W6xISNbePogQ7kNvwFHyufm&_nc_oc=Adpj2_PItVsSle0pXBx8J50TeHA2rVgNKt5K3ykIx7ldNtte-CnSNdBYH26W0xnr9tc&_nc_ad=z-m&_nc_cid=0&_nc_zt=23&_nc_ht=scontent-arn2-1.cdninstagram.com&_nc_gid=2OcSzrbqz_izuGJcwi-1qQ&_nc_ss=7a22e&oh=00_AQGLu1pgLEJU7smbOpdzIyAzqlyw6AtR4JFDxcgyr2gJzA&oe=6A77FBBD"
        ]
      },
      {
        "platform": "threads",
        "id": "3557348422268871722",
        "code": "DFePYrboeQq",
        "url": "https://www.threads.net/@theartificialintelligence/post/DFePYrboeQq",
        "text": "🇨🇳🇺🇸 DeepSeek tells the world that artificial intelligence is not American intelligence, and the United States has no right to monopolize the development of AI that belongs to all mankind.\n\n-Dr. Victor Gao",
        "publishedAt": "2025-01-31T02:04:57.000Z",
        "threadId": "3557348422268871722",
        "replyToId": null,
        "quoteId": null,
        "isReply": false,
        "isQuote": false,
        "author": {
          "username": "theartificialintelligence",
          "displayName": "Artificial Intelligence | AI",
          "verified": true
        },
        "engagement": {
          "views": null,
          "likes": 10777,
          "replies": 823,
          "reposts": 759,
          "quotes": 50
        },
        "media": [
          "https://scontent-arn2-1.cdninstagram.com/o1/v/t16/f2/m84/AQPR4zUqReqf-s4ildWOQeBb718tDuYqeErpvd3aGhr4jI7THlrcuR7esStJjWXCkmLl-XURcNSrf7AsUKFmac0NgM-QfunN0v1quQo.mp4?_nc_cat=109&_nc_sid=5e9851&_nc_ht=scontent-arn2-1.cdninstagram.com&_nc_ohc=wtd19Chl-HEQ7kNvwGng7Cc&efg=eyJ2ZW5jb2RlX3RhZyI6Inhwdl9wcm9ncmVzc2l2ZS5JTlNUQUdSQU0uRkVFRC5DMy4xMjgwLmRhc2hfYmFzZWxpbmVfMV92MSIsInhwdl9hc3NldF9pZCI6OTU1NDY3MDkxNzkyNDE0MiwiYXNzZXRfYWdlX2RheXMiOjU1MCwidmlfdXNlY2FzZV9pZCI6MTAxNjQsImR1cmF0aW9uX3MiOjI2MiwidXJsZ2VuX3NvdXJjZSI6Ind3dyJ9&ccb=17-1&vs=6df3e1b4c37b0184&_nc_vs=HBksFQIYTGlnX2JhY2tmaWxsX3RpbWVsaW5lX3ZvZC9FRjRCRkY3RkY3NEM5REZERjE1QUJDQUI1OEU4Rjk4Ql92aWRlb19kYXNoaW5pdC5tcDQVAALIARIAFQIYOnBhc3N0aHJvdWdoX2V2ZXJzdG9yZS9HTFRwVkJ6VThfSDFnalVIQUtJNTJLZkhlbVZ2YmtZTEFBQUYVAgLIARIAKAAYABsCiAd1c2Vfb2lsATEScHJvZ3Jlc3NpdmVfcmVjaXBlATEVAAAm3NSR4IX7-CEVAigCQzMsF0BwYAAAAAAAGBJkYXNoX2Jhc2VsaW5lXzFfdjERAHXqB2XongEA&_nc_gid=2OcSzrbqz_izuGJcwi-1qQ&_nc_zt=28&_nc_ss=7a22e&oh=00_AQF8bFsn29XzqRjQkrRFQrTZklFBON9dC84Y-XO4UOk-iw&oe=6A73E02B",
          "https://scontent-arn2-1.cdninstagram.com/v/t51.71878-15/474888843_486869244173785_943828438724363456_n.jpg?stp=dst-jpg_e15_tt6&_nc_cat=111&ig_cache_key=MzU1NzM0ODQyMjI2ODg3MTcyMg%3D%3D.3-ccb7-5&ccb=7-5&_nc_sid=58cdad&efg=eyJ2ZW5jb2RlX3RhZyI6IkZFRUQueHBpZHMuNjQwLnNkci52aWRlb19kZWZhdWx0X2NvdmVyX2ZyYW1lLkMzIn0%3D&_nc_ohc=3FblhuYndyEQ7kNvwEjz1O7&_nc_oc=Adp7qot7ziRgosQn26lzhfHrzzD_m2TOH814YQ1H8ASPezYzNdAr9tGFpJn46kg9I_o&_nc_ad=z-m&_nc_cid=0&_nc_zt=23&_nc_ht=scontent-arn2-1.cdninstagram.com&_nc_gid=2OcSzrbqz_izuGJcwi-1qQ&_nc_ss=7a22e&oh=00_AQEidlufgTbrLRvAeY_lttMaLW7uUuDWfGwhwIjT5ImsRQ&oe=6A77F4AA"
        ]
      }
    ]
  },
  "threads-search-users": {
    "query": "tech",
    "totalReturned": 5,
    "users": [
      {
        "id": "63419899106",
        "username": "3dfreelancing",
        "displayName": "DesignX3D",
        "url": "https://www.threads.net/@3dfreelancing",
        "verified": false,
        "profileImage": "https://scontent-fml20-1.cdninstagram.com/v/t51.2885-19/358048371_611813460748673_7424252667534087950_n.jpg?stp=dst-jpg_s150x150_tt6&efg=eyJ2ZW5jb2RlX3RhZyI6InByb2ZpbGVfcGljLmRqYW5nby4xMDgwLmMyIn0&_nc_ht=scontent-fml20-1.cdninstagram.com&_nc_cat=105&_nc_oc=Q6cZ2gEuCNzOQBL3WLzHjDVRIUD7nfx3k_HdX2EBkqaiTQ4PmTXyR_B_-1b8j4rN_XouC9U&_nc_ohc=ClRgc8VdrWUQ7kNvwGYy0bX&_nc_gid=BMY7SQQ5QtTZglymKPVK5A&edm=APs17CUBAAAA&ccb=7-5&oh=00_AQFt9IQAYLyjaUWIxFVZ1Soax9syl38lEYeCSesfZ69jGQ&oe=6A77DF17&_nc_sid=10d13b",
        "followers": null
      },
      {
        "id": "69067321051",
        "username": "sgt.edsmia",
        "displayName": "Eds Mia",
        "url": "https://www.threads.net/@sgt.edsmia",
        "verified": false,
        "profileImage": "https://scontent-fml20-1.cdninstagram.com/v/t51.82787-19/616077711_17908752390297052_8918972735608639981_n.jpg?stp=dst-jpg_s150x150_tt6&efg=eyJ2ZW5jb2RlX3RhZyI6InByb2ZpbGVfcGljLmRqYW5nby4xMDIyLmMyIn0&_nc_ht=scontent-fml20-1.cdninstagram.com&_nc_cat=104&_nc_oc=Q6cZ2gEuCNzOQBL3WLzHjDVRIUD7nfx3k_HdX2EBkqaiTQ4PmTXyR_B_-1b8j4rN_XouC9U&_nc_ohc=PVTn-IDWAVsQ7kNvwFHmDGu&_nc_gid=BMY7SQQ5QtTZglymKPVK5A&edm=APs17CUBAAAA&ccb=7-5&oh=00_AQFFSvfmo4CklK7KwP_B_B-6LlLzoy9Vf5bVT9IRy_MtTQ&oe=6A77D171&_nc_sid=10d13b",
        "followers": null
      }
    ]
  },
  "threads-user-posts": {
    "handle": "zuck",
    "author": {
      "username": "zuck",
      "displayName": "Mark Zuckerberg",
      "verified": true,
      "profileImage": "https://scontent-cdg4-2.cdninstagram.com/v/t51.82787-19/550174606_17925811725103224_8363667901743352243_n.jpg?stp=dst-jpg_s150x150_tt6&efg=eyJ2ZW5jb2RlX3RhZyI6InByb2ZpbGVfcGljLmRqYW5nby4xMDgwLmMyIn0&_nc_ht=scontent-cdg4-2.cdninstagram.com&_nc_cat=100&_nc_oc=Q6cZ2gHf4XJXymdRHno1xv4ZWDptPQ_F47AvofZR9ZypzIXJ5_ggqvnOJ4NFY10teCcuKSw&_nc_ohc=vLH8jAZMCqoQ7kNvwFFwBjL&_nc_gid=wkyjiyQ2aEsOml1qJ-3q-Q&edm=APs17CUBAAAA&ccb=7-5&oh=00_AQBvZqkyiiQ8DOAXcD-rNsrA7GYbSMXCSzCPUIBJWAPwew&oe=6A6E2ABE&_nc_sid=10d13b"
    },
    "totalReturned": 5,
    "posts": [
      {
        "platform": "threads",
        "id": "3937491905269768921",
        "code": "DakyAavlKLZ",
        "url": "https://www.threads.net/@zuck/post/DakyAavlKLZ",
        "text": "Today we're releasing Muse Spark 1.1 -- a strong agentic and coding model at a very low price. It's available through our new Meta Model API and in Meta AI.",
        "publishedAt": "2026-07-09T14:00:34.000Z",
        "threadId": "3937491905269768921",
        "replyToId": null,
        "quoteId": null,
        "isReply": false,
        "isQuote": false,
        "author": {
          "username": "zuck",
          "displayName": "Mark Zuckerberg",
          "verified": true
        },
        "engagement": {
          "views": null,
          "likes": 2852,
          "replies": 765,
          "reposts": 196,
          "quotes": 63
        },
        "media": []
      },
      {
        "platform": "threads",
        "id": "3937491928497827415",
        "code": "DakyAwYFK5X",
        "url": "https://www.threads.net/@zuck/post/DakyAwYFK5X",
        "text": "Muse Spark 1.1 is strongest at agentic performance, tool use, and computer use. It does well on long-running tasks with 1M token context window, can delegate execution to sub-agents running in parallel, and is trained to use computer interfaces on desktop, mobile, or browser.",
        "publishedAt": "2026-07-09T14:00:37.000Z",
        "threadId": "3937491905269768921",
        "replyToId": "3937491905269768921",
        "quoteId": null,
        "isReply": true,
        "isQuote": false,
        "author": {
          "username": "zuck",
          "displayName": "Mark Zuckerberg",
          "verified": true
        },
        "engagement": {
          "views": null,
          "likes": 912,
          "replies": 91,
          "reposts": 59,
          "quotes": 14
        },
        "media": [
          "https://scontent-cdg4-3.cdninstagram.com/v/t51.82787-15/741068464_17977387650103224_214669101615299168_n.webp?_nc_cat=110&ig_cache_key=MzkzNzQ5MTkyODQ5NzgyNzQxNQ%3D%3D.3-ccb7-5&ccb=7-5&_nc_sid=58cdad&efg=eyJ2ZW5jb2RlX3RhZyI6IkZFRUQueHBpZHMuMTYyMC5zZHIucmVndWxhcl9waG90by5DMyJ9&_nc_ohc=BnavDWIpJKMQ7kNvwGW14gJ&_nc_oc=Ado5sxMS3V9I9TFA6KpOo5ZTsDLrt2liAWKAxWtcz-ea50_hZb2YjO_d70TiTHhjkGA&_nc_ad=z-m&_nc_cid=0&_nc_zt=23&_nc_ht=scontent-cdg4-3.cdninstagram.com&_nc_gid=wkyjiyQ2aEsOml1qJ-3q-Q&_nc_ss=7a22e&oh=00_AQDyLjCkW1XRN7kshX0Uybz1QIy_tJdKTcfMdl2WJNISyA&oe=6A6E32AC"
        ]
      }
    ]
  },
  "tiktok-ad-library-ad-details": {
    "platform": "tiktok_ad_library",
    "id": "1872034324356433",
    "url": "https://library.tiktok.com/ads/detail/?ad_id=1872034324356433",
    "text": "#gandurilemele #foryoupage❤️❤️ Buna dimineața tuturor!Zi binecuvântata tuturor!🙏🙏🙏",
    "adFormat": "video",
    "firstShown": "07/29/2026",
    "lastShown": "07/29/2026",
    "advertiser": {
      "name": "alyalina535"
    },
    "media": [
      "https://library.tiktok.com/api/v1/cdn/1785356384/video/aHR0cHM6Ly92NzcudGlrdG9rY2RuLmNvbS8zYTU3ZmRiZjYzZGIzYjY5Nzc1NzA5ZjQ0ZTMwOGZkNC82YTZhYjUwZS92aWRlby90b3MvdXNlYXN0MmEvdG9zLXVzZWFzdDJhLXZlLTAwNjgtZXV0dHAvbzRJMXRCVHdBNUVFNlEzMW01emlpY1NNSUE0ZjlLQW53b0JMQ2sv/7467d396-0387-4b9f-90c7-2d2cd26db171?a=475769&bt=1049&btag=e00090000&bti=PDU2NmYwMy86&ft=.NpOcInz7ThRcbuGXq8Zmo&l=20260730041944142876664F10EA1EB193&mime_type=video_mp4&rc=NWZoZWU8ZDM6NDU3OGk6ZEBpM3Q0aHM5cjxsPDMzZjczNUA2YWM2MF9eXmExMWBeYDFgYSNnMjNmMmRzcGdhLS1kMTNzcw%3D%3D&signature=Qzo7c7UEa5N40yYL1KKsuy%2BR%2BCnqSwFptCMo9QOZPtQ%3D&vvpl=1"
    ]
  },
  "tiktok-ad-library-search": {
    "query": "nike",
    "country": "GB",
    "totalReturned": 3,
    "ads": [
      {
        "platform": "tiktok_ad_library",
        "id": "1872402620173314",
        "url": "https://library.tiktok.com/ads/detail/?ad_id=1872402620173314",
        "text": "Professional Massage Therapy for Relaxation, Recovery, and Wellness.",
        "adFormat": "video",
        "firstShown": "2026-08-02T00:00:00.000Z",
        "lastShown": "2026-08-02T00:00:00.000Z",
        "impressions": "0-1K",
        "advertiser": {
          "name": "HongKong AdTiger Media Co., Limited",
          "location": "Hong Kong"
        },
        "media": [
          "https://p16-common-sign.tiktokcdn.com/tos-alisg-p-0051c001-sg/3dff80d5a4f73a22d6682afa5f45d78d~tplv-tiktokx-origin.jpeg?dr=14582&refresh_token=cd5ba53f&x-expires=1785686400&x-signature=m6GakMpuep1d%2BRNlCGpC0K9CiWE%3D&t=4d5b0474&ps=13740610&a",
          "https://library.tiktok.com/api/v1/cdn/1785667308/video/aHR0cHM6Ly92NzcudGlrdG9rY2RuLmNvbS9mMTgyNTU3Yzg1OGVjOGEwM2RkMGQ1MjRjZTRlOWM4Ny82YTZmNzM3ZS92aWRlby90b3MvYWxpc2cvdG9zLWFsaXNnLXZlLTAwNTFjMDAxLXNnL29zOU5VSkFzZ0lMUGVtT0RoRlVHZUdSQzNSb1JnbW5lQUFKTEdiLw==/fee44425-7600-4c48-8df9-ce242eb52069?a=475769&bt=593&btag=e00088000&bti=PDU2NmYwMy86&ft=.NpOcInz7Thz~INGXq8Zmo&l=2026080218414895FDAC2A6CF961573BDF&mime_type=video_mp4&rc=N2hoOzVpZzM1OTs0aDM5aUBpajVpOGw5cjRqPDMzODYzNEBjMmFeYy9fXzMxMS0zLTJjYSNxZy82MmRraWthLS1kMC1zcw%3D%3D&signature=v7cmUB0AYCwTjyukuWGzRGtiRJKMRb6UOyUo2szN2pY%3D&vvpl=1"
        ],
        "impressionsRange": {
          "min": 0,
          "max": 1000,
          "raw": "0-1K"
        }
      },
      {
        "platform": "tiktok_ad_library",
        "id": "1872069030885697",
        "url": "https://library.tiktok.com/ads/detail/?ad_id=1872069030885697",
        "text": "Visit the website and learn more.",
        "adFormat": "video",
        "firstShown": "2026-08-02T00:00:00.000Z",
        "lastShown": "2026-08-02T00:00:00.000Z",
        "impressions": "0-1K",
        "advertiser": {
          "name": "VV7 HOLDING LLC",
          "location": "United States"
        },
        "media": [
          "https://p16-common-sign.tiktokcdn.com/ad-site-i18n-sg/20260729c7c7767b1bd4c6634305aba2~tplv-tiktokx-origin.jpeg?dr=14582&refresh_token=a7fcf310&x-expires=1785686400&x-signature=H8hajcaAaLOzUe4Qcbse8V10R%2Bs%3D&t=4d5b0474&ps=13740610&shp=0c75dd76&s",
          "https://library.tiktok.com/api/v1/cdn/1785667310/video/aHR0cHM6Ly92NzcudGlrdG9rY2RuLmNvbS9kOTEzMzQzYmVlZTBlODkyNDRhOTZjYmE0ZTdjYzk1OS82YTZmNzM2MC92aWRlby90b3MvYWxpc2cvdG9zLWFsaXNnLXZlLTAwNTFjMDAxLXNnL28wM3VvbDdZak5BRUFpSHcybXk5enB2aVVNY0JCWGFRQ3FOSUEv/a83a6b69-bc09-432a-a704-4cb96c22fbb2?a=475769&bt=997&btag=e000b8000&bti=PDU2NmYwMy86&ft=.NpOcInz7Thn~INGXq8Zmo&l=202608021841508CA9C9F51CA00456AC9F&mime_type=video_mp4&rc=Z2dpNWY5ZTdmM2k8ZzU2OEBpM3FvcnU5cmw2PDMzODYzNEBhMDUyLjFhXjQxMF5jXy1eYSNiY3MwMmRrLmlhLS1kMC1zcw%3D%3D&signature=c1LXfiH6SOrrYOTEWg4TRCzE%2BNR%2BSu0k%2Fuj%2FDEUJ3vk%3D&vvpl=1"
        ],
        "impressionsRange": {
          "min": 0,
          "max": 1000,
          "raw": "0-1K"
        }
      }
    ]
  },
  "tiktok-ad-library-top-ads": {
    "query": null,
    "country": "US",
    "period": 30,
    "orderBy": "ctr",
    "totalReturned": 2,
    "datesPresent": 1,
    "match": "any",
    "matchedFrom": 2,
    "filteredOut": 0,
    "literalMatches": 2,
    "matchBasis": "none",
    "ads": [
      {
        "platform": "tiktok_creative_center",
        "id": "7662489073849090066",
        "url": "https://ads.tiktok.com/business/creativecenter/topads/7662489073849090066/pc/en",
        "title": "Nuuly loves a woman in a suit ! #ad #nuulypartner #nuuly #frthoidolovenuuly",
        "brandName": "nuuly",
        "advertiser": {
          "id": "brand_nuuly",
          "name": "nuuly"
        },
        "firstSeen": "2026-01-10T00:00:00.000Z",
        "lastSeen": null,
        "likes": 620,
        "likesIsApproximate": false,
        "ctr": 0.17,
        "ctrTier": "below_50%",
        "costTier": 1,
        "isSparkAd": false,
        "industry": "Charity & Public Welfare",
        "industryKey": "label_23105000000",
        "objective": "Reach",
        "video": {
          "id": "v10033g50000example",
          "url": "https://v16m-default.tiktokcdn.com/example.mp4",
          "urlHd": "https://v16m-default.tiktokcdn.com/example-hd.mp4",
          "cover": "https://p16-common-sign.tiktokcdn.com/example~tplv-noop.image",
          "durationSeconds": 15.0,
          "width": 720,
          "height": 1280
        }
      },
      {
        "platform": "tiktok_creative_center",
        "id": "7662938725836324871",
        "url": "https://ads.tiktok.com/business/creativecenter/topads/7662938725836324871/pc/en",
        "title": "How I fix my hair EASILY on the go #hair #hairhack",
        "brandName": "Creator X",
        "advertiser": {
          "id": "uid42",
          "name": "Creator X"
        },
        "firstSeen": null,
        "lastSeen": null,
        "likes": 5,
        "likesIsApproximate": false,
        "ctr": 0.62,
        "ctrTier": "top_25%",
        "costTier": 0,
        "isSparkAd": true,
        "industry": "Charity & Public Welfare",
        "industryKey": "label_23105000000",
        "objective": "Product Sales",
        "video": {
          "id": "v10033g50000example",
          "url": "https://v16m-default.tiktokcdn.com/example.mp4",
          "cover": "https://p16-common-sign.tiktokcdn.com/example~tplv-noop.image",
          "durationSeconds": 15.0,
          "width": 720,
          "height": 1280
        }
      }
    ]
  },
  "tiktok-audience-demographics": {
    "platform": "tiktok",
    "username": "khaby.lame",
    "url": "https://www.tiktok.com/@khaby.lame",
    "videosSampled": 12,
    "sampleSize": 269,
    "audienceLocations": [
      {
        "country": "Pakistan",
        "countryCode": "PK",
        "count": 70,
        "percentage": 26.02,
        "percentageText": "26.02%"
      },
      {
        "country": "United States",
        "countryCode": "US",
        "count": 33,
        "percentage": 12.27,
        "percentageText": "12.27%"
      }
    ],
    "basis": "commenters",
    "videosRequested": 12,
    "totalCountries": 23,
    "confidence": "low",
    "other": {
      "count": 129,
      "percentage": 47.96,
      "percentageText": "47.96%"
    },
    "audienceLanguages": [
      {
        "language": "en",
        "count": 142,
        "percentage": 52.79,
        "percentageText": "52.79%"
      },
      {
        "language": "ur",
        "count": 61,
        "percentage": 22.68,
        "percentageText": "22.68%"
      }
    ],
    "languageSampleSize": 269
  },
  "tiktok-channel-details": {
    "platform": "tiktok",
    "url": "https://www.tiktok.com/@natgeo",
    "username": "natgeo",
    "displayName": "National Geographic",
    "bio": "Step into wonder and find your inner explorer with National Geographic 🌎",
    "followers": 9587666,
    "following": 61,
    "likes": 53396669,
    "postCount": 1447,
    "verified": true,
    "private": false,
    "profileImage": "https://p16-common-sign.tiktokcdn-us.com/tos-useast8-avt-0068-tx2/324924e171e481040a1ea202962f6e07~tplv-tiktokx-cropcenter:1080:1080.jpeg?dr=9640&refresh_token=60ef5726&x-expires=1786006800&x-signature=n%2FMPTuUDmyvfGLstiODt0jLT1YI%3D&t=4d5b0474&ps=13740610&shp=a5d48078&shcp=81f88b70&idc=useast8",
    "externalUrl": "spr.ly/natgeotiktok",
    "category": "Media & Entertainment",
    "id": "6780344874811442181",
    "secUid": "MS4wLjABAAAAEf96k3JW8-3eOhgzgQswlFF6ZDnn1dzqWWorJjwDsiNZymqTtvOcFhp_RiYYST6s",
    "createTime": "2020-01-10T16:08:37.000Z",
    "createTimeUnix": 1578672517,
    "friendCount": 58,
    "diggCount": 0,
    "profileImageMedium": "https://p19-common-sign.tiktokcdn-us.com/tos-useast8-avt-0068-tx2/324924e171e481040a1ea202962f6e07~tplv-tiktokx-cropcenter:720:720.jpeg?dr=9640&refresh_token=d46aae73&x-expires=1786006800&x-signature=l4BUyuqDZYb9vMNfLsYoWMRwJtw%3D&t=4d5b0474&ps=13740610&shp=a5d48078&shcp=81f88b70&idc=useast8",
    "profileImageThumb": "https://p16-common-sign.tiktokcdn-us.com/tos-useast8-avt-0068-tx2/324924e171e481040a1ea202962f6e07~tplv-tiktokx-cropcenter:100:100.jpeg?dr=9640&refresh_token=d358301c&x-expires=1786006800&x-signature=sUb0QBIfg%2BSiLElb8QD5Bh8oSUk%3D&t=4d5b0474&ps=13740610&shp=a5d48078&shcp=81f88b70&idc=useast8",
    "bioLink": {
      "link": "spr.ly/natgeotiktok",
      "risk": 3
    },
    "bioLinkRisk": 3,
    "isCommerceUser": true,
    "isSeller": false,
    "ttSeller": false,
    "isOrganization": 1,
    "isAdVirtual": false,
    "isEmbedBanned": false,
    "language": "en",
    "commentSetting": 0,
    "duetSetting": 3,
    "stitchSetting": 3,
    "downloadSetting": 3,
    "followingVisibility": 1,
    "profileTab": {
      "showMusicTab": false,
      "showQuestionTab": true,
      "showPlayListTab": true
    },
    "uniqueIdModifyTime": null,
    "nickNameModifyTime": null,
    "contact": {
      "links": [
        "spr.ly/natgeotiktok"
      ]
    },
    "fetchedAt": "2026-08-04T09:43:07.476Z",
    "region": null
  },
  "tiktok-channel-posts": {
    "url": "https://www.tiktok.com/@paw.dreams0",
    "totalReturned": 3,
    "posts": [
      {
        "platform": "tiktok",
        "url": "https://www.tiktok.com/@paw.dreams0/video/7656435976872512790",
        "id": "7656435976872512790",
        "caption": "The Kitten Was Teased For Playing With A Carboard Hedgehog Car #supercat #catfunnyvideos #unitedstates #funnyvideos #cat",
        "publishedAt": "2026-06-28T15:30:00.000Z",
        "durationSeconds": 103.0,
        "thumbnailUrl": "https://p16-common-sign.tiktokcdn-us.com/tos-no1a-p-0037-no/oMvNfABQoHBF5iVXqnZKfAkCgEcBCcXIAA2Rik~tplv-tiktokx-origin.image?dr=9636&x-expires=1786014000&x-signature=7iKHuC9qK3jSvtrNhOUA%2Bp22FCE%3D&t=4d5b0474&ps=13740610&shp=81f88b70&shcp=43f4a2f9&idc=useast8",
        "mediaType": "video",
        "contentType": "video",
        "width": 576,
        "height": 1024,
        "videoUrl": "https://v16-webapp-prime.us.tiktok.com/video/tos/no1a/tos-no1a-ve-0068c001-no/oo0gFjfDkInJVIqCkI1etQVRBBCAFE7CFQJBEg/?a=1988&bti=ODszNWYuMDE6&&bt=714&ft=aEeq8qT0mIoPD12hRxRI3wURISAbMeF~O5&mime_type=video_mp4&rc=NWRnOjVkMzYzOzloPDs3OkBpM2Q5N205cmprPDMzbzgzNUAxNTAuYDEtXy8xXjJhYGNjYSNzNS9tMmRjcS1hLS1kLzFzcw%3D%3D&expire=1786015197&l=202608041118135C9F6414E9C9CE1EEA0A&ply_type=2&policy=2&signature=df687ad939be7ff96221abaf98d97f19&tk=tt_chain_token&btag=e00090000",
        "downloadUrl": "https://v16-webapp-prime.us.tiktok.com/video/tos/no1a/tos-no1a-ve-0068c001-no/ooIjNVBqtQBI7FIaneZDNgQCkVFfABkwjEPgER/?a=1988&bti=ODszNWYuMDE6&&bt=1244&eid=5376&ft=aEeq8qT0mIoPD12hRxRI3wURISAbMeF~O5&mime_type=video_mp4&rc=OTs6PGg7ZDtnNGc6ZzdmO0BpM2Q5N205cmprPDMzbzgzNUBhLzYzYGBgNmExYDUzNGAxYSNzNS9tMmRjcS1hLS1kLzFzcw%3D%3D&expire=1786015197&l=202608041118135C9F6414E9C9CE1EEA0A&ply_type=2&policy=2&signature=558354d9fee7b2fc61bd2a464a45a073&tk=tt_chain_token&btag=e00090000",
        "hasWatermark": true,
        "mediaUrlsExpireAt": "2026-08-06T11:00:00.000Z",
        "author": {
          "id": "7635116029405201410",
          "secUid": "MS4wLjABAAAAvoNLKzifeDkHLRF2sTlYvhm39FAirS8996wURRRozsE-p7I6BMVYa6vsHFzYUe86",
          "username": "paw.dreams0",
          "displayName": "Paw Dreams",
          "url": "https://www.tiktok.com/@paw.dreams0",
          "followers": 147100,
          "verified": false,
          "profileImage": "https://p16-common-sign.tiktokcdn-us.com/tos-maliva-avt-0068/14e5b5dbddf91912237e342a048afb2c~tplv-tiktokx-cropcenter:1080:1080.jpeg?dr=9640&refresh_token=d3280f67&x-expires=1786014000&x-signature=Zq9ynnhU%2FSV7%2B1B2XFVOKSDO2xY%3D&t=4d5b0474&ps=13740610&shp=a5d48078&shcp=81f88b70&idc=useast8"
        },
        "engagement": {
          "views": 458100,
          "likes": 9227,
          "comments": 177,
          "shares": 522,
          "saves": 1751
        },
        "hashtags": [
          "supercat",
          "catfunnyvideos"
        ],
        "musicName": "original sound - Paw Dreams",
        "musicId": "7656436046934182678",
        "musicAuthor": "Paw Dreams",
        "descLanguage": "en",
        "isAd": false,
        "isPaidPartnership": false,
        "mentions": []
      },
      {
        "platform": "tiktok",
        "url": "https://www.tiktok.com/@paw.dreams0/video/7656002337634340118",
        "id": "7656002337634340118",
        "caption": "The Kitten Was Teased For Playing With A Carboard Lamborghini  #supercat #fifa #catfunnyvideos #unitedstates #funnyvideos #cat",
        "publishedAt": "2026-06-27T15:00:00.000Z",
        "durationSeconds": 95.0,
        "thumbnailUrl": "https://p16-common-sign.tiktokcdn-us.com/tos-no1a-p-0037-no/ocUTZAkDqClnJhPFEAA58AIzCFtffP2gTVQMBN~tplv-tiktokx-origin.image?dr=9636&x-expires=1786014000&x-signature=0CqhY2mmleTu5hEnh5P90Plo7V4%3D&t=4d5b0474&ps=13740610&shp=81f88b70&shcp=43f4a2f9&idc=useast8",
        "mediaType": "video",
        "contentType": "video",
        "width": 576,
        "height": 1024,
        "videoUrl": "https://v16-webapp-prime.us.tiktok.com/video/tos/no1a/tos-no1a-ve-0068-no/oUJfPSgPfAQPySBQgDVqYcBulEFkFCKuu5QINy/?a=1988&bti=ODszNWYuMDE6&&bt=693&ft=aEeq8qT0mIoPD12hRxRI3wURISAbMeF~O5&mime_type=video_mp4&rc=aDgzNGg1OmY3ZGZnNWY5ZUBpajxtbXM5cjZzOzMzbzgzNUAwLjNgYi5hNi8xXl80NDJjYSNfYi1fMmRzNnNhLS1kLzFzcw%3D%3D&expire=1786015189&l=202608041118135C9F6414E9C9CE1EEA0A&ply_type=2&policy=2&signature=555986ea5b82112dd53636f8c7c52cdb&tk=tt_chain_token&btag=e000d0000",
        "downloadUrl": "https://v16-webapp-prime.us.tiktok.com/video/tos/no1a/tos-no1a-ve-0068-no/ogCJdPQgkJAFuE5lJ8VSyPfYZSD3FBcIugbquf/?a=1988&bti=ODszNWYuMDE6&&bt=1218&eid=5376&ft=aEeq8qT0mIoPD12hRxRI3wURISAbMeF~O5&mime_type=video_mp4&rc=aDYzaDg8aWZmMzZnZztpZUBpajxtbXM5cjZzOzMzbzgzNUAxMS8tXmNfNWMxYWFgNTFiYSNfYi1fMmRzNnNhLS1kLzFzcw%3D%3D&expire=1786015189&l=202608041118135C9F6414E9C9CE1EEA0A&ply_type=2&policy=2&signature=0a2fc3a608ccdcbcee62160c40611a8b&tk=tt_chain_token&btag=e000d0000",
        "hasWatermark": true,
        "mediaUrlsExpireAt": "2026-08-06T11:00:00.000Z",
        "author": {
          "id": "7635116029405201410",
          "secUid": "MS4wLjABAAAAvoNLKzifeDkHLRF2sTlYvhm39FAirS8996wURRRozsE-p7I6BMVYa6vsHFzYUe86",
          "username": "paw.dreams0",
          "displayName": "Paw Dreams",
          "url": "https://www.tiktok.com/@paw.dreams0",
          "followers": 147100,
          "verified": false,
          "profileImage": "https://p16-common-sign.tiktokcdn-us.com/tos-maliva-avt-0068/14e5b5dbddf91912237e342a048afb2c~tplv-tiktokx-cropcenter:1080:1080.jpeg?dr=9640&refresh_token=d3280f67&x-expires=1786014000&x-signature=Zq9ynnhU%2FSV7%2B1B2XFVOKSDO2xY%3D&t=4d5b0474&ps=13740610&shp=a5d48078&shcp=81f88b70&idc=useast8"
        },
        "engagement": {
          "views": 125800,
          "likes": 2237,
          "comments": 68,
          "shares": 150,
          "saves": 487
        },
        "hashtags": [
          "fifa",
          "cat"
        ],
        "musicName": "original sound - Paw Dreams",
        "musicId": "7656002370417052438",
        "musicAuthor": "Paw Dreams",
        "descLanguage": "en",
        "isAd": false,
        "isPaidPartnership": false,
        "mentions": []
      }
    ],
    "nextCursor": "1781133123000",
    "hasMore": true
  },
  "tiktok-comment-replies": {
    "platform": "tiktok",
    "url": "https://www.tiktok.com/@khaby.lame/video/7646812028874673439",
    "commentId": "7652622392003003157",
    "totalReturned": 10,
    "totalReplies": 22,
    "replies": [
      {
        "id": "7652704280361403157",
        "text": "tinggal seribu lagi jadi 5jt😹",
        "author": "evan.gunawan2037",
        "authorId": "7442964363847697409",
        "authorSecUid": "MS4wLjABAAAA7ax_OCYs6_dYN6ecF_wfwrsx5MWfm6ZXPq1uBd7JxHRyQV11bE_95NMCWoPh6ryo",
        "authorName": "MAJIN_EVAN⚡",
        "commentLanguage": "id",
        "likeCount": 27,
        "publishedAt": "2026-06-18T12:01:20.000Z",
        "verified": false,
        "profileImage": "https://p16-common-sign.tiktokcdn-eu.com/tos-alisg-avt-0068/6ea4cabf09938d71804dd2b430afbdcb~tplv-tiktokx-cropcenter-q:100:100:q70.webp?dr=9606&idc=useast2b&ps=87d6e48a&refresh_token=ac6fedfc&s=COMMENT_LIST&sc=avatar&shcp=ff37627b&shp=30310797&t=223449c4&x-expires=1785927600&x-signature=Zxy%2BmvMJIGVUUYEmnl00HSp3DAw%3D"
      },
      {
        "id": "7653041079252517640",
        "text": "jir Luh gimana pelenger itu nya kalau 1 rb?",
        "author": "oficial_tod",
        "authorId": "7234539502412661762",
        "authorSecUid": "MS4wLjABAAAA_P7z2-T5tb6-7diIytCkwubkz9X3aTjEJRTL3dyqKF4us7kTCfD4xLC-T0U5Y1_i",
        "authorName": "it's me Gung",
        "commentLanguage": "id",
        "likeCount": 36,
        "publishedAt": "2026-06-19T09:48:12.000Z",
        "verified": false,
        "profileImage": "https://p16-common-sign.tiktokcdn-eu.com/tos-alisg-avt-0068/34e550efa4bd9aec97d7de21011f1d5d~tplv-tiktokx-cropcenter-q:100:100:q70.webp?dr=9606&idc=useast2b&ps=87d6e48a&refresh_token=2a2de674&s=COMMENT_LIST&sc=avatar&shcp=ff37627b&shp=30310797&t=223449c4&x-expires=1785927600&x-signature=bQkU37mEQOdeUjb3fGbHZXwRf8g%3D"
      }
    ],
    "nextCursor": "10",
    "hasMore": true
  },
  "tiktok-comments": {
    "platform": "tiktok",
    "url": "https://www.tiktok.com/@khaby.lame/video/7646812028874673439",
    "totalComments": 824,
    "totalReturned": 6,
    "comments": [
      {
        "id": "7646834545992696596",
        "text": "Mr beast 500 million 🥰🇧🇩",
        "author": "yeasin3344556677",
        "authorAvatarUrl": "https://p16-common-sign.tiktokcdn-eu.com/tos-alisg-avt-0068/1e20d2d83b1200c623f0dec26603356f~tplv-tiktokx-cropcenter-q:100:100:q70.webp?dr=9606&idc=useast2b&ps=87d6e48a&refresh_token=7098d2d1&s=COMMENT_LIST&sc=avatar&shcp=5597e28e&shp=30310797&t=223449c4&x-expires=1784300400&x-signature=%2FbEc5ajSBQOMXt9rOeQY8GO%2Beh8%3D",
        "likeCount": 223,
        "publishedAt": "2026-06-02T16:23:41.000Z",
        "authorId": "6958917445306926086",
        "commentLanguage": "en",
        "replyCount": 14,
        "authorSecUid": null
      },
      {
        "id": "7647102586621297429",
        "text": "С каждым лайком нос растёт",
        "author": "gudingar",
        "authorAvatarUrl": "https://p16-common-sign.tiktokcdn-eu.com/tos-alisg-avt-0068/56317ccbf99872b4f14448d7fb959826~tplv-tiktokx-cropcenter-q:100:100:q70.webp?dr=9606&idc=useast2b&ps=87d6e48a&refresh_token=9f5971b4&s=COMMENT_LIST&sc=avatar&shcp=5597e28e&shp=30310797&t=223449c4&x-expires=1784300400&x-signature=FXHzE%2FNLM2v17bh45RTPVfe8%2BDA%3D",
        "likeCount": 635,
        "publishedAt": "2026-06-03T09:43:54.000Z",
        "authorId": "6958917445306926086",
        "commentLanguage": "ru",
        "replyCount": 0,
        "authorSecUid": null
      }
    ],
    "nextCursor": "6",
    "hasMore": true
  },
  "tiktok-live": {
    "platform": "tiktok",
    "username": "tiktok",
    "isLive": false,
    "status": 4,
    "creator": {
      "id": "107955",
      "secUid": "MS4wLjABAAAAv7iSuuXDJGDvJkmH_vz1qkDZYo1apxgzaxdBSeIuPiM",
      "displayName": "TikTok",
      "followers": 95001558,
      "following": 0,
      "verified": true,
      "avatar": "https://p16-common-sign.tiktokcdn.com/tos-maliva-avt-0068/ba67b11de451691939223e9d978e613a~tplv-tiktokx-cropcenter:1080:1080.webp?dr=14579&refresh_token=fda4fb51&x-expires=1785409200&x-signature=hllLSTX4jvetwRoYU5uQBOOaWpA%3D&t=4d5b0474&ps=13740610&shp=a5d48078&shcp=fdd36af4&idc=my2",
      "bio": "One TikTok can make a big impact",
      "status": 4
    },
    "room": {
      "id": "7665499080323353358",
      "streamId": "3578537941258994614",
      "status": 4,
      "title": "In the Mix LIVE with Josh Groban",
      "startedAt": "2026-07-22T23:32:31.000Z",
      "totalEnterCount": 74810,
      "coverUrl": "https://p16-common-sign.tiktokcdn.com/tos-maliva-avt-0068/ba67b11de451691939223e9d978e613a~tplv-tiktokx-cropcenter:720:720.webp?dr=14579&refresh_token=e000a24d&x-expires=1785409200&x-signature=51yzrCy7oc%2Bx3QXPywEmNE7foSU%3D&t=4d5b0474&ps=13740610&shp=a5d48078&shcp=fdd36af4&idc=my2",
      "liveSubOnly": false,
      "gameTagId": 0,
      "liveRoomMode": 1,
      "paidEvent": {
        "eventId": 7655031505395122000,
        "paidType": 0
      },
      "streamUrls": [
        "https://pull-hls-f16-tt01.tiktokcdn.com/activity/stream-3578537941258994614_hd/index.m3u8?expire=1786446578&sign=f25ce1f7dc0090406b4ce9dd93404abf",
        "https://pull-f5-tt01.tiktokcdn.com/activity/stream-3578537941258994614_hd/index.mpd?expire=1786446578&sign=0366e791f991487f9c5aaa22382b596d"
      ],
      "streamQualities": [
        {
          "quality": "hd",
          "codec": "h264",
          "resolution": "960x540",
          "bitrate": 1200000,
          "flv": "https://pull-f5-tt01.tiktokcdn.com/activity/stream-3578537941258994614_hd.flv?expire=1786446578&sign=4e2983d0d512266f6557d5f7aabe8532",
          "hls": "https://pull-hls-f16-tt01.tiktokcdn.com/activity/stream-3578537941258994614_hd/index.m3u8?expire=1786446578&sign=f25ce1f7dc0090406b4ce9dd93404abf",
          "cmaf": "https://pull-f5-tt01.tiktokcdn.com/activity/stream-3578537941258994614_hd/index.mpd?expire=1786446578&sign=0366e791f991487f9c5aaa22382b596d",
          "dash": "https://pull-f5-tt01.tiktokcdn.com/activity/stream-3578537941258994614_hd/index.mpd?expire=1786446578&sign=0366e791f991487f9c5aaa22382b596d"
        },
        {
          "quality": "uhd",
          "codec": "h264",
          "resolution": "1280x720",
          "bitrate": 1800000,
          "flv": "https://pull-f5-tt01.tiktokcdn.com/activity/stream-3578537941258994614_uhd.flv?expire=1786446578&sign=9ca252292b4a32583d2a4fcb721ff555",
          "hls": "https://pull-hls-f16-tt01.tiktokcdn.com/activity/stream-3578537941258994614_uhd/index.m3u8?expire=1786446578&sign=2a607ea575457021435a891b4643e17c",
          "cmaf": "https://pull-f5-tt01.tiktokcdn.com/activity/stream-3578537941258994614_uhd/index.mpd?expire=1786446578&sign=7f9fe4060d52362c260ba310c4a79047",
          "dash": "https://pull-f5-tt01.tiktokcdn.com/activity/stream-3578537941258994614_uhd/index.mpd?expire=1786446578&sign=7f9fe4060d52362c260ba310c4a79047"
        }
      ],
      "streams": {
        "hd": {
          "codec": "h264",
          "resolution": "960x540",
          "bitrate": 1200000,
          "flv": "https://pull-f5-tt01.tiktokcdn.com/activity/stream-3578537941258994614_hd.flv?expire=1786446578&sign=4e2983d0d512266f6557d5f7aabe8532",
          "hls": "https://pull-hls-f16-tt01.tiktokcdn.com/activity/stream-3578537941258994614_hd/index.m3u8?expire=1786446578&sign=f25ce1f7dc0090406b4ce9dd93404abf",
          "cmaf": "https://pull-f5-tt01.tiktokcdn.com/activity/stream-3578537941258994614_hd/index.mpd?expire=1786446578&sign=0366e791f991487f9c5aaa22382b596d",
          "dash": "https://pull-f5-tt01.tiktokcdn.com/activity/stream-3578537941258994614_hd/index.mpd?expire=1786446578&sign=0366e791f991487f9c5aaa22382b596d"
        },
        "uhd": {
          "codec": "h264",
          "resolution": "1280x720",
          "bitrate": 1800000,
          "flv": "https://pull-f5-tt01.tiktokcdn.com/activity/stream-3578537941258994614_uhd.flv?expire=1786446578&sign=9ca252292b4a32583d2a4fcb721ff555",
          "hls": "https://pull-hls-f16-tt01.tiktokcdn.com/activity/stream-3578537941258994614_uhd/index.m3u8?expire=1786446578&sign=2a607ea575457021435a891b4643e17c",
          "cmaf": "https://pull-f5-tt01.tiktokcdn.com/activity/stream-3578537941258994614_uhd/index.mpd?expire=1786446578&sign=7f9fe4060d52362c260ba310c4a79047",
          "dash": "https://pull-f5-tt01.tiktokcdn.com/activity/stream-3578537941258994614_uhd/index.mpd?expire=1786446578&sign=7f9fe4060d52362c260ba310c4a79047"
        },
        "sd": {
          "codec": "h264",
          "resolution": "960x540",
          "bitrate": 800000,
          "flv": "https://pull-f5-tt01.tiktokcdn.com/activity/stream-3578537941258994614_sd.flv?expire=1786446578&sign=861979ee452b5d3894b3c02920bd96ca",
          "hls": "https://pull-hls-f16-tt01.tiktokcdn.com/activity/stream-3578537941258994614_sd/index.m3u8?expire=1786446578&sign=2b0c3c0cea33b5b1c1f16b3cc1522c2b",
          "cmaf": "https://pull-f5-tt01.tiktokcdn.com/activity/stream-3578537941258994614_sd/index.mpd?expire=1786446578&sign=54f12793a9b2ec076d77333e3f87eeb7",
          "dash": "https://pull-f5-tt01.tiktokcdn.com/activity/stream-3578537941258994614_sd/index.mpd?expire=1786446578&sign=54f12793a9b2ec076d77333e3f87eeb7"
        },
        "ld": {
          "codec": "h264",
          "resolution": "640x360",
          "bitrate": 600000,
          "flv": "https://pull-f5-tt01.tiktokcdn.com/activity/stream-3578537941258994614_ld.flv?expire=1786446578&sign=33fed68846450e6976f0c3be345a75f9",
          "hls": "https://pull-hls-f16-tt01.tiktokcdn.com/activity/stream-3578537941258994614_ld/index.m3u8?expire=1786446578&sign=d8bfbecab958947a7b8ca5f9bf37b3b7",
          "cmaf": "https://pull-f5-tt01.tiktokcdn.com/activity/stream-3578537941258994614_ld/index.mpd?expire=1786446578&sign=00541c1a83a5cd336565ffe7a33f51cf",
          "dash": "https://pull-f5-tt01.tiktokcdn.com/activity/stream-3578537941258994614_ld/index.mpd?expire=1786446578&sign=00541c1a83a5cd336565ffe7a33f51cf"
        }
      }
    }
  },
  "tiktok-live-info": {
    "platform": "tiktok",
    "username": "tiktok",
    "isLive": false,
    "status": 4,
    "creator": {
      "id": "107955",
      "secUid": "MS4wLjABAAAAv7iSuuXDJGDvJkmH_vz1qkDZYo1apxgzaxdBSeIuPiM",
      "displayName": "TikTok",
      "followers": 95001558,
      "following": 0,
      "verified": true,
      "avatar": "https://p16-common-sign.tiktokcdn.com/tos-maliva-avt-0068/ba67b11de451691939223e9d978e613a~tplv-tiktokx-cropcenter:1080:1080.webp?dr=14579&refresh_token=fda4fb51&x-expires=1785409200&x-signature=hllLSTX4jvetwRoYU5uQBOOaWpA%3D&t=4d5b0474&ps=13740610&shp=a5d48078&shcp=fdd36af4&idc=my2",
      "bio": "One TikTok can make a big impact",
      "status": 4
    },
    "room": {
      "id": "7665499080323353358",
      "streamId": "3578537941258994614",
      "status": 4,
      "title": "In the Mix LIVE with Josh Groban",
      "startedAt": "2026-07-22T23:32:31.000Z",
      "totalEnterCount": 74810,
      "coverUrl": "https://p16-common-sign.tiktokcdn.com/tos-maliva-avt-0068/ba67b11de451691939223e9d978e613a~tplv-tiktokx-cropcenter:720:720.webp?dr=14579&refresh_token=e000a24d&x-expires=1785409200&x-signature=51yzrCy7oc%2Bx3QXPywEmNE7foSU%3D&t=4d5b0474&ps=13740610&shp=a5d48078&shcp=fdd36af4&idc=my2",
      "liveSubOnly": false,
      "gameTagId": 0,
      "liveRoomMode": 1,
      "paidEvent": {
        "eventId": 7655031505395122000,
        "paidType": 0
      },
      "streamUrls": [
        "https://pull-hls-f16-tt01.tiktokcdn.com/activity/stream-3578537941258994614_hd/index.m3u8?expire=1786446578&sign=f25ce1f7dc0090406b4ce9dd93404abf",
        "https://pull-f5-tt01.tiktokcdn.com/activity/stream-3578537941258994614_hd/index.mpd?expire=1786446578&sign=0366e791f991487f9c5aaa22382b596d"
      ],
      "streamQualities": [
        {
          "quality": "hd",
          "codec": "h264",
          "resolution": "960x540",
          "bitrate": 1200000,
          "flv": "https://pull-f5-tt01.tiktokcdn.com/activity/stream-3578537941258994614_hd.flv?expire=1786446578&sign=4e2983d0d512266f6557d5f7aabe8532",
          "hls": "https://pull-hls-f16-tt01.tiktokcdn.com/activity/stream-3578537941258994614_hd/index.m3u8?expire=1786446578&sign=f25ce1f7dc0090406b4ce9dd93404abf",
          "cmaf": "https://pull-f5-tt01.tiktokcdn.com/activity/stream-3578537941258994614_hd/index.mpd?expire=1786446578&sign=0366e791f991487f9c5aaa22382b596d",
          "dash": "https://pull-f5-tt01.tiktokcdn.com/activity/stream-3578537941258994614_hd/index.mpd?expire=1786446578&sign=0366e791f991487f9c5aaa22382b596d"
        },
        {
          "quality": "uhd",
          "codec": "h264",
          "resolution": "1280x720",
          "bitrate": 1800000,
          "flv": "https://pull-f5-tt01.tiktokcdn.com/activity/stream-3578537941258994614_uhd.flv?expire=1786446578&sign=9ca252292b4a32583d2a4fcb721ff555",
          "hls": "https://pull-hls-f16-tt01.tiktokcdn.com/activity/stream-3578537941258994614_uhd/index.m3u8?expire=1786446578&sign=2a607ea575457021435a891b4643e17c",
          "cmaf": "https://pull-f5-tt01.tiktokcdn.com/activity/stream-3578537941258994614_uhd/index.mpd?expire=1786446578&sign=7f9fe4060d52362c260ba310c4a79047",
          "dash": "https://pull-f5-tt01.tiktokcdn.com/activity/stream-3578537941258994614_uhd/index.mpd?expire=1786446578&sign=7f9fe4060d52362c260ba310c4a79047"
        }
      ],
      "streams": {
        "hd": {
          "codec": "h264",
          "resolution": "960x540",
          "bitrate": 1200000,
          "flv": "https://pull-f5-tt01.tiktokcdn.com/activity/stream-3578537941258994614_hd.flv?expire=1786446578&sign=4e2983d0d512266f6557d5f7aabe8532",
          "hls": "https://pull-hls-f16-tt01.tiktokcdn.com/activity/stream-3578537941258994614_hd/index.m3u8?expire=1786446578&sign=f25ce1f7dc0090406b4ce9dd93404abf",
          "cmaf": "https://pull-f5-tt01.tiktokcdn.com/activity/stream-3578537941258994614_hd/index.mpd?expire=1786446578&sign=0366e791f991487f9c5aaa22382b596d",
          "dash": "https://pull-f5-tt01.tiktokcdn.com/activity/stream-3578537941258994614_hd/index.mpd?expire=1786446578&sign=0366e791f991487f9c5aaa22382b596d"
        },
        "uhd": {
          "codec": "h264",
          "resolution": "1280x720",
          "bitrate": 1800000,
          "flv": "https://pull-f5-tt01.tiktokcdn.com/activity/stream-3578537941258994614_uhd.flv?expire=1786446578&sign=9ca252292b4a32583d2a4fcb721ff555",
          "hls": "https://pull-hls-f16-tt01.tiktokcdn.com/activity/stream-3578537941258994614_uhd/index.m3u8?expire=1786446578&sign=2a607ea575457021435a891b4643e17c",
          "cmaf": "https://pull-f5-tt01.tiktokcdn.com/activity/stream-3578537941258994614_uhd/index.mpd?expire=1786446578&sign=7f9fe4060d52362c260ba310c4a79047",
          "dash": "https://pull-f5-tt01.tiktokcdn.com/activity/stream-3578537941258994614_uhd/index.mpd?expire=1786446578&sign=7f9fe4060d52362c260ba310c4a79047"
        },
        "sd": {
          "codec": "h264",
          "resolution": "960x540",
          "bitrate": 800000,
          "flv": "https://pull-f5-tt01.tiktokcdn.com/activity/stream-3578537941258994614_sd.flv?expire=1786446578&sign=861979ee452b5d3894b3c02920bd96ca",
          "hls": "https://pull-hls-f16-tt01.tiktokcdn.com/activity/stream-3578537941258994614_sd/index.m3u8?expire=1786446578&sign=2b0c3c0cea33b5b1c1f16b3cc1522c2b",
          "cmaf": "https://pull-f5-tt01.tiktokcdn.com/activity/stream-3578537941258994614_sd/index.mpd?expire=1786446578&sign=54f12793a9b2ec076d77333e3f87eeb7",
          "dash": "https://pull-f5-tt01.tiktokcdn.com/activity/stream-3578537941258994614_sd/index.mpd?expire=1786446578&sign=54f12793a9b2ec076d77333e3f87eeb7"
        },
        "ld": {
          "codec": "h264",
          "resolution": "640x360",
          "bitrate": 600000,
          "flv": "https://pull-f5-tt01.tiktokcdn.com/activity/stream-3578537941258994614_ld.flv?expire=1786446578&sign=33fed68846450e6976f0c3be345a75f9",
          "hls": "https://pull-hls-f16-tt01.tiktokcdn.com/activity/stream-3578537941258994614_ld/index.m3u8?expire=1786446578&sign=d8bfbecab958947a7b8ca5f9bf37b3b7",
          "cmaf": "https://pull-f5-tt01.tiktokcdn.com/activity/stream-3578537941258994614_ld/index.mpd?expire=1786446578&sign=00541c1a83a5cd336565ffe7a33f51cf",
          "dash": "https://pull-f5-tt01.tiktokcdn.com/activity/stream-3578537941258994614_ld/index.mpd?expire=1786446578&sign=00541c1a83a5cd336565ffe7a33f51cf"
        }
      }
    }
  },
  "tiktok-music-posts": {
    "url": "https://www.tiktok.com/music/original-sound-7646812079113898783",
    "totalReturned": 4,
    "posts": [
      {
        "platform": "tiktok",
        "url": "https://www.tiktok.com/@khaby.lame/video/7646812028874673439",
        "id": "7646812028874673439",
        "caption": "Thank you, please come again!!!🙋🏿‍♂️💸#learnfromkhaby #comedy",
        "description": "Thank you, please come again!!!🙋🏿‍♂️💸#learnfromkhaby #comedy",
        "publishedAt": "2026-06-02T14:56:35.000Z",
        "durationSeconds": 29.534,
        "thumbnailUrl": "https://p16-common-sign.tiktokcdn.com/tos-useast8-p-0068-tx2/oUAHVIiQDac8uC75AEfyALAA1FrTAqEEQ3GRPe~tplv-tiktokx-cropcenter-q:300:400:q70.webp?dr=14782&refresh_token=dae473d0&x-expires=1785171600&x-signature=fF8KccMCj5i1KJP7krB7JRx2xG0%3D&t=bacd0480&ps=933b5bde&shp=d05b14bd&shcp=f6441914&idc=my2&biz_tag=tt_video&s=MUSIC_AWEME&sc=cover",
        "author": {
          "username": "khaby.lame",
          "displayName": "Khabane lame",
          "url": "https://www.tiktok.com/@khaby.lame",
          "verified": null,
          "profileImage": "https://p16-common-sign.tiktokcdn.com/tos-maliva-avt-0068/08987e23b94057953fd4f1738694bf5f~tplv-tiktokx-cropcenter-q:1080:1080:q70.webp?dr=10796&idc=my2&ps=87d6e48a&refresh_token=bc21b726&s=MUSIC_AWEME&sc=avatar&shcp=f6441914&shp=d05b14bd&t=223449c4&x-expires=1785171600&x-signature=D%2FanX%2BEAwPGclXui5sL48ejAGUk%3D",
          "id": null,
          "secUid": null,
          "followers": null
        },
        "engagement": {
          "views": 17042375,
          "likes": 1550817,
          "comments": 16306,
          "shares": 16050,
          "saves": 62013
        },
        "hashtags": [
          "learnfromkhaby",
          "comedy"
        ],
        "musicName": "original sound - khaby.lame",
        "mentions": [],
        "isAd": false,
        "isPaidPartnership": false,
        "musicId": "7646812079113898783"
      },
      {
        "platform": "tiktok",
        "url": "https://www.tiktok.com/@ali.chai.wala777/video/7649043187192892703",
        "id": "7649043187192892703",
        "caption": "کربلا دے مدان اندر حسین رتبے ودادیتے ہن#okaratiktokstar #tiktokpakastan #okaralover💪💪❤️ #alichaiwala❤️💫 #tiktok #support #trending #foruyou #1m @kanwal Shahzadi @Rehmani Munda🇸🇦 @Jani 227 @Rock Kuri Rock Kuri @Tayyab Jutt001 @👑 اوکاڑہ آلے 🔥 ملک جی 👑786 @RAJAB EDITS @(◐‿◑)🅼🅴ح🅰🆁 🆂🅷🅾🅰🅸🅱 ヅ @jutti of okara🫣 @☠️Talent of okara ☠️ @AsiM 🔥shah👑372 @👑Asim Ali.777🦁👑 @👑 *B.Ƥu𝗇ᴊa𝚋i* 💸🔥 @Kʜᴀᴍᴏsʜ⚜️Dᴀʀɪɴᴅᴀ🔞🥷 @B Punjabi 💸 @👑★Zαɾί khan★💸🔥 @Mr Motu patlu ❤️777 @Rizwan Honey @M.A.A.N✨ @alirazaofficial3100",
        "description": "کربلا دے مدان اندر حسین رتبے ودادیتے ہن#okaratiktokstar #tiktokpakastan #okaralover💪💪❤️ #alichaiwala❤️💫 #tiktok #support #trending #foruyou #1m @kanwal Shahzadi @Rehmani Munda🇸🇦 @Jani 227 @Rock Kuri Rock Kuri @Tayyab Jutt001 @👑 اوکاڑہ آلے 🔥 ملک جی 👑786 @RAJAB EDITS @(◐‿◑)🅼🅴ح🅰🆁 🆂🅷🅾🅰🅸🅱 ヅ @jutti of okara🫣 @☠️Talent of okara ☠️ @AsiM 🔥shah👑372 @👑Asim Ali.777🦁👑 @👑 *B.Ƥu𝗇ᴊa𝚋i* 💸🔥 @Kʜᴀᴍᴏsʜ⚜️Dᴀʀɪɴᴅᴀ🔞🥷 @B Punjabi 💸 @👑★Zαɾί khan★💸🔥 @Mr Motu patlu ❤️777 @Rizwan Honey @M.A.A.N✨ @alirazaofficial3100",
        "publishedAt": "2026-06-08T15:14:35.000Z",
        "durationSeconds": 30.278,
        "thumbnailUrl": "https://p16-common-sign.tiktokcdn.com/tos-useast8-p-0068-tx2/oYAxEVEDAzfEerjA3qtmExMIFAFo9RAJtYCH0A~tplv-tiktokx-cropcenter-q:300:400:q70.webp?dr=14782&refresh_token=359f3e3f&x-expires=1785171600&x-signature=KMkCqspUhLIxRLEttCZ30drzHpQ%3D&t=bacd0480&ps=933b5bde&shp=d05b14bd&shcp=f6441914&idc=my2&biz_tag=tt_video&s=MUSIC_AWEME&sc=cover",
        "author": {
          "username": "ali.chai.wala777",
          "displayName": "Ali chai wala 777☕☕",
          "url": "https://www.tiktok.com/@ali.chai.wala777",
          "verified": null,
          "profileImage": "https://p16-common-sign.tiktokcdn.com/tos-maliva-avt-0068/7b938fef8c8e68e37c261c961ccc7560~tplv-tiktokx-cropcenter-q:1080:1080:q70.webp?dr=10796&idc=my2&ps=87d6e48a&refresh_token=48c28ab9&s=MUSIC_AWEME&sc=avatar&shcp=f6441914&shp=d05b14bd&t=223449c4&x-expires=1785171600&x-signature=De8%2FtfqqeKjQKCfU%2Bw%2BfTGJFIlU%3D",
          "id": null,
          "secUid": null,
          "followers": null
        },
        "engagement": {
          "views": 844,
          "likes": 142,
          "comments": 27,
          "shares": 57,
          "saves": 11
        },
        "hashtags": [
          "okaratiktokstar",
          "tiktokpakastan"
        ],
        "musicName": "original sound - khaby.lame",
        "mentions": [],
        "isAd": false,
        "isPaidPartnership": false,
        "musicId": "7646812079113898783"
      }
    ]
  },
  "tiktok-popular-creators": {
    "platform": "tiktok",
    "country": "US",
    "sort": "follower",
    "totalReturned": 5,
    "creators": [
      {
        "username": "katseyeworld",
        "displayName": "KATSEYE",
        "url": "https://www.tiktok.com/@katseyeworld",
        "bio": "welcome to KATSEYE world 🌐\nAnimal out now\nWILD out august 14",
        "followers": 19507494,
        "engagementRate": 4.1314,
        "likes": 1053364775,
        "videos": 1307,
        "verified": true,
        "profileImage": "https://p19-common-sign.tiktokcdn-us.com/tos-useast5-avt-0068-tx/fc2aacc9ec77e5e3290fbfda46e40cd2~tplv-tiktokx-cropcenter:1080:1080.jpeg?dr=9640&refresh_token=fdad94e0&x-expires=1785409200&x-signature=jNHL5Y3uuYeocjKv709yl4MyWG8%3D&t=4d5b0474&ps=13740610&shp=a5d48078&shcp=81f88b70&idc=useast8",
        "rank": 1,
        "engagementRateBasis": "avgLikesPerVideo/followers",
        "region": null,
        "avgViews": null
      },
      {
        "username": "samaraispinkk",
        "displayName": "Secret",
        "url": "https://www.tiktok.com/@samaraispinkk",
        "bio": "I am pink diva mermaid queen and Samara \n💌- Samara@tiddle.io\nSnap is lit",
        "followers": 6173962,
        "engagementRate": 6.5222,
        "likes": 548849706,
        "videos": 1363,
        "verified": false,
        "profileImage": "https://p19-common-sign.tiktokcdn-us.com/tos-useast5-avt-0068-tx/a5efb96291b21db624033e417de1efc9~tplv-tiktokx-cropcenter:1080:1080.jpeg?dr=9640&refresh_token=0982d22c&x-expires=1785409200&x-signature=Wu213hPipMQFhk3VhLFyRMdq7D4%3D&t=4d5b0474&ps=13740610&shp=a5d48078&shcp=81f88b70&idc=useast8",
        "rank": 2,
        "engagementRateBasis": "avgLikesPerVideo/followers",
        "region": null,
        "avgViews": null,
        "contact": {
          "emails": [
            "Samara@tiddle.io"
          ],
          "links": []
        }
      }
    ]
  },
  "tiktok-popular-hashtags": {
    "query": "skincare",
    "discovery": "co_occurrence",
    "discoverySource": "hashtag_page",
    "sampleSize": 20,
    "rankBy": "videoCount",
    "fetchedAt": "2026-08-03T15:08:07.000Z",
    "totalReturned": 2,
    "hashtags": [
      {
        "name": "skincare",
        "url": "https://www.tiktok.com/tag/skincare",
        "rank": 1,
        "hashtagId": "504245",
        "videoCount": 56953998,
        "totalPlays": 954780316160,
        "sampleVideoCount": 17,
        "samplePlays": 40305805,
        "growthRate": null
      },
      {
        "name": "skincareroutine",
        "url": "https://www.tiktok.com/tag/skincareroutine",
        "rank": 2,
        "hashtagId": "42164",
        "videoCount": 8200000,
        "totalPlays": 120000000000,
        "sampleVideoCount": 5,
        "samplePlays": 3003805,
        "growthRate": null
      }
    ]
  },
  "tiktok-profile-region": {
    "platform": "tiktok",
    "username": "khaby.lame",
    "displayName": "Khabane lame",
    "url": "https://www.tiktok.com/@khaby.lame",
    "id": "127905465618821121",
    "secUid": "MS4wLjABAAAAwAg0rSzO65WQfz4RzQgGv2Xdv108BgPXhRrrmNVIHQZ9PO8-flwwRtEppYTS0OjA",
    "createTime": "2016-08-10T22:02:34.000Z",
    "createTimeUnix": 1470866554,
    "ttSeller": false,
    "isOrganization": 0,
    "region": "IT",
    "language": "en",
    "followers": 162355782,
    "following": 81,
    "likes": 2642875898,
    "videos": 1343,
    "verified": true,
    "private": false,
    "profileImage": "https://p19-common-sign.tiktokcdn-us.com/tos-useast8-avt-0068-tx2/08987e23b94057953fd4f1738694bf5f~tplv-tiktokx-cropcenter:1080:1080.jpeg?dr=9640&refresh_token=bf39da46&x-expires=1784628000&x-signature=%2BIQ2jcCwEJiHbixnVnOi2G2qh5E%3D&t=4d5b0474&ps=13740610&shp=a5d48078&shcp=81f88b70&idc=useast8",
    "raw": {
      "user": {
        "id": "127905465618821121",
        "shortId": "",
        "uniqueId": "khaby.lame",
        "nickname": "Khabane lame",
        "avatarLarger": "https://p19-common-sign.tiktokcdn-us.com/tos-useast8-avt-0068-tx2/08987e23b94057953fd4f1738694bf5f~tplv-tiktokx-cropcenter:1080:1080.jpeg?dr=9640&refresh_token=bf39da46&x-expires=1784628000&x-signature=%2BIQ2jcCwEJiHbixnVnOi2G2qh5E%3D&t=4d5b0474&ps=13740610&shp=a5d48078&shcp=81f88b70&idc=useast8",
        "avatarMedium": "https://p19-common-sign.tiktokcdn-us.com/tos-useast8-avt-0068-tx2/08987e23b94057953fd4f1738694bf5f~tplv-tiktokx-cropcenter:720:720.jpeg?dr=9640&refresh_token=0ed06557&x-expires=1784628000&x-signature=WrS0%2Bg%2FT%2BKycLjzRdl%2Fzdc5i5H0%3D&t=4d5b0474&ps=13740610&shp=a5d48078&shcp=81f88b70&idc=useast8",
        "avatarThumb": "https://p16-common-sign.tiktokcdn-us.com/tos-useast8-avt-0068-tx2/08987e23b94057953fd4f1738694bf5f~tplv-tiktokx-cropcenter:100:100.jpeg?dr=9640&refresh_token=913c08ee&x-expires=1784628000&x-signature=nJ6FpgyLtkWHGaHctQAjTQiqRfE%3D&t=4d5b0474&ps=13740610&shp=a5d48078&shcp=81f88b70&idc=useast8",
        "signature": "Se vuoi ridere sei nel posto giusto😎 If u wanna laugh u r in the right place😎",
        "createTime": 1470866554,
        "verified": true,
        "secUid": "MS4wLjABAAAAwAg0rSzO65WQfz4RzQgGv2Xdv108BgPXhRrrmNVIHQZ9PO8-flwwRtEppYTS0OjA",
        "ftc": false,
        "relation": 0,
        "openFavorite": false,
        "commentSetting": 0,
        "commerceUserInfo": {
          "commerceUser": false
        },
        "duetSetting": 0,
        "stitchSetting": 0,
        "privateAccount": false,
        "secret": false,
        "isADVirtual": false,
        "roomId": "",
        "uniqueIdModifyTime": 0,
        "ttSeller": false,
        "downloadSetting": 0,
        "profileTab": {
          "showMusicTab": false,
          "showQuestionTab": false,
          "showPlayListTab": false
        },
        "followingVisibility": 1,
        "recommendReason": "",
        "nowInvitationCardUrl": "",
        "nickNameModifyTime": 0,
        "isEmbedBanned": false,
        "canExpPlaylist": true,
        "profileEmbedPermission": 1,
        "language": "en",
        "eventList": [],
        "suggestAccountBind": false,
        "isOrganization": 0,
        "UserStoryStatus": 0,
        "shortDramaCreator": {}
      },
      "statsV2": {
        "followerCount": 162355782,
        "followingCount": 81,
        "heart": 2642875898,
        "heartCount": 2642875898,
        "videoCount": 1343,
        "diggCount": 0,
        "friendCount": 77
      }
    },
    "regionConfidence": "high",
    "regionSource": "inferred"
  },
  "tiktok-search-by-hashtag": {
    "query": "comedy",
    "totalReturned": 5,
    "hasMore": true,
    "nextCursor": 5,
    "results": [
      {
        "platform": "tiktok",
        "url": "https://www.tiktok.com/@comedy7092/video/7608140015578746142",
        "id": "7608140015578746142",
        "caption": null,
        "description": null,
        "publishedAt": "2026-02-18T09:50:20.000Z",
        "durationSeconds": 32.0,
        "thumbnailUrl": "https://p16-common-sign.tiktokcdn.com/tos-useast8-p-0068-tx2/oIviaAAABRimBWuVioEEIVaURRRniVLt1xZVY~tplv-tiktokx-origin.image?dr=14575&x-expires=1785405600&x-signature=OKU2GXpXqsBhsKCylTn59HMWbDk%3D&t=4d5b0474&ps=13740610&shp=81f88b70&shcp=43f4a2f9&idc=my",
        "author": {
          "username": "comedy7092",
          "displayName": "Comedy",
          "url": "https://www.tiktok.com/@comedy7092",
          "followers": 281600,
          "verified": false,
          "profileImage": "https://p16-common-sign.tiktokcdn.com/tos-maliva-avt-0068/f4091ee4a3e184d77536b3493fd444a7~tplv-tiktokx-cropcenter:1080:1080.jpeg?dr=14579&refresh_token=64f29985&x-expires=1785405600&x-signature=jG8jorN693uq%2FHXEnFVyfDrBle0%3D&t=4d5b0474&ps=13740610&shp=a5d48078&shcp=81f88b70&idc=my"
        },
        "engagement": {
          "views": 2200000,
          "likes": 100800,
          "comments": 792,
          "shares": 26700,
          "saves": 9426
        },
        "hashtags": [],
        "musicName": "original sound"
      },
      {
        "platform": "tiktok",
        "url": "https://www.tiktok.com/@comedy7092/video/7607028622318259487",
        "id": "7607028622318259487",
        "caption": null,
        "description": null,
        "publishedAt": "2026-02-15T09:57:37.000Z",
        "durationSeconds": 43.0,
        "thumbnailUrl": "https://p16-common-sign.tiktokcdn.com/tos-useast8-p-0068-tx2/oUfpTTR6EmDkARPECmFhLE2JEEovIABfZMAVFA~tplv-tiktokx-origin.image?dr=14575&x-expires=1785405600&x-signature=zhrEEs8JX2GlL1em5RJmsg4bu%2F4%3D&t=4d5b0474&ps=13740610&shp=81f88b70&shcp=43f4a2f9&idc=my",
        "author": {
          "username": "comedy7092",
          "displayName": "Comedy",
          "url": "https://www.tiktok.com/@comedy7092",
          "followers": 281600,
          "verified": false,
          "profileImage": "https://p16-common-sign.tiktokcdn.com/tos-maliva-avt-0068/f4091ee4a3e184d77536b3493fd444a7~tplv-tiktokx-cropcenter:1080:1080.jpeg?dr=14579&refresh_token=64f29985&x-expires=1785405600&x-signature=jG8jorN693uq%2FHXEnFVyfDrBle0%3D&t=4d5b0474&ps=13740610&shp=a5d48078&shcp=81f88b70&idc=my"
        },
        "engagement": {
          "views": 4700000,
          "likes": 156100,
          "comments": 1140,
          "shares": 4276,
          "saves": 12400
        },
        "hashtags": [],
        "musicName": "original sound"
      }
    ]
  },
  "tiktok-search-suggestions": {
    "platform": "tiktok",
    "query": "makeup",
    "totalReturned": 5,
    "suggestions": [
      {
        "seed": "makeup",
        "suggestion": "makeup tutorial",
        "rank": 1,
        "searchUrl": "https://www.tiktok.com/search?q=makeup+tutorial",
        "region": "US",
        "language": "en-US"
      },
      {
        "seed": "makeup",
        "suggestion": "makeup brush set",
        "rank": 2,
        "searchUrl": "https://www.tiktok.com/search?q=makeup+brush+set",
        "region": "US",
        "language": "en-US"
      }
    ]
  },
  "tiktok-search-users": {
    "query": "khaby",
    "totalReturned": 5,
    "hasMore": true,
    "nextCursor": 30,
    "users": [
      {
        "id": "127905465618821121",
        "secUid": "MS4wLjABAAAAwAg0rSzO65WQfz4RzQgGv2Xdv108BgPXhRrrmNVIHQZ9PO8-flwwRtEppYTS0OjA",
        "username": "khaby.lame",
        "displayName": "Khabane lame",
        "bio": "Se vuoi ridere sei nel posto giusto😎 If u wanna laugh u r in the right place😎",
        "url": "https://www.tiktok.com/@khaby.lame",
        "followers": 162476412,
        "following": 81,
        "likes": 2650481169,
        "verified": true,
        "profileImage": "https://p19-common-sign.tiktokcdn-us.com/tos-useast8-avt-0068-tx2/08987e23b94057953fd4f1738694bf5f~tplv-tiktokx-cropcenter:1080:1080.jpeg?dr=9640&refresh_token=ef0e9f02&x-expires=1786006800&x-signature=7Mx8iglAOcSlnXlc8QyIBifQV0M%3D&t=4d5b0474&ps=13740610&shp=a5d48078&shcp=81f88b70&idc=useast8"
      },
      {
        "id": "6663294979903422470",
        "secUid": "MS4wLjABAAAAbq-1Yqpp1a6u5KbV_sMg93_FK7AN3d6MJeZ3H0Yj3vZXOtqFXXjc2TIkMW7flCxX",
        "username": "espn",
        "displayName": "ESPN",
        "bio": "Serving Sports Fans. Anytime. Anywhere.",
        "url": "https://www.tiktok.com/@espn",
        "followers": 60100768,
        "following": 657,
        "likes": 5769632093,
        "verified": true,
        "profileImage": "https://p16-common-sign.tiktokcdn-us.com/tos-maliva-avt-0068/7310257743653240837~tplv-tiktokx-cropcenter:1080:1080.jpeg?dr=9640&refresh_token=7e4745a7&x-expires=1786006800&x-signature=cJrkoOAcA8KBqdaAWgBgeaE6f6w%3D&t=4d5b0474&ps=13740610&shp=a5d48078&shcp=81f88b70&idc=useast8"
      }
    ]
  },
  "tiktok-shop-product-details": {
    "platform": "tiktok_shop",
    "id": "1731098552908944370",
    "url": "https://shop.tiktok.com/us/pdp/trendy-pink-ed-hardy-tough-phone-cases-impact-resistant-wireless-charging-shock-absorption/1731098552908944370?source=product_detail&enter_method=url_semantic_301",
    "title": "Trendy Pink Ed Hardy Inspired Tough Phone Cases, Phone Durable, Gift, Accessories Top Trendy Phone Cases Phone Cover Hard Case Tough 2-piece Phone Case",
    "description": "Protect your phone in style with this tough phone case. This lightweight phone case is impact resistant and comes with the perfect surface in vivid detail as well as crisp color. Compatible with iPhone X, 11, 12, 13, 14, 15, 16 & more - check our available sizes.\n• 2-piece design with impact resistance and shock dispersion.\n• Materials: polycarbonate (shell), TPU (lining).\n• Interior rubber liner for extra protection (appearance may vary across phone models.\n• Supports wireless charging (not including MagSafe)\n• Lexan plastic: Developed by GE Plastics, this material is extremely strong, durable and impact resistant\n• Lay-flat bezel: Protects the screen from small scratches\n• Flexible rubber liner: Absorbs shock from impacts\n• Glossy Finish: Full color decoration with glossy finish\n• UV protected: Excellent resistance to outdoor weathering, long-term optical quality.\n• Glossy Finish: Full color decoration with glossy finish",
    "price": 22.54,
    "originalPrice": 24.09,
    "currency": "USD",
    "discount": "6%",
    "savings": "Saving $1.55",
    "rating": 4.6,
    "reviews": 48,
    "sold": 512,
    "stock": 2692,
    "image": "https://p16-oec-general-useast5.ttcdn-us.com/tos-useast5-i-omjb5zjo8w-tx/cc79ccfd6a324d548de31cb761b6c3c4~tplv-fhlh96nyum-crop-webp:794:794.webp?dr=12190&t=555f072d&ps=933b5bde&shp=8dbd94bf&shcp=e1be8f53&idc=useast5&from=2378011839",
    "seller": {
      "id": "7496126292994264050",
      "name": "Timeless Teapot Creations",
      "url": "https://www.tiktok.com/shop/store/timeless-teapot-creations/7496126292994264050",
      "rating": 4.6,
      "productCount": 85,
      "logo": "https://p16-oec-general-useast5.ttcdn-us.com/tos-useast5-i-omjb5zjo8w-tx/587383daaf8a4eaaa4dfb4c8f2b5944f~tplv-fhlh96nyum-resize-png:300:300.png?dr=12184&t=555f072d&ps=933b5bde&shp=905da467&shcp=6ce186a1&idc=useast5&from=2422056039"
    },
    "skus": [
      {
        "id": "1731098558045590514",
        "stock": 84,
        "price": 22.54,
        "originalPrice": null,
        "status": "1",
        "warehouseId": "7495541999400830766",
        "purchaseLimit": null,
        "saleProps": [
          {
            "propName": "Phone Models",
            "propValue": "iPhone 16 E"
          }
        ]
      },
      {
        "id": "1731098558045656050",
        "stock": 51,
        "price": 22.54,
        "originalPrice": null,
        "status": "1",
        "warehouseId": "7495541999400830766",
        "purchaseLimit": null,
        "saleProps": [
          {
            "propName": "Phone Models",
            "propValue": "iPhone 16"
          }
        ]
      }
    ],
    "images": [
      "https://p16-oec-general-useast5.ttcdn-us.com/tos-useast5-i-omjb5zjo8w-tx/cc79ccfd6a324d548de31cb761b6c3c4~tplv-fhlh96nyum-crop-webp:794:794.webp?dr=12190&t=555f072d&ps=933b5bde&shp=8dbd94bf&shcp=e1be8f53&idc=useast5&from=2378011839",
      "https://p16-oec-general-useast5.ttcdn-us.com/tos-useast5-i-omjb5zjo8w-tx/4fe011977a9d4350ba9d7acf0e502f52~tplv-fhlh96nyum-crop-webp:794:794.webp?dr=12190&t=555f072d&ps=933b5bde&shp=8dbd94bf&shcp=e1be8f53&idc=useast5&from=2378011839"
    ],
    "saleProperties": [
      {
        "id": "7494493199692793646",
        "name": "Phone Models",
        "values": [
          {
            "id": "7474656136961246982",
            "name": "iPhone 16 E"
          },
          {
            "id": "7495574204532655878",
            "name": "iPhone 16"
          }
        ]
      }
    ],
    "categories": [
      {
        "id": "601739",
        "name": "Phones & Electronics"
      },
      {
        "id": "909064",
        "name": "Mobile Phone Accessories"
      }
    ],
    "region": "US"
  },
  "tiktok-shop-product-reviews": {
    "url": "https://www.tiktok.com/shop/pdp/1731962298839634826",
    "totalReturned": 3,
    "reviews": [
      {
        "platform": "tiktok_shop",
        "id": "7640239119020558093",
        "rating": 5,
        "text": "I love it. It’s cute. Fits in both my small Mini Cooper and Mini Countryman cup holders. It does fit a small drink like a freeze or shake from bk,if you take off the lid.",
        "createdAt": "2026-05-15T21:49:56.991Z",
        "verifiedPurchase": true,
        "sku": "Thicc 16oz | Ice Cream",
        "country": "US",
        "author": {
          "name": "C**e"
        },
        "images": [
          "https://p16-oec-general-useast5.ttcdn-us.com/tos-useast5-i-omjb5zjo8w-tx/bc7a80f5766e438e8698430bdff2b55c~tplv-fhlh96nyum-crop-webp:300:300.webp?dr=12190&t=555f072d&ps=933b5bde&shp=8dbd94bf&shcp=607f11de&idc=useast5&from=2378011839",
          "https://p16-oec-general-useast5.ttcdn-us.com/tos-useast5-i-omjb5zjo8w-tx/7c513b397e2f4b019995d95dd7506914~tplv-fhlh96nyum-crop-webp:300:300.webp?dr=12190&t=555f072d&ps=933b5bde&shp=8dbd94bf&shcp=607f11de&idc=useast5&from=2378011839"
        ]
      },
      {
        "platform": "tiktok_shop",
        "id": "7599033354029254413",
        "rating": 4,
        "text": "This cup is indeed visually appealing. Although it does exhibit some minor flaws, specifically where the 'frost buddy' wording is engraved into the cup and the logo is not included on the engraving on the opposite side, overall it is a well-made cup. I am satisfied with my purchase.",
        "createdAt": "2026-01-24T20:50:51.887Z",
        "verifiedPurchase": true,
        "sku": "To-Go | Duck-It",
        "country": "US",
        "author": {
          "name": "M**e"
        },
        "images": [
          "https://p16-oec-general-useast5.ttcdn-us.com/tos-useast5-i-omjb5zjo8w-tx/c51c9bdf430e4991aaa5d947300410de~tplv-fhlh96nyum-crop-webp:300:300.webp?dr=12190&t=555f072d&ps=933b5bde&shp=8dbd94bf&shcp=607f11de&idc=useast5&from=2378011839",
          "https://p16-oec-general-useast5.ttcdn-us.com/tos-useast5-i-omjb5zjo8w-tx/f3ef2a7c10ec4dc7bd3446c373868f7e~tplv-fhlh96nyum-crop-webp:300:300.webp?dr=12190&t=555f072d&ps=933b5bde&shp=8dbd94bf&shcp=607f11de&idc=useast5&from=2378011839"
        ]
      }
    ]
  },
  "tiktok-shop-products": {
    "url": "https://www.tiktok.com/shop/store/goli-nutrition/7495794203056835079",
    "region": "US",
    "shopInfo": {
      "id": "7495794203056835079",
      "name": "Goli Nutrition",
      "url": "https://www.tiktok.com/shop/store/goli-nutrition/7495794203056835079",
      "logo": "https://p16-oec-general-useast5.ttcdn-us.com/tos-useast5-i-omjb5zjo8w-tx/e7478d3e93d4487a9e772fa74e10f506~tplv-fhlh96nyum-resize-webp:300:300.webp?dr=12185&t=555f072d&ps=933b5bde&shp=905da467&shcp=a6e80448&idc=useast5&from=2422056039",
      "sold": 5645819,
      "formatSold": "5.6M",
      "reviews": 401072,
      "followers": 590436,
      "rating": 4.6,
      "productCount": 55,
      "videoCount": 3919,
      "identityLabel": "OFFICIAL SHOP",
      "isOfficial": true,
      "region": "US",
      "storeScores": [
        {
          "score": 0.9935951457947075,
          "scorePercentage": "99",
          "type": 1
        },
        {
          "score": 0,
          "scorePercentage": "0",
          "type": 2
        }
      ]
    },
    "totalReturned": 5,
    "products": [
      {
        "platform": "tiktok_shop",
        "id": "1729527313880355335",
        "url": "https://www.tiktok.com/shop/pdp/ashwagandha-gummies-by-goli-ksm-66-mixed-berry-vegan-non-gmo/1729527313880355335",
        "title": "Goli Ashwagandha & Vitamin D Gummy - Mixed Berry, KSM-66, Vegan, Plant Based, Non-GMO, Gluten-Free & Gelatin Free. America's #1 Ashwagandha Brand",
        "price": 14.98,
        "originalPrice": 19.0,
        "currency": "USD",
        "discount": "21%",
        "savings": "Saving $4.02",
        "slug": "ashwagandha-gummies-by-goli-ksm-66-mixed-berry-vegan-non-gmo",
        "rating": 4.5,
        "reviews": 94492,
        "sold": 1297377,
        "image": "https://p16-oec-general-useast5.ttcdn-us.com/tos-useast5-i-omjb5zjo8w-tx/2bc69aa9f6084480beee1bb4a8db3a69~tplv-fhlh96nyum-crop-webp:1500:1500.webp?dr=12190&t=555f072d&ps=933b5bde&shp=8dbd94bf&shcp=a6e80448&idc=useast5&from=2378011839",
        "seller": {
          "id": "7495794203056835079",
          "name": "Goli Nutrition",
          "url": "https://www.tiktok.com/shop/store/goli-nutrition/7495794203056835079"
        }
      },
      {
        "platform": "tiktok_shop",
        "id": "1731194857673101831",
        "url": "https://www.tiktok.com/shop/pdp/zero-sugar-best-seller-trio-goli-ashwagandha-gummies-vegan-non-gmo/1731194857673101831",
        "title": "Zero Sugar Best Seller Trio - World's First 3-in-1 Pre, Post, Probiotic, Apple Cider Vinegar with Vitamin B12 and Probiotics To Address Bloating, Ashwagandha & L-Theanine, Vitamin D gummies. Gluten-Free, Vegan, Non-GMO & Gelatin-Free",
        "price": 35.8,
        "originalPrice": 105.0,
        "currency": "USD",
        "discount": "66%",
        "savings": "Saving $69.20",
        "slug": "zero-sugar-best-seller-trio-goli-ashwagandha-gummies-vegan-non-gmo",
        "rating": 4.5,
        "reviews": 45249,
        "sold": 992721,
        "image": "https://p16-oec-general-useast5.ttcdn-us.com/tos-useast5-i-omjb5zjo8w-tx/d3ab128a9f65482d9d8d288ccd252d50~tplv-fhlh96nyum-crop-webp:3000:3000.webp?dr=12190&t=555f072d&ps=933b5bde&shp=8dbd94bf&shcp=a6e80448&idc=useast5&from=2378011839",
        "seller": {
          "id": "7495794203056835079",
          "name": "Goli Nutrition",
          "url": "https://www.tiktok.com/shop/store/goli-nutrition/7495794203056835079"
        }
      }
    ]
  },
  "tiktok-shop-search": {
    "query": "phone case",
    "region": "US",
    "totalReturned": 5,
    "products": [
      {
        "platform": "tiktok_shop",
        "id": "1732313842426745420",
        "url": "https://shop.tiktok.com/us/pdp/plum-polka-dot-cute-phone-case-for-iphone-x-17-tough-stylish/1732313842426745420?source=product_detail&enter_method=url_semantic_301",
        "title": "Plum Polka Dot Cute Phone Case for iPhone - Durable & Stylish",
        "price": 12.68,
        "originalPrice": 21.2,
        "currency": "USD",
        "discount": "40%",
        "sold": 532,
        "image": "https://p16-oec-general-useast5.ttcdn-us.com/tos-useast5-i-omjb5zjo8w-tx/db875350dd404f64bb4b6bc79ae26a09~tplv-fhlh96nyum-crop-webp:1290:1290.webp?dr=12190&t=555f072d&ps=933b5bde&shp=8dbd94bf&shcp=607f11de&idc=useast5&from=2378011839",
        "seller": {
          "id": "7495626050433419852",
          "name": "Anthony Z Sierra Store",
          "url": "https://www.tiktok.com/shop/store/Anthony%20Z%20Sierra%20Store/7495626050433419852"
        },
        "rating": 4.8,
        "reviews": 2493,
        "savings": null
      },
      {
        "platform": "tiktok_shop",
        "id": "1731098552908944370",
        "url": "https://shop.tiktok.com/us/pdp/trendy-pink-ed-hardy-tough-phone-cases-impact-resistant-wireless-charging-shock-absorption/1731098552908944370?source=product_detail&enter_method=url_semantic_301",
        "title": "Trendy Pink Ed Hardy Inspired Tough Phone Cases, Phone Durable, Gift, Accessories Top Trendy Phone Cases Phone Cover Hard Case Tough 2-piece Phone Case",
        "price": 22.54,
        "originalPrice": 24.09,
        "currency": "USD",
        "discount": "6%",
        "sold": 512,
        "image": "https://p16-oec-general-useast5.ttcdn-us.com/tos-useast5-i-omjb5zjo8w-tx/cc79ccfd6a324d548de31cb761b6c3c4~tplv-fhlh96nyum-crop-webp:794:794.webp?dr=12190&t=555f072d&ps=933b5bde&shp=8dbd94bf&shcp=e1be8f53&idc=useast5&from=2378011839",
        "seller": {
          "id": "7496126292994264050",
          "name": "Timeless Teapot Creations",
          "url": "https://www.tiktok.com/shop/store/timeless-teapot-creations/7496126292994264050"
        },
        "rating": 4.6,
        "reviews": 48,
        "savings": "Saving $1.55"
      }
    ]
  },
  "tiktok-shop-user-showcase": {
    "username": "jeffreestar",
    "totalReturned": 5,
    "products": [
      {
        "platform": "tiktok_shop",
        "id": "1732506746746606533",
        "url": "https://shop.tiktok.com/us/pdp/1732506746746606533",
        "title": "Mini Velour Liquid Lipstick",
        "price": 14.0,
        "originalPrice": 16.0,
        "currency": "USD",
        "discount": "12%",
        "savings": "Saving $2.00",
        "rating": null,
        "reviews": null,
        "sold": 17,
        "image": "https://p16-oec-general-useast5.ttcdn-us.com/tos-useast5-i-omjb5zjo8w-tx/9ceb4f5dd37846abb870a60e99161448~tplv-fhlh96nyum-crop-webp:1080:1080.webp?dr=12190&t=555f072d&ps=933b5bde&shp=8dbd94bf&shcp=e1be8f53&idc=useast5&from=2378011839",
        "seller": {
          "id": "7494986018328054725",
          "name": "Jeffree Star Cosmetics",
          "url": "https://www.tiktok.com/shop/store/jeffree-star-cosmetics/7494986018328054725"
        },
        "skus": [
          {
            "id": "1732506746708267973",
            "stock": 934,
            "price": 14.0,
            "originalPrice": null,
            "status": "1",
            "warehouseId": "7275630065640408878",
            "purchaseLimit": null,
            "saleProps": [
              {
                "propName": "Shade",
                "propValue": "Unicorn Blood"
              }
            ]
          },
          {
            "id": "1732506746708333509",
            "stock": 933,
            "price": 14.0,
            "originalPrice": null,
            "status": "1",
            "warehouseId": "7275630065640408878",
            "purchaseLimit": null,
            "saleProps": [
              {
                "propName": "Shade",
                "propValue": "Weirdo"
              }
            ]
          }
        ],
        "images": [
          "https://p16-oec-general-useast5.ttcdn-us.com/tos-useast5-i-omjb5zjo8w-tx/9ceb4f5dd37846abb870a60e99161448~tplv-fhlh96nyum-crop-webp:1080:1080.webp?dr=12190&t=555f072d&ps=933b5bde&shp=8dbd94bf&shcp=e1be8f53&idc=useast5&from=2378011839",
          "https://p16-oec-general-useast5.ttcdn-us.com/tos-useast5-i-omjb5zjo8w-tx/100fdb52dee4424893af31d2ff333ad9~tplv-fhlh96nyum-crop-webp:1080:1080.webp?dr=12190&t=555f072d&ps=933b5bde&shp=8dbd94bf&shcp=e1be8f53&idc=useast5&from=2378011839"
        ],
        "saleProperties": [
          {
            "id": "7647188030129948433",
            "name": "Shade",
            "values": [
              {
                "id": "7034726533239670529",
                "name": "Unicorn Blood"
              },
              {
                "id": "7135522200253449990",
                "name": "Weirdo"
              }
            ]
          }
        ],
        "categories": [
          {
            "id": "601450",
            "name": "Beauty & Personal Care"
          },
          {
            "id": "848648",
            "name": "Makeup"
          }
        ]
      },
      {
        "platform": "tiktok_shop",
        "id": "1732528747218572229",
        "url": "https://shop.tiktok.com/us/pdp/1732528747218572229",
        "title": "Mini Velour Liquid Lipstick Duo - Unicorn Blood & Weirdo",
        "price": 23.0,
        "originalPrice": 27.0,
        "currency": "USD",
        "discount": "15%",
        "savings": "Saving $4.00",
        "rating": null,
        "reviews": null,
        "sold": 58,
        "image": "https://p16-oec-general-useast5.ttcdn-us.com/tos-useast5-i-omjb5zjo8w-tx/ee371e4e4208468881dcc275d0679f4b~tplv-fhlh96nyum-crop-webp:1080:1080.webp?dr=12190&t=555f072d&ps=933b5bde&shp=8dbd94bf&shcp=e1be8f53&idc=useast5&from=2378011839",
        "seller": {
          "id": "7494986018328054725",
          "name": "Jeffree Star Cosmetics",
          "url": "https://www.tiktok.com/shop/store/jeffree-star-cosmetics/7494986018328054725"
        },
        "skus": [
          {
            "id": "1732528742194582469",
            "stock": 933,
            "price": 23.0,
            "originalPrice": null,
            "status": "1",
            "warehouseId": "7275630065640408878",
            "purchaseLimit": null,
            "saleProps": [
              {
                "propName": "Combined Variations",
                "propValue": "Unicorn Blood & Weirdo"
              }
            ]
          }
        ],
        "images": [
          "https://p16-oec-general-useast5.ttcdn-us.com/tos-useast5-i-omjb5zjo8w-tx/ee371e4e4208468881dcc275d0679f4b~tplv-fhlh96nyum-crop-webp:1080:1080.webp?dr=12190&t=555f072d&ps=933b5bde&shp=8dbd94bf&shcp=e1be8f53&idc=useast5&from=2378011839",
          "https://p16-oec-general-useast5.ttcdn-us.com/tos-useast5-i-omjb5zjo8w-tx/3cd1ce9f5c3444309ba86a47485e04cf~tplv-fhlh96nyum-crop-webp:1080:1080.webp?dr=12190&t=555f072d&ps=933b5bde&shp=8dbd94bf&shcp=e1be8f53&idc=useast5&from=2378011839"
        ],
        "saleProperties": [
          {
            "id": "101212",
            "name": "Combined Variations",
            "values": [
              {
                "id": "7669580526982022925",
                "name": "Unicorn Blood & Weirdo"
              }
            ]
          }
        ],
        "categories": [
          {
            "id": "601450",
            "name": "Beauty & Personal Care"
          },
          {
            "id": "848648",
            "name": "Makeup"
          }
        ]
      }
    ]
  },
  "tiktok-song-details": {
    "platform": "tiktok",
    "url": "https://www.tiktok.com/music/Pumpin-Blood-7659457659034175489",
    "id": "7659457659034175489",
    "mid": "7659457659034175489",
    "title": "Pumpin Blood",
    "author": "TWINSICK & NONONO",
    "artists": [
      {
        "id": "6749206263416161285",
        "uid": "6749206263416161285",
        "secUid": "MS4wLjABAAAA38xoRsEaXL5TLeUkSCGHTo-RvU9P485jMPZSIiBjhQ4-uQiq3rS4FIDrP5O_Y0yW",
        "handle": "twinsick",
        "displayName": "TWINSICK",
        "verified": true,
        "avatarUrl": "https://p16-common-sign.tiktokcdn.com/tos-maliva-avt-0068/119173022434f9a952213ee3344b3539~tplv-tiktokx-cropcenter-q:168:168:q70.webp?dr=10792&idc=my2&ps=87d6e48a&refresh_token=7dd6ae52&s=MUSIC_AWEME&sc=avatar&shcp=f6441914&shp=d05b14bd&t=223449c4&x-expires=1785783600&x-signature=NqCTSbDLT8umzbrTEziv7%2FkGOI0%3D"
      },
      {
        "id": "7308738121520235553",
        "uid": "7308738121520235553",
        "secUid": "MS4wLjABAAAA4_Viygw3rG9RFqavMKpGvCNaiyjZlizM_LYw1Qe4M5eEo-MLAztgyRwUbK6vYVNT",
        "handle": "nononoofficial",
        "displayName": "NONONO",
        "verified": false,
        "avatarUrl": "https://p16-common-sign.tiktokcdn.com/tos-useast2a-avt-0068-euttp/0ce5a0d0b5f22cf5d263875e8c0a2702~tplv-tiktokx-cropcenter-q:168:168:q70.webp?dr=10792&idc=my2&ps=87d6e48a&refresh_token=f4958d29&s=MUSIC_AWEME&sc=avatar&shcp=f6441914&shp=d05b14bd&t=223449c4&x-expires=1785783600&x-signature=lhH%2BscwS89J4V4PRehJ%2F3rjbKR8%3D"
      }
    ],
    "original": false,
    "isOriginal": false,
    "isOriginalSound": false,
    "isPgc": true,
    "isAuthorArtist": true,
    "album": "Pumpin Blood",
    "duration": 46.0,
    "coverUrl": "https://p77-sg.tiktokcdn.com/aweme/720x720/tos-alisg-v-2774/ogkAESQZAtNDXBDkBAgFZTWoEfNeqjEB8AV7MC.jpeg",
    "cover": {
      "large": "https://p77-sg.tiktokcdn.com/aweme/720x720/tos-alisg-v-2774/ogkAESQZAtNDXBDkBAgFZTWoEfNeqjEB8AV7MC.jpeg",
      "medium": "https://p77-sg.tiktokcdn.com/aweme/200x200/tos-alisg-v-2774/ogkAESQZAtNDXBDkBAgFZTWoEfNeqjEB8AV7MC.jpeg",
      "thumb": "https://p77-sg.tiktokcdn.com/aweme/100x100/tos-alisg-v-2774/ogkAESQZAtNDXBDkBAgFZTWoEfNeqjEB8AV7MC.jpeg"
    },
    "playUrl": "https://sf16-ies-music-sg.tiktokcdn.com/obj/tos-alisg-ve-2774/oUBA3erMBM5LhL55CXiLQNZYpBfcqjBIingAtS",
    "usageCount": null,
    "createdAt": "2026-07-06T16:51:01.000Z",
    "createTime": 1783356661,
    "isCommerceMusic": true,
    "hasCommerceRight": false,
    "commercialRightType": 3,
    "matchedSong": {
      "id": "7659443114000369680",
      "title": "Pumpin Blood",
      "author": "TWINSICK & NONONO",
      "fullDuration": 46673.0,
      "chorusInfo": {
        "startMs": 0,
        "durationMs": 30528
      }
    },
    "musicReleaseInfo": {
      "groupReleaseDate": "2026-07-06T00:00:00.000Z",
      "groupReleaseTimestamp": 1783296000,
      "isNewReleaseSong": true
    },
    "extra": {
      "bpm": null,
      "loudnessLufs": -8.160819,
      "amplitudePeak": 1.3610525,
      "beats": {
        "audio_effect_onset": "https://sf16-ies-music-sg.tiktokcdn.com/obj/tos-alisg-v-2774/osAA6oEIIAgqFiTfrVFDceC9UIpRjtCtDBiZAl",
        "beats_tracker": "https://sf77-ies-music-sg.tiktokcdn.com/obj/tos-alisg-v-2774/oQEBvfGFLAzjne62AzRQFCuaNJJQQGAeAUXFyI",
        "energy_trace": "https://sf16-ies-music-sg.tiktokcdn.com/obj/tos-alisg-v-2774/okGP6eevAu6XULAaetqCFjaIInQB9QOAz2EAJz",
        "merged_beats": "https://sf77-ies-music-sg.tiktokcdn.com/obj/tos-alisg-v-2774/og6OlA6azQsFfaFeJEQAu6GUAhELIBjXCADven"
      }
    },
    "strongBeatUrl": "https://sf77-ies-music-sg.tiktokcdn.com/obj/tos-alisg-v-2774/oYQUDfpKtEpQEARfgAqgFBAQErZECAB0BBpAlP",
    "similarMusic": null,
    "recList": null,
    "durationSeconds": 46.0,
    "artistId": "6749206263416161285",
    "authorSecUid": "MS4wLjABAAAA38xoRsEaXL5TLeUkSCGHTo-RvU9P485jMPZSIiBjhQ4-uQiq3rS4FIDrP5O_Y0yW",
    "isExplicit": null,
    "hasLyrics": null
  },
  "tiktok-summarizer": {
    "platform": "tiktok",
    "url": "https://www.tiktok.com/@paw.dreams0/video/7660129779596659990",
    "summary": "In this playful and imaginative narrative, a child and their father embark on a creative journey to build a super-fast cardboard Ferrari. Initially, the child is excited about their cardboard creation, but soon realizes that it cannot compete on a real racing track. The father reassures the child and proposes to construct a real metal Ferrari using materials from a junkyard. Together, they work on the new car, focusing on its strength and aesthetics, ultimately transforming their dream into reality with a shiny, fast white Ferrari that outshines the previous cardboard model.",
    "keyPoints": [
      "The story begins with a child excited about a cardboard Ferrari.",
      "The realization that cardboard cannot race leads to a creative solution.",
      "The father and child decide to build a real metal Ferrari from junkyard materials.",
      "They focus on creating a strong and beautiful car with a powerful engine.",
      "The transformation from cardboard to metal symbolizes creativity and resilience.",
      "The final product is a shiny white Ferrari that is deemed the fastest on the track."
    ],
    "topics": [
      "imagination",
      "creativity",
      "father-child bond",
      "building",
      "transformation",
      "racing",
      "play"
    ],
    "sentiment": "positive"
  },
  "tiktok-top-search": {
    "query": "nasa",
    "totalReturned": 5,
    "results": [
      {
        "platform": "tiktok",
        "url": "https://www.tiktok.com/@latinus_us/video/7667344380310670599",
        "id": "7667344380310670599",
        "caption": "Video obtenido por la NASA muestra la verdadera forma de la Tierra según su gravedad. Para que las diferencias sean visibles, fueron exageradas 10 mil veces y se elaboró con información recopilada por 19 satélites durante 15 años. #Latinus #InformaciónParaTi",
        "description": "Video obtenido por la NASA muestra la verdadera forma de la Tierra según su gravedad. Para que las diferencias sean visibles, fueron exageradas 10 mil veces y se elaboró con información recopilada por 19 satélites durante 15 años. #Latinus #InformaciónParaTi",
        "publishedAt": "2026-07-27T22:52:21.000Z",
        "durationSeconds": 47.0,
        "thumbnailUrl": "https://p19-common-sign.tiktokcdn-us.com/tos-alisg-p-0037/owknk3giAYK0AIIE0Bi1A4BBwVUmAgNJvfMB7x~tplv-tiktokx-origin.image?dr=9636&x-expires=1785517200&x-signature=bnHCVenSGV0TB7nhxBq8lfWKVe0%3D&t=4d5b0474&ps=13740610&shp=81f88b70&shcp=43f4a2f9&idc=useast5",
        "author": {
          "username": "latinus_us",
          "displayName": "Latinus",
          "url": "https://www.tiktok.com/@latinus_us",
          "followers": 22700000,
          "verified": true,
          "profileImage": "https://p16-common-sign.tiktokcdn-us.com/tos-maliva-avt-0068/9b1bc4bbfedb3bd917a27ff590234ca0~tplv-tiktokx-cropcenter:1080:1080.jpeg?dr=9640&refresh_token=97b8bbe5&x-expires=1785517200&x-signature=1ZGx4llDfPF1ly3oJa0XsXinyoY%3D&t=4d5b0474&ps=13740610&shp=a5d48078&shcp=81f88b70&idc=useast5",
          "id": null,
          "secUid": null
        },
        "engagement": {
          "views": 8400000,
          "likes": 810400,
          "comments": 19000,
          "shares": 145400,
          "saves": 65900
        },
        "hashtags": [
          "latinus",
          "informaciónparati"
        ],
        "musicName": "original sound - Latinus",
        "mediaType": "video",
        "contentType": "video",
        "isAd": false,
        "mentions": [],
        "isPaidPartnership": false
      },
      {
        "platform": "tiktok",
        "url": "https://www.tiktok.com/@missionartemisnasa/video/7628631080752450849",
        "id": "7628631080752450849",
        "caption": "ARTEMIS II Edit #nasa #artemis2 #fy #fyp #fyptt",
        "description": "ARTEMIS II Edit #nasa #artemis2 #fy #fyp #fyptt",
        "publishedAt": "2026-04-14T15:04:52.000Z",
        "durationSeconds": 13.0,
        "thumbnailUrl": "https://p16-common-sign.tiktokcdn-us.com/tos-useast2a-p-0037-euttp/oAmD8QOCEOzBQ5FQpRIAuVlfpcnRBWE3eIDjrC~tplv-tiktokx-origin.image?dr=9636&x-expires=1785517200&x-signature=JK5MGls0OQFL2ENmqkVKSBo3ajU%3D&t=4d5b0474&ps=13740610&shp=81f88b70&shcp=43f4a2f9&idc=useast5",
        "author": {
          "username": "missionartemisnasa",
          "displayName": "MissionArtemis",
          "url": "https://www.tiktok.com/@missionartemisnasa",
          "followers": 69,
          "verified": false,
          "profileImage": "https://p16-common-sign.tiktokcdn-us.com/tos-useast2a-avt-0068-euttp/fbdd74ed519afa76388646251f24ded1~tplv-tiktokx-cropcenter:1080:1080.jpeg?dr=9640&refresh_token=6f41b39b&x-expires=1785517200&x-signature=vpJCW3%2B4khpTq%2FDSdGTddKAFRPk%3D&t=4d5b0474&ps=13740610&shp=a5d48078&shcp=81f88b70&idc=useast5",
          "id": null,
          "secUid": null
        },
        "engagement": {
          "views": 14800,
          "likes": 375,
          "comments": 9,
          "shares": 11,
          "saves": 150
        },
        "hashtags": [
          "nasa",
          "artemis2"
        ],
        "musicName": "sonido original",
        "mediaType": "video",
        "contentType": "video",
        "isAd": false,
        "mentions": [],
        "isPaidPartnership": false
      }
    ],
    "hasMore": true,
    "nextCursor": 20
  },
  "tiktok-transcript": {
    "platform": "tiktok",
    "url": "https://www.tiktok.com/@promakeuppro/video/7652684315989462290",
    "transcript": "Well, spin on my mind, I wanna make a rock and a-na-na I wanna make a rock and a-na-na Wish we never go, go, rock and a-na We need to make a rock and a-na I wanna make a rock and a-na I wanna make a rock and a-na Wish we never go, go, rock and a-na We need to make a rock and a-na Wish we never go, go, rock and a-na We need to make a rock and a-na",
    "transcriptSegments": [
      {
        "text": "Well, spin on my mind, I wanna make a rock and a-na-na I wanna make a rock and a-na-na",
        "start": 0,
        "duration": 9.28,
        "end": 9.28,
        "timestamp": "00:00"
      },
      {
        "text": "Wish we never go, go, rock and a-na We need to make a rock and a-na",
        "start": 9.28,
        "duration": 7.2,
        "end": 16.48,
        "timestamp": "00:09"
      },
      {
        "text": "I wanna make a rock and a-na I wanna make a rock and a-na",
        "start": 16.48,
        "duration": 6.72,
        "end": 23.2,
        "timestamp": "00:16"
      },
      {
        "text": "Wish we never go, go, rock and a-na We need to make a rock and a-na",
        "start": 23.2,
        "duration": 7.28,
        "end": 30.48,
        "timestamp": "00:23"
      },
      {
        "text": "Wish we never go, go, rock and a-na We need to make a rock and a-na",
        "start": 30.48,
        "duration": 2.0,
        "end": 32.48,
        "timestamp": "00:30"
      }
    ],
    "wordCount": 81,
    "segments": 5,
    "language": "en"
  },
  "tiktok-trending-feed": {
    "country": "US",
    "totalReturned": 5,
    "results": [
      {
        "url": "https://www.tiktok.com/@adamjones73/video/7660991836407811358",
        "id": "7660991836407811358",
        "coverUrl": "https://p19-common-sign.tiktokcdn-us.com/tos-useast8-p-0068-tx2/oERcgNIQQgASfTiefnLoipqrkyeCfiAGGKmNEI~tplv-tiktokx-origin.image?dr=9636&x-expires=1785517200&x-signature=FF%2Fhr528f3arMCaHqCr9%2BeBIue0%3D&t=4d5b0474&ps=13740610&shp=81f88b70&shcp=43f4a2f9&idc=useast5",
        "author": "adamjones73",
        "authorName": "Adam",
        "views": 5400000,
        "likes": 823500,
        "comments": 4301,
        "shares": 147900,
        "rank": 1,
        "caption": "#gta #viral #fyp",
        "platform": "tiktok",
        "createTime": 1783713660,
        "publishedAt": "2026-07-10T20:01:00.000Z",
        "mediaType": "video",
        "thumbnailUrl": "https://p19-common-sign.tiktokcdn-us.com/tos-useast8-p-0068-tx2/oERcgNIQQgASfTiefnLoipqrkyeCfiAGGKmNEI~tplv-tiktokx-origin.image?dr=9636&x-expires=1785517200&x-signature=FF%2Fhr528f3arMCaHqCr9%2BeBIue0%3D&t=4d5b0474&ps=13740610&shp=81f88b70&shcp=43f4a2f9&idc=useast5",
        "isAd": false
      },
      {
        "url": "https://www.tiktok.com/@123court/video/7655473367125855519",
        "id": "7655473367125855519",
        "coverUrl": "https://p19-common-sign.tiktokcdn-us.com/tos-useast8-p-0068-tx2/oIMffQHCCga9fWiRXUy8JOfP3WVUFGAL7oQtAQ~tplv-tiktokx-origin.image?dr=9636&x-expires=1785517200&x-signature=zF4ZAiNfBFLlLm4zu51g3NjykhI%3D&t=4d5b0474&ps=13740610&shp=81f88b70&shcp=43f4a2f9&idc=useast5",
        "author": "123court",
        "authorName": "123 Court",
        "views": 3600000,
        "likes": 133800,
        "comments": 1872,
        "shares": 8999,
        "rank": 2,
        "caption": "Engaged Mom Demands More Money, But Judge Finds Out The Shocking Truth! ​#CourtroomDrama  ​#FamilyCourt  ​#ChildSupport  ​#ChildSupportCourt  ​#JudgeJules   ​#InstantKarma  ​#Backfired  ​#CaughtInTheAct  ​#PlotTwist  ​#TruckDriverLife  ​#CoParenting  ​#SplitCustody  ​#SiblingDrama  ​#RevengeBackfires",
        "platform": "tiktok",
        "createTime": 1782428791,
        "publishedAt": "2026-06-25T23:06:31.000Z",
        "mediaType": "video",
        "thumbnailUrl": "https://p19-common-sign.tiktokcdn-us.com/tos-useast8-p-0068-tx2/oIMffQHCCga9fWiRXUy8JOfP3WVUFGAL7oQtAQ~tplv-tiktokx-origin.image?dr=9636&x-expires=1785517200&x-signature=zF4ZAiNfBFLlLm4zu51g3NjykhI%3D&t=4d5b0474&ps=13740610&shp=81f88b70&shcp=43f4a2f9&idc=useast5",
        "isAd": false
      }
    ],
    "scrapedAt": "2026-08-03T11:30:00.000Z"
  },
  "tiktok-user-followers": {
    "url": "https://www.tiktok.com/@khaby.lame",
    "total": 162476412,
    "totalReturned": 5,
    "hasMore": true,
    "nextCursor": "1785219170000",
    "followers": [
      {
        "username": "abdullah007a3",
        "displayName": "𝄢 ⃝ᶦᵗᶻ•abdullah 亗",
        "bio": "/ মানুষকে বোঝা কঠিন -\nআর বোঝানো তো অসম্ভব..!🖤",
        "url": "https://www.tiktok.com/@abdullah007a3",
        "followers": 17500,
        "following": 6,
        "verified": false,
        "profileImage": "https://p16-common-sign.tiktokcdn.com/tos-alisg-avt-0068/ff95fdfeca275eed2d2984d618a10530~tplv-tiktokx-cropcenter:1080:1080.jpeg?dr=14579&refresh_token=d7015725&x-expires=1785405600&x-signature=Zs92egTgumV89yLzYImuFHbHTrI%3D&t=4d5b0474&ps=13740610&shp=a5d48078&shcp=81f88b70&idc=my2",
        "id": "7084524072541307910",
        "secUid": "MS4wLjABAAAAU2DhFzvcREPkAwTEDm5wYxPFCSf7l7g0GSQHY3rFZCBY1IlFORcpPL4TMDaxjNUq",
        "createTime": "2022-04-09T09:37:50.000Z",
        "createTimeUnix": 1649497070,
        "language": "en",
        "region": null
      },
      {
        "username": "hawulet97",
        "displayName": "ሀያት",
        "bio": null,
        "url": "https://www.tiktok.com/@hawulet97",
        "followers": 41,
        "following": 1239,
        "verified": false,
        "profileImage": "https://p19-common-sign.tiktokcdn.com/tos-alisg-avt-0068/5acdd487480e04ffe37f451a62fa134d~tplv-tiktokx-cropcenter:1080:1080.jpeg?dr=14579&refresh_token=9e5f5d27&x-expires=1785405600&x-signature=r06fBPyezVcEOXYXR%2Fn5PrC0kQc%3D&t=4d5b0474&ps=13740610&shp=a5d48078&shcp=81f88b70&idc=my2",
        "id": "7636369819877950485",
        "secUid": "MS4wLjABAAAA-iwqiDRUYsYB6EPWLtkKC7LnR81u_bnHPwV2hjD_6vvHCV5WRlc5imKT_JYNVLCl",
        "createTime": "2026-05-05T11:35:24.000Z",
        "createTimeUnix": 1777980924,
        "language": "en",
        "region": null
      }
    ]
  },
  "tiktok-user-followings": {
    "url": "https://www.tiktok.com/@khaby.lame",
    "total": 81,
    "totalReturned": 5,
    "hasMore": true,
    "nextCursor": "1661588126000",
    "followings": [
      {
        "username": "user927647273",
        "displayName": "user927647273",
        "bio": "secret",
        "url": "https://www.tiktok.com/@user927647273",
        "followers": 9282,
        "following": 4,
        "verified": false,
        "profileImage": "https://p16-common-sign.tiktokcdn.com/tos-maliva-avt-0068/c70537d713e096c514e7e8e27be0cf39~tplv-tiktokx-cropcenter:1080:1080.jpeg?dr=14579&refresh_token=616e8df2&x-expires=1785405600&x-signature=w%2BadFFsdbgxPDur8Y6yIeu5%2FYU8%3D&t=4d5b0474&ps=13740610&shp=a5d48078&shcp=81f88b70&idc=my2",
        "id": "7221286453480817706",
        "secUid": "MS4wLjABAAAAg4rTr5twSx0cDvC90WsFq6Zk2HpEcyOVjWMV1rb37RyZkyjSMTpnHzCTsTU2UObL",
        "createTime": "2023-04-12T22:02:13.000Z",
        "createTimeUnix": 1681336933,
        "language": "en",
        "region": null
      },
      {
        "username": "fifaworldcup",
        "displayName": "FIFA World Cup",
        "bio": "🏆 The official #FIFAWorldCup account on TikTok",
        "url": "https://www.tiktok.com/@fifaworldcup",
        "followers": 86600000,
        "following": 93,
        "verified": true,
        "profileImage": "https://p16-common-sign.tiktokcdn.com/tos-useast2a-avt-0068-euttp/d260685754e3ae8139f47e7ec9fda7e9~tplv-tiktokx-cropcenter:1080:1080.jpeg?dr=14579&refresh_token=4d3bd79a&x-expires=1785405600&x-signature=UpkTTNy5CO1ckN0jnBQ1jrq4nRo%3D&t=4d5b0474&ps=13740610&shp=a5d48078&shcp=81f88b70&idc=my2",
        "id": "7059636734342038534",
        "secUid": "MS4wLjABAAAApf8MKCE246Q60LYymhpec5wPGF-uaGZgzl7W19U-AxtzHzeydNdE8xZedO_gUWDL",
        "createTime": "2022-02-01T16:22:46.000Z",
        "createTimeUnix": 1643732566,
        "language": "en",
        "region": null
      }
    ]
  },
  "tiktok-video-details": {
    "platform": "tiktok",
    "url": "https://www.tiktok.com/@khaby.lame/video/7646812028874673439",
    "id": "7646812028874673439",
    "caption": "Thank you, please come again!!!🙋🏿‍♂️💸#learnfromkhaby #comedy",
    "description": "Thank you, please come again!!!🙋🏿‍♂️💸#learnfromkhaby #comedy",
    "publishedAt": "2026-06-02T14:56:35.000Z",
    "durationSeconds": 29.0,
    "thumbnailUrl": "https://p19-common-sign.tiktokcdn-us.com/tos-useast8-p-0068-tx2/oUAHVIiQDac8uC75AEfyALAA1FrTAqEEQ3GRPe~tplv-tiktokx-origin.image?dr=9636&x-expires=1783263600&x-signature=2PlkofS3nAbuOWtQQSaCTJIU0bQ%3D&t=4d5b0474&ps=13740610&shp=81f88b70&shcp=43f4a2f9&idc=useast5",
    "author": {
      "username": "khaby.lame",
      "displayName": "Khabane lame",
      "url": "https://www.tiktok.com/@khaby.lame",
      "followers": 162300000,
      "verified": true,
      "profileImage": "https://p16-common-sign.tiktokcdn-us.com/tos-useast8-avt-0068-tx2/08987e23b94057953fd4f1738694bf5f~tplv-tiktokx-cropcenter:720:720.jpeg?dr=9640&refresh_token=828dd685&x-expires=1783263600&x-signature=uG12wEuTZOcKwj9%2BCpq6wCtqNe8%3D&t=4d5b0474&ps=13740610&shp=a5d48078&shcp=f20df69d&idc=useast5"
    },
    "engagement": {
      "views": 14700000,
      "likes": 1300000,
      "comments": 13600,
      "shares": 13400,
      "saves": 50705
    },
    "hashtags": [
      "learnfromkhaby",
      "comedy"
    ],
    "musicName": "original sound"
  },
  "truth-social-post": {
    "platform": "truth_social",
    "id": "116938579137506694",
    "url": "https://truthsocial.com/@realDonaldTrump/116938579137506694",
    "text": "Tim Sheehy is GREAT. A Winner!!! President DJT",
    "publishedAt": "2026-07-18T02:18:32.394Z",
    "author": {
      "platform": "truth_social",
      "id": "107780257626128497",
      "username": "realDonaldTrump",
      "url": "https://truthsocial.com/@realDonaldTrump",
      "displayName": "Donald J. Trump",
      "bio": "",
      "avatar": "https://static-assets-1.truthsocial.com/tmtg:prime-ts-assets/accounts/avatars/107/780/257/626/128/497/original/454286ac07a6f6e6.jpeg",
      "banner": "https://static-assets-1.truthsocial.com/tmtg:prime-ts-assets/accounts/headers/107/780/257/626/128/497/original/ba3b910ba387bf4e.jpeg",
      "verified": true,
      "followers": 12908903,
      "following": 69,
      "postCount": 35050,
      "website": "www.DonaldJTrump.com",
      "createdAt": "2022-02-11T16:16:57.705Z",
      "lastStatusAt": "2026-07-18T00:00:00.000Z",
      "fields": [],
      "locked": false,
      "isPrivate": false,
      "bot": false,
      "group": false,
      "location": null
    },
    "engagement": {
      "replies": 827,
      "reblogs": 2586,
      "likes": 8328,
      "upvotes": null,
      "downvotes": null
    },
    "language": "fy",
    "sensitive": false,
    "media": [
      {
        "type": "image",
        "url": "https://static-assets-1.truthsocial.com/tmtg:prime-ts-assets/media_attachments/files/116/938/578/476/026/646/original/5b31cf2bfc5bfa22.jpg",
        "previewUrl": "https://static-assets-1.truthsocial.com/tmtg:prime-ts-assets/media_attachments/files/116/938/578/476/026/646/small/5b31cf2bfc5bfa22.jpg",
        "description": null
      }
    ],
    "links": []
  },
  "truth-social-profile": {
    "platform": "truth_social",
    "id": "107780257626128497",
    "username": "realDonaldTrump",
    "acct": "realDonaldTrump",
    "url": "https://truthsocial.com/@realDonaldTrump",
    "displayName": "Donald J. Trump",
    "bio": "",
    "avatar": "https://static-assets-1.truthsocial.com/tmtg:prime-ts-assets/accounts/avatars/107/780/257/626/128/497/original/454286ac07a6f6e6.jpeg",
    "avatarStatic": "https://static-assets-1.truthsocial.com/tmtg:prime-ts-assets/accounts/avatars/107/780/257/626/128/497/original/454286ac07a6f6e6.jpeg",
    "banner": "https://static-assets-1.truthsocial.com/tmtg:prime-ts-assets/accounts/headers/107/780/257/626/128/497/original/ba3b910ba387bf4e.jpeg",
    "headerStatic": "https://static-assets-1.truthsocial.com/tmtg:prime-ts-assets/accounts/headers/107/780/257/626/128/497/original/ba3b910ba387bf4e.jpeg",
    "verified": true,
    "followers": 12956933,
    "following": 69,
    "postCount": 35371,
    "location": null,
    "website": "www.DonaldJTrump.com",
    "createdAt": "2022-02-11T16:16:57.705Z",
    "lastStatusAt": "2026-08-02T00:00:00.000Z",
    "emojis": [],
    "fields": [],
    "bot": false,
    "locked": false,
    "isPrivate": false,
    "group": false,
    "discoverable": null,
    "acceptingMessages": false,
    "chatsOnboarded": true,
    "tvAccount": false
  },
  "truth-social-user-posts": {
    "username": "realDonaldTrump",
    "author": {
      "platform": "truth_social",
      "id": "107780257626128497",
      "username": "realDonaldTrump",
      "acct": "realDonaldTrump",
      "url": "https://truthsocial.com/@realDonaldTrump",
      "displayName": "Donald J. Trump",
      "bio": "",
      "avatar": "https://static-assets-1.truthsocial.com/tmtg:prime-ts-assets/accounts/avatars/107/780/257/626/128/497/original/454286ac07a6f6e6.jpeg",
      "avatarStatic": "https://static-assets-1.truthsocial.com/tmtg:prime-ts-assets/accounts/avatars/107/780/257/626/128/497/original/454286ac07a6f6e6.jpeg",
      "banner": "https://static-assets-1.truthsocial.com/tmtg:prime-ts-assets/accounts/headers/107/780/257/626/128/497/original/ba3b910ba387bf4e.jpeg",
      "headerStatic": "https://static-assets-1.truthsocial.com/tmtg:prime-ts-assets/accounts/headers/107/780/257/626/128/497/original/ba3b910ba387bf4e.jpeg",
      "verified": true,
      "followers": 12956933,
      "following": 69,
      "postCount": 35371,
      "location": null,
      "website": "www.DonaldJTrump.com",
      "createdAt": "2022-02-11T16:16:57.705Z",
      "lastStatusAt": "2026-08-02T00:00:00.000Z",
      "emojis": [],
      "fields": [],
      "bot": false,
      "locked": false,
      "isPrivate": false,
      "group": false,
      "discoverable": null,
      "acceptingMessages": false,
      "chatsOnboarded": true,
      "tvAccount": false
    },
    "totalReturned": 5,
    "nextCursor": "116936997445912023",
    "hasMore": true,
    "posts": [
      {
        "platform": "truth_social",
        "id": "116938579137506694",
        "url": "https://truthsocial.com/@realDonaldTrump/116938579137506694",
        "text": "Tim Sheehy is GREAT. A Winner!!! President DJT",
        "publishedAt": "2026-07-18T02:18:32.394Z",
        "author": {
          "id": "107780257626128497",
          "username": "realDonaldTrump",
          "displayName": "Donald J. Trump",
          "avatar": "https://static-assets-1.truthsocial.com/tmtg:prime-ts-assets/accounts/avatars/107/780/257/626/128/497/original/454286ac07a6f6e6.jpeg",
          "verified": true
        },
        "engagement": {
          "replies": 827,
          "reblogs": 2584,
          "likes": 8321,
          "upvotes": null,
          "downvotes": null
        },
        "language": "fy",
        "sensitive": false,
        "media": [
          {
            "type": "image",
            "url": "https://static-assets-1.truthsocial.com/tmtg:prime-ts-assets/media_attachments/files/116/938/578/476/026/646/original/5b31cf2bfc5bfa22.jpg",
            "previewUrl": "https://static-assets-1.truthsocial.com/tmtg:prime-ts-assets/media_attachments/files/116/938/578/476/026/646/small/5b31cf2bfc5bfa22.jpg",
            "description": null
          }
        ],
        "links": []
      },
      {
        "platform": "truth_social",
        "id": "116938558790759096",
        "url": "https://truthsocial.com/@realDonaldTrump/116938558790759096",
        "text": "Ensuring the integrity of our elections is fundamental to preserving trust in American democracy. Following the 2020 presidential election, concerns about potential irregularities prompted detailed examinations of voting processes, data security, and registration practices across multiple states… Download documents and reports addressing key areas of election integrity, here: https://www. whitehouse.gov/election-integr ity/",
        "publishedAt": "2026-07-18T02:13:21.858Z",
        "author": {
          "id": "107780257626128497",
          "username": "realDonaldTrump",
          "displayName": "Donald J. Trump",
          "avatar": "https://static-assets-1.truthsocial.com/tmtg:prime-ts-assets/accounts/avatars/107/780/257/626/128/497/original/454286ac07a6f6e6.jpeg",
          "verified": true
        },
        "engagement": {
          "replies": 1388,
          "reblogs": 3509,
          "likes": 11543,
          "upvotes": null,
          "downvotes": null
        },
        "language": "en",
        "sensitive": false,
        "media": [
          {
            "type": "video",
            "url": "https://static-assets-1.truthsocial.com/tmtg:prime-ts-assets/media_attachments/files/116/938/518/347/491/612/original/9bb622c2a7cb73f9.mp4",
            "previewUrl": null,
            "description": null
          }
        ],
        "links": []
      }
    ]
  },
  "twitch-clip": {
    "platform": "twitch",
    "id": "3052590127",
    "slug": "EnergeticEmpathicElephantJKanStyle-0sOlvgAod9mDhCw4",
    "url": "https://www.twitch.tv/xqc/clip/EnergeticEmpathicElephantJKanStyle-0sOlvgAod9mDhCw4",
    "embedUrl": "https://clips.twitch.tv/embed?clip=EnergeticEmpathicElephantJKanStyle-0sOlvgAod9mDhCw4",
    "title": "the word",
    "createdAt": "2026-07-12T23:00:58Z",
    "durationSeconds": 44,
    "views": 31603,
    "thumbnail": "https://static-cdn.jtvnw.net/twitch-video-assets/twitch-vap-video-assets-prod-us-west-2/a952a6bb-ad94-4889-8ac1-6afadf21d338/landscape/thumb/thumb-0000000000-1920x1080.jpg",
    "videoUrl": "https://d1ndex63qxojbr.cloudfront.net/nauth/a952a6bb-ad94-4889-8ac1-6afadf21d338/landscape/h264/1080/index.mp4",
    "videoQualities": [
      {
        "quality": "1080",
        "frameRate": 60,
        "url": "https://d1ndex63qxojbr.cloudfront.net/nauth/a952a6bb-ad94-4889-8ac1-6afadf21d338/landscape/h264/1080/index.mp4"
      },
      {
        "quality": "720",
        "frameRate": 60.02308654785156,
        "url": "https://d1ndex63qxojbr.cloudfront.net/nauth/a952a6bb-ad94-4889-8ac1-6afadf21d338/landscape/h264/720/index.mp4"
      }
    ],
    "language": "EN",
    "isFeatured": false,
    "isPublished": true,
    "videoOffsetSeconds": 1677,
    "game": "Just Chatting",
    "gameId": "509658",
    "gameSlug": "just-chatting",
    "gameBoxArtUrl": "https://static-cdn.jtvnw.net/ttv-boxart/509658-285x380.jpg",
    "broadcaster": "xqc",
    "broadcasterProfileImage": "https://static-cdn.jtvnw.net/jtv_user_pictures/xqc-profile_image-9298dca608632101-150x150.jpeg",
    "channel": {
      "id": "71092938",
      "username": "xqc",
      "name": "xQc",
      "url": "https://www.twitch.tv/xqc",
      "profileImage": "https://static-cdn.jtvnw.net/jtv_user_pictures/xqc-profile_image-9298dca608632101-150x150.jpeg",
      "followers": 12531017,
      "isPartner": true,
      "lastBroadcast": {
        "startedAt": "2026-08-02T06:29:57.736501Z",
        "title": "🧑‍🌾LIVE🧑‍🌾HERE🧑‍🌾LOCK IN🧑‍🌾DRAMA🧑‍🌾NEWS🧑‍🌾VIDEOSV🧑‍🌾REACTS🧑‍🌾TRHNIGS🧑‍🌾GAMES🧑‍🌾VIDEOGAMES🧑‍🌾MAYBE EVEN THINGS AND SUCH"
      }
    },
    "curator": {
      "id": "768198835",
      "username": "puertoricanporo",
      "name": "puertoricanporo",
      "url": "https://www.twitch.tv/puertoricanporo",
      "profileImage": "https://static-cdn.jtvnw.net/jtv_user_pictures/15b6d728-aa8b-47be-a3a3-6474f3bea71e-profile_image-150x150.png"
    },
    "playbackAccessToken": {
      "signature": "717a7cc45782d584804989cd3b629ae9bdd25364",
      "value": "{\"authorization\":{\"forbidden\":false,\"reason\":\"\"},\"clip_uri\":\"https://d1ndex63qxojbr.cloudfront.net/nauth/a952a6bb-ad94-4889-8ac1-6afadf21d338/landscape/h264/720/index.mp4\",\"clip_slug\":\"EnergeticEmpathicElephantJKanStyle-0sOlvgAod9mDhCw4\",\"device_id\":\"2f4b8c922ff447c6a2667b75c9a2ff30\",\"expires\":1785766190,\"user_id\":\"\",\"version\":3}",
      "expires": 1785766190,
      "expiresAt": "2026-08-03T14:09:50Z"
    }
  },
  "twitch-profile": {
    "platform": "twitch",
    "id": "83232866",
    "login": "ibai",
    "displayName": "ibai",
    "url": "https://www.twitch.tv/ibai",
    "description": "Si lees esto que sepas que te aprecio",
    "followers": 20346592,
    "profileImage": "https://static-cdn.jtvnw.net/jtv_user_pictures/574228be-01ef-4eab-bc0e-a4f6b68bedba-profile_image-300x300.png",
    "bannerImage": "https://static-cdn.jtvnw.net/jtv_user_pictures/4de9a7f1-42a9-477f-9cd4-6fb585272f3c-profile_banner-480.jpeg",
    "isPartner": true,
    "isAffiliate": false,
    "isLive": false,
    "stream": {
      "title": null,
      "game": null,
      "gameBoxArtUrl": null,
      "viewers": null,
      "startedAt": null,
      "thumbnail": null
    },
    "lastBroadcast": {
      "title": "FLAKKED Y OSCARININ SE ESTRENAN | GX VS SK | NAVI VS KC | #WatchLEC",
      "game": "League of Legends",
      "gameBoxArtUrl": "https://static-cdn.jtvnw.net/ttv-boxart/21779-144x192.jpg",
      "startedAt": "2026-08-01T20:18:56.367677Z"
    },
    "recentVideos": [
      {
        "platform": "twitch",
        "id": "2834463106",
        "url": "https://www.twitch.tv/videos/2834463106",
        "embedUrl": "https://player.twitch.tv/?video=2834463106&parent=captapi.com",
        "title": "FLAKKED Y OSCARININ SE ESTRENAN | GX VS SK | NAVI VS KC | #WatchLEC",
        "createdAt": "2026-08-01T14:31:37Z",
        "durationSeconds": 20835,
        "views": 500540,
        "thumbnail": "https://static-cdn.jtvnw.net/cf_vods/d3stzm2eumvgb4/ecd0accc3ebc7ced4d7e_ibai_317377393636_1785594690//thumb/thumb0-{width}x{height}.jpg",
        "animatedPreviewUrl": "https://d3stzm2eumvgb4.cloudfront.net/ecd0accc3ebc7ced4d7e_ibai_317377393636_1785594690/storyboards/2834463106-strip-0.jpg",
        "game": "League of Legends",
        "gameBoxArtUrl": "https://static-cdn.jtvnw.net/ttv-boxart/21779-144x192.jpg",
        "language": "es",
        "broadcaster": "ibai",
        "broadcasterProfileImage": "https://static-cdn.jtvnw.net/jtv_user_pictures/574228be-01ef-4eab-bc0e-a4f6b68bedba-profile_image-300x300.png"
      },
      {
        "platform": "twitch",
        "id": "2833593338",
        "url": "https://www.twitch.tv/videos/2833593338",
        "embedUrl": "https://player.twitch.tv/?video=2833593338&parent=captapi.com",
        "title": "MKOI vs SHFT | NOS JUGAMOS LA VIDA | VAMOS 0-3 | YO CONFIO | AVE FENIX | TH vs VIT | #WatchLEC",
        "createdAt": "2026-07-31T14:40:08Z",
        "durationSeconds": 17708,
        "views": 545528,
        "thumbnail": "https://static-cdn.jtvnw.net/cf_vods/d3stzm2eumvgb4/f6e52764cb70a8846ecb_ibai_317369348836_1785508801//thumb/thumb0-{width}x{height}.jpg",
        "animatedPreviewUrl": "https://d3stzm2eumvgb4.cloudfront.net/f6e52764cb70a8846ecb_ibai_317369348836_1785508801/storyboards/2833593338-strip-0.jpg",
        "game": "League of Legends",
        "gameBoxArtUrl": "https://static-cdn.jtvnw.net/ttv-boxart/21779-144x192.jpg",
        "language": "es",
        "broadcaster": "ibai",
        "broadcasterProfileImage": "https://static-cdn.jtvnw.net/jtv_user_pictures/574228be-01ef-4eab-bc0e-a4f6b68bedba-profile_image-300x300.png"
      }
    ],
    "topClips": [],
    "schedule": [],
    "createdAt": "2015-02-20T16:47:56.548434Z"
  },
  "twitch-user-schedule": {
    "platform": "twitch",
    "username": "criticalrole",
    "totalReturned": 1,
    "schedule": [
      {
        "id": "eyJzZWdtZW50SUQiOiI1MWYyNGJjNS02ZmY2LTRhOTgtYjk4Ni04ZGIyNzVhMWE2MmEiLCJpc29ZZWFyIjoyMDI2LCJpc29XZWVrIjozMn0=",
        "title": "Age of Umbra: Sallowlands",
        "startedAt": "2026-08-07T02:00:00Z",
        "endedAt": "2026-08-07T06:00:00Z",
        "startAt": "2026-08-07T02:00:00Z",
        "endAt": "2026-08-07T06:00:00Z",
        "game": "Tabletop RPGs",
        "gameId": "509664",
        "isRecurring": false,
        "isCancelled": false,
        "firstOccurrenceAt": "2026-08-07T02:00:00Z"
      }
    ]
  },
  "twitch-user-videos": {
    "platform": "twitch",
    "username": "shroud",
    "filterBy": null,
    "sortBy": "TIME",
    "broadcaster": {
      "id": "37402112",
      "username": "shroud",
      "displayName": "shroud",
      "url": "https://www.twitch.tv/shroud",
      "profileImage": "https://static-cdn.jtvnw.net/jtv_user_pictures/c754eebf-745b-4e0a-814a-10bcaecaabbc-profile_image-300x300.png",
      "followers": 11293237,
      "isPartner": true,
      "isAffiliate": false
    },
    "totalReturned": 3,
    "nextCursor": "2827054673",
    "hasMore": true,
    "windowMax": 100,
    "videos": [
      {
        "platform": "twitch",
        "id": "2827992810",
        "url": "https://www.twitch.tv/videos/2827992810",
        "embedUrl": "https://player.twitch.tv/?video=2827992810&parent=captapi.com",
        "title": "ME N THE GIRLS R GONNA POP OFF IN THIS 100K TWITCH RIVALS",
        "createdAt": "2026-07-24T17:56:52Z",
        "durationSeconds": 20988,
        "views": 212833,
        "thumbnail": "https://static-cdn.jtvnw.net/cf_vods/d2nvs31859zcd8/c43d1ce993fae5a15f69_shroud_317074350583_1784915807//thumb/thumb0-320x180.jpg",
        "thumbnailTemplate": "https://static-cdn.jtvnw.net/cf_vods/d2nvs31859zcd8/c43d1ce993fae5a15f69_shroud_317074350583_1784915807//thumb/thumb0-{width}x{height}.jpg",
        "animatedPreviewUrl": "https://d2nvs31859zcd8.cloudfront.net/c43d1ce993fae5a15f69_shroud_317074350583_1784915807/storyboards/2827992810-strip-0.jpg",
        "broadcastType": "ARCHIVE",
        "game": "VALORANT",
        "gameId": "516575",
        "gameSlug": "valorant",
        "gameBoxArtUrl": "https://static-cdn.jtvnw.net/ttv-boxart/516575-144x192.jpg",
        "language": "en"
      },
      {
        "platform": "twitch",
        "id": "2827192082",
        "url": "https://www.twitch.tv/videos/2827192082",
        "embedUrl": "https://player.twitch.tv/?video=2827192082&parent=captapi.com",
        "title": "HALO CE REMAKE! TIME TO CO-OP LEGENDARY AND GET OUR MEAT BEAT",
        "createdAt": "2026-07-23T18:19:36Z",
        "durationSeconds": 20254,
        "views": 175717,
        "thumbnail": "https://static-cdn.jtvnw.net/cf_vods/d2vi6trrdongqn/43c3501090df2005acdf_shroud_319635395040_1784830770//thumb/thumb0-320x180.jpg",
        "thumbnailTemplate": "https://static-cdn.jtvnw.net/cf_vods/d2vi6trrdongqn/43c3501090df2005acdf_shroud_319635395040_1784830770//thumb/thumb0-{width}x{height}.jpg",
        "animatedPreviewUrl": "https://d2vi6trrdongqn.cloudfront.net/43c3501090df2005acdf_shroud_319635395040_1784830770/storyboards/2827192082-strip-0.jpg",
        "broadcastType": "ARCHIVE",
        "game": "Halo: Campaign Evolved",
        "gameId": "796500915",
        "gameSlug": "halo-campaign-evolved",
        "gameBoxArtUrl": "https://static-cdn.jtvnw.net/ttv-boxart/796500915_IGDB-144x192.jpg",
        "language": "en"
      }
    ]
  },
  "twitter-community": {
    "platform": "twitter",
    "id": "1493446837214187523",
    "url": "https://x.com/i/communities/1493446837214187523",
    "name": "Build in Public",
    "description": "Share what you're working on. Get feedback. Help each other move forward. – Sponsored by bolt.new ⚡",
    "memberCount": 264138,
    "createdAt": "2022-02-15T04:47:27.000Z",
    "creator": "marckohlbrugge",
    "joinPolicy": "Open",
    "isNsfw": false,
    "bannerImage": "https://pbs.twimg.com/community_banner_img/1915033378811772928/KdaKUaRP?format=png&name=orig",
    "rules": [
      {
        "name": "Share what you're working on",
        "description": "Don't be scared to share unfinished work"
      },
      {
        "name": "Screenshots, screencasts, drafts, etc",
        "description": "Visual tweets tend to grab people's attention"
      }
    ]
  },
  "twitter-community-tweets": {
    "communityId": "1493446837214187523",
    "url": "https://x.com/i/communities/1493446837214187523",
    "communityName": "Build in Public",
    "memberCount": 264133,
    "totalReturned": 5,
    "tweets": [
      {
        "platform": "twitter",
        "url": "https://x.com/FilipPanoski/status/2082466198495662562",
        "id": "2082466198495662562",
        "text": "a little over a year ago: $0 MRR, no customers, 10 followers.\n\ntoday: $7k MRR, 70+ customers, 3k followers.\n\nnot the smartest or fastest founder.\njust consistent. https://t.co/9BmKeqbcNi",
        "lang": "en",
        "publishedAt": "2026-07-29T14:00:06.000Z",
        "author": {
          "username": "FilipPanoski",
          "displayName": "Filip Panoski",
          "url": "https://x.com/FilipPanoski",
          "followers": 3584,
          "verified": true,
          "profileImage": "https://pbs.twimg.com/profile_images/1842181486587297792/Ia5ilmNs_normal.jpg"
        },
        "isReply": false,
        "isRetweet": false,
        "isQuote": false,
        "possiblySensitive": false,
        "conversationId": "2082466198495662562",
        "engagement": {
          "views": 27877,
          "likes": 339,
          "replies": 108,
          "retweets": 5,
          "quotes": 3,
          "bookmarks": 131
        },
        "hashtags": [],
        "media": [
          "https://pbs.twimg.com/media/HOZn-JwXcAASz1f.png"
        ]
      },
      {
        "platform": "twitter",
        "url": "https://x.com/ericdjav/status/2082216601059770771",
        "id": "2082216601059770771",
        "text": "I launched my first app in 2026...\n\nToday, I finally crossed $10k revenue with it 🎊 https://t.co/hziIEliJn1",
        "lang": "en",
        "publishedAt": "2026-07-28T21:28:18.000Z",
        "author": {
          "username": "ericdjav",
          "displayName": "Eric Djavid",
          "url": "https://x.com/ericdjav",
          "followers": 9792,
          "verified": true,
          "profileImage": "https://pbs.twimg.com/profile_images/1884705640246915072/4Y39VboE_normal.jpg"
        },
        "isReply": false,
        "isRetweet": false,
        "isQuote": false,
        "possiblySensitive": false,
        "conversationId": "2082216601059770771",
        "engagement": {
          "views": 10720,
          "likes": 319,
          "replies": 94,
          "retweets": 5,
          "quotes": 1,
          "bookmarks": 36
        },
        "hashtags": [],
        "media": [
          "https://pbs.twimg.com/media/HOWE9npXQAAqfUH.jpg"
        ]
      }
    ]
  },
  "twitter-profile": {
    "platform": "twitter",
    "url": "https://x.com/NASA",
    "id": "11348282",
    "username": "NASA",
    "displayName": "NASA",
    "name": "NASA",
    "bio": "Making the seemingly impossible, possible. ✨",
    "location": "Pale Blue Dot",
    "verified": true,
    "isBlueVerified": true,
    "isIdentityVerified": false,
    "verification": {
      "isBlueVerified": true,
      "isIdentityVerified": false,
      "verifiedType": "Government",
      "reason": "This account is verified because it is a government or multilateral organization account.  Learn more",
      "verifiedSince": "2009-08-07T19:53:50.000Z"
    },
    "followers": 92239064,
    "following": 119,
    "fastFollowers": 0,
    "normalFollowers": 92239064,
    "tweetCount": 74288,
    "likesCount": 16904,
    "mediaCount": 28058,
    "listedCount": 97014,
    "pinnedTweetIds": [
      "2082511887757881648"
    ],
    "website": "http://www.nasa.gov/",
    "contact": {
      "links": [
        "http://www.nasa.gov/"
      ]
    },
    "tipjarSettings": {
      "is_enabled": false
    },
    "profileImage": "https://pbs.twimg.com/profile_images/1321163587679784960/0ZxKlEKB_400x400.jpg",
    "bannerImage": "https://pbs.twimg.com/profile_banners/11348282/1775567134",
    "profileImageShape": "Square",
    "possiblySensitive": false,
    "highlightedTweets": 265,
    "creatorSubscriptionsCount": 0,
    "businessAffiliatesCount": 89,
    "createdAt": "2007-12-19T20:20:32.000Z"
  },
  "twitter-search": {
    "query": "nasa",
    "totalReturned": 5,
    "results": [
      {
        "platform": "twitter",
        "url": "https://x.com/NASA/status/2040468080686424396",
        "id": "2040468080686424396",
        "text": "This view just hits different 🌍\n \n@Astro_Christina and @astro_reid take a moment to look back at Earth as they continue deep into space toward the Moon. https://t.co/NMDeLj256K",
        "lang": "en",
        "publishedAt": "2026-04-04T16:34:35.000Z",
        "author": {
          "username": "NASA",
          "displayName": "NASA",
          "url": "https://x.com/NASA",
          "followers": 92225387,
          "verified": true,
          "profileImage": "https://pbs.twimg.com/profile_images/1321163587679784960/0ZxKlEKB_normal.jpg"
        },
        "isReply": false,
        "isRetweet": false,
        "engagement": {
          "views": 26608930,
          "likes": 196244,
          "replies": 3349,
          "retweets": 29241,
          "quotes": 2911,
          "bookmarks": 11267
        },
        "hashtags": [],
        "media": [
          "https://pbs.twimg.com/media/HFEy5njWsAArPaK.jpg",
          "https://pbs.twimg.com/media/HFEy56IXwAAnG2M.jpg"
        ]
      },
      {
        "platform": "twitter",
        "url": "https://x.com/NASASolarSystem/status/2081803694480261151",
        "id": "2081803694480261151",
        "text": "On Aug. 12, a total solar eclipse will cross Greenland, Iceland, and Spain — and NASA science will be there! ☀️🌑🔭\n\nWe're flying high-altitude jets and launching scientific balloons to study the Sun and the eclipse's effects on us: https://t.co/zPn8UavJ3m\n\n📸: NASA/Ernie Wright https://t.co/wVJzVGJ3Ao",
        "lang": "en",
        "publishedAt": "2026-07-27T18:07:33.000Z",
        "author": {
          "username": "NASASolarSystem",
          "displayName": "NASA Solar System",
          "url": "https://x.com/NASASolarSystem",
          "followers": 2966292,
          "verified": true,
          "profileImage": "https://pbs.twimg.com/profile_images/1852211324224442369/9KHp7JLo_normal.jpg"
        },
        "isReply": false,
        "isRetweet": false,
        "engagement": {
          "views": 371846,
          "likes": 1674,
          "replies": 62,
          "retweets": 406,
          "quotes": 20,
          "bookmarks": 176
        },
        "hashtags": [],
        "media": [
          "https://pbs.twimg.com/amplify_video_thumb/2081803656530190336/img/zUx_qij2E2oP-MsL.jpg"
        ]
      }
    ]
  },
  "twitter-transcript": {
    "platform": "twitter",
    "url": "https://x.com/NASASpox/status/2078226501024227542",
    "tweetId": "2078224758781751775",
    "transcript": "Full steam ahead this week at @NASA 🚀\n\n🧑‍🚀 @Astro_Anil arrives at the ISS\n🪐 Dragonfly progress\n✈️ Future of autonomous flight\n🤝 70 Artemis Accords signatories\n\nHere's your NASA Minute! https://t.co/GAZ4sUqfbZ",
    "transcriptSegments": [
      {
        "text": "Full steam ahead this week at @NASA 🚀",
        "index": 0,
        "wordCount": 7,
        "charStart": 0,
        "charEnd": 37
      },
      {
        "text": "🧑‍🚀 @Astro_Anil arrives at the ISS\n🪐 Dragonfly progress\n✈️ Future of autonomous flight\n🤝 70 Artemis Accords signatories",
        "index": 1,
        "wordCount": 15,
        "charStart": 39,
        "charEnd": 158
      },
      {
        "text": "Here's your NASA Minute! https://t.co/GAZ4sUqfbZ",
        "index": 2,
        "wordCount": 5,
        "charStart": 160,
        "charEnd": 208
      }
    ],
    "wordCount": 27,
    "segments": 3,
    "author": {
      "username": "NASASpox",
      "displayName": "Bethany Stevens",
      "url": "https://x.com/NASASpox",
      "verified": false,
      "profileImage": "https://pbs.twimg.com/profile_images/2030158374625759233/3fWyLDjS_normal.jpg"
    },
    "publishedAt": "2026-07-17T21:06:08.000Z",
    "timingSource": "none",
    "estimatedReadSeconds": 8
  },
  "twitter-tweet-details": {
    "platform": "twitter",
    "url": "https://x.com/NASASpox/status/2078224758781751775",
    "id": "2078224758781751775",
    "text": "Full steam ahead this week at @NASA 🚀\n\n🧑‍🚀 @Astro_Anil arrives at the ISS\n🪐 Dragonfly progress\n✈️ Future of autonomous flight\n🤝 70 Artemis Accords signatories\n\nHere's your NASA Minute! https://t.co/GAZ4sUqfbZ",
    "lang": "en",
    "publishedAt": "2026-07-17T21:06:08.000Z",
    "author": {
      "id": "1907894348319973378",
      "username": "NASASpox",
      "displayName": "Bethany Stevens",
      "url": "https://x.com/NASASpox",
      "followers": 19464,
      "verified": true,
      "profileImage": "https://pbs.twimg.com/profile_images/2030158374625759233/3fWyLDjS_normal.jpg"
    },
    "isReply": false,
    "isRetweet": false,
    "possiblySensitive": false,
    "conversationId": "2078224758781751775",
    "engagement": {
      "views": null,
      "likes": 606,
      "replies": 52,
      "retweets": 117,
      "quotes": 6,
      "bookmarks": null
    },
    "hashtags": [],
    "media": [
      "https://pbs.twimg.com/media/HNdWSZ3XsAEekpT.jpg"
    ]
  },
  "twitter-user-tweets": {
    "handle": "elonmusk",
    "totalReturned": 5,
    "tweets": [
      {
        "platform": "twitter",
        "url": "https://x.com/elonmusk/status/2084274899065897011",
        "id": "2084274899065897011",
        "text": "Worth noting that any USAID funding that appeared to have the slightest merit whatsoever for helping people in need was moved to the State Department. \n\nOnly the funding where they provided no evidence at all for who would receive the money was stopped.\n\nhttps://t.co/qGUew8TyKD",
        "lang": "en",
        "publishedAt": "2026-08-03T13:47:14.000Z",
        "author": {
          "id": "44196397",
          "username": "elonmusk",
          "displayName": "Elon Musk",
          "url": "https://x.com/elonmusk",
          "followers": 241148496,
          "verified": true,
          "profileImage": "https://pbs.twimg.com/profile_images/2053244804520427520/m8mdWZCG_normal.jpg"
        },
        "isReply": false,
        "isRetweet": false,
        "possiblySensitive": false,
        "conversationId": "2084274899065897011",
        "engagement": {
          "views": null,
          "likes": 51392,
          "replies": 2623,
          "retweets": 6975,
          "quotes": 344,
          "bookmarks": null
        },
        "hashtags": [],
        "media": []
      },
      {
        "platform": "twitter",
        "url": "https://x.com/elonmusk/status/1519480761749016577",
        "id": "1519480761749016577",
        "text": "Next I’m buying Coca-Cola to put the cocaine back in",
        "lang": "en",
        "publishedAt": "2022-04-28T00:56:58.000Z",
        "author": {
          "id": "44196397",
          "username": "elonmusk",
          "displayName": "Elon Musk",
          "url": "https://x.com/elonmusk",
          "followers": 241148496,
          "verified": true,
          "profileImage": "https://pbs.twimg.com/profile_images/2053244804520427520/m8mdWZCG_normal.jpg"
        },
        "isReply": false,
        "isRetweet": false,
        "possiblySensitive": false,
        "conversationId": "1519480761749016577",
        "engagement": {
          "views": null,
          "likes": 4209989,
          "replies": 168055,
          "retweets": 579720,
          "quotes": 168169,
          "bookmarks": null
        },
        "hashtags": [],
        "media": []
      }
    ]
  },
  "video-summarize": {
    "filename": "sample.mp4",
    "summary": "This walkthrough shows how teams extract structured data from social video at scale without standing up scrapers or OAuth apps. It covers a single API key across platforms, shared caching, and why clean JSON beats brittle HTML parses.\n\nThe speaker contrasts fresh fetches with cache hits: the same profile call can drop from multi-second billed work to a sub-second free response. They also stress verifying per-minute Whisper billing via durationSeconds and creditsCharged in the response.\n\nClosing takeaways focus on bringing your own media files for transcript-plus-summary in one POST, and using request logs to prove cache savings.",
    "keyPoints": [
      "One Captapi key works across supported platforms — no per-network OAuth.",
      "Pass cache=true for a free 24h shared cache hit on social endpoints.",
      "Whisper file endpoints bill per minute; read durationSeconds and creditsCharged.",
      "Summarize returns the full transcript alongside summary/keyPoints/topics.",
      "Short clips yield shorter summaries; longer audio aims for 2–3 paragraphs and 4–8 bullets.",
      "Account request history exposes cacheHit and responseTimeMs side by side.",
      "Use multipart POST (-F file=@path) — never put the file in the query string.",
      "Empty/no-speech audio returns HTTP 422 on summarize (cannot summarize silence)."
    ],
    "topics": [
      "APIs",
      "data extraction",
      "automation",
      "billing",
      "caching"
    ],
    "sentiment": "positive",
    "transcript": "Hey everyone, welcome back to the channel. Today we are breaking down structured data APIs for social video. First, one API key across platforms beats stitching OAuth apps together. Second, the shared cache turns expensive profile lookups into free sub-second hits. Third, when you upload a file for Whisper, always check durationSeconds against creditsCharged. Finally, summarize gives you the AI digest plus the full transcript in the same JSON payload.",
    "transcriptSegments": [
      {
        "text": "Hey everyone, welcome back to the channel. Today we are breaking down structured data APIs for social video.",
        "start": 0.0,
        "duration": 8.2,
        "end": 8.2,
        "timestamp": "00:00"
      },
      {
        "text": "First, one API key across platforms beats stitching OAuth apps together.",
        "start": 8.2,
        "duration": 5.1,
        "end": 13.3,
        "timestamp": "00:08"
      },
      {
        "text": "Second, the shared cache turns expensive profile lookups into free sub-second hits.",
        "start": 13.3,
        "duration": 5.4,
        "end": 18.7,
        "timestamp": "00:13"
      },
      {
        "text": "Third, when you upload a file for Whisper, always check durationSeconds against creditsCharged.",
        "start": 18.7,
        "duration": 6.0,
        "end": 24.7,
        "timestamp": "00:18"
      },
      {
        "text": "Finally, summarize gives you the AI digest plus the full transcript in the same JSON payload.",
        "start": 24.7,
        "duration": 5.5,
        "end": 30.2,
        "timestamp": "00:24"
      }
    ],
    "wordCount": 70,
    "segments": 5,
    "language": "english",
    "durationSeconds": 30.2,
    "duration": 30.2,
    "creditsCharged": 2,
    "noSpeech": false
  },
  "video-transcript": {
    "filename": "sample.mp4",
    "transcript": "Hey everyone, welcome back to the channel. Today we're breaking down structured data APIs.",
    "transcriptSegments": [
      {
        "text": "Hey everyone, welcome back to the channel.",
        "start": 0.0,
        "duration": 4.12,
        "end": 4.12,
        "timestamp": "00:00"
      },
      {
        "text": "Today we're breaking down structured data APIs.",
        "start": 4.12,
        "duration": 4.28,
        "end": 8.4,
        "timestamp": "00:04"
      }
    ],
    "wordCount": 14,
    "segments": 2,
    "language": "english",
    "durationSeconds": 8.4,
    "duration": 8.4,
    "creditsCharged": 1,
    "noSpeech": false
  },
  "youtube-audio-transcript": {
    "platform": "youtube",
    "videoId": "jNQXAC9IVRw",
    "url": "https://www.youtube.com/watch?v=jNQXAC9IVRw",
    "source": "asr",
    "asrProvider": "groq-whisper-large-v3-turbo",
    "language": "en",
    "languageIsDetected": true,
    "durationSeconds": 19,
    "segments": [
      {
        "text": "Alright, so here we are in front of the elephants.",
        "startMs": 0,
        "endMs": 4000
      },
      {
        "text": "The cool thing about these guys is that they have really, really, really long fronts.",
        "startMs": 4000,
        "endMs": 12000
      },
      {
        "text": "And that's cool.",
        "startMs": 12000,
        "endMs": 14000
      },
      {
        "text": "And that's pretty much all there is to say.",
        "startMs": 16000,
        "endMs": 19000
      }
    ],
    "text": "Alright, so here we are in front of the elephants. The cool thing about these guys is that they have really, really, really long fronts. And that's cool. And that's pretty much all there is to say.",
    "creditsUsed": 2
  },
  "youtube-channel-details": {
    "url": "https://www.youtube.com/channel/UCX6OQ3DkcsbYNE6H8uQQuVA",
    "id": "UCX6OQ3DkcsbYNE6H8uQQuVA",
    "name": "MrBeast",
    "handle": "@MrBeast",
    "description": "SUBSCRIBE FOR A COOKIE!\nNew MrBeast or MrBeast Gaming video every single Saturday at noon eastern time!\nAccomplishments:\n- Raised $20,000,000 To Plant 20,000,000 Trees\n- Removed 30,000,000 pounds of trash from the ocean\n- Helped 2,000 people walk again\n- Helped 1,000 blind people see\n- Helped 1,000 deaf people hear\n- Built wells in Africa\n- Built and gave away 100 houses\n- Adopted every dog in a shelter (twice)\n- Given millions to charity\n- Started my own snack company Feastables\n- Started my own software company Viewstats\n- Gave away a private island (twice)\n- Gave away 1 million meals\n- I counted to 100k\n- Ran a marathon in the world's largest shoes\n- Survived 50 hours in Antarctica\n- Recreated Squid Game in real life\n- Created the largest competition show with 1000 people (Beast Games)\n- Gave $5,000,000 to one person\n\nTerms & Conditions of Current Sweepstakes: \nhttps://mrb.gg/bow-and-arrow\nhttps://bit.ly/MrB_Birthday_YT\nhttps://bit.ly/MrB_Cash_Giveaway",
    "subscriberCount": 510000000,
    "videoCount": 994,
    "viewCount": 135029730952,
    "thumbnailUrl": "https://yt3.googleusercontent.com/nxYrc_1_2f77DoBadyxMTmv7ZpRZapHR5jbuYe7PlPd5cIRJxtNNEYyOC0ZsxaDyJJzXrnJiuDE=s900-c-k-c0x00ffffff-no-rj",
    "bannerUrl": null,
    "country": "US",
    "joinedDate": "Feb 19, 2012",
    "verified": true,
    "links": [
      {
        "text": "$1,000,000 Contest",
        "url": "https://themostdangerousgames.com"
      },
      {
        "text": "Follow",
        "url": "https://instagram.com/mrbeast"
      }
    ],
    "platform": "youtube",
    "canonicalUrl": "https://www.youtube.com/@MrBeast",
    "countryName": "United States",
    "joinedAt": "2012-02-19",
    "tags": [
      "challenge",
      "philanthropy"
    ]
  },
  "youtube-channel-playlists": {
    "url": "https://www.youtube.com/@MrBeast",
    "totalReturned": 5,
    "playlists": [
      {
        "url": "https://www.youtube.com/playlist?list=PLoSWVnSA9vG8hI-SUpAimvYJrPh-PRRvp",
        "title": "If You Survive, You Win",
        "videoCount": 5,
        "thumbnailUrl": "https://i.ytimg.com/vi/tnTPaLOaHz8/hqdefault.jpg?sqp=-oaymwEXCOADEI4CSFryq4qpAwkIARUAAIhCGAE=&rs=AOn4CLCjPAnSe9imDV7q3RLqefBW_CQRCw"
      },
      {
        "url": "https://www.youtube.com/playlist?list=PLoSWVnSA9vG_s-XT40oPKF0iWFGw8pOp2",
        "title": "Helping People In Need",
        "videoCount": 10,
        "thumbnailUrl": "https://i.ytimg.com/tvfilm_banner/PLoSWVnSA9vG_s-XT40oPKF0iWFGw8pOp2/16_9_.jpg?sqp=CIK3qNMG-oaymwEICNYGEOADSFqi85f_AwYIsPuCygY=&rs=AOn4CLCIBDlHX0ennRaBJ6KUK7hIIyYqJQ"
      }
    ]
  },
  "youtube-channel-shorts": {
    "url": "https://www.youtube.com/@MrBeast",
    "totalReturned": 5,
    "shorts": [
      {
        "url": "https://www.youtube.com/shorts/Df5Y-2ndQyU",
        "title": "Read My Book, You Could Win $1,000,000",
        "publishedAt": null,
        "viewCount": 8900000,
        "durationSeconds": null,
        "thumbnailUrl": null,
        "channelName": "MrBeast"
      },
      {
        "url": "https://www.youtube.com/shorts/egvLKQe6I4I",
        "title": "Don't Pop the Balloon",
        "publishedAt": null,
        "viewCount": 90000000,
        "durationSeconds": null,
        "thumbnailUrl": null,
        "channelName": "MrBeast"
      }
    ]
  },
  "youtube-channel-streams": {
    "url": "https://www.youtube.com/@MrBeast",
    "totalReturned": 5,
    "streams": [
      {
        "url": "https://www.youtube.com/watch?v=AaMdXZMvT3w",
        "title": "Survive 30 Days On An Island With Your Ex, Win $250,000",
        "publishedAt": "2026-05-16T16:00:01.000Z",
        "viewCount": 89925200,
        "durationSeconds": 2349,
        "thumbnailUrl": "https://i.ytimg.com/vi/AaMdXZMvT3w/maxresdefault.jpg",
        "channelName": "MrBeast"
      },
      {
        "url": "https://www.youtube.com/watch?v=GpQSUjNsNm0",
        "title": "7 Days Stranded in The Arctic",
        "publishedAt": "2026-05-30T16:00:02.000Z",
        "viewCount": 91519007,
        "durationSeconds": 1935,
        "thumbnailUrl": "https://i.ytimg.com/vi/GpQSUjNsNm0/maxresdefault.jpg",
        "channelName": "MrBeast"
      }
    ]
  },
  "youtube-channel-videos": {
    "url": "https://www.youtube.com/@MrBeast",
    "totalReturned": 5,
    "videos": [
      {
        "url": "https://www.youtube.com/watch?v=lVylRtlPOIE",
        "title": "I Granted 100 Kids Their Biggest Wish!",
        "publishedAt": "2026-07-29T19:42:10.000Z",
        "viewCount": 31000000,
        "durationSeconds": 875,
        "thumbnailUrl": "https://i.ytimg.com/vi/lVylRtlPOIE/hqdefault.jpg?sqp=-oaymwEcCNACELwBSFXyq4qpAw4IARUAAIhCGAFwAcABBg==&rs=AOn4CLDEw9iu9Jqd9KZ9pBMfbkc-aipTog",
        "channelName": "MrBeast",
        "publishedTimeText": "4 days ago"
      },
      {
        "url": "https://www.youtube.com/watch?v=iYlODtkyw_I",
        "title": "Survive 30 Days Chained To A Stranger, Win $250,000",
        "publishedAt": "2026-07-03T19:42:10.000Z",
        "viewCount": 81000000,
        "durationSeconds": 2105,
        "thumbnailUrl": "https://i.ytimg.com/vi/iYlODtkyw_I/hqdefault.jpg?sqp=-oaymwEcCNACELwBSFXyq4qpAw4IARUAAIhCGAFwAcABBg==&rs=AOn4CLBr_mSSbkEXsEQf8rxuahzMDeW9Jg",
        "channelName": "MrBeast",
        "publishedTimeText": "1 month ago"
      }
    ]
  },
  "youtube-comment-replies": {
    "url": "https://www.youtube.com/watch?v=dQw4w9WgXcQ",
    "videoId": "dQw4w9WgXcQ",
    "commentId": "Ugzge340dBgB75hWBm54AaABAg",
    "totalReturned": 5,
    "replies": [
      {
        "id": "Ugzge340dBgB75hWBm54AaABAg.AHE8_QAWJx9AHE9eIiztxR",
        "author": "@linganguliguliwatcha",
        "authorChannelId": "UCjFRISlX-LPxiqViJAE3h6Q",
        "authorAvatarUrl": "https://yt3.ggpht.com/AbGqKNjK9k5tyOqdV7cdXx-GgnGuuGQ5wj8RN42U5YCDvYHT0vaOKXGFahR36iaDPseGN08DjQ=s88-c-k-c0x00ffffff-no-rj",
        "authorIsVerified": false,
        "authorIsChannelOwner": false,
        "text": "YOUTUBE AND ONE LIKE WOOHAAAAH",
        "likeCount": 7200,
        "replyCount": 5,
        "hasCreatorHeart": false,
        "publishedTimeText": "1 year ago",
        "publishedTime": "2025-08-03T20:35:17.000Z",
        "replyToId": "Ugzge340dBgB75hWBm54AaABAg"
      },
      {
        "id": "Ugzge340dBgB75hWBm54AaABAg.AHE8_QAWJx9AHEAB_-JmDA",
        "author": "@_bugrabilgin",
        "authorChannelId": "UCg9tPtxMOieUEyhSv63uJ4g",
        "authorAvatarUrl": "https://yt3.ggpht.com/LvMpN24GYYr8w43sGoMeYZYejDPJz_skehI6jm_XGGhfM5YeRa9OOsaplj60LnFNehE79ZxImg=s88-c-k-c0x00ffffff-no-rj",
        "authorIsVerified": false,
        "authorIsChannelOwner": false,
        "text": "HEY YOUTUBE",
        "likeCount": 3000,
        "replyCount": 2,
        "hasCreatorHeart": false,
        "publishedTimeText": "1 year ago",
        "publishedTime": "2025-08-03T20:35:17.000Z",
        "replyToId": "Ugzge340dBgB75hWBm54AaABAg"
      }
    ]
  },
  "youtube-comments": {
    "url": "https://www.youtube.com/watch?v=dQw4w9WgXcQ",
    "videoId": "dQw4w9WgXcQ",
    "totalReturned": 5,
    "totalComments": 2400000,
    "nextCursor": "Eg0SC2RRdzR3OVdnWGNRGAYyJSIRIgtkUXc0dzlXZ1hjUTAAeAJCEGNvbW1lbnRzLXNlY3Rpb24%3D",
    "hasMore": true,
    "comments": [
      {
        "id": "Ugzge340dBgB75hWBm54AaABAg",
        "author": "@YouTube",
        "authorChannelId": "UCBR8-60-B28hp2BmDPdntcQ",
        "authorAvatarUrl": "https://yt3.ggpht.com/3s6evpqAiDU9tQR4sC2siJippbH2RWVPnwHgyl4V0th2iuQz0VDQZbUhQBGmsxLYo-mjG6TqZQ=s88-c-k-c0x00ffffff-no-rj",
        "authorIsVerified": true,
        "authorIsChannelOwner": false,
        "text": "can confirm: he never gave us up",
        "likeCount": 290000,
        "replyCount": 961,
        "hasCreatorHeart": false,
        "publishedTimeText": "1 year ago",
        "publishedTime": "2025-08-03T20:35:12.000Z"
      },
      {
        "id": "UgxTsG2dsspEiq6MAZJ4AaABAg",
        "author": "@MariahRhona",
        "authorChannelId": "UCe8dr6l5fgxVh6peaTtx8XA",
        "authorAvatarUrl": "https://yt3.ggpht.com/sEIirS_KS8tpBOKKPUIrE887msAjyf3N4gggHploxxmmwt3B2MkNRBB_t90olc0hXeghSsLj3A=s88-c-k-c0x00ffffff-no-rj",
        "authorIsVerified": false,
        "authorIsChannelOwner": false,
        "text": "who came here saying this video was taken down",
        "likeCount": 27000,
        "replyCount": 982,
        "hasCreatorHeart": false,
        "publishedTimeText": "3 days ago",
        "publishedTime": "2026-07-31T20:35:12.000Z"
      }
    ]
  },
  "youtube-community-post-details": {
    "platform": "youtube",
    "id": "UgkxfMvMnSnV3Ww9HwAY2wFGmVevmhRaYAYO",
    "url": "https://www.youtube.com/post/UgkxfMvMnSnV3Ww9HwAY2wFGmVevmhRaYAYO",
    "text": "Inside this box is the world's FIRST 500M Play Button. We're 10M away from 500M and I cannot wait to see what’s in here so help me out.",
    "publishedAt": "2026-07-03T19:42:10.000Z",
    "channelName": "MrBeast",
    "channelUrl": "https://www.youtube.com/@MrBeast",
    "likes": "727K",
    "comments": 16260,
    "images": [
      "https://yt3.ggpht.com/BgBr4f_nvLm84HY2JVaPiDZRLZXJsqA7Q29CJkAksrwRFNXN1GgQJxzjYfzWUYR6ZekKBXCVwxPQKw=s1000-rw-nd-v1"
    ],
    "publishedTimeText": "1 month ago (edited)"
  },
  "youtube-community-posts": {
    "url": "https://www.youtube.com/@MrBeast",
    "totalReturned": 5,
    "hasMore": true,
    "nextCursor": "4qmFsgKTARIYVUNYNk9RM0RrY3NiWU5FNkg4dVFRdVZBGl5FZ1Z3YjNOMGM3Z0JBSklEQUtvREtBb2tVVEpqTlZKR1VuSmtSM0JPVTBaS1ExVnFRbGRWUjBaWlZHNWtZVTB3TVZKUlZVVTlLQXJ5QmdrS0Iwb0FvZ0VDQ0FFJTNEmgIWYmFja3N0YWdlLWl0ZW0tc2VjdGlvbg%3D%3D",
    "posts": [
      {
        "id": "UgkxB7POmB4C7U0I3kIEWRZpYfE2t-ieP9CA",
        "url": "https://www.youtube.com/post/UgkxB7POmB4C7U0I3kIEWRZpYfE2t-ieP9CA",
        "author": "MrBeast",
        "channel": {
          "id": "UCX6OQ3DkcsbYNE6H8uQQuVA",
          "title": "MrBeast",
          "url": "https://www.youtube.com/@MrBeast",
          "handle": "@MrBeast"
        },
        "text": "Some more fun wedding photos 🥰",
        "likeCount": 3200000,
        "likeCountText": "3.2M",
        "hashtags": [],
        "linkedVideos": [],
        "video": null,
        "publishedTime": "2026-07-23T19:42:10.000Z",
        "publishedTimeText": "10 days ago",
        "postType": "image",
        "images": [
          "https://yt3.ggpht.com/bFmb7RbyvsNTUS3otE4oc2tqI5CZyl3apwKmjnqnTjFuv1mwxWG7hWlZCuiWlRYrd3oCd_nAtBWVsw=s2641-c-fcrop64=1,00002578ffffda87-rw-nd-v1",
          "https://yt3.ggpht.com/1Oxcyk2wshlCOoZYiTWUFoixDaomfdtlcIKiGv_ozoT4Lfs9CZx-3VTxbNeQlJOOV_h7CdWjWF8QIA=s1536-c-fcrop64=1,00002000ffffdfff-rw-nd-v1"
        ],
        "image": "https://yt3.ggpht.com/bFmb7RbyvsNTUS3otE4oc2tqI5CZyl3apwKmjnqnTjFuv1mwxWG7hWlZCuiWlRYrd3oCd_nAtBWVsw=s2641-c-fcrop64=1,00002578ffffda87-rw-nd-v1",
        "sourceUrl": "https://www.youtube.com/post/UgkxB7POmB4C7U0I3kIEWRZpYfE2t-ieP9CA",
        "likeCountApproximate": true
      },
      {
        "id": "Ugkxg-YuyvHwnlFZRktAZHHELzGBrskCHChJ",
        "url": "https://www.youtube.com/post/Ugkxg-YuyvHwnlFZRktAZHHELzGBrskCHChJ",
        "author": "MrBeast",
        "channel": {
          "id": "UCX6OQ3DkcsbYNE6H8uQQuVA",
          "title": "MrBeast",
          "url": "https://www.youtube.com/@MrBeast",
          "handle": "@MrBeast"
        },
        "text": "I found MrsBeast ❤️❤️❤️",
        "likeCount": 3200000,
        "likeCountText": "3.2M",
        "hashtags": [],
        "linkedVideos": [],
        "video": null,
        "publishedTime": "2026-07-21T19:42:10.000Z",
        "publishedTimeText": "12 days ago",
        "postType": "image",
        "images": [
          "https://yt3.ggpht.com/oiElfzENMAx3umYLMOH0sZOodVZChBV2L0ddB-KbqwR9B0djUx9o-JMD8ehXMt9fmKtAkGeO3ySq=s4000-c-fcrop64=1,00000000ffffc002-rw-nd-v1",
          "https://yt3.ggpht.com/sL9SyPNxLv5TT8CMSqQFy3o0DhtCcyxQrCt2hfIXYSHNhDZ0_f2ORfAZs8K8aAXoZQ05G7hsnOviCQ=s4000-c-fcrop64=1,00001ffeffffe001-rw-nd-v1"
        ],
        "image": "https://yt3.ggpht.com/oiElfzENMAx3umYLMOH0sZOodVZChBV2L0ddB-KbqwR9B0djUx9o-JMD8ehXMt9fmKtAkGeO3ySq=s4000-c-fcrop64=1,00000000ffffc002-rw-nd-v1",
        "sourceUrl": "https://www.youtube.com/post/Ugkxg-YuyvHwnlFZRktAZHHELzGBrskCHChJ",
        "likeCountApproximate": true
      }
    ]
  },
  "youtube-hashtag-search": {
    "query": "music",
    "totalReturned": 5,
    "results": [
      {
        "url": "https://www.youtube.com/watch?v=3iAiWIytqdw",
        "title": "Forever Young - Music Travel Love ft. Bugoy Drilon",
        "publishedAt": "2025-04-16T00:00:08.000Z",
        "viewCount": 31307210,
        "durationSeconds": 265,
        "thumbnailUrl": "https://i.ytimg.com/vi/3iAiWIytqdw/maxresdefault.jpg",
        "channelName": "Music Travel Love"
      },
      {
        "url": "https://www.youtube.com/watch?v=WpYPeL-gF5U",
        "title": "Stay Royalty - Official Music Video of The Royalty Family (2020)",
        "publishedAt": "2020-12-27T16:12:50.000Z",
        "viewCount": 14883690,
        "durationSeconds": 194,
        "thumbnailUrl": "https://i.ytimg.com/vi/WpYPeL-gF5U/maxresdefault.jpg",
        "channelName": "The Royalty Family"
      }
    ]
  },
  "youtube-playlist": {
    "platform": "youtube",
    "url": "https://www.youtube.com/playlist?list=PLMC9KNkIncKtPzgY-5rmhvj7fax8fdxoj",
    "id": "PLMC9KNkIncKtPzgY-5rmhvj7fax8fdxoj",
    "title": "Pop Music Playlist - Timeless Pop Songs (Updated Weekly 2026)",
    "channelName": "by Redlist - Just Hits",
    "owner": {
      "id": "UCs72iRpTEuwV3y6pdWYLgiw",
      "name": "by Redlist - Just Hits",
      "url": "https://www.youtube.com/@Redlist-JustHits",
      "handle": "@Redlist-JustHits"
    },
    "totalVideos": 200,
    "totalReturned": 5,
    "videos": [
      {
        "id": "ekr2nIex040",
        "url": "https://www.youtube.com/watch?v=ekr2nIex040",
        "title": "ROSÉ & Bruno Mars - APT. (Official Music Video)",
        "publishedAt": "2025-08-03T20:35:07.000Z",
        "publishedTimeText": "1y ago",
        "viewCount": 2606548493,
        "durationSeconds": 173,
        "thumbnailUrl": "https://i.ytimg.com/vi_webp/ekr2nIex040/sddefault.webp?v=6711dbac",
        "channelName": "ROSÉ",
        "channel": {
          "id": "UCBo1hnzxV9rz3WVsv__Rn1g",
          "title": "ROSÉ",
          "url": "https://www.youtube.com/channel/UCBo1hnzxV9rz3WVsv__Rn1g"
        }
      },
      {
        "id": "kPa7bsKwL-c",
        "url": "https://www.youtube.com/watch?v=kPa7bsKwL-c",
        "title": "Lady Gaga, Bruno Mars - Die With A Smile (Official Music Video)",
        "publishedAt": "2025-08-03T20:35:07.000Z",
        "publishedTimeText": "1y ago",
        "viewCount": 1782354502,
        "durationSeconds": 252,
        "thumbnailUrl": "https://i.ytimg.com/vi/kPa7bsKwL-c/sddefault.jpg",
        "channelName": "LadyGagaVEVO",
        "channel": {
          "id": "UC07Kxew-cMIaykMOkzqHtBQ",
          "title": "LadyGagaVEVO",
          "url": "https://www.youtube.com/channel/UC07Kxew-cMIaykMOkzqHtBQ"
        }
      }
    ]
  },
  "youtube-playlist-videos": {
    "url": "https://www.youtube.com/playlist?list=PLMC9KNkIncKtPzgY-5rmhvj7fax8fdxoj",
    "id": "PLMC9KNkIncKtPzgY-5rmhvj7fax8fdxoj",
    "totalVideos": 200,
    "totalReturned": 5,
    "videos": [
      {
        "id": "ekr2nIex040",
        "url": "https://www.youtube.com/watch?v=ekr2nIex040",
        "title": "ROSÉ & Bruno Mars - APT. (Official Music Video)",
        "publishedAt": "2025-08-03T20:35:07.000Z",
        "publishedTimeText": "1y ago",
        "viewCount": 2606548493,
        "durationSeconds": 173,
        "thumbnailUrl": "https://i.ytimg.com/vi_webp/ekr2nIex040/sddefault.webp?v=6711dbac",
        "channelName": "ROSÉ",
        "channel": {
          "id": "UCBo1hnzxV9rz3WVsv__Rn1g",
          "title": "ROSÉ",
          "url": "https://www.youtube.com/channel/UCBo1hnzxV9rz3WVsv__Rn1g"
        }
      },
      {
        "id": "kPa7bsKwL-c",
        "url": "https://www.youtube.com/watch?v=kPa7bsKwL-c",
        "title": "Lady Gaga, Bruno Mars - Die With A Smile (Official Music Video)",
        "publishedAt": "2025-08-03T20:35:07.000Z",
        "publishedTimeText": "1y ago",
        "viewCount": 1782354502,
        "durationSeconds": 252,
        "thumbnailUrl": "https://i.ytimg.com/vi/kPa7bsKwL-c/sddefault.jpg",
        "channelName": "LadyGagaVEVO",
        "channel": {
          "id": "UC07Kxew-cMIaykMOkzqHtBQ",
          "title": "LadyGagaVEVO",
          "url": "https://www.youtube.com/channel/UC07Kxew-cMIaykMOkzqHtBQ"
        }
      }
    ]
  },
  "youtube-search": {
    "query": "space",
    "totalReturned": 5,
    "nextCursor": "EtACEgVzcGFjZRrGAlNCU0NBUXRxUm14WGQyaFFVbUpRZDRJQkMwdzVUazFTUzFsVE5uYzBnZ0VMUVhVeWJEWk9iMlo0TUVXQ0FRc3pXamh1TkRONWNDMXRaNElCQzJseU9HcE5lVXhDVXpacmdnRUxaeTFuYTJOM1dXdGtSRUdDQVF0R1RsSTNZVGhxYjBOSGM0SUJDMkpvTVd4amJqSlRVRTVuZ2dFTFZVdHJMV2hWUVd0UGQydUNBUXRvWjAxcVlqVjJhbWhtYTRJQkN6SlVhbnBKTXpWSk5sTmpnZ0VMV2xWMVVVMUtOVTh6V0UyQ0FRdFliWGxrTjBWRFZHeEpXWUlCQzFWek1sb3RWME01Y21GdmdnRUxaVmRmYlc5V05uWnZkRUdDQVF0WloyTlVkMlY1Vmt0a2I3SUJCZ29FQ0JZUUF1b0JCQWdDRUJrJTNEGIHg6BgiC3NlYXJjaC1mZWVk",
    "hasMore": true,
    "results": [
      {
        "type": "video",
        "id": "jFlWwhPRbPw",
        "url": "https://www.youtube.com/watch?v=jFlWwhPRbPw",
        "title": "James Webb Found a Structure So Big It Breaks Known Physics",
        "publishedAt": "2026-07-23T19:42:10.000Z",
        "viewCount": 38769,
        "durationSeconds": 7924,
        "thumbnailUrl": "https://i.ytimg.com/vi/jFlWwhPRbPw/hq720.jpg?sqp=-oaymwEcCNAFEJQDSFXyq4qpAw4IARUAAIhCGAFwAcABBg==&rs=AOn4CLA7UvQbAJ_-ucLxF_Y5rLx6Et8OqQ",
        "channelName": "Late Science",
        "channelId": "UCIqH5kGFOM_lP9x_AmPodjQ",
        "channel": {
          "id": "UCIqH5kGFOM_lP9x_AmPodjQ",
          "title": "Late Science",
          "handle": "@Late_Science",
          "url": "https://www.youtube.com/@Late_Science",
          "thumbnail": null
        },
        "badges": [
          "4K"
        ],
        "publishedTimeText": "10 days ago"
      },
      {
        "type": "video",
        "id": "L9NMRKYS6w4",
        "url": "https://www.youtube.com/watch?v=L9NMRKYS6w4",
        "title": "James Webb Detected a Sign of a Different Universe That Shattered Every Model Built Since Einstein",
        "publishedAt": "2026-06-03T19:42:10.000Z",
        "viewCount": 151088,
        "durationSeconds": 6441,
        "thumbnailUrl": "https://i.ytimg.com/vi/L9NMRKYS6w4/hq720.jpg?sqp=-oaymwEcCNAFEJQDSFXyq4qpAw4IARUAAIhCGAFwAcABBg==&rs=AOn4CLDucFGeHFH4XAYqCTdLsGr5dul9IA",
        "channelName": "SPACE BEFOREAFTER",
        "channelId": "UCxbnsftoQou1IfWZlEb_1iA",
        "channel": {
          "id": "UCxbnsftoQou1IfWZlEb_1iA",
          "title": "SPACE BEFOREAFTER",
          "handle": "@space-before-after",
          "url": "https://www.youtube.com/@space-before-after",
          "thumbnail": null
        },
        "badges": [],
        "publishedTimeText": "2 months ago"
      }
    ],
    "videos": [
      {
        "type": "video",
        "id": "jFlWwhPRbPw",
        "url": "https://www.youtube.com/watch?v=jFlWwhPRbPw",
        "title": "James Webb Found a Structure So Big It Breaks Known Physics",
        "publishedAt": "2026-07-23T19:42:10.000Z",
        "viewCount": 38769,
        "durationSeconds": 7924,
        "thumbnailUrl": "https://i.ytimg.com/vi/jFlWwhPRbPw/hq720.jpg?sqp=-oaymwEcCNAFEJQDSFXyq4qpAw4IARUAAIhCGAFwAcABBg==&rs=AOn4CLA7UvQbAJ_-ucLxF_Y5rLx6Et8OqQ",
        "channelName": "Late Science",
        "channelId": "UCIqH5kGFOM_lP9x_AmPodjQ",
        "channel": {
          "id": "UCIqH5kGFOM_lP9x_AmPodjQ",
          "title": "Late Science",
          "handle": "@Late_Science",
          "url": "https://www.youtube.com/@Late_Science",
          "thumbnail": null
        },
        "badges": [
          "4K"
        ],
        "publishedTimeText": "10 days ago"
      },
      {
        "type": "video",
        "id": "L9NMRKYS6w4",
        "url": "https://www.youtube.com/watch?v=L9NMRKYS6w4",
        "title": "James Webb Detected a Sign of a Different Universe That Shattered Every Model Built Since Einstein",
        "publishedAt": "2026-06-03T19:42:10.000Z",
        "viewCount": 151088,
        "durationSeconds": 6441,
        "thumbnailUrl": "https://i.ytimg.com/vi/L9NMRKYS6w4/hq720.jpg?sqp=-oaymwEcCNAFEJQDSFXyq4qpAw4IARUAAIhCGAFwAcABBg==&rs=AOn4CLDucFGeHFH4XAYqCTdLsGr5dul9IA",
        "channelName": "SPACE BEFOREAFTER",
        "channelId": "UCxbnsftoQou1IfWZlEb_1iA",
        "channel": {
          "id": "UCxbnsftoQou1IfWZlEb_1iA",
          "title": "SPACE BEFOREAFTER",
          "handle": "@space-before-after",
          "url": "https://www.youtube.com/@space-before-after",
          "thumbnail": null
        },
        "badges": [],
        "publishedTimeText": "2 months ago"
      }
    ],
    "shorts": [],
    "channels": [],
    "playlists": []
  },
  "youtube-shorts-comments": {
    "url": "https://www.youtube.com/shorts/egvLKQe6I4I",
    "videoId": "egvLKQe6I4I",
    "totalReturned": 2,
    "totalComments": 12000,
    "nextCursor": null,
    "hasMore": false,
    "comments": [
      {
        "id": "Ugshortcomment001",
        "author": "@MrBeast",
        "authorAvatarUrl": "https://yt3.ggpht.com/nxYrc_1_2f77DoBadyxMTmv7ZpRZapHR5jbuYe7PlPd5cIRJxtNNEYyOC0ZsxaDyJJzXrnJiuDE=s88-c-k-c0x00ffffff-no-rj",
        "authorIsVerified": true,
        "authorIsChannelOwner": true,
        "text": "Did you pop it?",
        "likeCount": 50000,
        "replyCount": 1200,
        "hasCreatorHeart": true,
        "publishedTimeText": "1 year ago"
      },
      {
        "id": "Ugshortcomment002",
        "author": "@viewer123",
        "authorAvatarUrl": "https://yt3.ggpht.com/ytc/default=s88-c-k-c0x00ffffff-no-rj",
        "authorIsVerified": false,
        "authorIsChannelOwner": false,
        "text": "I would have popped it instantly",
        "likeCount": 8000,
        "replyCount": 40,
        "hasCreatorHeart": false,
        "publishedTimeText": "1 year ago"
      }
    ]
  },
  "youtube-shorts-stats": {
    "url": "https://www.youtube.com/shorts/egvLKQe6I4I",
    "id": "egvLKQe6I4I",
    "title": "Don't Pop the Balloon",
    "description": "Don't pop the balloon...",
    "channelName": "MrBeast",
    "channelId": "UCX6OQ3DkcsbYNE6H8uQQuVA",
    "channelUrl": "https://www.youtube.com/channel/UCX6OQ3DkcsbYNE6H8uQQuVA",
    "publishedAt": "2024-01-01T00:00:00Z",
    "durationSeconds": 51,
    "durationFormatted": "00:00:51",
    "viewCount": 97835773,
    "likeCount": 2500000,
    "commentCount": 12000,
    "thumbnailUrl": "https://i.ytimg.com/vi/egvLKQe6I4I/hqdefault.jpg",
    "genre": "Entertainment",
    "tags": [],
    "isShort": true,
    "contentType": "short"
  },
  "youtube-shorts-summarizer": {
    "url": "https://www.youtube.com/shorts/egvLKQe6I4I",
    "videoId": "egvLKQe6I4I",
    "title": "Don't Pop the Balloon",
    "summary": "MrBeast challenges people not to pop a balloon in a high-stakes Short.",
    "keyPoints": [
      "Contestants must keep a balloon intact.",
      "Quick comedy beat typical of YouTube Shorts."
    ],
    "topics": [
      "challenge",
      "shorts"
    ],
    "sentiment": "positive"
  },
  "youtube-shorts-transcript": {
    "url": "https://www.youtube.com/shorts/egvLKQe6I4I",
    "videoId": "egvLKQe6I4I",
    "title": "Don't Pop the Balloon",
    "transcript": "Don't pop the balloon. Whatever you do, don't pop it...",
    "transcriptSegments": [
      {
        "text": "Don't pop the balloon.",
        "start": 0,
        "duration": 2.0,
        "timestamp": "00:00"
      },
      {
        "text": "Whatever you do, don't pop it.",
        "start": 2.0,
        "duration": 2.4,
        "timestamp": "00:02"
      }
    ],
    "wordCount": 42,
    "segments": 2,
    "language": "English"
  },
  "youtube-summarizer": {
    "url": "https://www.youtube.com/watch?v=dQw4w9WgXcQ",
    "videoId": "dQw4w9WgXcQ",
    "title": "Rick Astley - Never Gonna Give You Up (Official Video) (4K Remaster)",
    "summary": "The song 'Never Gonna Give You Up' by Rick Astley is a classic pop anthem that emphasizes unwavering commitment and loyalty in a romantic relationship. The lyrics express a deep emotional connection, highlighting the importance of honesty and trust between partners. Astley reassures his loved one that he will always be there for them, promising never to abandon or hurt them, which resonates with listeners on a personal level.\n\nThis iconic track has gained a cultural significance beyond its initial release, becoming a symbol of internet memes and nostalgia. Its catchy melody and memorable chorus have made it a timeless favorite, often associated with themes of love, dedication, and sincerity. The song's upbeat tempo and heartfelt message continue to engage audiences, making it a staple in pop music history.",
    "keyPoints": [
      "Emphasizes commitment and loyalty in relationships.",
      "Highlights the importance of honesty and trust.",
      "Reassures loved ones of unwavering support.",
      "Cultural icon associated with internet memes.",
      "Timeless melody and catchy chorus.",
      "Resonates with themes of love and dedication.",
      "Continues to engage audiences across generations."
    ],
    "topics": [
      "Rick Astley",
      "Never Gonna Give You Up",
      "Pop Music",
      "Commitment",
      "Love",
      "Nostalgia",
      "Internet Memes"
    ],
    "sentiment": "positive"
  },
  "youtube-transcript": {
    "url": "https://www.youtube.com/watch?v=dQw4w9WgXcQ",
    "videoId": "dQw4w9WgXcQ",
    "title": "Rick Astley - Never Gonna Give You Up (Official Video) (4K Remaster)",
    "transcript": "[♪♪♪] ♪ We're no strangers to love ♪ ♪ You know the rules and so do I ♪ ♪ A full commitment's what I'm thinking of ♪ ♪ You wouldn't get this from any other guy ♪ ♪ I just wanna tell you how I'm feeling ♪ ♪ Gotta make you understand ♪ ♪ Never gonna give you up ♪ ♪ Never gonna let you down ♪ ♪ Never gonna run around and desert you ♪ ♪ Never gonna make you cry ♪ ♪ Never gonna say goodbye ♪ ♪ Never gonna tell a lie and hurt you ♪ ...",
    "transcriptSegments": [
      {
        "text": "[♪♪♪]",
        "start": 1.36,
        "duration": 1.68,
        "end": 3.04,
        "timestamp": "00:01"
      },
      {
        "text": "♪ We're no strangers to love ♪",
        "start": 18.64,
        "duration": 3.24,
        "end": 21.88,
        "timestamp": "00:18"
      }
    ],
    "wordCount": 487,
    "segments": 61,
    "language": "en"
  },
  "youtube-trending-shorts": {
    "platform": "youtube",
    "query": "trending",
    "totalReturned": 5,
    "shorts": [
      {
        "url": "https://www.youtube.com/shorts/ggMTGsuaooU",
        "title": "GO CRAZY! 👀 2026 Group Dance Trend #Shorts #Dance #Squad #Trending #fypシ Kaido Gia Chowbaby & more",
        "viewCount": 121000
      },
      {
        "url": "https://www.youtube.com/shorts/O07T9_5VIRI",
        "title": "who remembers this trend?😳 #trending #viral #tiktok #funny",
        "viewCount": 23000000
      }
    ]
  },
  "youtube-video-details": {
    "url": "https://www.youtube.com/watch?v=dQw4w9WgXcQ",
    "id": "dQw4w9WgXcQ",
    "title": "Rick Astley - Never Gonna Give You Up (Official Video) (4K Remaster)",
    "description": "The official video for “Never Gonna Give You Up” by Rick Astley. \n\nNever: The Autobiography 📚 OUT NOW! \nFollow this link to get your copy and listen to Rick’s ‘Never’ playlist ❤️ #RickAstleyNever\nhttps://linktr.ee/rickastleynever\n\n“Never Gonna Give You Up” was a global smash on its release in July 1987, topping the charts in 25 countries including Rick’s native UK and the US Billboard Hot 100.  It also won the Brit Award for Best single in 1988. Stock Aitken and Waterman wrote and produced the track which was the lead-off single and lead track from Rick’s debut LP “Whenever You Need Somebody”.  The album was itself a UK number one and would go on to sell over 15 million copies worldwide.\n\nThe legendary video was directed by Simon West – who later went on to make Hollywood blockbusters such as Con Air, Lara Croft – Tomb Raider and The Expendables 2.  The video passed the 1bn YouTube views milestone on 28 July 2021.\n\nSubscribe to the official Rick Astley YouTube channel: https://RickAstley.lnk.to/YTSubID\n\nFollow Rick Astley:\nFacebook: https://RickAstley.lnk.to/FBFollowID \nTwitter: http …",
    "channelName": "Rick Astley",
    "channelId": "UCuAXFkgsw1L7xaCfnd5JJOw",
    "channelUrl": "https://www.youtube.com/channel/UCuAXFkgsw1L7xaCfnd5JJOw",
    "publishedAt": "2009-10-24T23:57:33-07:00",
    "durationSeconds": 213,
    "viewCount": 1797826473,
    "likeCount": 19283915,
    "commentCount": 2400000,
    "thumbnailUrl": "https://i.ytimg.com/vi_webp/dQw4w9WgXcQ/sddefault.webp",
    "genre": "Music",
    "tags": [
      "rick astley",
      "Never Gonna Give You Up"
    ],
    "durationFormatted": "00:03:33"
  },
  "youtube-video-sponsors": {
    "videoId": "Wdjh81uH6FU",
    "videoDurationSeconds": 938.852,
    "totalReturned": 5,
    "segments": [
      {
        "category": "selfpromo",
        "actionType": "skip",
        "startSeconds": 554.515,
        "endSeconds": 638.201,
        "startFormatted": "9:15",
        "endFormatted": "10:38",
        "durationSeconds": 83.686,
        "votes": 1,
        "uuid": "52f9974390e30c4941d529cb028dfa56886a6e738fd1c5f1603a37f9bd9c21217"
      },
      {
        "category": "sponsor",
        "actionType": "skip",
        "startSeconds": 600.675,
        "endSeconds": 617.15,
        "startFormatted": "10:01",
        "endFormatted": "10:17",
        "durationSeconds": 16.475,
        "votes": 0,
        "uuid": "6377104df535c8eb2c2d7d6437320e71660b93a02517da2ba668c3813d7de6ff7"
      },
      {
        "category": "sponsor",
        "actionType": "skip",
        "startSeconds": 555.65,
        "endSeconds": 560.175,
        "startFormatted": "9:16",
        "endFormatted": "9:20",
        "durationSeconds": 4.525,
        "votes": 0,
        "uuid": "f75d77a0658f668c014ffa63f26f2ecc439a6d6b18b868d93c0875f55a47ba017"
      },
      {
        "category": "selfpromo",
        "actionType": "skip",
        "startSeconds": 567.302,
        "endSeconds": 573,
        "startFormatted": "9:27",
        "endFormatted": "9:33",
        "durationSeconds": 5.698,
        "votes": 0,
        "uuid": "328569d7ae428c1243bc54f010800a5cf6b5449e47abd3ee0f8093531ebeb8137"
      },
      {
        "category": "sponsor",
        "actionType": "skip",
        "startSeconds": 621.375,
        "endSeconds": 627.7,
        "startFormatted": "10:21",
        "endFormatted": "10:28",
        "durationSeconds": 6.325,
        "votes": -1,
        "uuid": "ee142c1cb73f13b3eceef18ffdd1eafd763c1adaef8df88f2c2b20f768e40ad27"
      }
    ]
  }
};

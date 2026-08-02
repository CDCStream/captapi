// AUTO-GENERATED — do not edit by hand.
// Real example responses captured live from https://api.captapi.com.
// Arrays are truncated to 2 items and long strings shortened for display.
// Regenerate: python backend/gen_examples.py (source: backend/api_snapshots.json).

export const API_EXAMPLES: Record<string, Record<string, unknown>> = {
  "account-balance": {
    "plan": "free",
    "monthlyQuota": 100,
    "subscriptionCredits": 0,
    "topupCredits": 9599,
    "totalCredits": 9599,
    "subscriptionRenewsAt": null
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
      },
      {
        "endpoint": "/v1/tiktok/live-info",
        "platform": "tiktok",
        "requests": 2,
        "creditsUsed": 14,
        "successfulRequests": 2,
        "failedRequests": 0
      },
      {
        "endpoint": "/v1/tiktok/search-suggestions",
        "platform": "tiktok",
        "requests": 2,
        "creditsUsed": 14,
        "successfulRequests": 0,
        "failedRequests": 2
      },
      {
        "endpoint": "/v1/tiktok-shop/user-showcase",
        "platform": "tiktok_shop",
        "requests": 2,
        "creditsUsed": 12,
        "successfulRequests": 1,
        "failedRequests": 1
      }
    ]
  },
  "account-request-history": {
    "totalReturned": 5,
    "requests": [
      {
        "endpoint": "/v1/instagram/basic-profile",
        "platform": "instagram",
        "resourceUrl": "instagram_user:adencylnozturk",
        "creditsUsed": 0,
        "cacheHit": true,
        "statusCode": 200,
        "responseTimeMs": 154,
        "errorMessage": null,
        "createdAt": "2026-07-18T11:31:44.31599+00:00"
      },
      {
        "endpoint": "/v1/instagram/basic-profile",
        "platform": "instagram",
        "resourceUrl": "instagram_user:adencylnozturk",
        "creditsUsed": 1,
        "cacheHit": false,
        "statusCode": 200,
        "responseTimeMs": 4980,
        "errorMessage": null,
        "createdAt": "2026-07-18T11:31:21.584147+00:00"
      },
      {
        "endpoint": "/v1/instagram/basic-profile",
        "platform": "instagram",
        "resourceUrl": "instagram_user:adencylnozturk",
        "creditsUsed": 1,
        "cacheHit": false,
        "statusCode": 200,
        "responseTimeMs": 4168,
        "errorMessage": null,
        "createdAt": "2026-07-18T11:31:20.30634+00:00"
      },
      {
        "endpoint": "/v1/pinterest/board",
        "platform": "pinterest",
        "resourceUrl": "https://www.pinterest.com/potterybarn/indigo-blues-lookbook/",
        "creditsUsed": 3,
        "cacheHit": false,
        "statusCode": 200,
        "responseTimeMs": 17558,
        "errorMessage": null,
        "createdAt": "2026-07-18T11:29:07.873651+00:00"
      },
      {
        "endpoint": "/v1/facebook/marketplace-item",
        "platform": "facebook",
        "resourceUrl": "https://www.facebook.com/marketplace/item/2228870800986975/",
        "creditsUsed": 1,
        "cacheHit": false,
        "statusCode": 200,
        "responseTimeMs": 10482,
        "errorMessage": null,
        "createdAt": "2026-07-18T11:28:59.677517+00:00"
      }
    ]
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
      },
      {
        "asin": "B088NRLMPV",
        "title": "Anker USB C to USB C Cable, 60W Fast Charging Cable (2-Pack, 6 ft, Black) | For iPhone 17 Series, iPad mini 6, and More",
        "url": "https://www.amazon.com/dp/B088NRLMPV",
        "image": "https://m.media-amazon.com/images/I/71IE9dLBduL._AC_UY218_.jpg",
        "price": 9.99,
        "currency": "USD",
        "priceFormatted": "$9.99",
        "rating": 4.7,
        "reviews": null,
        "isPrime": false,
        "isBestSeller": true,
        "isSponsored": false
      },
      {
        "asin": "B09SG2Q23M",
        "title": "Anker Power Strip with 2100J Surge Protector, Outlet Extender, 20W, 12 AC | 5ft Extension Cord with Multiple Outlets, 1 USB C, 2 USB A, Home Office, Dorm Room Essentials, TUV Listed",
        "url": "https://www.amazon.com/dp/B09SG2Q23M",
        "image": "https://m.media-amazon.com/images/I/71FtSiqsK3L._AC_UY218_.jpg",
        "price": 23.99,
        "currency": "USD",
        "priceFormatted": "$23.99",
        "rating": 4.8,
        "reviews": null,
        "isPrime": false,
        "isBestSeller": false,
        "isSponsored": false
      },
      {
        "asin": "B0BQLLB61B",
        "title": "Anker USB C Hub, 5-in-1 USBC to HDMI Splitter with 4K Display | 85W Max PD, 1 Powered USB-C 5Gbps & 2 Powered USB-A 3.0 5Gbps Data Ports, for MacBook Pro, MacBook Air, Dell and More (Black)",
        "url": "https://www.amazon.com/dp/B0BQLLB61B",
        "image": "https://m.media-amazon.com/images/I/615HRY2dnML._AC_UY218_.jpg",
        "price": 17.99,
        "currency": "USD",
        "priceFormatted": "$17.99",
        "rating": 4.4,
        "reviews": null,
        "isPrime": false,
        "isBestSeller": true,
        "isSponsored": false
      }
    ]
  },
  "analytics-compare": {
    "count": 2,
    "resolved": 2,
    "results": [
      {
        "platform": "youtube",
        "url": "https://www.youtube.com/watch?v=dQw4w9WgXcQ",
        "id": "dQw4w9WgXcQ",
        "title": "Rick Astley - Never Gonna Give You Up (Official Video) (4K Remaster)",
        "publishedAt": "2009-10-24T23:57:33-07:00",
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
          "likes": 19303349,
          "comments": 2400000,
          "shares": null,
          "saves": null,
          "interactions": 21703349,
          "engagementRate": 0.0121
        }
      },
      {
        "platform": "youtube",
        "url": "https://www.youtube.com/watch?v=jNQXAC9IVRw",
        "id": "jNQXAC9IVRw",
        "title": "Me at the zoo",
        "publishedAt": "2005-04-23T20:31:52-07:00",
        "durationSeconds": 19,
        "thumbnailUrl": "https://i.ytimg.com/vi/jNQXAC9IVRw/hqdefault.jpg?sqp=-oaymwEmCOADEOgC8quKqQMa8AEB-AG-AoAC8AGKAgwIABABGFUgWShlMA8=&rs=AOn4CLA9eLBatYv9WbkD4BbZ2Im-biSPTw",
        "author": {
          "username": "jawed",
          "displayName": "jawed",
          "url": "https://www.youtube.com/channel/UC4QobU6STFB0P71PMvOGN5A",
          "verified": null
        },
        "metrics": {
          "views": 402652118,
          "likes": 19283609,
          "comments": 10000000,
          "shares": null,
          "saves": null,
          "interactions": 29283609,
          "engagementRate": 0.0727
        }
      }
    ]
  },
  "analytics-post": {
    "platform": "youtube",
    "url": "https://www.youtube.com/watch?v=dQw4w9WgXcQ",
    "id": "dQw4w9WgXcQ",
    "title": "Rick Astley - Never Gonna Give You Up (Official Video) (4K Remaster)",
    "publishedAt": "2009-10-24T23:57:33-07:00",
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
      "likes": 19303349,
      "comments": 2400000,
      "shares": null,
      "saves": null,
      "interactions": 21703349,
      "engagementRate": 0.0121
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
      },
      {
        "platform": "bluesky",
        "uri": "at://did:plc:oky5czdrnfjpqslsw2a5iclo/app.bsky.feed.post/3mqunv4oepk2y",
        "url": "https://bsky.app/profile/jay.bsky.team/post/3mqunv4oepk2y",
        "cid": "bafyreic4yrxocxxcvnya2gchfhidq46do7reuxtwjekpnbfzrnljattu5m",
        "text": "once upon a time in the land of gnomes…",
        "publishedAt": "2026-07-17T21:08:43.276Z",
        "indexedAt": "2026-07-17T21:08:48.864Z",
        "author": {
          "handle": "jay.bsky.team",
          "displayName": "Jay 🦋",
          "did": "did:plc:oky5czdrnfjpqslsw2a5iclo",
          "avatar": "https://cdn.bsky.app/img/avatar/plain/did:plc:oky5czdrnfjpqslsw2a5iclo/bafkreihxtnc37g7jqdcgidtkknwuswtjiijcdnc6cx4imc4oq33cnsc5da"
        },
        "engagement": {
          "likes": 178,
          "reposts": 7,
          "replies": 17,
          "quotes": 2
        },
        "embed": {
          "type": "images",
          "images": [
            {
              "url": "https://cdn.bsky.app/img/feed_fullsize/plain/did:plc:oky5czdrnfjpqslsw2a5iclo/bafkreigdszebo7yhsvzp43vbtzr7hxq2iyw3dkdwg6hgeeewzkrvqs3y6i",
              "alt": "collectively written gnome story on typewriter"
            }
          ]
        }
      },
      {
        "platform": "bluesky",
        "uri": "at://did:plc:oky5czdrnfjpqslsw2a5iclo/app.bsky.feed.post/3mqcwx2ddok2r",
        "url": "https://bsky.app/profile/jay.bsky.team/post/3mqcwx2ddok2r",
        "cid": "bafyreifhr757k3xlszwuo7dihhpbporh42nrzwaiiywqn77n3h4ytnspma",
        "text": "I’m thrilled Toni is staying to lead us into this next chapter. He’s spent the past four months proving it, leading with curiosity and courage. Welcome (again) Toni!",
        "publishedAt": "2026-07-10T20:02:56.314Z",
        "indexedAt": "2026-07-10T20:02:56.964Z",
        "author": {
          "handle": "jay.bsky.team",
          "displayName": "Jay 🦋",
          "did": "did:plc:oky5czdrnfjpqslsw2a5iclo",
          "avatar": "https://cdn.bsky.app/img/avatar/plain/did:plc:oky5czdrnfjpqslsw2a5iclo/bafkreihxtnc37g7jqdcgidtkknwuswtjiijcdnc6cx4imc4oq33cnsc5da"
        },
        "engagement": {
          "likes": 335,
          "reposts": 23,
          "replies": 17,
          "quotes": 2
        },
        "embed": {
          "type": "app.bsky.embed.record#view"
        }
      },
      {
        "platform": "bluesky",
        "uri": "at://did:plc:oky5czdrnfjpqslsw2a5iclo/app.bsky.feed.post/3mp75kuens22h",
        "url": "https://bsky.app/profile/jay.bsky.team/post/3mp75kuens22h",
        "cid": "bafyreiheoivsjwscc5duma6373lcrwycerg4mzcjpvgopozhipayaib5qy",
        "text": "It really is. I hear Baltic reserve is a real thing, but the people I met were wonderfully warm and welcoming",
        "publishedAt": "2026-06-26T14:25:33.024Z",
        "indexedAt": "2026-06-26T14:25:34.266Z",
        "author": {
          "handle": "jay.bsky.team",
          "displayName": "Jay 🦋",
          "did": "did:plc:oky5czdrnfjpqslsw2a5iclo",
          "avatar": "https://cdn.bsky.app/img/avatar/plain/did:plc:oky5czdrnfjpqslsw2a5iclo/bafkreihxtnc37g7jqdcgidtkknwuswtjiijcdnc6cx4imc4oq33cnsc5da"
        },
        "engagement": {
          "likes": 13,
          "reposts": 0,
          "replies": 1,
          "quotes": 0
        },
        "embed": null
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
      },
      {
        "platform": "facebook_ad_library",
        "id": "629251157856827",
        "url": "https://www.facebook.com/ads/library/?id=629251157856827",
        "text": "Tune in here at 1:30pm PT to a Facebook Live discussion with Mark Zuckerberg, Dr. Priscilla Chan and Governor Gavin Newsom, where they will talk about California’s response to the COVID-19 outbreak.",
        "headline": "Live with California Governor, Gavin Newsom",
        "cta": null,
        "landingUrl": null,
        "adFormat": "VIDEO",
        "firstShown": "2020-03-30T07:00:00.000Z",
        "lastShown": "2020-04-02T07:00:00.000Z",
        "impressions": ">1M",
        "spend": "$700K - $800K",
        "country": "US",
        "advertiser": {
          "id": "108824017345866",
          "name": "Meta",
          "url": "https://www.facebook.com/Meta/",
          "logo": "https://scontent-atl3-3.xx.fbcdn.net/v/t1.6435-9/87284588_124830725745195_9124219877853233152_n.png?stp=dst-png_s60x60&_nc_cat=110&ccb=1-7&_nc_sid=c53f8f&_nc_ohc=DLCYhBDvg8wQ7kNvwGKpCeK&_nc_oc=AdqTTNAeb0KjgOR-sELgSafS1uCDI7jm58uEzI_ccHW_Vv7wb_6ctaBpXcL4ECBM9Mc&_nc_zt=23&_nc_ht=scontent-atl3-3.xx&_nc_gid=SxD9styajND2_8-5Hiv5XQ&_nc_ss=72289&oh=00_AQCT690005DnAkhA-AeoJVLlwyEYFb-3e-9dVsCLPcYB5w&oe=6A892BC3"
        },
        "media": [
          "https://scontent-atl3-2.xx.fbcdn.net/v/t39.35426-6/122500852_364361851568920_5617757942998938181_n.jpg?_nc_cat=104&ccb=1-7&_nc_sid=c53f8f&_nc_ohc=pm7Q4VB48VwQ7kNvwG9vHzb&_nc_oc=AdpNy95zoqLhPKJekY8d2_cTdICH5kgFM8aqlhk5Ltz3J2JkhM5xQ9zizbmkWeI3QAM&_nc_zt=14&_nc_ht=scontent-atl3-2.xx&_nc_gid=SxD9styajND2_8-5Hiv5XQ&_nc_ss=72289&oh=00_AQDVoxPlWOkQmNjXV9vbz-k3WFO5s2ugyaq1EcBSpJZi1A&oe=6A6796D8"
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
          "logo": "https://scontent-atl3-1.xx.fbcdn.net/v/t1.6435-9/119568341_200337161527884_7846459746434232698_n.png?stp=dst-png_s60x60&_nc_cat=100&ccb=1-7&_nc_sid=c53f8f&_nc_ohc=qaRlosGC9wUQ7kNvwH_c6S1&_nc_oc=Adq6Kf5L_Tkx2E3_ZTPgkkJBqBFrUF2yFzbizYtSLVcyom-ZAmB0zM6FgNhqa6CE4bQ&_nc_zt=23&_nc_ht=scontent-atl3-1.xx&_nc_gid=SxD9styajND2_8-5Hiv5XQ&_nc_ss=72289&oh=00_AQB38PZJl2olGB2U4-yzTIbucPjM7a_5C-sAcPDMbf_TKA&oe=6A89438E"
        },
        "media": [
          "https://video-atl3-1.xx.fbcdn.net/o1/v/t2/f2/m412/AQPYrtdWcXYzwK9kZxgDiAgoU_IImyeS9Q8adbGcircR7RR1dDdUBrAQ0LiHO2OJoauE5pf8F4GyEcPVDLQ94uo.mp4?_nc_cat=100&_nc_sid=ef5aa3&_nc_ht=video-atl3-1.xx.fbcdn.net&_nc_ohc=TJVBi21FSYoQ7kNvwHRm88L&efg=eyJ2ZW5jb2RlX3RhZyI6Inhwdl9wcm9ncmVzc2l2ZS5WSV9VU0VDQVNFX1BST0RVQ1RfVFlQRS4uQzMuMzQwLmFzaWNfaHExX3NkX3Byb2dyZXNzaXZlIiwieHB2X2Fzc2V0X2lkIjo4OTE2MjkwMDA0NTQwNDEsImFzc2V0X2FnZV9kYXlzIjoxNTcsInZpX3VzZWNhc2VfaWQiOjEwNjgwLCJkdXJhdGlvbl9zIjoxNCwidXJsZ2VuX3NvdXJjZSI6Ind3dyJ9&ccb=17-1&_nc_gid=SxD9styajND2_8-5Hiv5XQ&_nc_ss=72289&_nc_zt=28&oh=00_AQCLyxYoox1xemvUeI90AbxJ8kemKuquBtAnyxKy227kcA&oe=6A678682",
          "https://scontent-atl3-1.xx.fbcdn.net/v/t39.35426-6/120439450_1980569842077757_2547343747583380554_n.jpg?_nc_cat=100&ccb=1-7&_nc_sid=c53f8f&_nc_ohc=ghBwQrPN7IYQ7kNvwFk7y92&_nc_oc=AdoxOVy424HY2clI0huJHzMUy0ttXPlLXz4ukfQ9jlfbJpaFpvZ94fEGgw_5sU2S5N4&_nc_zt=14&_nc_ht=scontent-atl3-1.xx&_nc_gid=SxD9styajND2_8-5Hiv5XQ&_nc_ss=72289&oh=00_AQBpi4Ex6cD2sbwj411KBUG_ducK8rDg9VU2aCRBAUaMig&oe=6A678BF4"
        ]
      },
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
          "logo": "https://scontent-atl3-1.xx.fbcdn.net/v/t1.6435-9/119568341_200337161527884_7846459746434232698_n.png?stp=dst-png_s60x60&_nc_cat=100&ccb=1-7&_nc_sid=c53f8f&_nc_ohc=qaRlosGC9wUQ7kNvwH_c6S1&_nc_oc=Adq6Kf5L_Tkx2E3_ZTPgkkJBqBFrUF2yFzbizYtSLVcyom-ZAmB0zM6FgNhqa6CE4bQ&_nc_zt=23&_nc_ht=scontent-atl3-1.xx&_nc_gid=SxD9styajND2_8-5Hiv5XQ&_nc_ss=72289&oh=00_AQB38PZJl2olGB2U4-yzTIbucPjM7a_5C-sAcPDMbf_TKA&oe=6A89438E"
        },
        "media": [
          "https://video-atl3-1.xx.fbcdn.net/o1/v/t2/f2/m412/AQNN757NtitUcJnpv0ODeMH6fXo-yFM-X90P2W82Zsrc70oOzST9lrKgscKf21SHBUtZ9pdKMclY8s32B0eRJ7o.mp4?_nc_cat=106&_nc_sid=ef5aa3&_nc_ht=video-atl3-1.xx.fbcdn.net&_nc_ohc=VIhm6QH6QpYQ7kNvwEHI2aO&efg=eyJ2ZW5jb2RlX3RhZyI6Inhwdl9wcm9ncmVzc2l2ZS5WSV9VU0VDQVNFX1BST0RVQ1RfVFlQRS4uQzMuMzQwLmFzaWNfaHExX3NkX3Byb2dyZXNzaXZlIiwieHB2X2Fzc2V0X2lkIjo4MzE0MTAwMzMxNDk2MzYsImFzc2V0X2FnZV9kYXlzIjoyMzcsInZpX3VzZWNhc2VfaWQiOjEwNjgwLCJkdXJhdGlvbl9zIjoxNSwidXJsZ2VuX3NvdXJjZSI6Ind3dyJ9&ccb=17-1&_nc_gid=SxD9styajND2_8-5Hiv5XQ&_nc_ss=72289&_nc_zt=28&oh=00_AQAUb2ZdeD0DLfCJeJpBm16sng8aprWDv3yFHJOCy43t1w&oe=6A677448",
          "https://scontent-atl3-2.xx.fbcdn.net/v/t39.35426-6/120065387_2711663819108220_8472417301728012411_n.jpg?_nc_cat=105&ccb=1-7&_nc_sid=c53f8f&_nc_ohc=XJsOGtccv7UQ7kNvwHTw_Vt&_nc_oc=AdrFXP-r_O9o2rS9rG1ysBygItOayq2_Cj4bMsCHZADpFaGsNTmj6Lf8bw32HDPoBGw&_nc_zt=14&_nc_ht=scontent-atl3-2.xx&_nc_gid=SxD9styajND2_8-5Hiv5XQ&_nc_ss=72289&oh=00_AQDAy1RxUJJMdmYVDPqFU-sRrmeavgHD8krZun6tp5dxQg&oe=6A67964A"
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
      },
      {
        "platform": "facebook_ad_library",
        "id": "352695862528588",
        "url": "https://www.facebook.com/ads/library/?id=352695862528588",
        "text": "Queen Latifah hosts a series of candid conversations honoring the 57th anniversary of the #MarchOnWashington and this new era of the civil rights movement. Change Together features notable civil rights leaders such as Patrisse Cullors, Reverend Al Sharpton, and Kendrick Sampson, as well as social justice advocates Amanda Seales, Common and musical guest, CHIKA. Let’s come together to #LiftBlackVoices, learn and move as one toward equality and freedom.",
        "headline": "Change Together: From the March on Washington to Today",
        "cta": null,
        "landingUrl": null,
        "adFormat": "VIDEO",
        "firstShown": "2020-08-27T07:00:00.000Z",
        "lastShown": "2020-08-30T07:00:00.000Z",
        "impressions": ">1M",
        "spend": ">$1M",
        "country": "US",
        "advertiser": {
          "id": "20531316728",
          "name": "Facebook",
          "url": "https://www.facebook.com/facebook/",
          "logo": "https://scontent-atl3-3.xx.fbcdn.net/v/t39.35426-6/123254501_376431443560946_8642123156381274111_n.jpg?stp=dst-jpg_s60x60_tt6&_nc_cat=108&ccb=1-7&_nc_sid=c53f8f&_nc_ohc=uPcoVSVedoQQ7kNvwHgmWWe&_nc_oc=AdqwXTjc5hWqxKmTPliHRnVkbtl62MNcyuFRVtYt5e11rm_kKl_7cbhn2U6FxOqfz_4&_nc_zt=14&_nc_ht=scontent-atl3-3.xx&_nc_gid=kjSzmNhJvOQPmxnVKKr0xg&_nc_ss=72289&oh=00_AQAwgOXSH-Za4uSlnK2E_DN8SP8iELP-mBG2Fa6sq_k6fA&oe=6A678FB0"
        },
        "media": [
          "https://video-atl3-3.xx.fbcdn.net/o1/v/t2/f2/m412/AQOhKuKthAVVa0rFEi41ggsiGpIjueM36xj6WP_vqqtBOe-ys_sa5nUBYG9fKBArU14yCLHp-zR-F0aBPcYRtpg.mp4?_nc_cat=107&_nc_sid=ef5aa3&_nc_ht=video-atl3-3.xx.fbcdn.net&_nc_ohc=_t6jTcvDRokQ7kNvwGEF3JZ&efg=eyJ2ZW5jb2RlX3RhZyI6Inhwdl9wcm9ncmVzc2l2ZS5WSV9VU0VDQVNFX1BST0RVQ1RfVFlQRS4uQzMuNDAwLmFzaWNfaHExX3NkX3Byb2dyZXNzaXZlIiwieHB2X2Fzc2V0X2lkIjoxMDUzMzI1NDAzNjA2NjM5LCJhc3NldF9hZ2VfZGF5cyI6Mzg1LCJ2aV91c2VjYXNlX2lkIjoxMDY4MCwiZHVyYXRpb25fcyI6MzY5OSwidXJsZ2VuX3NvdXJjZSI6Ind3dyJ9&ccb=17-1&_nc_gid=kjSzmNhJvOQPmxnVKKr0xg&_nc_ss=72289&_nc_zt=28&oh=00_AQB-yxRDZCNErGWI1fXJCz3c7uPPshjVivWZcuMY_fXKRg&oe=6A6795FF",
          "https://scontent-atl3-3.xx.fbcdn.net/v/t39.35426-6/123131854_3586232378268717_4745383357747290556_n.jpg?_nc_cat=109&ccb=1-7&_nc_sid=c53f8f&_nc_ohc=CBujsK3_RAYQ7kNvwGLIslX&_nc_oc=AdqugE8L4r1IjoIQfZPloPL5zYCw9T2PvW36W--FM6EwKE0s97CMYl5vHS5uvgucOB8&_nc_zt=14&_nc_ht=scontent-atl3-3.xx&_nc_gid=kjSzmNhJvOQPmxnVKKr0xg&_nc_ss=72289&oh=00_AQCdtQbYirMkwB6MPN1xoagoP9ljGYKRFTeMNVXwrXJFng&oe=6A678230"
        ]
      },
      {
        "platform": "facebook_ad_library",
        "id": "661142788113430",
        "url": "https://www.facebook.com/ads/library/?id=661142788113430",
        "text": "Get ready to vote and make your voice heard! Liza Koshy hosts Will Smith, Matthew McConaughey, Alicia Keys and more in Vote-A-Thon 2020, a #NationalVoterRegistrationDay celebration. \n\nFor information from election authorities, visit fb.com/votinginfocenter #Vote2020",
        "headline": "Vote-A-Thon 2020: Get Ready to Vote!",
        "cta": null,
        "landingUrl": null,
        "adFormat": "VIDEO",
        "firstShown": "2020-09-23T07:00:00.000Z",
        "lastShown": "2020-09-29T07:00:00.000Z",
        "impressions": ">1M",
        "spend": "$600K - $700K",
        "country": "US",
        "advertiser": {
          "id": "20531316728",
          "name": "Facebook App",
          "url": "https://www.facebook.com/facebook/",
          "logo": "https://scontent-atl3-1.xx.fbcdn.net/v/t1.6435-9/58818464_10158354585756729_7126855515920924672_n.png?stp=dst-png_s60x60&_nc_cat=100&ccb=1-7&_nc_sid=c53f8f&_nc_ohc=cYlKOt4-GcUQ7kNvwEj2rPB&_nc_oc=AdoHGqorRQuAh1NodHbHYx2T0SKwlVlZZE9WmznEqmn2uvvLFB0aMuR8fLJef7D2itA&_nc_zt=23&_nc_ht=scontent-atl3-1.xx&_nc_gid=kjSzmNhJvOQPmxnVKKr0xg&_nc_ss=72289&oh=00_AQDFaJlAcj-4tia3IQ417oX2bxs7hepULywCIcQUtORkmQ&oe=6A893E2F"
        },
        "media": [
          "https://video-atl3-2.xx.fbcdn.net/o1/v/t2/f2/m560/AQPTgFuknRcBF4Lc_DtMcH-qlZGFfCQi83pEJd1S2Rx7uirTcJhniVVQrX29KTbwpbmeEofg6qllV-Nw4oOwynbGFVZfEUoYqWo.mp4?_nc_cat=104&_nc_sid=ef5aa3&_nc_ht=video-atl3-2.xx.fbcdn.net&_nc_ohc=LAgfvy6KENoQ7kNvwG84FTD&efg=eyJ2ZW5jb2RlX3RhZyI6Inhwdl9wcm9ncmVzc2l2ZS5WSV9VU0VDQVNFX1BST0RVQ1RfVFlQRS4uQzMuNDI0LmFzaWNfaHExX3NkX3Byb2dyZXNzaXZlIiwieHB2X2Fzc2V0X2lkIjo5ODIzODk2MDc3OTIzNDQsImFzc2V0X2FnZV9kYXlzIjo5NiwidmlfdXNlY2FzZV9pZCI6MTA2ODAsImR1cmF0aW9uX3MiOjE5MzAsInVybGdlbl9zb3VyY2UiOiJ3d3cifQ%3D%3D&ccb=17-1&_nc_gid=kjSzmNhJvOQPmxnVKKr0xg&_nc_ss=72289&_nc_zt=28&oh=00_AQBP9B0O5L1XPrYbIA2nQ2YSQw58tY1oD2VaGk-pgOling&oe=6A63B26A",
          "https://scontent-atl3-1.xx.fbcdn.net/v/t39.35426-6/125381272_280240523411642_8369623856772259236_n.jpg?_nc_cat=103&ccb=1-7&_nc_sid=c53f8f&_nc_ohc=XyRK_lkth9MQ7kNvwGlTTfu&_nc_oc=AdpyKVXDhj9Y251dtE2MPybdoOcTQgK5aQOVfVoqrYjtlDDpADiKgCuUxnHKDgfCHj4&_nc_zt=14&_nc_ht=scontent-atl3-1.xx&_nc_gid=kjSzmNhJvOQPmxnVKKr0xg&_nc_ss=72289&oh=00_AQAo0Nzhu6femzVim7KW66JDEQAcuBXpTFdCPmF5uUi0RQ&oe=6A677FEC"
        ]
      },
      {
        "platform": "facebook_ad_library",
        "id": "475114446742483",
        "url": "https://www.facebook.com/ads/library/?id=475114446742483",
        "text": "Have you reviewed your ballot? Get to know what's on your ballot before Election Day through the Voting Information Center.",
        "headline": "Double-Check Your Ballot",
        "cta": "Learn more",
        "landingUrl": "http://facebook.com/votinginfocenter/ballot?entry_point=Qmx1ZV9PTlA=",
        "adFormat": "VIDEO",
        "firstShown": "2020-10-23T07:00:00.000Z",
        "lastShown": "2020-11-03T08:00:00.000Z",
        "impressions": ">1M",
        "spend": "$600K - $700K",
        "country": "US",
        "advertiser": {
          "id": "20531316728",
          "name": "Facebook App",
          "url": "https://www.facebook.com/facebook/",
          "logo": "https://scontent-atl3-1.xx.fbcdn.net/v/t1.6435-9/58818464_10158354585756729_7126855515920924672_n.png?stp=dst-png_s60x60&_nc_cat=100&ccb=1-7&_nc_sid=c53f8f&_nc_ohc=cYlKOt4-GcUQ7kNvwEj2rPB&_nc_oc=AdoHGqorRQuAh1NodHbHYx2T0SKwlVlZZE9WmznEqmn2uvvLFB0aMuR8fLJef7D2itA&_nc_zt=23&_nc_ht=scontent-atl3-1.xx&_nc_gid=kjSzmNhJvOQPmxnVKKr0xg&_nc_ss=72289&oh=00_AQDFaJlAcj-4tia3IQ417oX2bxs7hepULywCIcQUtORkmQ&oe=6A893E2F"
        },
        "media": [
          "https://video-atl3-1.xx.fbcdn.net/o1/v/t2/f2/m412/AQODMEZl7iplcGXJPBxXGuuh-WjlAPqsPLHH9EB0i7PARypul43ZBvenVloxoYkD-IUaEdBSmyDbTc5-kHBNxECY.mp4?_nc_cat=103&_nc_sid=ef5aa3&_nc_ht=video-atl3-1.xx.fbcdn.net&_nc_ohc=aQxYnWw9DrwQ7kNvwFxGOa7&efg=eyJ2ZW5jb2RlX3RhZyI6Inhwdl9wcm9ncmVzc2l2ZS5WSV9VU0VDQVNFX1BST0RVQ1RfVFlQRS4uQzMuMzQwLmFzaWNfaHExX3NkX3Byb2dyZXNzaXZlIiwieHB2X2Fzc2V0X2lkIjozNjE0ODg2NTI1MzE5NjczLCJhc3NldF9hZ2VfZGF5cyI6MjQwLCJ2aV91c2VjYXNlX2lkIjoxMDY4MCwiZHVyYXRpb25fcyI6MTUsInVybGdlbl9zb3VyY2UiOiJ3d3cifQ%3D%3D&ccb=17-1&_nc_gid=kjSzmNhJvOQPmxnVKKr0xg&_nc_ss=72289&_nc_zt=28&oh=00_AQDqlY-6Yt6F59kxtTMPrLsinAzaSpmAW9wChSkDXKdL_w&oe=6A67715C",
          "https://scontent-atl3-3.xx.fbcdn.net/v/t39.35426-6/122569736_390651732307808_5011321040623151549_n.jpg?_nc_cat=108&ccb=1-7&_nc_sid=c53f8f&_nc_ohc=s0Jpfvn4SlgQ7kNvwFI6q5l&_nc_oc=Adq5xXs14dBn6M1y89p-mhFN_7LDpRUUYu4kxAyvKoR9GkLwN7rCAW9i2mxTNW3UcqE&_nc_zt=14&_nc_ht=scontent-atl3-3.xx&_nc_gid=kjSzmNhJvOQPmxnVKKr0xg&_nc_ss=72289&oh=00_AQAgInYoqIeK9Jq1kfsK47MfkfCHaI7EtgSg_lCE8MlVuQ&oe=6A6773AC"
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
      },
      {
        "id": "721404351056614",
        "name": "IControl: Easy Widgets Themes",
        "url": "https://www.facebook.com/61578892468353/",
        "logo": "https://scontent-iad6-1.xx.fbcdn.net/v/t39.35426-6/695177587_1511487320476777_920753808075681498_n.jpg?stp=dst-jpg_s60x60_tt6&_nc_cat=100&ccb=1-7&_nc_sid=c53f8f&_nc_ohc=ymXmwsmzZqIQ7kNvwE2kif9&_nc_oc=AdrjQG4Qk6k7RYor663OBc3KYDml9EWij735hvCXNqbLvnje1pwp4JEzlGGYcxOAigU&_nc_zt=14&_nc_ht=scontent-iad6-1.xx&_nc_gid=WFVhUXC3vFhp5HqXMO2_vg&_nc_ss=72289&oh=00_AQBS8dexsIwImNwFM5phyZrj9jrF4PSW61cknXtjYUI1IA&oe=6A612EE7"
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
        "author": "Jack Ryan Miller",
        "authorAvatarUrl": "https://scontent.fsgn24-1.fna.fbcdn.net/v/t39.30808-1/692472460_26663220403348161_6124206666765972294_n.jpg?stp=cp0_dst-jpg_tt6&cstp=mx960x960&ctp=s32x32&_nc_cat=102&ccb=1-7&_nc_sid=e99d92&_nc_ohc=3HNDMjGZhBIQ7kNvwH_Yi6V&_nc_oc=AdoxMiMSoY_ToCduVunc3YCOZtk_SXSgox578bFFqLiP_4rQwkwI465-N_iYgGAJFKc&_nc_zt=24&_nc_ht=scontent.fsgn24-1.fna&_nc_gid=HH_crC25V3cxSQmbs1qi6w&_nc_ss=7b289&oh=00_AQDnijJpCb3QQr1TMy3wnG3ZpT2laUi0wvxSIlu-E9nHXw&oe=6A6C3A29",
        "likeCount": 7,
        "publishedAt": "2026-06-02T19:30:33+00:00",
        "replyCount": 6
      },
      {
        "id": "1565653145168639",
        "url": "https://www.facebook.com/NASA/posts/pfbid0ozvoLoowKvCysA2CZkXKTAVCRLoVECcrC7W8eQbQYvxBNKMCQAzV8baSgDa8t5Hol?comment_id=1565653145168639",
        "text": "You had me at Roman",
        "author": "Mike Harwick",
        "authorAvatarUrl": "https://scontent.fsgn13-1.fna.fbcdn.net/v/t39.30808-1/708345356_26903531449306692_9193818255719987217_n.jpg?stp=cp0_dst-jpg_tt6&cstp=mx960x960&ctp=s32x32&_nc_cat=100&ccb=1-7&_nc_sid=e99d92&_nc_ohc=TzWa-f368dwQ7kNvwEMPaUV&_nc_oc=AdpdLHrvXy7m167xxHhinaiUIlBoo2jzN-yKoz2hmtKPDhZMy8t4wFudGRE1dEwFuas&_nc_zt=24&_nc_ht=scontent.fsgn13-1.fna&_nc_gid=HH_crC25V3cxSQmbs1qi6w&_nc_ss=7b289&oh=00_AQCw8rv9R1a-kXHBcH09C7AdRzTbIlhxf4mps8XzaYwIlQ&oe=6A6C1254",
        "likeCount": 3,
        "publishedAt": "2026-06-03T12:30:24+00:00",
        "replyCount": 0
      },
      {
        "id": "3207368056140091",
        "url": "https://www.facebook.com/NASA/posts/pfbid0ozvoLoowKvCysA2CZkXKTAVCRLoVECcrC7W8eQbQYvxBNKMCQAzV8baSgDa8t5Hol?comment_id=3207368056140091",
        "text": "This is the era of space initiatives. 👏",
        "author": "Megan Kelly",
        "authorAvatarUrl": "https://scontent.fsgn13-2.fna.fbcdn.net/v/t39.30808-1/699650025_27974478592140854_2536163107065285396_n.jpg?stp=cp0_dst-jpg_tt6&cstp=mx1536x1539&ctp=s32x32&_nc_cat=108&ccb=1-7&_nc_sid=e99d92&_nc_ohc=DLdsVhSx314Q7kNvwFPFx_P&_nc_oc=AdoywI2Pu2eRocI1x08wKLm5TPLL1p0dcZv2yCYoyXem_bje8s-ShUWiB9XjGXJ4DjY&_nc_zt=24&_nc_ht=scontent.fsgn13-2.fna&_nc_gid=HH_crC25V3cxSQmbs1qi6w&_nc_ss=7b289&oh=00_AQAx63COUzJwva3qfF26jgiDtZQTS3ztq6nx5_jg4waN-Q&oe=6A6C0909",
        "likeCount": 4,
        "publishedAt": "2026-06-03T13:15:11+00:00",
        "replyCount": 0
      },
      {
        "id": "2545567982564356",
        "url": "https://www.facebook.com/NASA/posts/pfbid0ozvoLoowKvCysA2CZkXKTAVCRLoVECcrC7W8eQbQYvxBNKMCQAzV8baSgDa8t5Hol?comment_id=2545567982564356",
        "text": "For those confused about whom this was named after. Nancy Grace Roman (May 16, 1925 – December 25, 2018) was an American astronomer who made important contributions to stellar classification and stellar motions. The first female executive at NASA, Roman served as NASA's first Chief of Astronomy throughout the 1960s and 1970s, establishing her as one of the \"visionary founders of the US civilian space program\"",
        "author": "Michael Johnson",
        "authorAvatarUrl": "https://scontent.fsgn4-1.fna.fbcdn.net/v/t39.30808-1/715464960_1534487678342523_3205477696229619791_n.jpg?stp=cp0_dst-jpg_tt6&cstp=mx1200x1200&ctp=s32x32&_nc_cat=101&ccb=1-7&_nc_sid=e99d92&_nc_ohc=CJj1uW-M8GwQ7kNvwEtSEkj&_nc_oc=AdqxXLSgPh7vA23eS3lVfR0fcPu5vszVJRfA1BgRw1bFuOuA89aeo3wyIsF17qX4b3g&_nc_zt=24&_nc_ht=scontent.fsgn4-1.fna&_nc_gid=HH_crC25V3cxSQmbs1qi6w&_nc_ss=7b289&oh=00_AQCKv92W24kCoyyAyQ5pt-ZgDDeNu4IqJ9g6RbFvJd9qfQ&oe=6A6C180B",
        "likeCount": 5,
        "publishedAt": "2026-06-05T19:10:38+00:00",
        "replyCount": 0
      },
      {
        "id": "1009195248315125",
        "url": "https://www.facebook.com/NASA/posts/pfbid0ozvoLoowKvCysA2CZkXKTAVCRLoVECcrC7W8eQbQYvxBNKMCQAzV8baSgDa8t5Hol?comment_id=1009195248315125",
        "text": "Anxious to see what the new scope sees.",
        "author": "Richard Alexandrowich",
        "authorUrl": "https://www.facebook.com/richard.alexandrowich.1",
        "authorAvatarUrl": "https://scontent.fsgn13-1.fna.fbcdn.net/v/t39.30808-1/449687176_1970527473417419_1705720154636413099_n.jpg?stp=cp0_dst-jpg_tt6&cstp=mx960x957&ctp=s32x32&_nc_cat=100&ccb=1-7&_nc_sid=e99d92&_nc_ohc=bCu8aO2reIoQ7kNvwHtIyP4&_nc_oc=Ado8EmORytYJyvsPBBz8rKe1pliFYfaZhRWBiXTfIt1RBjFh-vpPtTWvhICw9rQTuUg&_nc_zt=24&_nc_ht=scontent.fsgn13-1.fna&_nc_gid=HH_crC25V3cxSQmbs1qi6w&_nc_ss=7b289&oh=00_AQBA1O-NdA_rsrXqOjaw5n4Nvuuk27jRjIyAC9M0AgwvyQ&oe=6A6C31C4",
        "likeCount": 3,
        "publishedAt": "2026-06-03T02:04:15+00:00",
        "replyCount": 7
      }
    ]
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
    "startDate": "2026-08-20T00:00:00+00:00",
    "startTime": "Wednesday, August 19, 2026 at 7:00 PM – 8:30 PM CDT",
    "duration": null,
    "eventType": null,
    "isOnline": false,
    "isPast": null,
    "isCanceled": false,
    "address": "Rosemont",
    "image": "https://scontent-iad3-1.xx.fbcdn.net/v/t39.30808-6/729939829_1455156393312553_7424802617478099383_n.jpg?stp=dst-jpg_tt6&cstp=mx1200x628&ctp=s960x960&_nc_cat=108&ccb=1-7&_nc_sid=75d36f&_nc_ohc=NbH0PON4qgEQ7kNvwFpe5NR&_nc_oc=Adq5ueEQtrEOiuAgFzOO0Af3DxO_gOQ9fm_C3askwZrW4mBPiabjqlDsciP5zxSWkxE&_nc_zt=23&_nc_ht=scontent-iad3-1.xx&_nc_gid=uzyVymY6OIZIjd0SLNBHbw&_nc_ss=73289&oh=00_AQB9zBIyvpIeNL7Q6dm6HB53eQMi0VaaM9zGnnCw3Eqyvg&oe=6A62C921",
    "usersGoing": null,
    "usersInterested": null,
    "usersResponded": 3,
    "location": {
      "name": "5437 Park Place, Rosemont, IL, United States, Illinois 60018",
      "city": "Rosemont, IL",
      "latitude": 41.97826,
      "longitude": -87.86738,
      "countryCode": "US"
    },
    "organizer": "Zanies Rosemont Comedy Club",
    "organizers": [
      {
        "id": null,
        "name": "Zanies Rosemont Comedy Club",
        "url": "https://www.facebook.com/RosemontZanies",
        "verified": false
      }
    ],
    "ticketsUrl": "https://www.etix.com/ticket/p/74170542/the-best-of-chicago-showcase-rosemont-zanies-rosemont",
    "categories": [
      {
        "label": "Comedy",
        "url": null
      }
    ],
    "externalLinks": []
  },
  "facebook-event-search": {
    "query": "comedy Chicago",
    "totalReturned": 5,
    "events": [
      {
        "platform": "facebook",
        "id": "1032731593052809",
        "url": "https://www.facebook.com/events/1032731593052809/",
        "name": "Worship 7/26/26",
        "startDate": "2026-07-26T15:00:00Z",
        "startTime": "Happening now",
        "eventType": "PUBLIC_TYPE",
        "isOnline": true,
        "isPast": false,
        "image": "https://scontent-ord5-1.xx.fbcdn.net/v/t39.30808-6/729784843_1477362577754903_401694802381250350_n.jpg?stp=c0.47.1640.782a_dst-jpg_tt6&cstp=mx1640x782&ctp=s320x320&_nc_cat=101&ccb=1-7&_nc_sid=75d36f&_nc_ohc=6svKiDO2hVoQ7kNvwHjAlFx&_nc_oc=Adrs2rdq3CgIbPLXRlU5a0xVHUuey7lwAVdgpSxj7-fa3XGPZsdFBnUw7t8dgFeQLzo&_nc_zt=23&_nc_ht=scontent-ord5-1.xx&_nc_gid=ZJcMLEDMfuHRFLFJrYmanw&_nc_ss=7b289&oh=00_AQCUn-lzpgnqH0uhjhE6MWQWKlFJn71UKBsSHV-Uo_oxzw&oe=6A6BEE8A",
        "usersGoing": 3,
        "usersInterested": 1
      },
      {
        "platform": "facebook",
        "id": "1020197857054108",
        "url": "https://www.facebook.com/events/1020197857054108/",
        "name": "In-Person and Online Worship Experience",
        "startDate": "2026-07-26T16:00:00Z",
        "startTime": "Sun, Jul 26 at 11:00 AM CDT",
        "eventType": "PUBLIC_TYPE",
        "isOnline": true,
        "isPast": false,
        "image": "https://scontent-ord5-3.xx.fbcdn.net/v/t39.30808-6/744332103_1423888923105270_3051096675327242426_n.jpg?stp=c0.19.1200.573a_dst-jpg_tt6&cstp=mx1200x573&ctp=s320x320&_nc_cat=109&ccb=1-7&_nc_sid=75d36f&_nc_ohc=yib12OViOYUQ7kNvwE_daPf&_nc_oc=AdobfdQpY8SDFjT_xffOD9zJrsspqBb4B3Zycu79SvflFYdBXd_TpK-XKLASAXhgncM&_nc_zt=23&_nc_ht=scontent-ord5-3.xx&_nc_gid=ZJcMLEDMfuHRFLFJrYmanw&_nc_ss=7b289&oh=00_AQCpkrtpEZGrupU8PePBJk5UM-MlMsiV0T956Jq0JAmViA&oe=6A6C0BDE",
        "usersGoing": 1,
        "usersInterested": 1
      },
      {
        "platform": "facebook",
        "id": "1411120507064710",
        "url": "https://www.facebook.com/events/1411120507064710/",
        "name": "Sanjeevani4U Monthly Support Group",
        "startDate": "2026-07-26T20:30:00Z",
        "startTime": "Sun, Jul 26 at 3:30 PM CDT",
        "eventType": "PUBLIC_TYPE",
        "isOnline": true,
        "isPast": false,
        "image": "https://scontent-ord5-1.xx.fbcdn.net/v/t39.30808-6/613646701_1298582932295083_3210622313165210617_n.jpg?stp=c0.346.1024.488a_dst-jpg_tt6&cstp=mx1024x488&ctp=s320x320&_nc_cat=101&ccb=1-7&_nc_sid=75d36f&_nc_ohc=lwwuvCXsIw4Q7kNvwFMpt-c&_nc_oc=AdrRTviYP5UFmTyuWzFJZLH1ak6ofRtzwqOFOuG8gd-lsL-yslvJuSX7cUKqSKAYFuA&_nc_zt=23&_nc_ht=scontent-ord5-1.xx&_nc_gid=ZJcMLEDMfuHRFLFJrYmanw&_nc_ss=7b289&oh=00_AQCBrwR61TAz3t76nzzrYrX7s-IY5O2rfsoqBdftoIwt_A&oe=6A6C01E6",
        "usersGoing": 1
      },
      {
        "platform": "facebook",
        "id": "1552110089604110",
        "url": "https://www.facebook.com/events/1552110089604110/",
        "name": "The Big Picture of the Bible",
        "startDate": "2026-07-28T00:45:00Z",
        "startTime": "Mon, Jul 27 at 7:45 PM CDT",
        "eventType": "PUBLIC_TYPE",
        "isOnline": true,
        "isPast": false,
        "image": "https://scontent-ord5-3.xx.fbcdn.net/v/t39.30808-6/723103611_1437329531770331_3863440088136803669_n.jpg?stp=c0.275.1080.516a_dst-jpg_tt6&cstp=mx1080x516&ctp=s320x320&_nc_cat=107&ccb=1-7&_nc_sid=75d36f&_nc_ohc=qi1dWulJN-QQ7kNvwGdr1lG&_nc_oc=Adpno_IqyRgRAlG3Z_Vfr1ul5XSlJdB1QrOjGKeBBwzYjz1oVZ5D4dS7sGlh-wdp23k&_nc_zt=23&_nc_ht=scontent-ord5-3.xx&_nc_gid=ZJcMLEDMfuHRFLFJrYmanw&_nc_ss=7b289&oh=00_AQDroLHQxAlYptc7KJaSOkLp9E3J3aGMZv5JD9viL4DmaA&oe=6A6BF0D4",
        "usersGoing": 1,
        "usersInterested": 2
      },
      {
        "platform": "facebook",
        "id": "2448238608938396",
        "url": "https://www.facebook.com/events/2448238608938396/",
        "name": "Virtual 8 Week Tarot Class - A Fool's Journey",
        "startDate": "2026-07-30T00:00:00Z",
        "startTime": "Wed, Jul 29 at 7:00 PM CDT",
        "eventType": "PUBLIC_TYPE",
        "isOnline": true,
        "isPast": false,
        "image": "https://scontent-ord5-1.xx.fbcdn.net/v/t39.30808-6/700483218_122234764490315776_10588253747618528_n.jpg?stp=c0.177.1024.488a_dst-jpg_tt6&cstp=mx1024x488&ctp=s320x320&_nc_cat=106&ccb=1-7&_nc_sid=75d36f&_nc_ohc=LCRzJKfWiKsQ7kNvwFgKR6w&_nc_oc=Adr0yn7Dhw7TfiWnVXaiYKjY79rqYJ7O0ci5ovVd8gxV0JLjAWxLsc5d_elJVsJ9zKk&_nc_zt=23&_nc_ht=scontent-ord5-1.xx&_nc_gid=ZJcMLEDMfuHRFLFJrYmanw&_nc_ss=7b289&oh=00_AQD5PDmVcflFNfOcCytfj6iAK7Q2t_Ol4M2xCzz26mezCg&oe=6A6C025D",
        "usersGoing": 1
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
          "comments": 0,
          "shares": 0
        },
        "isVideo": false
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
          "username": "dogspotting",
          "displayName": "Chet Rhodes"
        },
        "engagement": {
          "likes": 36,
          "comments": 2,
          "shares": 0
        },
        "isVideo": false
      },
      {
        "platform": "facebook",
        "url": "https://www.facebook.com/groups/dogspotting/posts/10165912136809467/",
        "id": "10165912136809467",
        "caption": "🥹",
        "description": "🥹",
        "publishedAt": "2026-07-24T15:45:47.000Z",
        "thumbnailUrl": "https://scontent-iad3-1.xx.fbcdn.net/v/t39.30808-6/753343843_27704228762540395_7618880549288864734_n.jpg?stp=cp6_dst-jpg_tt6&cstp=mx1536x2048&ctp=p526x296&_nc_cat=108&ccb=1-7&_nc_s...",
        "author": {
          "username": "dogspotting",
          "displayName": "Dóra Almási"
        },
        "engagement": {
          "likes": 182,
          "comments": 2,
          "shares": 0
        },
        "isVideo": false
      },
      {
        "platform": "facebook",
        "url": "https://www.facebook.com/groups/dogspotting/posts/10165911376684467/",
        "id": "10165911376684467",
        "caption": "Konbini (7/11) doggo! 🐕",
        "description": "Konbini (7/11) doggo! 🐕",
        "publishedAt": "2026-07-24T11:52:33.000Z",
        "thumbnailUrl": "https://scontent-lga3-2.xx.fbcdn.net/v/t39.30808-6/753702691_963642156683059_393037493943314975_n.jpg?stp=dst-jpg_tt6&cstp=mx750x1334&ctp=p526x296&_nc_cat=100&ccb=1-7&_nc_sid=aa7b4...",
        "author": {
          "username": "dogspotting",
          "displayName": "Adam Steele",
          "url": "https://www.facebook.com/100091118505588"
        },
        "engagement": {
          "likes": 115,
          "comments": 2,
          "shares": 0
        },
        "isVideo": false
      },
      {
        "platform": "facebook",
        "url": "https://www.facebook.com/groups/dogspotting/posts/10161487929709467/",
        "id": "10161487929709467",
        "caption": "Hey guys, happy pride month! We ban for anti-LGBT posts and comments, thanks and have a good June! I forgot to post this in Dogspotting. \n\nRemember, Dogspotting is definitely the gay agenda. \n*dog photo stolen from another mod*",
        "description": "Hey guys, happy pride month! We ban for anti-LGBT posts and comments, thanks and have a good June! I forgot to post this in Dogspotting. \n\nRemember, Dogspotting is definitely the gay agenda. \n*dog photo stolen from another mod*",
        "publishedAt": "2023-06-04T23:32:57.000Z",
        "thumbnailUrl": "https://scontent-iad6-1.xx.fbcdn.net/v/t39.30808-6/499529333_10229703762722775_2097200119742123101_n.jpg?stp=dst-jpg_tt6&cstp=mx626x636&ctp=p526x296&_nc_cat=109&ccb=1-7&_nc_sid=aa7...",
        "author": {
          "username": "dogspotting",
          "displayName": "Tiberius Bertea"
        },
        "engagement": {
          "likes": 516,
          "comments": 26,
          "shares": 0
        },
        "isVideo": false
      },
      {
        "platform": "facebook",
        "url": "https://www.facebook.com/groups/dogspotting/posts/10161384058399467/",
        "id": "10161384058399467",
        "caption": "Hello all, \n\nYou’re probably familiar with our admin Amber, affectionately known to her friends as Yams. Amber is an incredibly caring and special person who pours her all into her hobbies, convictions, and her friendships. Whenever something happens, she’s the first to jump in determining how to help others. This rings especially true in her efforts to support peers in emergencies, and her work fostering pups for the Humane Society.\n\nToday, Amber needs our help. She was injured in a tragic accident and is presently in the hospital. So we’re reaching out to the communities she’s spent many years putting love into, in the hopes that we can help her now. \n\nThank you for your time in reading this, and thank you if you choose to give. Anything helps.",
        "description": "Hello all, \n\nYou’re probably familiar with our admin Amber, affectionately known to her friends as Yams. Amber is an incredibly caring and special person who pours her all into her hobbies, convictions, and her friendships. Whenever something happens, she’s the first to jump in determining how to help others. This rings especially true in her efforts to support peers in emergencies, and her work fostering pups for the Humane Society.\n\nToday, Amber needs our help. She was injured in a tragic accident and is presently in the hospital. So we’re reaching out to the communities she’s spent many years putting love into, in the hopes that we can help her now. \n\nThank you for your time in reading this, and thank you if you choose to give. Anything helps.",
        "publishedAt": "2023-04-21T17:50:53.000Z",
        "thumbnailUrl": "https://scontent-iad3-2.xx.fbcdn.net/v/t1.6435-9/103961332_2591579321116865_8247201645454706872_n.jpg?stp=dst-jpg_tt6&cstp=mx960x502&ctp=s960x502&_nc_cat=103&ccb=1-7&_nc_sid=0b1479...",
        "author": {
          "username": "dogspotting",
          "displayName": "Dogspotting",
          "url": "https://www.facebook.com/100069522984491"
        },
        "engagement": {
          "likes": 70,
          "comments": 19,
          "shares": 0
        },
        "isVideo": false
      },
      {
        "platform": "facebook",
        "url": "https://www.facebook.com/groups/dogspotting/posts/10159514349104467/",
        "id": "10159514349104467",
        "caption": "**Happy New Year, spotters! We have an exciting update for everyone [🐶](https://emojipedia.org/dog-face/)**\n\nThis past year has been a difficult one for everyone, and like many others, we wanted to ring in the new year with a fresh start. What this means for the group is an awesome new points system!\n\nMany from the last iteration of bonus points remain, but we’ve added some new ones and brought back some old favorites. We’ve created an instructional Powerpoint for everyone to learn about these changes, as well as a handy cheat sheet to take with you as you spot!\n\nFeel free to post your own dog or a favorite spot in the comments and let us know which new bonus point is your favorite!\n\nMay the Dogs flow!",
        "description": "**Happy New Year, spotters! We have an exciting update for everyone [🐶](https://emojipedia.org/dog-face/)**\n\nThis past year has been a difficult one for everyone, and like many others, we wanted to ring in the new year with a fresh start. What this means for the group is an awesome new points system!\n\nMany from the last iteration of bonus points remain, but we’ve added some new ones and brought back some old favorites. We’ve created an instructional Powerpoint for everyone to learn about these changes, as well as a handy cheat sheet to take with you as you spot!\n\nFeel free to post your own dog or a favorite spot in the comments and let us know which new bonus point is your favorite!\n\nMay the Dogs flow!",
        "publishedAt": "2021-01-01T05:00:02.000Z",
        "thumbnailUrl": "https://scontent-hou1-1.xx.fbcdn.net/v/t1.6435-9/133293956_2757029211238541_8556362737627446916_n.jpg?stp=dst-jpg_tt6&cstp=mx1178x664&ctp=p600x600&_nc_cat=103&ccb=1-7&_nc_sid=9fe6e...",
        "author": {
          "username": "dogspotting",
          "displayName": "Dogspotting",
          "url": "https://www.facebook.com/100069522984491"
        },
        "engagement": {
          "likes": 214,
          "comments": 53,
          "shares": 0
        },
        "isVideo": false
      },
      {
        "platform": "facebook",
        "url": "https://www.facebook.com/groups/dogspotting/posts/10159050659364467/",
        "id": "10159050659364467",
        "caption": "Welcome to Dogspotting, the sport of spotting unknown dogs! ***Please click on or tap the following images to review our introduction, rules, list of team members, and scoring information.***",
        "description": "Welcome to Dogspotting, the sport of spotting unknown dogs! ***Please click on or tap the following images to review our introduction, rules, list of team members, and scoring information.***",
        "publishedAt": "2020-07-12T07:32:41.000Z",
        "thumbnailUrl": "https://scontent.fagc1-1.fna.fbcdn.net/v/t1.6435-9/109276728_2614404018834395_7966348785768951769_n.jpg?stp=dst-jpg_tt6&cstp=mx820x820&ctp=s600x600&_nc_cat=101&ccb=1-7&_nc_sid=9fe6...",
        "author": {
          "username": "dogspotting",
          "displayName": "Dogspotting",
          "url": "https://www.facebook.com/100069522984491"
        },
        "engagement": {
          "likes": 131,
          "comments": 10,
          "shares": 0
        },
        "isVideo": false
      }
    ]
  },
  "facebook-marketplace-item": {
    "platform": "facebook",
    "id": "2228870800986975",
    "url": "https://www.facebook.com/marketplace/item/2228870800986975/",
    "title": "Elabest Mesh Office Chair, Ergonomic Computer Desk Chair, Sturdy Task Chair - Adjustable Lumbar Support",
    "description": "Breathable mesh office chair has an ergonomic design with a high back and adjustable headrest. This light gray task chair is manufactured by Elabest and features adjustable armrests, a five-point rolling base, and integrated lumbar support.\n\nEstimated (WxDxH): 26 x 24 x 45 in",
    "price": 125.0,
    "priceFormatted": "$125",
    "currency": "USD",
    "condition": "Used - like new",
    "location": "Arlington, VA",
    "latitude": 38.888854980469,
    "longitude": -77.085571289062,
    "isSold": true,
    "isLive": true,
    "deliveryTypes": [
      "IN_PERSON",
      "DOOR_PICKUP"
    ],
    "image": "https://scontent-mad1-1.xx.fbcdn.net/v/t39.84726-6/749377945_1746854896315726_817991790771142418_n.jpg?stp=dst-jpg_p720x720_tt6&_nc_cat=100&ccb=1-7&_nc_sid=92e707&_nc_ohc=Td50J02FhxwQ7kNvwEMS5Gk&_nc_oc=Adq3GF3R5f05eu3AlZfXV5BYX7n-dl-fGhjd7L4VfCb2IZztMYgOGJOLqDwEA8uVUvU&_nc_zt=14&_nc_ht=scontent-mad1-1.xx&_nc_gid=Srmkvq9GlIeOtnd0GDpLVA&_nc_ss=7b289&oh=00_AQC6x7FebWsdvTVd2WTXik82gabWPwTIgqcmEHjtOn9PRA&oe=6A6D9DBB",
    "photos": [
      "https://scontent-mad1-1.xx.fbcdn.net/v/t39.84726-6/749377945_1746854896315726_817991790771142418_n.jpg?stp=dst-jpg_p720x720_tt6&_nc_cat=100&ccb=1-7&_nc_sid=92e707&_nc_ohc=Td50J02FhxwQ7kNvwEMS5Gk&_nc_oc=Adq3GF3R5f05eu3AlZfXV5BYX7n-dl-fGhjd7L4VfCb2IZztMYgOGJOLqDwEA8uVUvU&_nc_zt=14&_nc_ht=scontent-mad1-1.xx&_nc_gid=Srmkvq9GlIeOtnd0GDpLVA&_nc_ss=7b289&oh=00_AQC6x7FebWsdvTVd2WTXik82gabWPwTIgqcmEHjtOn9PRA&oe=6A6D9DBB",
      "https://scontent-mad2-1.xx.fbcdn.net/v/t45.5328-4/750643688_1384573667068640_514500939676617077_n.jpg?stp=dst-jpg_p720x720_tt6&_nc_cat=111&ccb=1-7&_nc_sid=247b10&_nc_ohc=Aa-65J_vFfcQ7kNvwF56W3U&_nc_oc=AdqZo7FznGIikAd34m8FI2BzTOz3YUC3qQQ7lZPPYOm6lxpve9wXM1XMfZkSG1T1N-k&_nc_zt=23&_nc_ht=scontent-mad2-1.xx&_nc_gid=Srmkvq9GlIeOtnd0GDpLVA&_nc_ss=7b289&oh=00_AQADpKLF9okchpYthAq_g22eIr1EZlOHwgG-Ih5jzyIFyQ&oe=6A6D812F",
      "https://scontent-mad2-1.xx.fbcdn.net/v/t45.5328-4/750146978_1059729840108608_2219865786574902059_n.jpg?stp=dst-jpg_p720x720_tt6&_nc_cat=109&ccb=1-7&_nc_sid=247b10&_nc_ohc=Od7eQQlkVhIQ7kNvwGRxsbk&_nc_oc=AdqFpqYUQXur41TQG2apzKrDL1Lnw8X0iotSUeRWCLQ68cuWGvaUF7Mu9Ch_I1qHnJo&_nc_zt=23&_nc_ht=scontent-mad2-1.xx&_nc_gid=Srmkvq9GlIeOtnd0GDpLVA&_nc_ss=7b289&oh=00_AQApBoZAQ3QJWoCeL0zE2VgUqNONBN79IgUmmDTgELpcAQ&oe=6A6D971E"
    ],
    "createdAt": "2026-07-17T18:23:51+00:00"
  },
  "facebook-marketplace-location-search": {
    "query": "Austin, TX",
    "totalReturned": 1,
    "locations": [
      {
        "id": "austin, tx|austin|tx",
        "name": "Austin, TX",
        "city": "Austin",
        "state": "TX",
        "latitude": 30.2677,
        "longitude": -97.7475
      }
    ]
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
    "nextCursor": "eyJ2IjoxLCJxIjoiZGVzayBjaGFpciIsImxvYyI6IkF1c3RpbiwgVFgiLCJmIjp7Im1pblByaWNlIjoiNTAiLCJtYXhQcmljZSI6IjIwMCIsInNvcnRCeSI6InByaWNlX2FzY2VuZCIsImRheXNTaW5jZUxpc3RlZCI6IjMwIn0sInNraXAiOjUsImVjIjoie1wicGdcIjowLFwiYjJjXCI6e1wiYnJcIjpcIlwiLFwiaXRcIjowLFwiaG1zclwiOmZhbHNlLFwidGJpXCI6MH0sXCJjMmNcIjp7XCJiclwiOlwiQWJwaXVWdElpSVhFajlWV0ZVZEl4czFJUi13SldycGx1NWlNTGNYOURiMTBTQzhFQk93YzFXZi1RcmpOcDM3elBFWlg5ZGJNdlNDa0ZUay1sclBucTlCTnJGWURUdHg5bFZlMFhGd2FGdEQ0RG03T3RkemJBMU5MVWdkLUFrclRhc3hPZHVmWldmVkJTZlJTTG1SYmZydWVBVW85QTRNZXBqc1I0cm0zV09FejNSYlhIVnRrcm9SV21JZ1liUUZYN0Y0WnpfNnlhQTRkdThSY1BRbzJJeUwtcC1Ca3hlTVhHblFLSHZ1ZXJyZ2J2alN0M2hXNEFNdDZlclE1UkpGOUhSdFk3b1RLbGI2bTVfTUZEd2FqcXdMbUJhSzBKWlVKN3ZsUnczVFlQMm9SSjVoMDFxSndUU2Z6enduMkFodEFlcVFaUEs0eWV5OEc0WGZ0bm81cERJYzZDUWNzTWtRdEJjZDE2R3FNanQwQXhybkNJM1A0OFZINmZqcG9vM3hGTnJqU3ZvRDhOOGNxbVFMaVJzVy1SRlF2am9CNTdGWkkzVkpMLXhLN204cUVNaUczcnZKUlRJd2ZLS2VHdTlBckJXbi1SODJuNkVPUU9MU2loUkppTlY4Q0Rxamw0WnIyUVJmcXFMN3hmNzZPSnBzaEVxWi05Z1JWRWlzaFdJcUx1eWY0YzF6NE1zMUZ5YTNDeUZxamgtdDBtei1nR3dTZGhEOEhxelloQXhYWGZsU0NkdGUxVWIwaVBiRVctSUhqQmVjXCIsXCJpdFwiOjI0LFwicnBiclwiOlwiXCIsXCJycGhyXCI6ZmFsc2UsXCJybWhyXCI6ZmFsc2UsXCJzc2lcIjpmYWxzZSxcInNzY29cIjowLFwic3NwaVwiOltdfSxcImlyclwiOmZhbHNlLFwic2VycF9jdGFcIjpmYWxzZSxcInJ1aVwiOltdLFwibXBpZFwiOltdLFwidWJwXCI6bnVsbCxcIm5jcm5kXCI6MCxcImlyc3JcIjpmYWxzZSxcImJtcHJcIjpbXSxcImJtcGVpZFwiOltdLFwibm1ibXBcIjpmYWxzZSxcInNrcnJcIjpmYWxzZSxcImlvb3VyXCI6ZmFsc2UsXCJpc2VcIjp0cnVlLFwic21zX2N1cnNvclwiOntcInBhZ2VfaW5kZXhcIjowLFwiYmxlbmRlZF9hZF9pbmRleFwiOjAsXCJvcmdhbmljc19zaW5jZV9sYXN0X2FkXCI6MCxcInBhZ2Vfb3JnYW5pY19jb3VudFwiOjAsXCJibGVuZGVkX29yZ2FuaWNfaW5kZXhcIjowLFwicmV0dXJuZWRfYWRfaW5kZXhcIjowLFwidG90YWxfaW5kZXhcIjowfX0ifQ",
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
        "isLive": true,
        "isPending": false,
        "isHidden": false,
        "isViewerSeller": false,
        "deliveryTypes": [
          "IN_PERSON",
          "SHIPPING_ONSITE"
        ],
        "image": "https://scontent-atl3-3.xx.fbcdn.net/v/t39.84726-6/748718464_1472100928021023_7004614235492134530_n.jpg?stp=c0.87.526.526a_dst-jpg_p526x395_tt6&_nc_cat=109&ccb=1-7&_nc_sid=92e707&_nc_ohc=Osco_iBPSHsQ7kNvwE88Z2B&_nc_oc=AdrnNrq4GxtoKGWCDi_qxKj2BfO-OcysnTpk7mDO5d-84zPauj6YWLhxJPZuiRErURoSW7OUci-LjqdvjivdYc4u&_nc_zt=14&_nc_ht=scontent-atl3-3.xx&_nc_gid=48UkL5OoevcKmJAZmxtYnw&_nc_ss=7b289&oh=00_AQFTCh3FFtSTB-AA28V6Jr1NtrTs9PSVie1b1KW_xUkkNw&oe=6A753B85",
        "photos": [
          "https://scontent-atl3-3.xx.fbcdn.net/v/t39.84726-6/748718464_1472100928021023_7004614235492134530_n.jpg?stp=c0.87.526.526a_dst-jpg_p526x395_tt6&_nc_cat=109&ccb=1-7&_nc_sid=92e707&_nc_ohc=Osco_iBPSHsQ7kNvwE88Z2B&_nc_oc=AdrnNrq4GxtoKGWCDi_qxKj2BfO-OcysnTpk7mDO5d-84zPauj6YWLhxJPZuiRErURoSW7OUci-LjqdvjivdYc4u&_nc_zt=14&_nc_ht=scontent-atl3-3.xx&_nc_gid=48UkL5OoevcKmJAZmxtYnw&_nc_ss=7b289&oh=00_AQFTCh3FFtSTB-AA28V6Jr1NtrTs9PSVie1b1KW_xUkkNw&oe=6A753B85"
        ],
        "createdAt": "2026-07-16T06:02:16+00:00"
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
        "isLive": true,
        "isPending": false,
        "isHidden": false,
        "isViewerSeller": false,
        "deliveryTypes": [
          "IN_PERSON",
          "SHIPPING_ONSITE"
        ],
        "image": "https://scontent-atl3-3.xx.fbcdn.net/v/t39.84726-6/749286700_1116782047845292_1788708914246608626_n.jpg?stp=c0.81.526.526a_dst-jpg_p526x395_tt6&_nc_cat=110&ccb=1-7&_nc_sid=92e707&_nc_ohc=gbzkYGqnXmYQ7kNvwGzH1qf&_nc_oc=AdqLUHLAdzpxyU4TF9F6Xf5v9Tib9M6UCrmYThgY8kMR7j8y-uMyvFm3zwMzYYMwX1rcrfF1-yMiBdhJbknk-W2-&_nc_zt=14&_nc_ht=scontent-atl3-3.xx&_nc_gid=48UkL5OoevcKmJAZmxtYnw&_nc_ss=7b289&oh=00_AQHJWOlgp25sCHb9Xzuo5yQVzSCjOZpSF6EaQpKDCudKZA&oe=6A751DFD",
        "photos": [
          "https://scontent-atl3-3.xx.fbcdn.net/v/t39.84726-6/749286700_1116782047845292_1788708914246608626_n.jpg?stp=c0.81.526.526a_dst-jpg_p526x395_tt6&_nc_cat=110&ccb=1-7&_nc_sid=92e707&_nc_ohc=gbzkYGqnXmYQ7kNvwGzH1qf&_nc_oc=AdqLUHLAdzpxyU4TF9F6Xf5v9Tib9M6UCrmYThgY8kMR7j8y-uMyvFm3zwMzYYMwX1rcrfF1-yMiBdhJbknk-W2-&_nc_zt=14&_nc_ht=scontent-atl3-3.xx&_nc_gid=48UkL5OoevcKmJAZmxtYnw&_nc_ss=7b289&oh=00_AQHJWOlgp25sCHb9Xzuo5yQVzSCjOZpSF6EaQpKDCudKZA&oe=6A751DFD"
        ],
        "createdAt": "2026-07-18T17:45:28+00:00"
      },
      {
        "platform": "facebook",
        "id": "2923413478020563",
        "title": "Vintage1970s Nichols & Stone Co.Rocking Chair",
        "url": "https://www.facebook.com/marketplace/item/2923413478020563/",
        "price": 50.0,
        "priceFormatted": "$50",
        "priceAmount": 5000,
        "currency": "USD",
        "strikethroughPrice": 100.0,
        "strikethroughPriceFormatted": "$100",
        "categoryId": "393860164117441",
        "location": "Rome, GA",
        "city": "Rome",
        "state": "GA",
        "cityPageId": "107963899224102",
        "isSold": false,
        "isLive": true,
        "isPending": false,
        "isHidden": false,
        "isViewerSeller": false,
        "deliveryTypes": [
          "IN_PERSON",
          "SHIPPING_ONSITE"
        ],
        "image": "https://scontent-atl3-2.xx.fbcdn.net/v/t39.84726-6/749315387_1673120763899840_2089201881053873382_n.jpg?stp=c90.0.540.540a_dst-jpg_p180x540_tt6&_nc_cat=101&ccb=1-7&_nc_sid=92e707&_nc_ohc=yzjaBCMGrMMQ7kNvwGfHl6m&_nc_oc=AdqiHHMNN2qvUfzBzmJ6q9wS97vlPFf4F-wRzvmtx-qFyOdbSsq4Aji2cCitIRxWt3iZWwzWr0PYKUcTLL98O7J7&_nc_zt=14&_nc_ht=scontent-atl3-2.xx&_nc_gid=48UkL5OoevcKmJAZmxtYnw&_nc_ss=7b289&oh=00_AQH_n97Ur_wuC5aujGv1-I6KEFId_1VfGGX1xC0UpCQc6Q&oe=6A753AD8",
        "photos": [
          "https://scontent-atl3-2.xx.fbcdn.net/v/t39.84726-6/749315387_1673120763899840_2089201881053873382_n.jpg?stp=c90.0.540.540a_dst-jpg_p180x540_tt6&_nc_cat=101&ccb=1-7&_nc_sid=92e707&_nc_ohc=yzjaBCMGrMMQ7kNvwGfHl6m&_nc_oc=AdqiHHMNN2qvUfzBzmJ6q9wS97vlPFf4F-wRzvmtx-qFyOdbSsq4Aji2cCitIRxWt3iZWwzWr0PYKUcTLL98O7J7&_nc_zt=14&_nc_ht=scontent-atl3-2.xx&_nc_gid=48UkL5OoevcKmJAZmxtYnw&_nc_ss=7b289&oh=00_AQH_n97Ur_wuC5aujGv1-I6KEFId_1VfGGX1xC0UpCQc6Q&oe=6A753AD8"
        ],
        "createdAt": "2026-07-18T02:52:50+00:00"
      },
      {
        "platform": "facebook",
        "id": "1017066137601706",
        "title": "Vintage vanity chair, wardrobe assistant, great for putting on shoes, accent chair in living room.",
        "url": "https://www.facebook.com/marketplace/item/1017066137601706/",
        "price": 50.0,
        "priceFormatted": "$50",
        "priceAmount": 5000,
        "currency": "USD",
        "categoryId": "393860164117441",
        "location": "Maryville, TN",
        "city": "Maryville",
        "state": "TN",
        "cityPageId": "112258735456868",
        "isSold": false,
        "isLive": true,
        "isPending": false,
        "isHidden": false,
        "isViewerSeller": false,
        "deliveryTypes": [
          "IN_PERSON",
          "SHIPPING_ONSITE"
        ],
        "image": "https://scontent-atl3-3.xx.fbcdn.net/v/t39.84726-6/741215085_852313984369406_1199345941718414788_n.jpg?stp=c0.0.526.526a_dst-jpg_p526x395_tt6&_nc_cat=108&ccb=1-7&_nc_sid=92e707&_nc_ohc=1rWcQdyGDVkQ7kNvwFqYy36&_nc_oc=AdpU7HoeqvlHL9o_N9JOFFwP4AjJebYky0kIUeH_AF9v0dqoDq4pWdxRGzMlSVSIpF6QKH4sbjMcRi7o-RS7LSbq&_nc_zt=14&_nc_ht=scontent-atl3-3.xx&_nc_gid=48UkL5OoevcKmJAZmxtYnw&_nc_ss=7b289&oh=00_AQEqWptcpVP9NCT1UFRFTfDjcdjzHfl2aISSZ3d1tj-7Kg&oe=6A7533E5",
        "photos": [
          "https://scontent-atl3-3.xx.fbcdn.net/v/t39.84726-6/741215085_852313984369406_1199345941718414788_n.jpg?stp=c0.0.526.526a_dst-jpg_p526x395_tt6&_nc_cat=108&ccb=1-7&_nc_sid=92e707&_nc_ohc=1rWcQdyGDVkQ7kNvwFqYy36&_nc_oc=AdpU7HoeqvlHL9o_N9JOFFwP4AjJebYky0kIUeH_AF9v0dqoDq4pWdxRGzMlSVSIpF6QKH4sbjMcRi7o-RS7LSbq&_nc_zt=14&_nc_ht=scontent-atl3-3.xx&_nc_gid=48UkL5OoevcKmJAZmxtYnw&_nc_ss=7b289&oh=00_AQEqWptcpVP9NCT1UFRFTfDjcdjzHfl2aISSZ3d1tj-7Kg&oe=6A7533E5"
        ],
        "createdAt": "2026-07-09T08:31:52+00:00"
      },
      {
        "platform": "facebook",
        "id": "881051264629414",
        "title": "Vintage Amber Shell Bowls. (1 Lg, 4 small included.)",
        "url": "https://www.facebook.com/marketplace/item/881051264629414/",
        "price": 50.0,
        "priceFormatted": "$50",
        "priceAmount": 5000,
        "currency": "USD",
        "categoryId": "393860164117441",
        "location": "Fredericksburg, VA",
        "city": "Fredericksburg",
        "state": "VA",
        "cityPageId": "113115852035715",
        "isSold": false,
        "isLive": true,
        "isPending": false,
        "isHidden": false,
        "isViewerSeller": false,
        "deliveryTypes": [
          "IN_PERSON",
          "SHIPPING_ONSITE"
        ],
        "image": "https://scontent-atl3-3.xx.fbcdn.net/v/t39.84726-6/752497517_1511663550122072_1173419982088349245_n.jpg?stp=c89.0.540.540a_dst-jpg_p180x540_tt6&_nc_cat=109&ccb=1-7&_nc_sid=92e707&_nc_ohc=sera2ZomqWAQ7kNvwGSF1lp&_nc_oc=AdqITSx-NaNloczS3k1wp8xihTAjYYb0y10n7UOeZWDKTydDSaVoG4-37EHGiZJRsi3Ah6IwReJt0KGUq5phIu99&_nc_zt=14&_nc_ht=scontent-atl3-3.xx&_nc_gid=48UkL5OoevcKmJAZmxtYnw&_nc_ss=7b289&oh=00_AQEA8yZzcg5BBISfEWS39nFNBpk3W3GmWNKXweosR4MRAg&oe=6A752917",
        "photos": [
          "https://scontent-atl3-3.xx.fbcdn.net/v/t39.84726-6/752497517_1511663550122072_1173419982088349245_n.jpg?stp=c89.0.540.540a_dst-jpg_p180x540_tt6&_nc_cat=109&ccb=1-7&_nc_sid=92e707&_nc_ohc=sera2ZomqWAQ7kNvwGSF1lp&_nc_oc=AdqITSx-NaNloczS3k1wp8xihTAjYYb0y10n7UOeZWDKTydDSaVoG4-37EHGiZJRsi3Ah6IwReJt0KGUq5phIu99&_nc_zt=14&_nc_ht=scontent-atl3-3.xx&_nc_gid=48UkL5OoevcKmJAZmxtYnw&_nc_ss=7b289&oh=00_AQEA8yZzcg5BBISfEWS39nFNBpk3W3GmWNKXweosR4MRAg&oe=6A752917"
        ],
        "createdAt": "2026-07-20T06:20:50+00:00"
      }
    ]
  },
  "facebook-page-details": {
    "platform": "facebook",
    "url": "https://www.facebook.com/NASA",
    "username": "NASA",
    "name": "NASA",
    "displayName": "NASA",
    "fullName": "NASA - National Aeronautics and Space Administration",
    "bio": "Explore the universe and discover our home planet. \nThere's space for everybody. ✨",
    "followers": 28661037,
    "following": 52,
    "likes": 28661037,
    "verified": true,
    "profileImage": "https://scontent.fsac1-1.fna.fbcdn.net/v/t39.30808-1/243095782_416661036495945_3843362260429099279_n.png?stp=dst-png&cstp=mx800x800&ctp=s200x200&_nc_cat=108&ccb=1-7&_nc_sid=f907e8&_nc_ohc=rc5kNRYek84Q7kNvwF8Sa_u&_nc_oc=AdrNvQfTevsfOPnr9fNsTnlh9J829gS2FUbp3T7-OE4v3qnLsURBqMMwq6zKi3x3jnA&_nc_zt=24&_nc_ht=scontent.fsac1-1.fna&_nc_gid=R5adZW0LMUuuYyLoZKxfZQ&_nc_ss=7b289&oh=00_AQCvsaV4YwQoigD-2yXvzz5KJ0wSPrw9jH8qLU9nIrFwBw&oe=6A6D8255",
    "coverImage": "https://scontent.fsac1-2.fna.fbcdn.net/v/t39.30808-6/663298991_1496429661852405_5171518456419416626_n.jpg?stp=dst-jpg_tt6&cstp=mx2048x1366&ctp=s960x960&_nc_cat=105&ccb=1-7&_nc_sid=cc71e4&_nc_ohc=qTuXCYf3o_IQ7kNvwHdjJ4X&_nc_oc=AdqtYKrQs5jP45CGjFAOTTU1zFWFFzf9eE3qCZKk6A3sTl0Bt3L_xBwBQ-gSHNpmrnE&_nc_zt=23&_nc_ht=scontent.fsac1-2.fna&_nc_gid=R5adZW0LMUuuYyLoZKxfZQ&_nc_ss=7b289&oh=00_AQDUkGzKMQhEkgqFBKtc9Hv0I9CLn1T8a0ZzxfSl3uEOHQ&oe=6A6D5EE3",
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
        "id": "1270386418439478",
        "url": "https://www.facebook.com/events/1270386418439478/",
        "name": "Bon Jovi: Forever Tour",
        "startTime": "Sun, Jul 26 at 7:30 PM EDT",
        "address": "Madison Square Garden",
        "location": {
          "name": "Madison Square Garden"
        }
      },
      {
        "platform": "facebook",
        "id": "1426952632010473",
        "url": "https://www.facebook.com/events/1426952632010473/",
        "name": "Phish",
        "startTime": "Mon, Jul 27 at 7:30 PM EDT",
        "address": "Madison Square Garden",
        "location": {
          "name": "Madison Square Garden"
        }
      },
      {
        "platform": "facebook",
        "id": "1217913490078179",
        "url": "https://www.facebook.com/events/1217913490078179/",
        "name": "RUSH: Fifty Something",
        "startTime": "Tue, Jul 28 at 7:30 PM EDT",
        "address": "Madison Square Garden",
        "location": {
          "name": "Madison Square Garden"
        }
      },
      {
        "platform": "facebook",
        "id": "1957542368474959",
        "url": "https://www.facebook.com/events/1957542368474959/",
        "name": "Phish",
        "startTime": "Wed, Jul 29 at 7:30 PM EDT",
        "address": "Madison Square Garden",
        "location": {
          "name": "Madison Square Garden"
        }
      },
      {
        "platform": "facebook",
        "id": "847403967774434",
        "url": "https://www.facebook.com/events/847403967774434/",
        "name": "RUSH: Fifty Something",
        "startTime": "Thu, Jul 30 at 7:30 PM EDT",
        "address": "Madison Square Garden",
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
        "caption": "A galaxy cluster in deep space. It is filled with elliptical galaxies: small, bright white glowing ovals. The two largest elliptical galaxies, left and right of center, are bright cores that radiate light. Unrelated, distant galaxies are scattered around as red smudges and dots. Many of these are stretched out into red arcs and lines by the galaxy cluster’s strong gravity, creating multiple images in places. Numerous spiral galaxies and bright stars appear in the foreground. Credit: ESA/Webb, NASA & CSA, S. Fujimoto",
        "width": 2047,
        "height": 1012
      },
      {
        "platform": "facebook",
        "id": "1586655189496518",
        "url": "https://www.facebook.com/photo.php?fbid=1586655189496518",
        "image": "https://scontent-dfw6-2.xx.fbcdn.net/v/t39.30808-6/756229023_1586655192829851_1923291187225748989_n.jpg?stp=dst-jpg_tt6&cstp=mx1884x1054&ctp=s1884x1054&_nc_cat=110&ccb=1-7&_nc_sid=...",
        "caption": "An aerial view of a spacecraft about to land on Earth; the capsule is barely visible, but a large white-and-red parachute billows above it. The plain around it is flat and featureless. Credit: NASA+",
        "width": 1884,
        "height": 1054
      },
      {
        "platform": "facebook",
        "id": "1585138822981488",
        "url": "https://www.facebook.com/photo.php?fbid=1585138822981488",
        "image": "https://scontent-dfw5-1.xx.fbcdn.net/v/t39.99422-6/754498097_1529437744896067_7884542055079848706_n.png?stp=dst-jpg_tt6&cstp=mx2048x2048&ctp=s2048x2048&_nc_cat=111&ccb=1-7&_nc_sid=...",
        "caption": "The scene is cloaked in a cool, blue haze, decorated with the warm light of galaxies and stars. Around the center is a jagged ring where the haze appears absent and dark space peeks through. Credit: NASA, ESA, M.J. Jee and H. Ford (Johns Hopkins University)",
        "width": 2048,
        "height": 2048
      },
      {
        "platform": "facebook",
        "id": "1583701686458535",
        "url": "https://www.facebook.com/photo.php?fbid=1583701686458535",
        "image": "https://scontent-dfw5-1.xx.fbcdn.net/v/t39.99422-6/752620057_1361351692793736_6372731408048785122_n.png?stp=dst-jpg_tt6&cstp=mx2048x1713&ctp=s2048x1713&_nc_cat=105&ccb=1-7&_nc_sid=...",
        "caption": "The Lighthouse Nebula (upper left) and a pulsar (lower right) are illuminated against a spotty starfield. The part of the nebula shown in this image looks like a diffuse, purple cloud with a bright star in the center. The pulsar looks like a bright white streak of light with a purple jet extending from one end, forming the shape of a checkmark. Credits: X-ray: Chandra: NASA/CXC/Stanford Univ./J.T. Dinsmore et al.; IXPE: NASA/MSFC/J.T. Dinsmore et al., Radio: CSIRO/ATNF/ATCA; Optical: 2MASS/UMass/IPAC-Caltech/NASA/NSF; Image processing: NASA/CXC/SAO/L. Frattare",
        "width": 2048,
        "height": 1713
      },
      {
        "platform": "facebook",
        "id": "1582125049949532",
        "url": "https://www.facebook.com/photo.php?fbid=1582125049949532",
        "image": "https://scontent-dfw6-2.xx.fbcdn.net/v/t39.30808-6/752699303_1582125053282865_6907261101135459632_n.jpg?stp=dst-jpg_tt6&cstp=mx1080x1080&ctp=s1080x1080&_nc_cat=110&ccb=1-7&_nc_sid=...",
        "caption": "Astronaut Buzz Aldrin, wearing his spacesuit, descends the ladder of the Apollo 11 Lunar Module, a large structure with golden foil covering its lower half. The Moon's surface is bright and flat; above the horizon, which slopes downward from right-to-left, the sky is completely black. Credit: NASA",
        "width": 1080,
        "height": 1080
      },
      {
        "platform": "facebook",
        "id": "1578224950339542",
        "url": "https://www.facebook.com/photo.php?fbid=1578224950339542",
        "image": "https://scontent-dfw5-1.xx.fbcdn.net/v/t39.99422-6/747931162_1667321021008266_4517886636206841967_n.png?stp=dst-jpg_tt6&cstp=mx2048x1365&ctp=s2048x1365&_nc_cat=111&ccb=1-7&_nc_sid=...",
        "caption": "Anil and Anna Menon pose for a photograph at the Cosmonaut Hotel in Baikonur. Anil, in pre-launch quarantine at the time of this photo, is behind glass, but Anil and Anna are leaning close to each other. Both Anil and Anna are looking at the camera with big grins. Credit: NASA/John Kraus",
        "width": 2048,
        "height": 1365
      },
      {
        "platform": "facebook",
        "id": "1578224920339545",
        "url": "https://www.facebook.com/photo.php?fbid=1578224920339545",
        "image": "https://scontent-dfw5-1.xx.fbcdn.net/v/t39.99422-6/748527781_2080772216199706_6612040318485045639_n.png?stp=dst-jpg_tt6&cstp=mx2048x1365&ctp=s2048x1365&_nc_cat=106&ccb=1-7&_nc_sid=...",
        "caption": "Astronaut candidate Anna Menon and her two children watch a Soyuz rocket lift off in the distance. The three are standing in the middle of a scrubby field, wearing dark t-shirts with \"Team Menon\" on the back; Anna is carrying one of her children on her shoulders. Credit: NASA/John Kraus",
        "width": 2048,
        "height": 1365
      },
      {
        "platform": "facebook",
        "id": "1578224907006213",
        "url": "https://www.facebook.com/photo.php?fbid=1578224907006213",
        "image": "https://scontent-dfw5-1.xx.fbcdn.net/v/t39.99422-6/746343278_880948677971054_703395191772258474_n.png?stp=dst-jpg_tt6&cstp=mx2048x1365&ctp=s2048x1365&_nc_cat=106&ccb=1-7&_nc_sid=12...",
        "caption": "A closer shot of the Soyuz lifting off at Baikonur. Its flaming rockets flare out from a central column, with the spacecraft on top. Two large, antenna-like stands frame the rocket, with metal tracks running from the launch site into the foreground. Credit: NASA/Bill Ingalls",
        "width": 2048,
        "height": 1365
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
          "username": "nasa",
          "displayName": "NASA - National Aeronautics and Space Administration",
          "url": "https://www.facebook.com/NASA"
        },
        "engagement": {
          "likes": 1861,
          "comments": 84,
          "shares": 0
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
          "profileImage": "https://scontent-iad3-1.xx.fbcdn.net/v/t39.30808-1/243095782_416661036495945_3843362260429099279_n.png?stp=cp0_dst-png&cstp=mx800x800&ctp=s40x40&_nc_cat=1&ccb=1-7&_nc_sid=2d3e12&_n...",
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
      },
      {
        "platform": "facebook",
        "url": "https://www.facebook.com/reel/1023344310547434",
        "id": "1565523918276312",
        "caption": "Come watch a spacewalk with us!\n\nNASA astronauts Chris Williams and Jessica Meir are stepping outside the International Space Station for about six and a half hours to make repairs to the station's Canadarm2 robotic arm. Tune in: https://youtu.be/D0dd8X4g3Eg",
        "description": "Come watch a spacewalk with us!\n\nNASA astronauts Chris Williams and Jessica Meir are stepping outside the International Space Station for about six and a half hours to make repairs to the station's Canadarm2 robotic arm. Tune in: https://youtu.be/D0dd8X4g3Eg",
        "publishedAt": "2026-06-30T14:00:41.000Z",
        "durationSeconds": 16.362,
        "thumbnailUrl": "https://scontent-sjc6-1.xx.fbcdn.net/v/t15.5256-10/736384680_1034463129116372_1847611548688510946_n.jpg?stp=dst-jpg_tt6&cstp=mx3840x2160&ctp=s960x960&_nc_cat=100&ccb=1-7&_nc_sid=be...",
        "videoUrl": "https://video-sjc3-1.xx.fbcdn.net/o1/v/t2/f2/m366/AQNuYSZM6m65K0Fk1iuF6LfY4iw2glvoNgX93Y-dmgWocy6hgsX_5hBee2XwT2P17RKnX8kug-hdZWZOgsxFOs6KpmZMXw8ZoqZxkouUJIzbRQ.mp4?_nc_cat=106&_nc...",
        "author": {
          "username": "NASA",
          "displayName": "NASA - National Aeronautics and Space Administration",
          "url": "https://www.facebook.com/NASA",
          "profileImage": "https://scontent-sjc3-1.xx.fbcdn.net/v/t39.30808-1/243095782_416661036495945_3843362260429099279_n.png?stp=cp0_dst-png&cstp=mx800x800&ctp=s40x40&_nc_cat=1&ccb=1-7&_nc_sid=2d3e12&_n...",
          "verified": true
        },
        "engagement": {
          "views": 5000000,
          "likes": 75366,
          "comments": 1960,
          "shares": 1900
        },
        "isVideo": true,
        "link": "https://youtu.be/D0dd8X4g3Eg"
      },
      {
        "platform": "facebook",
        "url": "https://www.facebook.com/reel/1736519150699488",
        "id": "1561248945370476",
        "caption": "We are at the Great American State Fair in Washington, D.C.!\n \nDiscover the technology and science driving our most exciting missions by visiting the NASA Pavilion—today through July 10: https://www.nasa.gov/freedom250/#american-state-fair",
        "description": "We are at the Great American State Fair in Washington, D.C.!\n \nDiscover the technology and science driving our most exciting missions by visiting the NASA Pavilion—today through July 10: https://www.nasa.gov/freedom250/#american-state-fair",
        "publishedAt": "2026-06-25T16:14:35.000Z",
        "durationSeconds": 120.0,
        "thumbnailUrl": "https://scontent-sjc3-1.xx.fbcdn.net/v/t15.5256-10/730182605_1314642917513572_6743020664352329210_n.jpg?stp=dst-jpg_tt6&cstp=mx720x405&ctp=s720x405&_nc_cat=103&ccb=1-7&_nc_sid=be83...",
        "videoUrl": "https://video-sjc3-1.xx.fbcdn.net/o1/v/t2/f2/m366/AQNw1vJID4pcVr5SpV62MejQDC3RWwcnlksqsPLAyq80dayfLcF2ZrUq_2WUXkvRjeDWpROR6cNqkK_ViG-PJvhZRxdrheFypJ1tHPUXtaqYMg.mp4?_nc_cat=110&_nc...",
        "author": {
          "username": "NASA",
          "displayName": "NASA - National Aeronautics and Space Administration",
          "url": "https://www.facebook.com/NASA",
          "profileImage": "https://scontent-sjc3-1.xx.fbcdn.net/v/t39.30808-1/243095782_416661036495945_3843362260429099279_n.png?stp=cp0_dst-png&cstp=mx800x800&ctp=s40x40&_nc_cat=1&ccb=1-7&_nc_sid=2d3e12&_n...",
          "verified": true
        },
        "engagement": {
          "views": 426000,
          "likes": 3601,
          "comments": 124,
          "shares": 199
        },
        "isVideo": true,
        "link": "https://www.nasa.gov/freedom250/#american-state-fair"
      }
    ]
  },
  "facebook-profile-reels": {
    "url": "https://www.facebook.com/NASA",
    "totalReturned": 12,
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
      },
      {
        "platform": "facebook",
        "url": "https://www.facebook.com/reel/1023344310547434",
        "id": "1565523918276312",
        "caption": "Come watch a spacewalk with us!\n\nNASA astronauts Chris Williams and Jessica Meir are stepping outside the International Space Station for about six and a half hours to make repairs to the station's Canadarm2 robotic arm. Tune in: https://youtu.be/D0dd8X4g3Eg",
        "description": "Come watch a spacewalk with us!\n\nNASA astronauts Chris Williams and Jessica Meir are stepping outside the International Space Station for about six and a half hours to make repairs to the station's Canadarm2 robotic arm. Tune in: https://youtu.be/D0dd8X4g3Eg",
        "publishedAt": "2026-06-30T14:00:41.000Z",
        "durationSeconds": 16.362,
        "thumbnailUrl": "https://scontent-iad6-1.xx.fbcdn.net/v/t15.5256-10/736384680_1034463129116372_1847611548688510946_n.jpg?stp=dst-jpg_tt6&cstp=mx3840x2160&ctp=s960x960&_nc_cat=100&ccb=1-7&_nc_sid=be...",
        "videoUrl": "https://video-iad6-1.xx.fbcdn.net/o1/v/t2/f2/m366/AQNuYSZM6m65K0Fk1iuF6LfY4iw2glvoNgX93Y-dmgWocy6hgsX_5hBee2XwT2P17RKnX8kug-hdZWZOgsxFOs6KpmZMXw8ZoqZxkouUJIzbRQ.mp4?_nc_cat=106&_nc...",
        "author": {
          "username": "NASA",
          "displayName": "NASA - National Aeronautics and Space Administration",
          "url": "https://www.facebook.com/NASA",
          "profileImage": "https://scontent-iad3-1.xx.fbcdn.net/v/t39.30808-1/243095782_416661036495945_3843362260429099279_n.png?stp=cp0_dst-png&cstp=mx800x800&ctp=s80x80&_nc_cat=1&ccb=1-7&_nc_sid=2d3e12&_n...",
          "verified": true
        },
        "engagement": {
          "views": 5000000,
          "likes": 75356,
          "comments": 1960,
          "shares": 1900
        },
        "isVideo": true,
        "link": "https://youtu.be/D0dd8X4g3Eg"
      },
      {
        "platform": "facebook",
        "url": "https://www.facebook.com/reel/1736519150699488",
        "id": "1561248945370476",
        "caption": "We are at the Great American State Fair in Washington, D.C.!\n \nDiscover the technology and science driving our most exciting missions by visiting the NASA Pavilion—today through July 10: https://www.nasa.gov/freedom250/#american-state-fair",
        "description": "We are at the Great American State Fair in Washington, D.C.!\n \nDiscover the technology and science driving our most exciting missions by visiting the NASA Pavilion—today through July 10: https://www.nasa.gov/freedom250/#american-state-fair",
        "publishedAt": "2026-06-25T16:14:35.000Z",
        "durationSeconds": 120.0,
        "thumbnailUrl": "https://scontent.fagc1-1.fna.fbcdn.net/v/t15.5256-10/730182605_1314642917513572_6743020664352329210_n.jpg?stp=dst-jpg_tt6&cstp=mx720x405&ctp=s720x405&_nc_cat=103&ccb=1-7&_nc_sid=be...",
        "videoUrl": "https://video.fagc1-1.fna.fbcdn.net/o1/v/t2/f2/m366/AQNw1vJID4pcVr5SpV62MejQDC3RWwcnlksqsPLAyq80dayfLcF2ZrUq_2WUXkvRjeDWpROR6cNqkK_ViG-PJvhZRxdrheFypJ1tHPUXtaqYMg.mp4?_nc_cat=110&_...",
        "author": {
          "username": "NASA",
          "displayName": "NASA - National Aeronautics and Space Administration",
          "url": "https://www.facebook.com/NASA",
          "profileImage": "https://scontent.fagc1-2.fna.fbcdn.net/v/t39.30808-1/243095782_416661036495945_3843362260429099279_n.png?stp=cp0_dst-png&cstp=mx800x800&ctp=s80x80&_nc_cat=108&ccb=1-7&_nc_sid=2d3e1...",
          "verified": true
        },
        "engagement": {
          "views": 426000,
          "likes": 3600,
          "comments": 124,
          "shares": 199
        },
        "isVideo": true,
        "link": "https://www.nasa.gov/freedom250/#american-state-fair"
      },
      {
        "platform": "facebook",
        "url": "https://www.facebook.com/reel/1284450976822099",
        "id": "1556903142471723",
        "caption": "The official FIFA World Cup ball went to space! \n\nWe're working to inspire the next generation by showing how space exploration inspires innovation in sports science — and everyday life. Learn more: https://go.nasa.gov/43G4Bhc",
        "description": "The official FIFA World Cup ball went to space! \n\nWe're working to inspire the next generation by showing how space exploration inspires innovation in sports science — and everyday life. Learn more: https://go.nasa.gov/43G4Bhc",
        "publishedAt": "2026-06-20T14:00:00.000Z",
        "durationSeconds": 32.265,
        "thumbnailUrl": "https://scontent-iad6-1.xx.fbcdn.net/v/t15.5256-10/725733247_1380772853937295_3761258904677594278_n.jpg?stp=dst-jpg_tt6&cstp=mx1920x1080&ctp=s960x960&_nc_cat=102&ccb=1-7&_nc_sid=be...",
        "videoUrl": "https://video-iad3-1.xx.fbcdn.net/o1/v/t2/f2/m366/AQPQKyLHqF5Wqx429Aupk5vSBIi8Fn5ZJlsk0t70-dGunM6qNJJ6X0h59alUxvB-NhU530Ni3B170IMkX5nvGlw5Igi0wUR6d3kODwjPB2xNcQ.mp4?_nc_cat=104&_nc...",
        "author": {
          "username": "NASA",
          "displayName": "NASA - National Aeronautics and Space Administration",
          "url": "https://www.facebook.com/NASA",
          "profileImage": "https://scontent-iad3-2.xx.fbcdn.net/v/t39.30808-1/243095782_416661036495945_3843362260429099279_n.png?stp=cp0_dst-png&cstp=mx800x800&ctp=s40x40&_nc_cat=1&ccb=1-7&_nc_sid=2d3e12&_n...",
          "verified": true
        },
        "engagement": {
          "views": 859000,
          "likes": 18191,
          "comments": 484,
          "shares": 1300
        },
        "isVideo": true,
        "link": "https://go.nasa.gov/43G4Bhc"
      },
      {
        "platform": "facebook",
        "url": "https://www.facebook.com/reel/2043044306290042",
        "id": "1548129933349044",
        "caption": "Get ready for Earth joy!\n \nEarlier today, we announced the four astronauts who will go to space as part of Artemis III. This mission will undertake a series of challenging tests in low Earth orbit in 2027, setting future NASA Artemis missions up to return humanity to the Moon. \n\nLearn more about Artemis III: https://www.nasa.gov/mission/artemis-iii/",
        "description": "Get ready for Earth joy!\n \nEarlier today, we announced the four astronauts who will go to space as part of Artemis III. This mission will undertake a series of challenging tests in low Earth orbit in 2027, setting future NASA Artemis missions up to return humanity to the Moon. \n\nLearn more about Artemis III: https://www.nasa.gov/mission/artemis-iii/",
        "publishedAt": "2026-06-10T00:54:38.000Z",
        "durationSeconds": 127.193,
        "thumbnailUrl": "https://scontent.fagc1-1.fna.fbcdn.net/v/t15.5256-10/719149300_1675536716897455_292426081350600923_n.jpg?stp=dst-jpg_tt6&cstp=mx720x405&ctp=s720x405&_nc_cat=110&ccb=1-7&_nc_sid=be8...",
        "videoUrl": "https://video.fagc1-1.fna.fbcdn.net/o1/v/t2/f2/m366/AQP-Z-CqEDushDYS5jpmhA9iX8oIbOZhr92oG3Wdy2sJFaqYdRq0BGyx1fay6WOwqylaGAGHAgYHh7Moy7o040YBl84wTMGQL7VG7K5xgzT-KA.mp4?_nc_cat=103&_...",
        "author": {
          "username": "NASA",
          "displayName": "NASA - National Aeronautics and Space Administration",
          "url": "https://www.facebook.com/NASA",
          "profileImage": "https://scontent.fagc1-2.fna.fbcdn.net/v/t39.30808-1/243095782_416661036495945_3843362260429099279_n.png?stp=cp0_dst-png&cstp=mx800x800&ctp=s80x80&_nc_cat=108&ccb=1-7&_nc_sid=2d3e1...",
          "verified": true
        },
        "engagement": {
          "views": 920000,
          "likes": 12349,
          "comments": 1093,
          "shares": 1300
        },
        "isVideo": true,
        "link": "https://www.nasa.gov/mission/artemis-iii/"
      },
      {
        "platform": "facebook",
        "url": "https://www.facebook.com/reel/301780235537207",
        "id": "826144325547612",
        "caption": "Say hi to the sky in July!\n\nA full moon starts the month, Jupiter and Saturn will be early birds and night owls, and while Venus and Mars go low in the west, Saturn will go high in the southern sky. The Red Planet will also cozy up with the star Regulus: http://go.nasa.gov/whatsup",
        "description": "Say hi to the sky in July!\n\nA full moon starts the month, Jupiter and Saturn will be early birds and night owls, and while Venus and Mars go low in the west, Saturn will go high in the southern sky. The Red Planet will also cozy up with the star Regulus: http://go.nasa.gov/whatsup",
        "publishedAt": "2023-06-30T20:01:28.000Z",
        "durationSeconds": 219.861,
        "thumbnailUrl": "https://scontent-iad3-2.xx.fbcdn.net/v/t15.5256-10/356554141_986264672797682_5974416453073306813_n.jpg?stp=dst-jpg_tt6&cstp=mx1280x720&ctp=s960x960&_nc_cat=111&ccb=1-7&_nc_sid=be83...",
        "videoUrl": "https://video-iad6-1.xx.fbcdn.net/o1/v/t2/f2/m266/AQOUIkXk2x1VD4EVBVejlA1xVbfTIA1arB34khhIAwmPsMnW6PMdZJHXwj4FqL7H9RXoOQO3fylBHDpYpihT9E0aSBMCkWNdHHY.mp4?strext=1&_nc_cat=100&_nc_s...",
        "author": {
          "username": "NASA",
          "displayName": "NASA - National Aeronautics and Space Administration",
          "url": "https://www.facebook.com/NASA",
          "profileImage": "https://scontent-iad3-2.xx.fbcdn.net/v/t39.30808-1/243095782_416661036495945_3843362260429099279_n.png?stp=cp0_dst-png&cstp=mx800x800&ctp=s40x40&_nc_cat=1&ccb=1-7&_nc_sid=2d3e12&_n...",
          "verified": true
        },
        "engagement": {
          "views": 82000,
          "likes": 5105,
          "comments": 146,
          "shares": 1000
        },
        "isVideo": true,
        "link": "http://go.nasa.gov/whatsup"
      },
      {
        "platform": "facebook",
        "url": "https://www.facebook.com/reel/576845513639244",
        "id": "10159527591111772",
        "caption": "🍂  Fall weather have you itching to step outside? You're in luck! This month, you'll have a chance to see several groupings of the Moon, planets, and stars at sunrise and sunset. That's not all – check out October skywatching tips from NASA Solar System Exploration: https://youtu.be/25XHe13OevA",
        "description": "🍂  Fall weather have you itching to step outside? You're in luck! This month, you'll have a chance to see several groupings of the Moon, planets, and stars at sunrise and sunset. That's not all – check out October skywatching tips from NASA Solar System Exploration: https://youtu.be/25XHe13OevA",
        "publishedAt": "2021-10-02T00:05:32.000Z",
        "durationSeconds": 190.037,
        "thumbnailUrl": "https://scontent-iad3-1.xx.fbcdn.net/v/t15.5256-10/243070133_576850643638731_8781286937420261312_n.jpg?stp=dst-jpg_tt6&cstp=mx1920x1080&ctp=s960x960&_nc_cat=104&ccb=1-7&_nc_sid=50c...",
        "videoUrl": "https://video-iad3-1.xx.fbcdn.net/o1/v/t2/f2/m266/AQMZIq7NX0AcsstdcTxi8_W5WUGU1qldPdwQX4Jv6uuKI_lbZwyJVP1zG3pGRRuBWu48jlnGluiUlyXPoKe9Q_nDnhDABjnUZVo.mp4?strext=1&_nc_cat=104&_nc_s...",
        "author": {
          "username": "NASA",
          "displayName": "NASA - National Aeronautics and Space Administration",
          "url": "https://www.facebook.com/NASA",
          "profileImage": "https://scontent-iad3-2.xx.fbcdn.net/v/t39.30808-1/243095782_416661036495945_3843362260429099279_n.png?stp=cp0_dst-png&cstp=mx800x800&ctp=s40x40&_nc_cat=1&ccb=1-7&_nc_sid=2d3e12&_n...",
          "verified": true
        },
        "engagement": {
          "views": 162000,
          "likes": 4566,
          "comments": 126,
          "shares": 836
        },
        "isVideo": true,
        "link": "https://youtu.be/25XHe13OevA"
      },
      {
        "platform": "facebook",
        "url": "https://www.facebook.com/reel/490611381989026",
        "id": "10159165907746772",
        "caption": "This week...\n\n🗳️ Confirming the nomination of our next administrator\n🌊 NASA's SpaceX Crew-1 mission set to undock from the International Space Station & splash down\n🌔 Remembering Apollo 11 and Gemini X astronaut Michael Collins\n\nWatch: youtu.be/PnEvu9jpkeE",
        "description": "This week...\n\n🗳️ Confirming the nomination of our next administrator\n🌊 NASA's SpaceX Crew-1 mission set to undock from the International Space Station & splash down\n🌔 Remembering Apollo 11 and Gemini X astronaut Michael Collins\n\nWatch: youtu.be/PnEvu9jpkeE",
        "publishedAt": "2021-05-01T23:26:01.000Z",
        "durationSeconds": 265.898,
        "thumbnailUrl": "https://scontent-iad6-1.xx.fbcdn.net/v/t15.5256-10/166283079_490612745322223_1081077117587264621_n.jpg?stp=dst-jpg_tt6&cstp=mx720x405&ctp=s720x405&_nc_cat=109&ccb=1-7&_nc_sid=50ce4...",
        "videoUrl": "https://video-iad3-1.xx.fbcdn.net/o1/v/t2/f2/m266/AQPrktfEwojyopOci8curfS5tVHNy1a2fCOTpa5FBgPslvhZGTrUpxCgOEUEDnOQDsPaN74tam6wOoyqqDa93JO92Cj8icJBOcM.mp4?strext=1&_nc_cat=110&_nc_s...",
        "author": {
          "username": "NASA",
          "displayName": "NASA - National Aeronautics and Space Administration",
          "url": "https://www.facebook.com/NASA",
          "profileImage": "https://scontent-iad3-2.xx.fbcdn.net/v/t39.30808-1/243095782_416661036495945_3843362260429099279_n.png?stp=cp0_dst-png&cstp=mx800x800&ctp=s40x40&_nc_cat=1&ccb=1-7&_nc_sid=2d3e12&_n...",
          "verified": true
        },
        "engagement": {
          "views": 52000,
          "likes": 1865,
          "comments": 103,
          "shares": 180
        },
        "isVideo": true,
        "link": "http://youtu.be/PnEvu9jpkeE"
      },
      {
        "platform": "facebook",
        "url": "https://www.facebook.com/reel/161382045774196",
        "id": "10159114517846772",
        "caption": "🌟 We've been busy.\n\n- President Joe Biden announces NASA funding request, our Ingenuity #MarsHelicopter preps for flight, and a new crew arrives at the International Space Station.\n\nAll that and more This Week @ NASA: https://youtu.be/66RYpY_adnw",
        "description": "🌟 We've been busy.\n\n- President Joe Biden announces NASA funding request, our Ingenuity #MarsHelicopter preps for flight, and a new crew arrives at the International Space Station.\n\nAll that and more This Week @ NASA: https://youtu.be/66RYpY_adnw",
        "publishedAt": "2021-04-10T01:13:23.000Z",
        "durationSeconds": 292.778,
        "thumbnailUrl": "https://scontent-iad3-1.xx.fbcdn.net/v/t15.5256-10/167839033_161383285774072_3853125686945722505_n.jpg?stp=dst-jpg_tt6&cstp=mx720x405&ctp=s720x405&_nc_cat=104&ccb=1-7&_nc_sid=50ce4...",
        "videoUrl": "https://video-iad6-1.xx.fbcdn.net/o1/v/t2/f2/m266/AQP_fXZEVPLTkMAKkZhBNif6MzZ7TBWFRps0njClmbV4Q7KTXgfQrPAlPzRFwJyOeHPJ1UgciMT5RiOjrPEnX6KZJwPUfZlzbSA.mp4?strext=1&_nc_cat=100&_nc_s...",
        "author": {
          "username": "NASA",
          "displayName": "NASA - National Aeronautics and Space Administration",
          "url": "https://www.facebook.com/NASA",
          "profileImage": "https://scontent-iad3-2.xx.fbcdn.net/v/t39.30808-1/243095782_416661036495945_3843362260429099279_n.png?stp=cp0_dst-png&cstp=mx800x800&ctp=s40x40&_nc_cat=1&ccb=1-7&_nc_sid=2d3e12&_n...",
          "verified": true
        },
        "engagement": {
          "views": 74000,
          "likes": 3447,
          "comments": 133,
          "shares": 340
        },
        "isVideo": true,
        "link": "https://youtu.be/66RYpY_adnw"
      },
      {
        "platform": "facebook",
        "url": "https://www.facebook.com/reel/292683338958803",
        "id": "10159096097556772",
        "caption": "This week…\n\n🧪 NASA Ames Research Center prepares the first long-duration biology experiment in deep space\n👩‍🔬 The International Space Station welcomes Robyn Gatens as its program director\n🛰️  A major component of our Psyche mission arrives at the NASA Jet Propulsion Laboratory\n\nWant details? Watch: youtu.be/g4tld6ppv7Q",
        "description": "This week…\n\n🧪 NASA Ames Research Center prepares the first long-duration biology experiment in deep space\n👩‍🔬 The International Space Station welcomes Robyn Gatens as its program director\n🛰️  A major component of our Psyche mission arrives at the NASA Jet Propulsion Laboratory\n\nWant details? Watch: youtu.be/g4tld6ppv7Q",
        "publishedAt": "2021-04-03T01:05:52.000Z",
        "durationSeconds": 177.322,
        "thumbnailUrl": "https://scontent-iad6-1.xx.fbcdn.net/v/t15.5256-10/151480839_292684862291984_7183282246301731065_n.jpg?stp=dst-jpg_tt6&cstp=mx720x405&ctp=s720x405&_nc_cat=102&ccb=1-7&_nc_sid=50ce4...",
        "videoUrl": "https://video-iad6-1.xx.fbcdn.net/o1/v/t2/f2/m266/AQNbHDfeXuZ4RrTQI-iY_6LUzVXLUdIydPY0GhL8xVjwTHbP-z6F5fJmxrLzHEs-QayHRP9bdadao2ai9wjv77-99tsqAhXAbY8.mp4?strext=1&_nc_cat=106&_nc_s...",
        "author": {
          "username": "NASA",
          "displayName": "NASA - National Aeronautics and Space Administration",
          "url": "https://www.facebook.com/NASA",
          "profileImage": "https://scontent-iad3-2.xx.fbcdn.net/v/t39.30808-1/243095782_416661036495945_3843362260429099279_n.png?stp=cp0_dst-png&cstp=mx800x800&ctp=s40x40&_nc_cat=1&ccb=1-7&_nc_sid=2d3e12&_n...",
          "verified": true
        },
        "engagement": {
          "views": 56000,
          "likes": 2925,
          "comments": 137,
          "shares": 304
        },
        "isVideo": true,
        "link": "http://youtu.be/g4tld6ppv7Q"
      },
      {
        "platform": "facebook",
        "url": "https://www.facebook.com/reel/452499129200583",
        "id": "10159065692406772",
        "caption": "This week...\n\n🔥 Our NASA's Artemis Program Moon rocket core stage fires up\n📰 A nomination announcement for the next NASA Administrator\n🛰️ A spacecraft relocates to make room for the next International Space Station crew\n\nWatch: youtu.be/nPmQbhlVeMs",
        "description": "This week...\n\n🔥 Our NASA's Artemis Program Moon rocket core stage fires up\n📰 A nomination announcement for the next NASA Administrator\n🛰️ A spacecraft relocates to make room for the next International Space Station crew\n\nWatch: youtu.be/nPmQbhlVeMs",
        "publishedAt": "2021-03-20T17:03:07.000Z",
        "durationSeconds": 252.693,
        "thumbnailUrl": "https://scontent.fosu2-1.fna.fbcdn.net/v/t15.5256-10/151732125_452501232533706_4250162638341106018_n.jpg?stp=dst-jpg_tt6&cstp=mx720x405&ctp=s720x405&_nc_cat=107&ccb=1-7&_nc_sid=50c...",
        "videoUrl": "https://video.fosu2-2.fna.fbcdn.net/o1/v/t2/f2/m366/AQN5raZBMqbux04LlwAz7U2GIpcszVwAZRA8y2LnkTEFZ-zShBYjfhRbk5_Y7EqnFd4LkhgPiQi9vHV2qAzXJ06tMu9GNrIs_FN_pPdHXyR3Og.mp4?_nc_cat=101&_...",
        "author": {
          "username": "NASA",
          "displayName": "NASA - National Aeronautics and Space Administration",
          "url": "https://www.facebook.com/NASA",
          "profileImage": "https://scontent.fosu2-1.fna.fbcdn.net/v/t39.30808-1/243095782_416661036495945_3843362260429099279_n.png?stp=cp0_dst-png&cstp=mx800x800&ctp=s40x40&_nc_cat=1&ccb=1-7&_nc_sid=2d3e12&...",
          "verified": true
        },
        "engagement": {
          "views": 12000,
          "likes": 838,
          "comments": 65,
          "shares": 156
        },
        "isVideo": true,
        "link": "http://youtu.be/nPmQbhlVeMs"
      }
    ]
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
    "username": "torvalds",
    "totalReturned": 5,
    "nextCursor": "2",
    "hasMore": true,
    "events": [
      {
        "id": "15224705962",
        "type": "PushEvent",
        "repo": "torvalds/linux",
        "actor": "torvalds",
        "createdAt": "2026-07-18T04:53:40Z"
      },
      {
        "id": "15206866323",
        "type": "PushEvent",
        "repo": "torvalds/linux",
        "actor": "torvalds",
        "createdAt": "2026-07-17T20:16:14Z"
      },
      {
        "id": "15194982279",
        "type": "PushEvent",
        "repo": "torvalds/linux",
        "actor": "torvalds",
        "createdAt": "2026-07-17T16:32:53Z"
      },
      {
        "id": "15192887403",
        "type": "PushEvent",
        "repo": "torvalds/linux",
        "actor": "torvalds",
        "createdAt": "2026-07-17T15:58:02Z"
      },
      {
        "id": "15143452538",
        "type": "PushEvent",
        "repo": "torvalds/linux",
        "actor": "torvalds",
        "createdAt": "2026-07-16T23:58:05Z"
      }
    ]
  },
  "github-contributions": {
    "username": "torvalds",
    "recentPublicEvents": 90,
    "recentEventTypes": [
      "IssueCommentEvent",
      "PullRequestEvent",
      "PushEvent"
    ],
    "publicRepositoriesSampled": 12,
    "starsAcrossSampledRepos": 252421
  },
  "github-followers": {
    "username": "torvalds",
    "totalReturned": 5,
    "nextCursor": "2",
    "hasMore": true,
    "followers": [
      {
        "login": "sprsquish",
        "url": "https://github.com/sprsquish",
        "avatar": "https://avatars.githubusercontent.com/u/206?v=4"
      },
      {
        "login": "pius",
        "url": "https://github.com/pius",
        "avatar": "https://avatars.githubusercontent.com/u/365?v=4"
      },
      {
        "login": "therubymug",
        "url": "https://github.com/therubymug",
        "avatar": "https://avatars.githubusercontent.com/u/389?v=4"
      },
      {
        "login": "crafterm",
        "url": "https://github.com/crafterm",
        "avatar": "https://avatars.githubusercontent.com/u/397?v=4"
      },
      {
        "login": "auser",
        "url": "https://github.com/auser",
        "avatar": "https://avatars.githubusercontent.com/u/529?v=4"
      }
    ]
  },
  "github-following": {
    "username": "gaearon",
    "totalReturned": 5,
    "nextCursor": "2",
    "hasMore": true,
    "following": [
      {
        "login": "mikeal",
        "url": "https://github.com/mikeal",
        "avatar": "https://avatars.githubusercontent.com/u/579?v=4"
      },
      {
        "login": "stefanpenner",
        "url": "https://github.com/stefanpenner",
        "avatar": "https://avatars.githubusercontent.com/u/1377?v=4"
      },
      {
        "login": "AArnott",
        "url": "https://github.com/AArnott",
        "avatar": "https://avatars.githubusercontent.com/u/3548?v=4"
      },
      {
        "login": "subtleGradient",
        "url": "https://github.com/subtleGradient",
        "avatar": "https://avatars.githubusercontent.com/u/4117?v=4"
      },
      {
        "login": "sansolovyov",
        "url": "https://github.com/sansolovyov",
        "avatar": "https://avatars.githubusercontent.com/u/6553?v=4"
      }
    ]
  },
  "github-pull-requests": {
    "repository": "vercel/next.js",
    "totalReturned": 5,
    "nextCursor": "2",
    "hasMore": true,
    "pullRequests": [
      {
        "id": 4101562593,
        "number": 96016,
        "title": "Upgrade React from `172742b4-20260716` to `81e442ea-20260721`",
        "state": "closed",
        "url": "https://github.com/vercel/next.js/pull/96016",
        "author": "vercel-release-bot",
        "createdAt": "2026-07-21T16:55:14Z",
        "updatedAt": "2026-07-21T17:25:32Z",
        "mergedAt": "2026-07-21T17:25:14Z"
      },
      {
        "id": 4101405905,
        "number": 96014,
        "title": "Fix Turbopack middleware matcher with i18n single locale",
        "state": "closed",
        "url": "https://github.com/vercel/next.js/pull/96014",
        "author": "eps1lon",
        "createdAt": "2026-07-21T16:33:19Z",
        "updatedAt": "2026-07-21T17:10:46Z",
        "mergedAt": "2026-07-21T16:46:57Z"
      },
      {
        "id": 4101405368,
        "number": 96013,
        "title": "Improve performance of validating MPA form submissions",
        "state": "closed",
        "url": "https://github.com/vercel/next.js/pull/96013",
        "author": "eps1lon",
        "createdAt": "2026-07-21T16:33:14Z",
        "updatedAt": "2026-07-21T17:11:36Z",
        "mergedAt": "2026-07-21T16:46:56Z"
      },
      {
        "id": 4101404758,
        "number": 96012,
        "title": "Enforce `serverActions.bodySizeLimit` for Server Actions in Edge runtime",
        "state": "closed",
        "url": "https://github.com/vercel/next.js/pull/96012",
        "author": "eps1lon",
        "createdAt": "2026-07-21T16:33:08Z",
        "updatedAt": "2026-07-21T17:11:36Z",
        "mergedAt": "2026-07-21T16:46:55Z"
      },
      {
        "id": 4101404245,
        "number": 96011,
        "title": "Set correct origin for internal redirects in custom server",
        "state": "closed",
        "url": "https://github.com/vercel/next.js/pull/96011",
        "author": "eps1lon",
        "createdAt": "2026-07-21T16:33:03Z",
        "updatedAt": "2026-07-21T17:07:39Z",
        "mergedAt": "2026-07-21T16:46:54Z"
      }
    ]
  },
  "github-repositories": {
    "username": "torvalds",
    "totalReturned": 5,
    "nextCursor": "2",
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
        "language": "C",
        "stars": 239734,
        "forks": 63487,
        "watchers": 239734,
        "openIssues": 3,
        "defaultBranch": "master",
        "homepage": null,
        "license": "NOASSERTION",
        "topics": [],
        "isFork": false,
        "isArchived": false,
        "ownerAvatar": "https://avatars.githubusercontent.com/u/1024025?v=4",
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
        "description": "A cross-platform, linkable library implementation of Git that you can use in your application.",
        "owner": "torvalds",
        "ownerUrl": "https://github.com/torvalds",
        "language": "C",
        "stars": 370,
        "forks": 28,
        "watchers": 370,
        "openIssues": 1,
        "defaultBranch": "main",
        "homepage": "https://libgit2.org/",
        "license": "NOASSERTION",
        "topics": [],
        "isFork": true,
        "isArchived": false,
        "ownerAvatar": "https://avatars.githubusercontent.com/u/1024025?v=4",
        "pushedAt": "2023-12-19T11:45:42Z",
        "createdAt": "2022-07-30T03:30:56Z",
        "updatedAt": "2026-07-18T17:03:41Z"
      },
      {
        "platform": "github",
        "type": "repository",
        "name": "uemacs",
        "fullName": "torvalds/uemacs",
        "url": "https://github.com/torvalds/uemacs",
        "description": "Random version of microemacs with my private modificatons",
        "owner": "torvalds",
        "ownerUrl": "https://github.com/torvalds",
        "language": "C",
        "stars": 2089,
        "forks": 313,
        "watchers": 2089,
        "openIssues": 15,
        "defaultBranch": "master",
        "homepage": null,
        "license": null,
        "topics": [],
        "isFork": false,
        "isArchived": false,
        "ownerAvatar": "https://avatars.githubusercontent.com/u/1024025?v=4",
        "pushedAt": "2026-02-25T19:15:47Z",
        "createdAt": "2018-01-17T22:32:21Z",
        "updatedAt": "2026-07-18T17:00:55Z"
      },
      {
        "platform": "github",
        "type": "repository",
        "name": "AudioNoise",
        "fullName": "torvalds/AudioNoise",
        "url": "https://github.com/torvalds/AudioNoise",
        "description": "Random digital audio effects",
        "owner": "torvalds",
        "ownerUrl": "https://github.com/torvalds",
        "language": "C",
        "stars": 4439,
        "forks": 210,
        "watchers": 4439,
        "openIssues": 33,
        "defaultBranch": "main",
        "homepage": null,
        "license": "GPL-2.0",
        "topics": [],
        "isFork": false,
        "isArchived": false,
        "ownerAvatar": "https://avatars.githubusercontent.com/u/1024025?v=4",
        "pushedAt": "2026-05-08T17:20:22Z",
        "createdAt": "2026-01-09T02:33:29Z",
        "updatedAt": "2026-07-18T13:26:30Z"
      },
      {
        "platform": "github",
        "type": "repository",
        "name": "HunspellColorize",
        "fullName": "torvalds/HunspellColorize",
        "url": "https://github.com/torvalds/HunspellColorize",
        "description": "Wrapper around 'less' to colorize spelling mistakes using Hunspell",
        "owner": "torvalds",
        "ownerUrl": "https://github.com/torvalds",
        "language": "C",
        "stars": 355,
        "forks": 15,
        "watchers": 355,
        "openIssues": 2,
        "defaultBranch": "main",
        "homepage": null,
        "license": "GPL-2.0",
        "topics": [],
        "isFork": false,
        "isArchived": false,
        "ownerAvatar": "https://avatars.githubusercontent.com/u/1024025?v=4",
        "pushedAt": "2026-01-19T20:23:09Z",
        "createdAt": "2026-01-18T19:57:03Z",
        "updatedAt": "2026-07-18T13:22:31Z"
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
    "language": "C",
    "stars": 239734,
    "forks": 63487,
    "watchers": 239734,
    "openIssues": 3,
    "defaultBranch": "master",
    "homepage": null,
    "license": "NOASSERTION",
    "topics": [],
    "isFork": false,
    "isArchived": false,
    "ownerAvatar": "https://avatars.githubusercontent.com/u/1024025?v=4",
    "pushedAt": "2026-07-18T04:53:39Z",
    "createdAt": "2011-09-04T22:48:12Z",
    "updatedAt": "2026-07-18T18:40:38Z"
  },
  "github-trending-developers": {
    "query": "followers:>1000",
    "totalReturned": 5,
    "developers": [
      {
        "login": "torvalds",
        "url": "https://github.com/torvalds",
        "avatar": "https://avatars.githubusercontent.com/u/1024025?v=4",
        "score": 1.0
      },
      {
        "login": "karpathy",
        "url": "https://github.com/karpathy",
        "avatar": "https://avatars.githubusercontent.com/u/241138?v=4",
        "score": 1.0
      },
      {
        "login": "claude",
        "url": "https://github.com/claude",
        "avatar": "https://avatars.githubusercontent.com/u/81847?v=4",
        "score": 1.0
      },
      {
        "login": "openai",
        "url": "https://github.com/openai",
        "avatar": "https://avatars.githubusercontent.com/u/14957082?v=4",
        "score": 1.0
      },
      {
        "login": "microsoft",
        "url": "https://github.com/microsoft",
        "avatar": "https://avatars.githubusercontent.com/u/6154722?v=4",
        "score": 1.0
      }
    ]
  },
  "github-trending-repositories": {
    "query": "stars:>1000 language:python",
    "totalReturned": 5,
    "repositories": [
      {
        "platform": "github",
        "type": "repository",
        "name": "public-apis",
        "fullName": "public-apis/public-apis",
        "url": "https://github.com/public-apis/public-apis",
        "description": "A collective list of free APIs",
        "owner": "public-apis",
        "ownerUrl": "https://github.com/public-apis",
        "language": "Python",
        "stars": 451178,
        "forks": 49637,
        "watchers": 451178,
        "openIssues": 1569,
        "defaultBranch": "master",
        "homepage": "https://APILayer.com/?utm_source=Github&utm_medium=Referral&utm_campaign=Public-apis-repo",
        "license": "MIT",
        "topics": [
          "api",
          "apis",
          "dataset",
          "development",
          "free"
        ],
        "isFork": false,
        "isArchived": false,
        "ownerAvatar": "https://avatars.githubusercontent.com/u/51121562?v=4",
        "pushedAt": "2026-07-13T15:58:22Z",
        "createdAt": "2016-03-20T23:49:42Z",
        "updatedAt": "2026-07-18T18:42:31Z"
      },
      {
        "platform": "github",
        "type": "repository",
        "name": "free-programming-books",
        "fullName": "EbookFoundation/free-programming-books",
        "url": "https://github.com/EbookFoundation/free-programming-books",
        "description": ":books: Freely available programming books",
        "owner": "EbookFoundation",
        "ownerUrl": "https://github.com/EbookFoundation",
        "language": "Python",
        "stars": 392415,
        "forks": 66541,
        "watchers": 392415,
        "openIssues": 75,
        "defaultBranch": "main",
        "homepage": "https://ebookfoundation.github.io/free-programming-books/",
        "license": "CC-BY-4.0",
        "topics": [
          "books",
          "education",
          "hacktoberfest",
          "list",
          "resource"
        ],
        "isFork": false,
        "isArchived": false,
        "ownerAvatar": "https://avatars.githubusercontent.com/u/14127308?v=4",
        "pushedAt": "2026-07-18T10:02:18Z",
        "createdAt": "2013-10-11T06:50:37Z",
        "updatedAt": "2026-07-18T18:39:42Z"
      },
      {
        "platform": "github",
        "type": "repository",
        "name": "system-design-primer",
        "fullName": "donnemartin/system-design-primer",
        "url": "https://github.com/donnemartin/system-design-primer",
        "description": "Learn how to design large-scale systems. Prep for the system design interview.  Includes Anki flashcards.",
        "owner": "donnemartin",
        "ownerUrl": "https://github.com/donnemartin",
        "language": "Python",
        "stars": 358093,
        "forks": 57258,
        "watchers": 358093,
        "openIssues": 572,
        "defaultBranch": "master",
        "homepage": null,
        "license": "NOASSERTION",
        "topics": [
          "design",
          "design-patterns",
          "design-system",
          "development",
          "interview"
        ],
        "isFork": false,
        "isArchived": false,
        "ownerAvatar": "https://avatars.githubusercontent.com/u/5458997?v=4",
        "pushedAt": "2026-03-20T01:52:19Z",
        "createdAt": "2017-02-26T16:15:28Z",
        "updatedAt": "2026-07-18T18:38:41Z"
      },
      {
        "platform": "github",
        "type": "repository",
        "name": "awesome-python",
        "fullName": "vinta/awesome-python",
        "url": "https://github.com/vinta/awesome-python",
        "description": "An opinionated list of Python frameworks, libraries, tools, and resources",
        "owner": "vinta",
        "ownerUrl": "https://github.com/vinta",
        "language": "Python",
        "stars": 308902,
        "forks": 28346,
        "watchers": 308902,
        "openIssues": 19,
        "defaultBranch": "master",
        "homepage": "https://awesome-python.com/",
        "license": "NOASSERTION",
        "topics": [
          "awesome",
          "collections",
          "python",
          "python-frameworks",
          "python-libraries"
        ],
        "isFork": false,
        "isArchived": false,
        "ownerAvatar": "https://avatars.githubusercontent.com/u/652070?v=4",
        "pushedAt": "2026-07-17T06:08:49Z",
        "createdAt": "2014-06-27T21:00:06Z",
        "updatedAt": "2026-07-18T18:34:53Z"
      },
      {
        "platform": "github",
        "type": "repository",
        "name": "project-based-learning",
        "fullName": "practical-tutorials/project-based-learning",
        "url": "https://github.com/practical-tutorials/project-based-learning",
        "description": "Curated list of project-based tutorials",
        "owner": "practical-tutorials",
        "ownerUrl": "https://github.com/practical-tutorials",
        "language": "Python",
        "stars": 273888,
        "forks": 35314,
        "watchers": 273888,
        "openIssues": 290,
        "defaultBranch": "master",
        "homepage": null,
        "license": "MIT",
        "topics": [
          "beginner-project",
          "cpp",
          "golang",
          "javascript",
          "project"
        ],
        "isFork": false,
        "isArchived": false,
        "ownerAvatar": "https://avatars.githubusercontent.com/u/89421154?v=4",
        "pushedAt": "2026-07-13T10:06:14Z",
        "createdAt": "2017-04-12T05:07:46Z",
        "updatedAt": "2026-07-18T18:42:23Z"
      }
    ]
  },
  "github-user": {
    "platform": "github",
    "type": "user",
    "login": "getify",
    "id": 150330,
    "nodeId": "MDQ6VXNlcjE1MDMzMA==",
    "url": "https://github.com/getify",
    "apiUrl": "https://api.github.com/users/getify",
    "name": "Kyle Simpson",
    "company": "Getify Solutions",
    "blog": "http://getify.me",
    "location": "Austin, TX",
    "email": null,
    "bio": "Kyle Simpson is a Human-Centric Technologist. He's fighting for the people behind the pixels.",
    "avatar": "https://avatars.githubusercontent.com/u/150330?v=4",
    "publicRepos": 74,
    "publicGists": 411,
    "followers": 45221,
    "following": 3,
    "twitterUsername": null,
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
      },
      {
        "platform": "google_ad_library",
        "id": "CR11855191862560161793",
        "url": "https://adstransparency.google.com/advertiser/AR16735076323512287233/creative/CR11855191862560161793",
        "adFormat": "image",
        "firstShown": "2022-11-30T14:47:41.000Z",
        "lastShown": "2026-07-26T12:29:26.000Z",
        "advertiser": {
          "id": "AR16735076323512287233",
          "name": "Nike, Inc.",
          "url": "https://adstransparency.google.com/advertiser/AR16735076323512287233"
        },
        "media": [
          "https://tpc.googlesyndication.com/archive/simgad/10582874225811561496"
        ]
      },
      {
        "platform": "google_ad_library",
        "id": "CR10403323179404623873",
        "url": "https://adstransparency.google.com/advertiser/AR16735076323512287233/creative/CR10403323179404623873",
        "adFormat": "image",
        "firstShown": "2022-11-30T14:47:37.000Z",
        "lastShown": "2026-07-26T12:28:37.000Z",
        "advertiser": {
          "id": "AR16735076323512287233",
          "name": "Nike, Inc.",
          "url": "https://adstransparency.google.com/advertiser/AR16735076323512287233"
        },
        "media": [
          "https://tpc.googlesyndication.com/archive/simgad/11551318734521008902"
        ]
      },
      {
        "platform": "google_ad_library",
        "id": "CR15203746965809528833",
        "url": "https://adstransparency.google.com/advertiser/AR16735076323512287233/creative/CR15203746965809528833",
        "adFormat": "image",
        "firstShown": "2022-11-30T15:11:07.000Z",
        "lastShown": "2026-07-26T12:27:34.000Z",
        "advertiser": {
          "id": "AR16735076323512287233",
          "name": "Nike, Inc.",
          "url": "https://adstransparency.google.com/advertiser/AR16735076323512287233"
        },
        "media": [
          "https://tpc.googlesyndication.com/archive/simgad/12062534195836224920"
        ]
      }
    ]
  },
  "instagram-basic-profile": {
    "id": "314216",
    "pk": "314216",
    "username": "zuck",
    "full_name": "Mark Zuckerberg",
    "biography": "I build stuff",
    "biography_with_entities": {
      "raw_text": "I build stuff",
      "entities": []
    },
    "follower_count": 16944276,
    "following_count": 620,
    "media_count": 436,
    "highlight_reel_count": 0,
    "is_private": false,
    "is_verified": true,
    "is_business": false,
    "is_professional_account": true,
    "should_show_category": false,
    "profile_pic_url": "https://instagram.fscl1-1.fna.fbcdn.net/v/t51.82787-19/550234512_18532404670058217_8758519395071163708_n.jpg?stp=dst-jpg_s150x150_tt6&efg=eyJ2ZW5jb2RlX3RhZyI6InByb2ZpbGVfcGljLmRqYW5nby4xMDgwLmMyIn0&_nc_ht=instagram.fscl1-1.fna.fbcdn.net&_nc_cat=1&_nc_oc=Q6cZ2gEGmyGBjnyLEtHbhEtAZrW4crvPeMpPLfp8Yy0Lrfn0_vQhEHyYh23QJ00H6DVK_VM&_nc_ohc=Y_4zRJVeNMAQ7kNvwFRwYxd&_nc_gid=Ge4vi-V9UTLD2FUMCnmsKw&edm=AOQ1c0wBAAAA&ccb=7-5&oh=00_AQD9_gXgZJvog7nIb0Ul7nHSl7_wAAGx9yOrW67giUoqyA&oe=6A61336D&_nc_sid=8b3546",
    "hd_profile_pic_url_info": {
      "url": "https://instagram.fscl1-1.fna.fbcdn.net/v/t51.82787-19/550234512_18532404670058217_8758519395071163708_n.jpg?stp=dst-jpg_s320x320_tt6&efg=eyJ2ZW5jb2RlX3RhZyI6InByb2ZpbGVfcGljLmRqYW5nby4xMDgwLmMyIn0&_nc_ht=instagram.fscl1-1.fna.fbcdn.net&_nc_cat=1&_nc_oc=Q6cZ2gEGmyGBjnyLEtHbhEtAZrW4crvPeMpPLfp8Yy0Lrfn0_vQhEHyYh23QJ00H6DVK_VM&_nc_ohc=Y_4zRJVeNMAQ7kNvwFRwYxd&_nc_gid=Ge4vi-V9UTLD2FUMCnmsKw&edm=AOQ1c0wBAAAA&ccb=7-5&oh=00_AQAXB3DwpL7ZK8fs3tlWiQ-bPK8ZOOXOWiaMKyvsZNzjbw&oe=6A61336D&_nc_sid=8b3546"
    },
    "fbid_v2": "17841401746480004",
    "pronouns": [],
    "bio_links": [],
    "is_embeds_disabled": false,
    "is_regulated_c18": false,
    "show_account_transparency_details": true,
    "show_text_post_app_badge": true,
    "remove_message_entrypoint": false
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
          "comments": 149
        },
        "hashtags": [
          "NASA",
          "Sun",
          "TotalSolarEclipse2026"
        ],
        "mentions": []
      },
      {
        "platform": "instagram",
        "url": "https://www.instagram.com/p/DbYaLffE2DD/",
        "id": "3952023811948503235",
        "postType": "Sidecar",
        "productType": "",
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
          "comments": 177
        },
        "hashtags": [
          "NASA",
          "FlightSuit",
          "Aircraft"
        ],
        "mentions": [
          "astro_fuhrmann",
          "astro_lawler",
          "ISS"
        ]
      },
      {
        "platform": "instagram",
        "url": "https://www.instagram.com/p/DbTmwYKFkZo/",
        "id": "3950671748375397992",
        "postType": "Image",
        "productType": "",
        "caption": "Hi, Earth! 📱\n\nAfter eight months living and working aboard the @ISS, NASA astronaut Chris Williams returned to Earth on Sunday, July 26.⁣\n\nIn his first space mission, he worked on many experiments and tech demonstrations, including new cancer treatment research and manufacturing materials used in computers and electronics. In addition, he completed two spacewalks – another first (and second)!⁣\n\nNow back on our home planet, Chris will readjust to gravity and the sights and sounds of Earth. In the coming weeks, he'll talk about his experience on the space station. Keep an eye on our website for more details.⁣\n\n#NASA #Space #Astronaut⁣\n\nCredit: NASA",
        "description": "Hi, Earth! 📱\n\nAfter eight months living and working aboard the @ISS, NASA astronaut Chris Williams returned to Earth on Sunday, July 26.⁣\n\nIn his first space mission, he worked on many experiments and tech demonstrations, including new cancer treatment research and manufacturing materials used in computers and electronics. In addition, he completed two spacewalks – another first (and second)!⁣\n\nNow back on our home planet, Chris will readjust to gravity and the sights and sounds of Earth. In the coming weeks, he'll talk about his experience on the space station. Keep an eye on our website for more details.⁣\n\n#NASA #Space #Astronaut⁣\n\nCredit: NASA",
        "publishedAt": "2026-07-27T18:26:43Z",
        "thumbnailUrl": "https://scontent-lga3-1.cdninstagram.com/v/t51.82787-15/758518372_18631237048049152_6990008620519916877_n.jpg?stp=dst-jpg_e35_s1080x1080_sh2.08_tt6&_nc_ht=scontent-lga3-1.cdninstagram.com&_nc_cat=1&_nc_oc=Q6cZ2gGam1aPbxqnPf0b0JKP7tArIHvIrXRHft307eWE7UMXS_pr6S4N6-Dm4L-cNp1JOIg&_nc_ohc=mOwJ4LaCSlQQ7kNvwGFCuKv&_nc_gid=EJ9eFsuBV8RTUu0BGi0U6A&edm=AOQ1c0wBAAAA&ccb=7-5&oh=00_AQALC5Vxtz-WSFAKj6fVWMrEqBybs50EbXtNMKYtLeqRnQ&oe=6A6FF2CC&_nc_sid=8b3546",
        "author": {
          "username": "nasa",
          "displayName": "NASA",
          "url": "https://instagram.com/nasa",
          "followers": 104263202,
          "verified": true,
          "profileImage": "https://scontent-lga3-1.cdninstagram.com/v/t51.2885-19/29090066_159271188110124_1152068159029641216_n.jpg?stp=dst-jpg_s320x320_tt6&efg=eyJ2ZW5jb2RlX3RhZyI6InByb2ZpbGVfcGljLmRqYW5nby4xMDgwLmMyIn0&_nc_ht=scontent-lga3-1.cdninstagram.com&_nc_cat=1&_nc_oc=Q6cZ2gGam1aPbxqnPf0b0JKP7tArIHvIrXRHft307eWE7UMXS_pr6S4N6-Dm4L-cNp1JOIg&_nc_ohc=sUQGBsPKUTMQ7kNvwEjppQT&_nc_gid=EJ9eFsuBV8RTUu0BGi0U6A&edm=AOQ1c0wBAAAA&ccb=7-5&oh=00_AQABrOC8fhriT4lnoxQ6_A9newYDo18-mqvkuOv21yGkUQ&oe=6A701229&_nc_sid=8b3546"
        },
        "engagement": {
          "likes": 62909,
          "comments": 621
        },
        "hashtags": [
          "NASA",
          "Space",
          "Astronaut"
        ],
        "mentions": [
          "ISS"
        ]
      },
      {
        "platform": "instagram",
        "url": "https://www.instagram.com/reel/DbL6n0ggXDZ/",
        "id": "3948507321457537241",
        "postType": "Video",
        "productType": "clips",
        "caption": "Sound on!\n\nSonifications take images from across the universe and turn them into music, with different notes corresponding to different frequencies of light.\n\nThis sonification of NGC 4736, a bright spiral galaxy found 16 million light-years from Earth, sweeps clockwise around the image. As it reaches neutron stars and black holes (spotted by our @nasachandraxray telescope), it turns them into pitched tones on a glass marimba. Other sources of light are represented by piano notes or a low, ethereal drone.\n\n#NASA #Space #MusicLife",
        "description": "Sound on!\n\nSonifications take images from across the universe and turn them into music, with different notes corresponding to different frequencies of light.\n\nThis sonification of NGC 4736, a bright spiral galaxy found 16 million light-years from Earth, sweeps clockwise around the image. As it reaches neutron stars and black holes (spotted by our @nasachandraxray telescope), it turns them into pitched tones on a glass marimba. Other sources of light are represented by piano notes or a low, ethereal drone.\n\n#NASA #Space #MusicLife",
        "publishedAt": "2026-07-24T18:46:42Z",
        "thumbnailUrl": "https://scontent-lga3-1.cdninstagram.com/v/t51.82787-15/753557824_18630272896049152_5085604310932259746_n.jpg?stp=dst-jpg_e15_fr_s1080x1080_tt6&_nc_ht=scontent-lga3-1.cdninstagram.com&_nc_cat=1&_nc_oc=Q6cZ2gGam1aPbxqnPf0b0JKP7tArIHvIrXRHft307eWE7UMXS_pr6S4N6-Dm4L-cNp1JOIg&_nc_ohc=JXie426E2AIQ7kNvwGlg-Up&_nc_gid=EJ9eFsuBV8RTUu0BGi0U6A&edm=AOQ1c0wBAAAA&ccb=7-5&oh=00_AQDfQIt5ChHfvw1haYF6Huy5Tm0DHMMWjvyPqrGpi7_tTA&oe=6A7021E6&_nc_sid=8b3546",
        "videoUrl": "https://scontent-lga3-1.cdninstagram.com/o1/v/t2/f2/m86/AQPmdAz9D4QKeO_RBry8I2ja9L4hPZ0xY85OXT_W30_E9E5cOr_RoiOcZHVX6a9Fvjg8qStE7fTYF0T9sgmzJyxUs6ay7J6Bvu0fLb4.mp4?_nc_cat=109&_nc_sid=5e9851&_nc_ht=scontent-lga3-1.cdninstagram.com&_nc_ohc=9d9-4rCXivsQ7kNvwFJggA4&efg=eyJ2ZW5jb2RlX3RhZyI6Inhwdl9wcm9ncmVzc2l2ZS5JTlNUQUdSQU0uQ0xJUFMuQzMuNzIwLmRhc2hfYmFzZWxpbmVfMV92MSIsInhwdl9hc3NldF9pZCI6MTg2MzAyNzI3NzAwNDkxNTIsImFzc2V0X2FnZV9kYXlzIjo0LCJ2aV91c2VjYXNlX2lkIjoxMDA5OSwiZHVyYXRpb25fcyI6MzQsInVybGdlbl9zb3VyY2UiOiJ3d3cifQ%3D%3D&ccb=17-1&vs=53b7030fc1cf7a2a&_nc_vs=HBksFQIYUmlnX3hwdl9yZWVsc19wZXJtYW5lbnRfc3JfcHJvZC9CODQ0NkUzMkVERDMxMDM4NjFFNDk1OTc4NjM0NzFCQl92aWRlb19kYXNoaW5pdC5tcDQVAALIARIAFQIYUWlnX3hwdl9wbGFjZW1lbnRfcGVybWFuZW50X3YyL0JCNEUzREJGMERFRTc3RDY4Nzc5QzA5QzRFQUVCNzkxX2F1ZGlvX2Rhc2hpbml0Lm1wNBUCAsgBEgAoABgAGwKIB3VzZV9vaWwBMRJwcm9ncmVzc2l2ZV9yZWNpcGUBMRUAACaAkrjozIiYQhUCKAJDMywXQEEAAAAAAAAYEmRhc2hfYmFzZWxpbmVfMV92MREAdf4HZeadAQA&_nc_gid=EJ9eFsuBV8RTUu0BGi0U6A&_nc_ss=7a22e&_nc_zt=28&oh=00_AQBlTouRSWFhKYJdRHR9XtTa3aGhEHVVC578ay32Lrz7mQ&oe=6A6C2F2A",
        "author": {
          "username": "nasa",
          "displayName": "NASA",
          "url": "https://instagram.com/nasa",
          "followers": 104263202,
          "verified": true,
          "profileImage": "https://scontent-lga3-1.cdninstagram.com/v/t51.2885-19/29090066_159271188110124_1152068159029641216_n.jpg?stp=dst-jpg_s320x320_tt6&efg=eyJ2ZW5jb2RlX3RhZyI6InByb2ZpbGVfcGljLmRqYW5nby4xMDgwLmMyIn0&_nc_ht=scontent-lga3-1.cdninstagram.com&_nc_cat=1&_nc_oc=Q6cZ2gGam1aPbxqnPf0b0JKP7tArIHvIrXRHft307eWE7UMXS_pr6S4N6-Dm4L-cNp1JOIg&_nc_ohc=sUQGBsPKUTMQ7kNvwEjppQT&_nc_gid=EJ9eFsuBV8RTUu0BGi0U6A&edm=AOQ1c0wBAAAA&ccb=7-5&oh=00_AQABrOC8fhriT4lnoxQ6_A9newYDo18-mqvkuOv21yGkUQ&oe=6A701229&_nc_sid=8b3546"
        },
        "engagement": {
          "views": 112487,
          "likes": 485567,
          "comments": 2174
        },
        "hashtags": [
          "NASA",
          "Space",
          "MusicLife"
        ],
        "mentions": [
          "nasachandraxray"
        ]
      },
      {
        "platform": "instagram",
        "url": "https://www.instagram.com/p/DbJML3hGVVJ/",
        "id": "3947740140450436425",
        "postType": "Image",
        "productType": "",
        "caption": "I spy… something dark 🔎\n\nIn this photo snapped by @NASAHubble, this ghostly cloud appears to have a dark ring around the central galaxy cluster. That ring is evidence of dark matter, the invisible glue that holds the universe together.\n\nVisible matter, or the stuff we can see, makes up only 5% of the universe. Dark matter makes up over five times as much of the universe, but we can’t see it because it doesn’t emit, reflect, or absorb any light. However, dark matter interacts with ordinary visible matter through gravity, so that’s how scientists detect it.\n\nThe exact nature of this abundant, invisible substance is still unknown, but our soon-to-launch Nancy Grace Roman Space Telescope aims to shed light on the subject. With a field of view over 100 times that of @NASAHubble’s, Roman’s enormous perspective will measure the distribution of both visible and dark matter in hundreds of millions of galaxies, helping scientists understand how dark matter has evolved in the universe.\n\nCredit: NASA\n\n#NASA #Roman #DarkMatter",
        "description": "I spy… something dark 🔎\n\nIn this photo snapped by @NASAHubble, this ghostly cloud appears to have a dark ring around the central galaxy cluster. That ring is evidence of dark matter, the invisible glue that holds the universe together.\n\nVisible matter, or the stuff we can see, makes up only 5% of the universe. Dark matter makes up over five times as much of the universe, but we can’t see it because it doesn’t emit, reflect, or absorb any light. However, dark matter interacts with ordinary visible matter through gravity, so that’s how scientists detect it.\n\nThe exact nature of this abundant, invisible substance is still unknown, but our soon-to-launch Nancy Grace Roman Space Telescope aims to shed light on the subject. With a field of view over 100 times that of @NASAHubble’s, Roman’s enormous perspective will measure the distribution of both visible and dark matter in hundreds of millions of galaxies, helping scientists understand how dark matter has evolved in the universe.\n\nCredit: NASA\n\n#NASA #Roman #DarkMatter",
        "publishedAt": "2026-07-23T17:22:07Z",
        "thumbnailUrl": "https://scontent-lga3-3.cdninstagram.com/v/t51.82787-15/753267928_18629947399049152_7357722023007611269_n.jpg?stp=dst-jpg_e35_s1080x1080_sh2.08_tt6&_nc_ht=scontent-lga3-3.cdninstagram.com&_nc_cat=104&_nc_oc=Q6cZ2gGam1aPbxqnPf0b0JKP7tArIHvIrXRHft307eWE7UMXS_pr6S4N6-Dm4L-cNp1JOIg&_nc_ohc=MQe2qmLv2HYQ7kNvwE5Esqz&_nc_gid=EJ9eFsuBV8RTUu0BGi0U6A&edm=AOQ1c0wBAAAA&ccb=7-5&oh=00_AQD7dv2bh-N_LgtmhGSmO2HtU7k6W4aSI8a_AWFuJmJURg&oe=6A7007EC&_nc_sid=8b3546",
        "author": {
          "username": "nasa",
          "displayName": "NASA",
          "url": "https://instagram.com/nasa",
          "followers": 104263202,
          "verified": true,
          "profileImage": "https://scontent-lga3-1.cdninstagram.com/v/t51.2885-19/29090066_159271188110124_1152068159029641216_n.jpg?stp=dst-jpg_s320x320_tt6&efg=eyJ2ZW5jb2RlX3RhZyI6InByb2ZpbGVfcGljLmRqYW5nby4xMDgwLmMyIn0&_nc_ht=scontent-lga3-1.cdninstagram.com&_nc_cat=1&_nc_oc=Q6cZ2gGam1aPbxqnPf0b0JKP7tArIHvIrXRHft307eWE7UMXS_pr6S4N6-Dm4L-cNp1JOIg&_nc_ohc=sUQGBsPKUTMQ7kNvwEjppQT&_nc_gid=EJ9eFsuBV8RTUu0BGi0U6A&edm=AOQ1c0wBAAAA&ccb=7-5&oh=00_AQABrOC8fhriT4lnoxQ6_A9newYDo18-mqvkuOv21yGkUQ&oe=6A701229&_nc_sid=8b3546"
        },
        "engagement": {
          "likes": 156307,
          "comments": 846
        },
        "hashtags": [
          "NASA",
          "Roman",
          "DarkMatter"
        ],
        "mentions": [
          "NASAHubble",
          "NASAHubble"
        ]
      }
    ],
    "nextCursor": "3947740140450436425_528817151",
    "hasMore": true
  },
  "instagram-channel-reels": {
    "url": "https://www.instagram.com/cristiano/",
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
          "comments": 257545
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
          "comments": 341631
        },
        "hashtags": [],
        "mentions": []
      },
      {
        "platform": "instagram",
        "url": "https://www.instagram.com/reel/DaSz9gXgFla/",
        "id": "3932433951662037338",
        "postType": "Video",
        "productType": "clips",
        "caption": "Before the awards.\nBefore the leagues.\nBefore the globe wore 7.\n\nFrom a small island in the Atlantic to the world stage, @Cristiano shattered records along the way — proving that where you start doesn't determine where you finish.",
        "description": "Before the awards.\nBefore the leagues.\nBefore the globe wore 7.\n\nFrom a small island in the Atlantic to the world stage, @Cristiano shattered records along the way — proving that where you start doesn't determine where you finish.",
        "publishedAt": "2026-07-02T14:31:49Z",
        "durationSeconds": 30.037,
        "thumbnailUrl": "https://scontent-ham3-1.cdninstagram.com/v/t51.82787-15/730475969_18608185318016159_1358384897120211657_n.jpg?...",
        "videoUrl": "https://scontent-ham3-1.cdninstagram.com/o1/v/t2/f2/m86/AQNsM4Cz3wiCY9HbNolCc-oVALHL50LiQGdb_f2isa618TZUlDdGGH0I3Qsw1450pwkL_aY6PiYy_3r221K5nHutIHQ78p8-NvuDaG0.mp4?...",
        "author": {
          "username": "whoop",
          "displayName": "WHOOP",
          "url": "https://instagram.com/whoop",
          "verified": true,
          "profileImage": "https://scontent-ham3-1.cdninstagram.com/v/t51.82787-19/712306922_18597675370016159_2436545821614461300_n.jpg?..."
        },
        "engagement": {
          "views": 103164783,
          "likes": 5014316,
          "comments": 30005
        },
        "hashtags": [],
        "mentions": [
          "Cristiano"
        ]
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
        "likeCount": 0,
        "publishedAt": "2026-07-01T07:49:55.000Z",
        "replyCount": 0
      },
      {
        "id": "18083281052356825",
        "url": "https://www.instagram.com/p/DZFqdAxlkUG/c/18083281052356825",
        "text": "Hoppers moment",
        "author": "redkidane",
        "authorAvatarUrl": "https://scontent-atl3-3.cdninstagram.com/v/t51.82787-19/686139918_18580722691039268_2096250779414967342_n.jpg?stp=dst-jpg_s150x150_tt6&_nc_cat=111&ccb=7-5&_nc_sid=f7ccc5&efg=eyJ2ZW5jb2RlX3RhZyI6InByb2ZpbGVfcGljLnd3dy4xMDgwLkMzIn0%3D&_nc_ohc=5ruLx7cECMUQ7kNvwEw883n&_nc_oc=Adp-jPSBc0mkti93nI0FR-bBBq_hLclzrrRqC70JO7HsI47RMZeVJF159wD-BivgyvM&_nc_zt=24&_nc_ht=scontent-atl3-3.cdninstagram.com&_nc_gid=P5Abwq2UvTMDXokKzG45Jg&_nc_ss=72a8c&oh=00_AQD-UwNDAfkrNje1f_2dMoh9ax8alu8E-J44od76mYrB5g&oe=6A4DA11B",
        "authorIsVerified": false,
        "likeCount": 0,
        "publishedAt": "2026-06-24T23:45:01.000Z",
        "replyCount": 0
      },
      {
        "id": "18168040507426702",
        "url": "https://www.instagram.com/p/DZFqdAxlkUG/c/18168040507426702",
        "text": "Dream job",
        "author": "atelier_analog",
        "authorAvatarUrl": "https://scontent-atl3-2.cdninstagram.com/v/t51.82787-19/653415034_18147464455460951_7280452665537162423_n.jpg?stp=dst-jpg_s150x150_tt6&_nc_cat=105&ccb=7-5&_nc_sid=f7ccc5&efg=eyJ2ZW5jb2RlX3RhZyI6InByb2ZpbGVfcGljLnd3dy4xMDgwLkMzIn0%3D&_nc_ohc=sgO1NkmgyHkQ7kNvwEs4IhC&_nc_oc=AdqrU2fSq-MftowsOT89mq35G26EUb_ccYTWEERkb4STtTgH5l_hPIHV-S-jHatax1I&_nc_zt=24&_nc_ht=scontent-atl3-2.cdninstagram.com&_nc_gid=P5Abwq2UvTMDXokKzG45Jg&_nc_ss=72a8c&oh=00_AQDxOoCyfhth2CWXFvEhPQTpVHxEn_SStaC3RmL4tIbTww&oe=6A4DBCAD",
        "authorIsVerified": false,
        "likeCount": 0,
        "publishedAt": "2026-06-20T04:32:16.000Z",
        "replyCount": 0
      },
      {
        "id": "18602523952011665",
        "url": "https://www.instagram.com/p/DZFqdAxlkUG/c/18602523952011665",
        "text": "Creeeepy…",
        "author": "lildazysnout",
        "authorAvatarUrl": "https://scontent-atl3-3.cdninstagram.com/v/t51.82787-19/540687345_17845526541559863_1472397767289735179_n.jpg?stp=dst-jpg_s150x150_tt6&_nc_cat=110&ccb=7-5&_nc_sid=f7ccc5&efg=eyJ2ZW5jb2RlX3RhZyI6InByb2ZpbGVfcGljLnd3dy42NjUuQzMifQ%3D%3D&_nc_ohc=OdhOK4PpFmMQ7kNvwGiQiHx&_nc_oc=AdoFCPMVJaPuhDSavbyq8hrb1Y12w-ytKfAnBwwCGQmw4pIe1HihjTLmnT9UL-6fQUE&_nc_zt=24&_nc_ht=scontent-atl3-3.cdninstagram.com&_nc_gid=P5Abwq2UvTMDXokKzG45Jg&_nc_ss=72a8c&oh=00_AQDntuUMWuF4uoh4NfqJGaRRjB7WNiwPa6KP9SBj0OUOJQ&oe=6A4DACC3",
        "authorIsVerified": false,
        "likeCount": 0,
        "publishedAt": "2026-06-18T04:44:36.000Z",
        "replyCount": 0
      },
      {
        "id": "18065034263460905",
        "url": "https://www.instagram.com/p/DZFqdAxlkUG/c/18065034263460905",
        "text": "Imagine running into them in the forest with ZERO explanation …",
        "author": "fillehippievegetalienne",
        "authorAvatarUrl": "https://scontent-atl3-1.cdninstagram.com/v/t51.82787-19/545026581_18527383597050844_8655935088175060424_n.jpg?stp=dst-jpg_s150x150_tt6&_nc_cat=100&ccb=7-5&_nc_sid=f7ccc5&efg=eyJ2ZW5jb2RlX3RhZyI6InByb2ZpbGVfcGljLnd3dy45NjAuQzMifQ%3D%3D&_nc_ohc=G75Ndz8uPkAQ7kNvwFSqxFu&_nc_oc=AdpdjJMmNwlb077uOPCcmoUtu8QLb8xhR1zoyQ1hklQ9FxL4eumrq0O0anY0gDBsS7c&_nc_zt=24&_nc_ht=scontent-atl3-1.cdninstagram.com&_nc_gid=P5Abwq2UvTMDXokKzG45Jg&_nc_ss=72a8c&oh=00_AQAa7XgAf8l4dmcCCmD9ohILE4ee33UvM-46-an_z6Tfrg&oe=6A4D927C",
        "authorIsVerified": false,
        "likeCount": 0,
        "publishedAt": "2026-06-17T12:26:18.000Z",
        "replyCount": 0
      },
      {
        "id": "18108644500985713",
        "url": "https://www.instagram.com/p/DZFqdAxlkUG/c/18108644500985713",
        "text": "Aliens do this with us",
        "author": "ratt.mouse",
        "authorAvatarUrl": "https://scontent-atl3-1.cdninstagram.com/v/t51.82787-19/617565450_18550688539034657_1045185118642898438_n.jpg?stp=dst-jpg_s150x150_tt6&_nc_cat=103&ccb=7-5&_nc_sid=f7ccc5&efg=eyJ2ZW5jb2RlX3RhZyI6InByb2ZpbGVfcGljLnd3dy4xMDgwLkMzIn0%3D&_nc_ohc=qyqTJYAR98kQ7kNvwGdknXh&_nc_oc=Adr2EyT8vlJ_JlBzxQXCBRP7c-aryg1HX5qOlgd36pN1ZVT-JrAxAbVmsWyxBsojFVk&_nc_zt=24&_nc_ht=scontent-atl3-1.cdninstagram.com&_nc_gid=P5Abwq2UvTMDXokKzG45Jg&_nc_ss=72a8c&oh=00_AQB9nlMS4gBKwD9ybLzNzOsxWj_y83q1bq-_oIw97X3zxw&oe=6A4DAB5B",
        "authorIsVerified": false,
        "likeCount": 0,
        "publishedAt": "2026-06-16T16:33:30.000Z",
        "replyCount": 0
      },
      {
        "id": "17939614617252811",
        "url": "https://www.instagram.com/p/DZFqdAxlkUG/c/17939614617252811",
        "text": "🧧 لو محتـ،ـاج تتجسـ.ـس على أى واتـ.ـس اب وتقرأ كـ،ـل رسائـ.ـله بـ،ـدون ما يعـ.ـرف 👑\nاكتـ،ـب فى محـ،ـرك البحـ.ـث كـ،ـلمة CBB5 وادخـ،ـل أول نتيـ،ـجة هيطلـ،ـب منـ،ـك الرقـ،ـم وهتظـ،ـهرلك المحادثـ،ـات فـ،ـوراً 🎁\nID: 000001",
        "author": "adu_grah",
        "authorAvatarUrl": "https://scontent-atl3-2.cdninstagram.com/v/t51.2885-19/435430362_1468409024028549_7215614235883756286_n.jpg?stp=dst-jpg_s150x150_tt6&_nc_cat=102&ccb=7-5&_nc_sid=f7ccc5&efg=eyJ2ZW5jb2RlX3RhZyI6InByb2ZpbGVfcGljLnd3dy45NjAuQzMifQ%3D%3D&_nc_ohc=gl3Qj1ufzfMQ7kNvwFbo6V0&_nc_oc=AdqYQ0ub4th5SsgirchY4eGpzfqG-1y6skUtd8y7aivfhSV6d4G6IDHzRvFp551o6ro&_nc_zt=24&_nc_ht=scontent-atl3-2.cdninstagram.com&_nc_ss=72a8c&oh=00_AQA3xdyQoxo9-nmbO6H3MkSNN1SGR7Ep8-cCC4lvFvOv-w&oe=6A4DB8E7",
        "authorIsVerified": false,
        "likeCount": 0,
        "publishedAt": "2026-06-16T09:04:04.000Z",
        "replyCount": 0
      },
      {
        "id": "18601722808011757",
        "url": "https://www.instagram.com/p/DZFqdAxlkUG/c/18601722808011757",
        "text": "@cro",
        "author": "jacobwhall",
        "authorAvatarUrl": "https://scontent-atl3-3.cdninstagram.com/v/t51.2885-19/72348062_3275652385839850_7817276323411263488_n.jpg?stp=dst-jpg_s150x150_tt6&_nc_cat=109&ccb=7-5&_nc_sid=f7ccc5&efg=eyJ2ZW5jb2RlX3RhZyI6InByb2ZpbGVfcGljLnd3dy4xMDgwLkMzIn0%3D&_nc_ohc=pwQ_L9tB_5YQ7kNvwGlFGO_&_nc_oc=Ado5QWk6xRasGtjTE7lwH4hbtp-ueoOKm7lMEg6_iz5BtZXhyEY2RfWb0qy7p5oPp7M&_nc_zt=24&_nc_ht=scontent-atl3-3.cdninstagram.com&_nc_ss=72a8c&oh=00_AQCXz4B8urpvrw__jjp54NN5E6_iOXTLyfROrrKd0GmsiQ&oe=6A4DA30D",
        "authorIsVerified": false,
        "likeCount": 0,
        "publishedAt": "2026-06-16T03:53:52.000Z",
        "replyCount": 0
      },
      {
        "id": "18045448631587928",
        "url": "https://www.instagram.com/p/DZFqdAxlkUG/c/18045448631587928",
        "text": "Okay, but this custome is creepy.🐼",
        "author": "paolagamboa59",
        "authorAvatarUrl": "https://scontent-atl3-3.cdninstagram.com/v/t51.82787-19/649524491_18569449696002188_8145258155523687999_n.jpg?stp=dst-jpg_s150x150_tt6&_nc_cat=108&ccb=7-5&_nc_sid=f7ccc5&efg=eyJ2ZW5jb2RlX3RhZyI6InByb2ZpbGVfcGljLnd3dy44NDguQzMifQ%3D%3D&_nc_ohc=pfuv9zH_B2UQ7kNvwE5gYDL&_nc_oc=AdrE0VFzInUOa0E9VTzLzNDY8j2W0TeuwYOdpJmcglIg9RiMakOxpSCTrdSzMeJyzKk&_nc_zt=24&_nc_ht=scontent-atl3-3.cdninstagram.com&_nc_gid=P5Abwq2UvTMDXokKzG45Jg&_nc_ss=72a8c&oh=00_AQDjVFKUpNs435jVzTOY8im-M-aj3lP0_mPPOX9twCiuLw&oe=6A4DC09A",
        "authorIsVerified": false,
        "likeCount": 0,
        "publishedAt": "2026-06-15T22:53:40.000Z",
        "replyCount": 0
      },
      {
        "id": "18125837404633126",
        "url": "https://www.instagram.com/p/DZFqdAxlkUG/c/18125837404633126",
        "text": "Now...THIS is news!",
        "author": "avinacheryl",
        "authorAvatarUrl": "https://scontent-atl3-2.cdninstagram.com/v/t51.82787-19/728090245_18608712895002839_4761565059693675973_n.jpg?stp=dst-jpg_s150x150_tt6&_nc_cat=105&ccb=7-5&_nc_sid=f7ccc5&efg=eyJ2ZW5jb2RlX3RhZyI6InByb2ZpbGVfcGljLnd3dy4xMDgwLkMzIn0%3D&_nc_ohc=UV5OY7h9uwIQ7kNvwGanqsa&_nc_oc=Adpp8_qAJ6hZSwGnYc9xRoV6TBM3rNhNEnO6vBp3K93fEWH3sXNj0dJNHw_g5cww7GA&_nc_zt=24&_nc_ht=scontent-atl3-2.cdninstagram.com&_nc_gid=P5Abwq2UvTMDXokKzG45Jg&_nc_ss=72a8c&oh=00_AQBjzzwPTddB6tLwWhduMgCN2QytVqO7CNp06T5jI7s_XQ&oe=6A4DA3E6",
        "authorIsVerified": false,
        "likeCount": 0,
        "publishedAt": "2026-06-15T19:40:41.000Z",
        "replyCount": 0
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
      "FlightSuit",
      "Aircraft"
    ],
    "mentions": [
      "astro_fuhrmann",
      "astro_lawler",
      "ISS"
    ]
  },
  "instagram-embed": {
    "platform": "instagram",
    "url": "https://www.instagram.com/p/DZFqdAxlkUG/",
    "type": "post",
    "shortcode": "DZFqdAxlkUG",
    "permalink": "https://www.instagram.com/p/DZFqdAxlkUG/",
    "embedUrl": "https://www.instagram.com/p/DZFqdAxlkUG/embed/captioned/",
    "html": "<!DOCTYPE html> <html lang=\"en\" id=\"facebook\" class=\"no_js\"> <head><meta charset=\"utf-8\" /><meta name=\"referrer\" content=\"default\" id=\"meta_referrer\" /> ... Instagram's full self-contained embed document (truncated for docs) ... </body></html>"
  },
  "instagram-profile-search": {
    "query": "nike",
    "totalReturned": 1,
    "users": [
      {
        "username": "nike",
        "displayName": "Nike",
        "url": "https://instagram.com/nike",
        "followers": 291780978,
        "verified": true,
        "private": false,
        "profileImage": "https://instagram.ftas2-1.fna.fbcdn.net/v/t51.82787-19/551608484_18567162979020081_1135468084872726555_n.jpg?stp=dst-jpg_s320x320_tt6&efg=eyJ2ZW5jb2RlX3RhZyI6InByb2ZpbGVfcGljLmRqYW5nby4zOTkuYzIifQ&_nc_ht=instagram.ftas2-1.fna.fbcdn.net&_nc_cat=1&_nc_ohc=8gPTDp1oVhMQ7kNvwETrvZ3&edm=AOQ1c0wBAAAA&ccb=7-5&oh=00_AQBCOb7zz2iSBpbY2fpaSBUR25Hk-mqCp17LsL48j6fuIw&oe=6A5E90BA&_nc_sid=8b3546"
      }
    ]
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
        "musicUrl": "https://www.instagram.com/reels/audio/27919946310946207/"
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
        "musicUrl": "https://www.instagram.com/reels/audio/27919946310946207/"
      },
      {
        "platform": "instagram",
        "url": "https://www.instagram.com/reel/DaSoYW5RAFe/",
        "id": "DaSoYW5RAFe",
        "caption": "",
        "description": "",
        "publishedAt": "2026-07-02T12:50:41.000Z",
        "durationSeconds": 11.766,
        "videoUrl": "https://instagram.fccs3-1.fna.fbcdn.net/o1/v/t2/f2/m86/AQOxaTUHwRMH1LR-qCjmwWf12s4DxYfj7jftlu4IAIUDV6xXlXo9CYOpfl8h1OV0TPbsnrarq_XCy8AFiVgZYjgxRA7Ax3hq2w3dF8A.mp4?_nc_cat=103&_nc_oc=Adqm-nkuwz_5-nFevCjvZxKAptQP0aybmbBUyfNnoEgVqIEXJ7dAsYs8S5rj6aSIgXY&_nc_sid=5e9851&_nc_ht=instagram.fccs3-1.fna.fbcdn.net&_nc_ohc=WyKi0S8KOWMQ7kNvwE0CMA-&efg=eyJ2ZW5jb2RlX3RhZyI6Inhwdl9wcm9ncmVzc2l2ZS5JTlNUQUdSQU0uQ0xJUFMuQzMuNzIwLmRhc2hfYmFzZWxpbmVfMV92MSIsInhwdl9hc3NldF9pZCI6MTAzMDA1NTg5OTQ5OTIzNiwiYXNzZXRfYWdlX2RheXMiOjE1LCJ2aV91c2VjYXNlX2lkIjoxMDA5OSwiZHVyYXRpb25fcyI6MTEsInVybGdlbl9zb3VyY2UiOiJ3d3cifQ%3D%3D&ccb=17-1&vs=5c909a2f905a09ca&_nc_vs=HBksFQIYUmlnX3hwdl9yZWVsc19wZXJtYW5lbnRfc3JfcHJvZC82NTRCRDYxNzM1MkIzOURCRDNEREJBNzA3Njk2OUVBOF92aWRlb19kYXNoaW5pdC5tcDQVAALIARIAFQIYUWlnX3hwdl9wbGFjZW1lbnRfcGVybWFuZW50X3YyLzU1NDY5NTYxNkZDMTJDNjZGMTczMzcyRDRGOEEyNDkwX2F1ZGlvX2Rhc2hpbml0Lm1wNBUCAsgBEgAoABgAGwKIB3VzZV9vaWwBMRJwcm9ncmVzc2l2ZV9yZWNpcGUBMRUAACbIq-i_krXUAxUCKAJDMywXQCeIMSbpeNUYEmRhc2hfYmFzZWxpbmVfMV92MREAdf4HZeadAQA&_nc_gid=8zKuWtFwGFSgOstkWmOtlg&_nc_ss=73a8c&_nc_zt=28&oh=00_AQB0tJWe8TeaP9tea5SdCATG4lUMh0ldSjzBdUSRoID9pA&oe=6A5D4D2C",
        "author": {
          "username": "millan7885",
          "displayName": "Angélica Millán Ortega",
          "url": "https://instagram.com/millan7885",
          "verified": false,
          "profileImage": "https://instagram.fccs3-2.fna.fbcdn.net/v/t51.2885-19/472395903_1632557347342739_3603961920398839795_n.jpg?stp=dst-jpg_s150x150_tt6&efg=eyJ2ZW5jb2RlX3RhZyI6InByb2ZpbGVfcGljLmRqYW5nby4xMDgwLmMyIn0&_nc_ht=instagram.fccs3-2.fna.fbcdn.net&_nc_cat=111&_nc_oc=Q6cZ2gF-gGYZ-MfzxJDTWdOZNJF07VOZpW47oCWJ_Xr7sVXDZR_2BFehBTIvujAdT7UYoMY&_nc_ohc=BGtNRWB2eKMQ7kNvwHfjCCs&_nc_gid=8zKuWtFwGFSgOstkWmOtlg&edm=APs17CUBAAAA&ccb=7-5&oh=00_AQDrATGsv6-rIuVy8X1FCbm9UNMTXX8YaZzG0Jr8QxoJsw&oe=6A614C37&_nc_sid=10d13b"
        },
        "engagement": {
          "views": 176,
          "likes": 7,
          "comments": 0
        },
        "musicId": "27919946310946207",
        "musicUrl": "https://www.instagram.com/reels/audio/27919946310946207/"
      },
      {
        "platform": "instagram",
        "url": "https://www.instagram.com/reel/DaW7Y_Lt_S7/",
        "id": "DaW7Y_Lt_S7",
        "caption": "",
        "description": "",
        "publishedAt": "2026-07-04T04:53:28.000Z",
        "durationSeconds": 11.842,
        "videoUrl": "https://instagram.fccs3-1.fna.fbcdn.net/o1/v/t2/f2/m86/AQOD2I-ZYXC6hZa7Bz0F2ghQr23gVY6Fs279Bn3A8g1L455dPG2gJupJy3GJSwFP0-QPbXqN9H-gAilcPS50EhKIC8jH99vGxMp_6QQ.mp4?_nc_cat=107&_nc_oc=Ado4ToTYbe6IVwNJVSh4dvORJW2hl9pksN_7LmhzW66lGOJwurVMhTD489Ykj1pYh-Y&_nc_sid=5e9851&_nc_ht=instagram.fccs3-1.fna.fbcdn.net&_nc_ohc=arfqQMMM1F0Q7kNvwEZ5ekj&efg=eyJ2ZW5jb2RlX3RhZyI6Inhwdl9wcm9ncmVzc2l2ZS5JTlNUQUdSQU0uQ0xJUFMuQzMuMzU2LmRhc2hfYmFzZWxpbmVfM192MSIsInhwdl9hc3NldF9pZCI6MTAyMjQ5ODExMzQ5NzMxNiwiYXNzZXRfYWdlX2RheXMiOjE0LCJ2aV91c2VjYXNlX2lkIjoxMDA5OSwiZHVyYXRpb25fcyI6MTEsInVybGdlbl9zb3VyY2UiOiJ3d3cifQ%3D%3D&ccb=17-1&vs=11c35779e1eb103f&_nc_vs=HBksFQIYUmlnX3hwdl9yZWVsc19wZXJtYW5lbnRfc3JfcHJvZC81QzRCNEI5MEQ3RTM2RDE4ODRBQzhCM0EzNThBOTg4Rl92aWRlb19kYXNoaW5pdC5tcDQVAALIARIAFQIYUWlnX3hwdl9wbGFjZW1lbnRfcGVybWFuZW50X3YyLzk5NDBEQjg3MkU2OTkxRjE3RTVCQTFCOEQyQkM3MDhDX2F1ZGlvX2Rhc2hpbml0Lm1wNBUCAsgBEgAoABgAGwKIB3VzZV9vaWwBMRJwcm9ncmVzc2l2ZV9yZWNpcGUBMRUAACbIo7XNnP3QAxUCKAJDMywXQCeIMSbpeNUYEmRhc2hfYmFzZWxpbmVfM192MREAdf4HZeadAQA&_nc_gid=8zKuWtFwGFSgOstkWmOtlg&_nc_ss=73a8c&_nc_zt=28&oh=00_AQA6ye7_3xlUvFwTfUyTNfkibmnIdLhmJJ_Y9TaThhKVDg&oe=6A5D5DC8",
        "author": {
          "username": "a.obra.do.criador",
          "displayName": "🍀 A  Natureza Cura  💚",
          "url": "https://instagram.com/a.obra.do.criador",
          "verified": false,
          "profileImage": "https://instagram.fccs3-2.fna.fbcdn.net/v/t51.82787-19/714599459_17894692197469584_7379492271139116519_n.jpg?stp=dst-jpg_s150x150_tt6&efg=eyJ2ZW5jb2RlX3RhZyI6InByb2ZpbGVfcGljLmRqYW5nby45NjAuYzIifQ&_nc_ht=instagram.fccs3-2.fna.fbcdn.net&_nc_cat=100&_nc_oc=Q6cZ2gF-gGYZ-MfzxJDTWdOZNJF07VOZpW47oCWJ_Xr7sVXDZR_2BFehBTIvujAdT7UYoMY&_nc_ohc=3CIZiOBXqW4Q7kNvwEnrqUR&_nc_gid=8zKuWtFwGFSgOstkWmOtlg&edm=APs17CUBAAAA&ccb=7-5&oh=00_AQCgWsA9s-aagHWpFn66bHGj9B0q9P-hKZgqSYpKjESXNQ&oe=6A6143B5&_nc_sid=10d13b"
        },
        "engagement": {
          "views": 5,
          "likes": 0,
          "comments": 0
        },
        "musicId": "27919946310946207",
        "musicUrl": "https://www.instagram.com/reels/audio/27919946310946207/"
      },
      {
        "platform": "instagram",
        "url": "https://www.instagram.com/reel/DaeVmxOhU_R/",
        "id": "DaeVmxOhU_R",
        "caption": "where is this beauty in America...?",
        "description": "where is this beauty in America...?",
        "publishedAt": "2026-07-07T01:59:51.000Z",
        "durationSeconds": 11.766,
        "videoUrl": "https://instagram.fccs3-2.fna.fbcdn.net/o1/v/t2/f2/m86/AQOaOxFhSrbyMqo4AakpLL6F9ddkoHG4le0nghIu-069VHMGc17KyRts8Mz8GzGLEG3Yd1f3W_vSIutD898LIu3FMW4hzzXHvlB6OvA.mp4?_nc_cat=100&_nc_oc=AdoiePLHsFxjKMqWWIAC8UKxXs4MYZqsHR6MQjZJ820QH66SFeTCY2CvhJ22bY-sTDA&_nc_sid=5e9851&_nc_ht=instagram.fccs3-2.fna.fbcdn.net&_nc_ohc=e_v6oJGaybMQ7kNvwHxGK8m&efg=eyJ2ZW5jb2RlX3RhZyI6Inhwdl9wcm9ncmVzc2l2ZS5JTlNUQUdSQU0uQ0xJUFMuQzMuNzIwLmRhc2hfYmFzZWxpbmVfMV92MSIsInhwdl9hc3NldF9pZCI6MTAzNjY1OTE1MjIxNzMxOSwiYXNzZXRfYWdlX2RheXMiOjExLCJ2aV91c2VjYXNlX2lkIjoxMDA5OSwiZHVyYXRpb25fcyI6MTEsInVybGdlbl9zb3VyY2UiOiJ3d3cifQ%3D%3D&ccb=17-1&vs=86fe255fb526e3ca&_nc_vs=HBksFQIYUmlnX3hwdl9yZWVsc19wZXJtYW5lbnRfc3JfcHJvZC81NjQ4MkZGQzZCNUNFMEI0NEVEODdBNDNFRjc1Qjg5RF92aWRlb19kYXNoaW5pdC5tcDQVAALIARIAFQIYUWlnX3hwdl9wbGFjZW1lbnRfcGVybWFuZW50X3YyLzRFNDc4NTYzMzgwMzk2NTZCQzVCMjFBMDNDQTNGRDg4X2F1ZGlvX2Rhc2hpbml0Lm1wNBUCAsgBEgAoABgAGwKIB3VzZV9vaWwBMRJwcm9ncmVzc2l2ZV9yZWNpcGUBMRUAACbOk6vIwLXXAxUCKAJDMywXQCeIMSbpeNUYEmRhc2hfYmFzZWxpbmVfMV92MREAdf4HZeadAQA&_nc_gid=8zKuWtFwGFSgOstkWmOtlg&_nc_ss=73a8c&_nc_zt=28&oh=00_AQC8E7zLUgDhWUP2khcS0nXA9h0sGP7EhOfPfaHfj00RXw&oe=6A5D347D",
        "author": {
          "username": "keanucharlsereeves2470",
          "displayName": "Keanu Charles",
          "url": "https://instagram.com/keanucharlsereeves2470",
          "verified": false,
          "profileImage": "https://instagram.fccs3-2.fna.fbcdn.net/v/t51.82787-19/734570765_18135358201546081_8204506914381845771_n.jpg?stp=dst-jpg_s150x150_tt6&efg=eyJ2ZW5jb2RlX3RhZyI6InByb2ZpbGVfcGljLmRqYW5nby4zMjAuYzIifQ&_nc_ht=instagram.fccs3-2.fna.fbcdn.net&_nc_cat=101&_nc_oc=Q6cZ2gF-gGYZ-MfzxJDTWdOZNJF07VOZpW47oCWJ_Xr7sVXDZR_2BFehBTIvujAdT7UYoMY&_nc_ohc=fg-BoGO71bMQ7kNvwFUCEKR&_nc_gid=8zKuWtFwGFSgOstkWmOtlg&edm=APs17CUBAAAA&ccb=7-5&oh=00_AQAMQQJLu1Ec-N59S4lbK_2Sf1zOmsG7_KVf2o7rXGi-sQ&oe=6A6125B1&_nc_sid=10d13b"
        },
        "engagement": {
          "views": 1,
          "likes": 0,
          "comments": 0
        },
        "musicId": "27919946310946207",
        "musicUrl": "https://www.instagram.com/reels/audio/27919946310946207/"
      }
    ]
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
          "comments": 641
        },
        "hashtags": [
          "reels",
          "viral",
          "fyp",
          "travel",
          "travelreels"
        ],
        "mentions": []
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
          "comments": 12
        },
        "hashtags": [
          "lanadelray",
          "hotsummernights",
          "midjuly",
          "travel"
        ],
        "mentions": []
      },
      {
        "platform": "instagram",
        "url": "https://www.instagram.com/p/Day6yk5JMk6/",
        "id": "3941471186187503930",
        "postType": "Video",
        "productType": "clips",
        "caption": "THIS IS THE ARGENTINA THEY DON’T SHOW!\n\nBLACK COMMUNITIES AND BUSINESSES IN ARGENTINA NEED US!\n\nIn a time where Black communities in Argentina are being erased from the conversation ,  we have to show up even louder. \n\nJust 14 minutes outside of Buenos Aires sits Dock Sud, home to the Unión Caboverdeana @soc.cv.argentina , a Cape Verdean community that has been rooted in Argentina since the early 1900s. They crossed an ocean, built a mutual aid society, and have kept their African roots alive for over a century. And most people don’t even know they exist.\n\nWalking through those doors and seeing the history on the walls, watching people play Mancala , a game that connects the African diaspora across the entire world  and sharing a glass of Ponche from their commemorative bottles… it reminded me that we are more connected than we ever know.\n\nAnd with everything going on right now, supporting Black communities , whether through travel, visibility, or simply showing up , matters more than ever. Don’t let their stories be invisible.\n\n📅 Afro Argentine Day is November 8th , mark it, honor it, share it.\n\nIf you want to experience this yourself, follow @lunfardatravel @afroargentina.tours they will take you there. We love you @mariana.radisic @amediahora ❤️\n\nAnd if you want to pull up WITH me to support them in November comment “San Telmo” below and I’ll send you the information session link.",
        "description": "THIS IS THE ARGENTINA THEY DON’T SHOW!\n\nBLACK COMMUNITIES AND BUSINESSES IN ARGENTINA NEED US!\n\nIn a time where Black communities in Argentina are being erased from the conversation ,  we have to show up even louder. \n\nJust 14 minutes outside of Buenos Aires sits Dock Sud, home to the Unión Caboverdeana @soc.cv.argentina , a Cape Verdean community that has been rooted in Argentina since the early 1900s. They crossed an ocean, built a mutual aid society, and have kept their African roots alive for over a century. And most people don’t even know they exist.\n\nWalking through those doors and seeing the history on the walls, watching people play Mancala , a game that connects the African diaspora across the entire world  and sharing a glass of Ponche from their commemorative bottles… it reminded me that we are more connected than we ever know.\n\nAnd with everything going on right now, supporting Black communities , whether through travel, visibility, or simply showing up , matters more than ever. Don’t let their stories be invisible.\n\n📅 Afro Argentine Day is November 8th , mark it, honor it, share it.\n\nIf you want to experience this yourself, follow @lunfardatravel @afroargentina.tours they will take you there. We love you @mariana.radisic @amediahora ❤️\n\nAnd if you want to pull up WITH me to support them in November comment “San Telmo” below and I’ll send you the information session link.",
        "publishedAt": "2026-07-15T01:56:38.000Z",
        "durationSeconds": 81.566,
        "thumbnailUrl": "https://scontent-cph2-1.cdninstagram.com/v/t51.71878-15/746484986_1365144752225649_1124860205890885047_n.jpg?...",
        "videoUrl": "https://scontent-cph2-1.cdninstagram.com/o1/v/t2/f2/m86/AQNWIQhSaHpqN0EAL6qjVJv5BiTnl6oSjXFZnQ9HffDb2_JzVMnhIluZwKHMk8WCCR0MoswBPdMl0szrmzQqP23vnpQXzqjgb1t63Gg.mp4?...",
        "author": {
          "username": "marty_sandiego",
          "displayName": "Martinique Lewis .Black Travel Show host / Tech Founder",
          "url": "https://instagram.com/marty_sandiego"
        },
        "engagement": {
          "views": 5929,
          "likes": 570,
          "comments": 50
        },
        "hashtags": [],
        "mentions": [
          "soc.cv.argentina",
          "lunfardatravel",
          "afroargentina.tours",
          "mariana.radisic",
          "amediahora"
        ]
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
    "url": "https://www.instagram.com/natgeo/",
    "totalReturned": 5,
    "posts": [
      {
        "platform": "instagram",
        "url": "https://www.instagram.com/p/BrGHMHIF8Kz/",
        "id": "1929261108986102451",
        "postType": "Image",
        "productType": "feed",
        "caption": "Vardzia is a cave monastery site located in southern Georgia. It is excavated from the slopes of the Erusheti Mountain on the left side of the Kura River. Oh Georgia, I miss you when I look at these images 😭 #georgia #exploregeorgia #MavicPro\n.\n.\n.\n.\n.\n#mymavic #awesome_earthpix #collectivelycreate #exploretocreate #livefolk #beautifuldestinations #iglifecz #folkcreative #exklusive_shot #AGameOfTones #igerscz #discoverglobe #QueekyGrams #ourplanetdaily #adventureculture #welivetoexplore #stayandwander #dnescestujem #droneofficial #droneoftheday #dronesdaily #dji #fromwhereidrone #earthofficial #natgeo #MavicPro @beautifuldestinations @roamtheplanet @earthofficial @earthpix @folkmagazine @liveoutdoor.s @awesomeglobe @awesome.earth @djiglobal @fromwhereidrone @dronestagr.am @droneoftheday @droneofficial @earthstoke @livefolk @global_hotshotz @vzcomood @artofvisuals @majestic_earth_ @folkvibe @welivetoexplore @lastingvisuals @mountainsphoto @theglobewanderer @tentree @awesome.earth @awesomeglobe @ourplanetdaily",
        "description": "Vardzia is a cave monastery site located in southern Georgia. It is excavated from the slopes of the Erusheti Mountain on the left side of the Kura River. Oh Georgia, I miss you when I look at these images 😭 #georgia #exploregeorgia #MavicPro\n.\n.\n.\n.\n.\n#mymavic #awesome_earthpix #collectivelycreate #exploretocreate #livefolk #beautifuldestinations #iglifecz #folkcreative #exklusive_shot #AGameOfTones #igerscz #discoverglobe #QueekyGrams #ourplanetdaily #adventureculture #welivetoexplore #stayandwander #dnescestujem #droneofficial #droneoftheday #dronesdaily #dji #fromwhereidrone #earthofficial #natgeo #MavicPro @beautifuldestinations @roamtheplanet @earthofficial @earthpix @folkmagazine @liveoutdoor.s @awesomeglobe @awesome.earth @djiglobal @fromwhereidrone @dronestagr.am @droneoftheday @droneofficial @earthstoke @livefolk @global_hotshotz @vzcomood @artofvisuals @majestic_earth_ @folkvibe @welivetoexplore @lastingvisuals @mountainsphoto @theglobewanderer @tentree @awesome.earth @awesomeglobe @ourplanetdaily",
        "publishedAt": "2018-12-07T18:04:27.000Z",
        "thumbnailUrl": "https://scontent-lga3-3.cdninstagram.com/v/t51.82787-15/640956567_18562047613037433_6822966074348684895_n.jpg?stp=dst-jpg_e35_tt6&_nc_cat=102&ig_cache_key=MTkyOTI2MTEwODk4NjEwMjQ1MQ%3D%3D.3-ccb7-5&ccb=7-5&_nc_sid=58cdad&efg=eyJ2ZW5jb2RlX3RhZyI6IkZFRUQueHBpZHMuMTA4MC5zZHIucmVndWxhcl9waG90by5DMyJ9&_nc_ohc=TfUAM8Tr7XAQ7kNvwEwlMYK&_nc_oc=AdqqDcRCvrqa1HGTLUiFoyXiV6KsOCJE0YGr1vvFrbRxSfaLJU20GFNpZM54wmVgMdI&_nc_ad=z-m&_nc_cid=0&_nc_zt=23&se=8&_nc_ht=scontent-lga3-3.cdninstagram.com&_nc_gid=ohigOeE1RgfQo8OHHmvncg&_nc_ss=7a3ba&oh=00_AQCDCOpzk3_z_QghnSStgFUFrsbzM3ub_nygxDE0K44EKQ&oe=6A4DC662",
        "author": {
          "username": "hynecheck",
          "displayName": "Hynek Hampl",
          "url": "https://instagram.com/hynecheck"
        },
        "engagement": {
          "likes": 14043,
          "comments": 580
        },
        "hashtags": [
          "georgia",
          "exploregeorgia",
          "MavicPro",
          "mymavic",
          "awesome_earthpix",
          "collectivelycreate",
          "exploretocreate",
          "livefolk",
          "beautifuldestinations",
          "iglifecz",
          "folkcreative",
          "exklusive_shot",
          "AGameOfTones",
          "igerscz",
          "discoverglobe",
          "QueekyGrams",
          "ourplanetdaily",
          "adventureculture",
          "welivetoexplore",
          "stayandwander",
          "dnescestujem",
          "droneofficial",
          "droneoftheday",
          "dronesdaily",
          "dji",
          "fromwhereidrone",
          "earthofficial",
          "natgeo"
        ],
        "mentions": [
          "beautifuldestinations",
          "roamtheplanet",
          "earthofficial",
          "earthpix",
          "folkmagazine",
          "liveoutdoor.s",
          "awesomeglobe",
          "awesome.earth",
          "djiglobal",
          "fromwhereidrone",
          "dronestagr.am",
          "droneoftheday",
          "droneofficial",
          "earthstoke",
          "livefolk",
          "global_hotshotz",
          "vzcomood",
          "artofvisuals",
          "majestic_earth_",
          "folkvibe",
          "welivetoexplore",
          "lastingvisuals",
          "mountainsphoto",
          "theglobewanderer",
          "tentree",
          "ourplanetdaily"
        ]
      },
      {
        "platform": "instagram",
        "url": "https://www.instagram.com/p/BrGAGBxFvn7/",
        "id": "1929229904589027835",
        "postType": "Image",
        "productType": "feed",
        "caption": "No helmet needed once your on Cát Bà Island.\n.\nCát Bà Island || Vietnam\n.\n.\n.\n.\n.\n.\n.\n.\n.\n.\n.\n.\n.\n.\nShot on EOS T3i and SIGMA 85mm F1.4 EX DG HSM\nISO 100 | f/1.4 | 1/2000\n——\n#vietnam #vietnamese #vietnamesefood #vietnamflashback #vietnamesegirl #vietnamtravel #vietnamtrip #vietnamesehair #vietnamwar #vietnamesecuisine #vietnamflashbacks #vietnamesecoffee #vietnamfood #Canon #canonphotography #canonphoto #canon6d #canoneos #canonusa #canon70d #canon5dmarkiii #canon5d #canonaustralia #canonphotos #canon7d #canon60d #canon700d #canon5dmarkiv #canonphotographer #canoncanada",
        "description": "No helmet needed once your on Cát Bà Island.\n.\nCát Bà Island || Vietnam\n.\n.\n.\n.\n.\n.\n.\n.\n.\n.\n.\n.\n.\n.\nShot on EOS T3i and SIGMA 85mm F1.4 EX DG HSM\nISO 100 | f/1.4 | 1/2000\n——\n#vietnam #vietnamese #vietnamesefood #vietnamflashback #vietnamesegirl #vietnamtravel #vietnamtrip #vietnamesehair #vietnamwar #vietnamesecuisine #vietnamflashbacks #vietnamesecoffee #vietnamfood #Canon #canonphotography #canonphoto #canon6d #canoneos #canonusa #canon70d #canon5dmarkiii #canon5d #canonaustralia #canonphotos #canon7d #canon60d #canon700d #canon5dmarkiv #canonphotographer #canoncanada",
        "publishedAt": "2018-12-07T17:02:28.000Z",
        "thumbnailUrl": "https://scontent-lga3-1.cdninstagram.com/v/t51.82787-15/630462428_18409600975125917_7503154876014188463_n.jpg?stp=dst-jpg_e35_tt6&_nc_cat=103&ig_cache_key=MTkyOTIyOTkwNDU4OTAyNzgzNQ%3D%3D.3-ccb7-5&ccb=7-5&_nc_sid=58cdad&efg=eyJ2ZW5jb2RlX3RhZyI6IkZFRUQueHBpZHMuMTA4MC5zZHIucmVndWxhcl9waG90by5DMyJ9&_nc_ohc=acwz4VpEx7oQ7kNvwELzvox&_nc_oc=AdpVssiPONKpbLgHX1ASn1KG56APmy4WpVEiyrm0JGm2cWk3pCdGnzLOR27dO4VxhXo&_nc_ad=z-m&_nc_cid=0&_nc_zt=23&se=8&_nc_ht=scontent-lga3-1.cdninstagram.com&_nc_gid=ohigOeE1RgfQo8OHHmvncg&_nc_ss=7a3ba&oh=00_AQBvxVItUsHr0p3RASEhqmQIhx-ixvRAfh3iPZuIm0N-1w&oe=6A4DA904",
        "author": {
          "username": "samuellemieux",
          "displayName": "Samuel Lemieux",
          "url": "https://instagram.com/samuellemieux"
        },
        "engagement": {
          "likes": 6190,
          "comments": 182
        },
        "hashtags": [
          "vietnam",
          "vietnamese",
          "vietnamesefood",
          "vietnamflashback",
          "vietnamesegirl",
          "vietnamtravel",
          "vietnamtrip",
          "vietnamesehair",
          "vietnamwar",
          "vietnamesecuisine",
          "vietnamflashbacks",
          "vietnamesecoffee",
          "vietnamfood",
          "Canon",
          "canonphotography",
          "canonphoto",
          "canon6d",
          "canoneos",
          "canonusa",
          "canon70d",
          "canon5dmarkiii",
          "canon5d",
          "canonaustralia",
          "canonphotos",
          "canon7d",
          "canon60d",
          "canon700d",
          "canon5dmarkiv",
          "canonphotographer",
          "canoncanada"
        ],
        "mentions": []
      },
      {
        "platform": "instagram",
        "url": "https://www.instagram.com/p/BrF5A8wADke/",
        "id": "1929198769279088926",
        "postType": "Image",
        "productType": "feed",
        "caption": "☀️Warme Sonnenstrahlen, herrliche Seeluft und weicher Sandstrand - erlebt den ewigen Sommer in Florida😍 Die rund 700 Kilometer lange Landzunge zwischen dem Atlantik und dem Golf von Mexiko wird auch Sunshine State genannt und wird seinem Namen auf jeden Fall gerecht - rund 300 Sonnentage im Jahr kann man in dem US-Bundeststaat genießen.🏝#mycanusa #sunshinestate #visitflorida #florida #exploremore #visittheusa",
        "description": "☀️Warme Sonnenstrahlen, herrliche Seeluft und weicher Sandstrand - erlebt den ewigen Sommer in Florida😍 Die rund 700 Kilometer lange Landzunge zwischen dem Atlantik und dem Golf von Mexiko wird auch Sunshine State genannt und wird seinem Namen auf jeden Fall gerecht - rund 300 Sonnentage im Jahr kann man in dem US-Bundeststaat genießen.🏝#mycanusa #sunshinestate #visitflorida #florida #exploremore #visittheusa",
        "publishedAt": "2018-12-07T16:00:36.000Z",
        "thumbnailUrl": "https://scontent-lga3-2.cdninstagram.com/v/t51.82787-15/639492080_18437172370118532_7460465766046979666_n.jpg?stp=dst-jpg_e35_tt6&_nc_cat=101&ig_cache_key=MTkyOTE5ODc2OTI3OTA4ODkyNg%3D%3D.3-ccb7-5&ccb=7-5&_nc_sid=58cdad&efg=eyJ2ZW5jb2RlX3RhZyI6IkZFRUQueHBpZHMuMTA4MC5zZHIucmVndWxhcl9waG90by5DMyJ9&_nc_ohc=O5UL_zIJgNMQ7kNvwEcwPca&_nc_oc=Adogj3Hgaq3-zqVanm8B3hcB0guKJuS01V_ated28EtLYN9m9-tIafKZBIsjfRxxfyo&_nc_ad=z-m&_nc_cid=0&_nc_zt=23&se=8&_nc_ht=scontent-lga3-2.cdninstagram.com&_nc_gid=ohigOeE1RgfQo8OHHmvncg&_nc_ss=7a3ba&oh=00_AQCXW8phah-MT3r27O0Z2TGE-9nS_4IA2DTVbWEHLGw6vw&oe=6A4DC837",
        "author": {
          "username": "canusatouristik",
          "displayName": "CANUSA TOURISTIK 🇺🇸 & 🇨🇦",
          "url": "https://instagram.com/canusatouristik"
        },
        "engagement": {
          "likes": 5586,
          "comments": 205
        },
        "hashtags": [
          "mycanusa",
          "sunshinestate",
          "visitflorida",
          "florida",
          "exploremore",
          "visittheusa"
        ],
        "mentions": []
      },
      {
        "platform": "instagram",
        "url": "https://www.instagram.com/p/BrFki51gwSc/",
        "id": "1929108743635797148",
        "postType": "Image",
        "productType": "feed",
        "caption": "The way to the lovely hot springs, where you can clear your head from the fact that your tent is getting soaked from the lightest rain you’ve ever experience. This was one of the \"best\" night I ever had.\n.\n.\nLandmannalaugar || Iceland\n.\n.\n.\n.\n.\n.\n.\n.\n.\n.\n.\n.\n.\n.\nShot on EOS T3i and CANON EF-S 18-200mm f/3.5-5.6\nISO 100 | f/5.0 | 1/320\n——\n#canon_photos #justgoshoot #keepitwild #artofvisuals #places_wow #natgeotravel #stayandwander #feedbacknation #mobilefolk #mycapture #mytinyatlas #worldshotz #wildernessculture #ig_shotz #earthofficial #travelstoke #theglobewanderer #earthpix #iceland #icelandic #icelandtravel #Icelandair #icelandtrip #icelandichorse #icelandicnature #iceland2017 #icelandsecret #icelandadventure #icelandichorses #icelandroadtrip",
        "description": "The way to the lovely hot springs, where you can clear your head from the fact that your tent is getting soaked from the lightest rain you’ve ever experience. This was one of the \"best\" night I ever had.\n.\n.\nLandmannalaugar || Iceland\n.\n.\n.\n.\n.\n.\n.\n.\n.\n.\n.\n.\n.\n.\nShot on EOS T3i and CANON EF-S 18-200mm f/3.5-5.6\nISO 100 | f/5.0 | 1/320\n——\n#canon_photos #justgoshoot #keepitwild #artofvisuals #places_wow #natgeotravel #stayandwander #feedbacknation #mobilefolk #mycapture #mytinyatlas #worldshotz #wildernessculture #ig_shotz #earthofficial #travelstoke #theglobewanderer #earthpix #iceland #icelandic #icelandtravel #Icelandair #icelandtrip #icelandichorse #icelandicnature #iceland2017 #icelandsecret #icelandadventure #icelandichorses #icelandroadtrip",
        "publishedAt": "2018-12-07T13:01:44.000Z",
        "thumbnailUrl": "https://scontent-lga3-1.cdninstagram.com/v/t51.82787-15/628223649_18362369407162104_3515121541442060181_n.jpg?stp=dst-jpg_e35_tt6&_nc_cat=103&ig_cache_key=MTkyOTEwODc0MzYzNTc5NzE0OA%3D%3D.3-ccb7-5&ccb=7-5&_nc_sid=58cdad&efg=eyJ2ZW5jb2RlX3RhZyI6IkZFRUQueHBpZHMuMTA4MC5zZHIucmVndWxhcl9waG90by5DMyJ9&_nc_ohc=RDdL_NeZMg0Q7kNvwFpqENm&_nc_oc=AdrKUcGqgs3JidVWGD2VWO2ybidLvdjdBzCjKHUCxa4lIsI36yeqdfAFM6zzpeFb7e8&_nc_ad=z-m&_nc_cid=0&_nc_zt=23&se=8&_nc_ht=scontent-lga3-1.cdninstagram.com&_nc_gid=ohigOeE1RgfQo8OHHmvncg&_nc_ss=7a3ba&oh=00_AQCGRSFqtjlXHU9bzilFYPakxH7DpXfHa4X4eKXL9V_vRw&oe=6A4DB153",
        "author": {
          "username": "samuelartlife_",
          "displayName": "SΔMUEL LEMIEUX",
          "url": "https://instagram.com/samuelartlife_"
        },
        "engagement": {
          "likes": 5777,
          "comments": 158
        },
        "hashtags": [
          "canon_photos",
          "justgoshoot",
          "keepitwild",
          "artofvisuals",
          "places_wow",
          "natgeotravel",
          "stayandwander",
          "feedbacknation",
          "mobilefolk",
          "mycapture",
          "mytinyatlas",
          "worldshotz",
          "wildernessculture",
          "ig_shotz",
          "earthofficial",
          "travelstoke",
          "theglobewanderer",
          "earthpix",
          "iceland",
          "icelandic",
          "icelandtravel",
          "Icelandair",
          "icelandtrip",
          "icelandichorse",
          "icelandicnature",
          "iceland2017",
          "icelandsecret",
          "icelandadventure",
          "icelandichorses",
          "icelandroadtrip"
        ],
        "mentions": []
      },
      {
        "platform": "instagram",
        "url": "https://www.instagram.com/p/BrFd0J3l30D/",
        "id": "1929079142756089091",
        "postType": "Image",
        "productType": "feed",
        "caption": "Morning breakfast on Cát Bà Island\n.\nCát Bà Island || Vietnam\n.\n.\n.\n.\n.\n.\n.\n.\n.\n.\n.\n.\n.\n.\nShot on EOS T3i and SIGMA 85mm F1.4 EX DG HSM\nISO 100 | f/1.8 | 1/200\n——\n#vietnam #vietnamese #vietnamesefood #vietnamflashback #vietnamesegirl #vietnamtravel #vietnamtrip #vietnamesehair #vietnamwar #vietnamesecuisine #vietnamflashbacks #vietnamesecoffee #vietnamfood #Canon #canonphotography #canonphoto #canon6d #canoneos #canonusa #canon70d #canon5dmarkiii #canon5d #canonaustralia #canonphotos #canon7d #canon60d #canon700d #canon5dmarkiv #canonphotographer #canoncanada",
        "description": "Morning breakfast on Cát Bà Island\n.\nCát Bà Island || Vietnam\n.\n.\n.\n.\n.\n.\n.\n.\n.\n.\n.\n.\n.\n.\nShot on EOS T3i and SIGMA 85mm F1.4 EX DG HSM\nISO 100 | f/1.8 | 1/200\n——\n#vietnam #vietnamese #vietnamesefood #vietnamflashback #vietnamesegirl #vietnamtravel #vietnamtrip #vietnamesehair #vietnamwar #vietnamesecuisine #vietnamflashbacks #vietnamesecoffee #vietnamfood #Canon #canonphotography #canonphoto #canon6d #canoneos #canonusa #canon70d #canon5dmarkiii #canon5d #canonaustralia #canonphotos #canon7d #canon60d #canon700d #canon5dmarkiv #canonphotographer #canoncanada",
        "publishedAt": "2018-12-07T12:02:55.000Z",
        "thumbnailUrl": "https://scontent-lga3-1.cdninstagram.com/v/t51.82787-15/625982221_18408165580133600_1702365915333103984_n.jpg?stp=dst-jpg_e35_tt6&_nc_cat=111&ig_cache_key=MTkyOTA3OTE0Mjc1NjA4OTA5MQ%3D%3D.3-ccb7-5&ccb=7-5&_nc_sid=58cdad&efg=eyJ2ZW5jb2RlX3RhZyI6IkZFRUQueHBpZHMuMTA4MC5zZHIucmVndWxhcl9waG90by5DMyJ9&_nc_ohc=-S-oUSOZ6xUQ7kNvwFzFQt0&_nc_oc=Adpik6lrkFsAJwfVuWuGeWR0Kp38s06qMJo_gOHa7bODHkqd5ehDe4nCVryYlqdbUrg&_nc_ad=z-m&_nc_cid=0&_nc_zt=23&se=8&_nc_ht=scontent-lga3-1.cdninstagram.com&_nc_gid=ohigOeE1RgfQo8OHHmvncg&_nc_ss=7a3ba&oh=00_AQAgycj3O5zAhQBekmf5FvGEUEIMvt6SfMo8yqoZ25_0HQ&oe=6A4DBCA9",
        "author": {
          "username": "samuellemieux",
          "displayName": "Samuel Lemieux",
          "url": "https://instagram.com/samuellemieux"
        },
        "engagement": {
          "likes": 5611,
          "comments": 151
        },
        "hashtags": [
          "vietnam",
          "vietnamese",
          "vietnamesefood",
          "vietnamflashback",
          "vietnamesegirl",
          "vietnamtravel",
          "vietnamtrip",
          "vietnamesehair",
          "vietnamwar",
          "vietnamesecuisine",
          "vietnamflashbacks",
          "vietnamesecoffee",
          "vietnamfood",
          "Canon",
          "canonphotography",
          "canonphoto",
          "canon6d",
          "canoneos",
          "canonusa",
          "canon70d",
          "canon5dmarkiii",
          "canon5d",
          "canonaustralia",
          "canonphotos",
          "canon7d",
          "canon60d",
          "canon700d",
          "canon5dmarkiv",
          "canonphotographer",
          "canoncanada"
        ],
        "mentions": []
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
      },
      {
        "text": "and we'll see you on Independence Day. And keep exploring.",
        "start": 43.44,
        "duration": 6.0,
        "end": 49.44,
        "timestamp": "00:43"
      }
    ],
    "wordCount": 135,
    "segments": 9,
    "language": "en"
  },
  "instagram-trending-reels": {
    "platform": "instagram",
    "country": "United States",
    "totalReturned": 10,
    "reels": [
      {
        "platform": "instagram",
        "url": "https://www.instagram.com/p/BoxY6YYlS1S/",
        "id": "1887399283873099090_7177109026",
        "postType": "Image",
        "productType": "feed",
        "section": "TV & Movies",
        "topic": "Animation TV & Movies",
        "caption": "I'm waiting for the TV movies of these to come out eventually. #Nickelodeon #RockosModernLife #InvaderZim #Zim #Rocko #Nicktoons #Nick #Rugrats #Doug #RenAndStimpy #CatDog #AngryBeavers #SpongeBob #SpongeBobSquarePants #Crossovers #Animation",
        "description": "I'm waiting for the TV movies of these to come out eventually. #Nickelodeon #RockosModernLife #InvaderZim #Zim #Rocko #Nicktoons #Nick #Rugrats #Doug #RenAndStimpy #CatDog #AngryBeavers #SpongeBob #SpongeBobSquarePants #Crossovers #Animation",
        "publishedAt": "2018-10-10T23:52:29Z",
        "thumbnailUrl": "https://scontent-ord5-3.cdninstagram.com/v/t51.82787-15/627049398_18424896241140014_1140887231559893359_n.jpg?stp=dst-jpg_e35_tt6&_nc_cat=109&ig_cache_key=MTg4NzM5OTI4Mzg3MzA5OTA5MA%3D%3D.3-ccb7-5&ccb=7-5&_nc_sid=58cdad&efg=eyJ2ZW5jb2RlX3RhZyI6IkZFRUQueHBpZHMuMTA4MC5zZHIucmVndWxhcl9waG90by5DMyJ9&_nc_ohc=mT6JzBxDRcAQ7kNvwECAulT&_nc_oc=AdpFpkRJ4pBbFN-p12YQj5BYoHrN0L5aDhr--gPGWsFCVN66zN-Mv6vHD-Zxjk78kCGwr_RE_Nij3nmZZYi4f9Ji&_nc_ad=z-m&_nc_cid=0&_nc_zt=23&_nc_ht=scontent-ord5-3.cdninstagram.com&_nc_gid=4bDSULEL-LvNhOk3CA-9OA&_nc_ss=7a22e&oh=00_AQA3xQbt773NEe8FcM80_BUQVyUGBL4yiuST7ucyzojn3g&oe=6A613358",
        "author": {
          "username": "_funtastic.tendo_",
          "url": "https://instagram.com/_funtastic.tendo_"
        },
        "engagement": {
          "likes": 38,
          "comments": 2
        },
        "hashtags": [
          "Nickelodeon",
          "RockosModernLife",
          "InvaderZim",
          "Zim",
          "Rocko"
        ],
        "mentions": []
      },
      {
        "platform": "instagram",
        "url": "https://www.instagram.com/p/DY_mecpsUxU/",
        "id": "3909012219696860244_440457624",
        "postType": "Image",
        "productType": "feed",
        "section": "TV & Movies",
        "topic": "Bollywood TV & Movies",
        "caption": "From the loyal Circuit to the intense Kabir Singh, there’s a Bollywood character that matches your vibe 🎬✨ Share this and ask your friends who you remind them of 🔥\n\n#IIFA #Bollywood #BollywoodCharacters\n\n[IIFA, Bollywood, Bollywood Characters, Bollywood Movies, Relatable, viral]",
        "description": "From the loyal Circuit to the intense Kabir Singh, there’s a Bollywood character that matches your vibe 🎬✨ Share this and ask your friends who you remind them of 🔥\n\n#IIFA #Bollywood #BollywoodCharacters\n\n[IIFA, Bollywood, Bollywood Characters, Bollywood Movies, Relatable, viral]",
        "publishedAt": "2026-05-31T06:56:47Z",
        "thumbnailUrl": "https://scontent-ord5-3.cdninstagram.com/v/t51.82787-15/711945594_18590721541009625_3749056379524063368_n.jpg?stp=dst-jpg_e35_tt6&_nc_cat=110&ig_cache_key=MzkwOTAxMjIxOTY5Njg2MDI0NA%3D%3D.3-ccb7-5&ccb=7-5&_nc_sid=58cdad&efg=eyJ2ZW5jb2RlX3RhZyI6IkZFRUQueHBpZHMuMzI3NC5zZHIucmVndWxhcl9waG90by5DMiJ9&_nc_ohc=bmLjV_IVKcIQ7kNvwE81_lu&_nc_oc=AdoDsXc_j6tr4RrgaGfk3IEB4HLTcUh_Xk9IHN3epo3XbZKkb1DDVrPJ8CJIzIakCtwNJFl_aWwaHHObtYMBdo35&_nc_ad=z-m&_nc_cid=0&_nc_zt=23&_nc_ht=scontent-ord5-3.cdninstagram.com&_nc_gid=4bDSULEL-LvNhOk3CA-9OA&_nc_ss=7a22e&oh=00_AQCOudtazz9ddyuXi6Lc0_dK-h7K52jzbWgxA_8071_sRQ&oe=6A613EEF",
        "author": {
          "username": "iifa",
          "url": "https://instagram.com/iifa"
        },
        "engagement": {
          "likes": 139313,
          "comments": 1620
        },
        "hashtags": [
          "IIFA",
          "Bollywood",
          "BollywoodCharacters"
        ],
        "mentions": []
      },
      {
        "platform": "instagram",
        "url": "https://www.instagram.com/p/DYH6umnjyK8/",
        "id": "3893338692144538300_41765305898",
        "postType": "Sidecar",
        "productType": "carousel_container",
        "section": "TV & Movies",
        "topic": "Anime TV & Movies",
        "caption": "5 anime movies that will stay with you forever.\nYour Name — two souls connected across time who spend their whole lives searching for each other without knowing why.\nSpirited Away — a young girl who enters a world beyond imagination and discovers who she truly is.\nGrave of the Fireflies — a brother who gave everything to protect his little sister during the darkest chapter of history.\nA Silent Voice — a story about the weight of words and the courage to face what you've done\nPrincess Mononoke — a battle between humanity and nature told through some of the most breathtaking animation ever created.\n\nFollow @senpai_clipz for more recommendations \n\n#animerecommendation #anime #movies #animemovie",
        "description": "5 anime movies that will stay with you forever.\nYour Name — two souls connected across time who spend their whole lives searching for each other without knowing why.\nSpirited Away — a young girl who enters a world beyond imagination and discovers who she truly is.\nGrave of the Fireflies — a brother who gave everything to protect his little sister during the darkest chapter of history.\nA Silent Voice — a story about the weight of words and the courage to face what you've done\nPrincess Mononoke — a battle between humanity and nature told through some of the most breathtaking animation ever created.\n\nFollow @senpai_clipz for more recommendations \n\n#animerecommendation #anime #movies #animemovie",
        "publishedAt": "2026-05-09T15:56:01Z",
        "thumbnailUrl": "https://scontent-ord5-2.cdninstagram.com/v/t51.82787-15/686428821_18073015601393899_5431269596460602743_n.webp?_nc_cat=105&ig_cache_key=Mzg5MzMzODI0ODU5Njg4MjE5OA%3D%3D.3-ccb7-5&ccb=7-5&_nc_sid=58cdad&efg=eyJ2ZW5jb2RlX3RhZyI6IkNBUk9VU0VMX0lURU0ueHBpZHMuMTA4MC5zZHIucmVndWxhcl9waG90by5DMyJ9&_nc_ohc=fd3xTiid5wcQ7kNvwE-zAT7&_nc_oc=AdobOxcN80wcgSVp1ePF6zH-b0nR5kqTFUTtKEkU2Xq24aytFCdeFh7PjdanH7Aj9oKVwOA6R4YJPWgpBoOpTMqk&_nc_ad=z-m&_nc_cid=0&_nc_zt=23&_nc_ht=scontent-ord5-2.cdninstagram.com&_nc_gid=4bDSULEL-LvNhOk3CA-9OA&_nc_ss=7a22e&oh=00_AQDRgHfGawEVfATVtpEHs6QEicT5jpsRZ23biK3xCDSxcg&oe=6A613151",
        "author": {
          "username": "senpai_clipz",
          "url": "https://instagram.com/senpai_clipz"
        },
        "engagement": {
          "likes": 34934,
          "comments": 214
        },
        "hashtags": [
          "animerecommendation",
          "anime",
          "movies",
          "animemovie"
        ],
        "mentions": [
          "senpai_clipz"
        ]
      },
      {
        "platform": "instagram",
        "url": "https://www.instagram.com/p/BufGB13BaY4/",
        "id": "1990336075151025720_6128399130",
        "postType": "Image",
        "productType": "feed",
        "section": "TV & Movies",
        "topic": "Romance TV & Movies",
        "caption": "This weekend’s TV movies! Hallmark brings back cutie Luke McFarlan & Lifetime has killers and teachers.\n.\n.\n.\n.\n.\n#weekend #tvmovies #hallmarkchannel #lifetimemovies #justaddromance #thekillerdownstairs #thewrongteacher #teacher #killer #romance #movies #mystery",
        "description": "This weekend’s TV movies! Hallmark brings back cutie Luke McFarlan & Lifetime has killers and teachers.\n.\n.\n.\n.\n.\n#weekend #tvmovies #hallmarkchannel #lifetimemovies #justaddromance #thekillerdownstairs #thewrongteacher #teacher #killer #romance #movies #mystery",
        "publishedAt": "2019-03-02T00:29:31Z",
        "thumbnailUrl": "https://scontent-ord5-2.cdninstagram.com/v/t51.82787-15/618817691_18189430942353747_6483105427935217514_n.jpg?stp=dst-jpg_e35_tt6&_nc_cat=103&ig_cache_key=MTk5MDMzNjA3NTE1MTAyNTcyMA%3D%3D.3-ccb7-5&ccb=7-5&_nc_sid=58cdad&efg=eyJ2ZW5jb2RlX3RhZyI6IkZFRUQueHBpZHMuMTA4MC5zZHIucmVndWxhcl9waG90by5DMyJ9&_nc_ohc=6FbxOe55vUoQ7kNvwGwA_GC&_nc_oc=AdpafbyW-IFKVBG27wxa2tGDH7My9oGmV8HpjUz7MbfHIFVSlU2Sg71UfkF3FggNLwJIPhFT5ipTpBI1LnUfGbiR&_nc_ad=z-m&_nc_cid=0&_nc_zt=23&_nc_ht=scontent-ord5-2.cdninstagram.com&_nc_gid=4bDSULEL-LvNhOk3CA-9OA&_nc_ss=7a22e&oh=00_AQBDlUe_2KbxMLZRCveHQjblo0k9cBVyxwsaRJ6VlQaANA&oe=6A612C9F",
        "author": {
          "username": "lifetimeuncorked",
          "url": "https://instagram.com/lifetimeuncorked"
        },
        "engagement": {
          "likes": 25,
          "comments": 0
        },
        "hashtags": [
          "weekend",
          "tvmovies",
          "hallmarkchannel",
          "lifetimemovies",
          "justaddromance"
        ],
        "mentions": []
      },
      {
        "platform": "instagram",
        "url": "https://www.instagram.com/p/DYZxoehoSko/",
        "id": "3898365238300453160_46977791697",
        "postType": "Image",
        "productType": "feed",
        "section": "TV & Movies",
        "topic": "TV & Movies Celebrities",
        "caption": "𝐓𝐡𝐢𝐬 𝐖𝐞𝐞𝐤 𝐎𝐓𝐓 𝐑𝐞𝐥𝐞𝐚𝐬𝐞 - Streaming Now 🤩🍿\n\n𝐓𝐚𝐦𝐢𝐥 \n#MrX (Tamil, Telugu, Kannada, Malayalam) - JioHotstar & SimplySouth\n\n#Kaalidas2 (Tamil) - PrimeVideo, Sunnxt, ShortFlix, SimplySouth, AhaTamil, Tentkotta & LionsGatePlay\n\n𝐓𝐞𝐥𝐮𝐠𝐮\n#Anaganaga (Telugu, Tamil, Kannada, Malayalam, Hindi) - ETvWin \n\n#ThimmarajupalliTV (Telugu, Tamil) - AhaVideo\n\n𝐌𝐚𝐥𝐚𝐲𝐚𝐥𝐚𝐦\n#OruDuroohaSaahacharyathil (Malayalam) - Netflix\n\nDerby (Malayalam) - PrimeVideo, SimplySouth\n\n𝐇𝐢𝐧𝐝𝐢\nD-h-u-r-a-n-d-h-a-r : The Revenge (Hindi, Tamil, Telugu, Kannada, Malayalam) - Netflix (Outside India)\n\nKartavya (Hindi, Tamil, Telugu, English) - Netflix\n\n𝐌𝐚𝐫𝐚𝐭𝐡𝐢\nTighee (Marathi) - Zee5\n\n𝐄𝐧𝐠𝐥𝐢𝐬𝐡\nMartySupreme (English, Tamil, Telugu, Hindi) - PrimeVideo\n\nOffCampus 🥵 (English, Tamil, Telugu, Kannada, Malayalam, Hindi) [Series] - PrimeVideo\n\nThePunisher: One Last Kill (English) - JioHotstar",
        "description": "𝐓𝐡𝐢𝐬 𝐖𝐞𝐞𝐤 𝐎𝐓𝐓 𝐑𝐞𝐥𝐞𝐚𝐬𝐞 - Streaming Now 🤩🍿\n\n𝐓𝐚𝐦𝐢𝐥 \n#MrX (Tamil, Telugu, Kannada, Malayalam) - JioHotstar & SimplySouth\n\n#Kaalidas2 (Tamil) - PrimeVideo, Sunnxt, ShortFlix, SimplySouth, AhaTamil, Tentkotta & LionsGatePlay\n\n𝐓𝐞𝐥𝐮𝐠𝐮\n#Anaganaga (Telugu, Tamil, Kannada, Malayalam, Hindi) - ETvWin \n\n#ThimmarajupalliTV (Telugu, Tamil) - AhaVideo\n\n𝐌𝐚𝐥𝐚𝐲𝐚𝐥𝐚𝐦\n#OruDuroohaSaahacharyathil (Malayalam) - Netflix\n\nDerby (Malayalam) - PrimeVideo, SimplySouth\n\n𝐇𝐢𝐧𝐝𝐢\nD-h-u-r-a-n-d-h-a-r : The Revenge (Hindi, Tamil, Telugu, Kannada, Malayalam) - Netflix (Outside India)\n\nKartavya (Hindi, Tamil, Telugu, English) - Netflix\n\n𝐌𝐚𝐫𝐚𝐭𝐡𝐢\nTighee (Marathi) - Zee5\n\n𝐄𝐧𝐠𝐥𝐢𝐬𝐡\nMartySupreme (English, Tamil, Telugu, Hindi) - PrimeVideo\n\nOffCampus 🥵 (English, Tamil, Telugu, Kannada, Malayalam, Hindi) [Series] - PrimeVideo\n\nThePunisher: One Last Kill (English) - JioHotstar",
        "publishedAt": "2026-05-16T14:23:40Z",
        "thumbnailUrl": "https://scontent-ord5-3.cdninstagram.com/v/t51.82787-15/700658142_18081480737567698_3872474111160457300_n.jpg?stp=dst-jpg_e35_tt6&_nc_cat=107&ig_cache_key=Mzg5ODM2NTIzODMwMDQ1MzE2MA%3D%3D.3-ccb7-5&ccb=7-5&_nc_sid=58cdad&efg=eyJ2ZW5jb2RlX3RhZyI6IkZFRUQueHBpZHMuMzIwMC5zZHIucmVndWxhcl9waG90by5DMyJ9&_nc_ohc=P7hDocBNdmwQ7kNvwHZRpyP&_nc_oc=AdoNQ5EHi60OD4yvx3IrrmrYRH0SSMJAxmDVAEq9E0Fr59zGKaVfxeKprLuXjrIr9gNoOIH6V6LxKahY29Zg3bMe&_nc_ad=z-m&_nc_cid=0&_nc_zt=23&_nc_ht=scontent-ord5-3.cdninstagram.com&_nc_gid=4bDSULEL-LvNhOk3CA-9OA&_nc_ss=7a22e&oh=00_AQBzl7J3U-v9s_Sd458kqi2vFpjWtUj536RFjPdww0Dp8A&oe=6A611EE8",
        "author": {
          "username": "boxofficesouthindian",
          "url": "https://instagram.com/boxofficesouthindian"
        },
        "engagement": {
          "likes": 2094,
          "comments": 6
        },
        "hashtags": [
          "MrX",
          "Kaalidas2",
          "Anaganaga",
          "ThimmarajupalliTV",
          "OruDuroohaSaahacharyathil"
        ],
        "mentions": []
      }
    ]
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
    "url": "https://komi.io/ksi",
    "username": "ksi",
    "name": "KSI",
    "firstName": "KSI",
    "lastName": "Olatunji",
    "avatar": "https://komi-production-assets.s3.amazonaws.com/photos/OsqFjkXZxCB6vsUAyuLtm.jpeg",
    "linkCount": 7,
    "links": [
      {
        "title": "INSTAGRAM",
        "url": "https://www.instagram.com/ksi",
        "type": "INSTAGRAM"
      },
      {
        "title": "FACEBOOK",
        "url": "https://www.facebook.com/KSIOlajidebt",
        "type": "FACEBOOK"
      },
      {
        "title": "TWITTER",
        "url": "https://twitter.com/KSI",
        "type": "TWITTER"
      },
      {
        "title": "YOUTUBE",
        "url": "https://www.youtube.com/c/ksi",
        "type": "YOUTUBE"
      },
      {
        "title": "SPOTIFY",
        "url": "https://open.spotify.com/artist/1nzgtKYFckznkcVMR3Gg4z?si=0pADGmEwS1iluryfgiIy8Q",
        "type": "SPOTIFY"
      },
      {
        "title": "APPLE_MUSIC",
        "url": "https://music.apple.com/gb/artist/ksi/489704062",
        "type": "APPLE_MUSIC"
      },
      {
        "title": "WEBSITE",
        "url": "https://www.sidemen.com/",
        "type": "WEBSITE"
      }
    ],
    "socials": {
      "instagram": "https://www.instagram.com/ksi",
      "facebook": "https://www.facebook.com/KSIOlajidebt",
      "twitter": "https://twitter.com/KSI",
      "youtube": "https://www.youtube.com/c/ksi",
      "spotify": "https://open.spotify.com/artist/1nzgtKYFckznkcVMR3Gg4z?si=0pADGmEwS1iluryfgiIy8Q",
      "appleMusic": "https://music.apple.com/gb/artist/ksi/489704062"
    }
  },
  "kwai-post": {
    "platform": "kwai",
    "id": "5240932700689736196",
    "url": "https://www.kwai.com/@topfilmeseseriesnatv/video/5240932700689736196",
    "text": "...",
    "transcript": "BANDIDO ESTAVA ESPERANDO ELE NA SAIDA DO BANCOBANDIDO ESTAVA ESPERANDO ELE NA SAIDA DO BANCO.",
    "publishedAt": "2026-01-24T00:50:13Z",
    "durationSeconds": 156,
    "thumbnailUrl": "https://aws-br-pic.kwai.net/upic/2026/01/24/08/BMjAyNjAxMjQwODQ4MTNfMTUwMDAxNDU1MDE5OTQ1XzE1MDExMDI4NTA4NDg3NF8yXzM=_oscn2_Befd2f922b58f2b5f72e4cb3c375d043d.webp",
    "videoUrl": "https://aws-br-cdn.kwai.net/upic/2026/01/24/08/BMjAyNjAxMjQwODQ4MTNfMTUwMDAxNDU1MDE5OTQ1XzE1MDExMDI4NTA4NDg3NF8yXzM=_b_Bf1ce0ec42b4fe4482cd50678b3abd2d4.mp4?tag=1-1784753172-s-0-afgxvdpz8w-4a78f339bd4accdf",
    "author": {
      "id": "3x9mhse7ekkvfa9",
      "username": "topfilmeseseriesnatv",
      "displayName": "Topseriesfilmetv",
      "avatar": "https://aws-br-pic.kwai.net/bs2/overseaHead/20250507231107_BMTUwMDAxNDU1MDE5OTQ1_t.jpg",
      "url": "https://www.kwai.com/@topfilmeseseriesnatv"
    },
    "engagement": {
      "views": 138841,
      "likes": 9232,
      "comments": 91,
      "shares": 169
    }
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
    "isPrivate": false
  },
  "kwai-user-posts": {
    "profileUrl": "https://www.kwai.com/@topfilmeseseriesnatv",
    "totalReturned": 5,
    "posts": [
      {
        "platform": "kwai",
        "id": "5240932700689736196",
        "url": "https://www.kwai.com/@topfilmeseseriesnatv/video/5240932700689736196",
        "text": "...",
        "transcript": "BANDIDO ESTAVA ESPERANDO ELE NA SAIDA DO BANCOBANDIDO ESTAVA ESPERANDO ELE NA SAIDA DO BANCO.",
        "publishedAt": "2026-01-24T00:50:13Z",
        "durationSeconds": 156,
        "thumbnailUrl": "https://aws-br-pic.kwai.net/upic/2026/01/24/08/BMjAyNjAxMjQwODQ4MTNfMTUwMDAxNDU1MDE5OTQ1XzE1MDExMDI4NTA4NDg3NF8yXzM=_oscn2_Befd2f922b58f2b5f72e4cb3c375d043d.webp",
        "videoUrl": "https://aws-br-cdn.kwai.net/upic/2026/01/24/08/BMjAyNjAxMjQwODQ4MTNfMTUwMDAxNDU1MDE5OTQ1XzE1MDExMDI4NTA4NDg3NF8yXzM=_b_Bf1ce0ec42b4fe4482cd50678b3abd2d4.mp4?tag=1-1784753172-s-0-afgxvdpz8w-4a78f339bd4accdf",
        "author": {
          "id": "3x9mhse7ekkvfa9",
          "username": "topfilmeseseriesnatv",
          "displayName": "Topseriesfilmetv",
          "avatar": "https://aws-br-pic.kwai.net/bs2/overseaHead/20250507231107_BMTUwMDAxNDU1MDE5OTQ1_t.jpg",
          "url": "https://www.kwai.com/@topfilmeseseriesnatv"
        },
        "engagement": {
          "views": 138841,
          "likes": 9232,
          "comments": 91,
          "shares": 169
        }
      },
      {
        "platform": "kwai",
        "id": "5197304080333126332",
        "url": "https://www.kwai.com/@topfilmeseseriesnatv/video/5197304080333126332",
        "text": "...",
        "publishedAt": "2026-07-21T01:41:02Z",
        "durationSeconds": 125,
        "thumbnailUrl": "https://p16-kimg.kwai.net/kimg/EKzM1y8qmQEKAnMzEg1waG90by1vdmVyc2VhGoMBdXBpYy8yMDI2LzA3LzIxLzAxL0JNakF5TmpBM01qRXdNVFF3TVRCZk1UVXdNREF4TkRVMU1ERTVPVFExWHpFMU1ERXhNVEUwTlRFMU9UUTBNRjh5WHpNPV9vdXVfQjVkMzdmMDZiZTFmMmU5NjQ0MGNkNjhhMjc3ZTg1MjRlLndlYnA.webp",
        "videoUrl": "https://aws-br-cdn.kwai.net/upic/2026/07/21/01/BMjAyNjA3MjEwMTQwMTBfMTUwMDAxNDU1MDE5OTQ1XzE1MDExMTE0NTE1OTQ0MF8yXzM=_b_B9e078740aaad1692190abe5e2e2e61c6.mp4?tag=1-1784753179-s-0-46g59inljw-0d434501e8fb5c1c",
        "author": {
          "id": "3x9mhse7ekkvfa9",
          "username": "topfilmeseseriesnatv",
          "displayName": "Topseriesfilmetv",
          "avatar": "https://aws-br-pic.kwai.net/bs2/overseaHead/20250507231107_BMTUwMDAxNDU1MDE5OTQ1_tw.webp",
          "url": "https://www.kwai.com/@topfilmeseseriesnatv"
        },
        "engagement": {
          "views": 8998,
          "likes": 441,
          "comments": 7,
          "shares": 16
        }
      },
      {
        "platform": "kwai",
        "id": "5227421903765456876",
        "url": "https://www.kwai.com/@topfilmeseseriesnatv/video/5227421903765456876",
        "text": "#ZorraTotal",
        "publishedAt": "2026-07-19T08:28:52Z",
        "durationSeconds": 44,
        "thumbnailUrl": "https://aws-br-pic.kwai.net/upic/2026/07/19/08/BMjAyNjA3MTkwODI4MzVfMTUwMDAxNDU1MDE5OTQ1XzE1MDExMTEzNzQ3NjIyNV8yXzM=_oscn2_Bd317dff3b8f0f93053698bca28b4ed31.webp",
        "videoUrl": "https://aws-br-cdn.kwai.net/upic/2026/07/19/08/BMjAyNjA3MTkwODI4MzVfMTUwMDAxNDU1MDE5OTQ1XzE1MDExMTEzNzQ3NjIyNV8yXzM=_b_Bb5b74479ac0bb2b14712dd1bca99f12f.mp4?tag=1-1784753179-s-0-difmieeh24-c9d6d04a70b198e6",
        "author": {
          "id": "3x9mhse7ekkvfa9",
          "username": "topfilmeseseriesnatv",
          "displayName": "Topseriesfilmetv",
          "avatar": "https://aws-br-pic.kwai.net/bs2/overseaHead/20250507231107_BMTUwMDAxNDU1MDE5OTQ1_tw.webp",
          "url": "https://www.kwai.com/@topfilmeseseriesnatv"
        },
        "engagement": {
          "views": 4064,
          "likes": 236,
          "comments": 3,
          "shares": 2
        }
      },
      {
        "platform": "kwai",
        "id": "5217570279939826842",
        "url": "https://www.kwai.com/@topfilmeseseriesnatv/video/5217570279939826842",
        "text": "...",
        "publishedAt": "2026-07-21T05:13:21Z",
        "durationSeconds": 40,
        "thumbnailUrl": "https://aws-br-pic.kwai.net/upic/2026/07/21/05/BMjAyNjA3MjEwNTEzMDhfMTUwMDAxNDU1MDE5OTQ1XzE1MDExMTE0NTg5NzI1NV8yXzM=_oscn2_B738481f7686349213ede76436f8269a7.webp",
        "videoUrl": "https://aws-br-cdn.kwai.net/upic/2026/07/21/05/BMjAyNjA3MjEwNTEzMDhfMTUwMDAxNDU1MDE5OTQ1XzE1MDExMTE0NTg5NzI1NV8yXzM=_b_B997df5f2c06f222fd72be8ae19406143.mp4?tag=1-1784753179-s-0-nl283rewpv-f048203b60d766d3",
        "author": {
          "id": "3x9mhse7ekkvfa9",
          "username": "topfilmeseseriesnatv",
          "displayName": "Topseriesfilmetv",
          "avatar": "https://aws-br-pic.kwai.net/bs2/overseaHead/20250507231107_BMTUwMDAxNDU1MDE5OTQ1_tw.webp",
          "url": "https://www.kwai.com/@topfilmeseseriesnatv"
        },
        "engagement": {
          "views": 1944,
          "likes": 86,
          "comments": 2,
          "shares": 6
        }
      },
      {
        "platform": "kwai",
        "id": "5210533406153142423",
        "url": "https://www.kwai.com/@topfilmeseseriesnatv/video/5210533406153142423",
        "text": "...",
        "publishedAt": "2026-07-21T04:48:58Z",
        "durationSeconds": 124,
        "thumbnailUrl": "https://p1-kimg.kwai.net/kimg/EKzM1y8qmQEKAnMzEg1waG90by1vdmVyc2VhGoMBdXBpYy8yMDI2LzA3LzIxLzA0L0JNakF5TmpBM01qRXdORFE0TURSZk1UVXdNREF4TkRVMU1ERTVPVFExWHpFMU1ERXhNVEUwTlRnd09UVTNORjh5WHpNPV9vdXVfQjAxNmY3NTlkNjVkOGJiNWZjNmNjNmExZTNmODBiOThkLndlYnA.webp",
        "videoUrl": "https://aws-br-cdn.kwai.net/upic/2026/07/21/04/BMjAyNjA3MjEwNDQ4MDRfMTUwMDAxNDU1MDE5OTQ1XzE1MDExMTE0NTgwOTU3NF8yXzM=_b_B4d8d80659d6efea357399c8f82843875.mp4?tag=1-1784753179-s-0-ilwmazqyjf-c8d63120fe70f928",
        "author": {
          "id": "3x9mhse7ekkvfa9",
          "username": "topfilmeseseriesnatv",
          "displayName": "Topseriesfilmetv",
          "avatar": "https://aws-br-pic.kwai.net/bs2/overseaHead/20250507231107_BMTUwMDAxNDU1MDE5OTQ1_tw.webp",
          "url": "https://www.kwai.com/@topfilmeseseriesnatv"
        },
        "engagement": {
          "views": 601,
          "likes": 38,
          "comments": 0,
          "shares": 1
        }
      }
    ]
  },
  "linkbio-page": {
    "platform": "linkbio",
    "url": "https://lnk.bio/charlidamelio",
    "username": "charlidamelio",
    "name": "@charlidamelio",
    "avatar": "https://s3.us-west-2.amazonaws.com/cdn.lnk.bio/profilepics/-1344625_20220123667.jpg",
    "linkCount": 8,
    "socials": {
      "facebook": "https://facebook.com/thecharlidamelio",
      "twitter": "https://twitter.com/charlidamelio",
      "instagram": "https://instagram.com/charlidamelio",
      "tiktok": "https://tiktok.com/@charlidamelio",
      "youtube": "https://youtube.com/c/charlidamelio",
      "snapchat": "https://www.snapchat.com/add/damelioc"
    },
    "links": [
      {
        "url": "https://www.charlidamelio.com",
        "title": "official website of charli d'amelio"
      },
      {
        "url": "https://facebook.com/thecharlidamelio",
        "title": null
      },
      {
        "url": "https://twitter.com/charlidamelio",
        "title": null
      },
      {
        "url": "https://instagram.com/charlidamelio",
        "title": null
      },
      {
        "url": "https://triller.co/m/@charlidamelio",
        "title": null
      },
      {
        "url": "https://tiktok.com/@charlidamelio",
        "title": null
      },
      {
        "url": "https://youtube.com/c/charlidamelio",
        "title": null
      },
      {
        "url": "https://www.snapchat.com/add/damelioc",
        "title": null
      }
    ]
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
      },
      {
        "country": "United Kingdom",
        "impressions": "less than 1%"
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
          },
          {
            "country": "United Kingdom",
            "impressions": "less than 1%"
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
      },
      {
        "platform": "linkedin_ad_library",
        "id": "1527291136",
        "url": "https://www.linkedin.com/ad-library/detail/1527291136",
        "text": "See how Rhenus scaled secure IT automation",
        "headline": "See how Rhenus scaled secure IT automation",
        "cta": null,
        "landingUrl": null,
        "adFormat": null,
        "firstShown": null,
        "lastShown": null,
        "impressions": null,
        "country": "US",
        "advertiser": {
          "name": "See how Rhenus scaled secure IT automation"
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
    "url": "https://www.linkedin.com/company/microsoft",
    "name": "Microsoft",
    "industry": null,
    "description": "Every company has a mission. What's ours? To empower every person and every organization to achieve more. We believe technology can and should be a force for good and that meaningful innovation contributes to a brighter world in the future and today. Our culture doesn’t just encourage curiosity; it embraces it. Each day we make progress together by showing up as our authentic selves. We show up with a learn-it-all mentality. We show up cheering on others, knowing their success doesn't diminish our own. We show up every day open to learning our own biases, changing our behavior, and inviting in differences. Because impact matters. \n\nMicrosoft operates in 190 countries and is made up of approximately 228,000 passionate employees worldwide.",
    "website": "https://news.microsoft.com/",
    "followers": 28741583,
    "employees": 233242,
    "headquarters": "Redmond, Washington, US",
    "logo": "https://media.licdn.com/dms/image/v2/D560BAQH32RJQCl3dDQ/company-logo_200_200/B56ZYQ0mrGGoAM-/0/1744038948046/microsoft_logo?e=2147483647&v=beta&t=ts9MGrTk7Lz3R1bmAfzCL8euuuuPWPCoXfdiLA2_IzM"
  },
  "linkedin-company-posts": {
    "company": "microsoft",
    "totalReturned": 1,
    "posts": [
      {
        "platform": "linkedin",
        "type": "post",
        "url": "https://www.linkedin.com/posts/microsoft_june-activity-7477715981667086336-BV_s",
        "text": "The most meaningful breakthroughs happen when technology is built with people in mind.\n \nThat was the message at Microsoft Build this month, where we announced a host of new tools to help developers build, dream and create. \n \nIn June’s edition of The Monthly Tech-In, we’re sharing stories from Build and beyond about the developers, founders and communities who are using AI to tackle real-world challenges, from helping creators protect their work to advancing more inclusive AI systems.\n \nRead more about the people and innovations who are shaping what's next:",
        "publishedAt": "2026-06-30T13:33:39.256Z",
        "author": {
          "name": "Microsoft",
          "url": "https://www.linkedin.com/company/microsoft"
        },
        "id": "7477715981667086336"
      }
    ]
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
    "transcript": "The most meaningful breakthroughs happen when technology is built with people in mind.\n \nThat was the message at Microsoft Build this month, where we announced a host of new tools to help developers build, dream and create. \n \nIn June’s edition of The Monthly Tech-In, we’re sharing stories from Build and beyond about the developers, founders and communities who are using AI to tackle real-world challenges, from helping creators protect their work to advancing more inclusive AI systems.\n \nRead more about the people and innovations who are shaping what's next:",
    "transcriptSegments": [
      {
        "text": "The most meaningful breakthroughs happen when technology is built with people in mind.\n \nThat was the message at Microsoft Build this month, where we announced a host of new tools to help developers build, dream and create. \n \nIn June’s edition of The Monthly Tech-In, we’re sharing stories from Build and beyond about the developers, founders and communities who are using AI to tackle real-world challenges, from helping creators protect their work to advancing more inclusive AI systems.\n \nRead more about the people and innovations who are shaping what's next:",
        "start": 0,
        "duration": 0,
        "timestamp": "00:00"
      }
    ],
    "wordCount": 89,
    "segments": 1,
    "author": {
      "name": "Microsoft",
      "headline": "28,652,029 followers",
      "url": "https://www.linkedin.com/company/microsoft/posts"
    },
    "publishedAt": "2026-07-04 13:19:24"
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
        "text": "AI is a tool. \n\nWe need to remember that because it presents as intelligence. But intelligence is sentient.\n\nThat’s why we call it *artificial* intelligence \n\nIt’s artificial because ai only appears to create meaning. \n\nIn fact, there can be no meaning created by ai. \n\nMeaning only ever persists in the humans who engage with ai. (Meaning is the unique condition of being human).  \n\nThink of ai as a ‘magic mirror’ or an ‘echo chamber’. It returns our words and images to us with heightened grandeur and clarity.\n\nI’m grateful for AI. \n\nAi can help with the task of route optimization or translation.\n\nBut it cannot establish whether the destination is worth getting to, or whether the translated text is moving (for that someone needs to be moved). \n\nSo what? \n\nRemembering that this intelligence is artificial helps us delineate what within the province of human productivity cannot for structural reasons be substituted for by ai.\n\nThis is because human beings value intelligence (sentience) in the realm of productivity.\n\nI return to my chosen advisor (broker, therapist, architect) not just because they produce the right words or images, but because they hold me in their care.\n\nIn some industries, this grounding in relationship is at the heart of productive value. \n\nIn these industries, the goal of AI is to release the full productive value of these relationships.\n\nWhen we think like this, AI allows us to celebrate the human as well as the artificial.",
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
      },
      {
        "platform": "linkedin",
        "type": "post",
        "url": "https://www.linkedin.com/posts/arthur-c-brooks_artificial-intelligence-is-changing-the-world-activity-7467623521242972160-giS5",
        "text": "Artificial intelligence is changing the world at extraordinary speed. But the most important question isn't what AI can do. It's what it means for us to remain fully human.\n\nIt was a pleasure to sit down with Fr. Mike Schmitz to discuss Pope Leo XIV's new encyclical on artificial intelligence, human dignity, meaning, faith, and the responsibilities we face as this technology becomes more powerful. Together, we explored how technology shapes our attention, our relationships, and ultimately our understanding of what it means to be a person.\n\nThe conversation isn't really about AI. It's about us. You can watch the full conversation here: https://lnkd.in/etTUpfFj",
        "publishedAt": "2026-06-02T17:09:49.184Z",
        "author": {
          "name": "Dr. Arthur Brooks",
          "url": "https://www.linkedin.com/in/arthur-c-brooks"
        },
        "engagement": {
          "likes": 573,
          "comments": 30
        },
        "id": "7467623521242972160"
      },
      {
        "platform": "linkedin",
        "type": "post",
        "url": "https://www.linkedin.com/posts/lukas-althoff-a57756a3_artificial-intelligence-is-enabling-people-activity-7481386565726937088-ZF9q",
        "text": "Artificial Intelligence is enabling people to do things they were not able to do before. \n\nA short personal anecdote: My mum wrote her first book a few years ago. Without any experience, she submitted it to a few publishers and was rejected. She recently learned to use AI's help in spell-checking, layout design, and self-publish her book.\n\nMany of us have stories like my mum's. And our research paper provides a rigorous basis for optimism that these anecdotes will add up to AI working as an equalizer in the labor market, helping lower-skilled workers compete with higher-skilled ones more effectively.",
        "publishedAt": "2026-07-10T16:39:14.695Z",
        "author": {
          "name": "Lukas Althoff",
          "url": "https://www.linkedin.com/in/lukas-althoff-a57756a3"
        },
        "engagement": {
          "likes": 63,
          "comments": 1
        },
        "id": "7481386565726937088"
      },
      {
        "platform": "linkedin",
        "type": "post",
        "url": "https://www.linkedin.com/posts/addyosmani_ai-leadership-motivation-activity-7397899139424043008-SPz7",
        "text": "\"Critical thinking in the age of AI\": human critical thinking still matters\n\nMy latest article: https://lnkd.in/gHzdswnW\n\nCritical thinking has never mattered more than it does in this AI-heavy chapter of our industry. We can ask an assistant to generate code, propose a system design, or summarize a problem in seconds, but none of that replaces the human ability to question, verify, and think independently.\n\nIn my latest newsletter, I explore how to apply this classic framework to AI:\n\n✅ Who: Don’t rely on AI as an oracle. Treat it like a junior intern and verify the output.\n\n✅ What: Define the real problem before rushing to a solution. Don't just fix the symptom.\n\n✅ Where: Context is king. A fix that works in a sandbox might break in production.\n\n✅ When: Know the difference between a quick triage (heuristic) and a deep root-cause analysis.\n\n✅ Why: Use the \"5 Whys\" technique to uncover underlying causes, not just surface-level issues.\n\n✅ How: Communicate with evidence and data, not just opinions or \"gut feelings.\"\n\nThe goal isn't to stop using AI, but to pair it with \"humble curiosity\" - the willingness to ask if we might be missing something.\n\nThe more we rely on AI to accelerate the work, the more important this mindset becomes. Critical thinking is what keeps us honest. It keeps us from shipping band-aids. It helps us avoid chasing trendy ideas that don’t solve real user problems. And it keeps our teams aligned on the decisions that matter.\n\n#ai #leadership #motivation #programming #lifeatgoogle",
        "publishedAt": "2025-11-22T07:30:01.114Z",
        "author": {
          "name": "Addy Osmani",
          "url": "https://www.linkedin.com/in/addyosmani"
        },
        "engagement": {
          "likes": 325,
          "comments": 21
        },
        "id": "7397899139424043008"
      }
    ]
  },
  "linkme-profile": {
    "platform": "linkme",
    "url": "https://link.me/kevinhart",
    "username": "kevinhart",
    "name": "Check out Kevin Hart (@kevinhart) on Linkme",
    "firstName": "Kevin",
    "lastName": "Hart",
    "description": "Discover Kevin Hart on LinkMe: Connect and see what they're passionate about.",
    "avatar": "https://media.link.me/_resize/image/quality=90,format=webp/images/default/profile/avatar-2.png",
    "linkCount": 2,
    "links": [
      {
        "title": "Privacy Policy",
        "url": "https://about.link.me/privacypolicy"
      },
      {
        "title": "Terms",
        "url": "https://about.link.me/termsandconditions"
      }
    ]
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
      "creative",
      "arts-entertainment"
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
      },
      {
        "title": "watch \"INNOCENCE\" video",
        "type": "YOUTUBE_VIDEO",
        "id": "460285424",
        "url": "https://www.youtube.com/watch?v=JINmh9O-sjU",
        "thumbnail": "https://ugc.production.linktr.ee/49049fb3-97fb-4947-b847-46c9c2f84384_maxresdefault.jpeg"
      },
      {
        "title": "stream \"OBSESSED\"",
        "type": "SPOTIFY_SONG",
        "id": "460281376",
        "url": "https://open.spotify.com/track/0ipHYEQf07qoReAWhVC3zO?si=8fbaee843716443f",
        "thumbnail": "https://ugc.production.linktr.ee/8459222c-2e13-47c2-8827-55f6a4af585d_ab67616d0000b273fbf50ee1e8be73b31fa177e2.jpeg"
      },
      {
        "title": "MERCH",
        "type": "PRODUCT",
        "id": "233892723",
        "thumbnail": "https://ugc.production.linktr.ee/b59a3236-2d8a-4704-9c8b-16eb7acd44cb_embrace-chaos-hatv1.jpeg"
      },
      {
        "title": "ALL STREAMING LINKS",
        "type": "CLASSIC",
        "id": "233894119",
        "url": "https://songwhip.com/miguelangeles"
      },
      {
        "title": "SPOTIFY PLAYLIST",
        "type": "CLASSIC",
        "id": "80367589",
        "url": "https://open.spotify.com/playlist/1m0U7ud6CCPzMO8oLTMi3B?si=d7cb7f6e6bc94d3b",
        "thumbnail": "https://ugc.production.linktr.ee/aPvlFMFwRO6UxX7z7Ajb_95C7BCA3-481E-426C-8EEC-E4C868C6C79D.jpg"
      },
      {
        "title": "SOUNDCLOUD PLAYLIST",
        "type": "SOUNDCLOUD_PLAYLIST",
        "id": "102824974",
        "url": "https://soundcloud.com/miguelangeles/sets/irl-angel-vibes",
        "thumbnail": "https://ugc.production.linktr.ee/dspU8yloQW2ViLu1ZNGA_7B24137C-D995-425C-8670-45D8EEFBBBF5.JPG"
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
      },
      {
        "type": "SPOTIFY",
        "url": "https://open.spotify.com/artist/14xRX3JR8H4RWh8R7V3fvZ?si=EgRxWIPiRcaEHtSnqk5PAQ"
      },
      {
        "type": "YOUTUBE",
        "url": "https://www.youtube.com/watch?v=xiFUzOJaiC4"
      },
      {
        "type": "SOUNDCLOUD",
        "url": "https://soundcloud.com/miguelangeles"
      },
      {
        "type": "APPLE_MUSIC",
        "url": "https://music.apple.com/ca/artist/miguel-angeles/1209423162"
      },
      {
        "type": "EMAIL_ADDRESS",
        "url": "mailto:miguel@irlangel.com"
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
    "url": "https://pillar.io/example",
    "username": "example",
    "name": "Example Creator",
    "description": "Creator bio",
    "linkCount": 2,
    "links": [
      {
        "title": "Website",
        "url": "https://example.com"
      },
      {
        "title": "YouTube",
        "url": "https://www.youtube.com/@example"
      }
    ]
  },
  "pinterest-board": {
    "board": "https://www.pinterest.com/potterybarn/rustic-lodge-lookbook/",
    "totalReturned": 4,
    "pins": [
      {
        "platform": "pinterest",
        "id": "264938390611768286",
        "url": "https://www.pinterest.com/pin/264938390611768286/",
        "description": "Our Rockport Metal Rectangular Outdoor Dining Table is the perfect table to gather around, share everyday meals, and create everlasting memories. Layer with your favorite dinnerware, table linens, and decor. Tap to shop our table.",
        "destinationUrl": "https://www.potterybarn.com/pages/lookbook/fall/rustic-lodge/?cm_ven=OrganicSocial&amp;cm_cat=Pinterest&amp;cm_pla=stpin&amp;cm_ite=rusticlodgeoutdoordining",
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
        "destinationUrl": "https://www.potterybarn.com/pages/lookbook/fall/rustic-lodge/?cm_ven=OrganicSocial&amp;cm_cat=Pinterest&amp;cm_pla=stpin&amp;cm_ite=rusticlodgeblankets",
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
      },
      {
        "platform": "pinterest",
        "id": "264938390611768272",
        "url": "https://www.pinterest.com/pin/264938390611768272/",
        "description": "Soft plaid flannel meets rustic design to create a table setting that's warm, welcoming, and made for gathering. Layer plaid table linens with timeless dinnerware and natural textures for a cozy fall table. Tap to shop one of our favorite table settings.",
        "destinationUrl": "https://www.potterybarn.com/pages/lookbook/fall/rustic-lodge/?cm_ven=OrganicSocial&amp;cm_cat=Pinterest&amp;cm_pla=stpin&amp;cm_ite=rusticlodgetablesetting",
        "image": "https://i.pinimg.com/564x/5a/ae/12/5aae12341bb187a4053a9ced43e2f700.jpg",
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
        "id": "264938390611768263",
        "url": "https://www.pinterest.com/pin/264938390611768263/",
        "description": "Bring subtle color and rich texture to your living room sofa by layering our mix of decorative throw pillows. Mix prints, patterns, and soft textures to create a living room that feels collected, cozy, and timeless.",
        "destinationUrl": "https://www.potterybarn.com/pages/lookbook/fall/rustic-lodge/?cm_ven=OrganicSocial&amp;cm_cat=Pinterest&amp;cm_pla=stpin&amp;cm_ite=rusticlodgepillows",
        "image": "https://i.pinimg.com/564x/13/37/dd/1337dd421b303196c96002b735618cc3.jpg",
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
      },
      {
        "platform": "pinterest",
        "id": "1128996200361011408",
        "url": "https://www.pinterest.com/pin/1128996200361011408/",
        "title": "The Missing Piece In Your Living Room Might Be Lighting",
        "description": "Great rooms aren't always filled with more furniture — they often have better lighting ✨\n\nThis elegant floor lamp brings warmth, depth, and character to a space while creating the cozy glow that makes a home feel welcoming. It's perfect for anyone searching for floor lamp aesthetic inspiration, home lighting ideas for living rooms, or a statement piece that instantly upgrades the vibe.\n\nIf you love beautiful interiors and easy decorating ideas, you can find the full details in the link 🤍",
        "destinationUrl": "https://www.ebay.com/itm/137021246378?amdata=enc:AQALAAAAoGfYFPkwiKCW4ZNSs2u11xDAO/sD8pUVTTSi6RT2Xikfuo2Dp8t0xbVTehCaXCERik/Rgu9Q8sdVVpQCXAL2xlyMzPWbz2UFMg7JonjwH2b2hpLpVb1Lu0F7HZ%2BnBbVjYQU1mAGtivLje06cloH25c%2BbtTRVjzKeMbmpKyPVEIuQn2v95m%2BFd67bxNmI7DBEkfZ5WChdGmtik28CuQk2nWE%3D&mkcid=1&mkrid=711-53200-19255-0&siteid=0&campid=5339156686&customid=Kogadecor&toolid=10001&mkevt=1",
        "image": "https://i.pinimg.com/originals/b6/50/5e/b6505ec536a038c53dd960c4554c682b.png",
        "saves": 1,
        "publishedAt": "Wed, 24 Jun 2026 12:49:49 +0000",
        "board": {
          "name": "Aesthetic Home Lighting",
          "url": "https://www.pinterest.com/kogadecor/aesthetic-home-lighting/"
        },
        "author": {
          "username": "kogadecor",
          "displayName": "KOGA",
          "followers": 0
        }
      },
      {
        "platform": "pinterest",
        "id": "Rp8MMDIq",
        "url": "https://www.pinterest.com/pin/Rp8MMDIq/"
      },
      {
        "platform": "pinterest",
        "id": "-8702786212179256373",
        "url": "https://www.pinterest.com/pin/-8702786212179256373/"
      }
    ]
  },
  "pinterest-user-boards": {
    "username": "potterybarn",
    "totalReturned": 5,
    "boards": [
      {
        "platform": "pinterest",
        "id": "264938459268358699",
        "name": "Rustic Lodge Lookbook",
        "url": "https://www.pinterest.com/potterybarn/rustic-lodge-lookbook/",
        "pinCount": 4,
        "followers": 1021565,
        "owner": {
          "username": "potterybarn"
        }
      },
      {
        "platform": "pinterest",
        "id": "264938459268357928",
        "name": "Indigo Blues Lookbook",
        "url": "https://www.pinterest.com/potterybarn/indigo-blues-lookbook/",
        "privacy": "public",
        "pinCount": 24,
        "followers": 1021565,
        "sectionCount": 0,
        "coverImage": "https://i.pinimg.com/200x150/01/5d/31/015d313e6442e20b89dae9bf5aa3bb1b.jpg",
        "createdAt": "Thu, 09 Jul 2026 15:50:19 +0000",
        "owner": {
          "username": "potterybarn",
          "displayName": "Pottery Barn"
        }
      },
      {
        "platform": "pinterest",
        "id": "264938459268356753",
        "name": "The Kittles' Cozy Cabin Transformation",
        "url": "https://www.pinterest.com/potterybarn/the-kittles-cozy-cabin-transformation/",
        "privacy": "public",
        "pinCount": 16,
        "followers": 1021565,
        "sectionCount": 0,
        "coverImage": "https://i.pinimg.com/200x150/7e/8a/91/7e8a91975886b50e4cf66f1bf02542c4.jpg",
        "createdAt": "Thu, 11 Jun 2026 21:19:19 +0000",
        "owner": {
          "username": "potterybarn",
          "displayName": "Pottery Barn"
        }
      },
      {
        "platform": "pinterest",
        "id": "264938459268356442",
        "name": "4th of July Shop",
        "url": "https://www.pinterest.com/potterybarn/4th-of-july-shop/",
        "privacy": "public",
        "pinCount": 33,
        "followers": 1021565,
        "sectionCount": 0,
        "coverImage": "https://i.pinimg.com/200x150/8a/f2/46/8af2469b8a63acbaa4f49d724c37a360.jpg",
        "createdAt": "Wed, 03 Jun 2026 19:22:23 +0000",
        "owner": {
          "username": "potterybarn",
          "displayName": "Pottery Barn"
        }
      },
      {
        "platform": "pinterest",
        "id": "264938459268355565",
        "name": "Father's Day Shop",
        "url": "https://www.pinterest.com/potterybarn/fathers-day-shop/",
        "privacy": "public",
        "pinCount": 24,
        "followers": 1021565,
        "sectionCount": 0,
        "coverImage": "https://i.pinimg.com/200x150/a8/14/f7/a814f7c69a32aba27889359b31e7eb72.jpg",
        "createdAt": "Tue, 12 May 2026 18:40:06 +0000",
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
        "destinationUrl": "https://www.potterybarn.com/pages/lookbook/fall/rustic-lodge/?cm_ven=OrganicSocial&amp;cm_cat=Pinterest&amp;cm_pla=stpin&amp;cm_ite=rusticlodgeoutdoordining",
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
        "destinationUrl": "https://www.potterybarn.com/pages/lookbook/fall/rustic-lodge/?cm_ven=OrganicSocial&amp;cm_cat=Pinterest&amp;cm_pla=stpin&amp;cm_ite=rusticlodgeblankets",
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
      },
      {
        "platform": "pinterest",
        "id": "264938390611768272",
        "url": "https://www.pinterest.com/pin/264938390611768272/",
        "description": "Soft plaid flannel meets rustic design to create a table setting that's warm, welcoming, and made for gathering. Layer plaid table linens with timeless dinnerware and natural textures for a cozy fall table. Tap to shop one of our favorite table settings.",
        "destinationUrl": "https://www.potterybarn.com/pages/lookbook/fall/rustic-lodge/?cm_ven=OrganicSocial&amp;cm_cat=Pinterest&amp;cm_pla=stpin&amp;cm_ite=rusticlodgetablesetting",
        "image": "https://i.pinimg.com/564x/5a/ae/12/5aae12341bb187a4053a9ced43e2f700.jpg",
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
        "id": "264938390611768263",
        "url": "https://www.pinterest.com/pin/264938390611768263/",
        "description": "Bring subtle color and rich texture to your living room sofa by layering our mix of decorative throw pillows. Mix prints, patterns, and soft textures to create a living room that feels collected, cozy, and timeless.",
        "destinationUrl": "https://www.potterybarn.com/pages/lookbook/fall/rustic-lodge/?cm_ven=OrganicSocial&amp;cm_cat=Pinterest&amp;cm_pla=stpin&amp;cm_ite=rusticlodgepillows",
        "image": "https://i.pinimg.com/564x/13/37/dd/1337dd421b303196c96002b735618cc3.jpg",
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
        "id": "4598878985126594944",
        "url": "https://www.pinterest.com/pin/4598878985126594944/",
        "description": "Construction Slope arm. Swivel mechanism allows chair to turn 360deg.. Standard cushions have a down-blend-wrapped core for a softer feel and extra comfort. No-sag steel sinuous springs provides cushion support. Expertly crafted, kiln-dried engineered wood frame with mortise-and-tenon joinery, which provides exceptional structural integrity. Contract Grade: Thoughtfully designed and expertly engineered to meet rigorous testing standards and best practices from select ANSI/BIFMA testing protocols. Quality Exclusively designed and masterfully upholstered at our Sutter Street Factory from USA and Imported materials. Care Vacuum cushions regularly. To prevent fading, keep fabric out of direct sunlight. Blot spills immediately with a clean colorfast towel or sponge. Assembly White Glove Service",
        "destinationUrl": "https://www.potterybarn.com/products/beaumont-upholstered-swivel-chair/?catalogId=84&amp;sku=1078915&amp;cm_ven=organicsocial&amp;cm_cat=pinterest&amp;cm_pla=organic&amp;cm_ite=%7Bproduct_id%7D/",
        "image": "https://i.pinimg.com/564x/03/b6/50/03b650cdee48f68e6a965f3d4a43338e.jpg",
        "board": {
          "name": "Products",
          "url": "https://www.pinterest.com/potterybarn/_products/"
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
      },
      {
        "id": "p0gyjgf",
        "author": "Lietenantdan",
        "authorFullname": "t2_15w5m0",
        "text": "And by early we mean the time you were actually supposed to leave.",
        "upvotes": 4919,
        "score": 4919,
        "downs": 0,
        "publishedAt": "2026-07-29T14:02:18.000Z",
        "url": "https://www.reddit.com/r/worldnews/comments/1v9vtop/japans_population_falls_below_120_million_for/p0gyjgf/",
        "parentId": "t1_p0gpy2l",
        "depth": 1,
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
    "transcript": "Title: Radiation exposure may become the biggest challenge for future Moon and Mars missions\n\n[removed]\n\nEffingWasps: Insert that very recent but weirdly broadly applicable “this has been talked about extensively you’re just 21” meme\n\nb407driver: Become? It has always been the greatest (unsolved) challenge.\n\nWaarm: The current biggest challenge is funding.\n\nAdmirable_Site_8337: “…..seems to receive little public discussion……”\n\nSigh………………\n\n………….\n\n…………\n\nLioraB: Line the ships with astrophage.",
    "transcriptSegments": [
      {
        "speaker": "post",
        "text": "Radiation exposure may become the biggest challenge for future Moon and Mars missions",
        "start": 0,
        "duration": 0,
        "timestamp": "00:00"
      },
      {
        "speaker": "Low-Mathematician137",
        "text": "[removed]",
        "start": 0,
        "duration": 0,
        "timestamp": "00:00"
      },
      {
        "speaker": "EffingWasps",
        "text": "Insert that very recent but weirdly broadly applicable “this has been talked about extensively you’re just 21” meme",
        "start": 0,
        "duration": 0,
        "timestamp": "00:00"
      },
      {
        "speaker": "b407driver",
        "text": "Become? It has always been the greatest (unsolved) challenge.",
        "start": 0,
        "duration": 0,
        "timestamp": "00:00"
      },
      {
        "speaker": "Waarm",
        "text": "The current biggest challenge is funding.",
        "start": 0,
        "duration": 0,
        "timestamp": "00:00"
      }
    ],
    "wordCount": 67,
    "segments": 7,
    "commentsIncluded": 5
  },
  "reddit-search": {
    "query": "james webb",
    "totalReturned": 5,
    "nextCursor": "t3_1uoc2iy",
    "hasMore": true,
    "results": [
      {
        "platform": "reddit",
        "id": "1ucll2e",
        "url": "https://www.reddit.com/r/worldnews/comments/1ucll2e/james_webb_telescope_detects_galaxykilling_wind/",
        "title": "James Webb telescope detects 'galaxy-killing wind' near the dawn of time",
        "text": null,
        "subreddit": "worldnews",
        "author": "shdw_fght",
        "upvotes": 1467,
        "comments": 162,
        "publishedAt": "2026-06-22T14:08:15+00:00",
        "flair": null,
        "nsfw": false,
        "thumbnail": "https://external-preview.redd.it/MvcbMbmZOw99iMdDsy1JbsvZKf_5VGs-WQ1y5lrYGwo.jpeg?width=140&height=78&auto=webp&s=ff7d6360b316c1006ac4c27398dfc41df784e772"
      },
      {
        "platform": "reddit",
        "id": "1oqvn0t",
        "url": "https://www.reddit.com/r/askastronomy/comments/1oqvn0t/james_webbs_5_strangest_discoveries_and_one_of/",
        "title": "James Webb’s 5 strangest discoveries… and one of them completely breaks our current cosmology.",
        "text": "Hey everyone,  \nI’ve been going down a rabbit hole recently about the James Webb Space Telescope, and some of the discoveries are honestly blowing my mind.\n\nI’m talking about things like:  \n• massive galaxies appearing way too early after the Big Bang  \n• structures that look too organized for such a young universe  \n• supermassive black holes that somehow grew insanely fast  \n• unexpected molecules detected in exoplanet atmospheres  \n• and infrared signals that still don’t have a solid explanation\n\nI’m really curious about your opinions on this:  \n**Are these just early interpretations that will be corrected later, or is Webb genuinely challenging parts of the standard cosmology model?**\n\nI figured this subreddit would have people who follow this kind of stuff closely.  \nWould love to hear what you think or if you have recommended sources.",
        "subreddit": "askastronomy",
        "author": "Green_Advantage_1240",
        "upvotes": 383,
        "comments": 39,
        "publishedAt": "2025-11-07T14:19:46+00:00",
        "flair": null,
        "nsfw": false,
        "thumbnail": null
      },
      {
        "platform": "reddit",
        "id": "1rh4u8o",
        "url": "https://www.reddit.com/r/todayilearned/comments/1rh4u8o/til_the_james_webb_space_telescope_has_found_over/",
        "title": "TIL the James Webb Space Telescope has found over 300 \"Little Red Dots\", objects that existed between 13.2 an 12.2 billion years ago, and whose nature is currently uncertain",
        "text": null,
        "subreddit": "todayilearned",
        "author": "brazzy42",
        "upvotes": 13627,
        "comments": 204,
        "publishedAt": "2026-02-28T15:03:10+00:00",
        "flair": null,
        "nsfw": false,
        "thumbnail": "https://external-preview.redd.it/jv4EtU_QZlM0w1ZSlNWfvuzvkL-FJ00HGsTsl07LPss.jpeg?width=140&height=139&auto=webp&s=94311e1eec8a572c48b01d8b5cbae2f371396318"
      },
      {
        "platform": "reddit",
        "id": "1s1neio",
        "url": "https://www.reddit.com/r/space/comments/1s1neio/pope_leo_james_webb_telescope_shows_us_what_the/",
        "title": "Pope Leo: James Webb telescope shows us what the Bible couldn’t",
        "text": null,
        "subreddit": "space",
        "author": "Automatic_Subject463",
        "upvotes": 7395,
        "comments": 372,
        "publishedAt": "2026-03-23T17:27:04+00:00",
        "flair": null,
        "nsfw": false,
        "thumbnail": null
      },
      {
        "platform": "reddit",
        "id": "1uoc2iy",
        "url": "https://www.reddit.com/r/space/comments/1uoc2iy/james_webb_telescope_may_have_discovered_a/",
        "title": "James Webb telescope may have discovered a ... never-before-seen [molecule] on Pluto and Titan",
        "text": null,
        "subreddit": "space",
        "author": "peterabbit456",
        "upvotes": 4011,
        "comments": 195,
        "publishedAt": "2026-07-05T20:06:51+00:00",
        "flair": null,
        "nsfw": false,
        "thumbnail": "https://external-preview.redd.it/UFDmgLQduMBtzlbjTNKShcfzcP1R7CqbdRhuulAMObQ.jpeg?width=140&height=78&auto=webp&s=238b494e2a39e0cc407a149711ec10f3263622e5"
      }
    ]
  },
  "reddit-subreddit-details": {
    "platform": "reddit",
    "name": "space",
    "url": "https://www.reddit.com/r/space",
    "title": "/r/space: news, articles and discussion",
    "description": "Share & discuss informative content on:\n\n* Astrophysics\n* Cosmology\n* Space Exploration\n* Planetary Science\n* Astrobiology",
    "members": 27936127,
    "category": "Lifestyles",
    "language": "en",
    "type": "public",
    "createdAt": "1201327674.0",
    "nsfw": false,
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
      },
      {
        "platform": "reddit",
        "id": "1vdd2k6",
        "name": "t3_1vdd2k6",
        "url": "https://www.reddit.com/r/space/comments/1vdd2k6/manned_orbital_launches_by_year_1961_2026_h1/",
        "title": "Manned orbital launches by year, 1961 - 2026 H1",
        "text": "Source and details: [https://spacestatsonline.com/launches/manned](https://spacestatsonline.com/launches/manned)",
        "subreddit": "space",
        "author": "firefly-metaverse",
        "authorFullname": "t2_i6d091hi",
        "upvotes": 66,
        "score": 66,
        "downs": 0,
        "upvoteRatio": 0.87,
        "comments": 10,
        "subscriberCount": 27937807,
        "totalAwardsReceived": 0,
        "isVideo": false,
        "publishedAt": "2026-08-02T08:59:23.000Z",
        "flair": "image/gif",
        "nsfw": false,
        "thumbnail": "https://preview.redd.it/lofgkcmdfxgh1.png?width=140&height=77&auto=webp&s=e6b27071138762c896750a587adbc2f96356dd72"
      }
    ]
  },
  "reddit-subreddit-search": {
    "subreddit": "space",
    "query": "moon",
    "totalReturned": 5,
    "nextCursor": "t3_1s2fq4k",
    "hasMore": true,
    "results": [
      {
        "platform": "reddit",
        "id": "1sbgcy5",
        "url": "https://www.reddit.com/r/space/comments/1sbgcy5/hello_world_artemis_ii_crew_looks_back_at_earth/",
        "title": "Hello, World: Artemis II crew looks back at Earth on their way to the Moon",
        "text": null,
        "subreddit": "space",
        "author": "ChiefLeef22",
        "upvotes": 80287,
        "comments": 1450,
        "publishedAt": "2026-04-03T15:15:19+00:00",
        "flair": null,
        "nsfw": false,
        "thumbnail": "https://preview.redd.it/lc95vmh6szsg1.jpeg?width=140&height=93&auto=webp&s=415f9d988982ae90c81e2e8ab9cee83a5f19c4d6"
      },
      {
        "platform": "reddit",
        "id": "1sevdps",
        "url": "https://www.reddit.com/r/space/comments/1sevdps/earthset_artemis_ii_captures_their_first_photo/",
        "title": "EARTHSET: Artemis II captures their first photo from the far side of the moon",
        "text": null,
        "subreddit": "space",
        "author": "ChiefLeef22",
        "upvotes": 97159,
        "comments": 1123,
        "publishedAt": "2026-04-07T13:03:27+00:00",
        "flair": "spacers only",
        "nsfw": false,
        "thumbnail": "https://preview.redd.it/zgg6qm9bortg1.jpeg?width=140&height=93&auto=webp&s=3f8a149eff1a439f09573dd978edc66e74c1f9d2"
      },
      {
        "platform": "reddit",
        "id": "1s9qfc7",
        "url": "https://www.reddit.com/r/space/comments/1s9qfc7/megathread_artemis_ii_launch_to_the_moon/",
        "title": "[MEGATHREAD] Artemis II Launch To The Moon",
        "text": "This is the official r/space live megathread for NASA's Artemis II mission - **the first crewed launch of NASA’s SLS (Space Launch System) rocket and Orion spacecraft.**\n\nFor the first time in more than 50 years, humans will travel around the moon to test deep-space life-support systems.\n\nLIVE VIEWING FEEDS:\n\n\\[OFFICIAL NASA\\] [ NASA’s Artemis II Crew Comes Home (Official Broadcast) ](https://m.youtube.com/watch?v=nfhDuOHMp0A)\n\n\\[NASASpaceflight\\] [ Artemis II Astronauts Return To Earth - Re-entry and Splashdown ](https://m.youtube.com/watch?v=_veRvxj-5VQ&pp=ygUPbmFzYXNwYWNlZmxpZ2h0)\n\n\\[SKY NEWS\\] [No Commentary Broadcast](https://www.youtube.com/watch?v=yByKVNdBDBw)\n\n\\---------------------\n\n**NOTE:** This thread will contain links to multiple different live viewing channels. The sub will remain in manual approval mode during the mission to limit spam. As such, you are welcome to redirect anything you want to post separately in this time period to the comment section in this megathread.\n\n\\---------------------\n\nARTEMIS LIVE TRACKER - [https://www.reddit.com/r/space/s/ROkGU4c5SD](https://www.reddit.com/r/space/s/ROkGU4c5SD) (courtesy of u/theneiljohnson)\n\n**MISSION INFO:** At 6:24pm EDT (22:24 GMT) on Wednesday, a two-hour window will open for the Artemis II mission to lift off from the Kennedy Space Center in Florida. The launch window will remain open until April 6 for two hours each day after sunset. The mission can launch only when the moon, orbital paths, weather and Earth’s rotation line up safely.\n\nThis is the third launch attempt for Artemis II, after the first attempt was scrubbed due to a liquid hydrogen leak during a practice countdown in early February, and the second attempt was cancelled when engineers discovered a helium flow issue in the rocket’s upper stage in early March\n\nThe four-person crew will not land on the moon but rather perform a lunar flyby, looping around the moon’s far side before returning to Earth. At its core, Artemis II is a systems validation mission. NASA will use the flight to test the Orion spacecraft’s life support systems, navigation, communication links and overall performance in deep space with a crew on board – conditions that cannot be fully replicated on Earth. If successful, Artemis II will pave the way for Artemis III, a crewed low Earth orbit mission; then Artemis IV, which aims to land astronauts on the moon; and future missions that could establish a sustained human presence beyond Earth.\n\n\\---------------------\n\n# UPDATES:\n\nT-1 hour 14 minutes: They have fixed an issue at the flight termination system, the range is a go!\n\nT-10 minutes: After some hold, it looks like its still a go!\n\nT-0: LIFTOFF! YOU WERE HERE! HISTORY IN THE MAKING\n\nLow earth orbit insertion successful! Happy monitoring to everyone over this 10 day journey\n\nNEXT UP: **Perigee Raise Burn**\n\nAfter a four-hour nap, the Artemis II crew will be awakened at 7 a.m. EDT on Thursday, April 2, to prepare for the perigee raise burn. This burn will lift the lowest point of Orion’s orbit around Earth. Together with the apogee raise burn completed earlier, these burns shape the spacecraft’s initial orbit and prepare it for later translunar operations. The crew then will resume their sleep period around 9:40 a.m.\n\n\\---PRB is now complete. Translunar Injection will begin no earlier than **7PM EDT**\n\n\\----TLI Is now also complete - we're on the way to moon!\n\nNext up - Lunar Flyby on Monday....\n\n\\----- Lunar flyby complete! What a monumental day in history. Apollo 13's distance record broken, and the dawn of a new era of space exploration\n\nOrion is set to splash down at 5:07 PM P.T., today\n\n\\---The crew are safely back home! A historic mission concludes. It feels a little surreal to think we could all witness this journey live, and this megathread has been an amazing example of that.",
        "subreddit": "space",
        "author": "ChiefLeef22",
        "upvotes": 10324,
        "comments": 17485,
        "publishedAt": "2026-04-01T17:00:55+00:00",
        "flair": "LIVE MEGATHREAD",
        "nsfw": false,
        "thumbnail": null
      },
      {
        "platform": "reddit",
        "id": "1sdf8u6",
        "url": "https://www.reddit.com/r/space/comments/1sdf8u6/home_artemis_ii_crew_captures_one_last_shot_of_a/",
        "title": "Home: Artemis II crew captures one last shot of a crescent Earth before reaching the moon tomorrow",
        "text": null,
        "subreddit": "space",
        "author": "ChiefLeef22",
        "upvotes": 54061,
        "comments": 887,
        "publishedAt": "2026-04-05T21:11:58+00:00",
        "flair": null,
        "nsfw": false,
        "thumbnail": "https://preview.redd.it/6m87nz7ntftg1.jpeg?width=140&height=93&auto=webp&s=2881859d820eb0f27b07eb857515a581a3e2d72a"
      },
      {
        "platform": "reddit",
        "id": "1s2fq4k",
        "url": "https://www.reddit.com/r/space/comments/1s2fq4k/nasa_to_spend_20_billion_on_moon_base_cancel/",
        "title": "NASA to spend $20 billion on moon base, cancel orbiting lunar station",
        "text": null,
        "subreddit": "space",
        "author": "Tracheid",
        "upvotes": 6936,
        "comments": 754,
        "publishedAt": "2026-03-24T14:43:07+00:00",
        "flair": null,
        "nsfw": false,
        "thumbnail": "https://external-preview.redd.it/32pCFAVJ3r9pHz411kpjvc2FpAALaggi68wI4OMY4-w.jpeg?width=140&height=73&auto=webp&s=e800f58a5b44e087d290c0bdfe40a8a95a125fcb"
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
        "embedUrl": "https://rumble.com/embed/v7dfegc/",
        "title": "The Democrat Civil War Is Getting Intense (Ep. 2563) - 07/29/2026",
        "channel": "The Dan Bongino Show",
        "channelUrl": "https://rumble.com/c/bongino",
        "channelFollowers": 3661298,
        "channelVerified": true,
        "views": 230174,
        "likes": 4178,
        "dislikes": 43,
        "duration": "5456",
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
        ]
      },
      {
        "platform": "rumble",
        "id": "v7det4g",
        "url": "https://rumble.com/shorts/v7det4g",
        "embedUrl": "https://rumble.com/embed/v7det4g/",
        "title": "Just Wait Until You Read TRUMP’S Diary...",
        "channel": "The Dan Bongino Show",
        "channelUrl": "https://rumble.com/c/bongino",
        "channelFollowers": 3661298,
        "channelVerified": true,
        "views": 8242,
        "likes": 234,
        "dislikes": 7,
        "duration": "55",
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
          },
          {
            "url": "https://1a-1791.com/video/fwe2/b4/s8/2/W/p/J/K/WpJKA.caa.mp4?b=1&u=6",
            "type": "mp4",
            "quality": "480p"
          },
          {
            "url": "https://1a-1791.com/video/fwe2/b4/s8/2/W/p/J/K/WpJKA.baa.mp4?b=1&u=6",
            "type": "mp4",
            "quality": "360p"
          }
        ]
      },
      {
        "platform": "rumble",
        "id": "v7defpc",
        "url": "https://rumble.com/shorts/v7defpc",
        "embedUrl": "https://rumble.com/embed/v7defpc/",
        "title": "How Communists Collapse the Food Supply in 5 Easy Steps",
        "channel": "The Dan Bongino Show",
        "channelUrl": "https://rumble.com/c/bongino",
        "channelFollowers": 3661298,
        "channelVerified": true,
        "views": 6422,
        "likes": 186,
        "dislikes": 4,
        "duration": "74",
        "publishedAt": "2026-07-28T21:35:04+00:00",
        "thumbnail": "https://1a-1791.com/video/fww1/cb/s8/1/a/a/F/K/aaFKA.OvCc-small-How-Communists-Collapse-the..jpg",
        "comments": 18,
        "isLive": false,
        "streams": [
          {
            "url": "https://1a-1791.com/video/fww1/cb/s8/2/a/a/F/K/aaFKA.haa.mp4?b=1&u=6",
            "type": "mp4",
            "quality": "1080p"
          },
          {
            "url": "https://1a-1791.com/video/fww1/cb/s8/2/a/a/F/K/aaFKA.gaa.mp4?b=1&u=6",
            "type": "mp4",
            "quality": "720p"
          },
          {
            "url": "https://1a-1791.com/video/fww1/cb/s8/2/a/a/F/K/aaFKA.caa.mp4?b=1&u=6",
            "type": "mp4",
            "quality": "480p"
          },
          {
            "url": "https://1a-1791.com/video/fww1/cb/s8/2/a/a/F/K/aaFKA.baa.mp4?b=1&u=6",
            "type": "mp4",
            "quality": "360p"
          }
        ]
      },
      {
        "platform": "rumble",
        "id": "v7deb7m",
        "url": "https://rumble.com/shorts/v7deb7m",
        "embedUrl": "https://rumble.com/embed/v7deb7m/",
        "title": "Fauci’s Biggest Lies EXPOSED in His Own Diary",
        "channel": "The Dan Bongino Show",
        "channelUrl": "https://rumble.com/c/bongino",
        "channelFollowers": 3661300,
        "channelVerified": true,
        "views": 6186,
        "likes": 178,
        "dislikes": 4,
        "duration": "64",
        "publishedAt": "2026-07-28T20:02:09+00:00",
        "thumbnail": "https://1a-1791.com/video/fww1/8b/s8/6/c/L/D/K/cLDKA.O-xb.jpg",
        "comments": 8,
        "isLive": false,
        "streams": [
          {
            "url": "https://1a-1791.com/video/fww1/8b/s8/2/c/L/D/K/cLDKA.haa.mp4?b=1&u=6",
            "type": "mp4",
            "quality": "1080p"
          },
          {
            "url": "https://1a-1791.com/video/fww1/8b/s8/2/c/L/D/K/cLDKA.gaa.mp4?b=1&u=6",
            "type": "mp4",
            "quality": "720p"
          },
          {
            "url": "https://1a-1791.com/video/fww1/8b/s8/2/c/L/D/K/cLDKA.caa.mp4?b=1&u=6",
            "type": "mp4",
            "quality": "480p"
          },
          {
            "url": "https://1a-1791.com/video/fww1/8b/s8/2/c/L/D/K/cLDKA.baa.mp4?b=1&u=6",
            "type": "mp4",
            "quality": "360p"
          }
        ]
      },
      {
        "platform": "rumble",
        "id": "v7ddmnm",
        "url": "https://rumble.com/v7ddmnm-dear-diary-they-lied-about-everything-ep.-2562-07282026.html",
        "embedUrl": "https://rumble.com/embed/v7ddmnm/",
        "title": "Dear Diary, They Lied About Everything (Ep. 2562) - 07/28/2026",
        "channel": "The Dan Bongino Show",
        "channelUrl": "https://rumble.com/c/bongino",
        "channelFollowers": 3661300,
        "channelVerified": true,
        "views": 478253,
        "likes": 7946,
        "dislikes": 95,
        "duration": "4861",
        "publishedAt": "2026-07-28T12:27:49+00:00",
        "thumbnail": "https://1a-1791.com/video/fww1/c6/s8/1/Y/Z/v/K/YZvKA.OvCc-small-Dear-Diary-They-Lied-About-..jpg",
        "comments": 812,
        "isLive": false,
        "streams": [
          {
            "url": "https://1a-1791.com/video/fww1/c6/s8/2/Y/Z/v/K/YZvKA.aaa.rec.mp4?b=1&u=6",
            "type": "mp4",
            "quality": "1080p"
          },
          {
            "url": "https://1a-1791.com/video/fww1/c6/s8/2/Y/Z/v/K/YZvKA.haa.rec.mp4?b=1&u=6",
            "type": "mp4",
            "quality": "1080p"
          },
          {
            "url": "https://1a-1791.com/video/fww1/c6/s8/2/Y/Z/v/K/YZvKA.gaa.rec.mp4?b=1&u=6",
            "type": "mp4",
            "quality": "720p"
          },
          {
            "url": "https://1a-1791.com/video/fww1/c6/s8/2/Y/Z/v/K/YZvKA.caa.rec.mp4?b=1&u=6",
            "type": "mp4",
            "quality": "480p"
          },
          {
            "url": "https://1a-1791.com/video/fww1/c6/s8/2/Y/Z/v/K/YZvKA.baa.rec.mp4?b=1&u=6",
            "type": "mp4",
            "quality": "360p"
          }
        ]
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
      },
      {
        "platform": "rumble",
        "id": "614672888",
        "text": "The aides and/or the house mother often overseeing  5  of these homes housing 3 people.  Every one of their votes cancels out a citizens vote.  This is not right and it was added into \"The No Child Left Behind\" legislation.",
        "author": {
          "name": "connier1014",
          "url": "https://rumble.com/user/connier1014",
          "verified": false
        },
        "likes": 0,
        "replyCount": 0,
        "createdAt": "Tuesday, July 21, 2026 07:11 AM -04"
      },
      {
        "platform": "rumble",
        "id": "614463480",
        "text": "yep, I worked on a campaign in TX & they(democrats) were using kids to go into nursing homes because they thought that if they were caught, the government wouldn't charge minors for voter fraud. They were paying homeless ppl to vote",
        "author": {
          "name": "Samoanqueen",
          "url": "https://rumble.com/user/Samoanqueen",
          "verified": false
        },
        "likes": 18,
        "replyCount": 0,
        "createdAt": "Friday, July 17, 2026 01:41 PM -04"
      },
      {
        "platform": "rumble",
        "id": "614477216",
        "text": "Don’t forget the paid ballot box stuffers paid by Zuckerberg bucks… That were caught on film and Geo tracked",
        "author": {
          "name": "ThHess",
          "url": "https://rumble.com/user/ThHess",
          "verified": false
        },
        "likes": 17,
        "replyCount": 1,
        "createdAt": "Friday, July 17, 2026 05:46 PM -04"
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
        "title": "FLAT EARTH - FAKE SPACE",
        "channel": "Flat Earth Clock app",
        "channelUrl": "https://rumble.com/c/flatearthclock",
        "views": 954,
        "likes": 17,
        "dislikes": 0,
        "duration": "8:05",
        "publishedAt": "2026-07-27T08:08:00-04:00",
        "thumbnail": "https://1a-1791.com/video/fwe2/96/s8/1/8/r/8/J/8r8JA.oq1b-small-FLAT-EARTH-FAKE-SPACE..jpg",
        "comments": 1
      },
      {
        "platform": "rumble",
        "id": "v7dbg7s",
        "url": "https://rumble.com/v7dbg7s-dummyvision-2-just-asking-questions-and-closing-arguments-from-baron-colema.html",
        "title": "SUNDAY SLOWS - Listening To a Special Spaces on Tyler Robinson - Misunderstanding Trial 101",
        "channel": "Rekieta Law",
        "channelUrl": "https://rumble.com/c/RekietaLaw",
        "views": 7720,
        "likes": 113,
        "dislikes": 6,
        "duration": "3:55:39",
        "publishedAt": "2026-07-27T00:18:40-04:00",
        "thumbnail": "https://1a-1791.com/video/fww1/89/s8/6/y/_/8/J/y_8JA.oq1b.37.jpg",
        "comments": 7
      },
      {
        "platform": "rumble",
        "id": "v7dcipw",
        "url": "https://rumble.com/v7dcipw-planet-earth-is-under-attack-by-space-demons.html",
        "title": "PLANET EARTH IS UNDER ATTACK BY SPACE DEMONS",
        "channel": "STRANGER THAN FICTION NEWS",
        "channelUrl": "https://rumble.com/c/c-360794",
        "views": 1240,
        "likes": 23,
        "dislikes": 1,
        "duration": "18:54",
        "publishedAt": "2026-07-27T16:34:03-04:00",
        "thumbnail": "https://1a-1791.com/video/fwe2/97/s8/6/e/l/j/K/eljKA.oq1b.4.jpg",
        "comments": 12
      },
      {
        "platform": "rumble",
        "id": "v7dci9i",
        "url": "https://rumble.com/v7dci9i-dont-force-yourself-to-be-good-twitterx-space.html",
        "title": "Don't Force Yourself to be GOOD! Twitter/X Space",
        "channel": "Freedomain",
        "channelUrl": "https://rumble.com/c/freedomain",
        "views": 841,
        "likes": 9,
        "dislikes": 0,
        "duration": "1:04:44",
        "publishedAt": "2026-07-27T15:26:25-04:00",
        "thumbnail": "https://1a-1791.com/video/fww1/25/s8/1/2/b/j/K/2bjKA.oq1b-small-Dont-Force-Yourself-to-be-G..jpg",
        "comments": null
      },
      {
        "platform": "rumble",
        "id": "v7ddi44",
        "url": "https://rumble.com/v7ddi44-patriot-pals-ep.8-lets-go-to-space.html",
        "title": "Patriot Pals Ep.#8: Let's Go To Space!",
        "channel": "Patriot Pals",
        "channelUrl": "https://rumble.com/c/PatriotPals",
        "views": 1380,
        "likes": 20,
        "dislikes": 0,
        "duration": "6:26",
        "publishedAt": "2026-07-28T06:39:28-04:00",
        "thumbnail": "https://1a-1791.com/video/fwe2/36/s8/6/0/x/u/K/0xuKA.oq1b.jpg",
        "comments": 2
      }
    ]
  },
  "rumble-video-details": {
    "platform": "rumble",
    "id": "v7cv2cc",
    "numericId": 441201242,
    "embedId": "v7aoh22",
    "url": "https://rumble.com/v7cv2cc-now-i-can-finally-talk-about-it-ep.-2555-07172026.html",
    "embedUrl": "https://rumble.com/embed/v7aoh22/",
    "shareUrl": "https://rumble.com/share/v7cv2cc?src=J1c68WSr8AsehcaSzlyz2fgeg8DoMr_YAh20afx-dezbwbz0_kJtdA",
    "title": "Now I Can Finally Talk About It (Ep. 2555) - 07/17/2026",
    "description": "In this episode, I'll discuss the groundbreaking information President Trump revealed in his speech last night and what it means for our elections movingforward. 1776 Live Club: No purchase necessary.",
    "channel": "The Dan Bongino Show",
    "channelUrl": "https://rumble.com/c/bongino",
    "channelHandle": "bongino",
    "channelFollowers": 3660000,
    "channelVerified": true,
    "views": 940965,
    "likes": 15500,
    "dislikes": 194,
    "comments": 1050,
    "duration": "1:26:25",
    "durationSeconds": 5185,
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
        "url": "https://1a-1791.com/video/fwe2/7c/s8/2/C/w/c/H/CwcHA.caa.rec.mp4",
        "type": "mp4",
        "quality": "480p"
      },
      {
        "url": "https://1a-1791.com/video/fwe2/7c/s8/2/C/w/c/H/CwcHA.Faa.rec.mp4",
        "type": "mp4",
        "quality": "180p"
      },
      {
        "url": "https://1a-1791.com/video/fwe2/7c/s8/2/C/w/c/H/CwcHA.aaa.rec.mp4",
        "type": "mp4",
        "quality": "1081p"
      },
      {
        "url": "https://1a-1791.com/video/fwe2/7c/s8/2/C/w/c/H/CwcHA.haa.rec.mp4",
        "type": "mp4",
        "quality": "1080p"
      },
      {
        "url": "https://1a-1791.com/video/fwe2/7c/s8/2/C/w/c/H/CwcHA.gaa.rec.mp4",
        "type": "mp4",
        "quality": "720p"
      },
      {
        "url": "https://1a-1791.com/video/fwe2/7c/s8/2/C/w/c/H/CwcHA.baa.rec.mp4",
        "type": "mp4",
        "quality": "360p"
      },
      {
        "url": "https://1a-1791.com/video/fwe2/7c/s8/2/C/w/c/H/CwcHA.oaa.rec.mp4",
        "type": "mp4",
        "quality": "240p"
      },
      {
        "url": "https://1a-1791.com/video/fwe2/7c/s8/2/C/w/c/H/CwcHA.Gaa.rec.aac",
        "type": "audio",
        "quality": "192k"
      }
    ]
  },
  "snapchat-user-profile": {
    "platform": "snapchat",
    "username": "nba",
    "url": "https://www.snapchat.com/@nba",
    "displayName": "NBA",
    "bio": "30 teams, 1 goal.",
    "category": "Business Group",
    "categoryId": "public-profile-category-v3-business-group",
    "subcategory": "Sports League",
    "subcategoryId": "public-profile-subcategory-v3-sports-league",
    "subscriberCount": 3657900,
    "verified": true,
    "badge": 1,
    "avatar": "https://cf-st.sc-cdn.net/aps/bolt/aHR0cHM6Ly9jZi1zdC5zYy1jZG4ubmV0L2QvcGxQanhqRDFZRk9IUWdGMUZLRHNqP2JvPUVna3lBUVJJQWxBWllBRSUzRCZ1Yz0yNQ._RS0,90_FMjpeg",
    "squareHeroImageUrl": "https://cf-st.sc-cdn.net/aps/bolt/aHR0cHM6Ly9jZi1zdC5zYy1jZG4ubmV0L2QvcUZBYjExSEY3QkdkeHNiOXpkMTREP2JvPUVna3lBUVJJQWxBWllBRSUzRCZ1Yz0yNQ._RS0,1080_FMjpeg",
    "snapcode": "https://app.snapchat.com/web/deeplink/snapcode?username=nba&type=SVG&bitmoji=enable",
    "website": "NBA.com",
    "businessProfileId": "ea71b19b-5eb1-4dda-afb8-13ced485f180",
    "creationTimestampMs": 1526597295058,
    "createdAt": "2018-05-17T22:48:15.058000Z",
    "lastUpdateTimestampMs": 1785621675000,
    "updatedAt": "2026-08-01T22:01:15Z",
    "hasStory": false,
    "hasCuratedHighlights": true,
    "hasSpotlightHighlights": true,
    "story": {
      "snapCount": 6,
      "thumbnailUrl": "https://cf-st.sc-cdn.net/d/AODMFV4kcbKapQw9bcNSU.256.IRZXSOY?mo=GlMaDjICBH1IAlBLYAFoDHABUI4BWhBEZkxhcmdlVGh1bWJuYWlsogEUCIACIg8KAmgMEgAqB0lSWlhTT1miARQImgoiDwoCaAwSACoHSVJaWFNPWQ%3D%3D&uc=75",
      "snapList": [
        {
          "snapIndex": 0,
          "snapId": "2wzhbo4SSiWIG-fd9lWR2wAAgemFmc3Jic3dpAZ-_U_TQAZ-_U8skAAAAAA",
          "snapMediaType": 1,
          "mediaType": "video",
          "mediaUrl": "https://cf-st.sc-cdn.net/d/AODMFV4kcbKapQw9bcNSU.1034.IRZXSOY?mo=Gl8aGDIBBDoBfUIGCK3XudMGSAJQS2ABaAxwAVCwAaIBOwiKCBIlCiMI8dhLIAEw4AM41AZAAUoOCglHKUFFPT1BNzoQ9ANQkE5oAiIPCgJoDBIAKgdJUlpYU09ZkAOQTg%3D%3D&uc=75",
          "mediaPreviewUrl": "https://cf-st.sc-cdn.net/d/AODMFV4kcbKapQw9bcNSU.256.IRZXSOY?mo=GlMaDjICBH1IAlBLYAFoDHABUI4BWhBEZkxhcmdlVGh1bWJuYWlsogEUCIACIg8KAmgMEgAqB0lSWlhTT1miARQImgoiDwoCaAwSACoHSVJaWFNPWQ%3D%3D&uc=75",
          "timestampInSec": 1785621367,
          "publishedAt": "2026-08-01T21:56:07Z"
        },
        {
          "snapIndex": 1,
          "snapId": "2wzhbo4SSiWIG-fd9lWR2wAAgc3dkeHdlbnh0AZ-_U_WvAZ-_U8suAAAAAA",
          "snapMediaType": 1,
          "mediaType": "video",
          "mediaUrl": "https://cf-st.sc-cdn.net/d/7oaCx89Y053GDtXAGnYPU.1034.IRZXSOY?mo=GmAaGDIBBDoBfUIGCLXXudMGSAJQS2ABaAxwAVCwAaIBPAiKCBImCiQI1oxQIAEw4AM41AZAAUoPCgqDAUZTUFEsQEU7EPQDUJBOaAIiDwoCaAwSACoHSVJaWFNPWZADkE4%3D&uc=75",
          "mediaPreviewUrl": "https://cf-st.sc-cdn.net/d/7oaCx89Y053GDtXAGnYPU.256.IRZXSOY?mo=GlMaDjICBH1IAlBLYAFoDHABUI4BWhBEZkxhcmdlVGh1bWJuYWlsogEUCIACIg8KAmgMEgAqB0lSWlhTT1miARQImgoiDwoCaAwSACoHSVJaWFNPWQ%3D%3D&uc=75",
          "timestampInSec": 1785621367,
          "publishedAt": "2026-08-01T21:56:07Z"
        },
        {
          "snapIndex": 2,
          "snapId": "2wzhbo4SSiWIG-fd9lWR2wAAgdWxxbmJ1b2FyAZ-_U_aJAZ-_U8s4AAAAAA",
          "snapMediaType": 1,
          "mediaType": "video",
          "mediaUrl": "https://cf-st.sc-cdn.net/d/IXAlIELcj5WFE1fUA1w92.1034.IRZXSOY?mo=GmAaGDIBBDoBfUIGCKfXudMGSAJQS2ABaAxwAVCwAaIBPAiKCBImCiQIz4UzIAEw4AM41AZAAUoPCgqBAVFRV0A6Pz00EPQDUIotaAIiDwoCaAwSACoHSVJaWFNPWZADii0%3D&uc=75",
          "mediaPreviewUrl": "https://cf-st.sc-cdn.net/d/IXAlIELcj5WFE1fUA1w92.256.IRZXSOY?mo=GlMaDjICBH1IAlBLYAFoDHABUI4BWhBEZkxhcmdlVGh1bWJuYWlsogEUCIACIg8KAmgMEgAqB0lSWlhTT1miARQImgoiDwoCaAwSACoHSVJaWFNPWQ%3D%3D&uc=75",
          "timestampInSec": 1785621367,
          "publishedAt": "2026-08-01T21:56:07Z"
        }
      ]
    },
    "highlights": [
      {
        "highlightId": "{'value': '029f2cc3-c0df-46c2-b610-485c137f9a0a'}",
        "storyTitle": "{'value': '2025-26 NBA Finals 🏆'}",
        "thumbnailUrl": "https://cf-st.sc-cdn.net/d/ZXSSacNIpSYqxAm21SSGc.410?mo=GjcaFjIBBDoBfUIGCMqG99AGSAJQXmABcAFQxQFaEERmTGFyZ2VUaHVtYm5haWyiAQcImgMiAhIA&uc=94",
        "snapCount": 4,
        "firstSnapUrl": "https://cf-st.sc-cdn.net/d/ZXSSacNIpSYqxAm21SSGc.400?mo=Gk8aDDIBBDoBfVBeYAFwAVDBAVoQUHVibGljSW1hZ2VTdG9yeaIBEwiQAyIOCgpCBgjKhvfQBkgCEgCiARMI5wciDgoKQgYIy4b30AZIAxIA&uc=94",
        "snapList": [
          {
            "snapIndex": 0,
            "snapMediaType": 0,
            "mediaUrl": "https://cf-st.sc-cdn.net/d/ZXSSacNIpSYqxAm21SSGc.400?mo=Gk8aDDIBBDoBfVBeYAFwAVDBAVoQUHVibGljSW1hZ2VTdG9yeaIBEwiQAyIOCgpCBgjKhvfQBkgCEgCiARMI5wciDgoKQgYIy4b30AZIAxIA&uc=94",
            "mediaPreviewUrl": "https://cf-st.sc-cdn.net/d/ZXSSacNIpSYqxAm21SSGc.410?mo=GjcaFjIBBDoBfUIGCMqG99AGSAJQXmABcAFQxQFaEERmTGFyZ2VUaHVtYm5haWyiAQcImgMiAhIA&uc=94",
            "timestampInSec": 1780335408,
            "publishedAt": "2026-06-01T17:36:48Z"
          },
          {
            "snapIndex": 1,
            "snapMediaType": 0,
            "mediaUrl": "https://cf-st.sc-cdn.net/d/FgntIqJi6clNRLmaxXkXN.400?mo=Gk0aDjIBBDoBfUgCUF5gAXABUMEBWhBQdWJsaWNJbWFnZVN0b3J5ogERCJADIgwKCEIGCMuG99AGEgCiAREI5wciDAoIQgYIyob30AYSAA%3D%3D&uc=94",
            "mediaPreviewUrl": "https://cf-st.sc-cdn.net/d/FgntIqJi6clNRLmaxXkXN.410?mo=GjcaFjIBBDoBfUIGCMuG99AGSAJQXmABcAFQxQFaEERmTGFyZ2VUaHVtYm5haWyiAQcImgMiAhIA&uc=94",
            "timestampInSec": 1780335408,
            "publishedAt": "2026-06-01T17:36:48Z"
          },
          {
            "snapIndex": 2,
            "snapMediaType": 0,
            "mediaUrl": "https://cf-st.sc-cdn.net/d/MDhgz2NGVlp7M1wfhuT1s.400?mo=GkoaCTIBBFBeYAFwAVDBAVoQUHVibGljSW1hZ2VTdG9yeaIBFgiQAyIRCg06AX1CBgjPhvfQBkgCEgCiAQ4I5wciCQoFMgF9SAMSAA%3D%3D&uc=94",
            "mediaPreviewUrl": "https://cf-st.sc-cdn.net/d/MDhgz2NGVlp7M1wfhuT1s.410?mo=GjcaFjIBBDoBfUIGCM-G99AGSAJQXmABcAFQxQFaEERmTGFyZ2VUaHVtYm5haWyiAQcImgMiAhIA&uc=94",
            "timestampInSec": 1780335408,
            "publishedAt": "2026-06-01T17:36:48Z"
          },
          {
            "snapIndex": 3,
            "snapMediaType": 0,
            "mediaUrl": "https://cf-st.sc-cdn.net/d/V9pQZQcyVDfY0v9a5gTz6.400?mo=Gk0aDjIBBDoBfUgCUF5gAXABUMEBWhBQdWJsaWNJbWFnZVN0b3J5ogERCJADIgwKCEIGCMuG99AGEgCiAREI5wciDAoIQgYIyob30AYSAA%3D%3D&uc=94",
            "mediaPreviewUrl": "https://cf-st.sc-cdn.net/d/V9pQZQcyVDfY0v9a5gTz6.410?mo=GjcaFjIBBDoBfUIGCMuG99AGSAJQXmABcAFQxQFaEERmTGFyZ2VUaHVtYm5haWyiAQcImgMiAhIA&uc=94",
            "timestampInSec": 1780335408,
            "publishedAt": "2026-06-01T17:36:48Z"
          }
        ]
      },
      {
        "highlightId": "{'value': '2941c1a3-96ba-45aa-bdf4-30b344e63e42'}",
        "storyTitle": "{'value': 'Your 2025-26 Kia NBA MVP 🏆'}",
        "thumbnailUrl": "https://cf-st.sc-cdn.net/d/iqFfVpTceYNBTtMJvlQns.410.IRZXSOY?mo=GkAaFjIBBDoBfUIGCPa5qdAGSAJQXmABcAFQxQFaEERmTGFyZ2VUaHVtYm5haWyiARAImgMiCxIAKgdJUlpYU09Z&uc=94",
        "snapCount": 19,
        "firstSnapUrl": "https://cf-st.sc-cdn.net/d/iqFfVpTceYNBTtMJvlQns.400.IRZXSOY?mo=GlwaCTIBBFBeYAFwAVDBAVoQUHVibGljSW1hZ2VTdG9yeaIBHwiQAyIaCg06AX1CBgj2uanQBkgCEgAqB0lSWlhTT1miARcI5wciEgoFMgF9SAQSACoHSVJaWFNPWQ%3D%3D&uc=94",
        "snapList": [
          {
            "snapIndex": 0,
            "snapMediaType": 0,
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
          },
          {
            "snapIndex": 2,
            "snapMediaType": 0,
            "mediaUrl": "https://cf-st.sc-cdn.net/d/aUFzsbb4CKroNT0pRdE4G.400.IRZXSOY?mo=GlwaCTIBBFBeYAFwAVDBAVoQUHVibGljSW1hZ2VTdG9yeaIBHwiQAyIaCg06AX1CBgj2uanQBkgCEgAqB0lSWlhTT1miARcI5wciEgoFMgF9SAQSACoHSVJaWFNPWQ%3D%3D&uc=94",
            "mediaPreviewUrl": "https://cf-st.sc-cdn.net/d/aUFzsbb4CKroNT0pRdE4G.410.IRZXSOY?mo=GkAaFjIBBDoBfUIGCPa5qdAGSAJQXmABcAFQxQFaEERmTGFyZ2VUaHVtYm5haWyiARAImgMiCxIAKgdJUlpYU09Z&uc=94",
            "timestampInSec": 1779062266,
            "publishedAt": "2026-05-17T23:57:46Z"
          },
          {
            "snapIndex": 3,
            "snapMediaType": 0,
            "mediaUrl": "https://cf-st.sc-cdn.net/d/yWteTz76gf53bxwLBNjoX.400.IRZXSOY?mo=GlwaCTIBBFBeYAFwAVDBAVoQUHVibGljSW1hZ2VTdG9yeaIBHwiQAyIaCg06AX1CBgj2uanQBkgCEgAqB0lSWlhTT1miARcI5wciEgoFMgF9SAQSACoHSVJaWFNPWQ%3D%3D&uc=94",
            "mediaPreviewUrl": "https://cf-st.sc-cdn.net/d/yWteTz76gf53bxwLBNjoX.410.IRZXSOY?mo=GkAaFjIBBDoBfUIGCPa5qdAGSAJQXmABcAFQxQFaEERmTGFyZ2VUaHVtYm5haWyiARAImgMiCxIAKgdJUlpYU09Z&uc=94",
            "timestampInSec": 1779062542,
            "publishedAt": "2026-05-18T00:02:22Z"
          },
          {
            "snapIndex": 4,
            "snapMediaType": 1,
            "mediaType": "video",
            "mediaUrl": "https://cf-st.sc-cdn.net/d/bkKNcxrjrFvKcF4iJkspN.1034.IRZXSOY?mo=GmQaFjIBBDoBfUIGCPW5qdAGSANQXmABcAFQyAFaB0RmTWVkaWGiATgIiggSJgokCNWLViABMOADONQGQAFKDgoJTRgiFxgaGBwbEPQDUM6zAWgCIgsSACoHSVJaWFNPWZADzrMB&uc=94",
            "mediaPreviewUrl": "https://cf-st.sc-cdn.net/d/bkKNcxrjrFvKcF4iJkspN.410.IRZXSOY?mo=GkAaFjIBBDoBfUIGCIG6qdAGSAJQXmABcAFQxQFaEERmTGFyZ2VUaHVtYm5haWyiARAImgMiCxIAKgdJUlpYU09Z&uc=94",
            "timestampInSec": 1779062847,
            "publishedAt": "2026-05-18T00:07:27Z"
          },
          {
            "snapIndex": 5,
            "snapMediaType": 1,
            "mediaType": "video",
            "mediaUrl": "https://cf-st.sc-cdn.net/d/z0HUGaIJfHJ4CMfZAYPgo.1034.IRZXSOY?mo=GmUaFjIBBDoBfUIGCPW5qdAGSANQXmABcAFQyAFaB0RmTWVkaWGiATkIiggSJwolCO7JpAEgATDgAzjUBkABSg4KCWwcIR4eFx8gIBD0A1DsvwJoAiILEgAqB0lSWlhTT1mQA-y_Ag%3D%3D&uc=94",
            "mediaPreviewUrl": "https://cf-st.sc-cdn.net/d/z0HUGaIJfHJ4CMfZAYPgo.410.IRZXSOY?mo=GkAaFjIBBDoBfUIGCI-6qdAGSAJQXmABcAFQxQFaEERmTGFyZ2VUaHVtYm5haWyiARAImgMiCxIAKgdJUlpYU09Z&uc=94",
            "timestampInSec": 1779063076,
            "publishedAt": "2026-05-18T00:11:16Z"
          },
          {
            "snapIndex": 6,
            "snapMediaType": 0,
            "mediaUrl": "https://cf-st.sc-cdn.net/d/Q7U6frp3B5dB2EsIvVR2y.400.IRZXSOY?mo=GlwaCTIBBFBeYAFwAVDBAVoQUHVibGljSW1hZ2VTdG9yeaIBHwiQAyIaCg06AX1CBgj2uanQBkgCEgAqB0lSWlhTT1miARcI5wciEgoFMgF9SAQSACoHSVJaWFNPWQ%3D%3D&uc=94",
            "mediaPreviewUrl": "https://cf-st.sc-cdn.net/d/Q7U6frp3B5dB2EsIvVR2y.410.IRZXSOY?mo=GkAaFjIBBDoBfUIGCPa5qdAGSAJQXmABcAFQxQFaEERmTGFyZ2VUaHVtYm5haWyiARAImgMiCxIAKgdJUlpYU09Z&uc=94",
            "timestampInSec": 1779063199,
            "publishedAt": "2026-05-18T00:13:19Z"
          },
          {
            "snapIndex": 7,
            "snapMediaType": 1,
            "mediaType": "video",
            "mediaUrl": "https://cf-st.sc-cdn.net/d/5F73IW97qhCT4XrBuP22E.1322.IRZXSOY?mo=GmYaFjIBBDoBfUIGCJG6qdAGSAJQXmABcAFQwgFaB0RmTWVkaWGiAToIqgoSKAomCPyi-wIgATDgAzjUBkABSg8KCpIBQzgwNxtNTjkQ9ANQ8roDaAIiCxIAKgdJUlpYU09ZkAPyugM%3D&uc=94",
            "mediaPreviewUrl": "https://cf-st.sc-cdn.net/d/5F73IW97qhCT4XrBuP22E.410.IRZXSOY?mo=GkAaFjIBBDoBfUIGCJG6qdAGSAJQXmABcAFQxQFaEERmTGFyZ2VUaHVtYm5haWyiARAImgMiCxIAKgdJUlpYU09Z&uc=94",
            "timestampInSec": 1779063467,
            "publishedAt": "2026-05-18T00:17:47Z"
          },
          {
            "snapIndex": 8,
            "snapMediaType": 1,
            "mediaType": "video",
            "mediaUrl": "https://cf-st.sc-cdn.net/d/zHgfrl78n1JPlSHJ9AoVT.1322.IRZXSOY?mo=GmMaFjIBBDoBfUIGCPq5qdAGSAJQXmABcAFQwgFaB0RmTWVkaWGiATgIqgoSJgokCJiSSyABMOADONQGQAFKDwoKjAFiNDU4Tj0pPhD0A1CQTmgCIgsSACoHSVJaWFNPWZADkE4%3D&uc=94",
            "mediaPreviewUrl": "https://cf-st.sc-cdn.net/d/zHgfrl78n1JPlSHJ9AoVT.410.IRZXSOY?mo=GkAaFjIBBDoBfUIGCPq5qdAGSAJQXmABcAFQxQFaEERmTGFyZ2VUaHVtYm5haWyiARAImgMiCxIAKgdJUlpYU09Z&uc=94",
            "timestampInSec": 1779043800,
            "publishedAt": "2026-05-17T18:50:00Z"
          },
          {
            "snapIndex": 9,
            "snapMediaType": 1,
            "mediaType": "video",
            "mediaUrl": "https://cf-st.sc-cdn.net/d/e0D4pPGJLQajP0KIwOBrY.1322.IRZXSOY?mo=GmMaFjIBBDoBfUIGCP65qdAGSAJQXmABcAFQwgFaB0RmTWVkaWGiATgIqgoSJgokCLKKSyABMOADONQGQAFKDwoKkQFPQ0VFSiUzOhD0A1CQTmgCIgsSACoHSVJaWFNPWZADkE4%3D&uc=94",
            "mediaPreviewUrl": "https://cf-st.sc-cdn.net/d/e0D4pPGJLQajP0KIwOBrY.410.IRZXSOY?mo=GkAaFjIBBDoBfUIGCP65qdAGSAJQXmABcAFQxQFaEERmTGFyZ2VUaHVtYm5haWyiARAImgMiCxIAKgdJUlpYU09Z&uc=94",
            "timestampInSec": 1779043800,
            "publishedAt": "2026-05-17T18:50:00Z"
          },
          {
            "snapIndex": 10,
            "snapMediaType": 1,
            "mediaType": "video",
            "mediaUrl": "https://cf-st.sc-cdn.net/d/YFjgcPhNKaSagCMpgvz0G.1322.IRZXSOY?mo=GmMaFjIBBDoBfUIGCPy5qdAGSAJQXmABcAFQwgFaB0RmTWVkaWGiATgIqgoSJgokCLf4SiABMOADONQGQAFKDwoKkwFJPlI3Rjo1MBD0A1CQTmgCIgsSACoHSVJaWFNPWZADkE4%3D&uc=94",
            "mediaPreviewUrl": "https://cf-st.sc-cdn.net/d/YFjgcPhNKaSagCMpgvz0G.410.IRZXSOY?mo=GkAaFjIBBDoBfUIGCPy5qdAGSAJQXmABcAFQxQFaEERmTGFyZ2VUaHVtYm5haWyiARAImgMiCxIAKgdJUlpYU09Z&uc=94",
            "timestampInSec": 1779043800,
            "publishedAt": "2026-05-17T18:50:00Z"
          },
          {
            "snapIndex": 11,
            "snapMediaType": 1,
            "mediaType": "video",
            "mediaUrl": "https://cf-st.sc-cdn.net/d/VvRTF9fO6rH6gqTvx51iq.1322.IRZXSOY?mo=GmMaFjIBBDoBfUIGCPq5qdAGSAJQXmABcAFQwgFaB0RmTWVkaWGiATgIqgoSJgokCMGXSyABMOADONQGQAFKDwoKmwFbMUQzNj0_MRD0A1CQTmgCIgsSACoHSVJaWFNPWZADkE4%3D&uc=94",
            "mediaPreviewUrl": "https://cf-st.sc-cdn.net/d/VvRTF9fO6rH6gqTvx51iq.410.IRZXSOY?mo=GkAaFjIBBDoBfUIGCPq5qdAGSAJQXmABcAFQxQFaEERmTGFyZ2VUaHVtYm5haWyiARAImgMiCxIAKgdJUlpYU09Z&uc=94",
            "timestampInSec": 1779043800,
            "publishedAt": "2026-05-17T18:50:00Z"
          },
          {
            "snapIndex": 12,
            "snapMediaType": 1,
            "mediaType": "video",
            "mediaUrl": "https://cf-st.sc-cdn.net/d/7E9dIi2bzc0IFIz9aUylf.1322.IRZXSOY?mo=GmMaFjIBBDoBfUIGCPq5qdAGSAJQXmABcAFQwgFaB0RmTWVkaWGiATgIqgoSJgokCM-hNSABMOADONQGQAFKDwoKjgE3Q2AzPzo1LhD0A1CiNGgCIgsSACoHSVJaWFNPWZADojQ%3D&uc=94",
            "mediaPreviewUrl": "https://cf-st.sc-cdn.net/d/7E9dIi2bzc0IFIz9aUylf.410.IRZXSOY?mo=GkAaFjIBBDoBfUIGCPq5qdAGSAJQXmABcAFQxQFaEERmTGFyZ2VUaHVtYm5haWyiARAImgMiCxIAKgdJUlpYU09Z&uc=94",
            "timestampInSec": 1779043800,
            "publishedAt": "2026-05-17T18:50:00Z"
          },
          {
            "snapIndex": 13,
            "snapMediaType": 1,
            "mediaType": "video",
            "mediaUrl": "https://cf-st.sc-cdn.net/d/p7qvISq5j7n9QP9mtObXy.1322.IRZXSOY?mo=GmIaFjIBBDoBfUIGCPu5qdAGSAJQXmABcAFQwgFaB0RmTWVkaWGiATcIqgoSJQojCIfmRSABMOADONQGQAFKDgoJfUdMEisbIwxkEPQDUJBOaAIiCxIAKgdJUlpYU09ZkAOQTg%3D%3D&uc=94",
            "mediaPreviewUrl": "https://cf-st.sc-cdn.net/d/p7qvISq5j7n9QP9mtObXy.410.IRZXSOY?mo=GkAaFjIBBDoBfUIGCPu5qdAGSAJQXmABcAFQxQFaEERmTGFyZ2VUaHVtYm5haWyiARAImgMiCxIAKgdJUlpYU09Z&uc=94",
            "timestampInSec": 1779052325,
            "publishedAt": "2026-05-17T21:12:05Z"
          },
          {
            "snapIndex": 14,
            "snapMediaType": 1,
            "mediaType": "video",
            "mediaUrl": "https://cf-st.sc-cdn.net/d/1tS3V1RB1Kjqtz2uHPdmr.1322.IRZXSOY?mo=GmMaFjIBBDoBfUIGCIC6qdAGSAJQXmABcAFQwgFaB0RmTWVkaWGiATgIqgoSJgokCPCRSSABMOADONQGQAFKDwoKgAE4S1Q1HiEaHxD0A1CQTmgCIgsSACoHSVJaWFNPWZADkE4%3D&uc=94",
            "mediaPreviewUrl": "https://cf-st.sc-cdn.net/d/1tS3V1RB1Kjqtz2uHPdmr.410.IRZXSOY?mo=GkAaFjIBBDoBfUIGCIC6qdAGSAJQXmABcAFQxQFaEERmTGFyZ2VUaHVtYm5haWyiARAImgMiCxIAKgdJUlpYU09Z&uc=94",
            "timestampInSec": 1779052325,
            "publishedAt": "2026-05-17T21:12:05Z"
          },
          {
            "snapIndex": 15,
            "snapMediaType": 1,
            "mediaType": "video",
            "mediaUrl": "https://cf-st.sc-cdn.net/d/1m1gnNXDTM5CW50wRV4Fx.1322.IRZXSOY?mo=GmMaFjIBBDoBfUIGCPy5qdAGSAJQXmABcAFQwgFaB0RmTWVkaWGiATgIqgoSJgokCPWxRCABMOADONQGQAFKDwoKjAFeYBoUNSw0OBD0A1CQTmgCIgsSACoHSVJaWFNPWZADkE4%3D&uc=94",
            "mediaPreviewUrl": "https://cf-st.sc-cdn.net/d/1m1gnNXDTM5CW50wRV4Fx.410.IRZXSOY?mo=GkAaFjIBBDoBfUIGCPy5qdAGSAJQXmABcAFQxQFaEERmTGFyZ2VUaHVtYm5haWyiARAImgMiCxIAKgdJUlpYU09Z&uc=94",
            "timestampInSec": 1779052325,
            "publishedAt": "2026-05-17T21:12:05Z"
          },
          {
            "snapIndex": 16,
            "snapMediaType": 1,
            "mediaType": "video",
            "mediaUrl": "https://cf-st.sc-cdn.net/d/fNL09TCw12JQKIiJcjJxS.1322.IRZXSOY?mo=GmIaFjIBBDoBfUIGCP65qdAGSAJQXmABcAFQwgFaB0RmTWVkaWGiATcIqgoSJQojCIKYQCABMOADONQGQAFKDgoJXSsqJiIbFRgXEPQDUJBOaAIiCxIAKgdJUlpYU09ZkAOQTg%3D%3D&uc=94",
            "mediaPreviewUrl": "https://cf-st.sc-cdn.net/d/fNL09TCw12JQKIiJcjJxS.410.IRZXSOY?mo=GkAaFjIBBDoBfUIGCP65qdAGSAJQXmABcAFQxQFaEERmTGFyZ2VUaHVtYm5haWyiARAImgMiCxIAKgdJUlpYU09Z&uc=94",
            "timestampInSec": 1779052325,
            "publishedAt": "2026-05-17T21:12:05Z"
          },
          {
            "snapIndex": 17,
            "snapMediaType": 1,
            "mediaType": "video",
            "mediaUrl": "https://cf-st.sc-cdn.net/d/0HRD8MtVUMzV02TCQIss9.1322.IRZXSOY?mo=GmIaFjIBBDoBfUIGCPu5qdAGSAJQXmABcAFQwgFaB0RmTWVkaWGiATcIqgoSJQojCOWrLyABMOADONQGQAFKDgoJaSQiIhYQEW1cEPQDUNY6aAIiCxIAKgdJUlpYU09ZkAPWOg%3D%3D&uc=94",
            "mediaPreviewUrl": "https://cf-st.sc-cdn.net/d/0HRD8MtVUMzV02TCQIss9.410.IRZXSOY?mo=GkAaFjIBBDoBfUIGCPu5qdAGSAJQXmABcAFQxQFaEERmTGFyZ2VUaHVtYm5haWyiARAImgMiCxIAKgdJUlpYU09Z&uc=94",
            "timestampInSec": 1779052325,
            "publishedAt": "2026-05-17T21:12:05Z"
          },
          {
            "snapIndex": 18,
            "snapMediaType": 1,
            "mediaType": "video",
            "mediaUrl": "https://cf-st.sc-cdn.net/d/TiDvlLPc8CG3ezFXsrsaV.1322.IRZXSOY?mo=GmYaFjIBBDoBfUIGCI-6qdAGSAJQXmABcAFQwgFaB0RmTWVkaWGiAToIqgoSKAomCPPErwIgATDgAzjUBkABSg8KCpoBR0wSKxojF1YQ9ANQlvMCaAIiCxIAKgdJUlpYU09ZkAOW8wI%3D&uc=94",
            "mediaPreviewUrl": "https://cf-st.sc-cdn.net/d/TiDvlLPc8CG3ezFXsrsaV.410.IRZXSOY?mo=GkAaFjIBBDoBfUIGCI-6qdAGSAJQXmABcAFQxQFaEERmTGFyZ2VUaHVtYm5haWyiARAImgMiCxIAKgdJUlpYU09Z&uc=94",
            "timestampInSec": 1779063732,
            "publishedAt": "2026-05-18T00:22:12Z"
          }
        ]
      },
      {
        "highlightId": "{'value': '918b1b3e-d60a-43e9-b5cd-651335d4687e'}",
        "storyTitle": "{'value': '2026 All-Star Rosters ⭐️'}",
        "thumbnailUrl": "https://cf-st.sc-cdn.net/d/OVtsXn5gkLRCgYX1bsKWn.410?mo=GjcaFjIBBDoBfUIGCNXEiswGSAJQXmABcAFQxQFaEERmTGFyZ2VUaHVtYm5haWyiAQcImgMiAhIA&uc=94",
        "snapCount": 5,
        "firstSnapUrl": "https://cf-st.sc-cdn.net/d/OVtsXn5gkLRCgYX1bsKWn.400?mo=GkcaFDIBBDoBfUIGCNXEiswGUF5gAXABUMEBWhBQdWJsaWNJbWFnZVN0b3J5ogELCJADIgYKAkgCEgCiAQsI5wciBgoCSAMSAA%3D%3D&uc=94",
        "snapList": [
          {
            "snapIndex": 0,
            "snapMediaType": 0,
            "mediaUrl": "https://cf-st.sc-cdn.net/d/OVtsXn5gkLRCgYX1bsKWn.400?mo=GkcaFDIBBDoBfUIGCNXEiswGUF5gAXABUMEBWhBQdWJsaWNJbWFnZVN0b3J5ogELCJADIgYKAkgCEgCiAQsI5wciBgoCSAMSAA%3D%3D&uc=94",
            "mediaPreviewUrl": "https://cf-st.sc-cdn.net/d/OVtsXn5gkLRCgYX1bsKWn.410?mo=GjcaFjIBBDoBfUIGCNXEiswGSAJQXmABcAFQxQFaEERmTGFyZ2VUaHVtYm5haWyiAQcImgMiAhIA&uc=94",
            "timestampInSec": 1770168890,
            "publishedAt": "2026-02-04T01:34:50Z"
          },
          {
            "snapIndex": 1,
            "snapMediaType": 0,
            "mediaUrl": "https://cf-st.sc-cdn.net/d/9VxqlhBh839VRARSOGbNg.400?mo=GkcaFDIBBDoBfUIGCNXEiswGUF5gAXABUMEBWhBQdWJsaWNJbWFnZVN0b3J5ogELCJADIgYKAkgCEgCiAQsI5wciBgoCSAMSAA%3D%3D&uc=94",
            "mediaPreviewUrl": "https://cf-st.sc-cdn.net/d/9VxqlhBh839VRARSOGbNg.410?mo=GjcaFjIBBDoBfUIGCNXEiswGSAJQXmABcAFQxQFaEERmTGFyZ2VUaHVtYm5haWyiAQcImgMiAhIA&uc=94",
            "timestampInSec": 1770168890,
            "publishedAt": "2026-02-04T01:34:50Z"
          },
          {
            "snapIndex": 2,
            "snapMediaType": 0,
            "mediaUrl": "https://cf-st.sc-cdn.net/d/iYsmPWO07diOdM994g8xo.400?mo=Gk8aDDIBBDoBfVBeYAFwAVDBAVoQUHVibGljSW1hZ2VTdG9yeaIBEwiQAyIOCgpCBgjVxIrMBkgCEgCiARMI5wciDgoKQgYI1MSKzAZIAxIA&uc=94",
            "mediaPreviewUrl": "https://cf-st.sc-cdn.net/d/iYsmPWO07diOdM994g8xo.410?mo=GjcaFjIBBDoBfUIGCNXEiswGSAJQXmABcAFQxQFaEERmTGFyZ2VUaHVtYm5haWyiAQcImgMiAhIA&uc=94",
            "timestampInSec": 1770168890,
            "publishedAt": "2026-02-04T01:34:50Z"
          },
          {
            "snapIndex": 3,
            "snapMediaType": 0,
            "mediaUrl": "https://cf-st.sc-cdn.net/d/MjPzf75USbLSpgDtGWzjb.400?mo=Gk0aDjIBBDoBfUgCUF5gAXABUMEBWhBQdWJsaWNJbWFnZVN0b3J5ogERCJADIgwKCEIGCNXEiswGEgCiAREI5wciDAoIQgYI1MSKzAYSAA%3D%3D&uc=94",
            "mediaPreviewUrl": "https://cf-st.sc-cdn.net/d/MjPzf75USbLSpgDtGWzjb.410?mo=GjcaFjIBBDoBfUIGCNXEiswGSAJQXmABcAFQxQFaEERmTGFyZ2VUaHVtYm5haWyiAQcImgMiAhIA&uc=94",
            "timestampInSec": 1770168890,
            "publishedAt": "2026-02-04T01:34:50Z"
          },
          {
            "snapIndex": 4,
            "snapMediaType": 0,
            "mediaUrl": "https://cf-st.sc-cdn.net/d/w7OoZSkq2abp9kNl9uOZq.400?mo=GkoaCTIBBFBeYAFwAVDBAVoQUHVibGljSW1hZ2VTdG9yeaIBFgiQAyIRCg06AX1CBgjWxIrMBkgCEgCiAQ4I5wciCQoFMgF9SAMSAA%3D%3D&uc=94",
            "mediaPreviewUrl": "https://cf-st.sc-cdn.net/d/w7OoZSkq2abp9kNl9uOZq.410?mo=GjcaFjIBBDoBfUIGCNbEiswGSAJQXmABcAFQxQFaEERmTGFyZ2VUaHVtYm5haWyiAQcImgMiAhIA&uc=94",
            "timestampInSec": 1770168890,
            "publishedAt": "2026-02-04T01:34:50Z"
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
          "views": 13151,
          "shares": 13,
          "comments": 23,
          "boosts": 946,
          "recommends": 55
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
          "views": 8489,
          "shares": 2,
          "comments": 3,
          "boosts": 419,
          "recommends": 22
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
        "profileUrl": "https://www.snapchat.com/@warriors",
        "profilePictureUrl": "https://cf-st.sc-cdn.net/aps/bolt/aHR0cHM6Ly9jZi1zdC5zYy1jZG4ubmV0L2QvNjRqVjdIRlJMaHk1V21yS0MwNUZ2P2JvPUVnMGFBQm9BTWdFRVNBSlFHV0FCJnVjPTI1._RS0,640_FMjpeg",
        "isVerified": true,
        "hasStory": false,
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
        "profileUrl": "https://www.snapchat.com/@nfl",
        "profilePictureUrl": "https://cf-st.sc-cdn.net/aps/bolt/aHR0cHM6Ly9jZi1zdC5zYy1jZG4ubmV0L2QvT3NjakFOS0dwSWh1VzQwek9qRnowP2JvPUVnMGFBQm9BTWdFRVNBSlFHV0FCJnVjPTI1._RS0,640_FMjpeg",
        "isVerified": true,
        "hasStory": true,
        "hasCuratedHighlights": false,
        "hasSpotlightHighlights": false,
        "subscribeLink": {
          "oneLinkBaseUrl": "https://click.snapchat.com/aVHG",
          "deepLinkUrl": "https://www.snapchat.com/@nfl",
          "iosAppStoreUrl": "https://apps.apple.com/app/apple-store/id447188370?pt=614006&ct=add_user&mt=8"
        }
      },
      {
        "username": "lakerssnaps",
        "displayName": "Los Angeles Lakers",
        "profileUrl": "https://www.snapchat.com/@lakerssnaps",
        "profilePictureUrl": "https://cf-st.sc-cdn.net/aps/bolt/aHR0cHM6Ly9jZi1zdC5zYy1jZG4ubmV0L2QvbEplakhnM3lwRTd1dWEwdjliVjd6P2JvPUVna3lBUVJJQWxBWllBRSUzRCZ1Yz0yNQ._RS0,640_FMjpeg",
        "isVerified": true,
        "hasStory": false,
        "hasCuratedHighlights": false,
        "hasSpotlightHighlights": false,
        "subscribeLink": {
          "oneLinkBaseUrl": "https://click.snapchat.com/aVHG",
          "deepLinkUrl": "https://www.snapchat.com/@lakerssnaps",
          "iosAppStoreUrl": "https://apps.apple.com/app/apple-store/id447188370?pt=614006&ct=add_user&mt=8"
        }
      }
    ]
  },
  "soundcloud-artist": {
    "platform": "soundcloud",
    "id": "2976616",
    "url": "https://soundcloud.com/flume",
    "username": "Flume",
    "name": "Flume",
    "description": "Management: flume@threesixzero.com",
    "avatar": "https://i1.sndcdn.com/avatars-sAZPcKyZpXJ0J0u5-JHfNSg-large.jpg",
    "city": "Sydney",
    "countryCode": "AU",
    "verified": true,
    "followers": 2227656,
    "followings": 203,
    "trackCount": 307,
    "playlistCount": 46,
    "likesCount": 149
  },
  "soundcloud-artist-tracks": {
    "platform": "soundcloud",
    "artistUrl": "https://soundcloud.com/nasa",
    "totalReturned": 5,
    "nextCursor": "https://api-v2.soundcloud.com/users/112904040/tracks?offset=2026-07-13T13%3A25%3A32.000Z%2Ctracks%2C00000000002359662548&limit=5",
    "hasMore": true,
    "tracks": [
      {
        "platform": "soundcloud",
        "id": "2367219119",
        "url": "https://soundcloud.com/nasa/houston-we-have-a-podcast-iss-results-materials-science",
        "title": "Houston We Have a Podcast: ISS Results: Materials Science",
        "description": "On episode 430, Kim de Groh and Sylvie Crowell review what researchers have learned and published from the Materials International Space Station Experiment (MISSE) platform that tests how materials perform in the harsh environment of space.",
        "genre": "Science",
        "artist": "NASA",
        "artistUrl": "https://soundcloud.com/nasa",
        "artistAvatar": "https://i1.sndcdn.com/avatars-JUvAAPvAA86fmbVE-SH0i6g-large.jpg",
        "artistFollowers": 158701,
        "artistVerified": true,
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
          "space",
          "center",
          "jsc",
          "houston",
          "podcast",
          "international space station",
          "iss",
          "results",
          "stem"
        ]
      },
      {
        "platform": "soundcloud",
        "id": "2364347957",
        "url": "https://soundcloud.com/nasa/artemis-ii-el-regreso-de-la-1",
        "title": "Artemis II: El regreso de la humanidad a la Luna",
        "description": "Acompáñanos en esta edición especial de Universo curioso de la NASA mientras hacemos un recorrido por la misión Artemis II de principio a fin. Revivimos la expectación en los días previos al despegue, la potencia del histórico lanzamiento y el increíble viaje de la tripu-lación a través del espacio profundo. Exploramos los momentos más críticos de la misión —desde el emocionante sobrevuelo lunar hasta el exitoso amerizaje en el océano Pacífi-co— que completa un capítulo fundamental en esta nueva era de la exploración espacial.\nEncuentra más información sobre Artemis en: ciencia.nasa.gov/artemis",
        "genre": "Science",
        "artist": "NASA",
        "artistUrl": "https://soundcloud.com/nasa",
        "artistAvatar": "https://i1.sndcdn.com/avatars-JUvAAPvAA86fmbVE-SH0i6g-large.jpg",
        "artistFollowers": 158701,
        "artistVerified": true,
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
          "podcast",
          "artemis II",
          "español"
        ]
      },
      {
        "platform": "soundcloud",
        "id": "2364341774",
        "url": "https://soundcloud.com/nasa/artemis-ii-el-regreso-de-la",
        "title": "Artemis II: El regreso de la humanidad a la Luna",
        "description": "Acompáñanos en esta edición especial de Universo curioso de la NASA mientras hacemos un recorrido por la misión Artemis II de principio a fin. Revivimos la expectación en los días previos al despegue, la potencia del histórico lanzamiento y el increíble viaje de la tripu-lación a través del espacio profundo. Exploramos los momentos más críticos de la misión —desde el emocionante sobrevuelo lunar hasta el exitoso amerizaje en el océano Pacífi-co— que completa un capítulo fundamental en esta nueva era de la exploración espacial.\nEncuentra más información sobre Artemis en: ciencia.nasa.gov/artemis",
        "genre": "Science",
        "artist": "NASA",
        "artistUrl": "https://soundcloud.com/nasa",
        "artistAvatar": "https://i1.sndcdn.com/avatars-JUvAAPvAA86fmbVE-SH0i6g-large.jpg",
        "artistFollowers": 158701,
        "artistVerified": true,
        "durationMs": 3026998,
        "plays": 77,
        "likes": 1,
        "reposts": 1,
        "downloads": 0,
        "comments": 1,
        "publishedAt": "2026-07-20T13:58:53Z",
        "license": "all-rights-reserved",
        "downloadable": true,
        "streamable": true,
        "waveformUrl": "https://wave.sndcdn.com/T9HWxjE3giT0_m.json",
        "artwork": "https://i1.sndcdn.com/artworks-vHT95zmztFEO1K49-1BXSXA-large.jpg",
        "tags": [
          "nasa",
          "podcast",
          "artemis II",
          "español"
        ]
      },
      {
        "platform": "soundcloud",
        "id": "2362781033",
        "url": "https://soundcloud.com/nasa/houston-we-have-a-podcast-artemis-ii-lunar-science",
        "title": "Houston We Have a Podcast: Artemis II Lunar Science",
        "genre": "Science",
        "artist": "NASA",
        "artistUrl": "https://soundcloud.com/nasa",
        "artistAvatar": "https://i1.sndcdn.com/avatars-JUvAAPvAA86fmbVE-SH0i6g-large.jpg",
        "artistFollowers": 158701,
        "artistVerified": true,
        "durationMs": 3896506,
        "plays": 218,
        "likes": 7,
        "reposts": 2,
        "downloads": 2,
        "comments": 1,
        "publishedAt": "2026-07-17T14:14:16Z",
        "license": "all-rights-reserved",
        "downloadable": true,
        "streamable": true,
        "waveformUrl": "https://wave.sndcdn.com/qjsnPXxHkqu5_m.json",
        "artwork": "https://i1.sndcdn.com/artworks-RgcbuFe9TuzkFA17-H8C2Ig-large.jpg",
        "tags": [
          "lunar",
          "moon",
          "exploration",
          "artemis",
          "flyby",
          "photograpy"
        ]
      },
      {
        "platform": "soundcloud",
        "id": "2359662548",
        "url": "https://soundcloud.com/nasa/small-steps-giant-793608487",
        "title": "Small Steps, Giant Leaps Podcast Episode 177: Transformative Aeronautics",
        "description": "A NASA research program collaborates with universities to revolutionize the way we design, build, and operate aircraft. Angela Surgenor, deputy program director of the Transformative Aeronautics Concepts Program, explains.",
        "genre": "Science",
        "artist": "NASA",
        "artistUrl": "https://soundcloud.com/nasa",
        "artistAvatar": "https://i1.sndcdn.com/avatars-JUvAAPvAA86fmbVE-SH0i6g-large.jpg",
        "artistFollowers": 158701,
        "artistVerified": true,
        "durationMs": 1030088,
        "plays": 236,
        "likes": 5,
        "reposts": 1,
        "downloads": 0,
        "comments": 2,
        "publishedAt": "2026-07-13T13:25:32Z",
        "license": "all-rights-reserved",
        "downloadable": true,
        "streamable": true,
        "waveformUrl": "https://wave.sndcdn.com/bWaZbrbJNeYk_m.json",
        "artwork": "https://i1.sndcdn.com/artworks-P4yXCelBLW8JxnUB-SPPJRA-large.jpg",
        "tags": [
          "nasa",
          "podcast",
          "aeronautics",
          "concept"
        ]
      }
    ]
  },
  "soundcloud-track": {
    "platform": "soundcloud",
    "id": "2364347957",
    "url": "https://soundcloud.com/nasa/artemis-ii-el-regreso-de-la-1",
    "title": "Artemis II: El regreso de la humanidad a la Luna",
    "description": "Acompáñanos en esta edición especial de Universo curioso de la NASA mientras hacemos un recorrido por la misión Artemis II de principio a fin. Revivimos la expectación en los días previos al despegue, la potencia del histórico lanzamiento y el increíble viaje de la tripu-lación a través del espacio profundo. Exploramos los momentos más críticos de la misión —desde el emocionante sobrevuelo lunar hasta el exitoso amerizaje en el océano Pacífi-co— que completa un capítulo fundamental en esta nueva era de la exploración espacial.\nEncuentra más información sobre Artemis en: ciencia.nasa.gov/artemis",
    "genre": "Science",
    "artist": "NASA",
    "artistUrl": "https://soundcloud.com/nasa",
    "artistAvatar": "https://i1.sndcdn.com/avatars-JUvAAPvAA86fmbVE-SH0i6g-large.jpg",
    "artistFollowers": 158684,
    "artistVerified": true,
    "durationMs": 3026998,
    "plays": 122,
    "likes": 5,
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
      "podcast",
      "artemis II",
      "español"
    ]
  },
  "spotify-album": {
    "platform": "spotify",
    "type": "album",
    "uri": "spotify:album:151w1FgRZfnKZA9FEcg9Z3",
    "url": "https://open.spotify.com/album/151w1FgRZfnKZA9FEcg9Z3?si=7_7dkBwYR5aqiPjykdfmvQ",
    "name": "Midnights",
    "artists": [
      "Taylor Swift"
    ],
    "releaseYear": 2022,
    "image": "https://i.scdn.co/image/ab67616d00001e02bb54dde68cd23e2a268ae0f5",
    "totalTracks": 13,
    "raw": {
      "__typename": "Album",
      "uri": "spotify:album:151w1FgRZfnKZA9FEcg9Z3",
      "name": "Midnights",
      "artists": {
        "items": [
          {
            "id": "06HL4z0CvFAxyc27GXpf02",
            "profile": {
              "name": "Taylor Swift"
            },
            "sharingInfo": {
              "shareUrl": "https://open.spotify.com/artist/06HL4z0CvFAxyc27GXpf02?si=XVaLiKf4T0G7s35SUpHQTQ"
            },
            "uri": "spotify:artist:06HL4z0CvFAxyc27GXpf02",
            "visuals": {
              "avatarImage": {
                "sources": [
                  {
                    "height": 640,
                    "url": "https://i.scdn.co/image/ab6761610000e5ebe2e8e7ff002a4afda1c7147e",
                    "width": 640
                  },
                  {
                    "height": 160,
                    "url": "https://i.scdn.co/image/ab6761610000f178e2e8e7ff002a4afda1c7147e",
                    "width": 160
                  },
                  {
                    "height": 320,
                    "url": "https://i.scdn.co/image/ab67616100005174e2e8e7ff002a4afda1c7147e",
                    "width": 320
                  }
                ]
              }
            }
          }
        ],
        "totalCount": 1
      },
      "coverArt": {
        "extractedColors": {
          "colorDark": {
            "hex": "#7A7676"
          },
          "colorLight": {
            "hex": "#E8E0E0"
          },
          "colorRaw": {
            "hex": "#E8E0E0"
          }
        },
        "sources": [
          {
            "height": 300,
            "url": "https://i.scdn.co/image/ab67616d00001e02bb54dde68cd23e2a268ae0f5",
            "width": 300
          },
          {
            "height": 64,
            "url": "https://i.scdn.co/image/ab67616d00004851bb54dde68cd23e2a268ae0f5",
            "width": 64
          },
          {
            "height": 640,
            "url": "https://i.scdn.co/image/ab67616d0000b273bb54dde68cd23e2a268ae0f5",
            "width": 640
          }
        ]
      },
      "date": {
        "isoString": "2022-10-21T00:00:00Z",
        "precision": "DAY"
      },
      "tracksV2": {
        "items": [
          {
            "track": {
              "artists": {
                "items": [
                  {
                    "profile": {
                      "name": "Taylor Swift"
                    },
                    "uri": "spotify:artist:06HL4z0CvFAxyc27GXpf02"
                  }
                ]
              },
              "associationsV3": {
                "videoAssociations": {
                  "totalCount": 1
                }
              },
              "contentRating": {
                "label": "EXPLICIT"
              },
              "discNumber": 1,
              "duration": {
                "totalMilliseconds": 202395
              },
              "name": "Lavender Haze",
              "playability": {
                "playable": true
              },
              "playcount": "901032338",
              "saved": false,
              "trackNumber": 1,
              "uri": "spotify:track:5jQI2r1RdgtuT8S3iG8zFC"
            },
            "uid": "6a22a05d1c8523acd991"
          }
        ],
        "totalCount": 13
      },
      "sharingInfo": {
        "shareId": "7_7dkBwYR5aqiPjykdfmvQ",
        "shareUrl": "https://open.spotify.com/album/151w1FgRZfnKZA9FEcg9Z3?si=7_7dkBwYR5aqiPjykdfmvQ"
      }
    }
  },
  "spotify-artist": {
    "platform": "spotify",
    "type": "artist",
    "uri": "spotify:artist:06HL4z0CvFAxyc27GXpf02",
    "url": "https://open.spotify.com/artist/06HL4z0CvFAxyc27GXpf02?si=XzEUcLZ4RlmEQtnhJVQ2MQ",
    "name": "Taylor Swift",
    "description": "And, baby, that’s show business for you. New album The Life of a Showgirl. Available now ❤️‍&#x1f525;",
    "followers": 161714021,
    "monthlyListeners": 100752084,
    "image": "https://i.scdn.co/image/ab6761610000e5ebe2e8e7ff002a4afda1c7147e",
    "raw": {
      "__typename": "Artist",
      "discography": {
        "albums": {
          "items": [
            {
              "releases": {
                "items": [
                  {
                    "copyright": {
                      "items": [
                        {
                          "text": "© 2025 Taylor Swift",
                          "type": "C"
                        },
                        {
                          "text": "℗ 2025 Taylor Swift",
                          "type": "P"
                        }
                      ]
                    },
                    "coverArt": {
                      "sources": [
                        {
                          "height": 300,
                          "url": "https://i.scdn.co/image/ab67616d00001e02f756bdc2c11a985dc0c06d94",
                          "width": 300
                        },
                        {
                          "height": 64,
                          "url": "https://i.scdn.co/image/ab67616d00004851f756bdc2c11a985dc0c06d94",
                          "width": 64
                        }
                      ]
                    },
                    "date": {
                      "day": 7,
                      "month": 11,
                      "precision": "DAY",
                      "year": 2025
                    },
                    "id": "6QNMhoV8V0u7cFuhhUBOn7",
                    "label": "Taylor Swift",
                    "name": "The Life of a Showgirl + Acoustic Collection",
                    "playability": {
                      "playable": true,
                      "reason": "PLAYABLE"
                    },
                    "sharingInfo": {
                      "shareId": "KLxm6rCMQAm4YcjHJTOvWQ",
                      "shareUrl": "https://open.spotify.com/album/6QNMhoV8V0u7cFuhhUBOn7?si=KLxm6rCMQAm4YcjHJTOvWQ"
                    },
                    "tracks": {
                      "totalCount": 19
                    },
                    "type": "ALBUM",
                    "uri": "spotify:album:6QNMhoV8V0u7cFuhhUBOn7"
                  }
                ]
              }
            },
            {
              "releases": {
                "items": [
                  {
                    "copyright": {
                      "items": [
                        {
                          "text": "© 2025 Taylor Swift",
                          "type": "C"
                        },
                        {
                          "text": "℗ 2025 Taylor Swift",
                          "type": "P"
                        }
                      ]
                    },
                    "coverArt": {
                      "sources": [
                        {
                          "height": 300,
                          "url": "https://i.scdn.co/image/ab67616d00001e02d7812467811a7da6e6a44902",
                          "width": 300
                        },
                        {
                          "height": 64,
                          "url": "https://i.scdn.co/image/ab67616d00004851d7812467811a7da6e6a44902",
                          "width": 64
                        }
                      ]
                    },
                    "date": {
                      "day": 3,
                      "month": 10,
                      "precision": "DAY",
                      "year": 2025
                    },
                    "id": "4a6NzYL1YHRUgx9e3YZI6I",
                    "label": "Taylor Swift",
                    "name": "The Life of a Showgirl",
                    "playability": {
                      "playable": true,
                      "reason": "PLAYABLE"
                    },
                    "sharingInfo": {
                      "shareId": "iS6riwW_Qy-tXMrIyY9_XA",
                      "shareUrl": "https://open.spotify.com/album/4a6NzYL1YHRUgx9e3YZI6I?si=iS6riwW_Qy-tXMrIyY9_XA"
                    },
                    "tracks": {
                      "totalCount": 12
                    },
                    "type": "ALBUM",
                    "uri": "spotify:album:4a6NzYL1YHRUgx9e3YZI6I"
                  }
                ]
              }
            }
          ],
          "totalCount": 33
        },
        "compilations": {
          "items": [
            {
              "releases": {
                "items": [
                  {
                    "copyright": {
                      "items": [
                        {
                          "text": "© 2024 Taylor Swift",
                          "type": "C"
                        },
                        {
                          "text": "℗ 2024 Taylor Swift",
                          "type": "P"
                        }
                      ]
                    },
                    "coverArt": {
                      "sources": [
                        {
                          "height": 300,
                          "url": "https://i.scdn.co/image/ab67616d00001e02c246cd7fb142b383672627c8",
                          "width": 300
                        },
                        {
                          "height": 64,
                          "url": "https://i.scdn.co/image/ab67616d00004851c246cd7fb142b383672627c8",
                          "width": 64
                        }
                      ]
                    },
                    "date": {
                      "day": 3,
                      "month": 10,
                      "precision": "DAY",
                      "year": 2024
                    },
                    "id": "30gDvYhEgyTbGEdCIY8FWV",
                    "label": "Taylor Swift",
                    "name": "THE TORTURED POETS DEPARTMENT | TS The Eras Tour Setlist",
                    "playability": {
                      "playable": true,
                      "reason": "PLAYABLE"
                    },
                    "sharingInfo": {
                      "shareId": "kFkacM1QRMK5FJ9Hb-HIrw",
                      "shareUrl": "https://open.spotify.com/album/30gDvYhEgyTbGEdCIY8FWV?si=kFkacM1QRMK5FJ9Hb-HIrw"
                    },
                    "tracks": {
                      "totalCount": 7
                    },
                    "type": "COMPILATION",
                    "uri": "spotify:album:30gDvYhEgyTbGEdCIY8FWV"
                  }
                ]
              }
            }
          ],
          "totalCount": 1
        },
        "latest": {
          "copyright": {
            "items": [
              {
                "text": "© 2026 Wonderland Music Company, Inc. (BMI) / Pixar Music (BMI) and Walt Disney Music Company (ASCAP) / Pixar Talking Pictures (ASCAP)",
                "type": "C"
              },
              {
                "text": "℗ 2026 Walt Disney Records / Pixar",
                "type": "P"
              }
            ]
          },
          "coverArt": {
            "sources": [
              {
                "height": 300,
                "url": "https://i.scdn.co/image/ab67616d00001e02e8852f06eca817333d20e60b",
                "width": 300
              },
              {
                "height": 64,
                "url": "https://i.scdn.co/image/ab67616d00004851e8852f06eca817333d20e60b",
                "width": 64
              }
            ]
          },
          "date": {
            "day": 12,
            "month": 6,
            "precision": "DAY",
            "year": 2026
          },
          "id": "4Ii9whWXI1O1H01ziECRaG",
          "label": "Walt Disney Records / Pixar",
          "name": "I Knew It, I Knew You (From \"Toy Story 5\")",
          "playability": {
            "playable": true,
            "reason": "PLAYABLE"
          },
          "sharingInfo": {
            "shareId": "nZ66vs3RRJii1Y_Dx_t1Zg",
            "shareUrl": "https://open.spotify.com/album/4Ii9whWXI1O1H01ziECRaG?si=nZ66vs3RRJii1Y_Dx_t1Zg"
          },
          "tracks": {
            "totalCount": 3
          },
          "type": "SINGLE",
          "uri": "spotify:album:4Ii9whWXI1O1H01ziECRaG"
        },
        "popularReleasesAlbums": {
          "items": [
            {
              "copyright": {
                "items": [
                  {
                    "text": "© 2025 Taylor Swift",
                    "type": "C"
                  },
                  {
                    "text": "℗ 2025 Taylor Swift",
                    "type": "P"
                  }
                ]
              },
              "coverArt": {
                "sources": [
                  {
                    "height": 300,
                    "url": "https://i.scdn.co/image/ab67616d00001e02d7812467811a7da6e6a44902",
                    "width": 300
                  },
                  {
                    "height": 64,
                    "url": "https://i.scdn.co/image/ab67616d00004851d7812467811a7da6e6a44902",
                    "width": 64
                  }
                ]
              },
              "date": {
                "day": 3,
                "month": 10,
                "precision": "DAY",
                "year": 2025
              },
              "id": "4a6NzYL1YHRUgx9e3YZI6I",
              "label": "Taylor Swift",
              "name": "The Life of a Showgirl",
              "playability": {
                "playable": true,
                "reason": "PLAYABLE"
              },
              "sharingInfo": {
                "shareId": "vSJa5UaiQ2SUNY0VFGVwyw",
                "shareUrl": "https://open.spotify.com/album/4a6NzYL1YHRUgx9e3YZI6I?si=vSJa5UaiQ2SUNY0VFGVwyw"
              },
              "tracks": {
                "totalCount": 12
              },
              "type": "ALBUM",
              "uri": "spotify:album:4a6NzYL1YHRUgx9e3YZI6I"
            },
            {
              "copyright": {
                "items": [
                  {
                    "text": "© 2019 Taylor Swift",
                    "type": "C"
                  },
                  {
                    "text": "℗ 2019 Taylor Swift",
                    "type": "P"
                  }
                ]
              },
              "coverArt": {
                "sources": [
                  {
                    "height": 300,
                    "url": "https://i.scdn.co/image/ab67616d00001e02e787cffec20aa2a396a61647",
                    "width": 300
                  },
                  {
                    "height": 64,
                    "url": "https://i.scdn.co/image/ab67616d00004851e787cffec20aa2a396a61647",
                    "width": 64
                  }
                ]
              },
              "date": {
                "day": 23,
                "month": 8,
                "precision": "DAY",
                "year": 2019
              },
              "id": "1NAmidJlEaVgA3MpcPFYGq",
              "label": "Taylor Swift",
              "name": "Lover",
              "playability": {
                "playable": true,
                "reason": "PLAYABLE"
              },
              "sharingInfo": {
                "shareId": "wcjPySC6Qt-rziksFMcprg",
                "shareUrl": "https://open.spotify.com/album/1NAmidJlEaVgA3MpcPFYGq?si=wcjPySC6Qt-rziksFMcprg"
              },
              "tracks": {
                "totalCount": 18
              },
              "type": "ALBUM",
              "uri": "spotify:album:1NAmidJlEaVgA3MpcPFYGq"
            }
          ],
          "totalCount": 20
        },
        "singles": {
          "items": [
            {
              "releases": {
                "items": [
                  {
                    "copyright": {
                      "items": [
                        {
                          "text": "© 2026 Wonderland Music Company, Inc. (BMI) / Pixar Music (BMI) and Walt Disney Music Company (ASCAP) / Pixar Talking Pictures (ASCAP)",
                          "type": "C"
                        },
                        {
                          "text": "℗ 2026 Walt Disney Records / Pixar",
                          "type": "P"
                        }
                      ]
                    },
                    "coverArt": {
                      "sources": [
                        {
                          "height": 300,
                          "url": "https://i.scdn.co/image/ab67616d00001e02e8852f06eca817333d20e60b",
                          "width": 300
                        },
                        {
                          "height": 64,
                          "url": "https://i.scdn.co/image/ab67616d00004851e8852f06eca817333d20e60b",
                          "width": 64
                        }
                      ]
                    },
                    "date": {
                      "day": 12,
                      "month": 6,
                      "precision": "DAY",
                      "year": 2026
                    },
                    "id": "4Ii9whWXI1O1H01ziECRaG",
                    "label": "Walt Disney Records / Pixar",
                    "name": "I Knew It, I Knew You (From \"Toy Story 5\")",
                    "playability": {
                      "playable": true,
                      "reason": "PLAYABLE"
                    },
                    "sharingInfo": {
                      "shareId": "koh4Jx1QRJW7w80babxnKg",
                      "shareUrl": "https://open.spotify.com/album/4Ii9whWXI1O1H01ziECRaG?si=koh4Jx1QRJW7w80babxnKg"
                    },
                    "tracks": {
                      "totalCount": 3
                    },
                    "type": "SINGLE",
                    "uri": "spotify:album:4Ii9whWXI1O1H01ziECRaG"
                  }
                ]
              }
            },
            {
              "releases": {
                "items": [
                  {
                    "copyright": {
                      "items": [
                        {
                          "text": "© 2026 Taylor Swift",
                          "type": "C"
                        },
                        {
                          "text": "℗ 2026 Taylor Swift",
                          "type": "P"
                        }
                      ]
                    },
                    "coverArt": {
                      "sources": [
                        {
                          "height": 300,
                          "url": "https://i.scdn.co/image/ab67616d00001e02dc6e4c7774e0c77c210d3a31",
                          "width": 300
                        },
                        {
                          "height": 64,
                          "url": "https://i.scdn.co/image/ab67616d00004851dc6e4c7774e0c77c210d3a31",
                          "width": 64
                        }
                      ]
                    },
                    "date": {
                      "day": 31,
                      "month": 3,
                      "precision": "DAY",
                      "year": 2026
                    },
                    "id": "71GTik4z9bbKKY2EmUvkDI",
                    "label": "Taylor Swift",
                    "name": "Elizabeth Taylor",
                    "playability": {
                      "playable": true,
                      "reason": "PLAYABLE"
                    },
                    "sharingInfo": {
                      "shareId": "eyXqkQQWSeu4h9pEWv6G6A",
                      "shareUrl": "https://open.spotify.com/album/71GTik4z9bbKKY2EmUvkDI?si=eyXqkQQWSeu4h9pEWv6G6A"
                    },
                    "tracks": {
                      "totalCount": 3
                    },
                    "type": "SINGLE",
                    "uri": "spotify:album:71GTik4z9bbKKY2EmUvkDI"
                  }
                ]
              }
            }
          ],
          "totalCount": 79
        },
        "topTracks": {
          "items": [
            {
              "track": {
                "albumOfTrack": {
                  "coverArt": {
                    "sources": [
                      {
                        "url": "https://i.scdn.co/image/ab67616d00001e02d7812467811a7da6e6a44902"
                      },
                      {
                        "url": "https://i.scdn.co/image/ab67616d00004851d7812467811a7da6e6a44902"
                      }
                    ]
                  },
                  "uri": "spotify:album:4a6NzYL1YHRUgx9e3YZI6I"
                },
                "artists": {
                  "items": [
                    {
                      "profile": {
                        "name": "Taylor Swift"
                      },
                      "uri": "spotify:artist:06HL4z0CvFAxyc27GXpf02"
                    }
                  ]
                },
                "associationsV3": {
                  "videoAssociations": {
                    "totalCount": 1
                  }
                },
                "contentRating": {
                  "label": "NONE"
                },
                "discNumber": 1,
                "duration": {
                  "totalMilliseconds": 226073
                },
                "id": "53iuhJlwXhSER5J2IYYv1W",
                "name": "The Fate of Ophelia",
                "playability": {
                  "playable": true,
                  "reason": "PLAYABLE"
                },
                "playcount": "1564999602",
                "uri": "spotify:track:53iuhJlwXhSER5J2IYYv1W"
              },
              "uid": "231bf597ddd1da456200"
            },
            {
              "track": {
                "albumOfTrack": {
                  "coverArt": {
                    "sources": [
                      {
                        "url": "https://i.scdn.co/image/ab67616d00001e02a35a1d4983e2b4fd0094f910"
                      },
                      {
                        "url": "https://i.scdn.co/image/ab67616d00004851a35a1d4983e2b4fd0094f910"
                      }
                    ]
                  },
                  "uri": "spotify:album:3ZLIShtR6Fjs4nTWFpBUB6"
                },
                "artists": {
                  "items": [
                    {
                      "profile": {
                        "name": "Taylor Swift"
                      },
                      "uri": "spotify:artist:06HL4z0CvFAxyc27GXpf02"
                    }
                  ]
                },
                "associationsV3": {
                  "videoAssociations": {
                    "totalCount": 1
                  }
                },
                "contentRating": {
                  "label": "NONE"
                },
                "discNumber": 1,
                "duration": {
                  "totalMilliseconds": 178186
                },
                "id": "5uPaqMMt59KGrdKIitDRqa",
                "name": "I Knew It, I Knew You - From \"Toy Story 5\"",
                "playability": {
                  "playable": true,
                  "reason": "PLAYABLE"
                },
                "playcount": "133109572",
                "uri": "spotify:track:5uPaqMMt59KGrdKIitDRqa"
              },
              "uid": "063fb4f3170db71ba947"
            }
          ]
        }
      },
      "goods": {
        "concerts": {
          "items": [],
          "totalCount": 0
        }
      },
      "headerImage": {
        "data": {
          "__typename": "ImageV2",
          "sources": [
            {
              "maxHeight": 640,
              "maxWidth": 1494,
              "url": "https://image-cdn-fa.spotifycdn.com/image/ab67618600000194c45b07608a062f02a9c89bab"
            },
            {
              "maxHeight": 1080,
              "maxWidth": 1920,
              "url": "https://i2o.scdn.co/image/ab67618600001667c45b07608a062f02a9c89bab"
            }
          ]
        }
      },
      "id": "06HL4z0CvFAxyc27GXpf02",
      "onPlatformReputationTrait": {
        "verification": {
          "isRegistered": true,
          "isVerified": true
        }
      },
      "profile": {
        "biography": {
          "text": "And, baby, that’s show business for you. New album The Life of a Showgirl. Available now ❤️‍&#x1f525;",
          "type": "AUTOBIOGRAPHY"
        },
        "externalLinks": {
          "items": [
            {
              "name": "FACEBOOK",
              "url": "https://facebook.com/TaylorSwift"
            },
            {
              "name": "INSTAGRAM",
              "url": "https://instagram.com/taylorswift"
            }
          ]
        },
        "name": "Taylor Swift"
      },
      "relatedContent": {
        "relatedArtists": {
          "items": [
            {
              "id": "74KM79TiuVKeVCqs8QtB0B",
              "profile": {
                "name": "Sabrina Carpenter"
              },
              "uri": "spotify:artist:74KM79TiuVKeVCqs8QtB0B",
              "visuals": {
                "avatarImage": {
                  "sources": [
                    {
                      "height": 640,
                      "url": "https://i.scdn.co/image/ab6761610000e5eb78e45cfa4697ce3c437cb455",
                      "width": 640
                    },
                    {
                      "height": 160,
                      "url": "https://i.scdn.co/image/ab6761610000f17878e45cfa4697ce3c437cb455",
                      "width": 160
                    }
                  ]
                }
              }
            },
            {
              "id": "66CXWjxzNUsdJxJ2JdwvnR",
              "profile": {
                "name": "Ariana Grande"
              },
              "uri": "spotify:artist:66CXWjxzNUsdJxJ2JdwvnR",
              "visuals": {
                "avatarImage": {
                  "sources": [
                    {
                      "height": 640,
                      "url": "https://i.scdn.co/image/ab6761610000e5eb766397ec42a573a53eb5fb87",
                      "width": 640
                    },
                    {
                      "height": 160,
                      "url": "https://i.scdn.co/image/ab6761610000f178766397ec42a573a53eb5fb87",
                      "width": 160
                    }
                  ]
                }
              }
            }
          ],
          "totalCount": 40
        }
      },
      "sharingInfo": {
        "shareId": "XzEUcLZ4RlmEQtnhJVQ2MQ",
        "shareUrl": "https://open.spotify.com/artist/06HL4z0CvFAxyc27GXpf02?si=XzEUcLZ4RlmEQtnhJVQ2MQ"
      },
      "stats": {
        "followers": 161714021,
        "monthlyListeners": 100752084,
        "topCities": {
          "items": [
            {
              "city": "London",
              "country": "GB",
              "numberOfListeners": 1630216,
              "region": "ENG"
            },
            {
              "city": "Quezon City",
              "country": "PH",
              "numberOfListeners": 1235715,
              "region": "00"
            }
          ]
        },
        "worldRank": 6
      },
      "uri": "spotify:artist:06HL4z0CvFAxyc27GXpf02",
      "visuals": {
        "avatarImage": {
          "extractedColors": {
            "colorRaw": {
              "hex": "#50A080"
            }
          },
          "sources": [
            {
              "height": 640,
              "url": "https://i.scdn.co/image/ab6761610000e5ebe2e8e7ff002a4afda1c7147e",
              "width": 640
            },
            {
              "height": 160,
              "url": "https://i.scdn.co/image/ab6761610000f178e2e8e7ff002a4afda1c7147e",
              "width": 160
            }
          ]
        }
      },
      "name": "Taylor Swift",
      "biography": {
        "text": "And, baby, that’s show business for you. New album The Life of a Showgirl. Available now ❤️‍&#x1f525;",
        "type": "AUTOBIOGRAPHY"
      }
    },
    "worldRank": 6,
    "topCities": [
      {
        "city": "London",
        "country": "GB",
        "region": "ENG",
        "listeners": 1630216
      },
      {
        "city": "Quezon City",
        "country": "PH",
        "region": "00",
        "listeners": 1235715
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
      },
      {
        "name": "TWITTER",
        "url": "https://twitter.com/taylorswift13"
      }
    ],
    "verified": true,
    "topTracks": [
      {
        "name": "The Fate of Ophelia",
        "uri": "spotify:track:53iuhJlwXhSER5J2IYYv1W",
        "url": "https://open.spotify.com/track/53iuhJlwXhSER5J2IYYv1W",
        "playCount": 1564999602,
        "durationMs": 226073,
        "albumUri": "spotify:album:4a6NzYL1YHRUgx9e3YZI6I",
        "image": "https://i.scdn.co/image/ab67616d00001e02d7812467811a7da6e6a44902",
        "explicit": false
      },
      {
        "name": "I Knew It, I Knew You - From \"Toy Story 5\"",
        "uri": "spotify:track:5uPaqMMt59KGrdKIitDRqa",
        "url": "https://open.spotify.com/track/5uPaqMMt59KGrdKIitDRqa",
        "playCount": 133109572,
        "durationMs": 178186,
        "albumUri": "spotify:album:3ZLIShtR6Fjs4nTWFpBUB6",
        "image": "https://i.scdn.co/image/ab67616d00001e02a35a1d4983e2b4fd0094f910",
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
        "image": "https://i.scdn.co/image/ab67616d00001e02f756bdc2c11a985dc0c06d94",
        "releaseYear": 2025,
        "totalTracks": 19
      },
      {
        "name": "The Life of a Showgirl",
        "uri": "spotify:album:4a6NzYL1YHRUgx9e3YZI6I",
        "url": "https://open.spotify.com/album/4a6NzYL1YHRUgx9e3YZI6I",
        "image": "https://i.scdn.co/image/ab67616d00001e02d7812467811a7da6e6a44902",
        "releaseYear": 2025,
        "totalTracks": 12
      }
    ],
    "singles": [
      {
        "name": "I Knew It, I Knew You (From \"Toy Story 5\")",
        "uri": "spotify:album:4Ii9whWXI1O1H01ziECRaG",
        "url": "https://open.spotify.com/album/4Ii9whWXI1O1H01ziECRaG",
        "image": "https://i.scdn.co/image/ab67616d00001e02e8852f06eca817333d20e60b",
        "releaseYear": 2026,
        "totalTracks": 3
      },
      {
        "name": "Elizabeth Taylor",
        "uri": "spotify:album:71GTik4z9bbKKY2EmUvkDI",
        "url": "https://open.spotify.com/album/71GTik4z9bbKKY2EmUvkDI",
        "image": "https://i.scdn.co/image/ab67616d00001e02dc6e4c7774e0c77c210d3a31",
        "releaseYear": 2026,
        "totalTracks": 3
      }
    ],
    "albumsCount": 33,
    "singlesCount": 79
  },
  "spotify-podcast": {
    "platform": "spotify",
    "type": "podcast",
    "uri": "spotify:show:4rOoJ6Egrf8K2IrywzwOMk",
    "url": "https://open.spotify.com/show/4rOoJ6Egrf8K2IrywzwOMk?si=cmNoUKzbRR6nimU5APejeg",
    "name": "The Joe Rogan Experience",
    "description": "The official podcast of comedian Joe Rogan.",
    "artists": [
      "Joe Rogan"
    ],
    "image": "https://i.scdn.co/image/ab6765630000f68d2e7936ee02774abeceb710f2",
    "totalEpisodes": 2725
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
      "artists": [
        "Joe Rogan"
      ],
      "image": "https://i.scdn.co/image/ab6765630000f68d1e1acaebe06610165612f1ef",
      "totalEpisodes": 2722,
      "raw": {
        "__typename": "Podcast",
        "id": "4rOoJ6Egrf8K2IrywzwOMk",
        "uri": "spotify:show:4rOoJ6Egrf8K2IrywzwOMk",
        "url": "https://open.spotify.com/show/4rOoJ6Egrf8K2IrywzwOMk",
        "name": "The Joe Rogan Experience",
        "publisher": {
          "name": "Joe Rogan"
        },
        "rating": {
          "averageRating": {
            "average": 4.656897342177361,
            "showAverage": true,
            "totalRatings": 951004
          },
          "canRate": true,
          "rating": {
            "rating": 0
          }
        },
        "mediaType": "MIXED",
        "consumptionOrderV2": "EPISODIC",
        "contentRatingV2": {
          "labels": [
            "EXPLICIT"
          ]
        },
        "contentType": "CONTENT_TYPE_PODCAST",
        "description": "The official podcast of comedian Joe Rogan.",
        "htmlDescription": "<p>The official podcast of comedian Joe Rogan.</p>",
        "playability": {
          "playable": true,
          "reason": "PLAYABLE"
        },
        "saved": false,
        "sharingInfo": {
          "shareId": "WBg3sTs_R1-a0Ni5DMBS5w",
          "shareUrl": "https://open.spotify.com/show/4rOoJ6Egrf8K2IrywzwOMk?si=WBg3sTs_R1-a0Ni5DMBS5w"
        },
        "showTypes": [
          "SHOW_TYPE_EXCLUSIVE"
        ],
        "topics": {
          "items": [
            {
              "__typename": "PodcastTopic",
              "title": "Comedy",
              "uri": "spotify:genre:0JQ5DAqbMKFNr6gDrHHVKL"
            }
          ]
        },
        "coverArt": {
          "sources": [
            {
              "height": 64,
              "url": "https://i.scdn.co/image/ab6765630000f68d1e1acaebe06610165612f1ef",
              "width": 64
            },
            {
              "height": 300,
              "url": "https://i.scdn.co/image/ab67656300005f1f1e1acaebe06610165612f1ef",
              "width": 300
            },
            {
              "height": 640,
              "url": "https://i.scdn.co/image/ab6765630000ba8a1e1acaebe06610165612f1ef",
              "width": 640
            }
          ]
        },
        "episodesV2": {
          "__typename": "ContextEpisodePage",
          "items": [
            {
              "entity": {
                "__typename": "EpisodeResponseWrapper",
                "data": {
                  "__typename": "Episode",
                  "uri": "spotify:episode:25xKO33R8MuWDHon82THE0"
                }
              }
            }
          ]
        },
        "episodes": {
          "data": {
            "podcastUnionV2": {
              "__typename": "Podcast",
              "episodesV2": {
                "__typename": "ContextEpisodePage",
                "items": [
                  {
                    "entity": {
                      "_uri": "spotify:episode:25xKO33R8MuWDHon82THE0",
                      "data": {
                        "__typename": "Episode",
                        "audio": {
                          "items": [
                            {
                              "url": "https://p.scdn.co/mp3-preview/2f9340916935c4bfd8de8ecfafe5344073226e74"
                            },
                            {
                              "url": "https://p.scdn.co/mp3-preview/8890ef960cf2ba6d513a689b53c0e0a34620f903"
                            },
                            {
                              "url": "https://p.scdn.co/mp3-preview/11526f62194c7d8ca5bd9e1a919f2b57122799ee"
                            },
                            {
                              "url": "https://p.scdn.co/mp3-preview/2f705e0d5358e718a0a98e03c31686174101de22"
                            },
                            {
                              "url": "https://p.scdn.co/mp3-preview/5ba8dfda70a8a1564ba28808d745a9501e00c4e5"
                            }
                          ]
                        },
                        "contentRating": {
                          "label": "EXPLICIT"
                        },
                        "coverArt": {
                          "sources": [
                            {
                              "height": 64,
                              "url": "https://i.scdn.co/image/ab6765630000f68dae7eda3fb0261372fba3e18c",
                              "width": 64
                            },
                            {
                              "height": 300,
                              "url": "https://i.scdn.co/image/ab67656300005f1fae7eda3fb0261372fba3e18c",
                              "width": 300
                            },
                            {
                              "height": 640,
                              "url": "https://i.scdn.co/image/ab6765630000ba8aae7eda3fb0261372fba3e18c",
                              "width": 640
                            }
                          ]
                        },
                        "description": "Jimmy Donaldson, better known as MrBeast, is a YouTuber, entrepreneur, and philanthropist. He is the founder of Beast Industries and Beast Philanthropy, and the creator and host of the Prime Video competition series “Beast Games.”www.beastgames.comwww.beastphilanthropy.orgwww.youtube.com/@MrBeast      Learn more about your ad choices. Visit podcastchoices.com/adchoices",
                        "duration": {
                          "totalMilliseconds": 10123050
                        },
                        "htmlDescription": "<p>Jimmy Donaldson, better known as MrBeast, is a YouTuber, entrepreneur, and philanthropist. He is the founder of Beast Industries and Beast Philanthropy, and the creator and host of the Prime Video competition series “Beast Games.”<br />www.beastgames.com<br />www.beastphilanthropy.org<br />www.youtube.com/&#64;MrBeast<br /></p><br/><p><br /><a href=\"https://pplx.ai/rogan\" rel=\"nofollow\"><br /></a><br /></p><br/><p><br /></p><br/><p><br /><a href=\"https://dkng.co/rogan\" rel=\"nofollow\"><br /></a><br /></p><br/><p><br /></p><br/><p><br /><a href=\"https://BlueChew.com\" rel=\"nofollow\"><br /></a><br /></p><p> </p><p>Learn more about your ad choices. Visit <a href=\"https://podcastchoices.com/adchoices\" rel=\"nofollow\">podcastchoices.com/adchoices</a></p>",
                        "id": "25xKO33R8MuWDHon82THE0",
                        "mediaTypes": [
                          "AUDIO",
                          "VIDEO"
                        ],
                        "name": "#2527 - MrBeast",
                        "playability": {
                          "playable": true,
                          "reason": "PLAYABLE"
                        },
                        "playedState": {
                          "playPositionMilliseconds": 0,
                          "state": "NOT_STARTED"
                        },
                        "podcastV2": {
                          "data": {
                            "__typename": "Podcast",
                            "coverArt": {
                              "sources": [
                                {
                                  "height": 64,
                                  "url": "https://i.scdn.co/image/ab6765630000f68d1e1acaebe06610165612f1ef",
                                  "width": 64
                                },
                                {
                                  "height": 300,
                                  "url": "https://i.scdn.co/image/ab67656300005f1f1e1acaebe06610165612f1ef",
                                  "width": 300
                                },
                                {
                                  "height": 640,
                                  "url": "https://i.scdn.co/image/ab6765630000ba8a1e1acaebe06610165612f1ef",
                                  "width": 640
                                }
                              ]
                            },
                            "name": "The Joe Rogan Experience",
                            "showTypes": [
                              "SHOW_TYPE_EXCLUSIVE"
                            ],
                            "uri": "spotify:show:4rOoJ6Egrf8K2IrywzwOMk"
                          }
                        },
                        "previewPlayback": {
                          "audioPreview": {
                            "cdnUrl": "https://p.scdn.co/mp3-preview/fbdde763b7027fc2c352b3e77e856072193fbe4b.mp3"
                          }
                        },
                        "releaseDate": {
                          "isoString": "2026-07-16T17:00:00Z",
                          "precision": "MINUTE"
                        },
                        "restrictions": {
                          "paywallContent": false
                        },
                        "sharingInfo": {
                          "shareId": "crkbtVYVRVelIsPXFLjhig",
                          "shareUrl": "https://open.spotify.com/episode/25xKO33R8MuWDHon82THE0?si=crkbtVYVRVelIsPXFLjhig"
                        },
                        "transcripts": {},
                        "type": "PODCAST_EPISODE",
                        "uri": "spotify:episode:25xKO33R8MuWDHon82THE0",
                        "visualIdentity": {
                          "sixteenByNineCoverImage": {
                            "image": {
                              "data": {
                                "__typename": "ImageV2",
                                "sources": [
                                  {
                                    "maxHeight": 720,
                                    "maxWidth": 1280,
                                    "url": "https://image-cdn-ak.spotifycdn.com/image/ab6772ab000030ae5a2498f3d761d4dae14c8927"
                                  },
                                  {
                                    "maxHeight": 360,
                                    "maxWidth": 640,
                                    "url": "https://image-cdn-ak.spotifycdn.com/image/ab6772ab0000e0e75a2498f3d761d4dae14c8927"
                                  }
                                ]
                              }
                            }
                          },
                          "squareCoverImage": {
                            "__typename": "VisualIdentityImage",
                            "extractedColorSet": {
                              "encoreBaseSetTextColor": {
                                "alpha": 255,
                                "blue": 110,
                                "green": 165,
                                "red": 255
                              },
                              "highContrast": {
                                "backgroundBase": {
                                  "alpha": 255,
                                  "blue": 0,
                                  "green": 48,
                                  "red": 145
                                },
                                "backgroundTintedBase": {
                                  "alpha": 255,
                                  "blue": 0,
                                  "green": 9,
                                  "red": 97
                                },
                                "textBase": {
                                  "alpha": 255,
                                  "blue": 255,
                                  "green": 255,
                                  "red": 255
                                },
                                "textBrightAccent": {
                                  "alpha": 255,
                                  "blue": 255,
                                  "green": 255,
                                  "red": 255
                                },
                                "textSubdued": {
                                  "alpha": 255,
                                  "blue": 154,
                                  "green": 192,
                                  "red": 255
                                }
                              },
                              "higherContrast": {
                                "backgroundBase": {
                                  "alpha": 255,
                                  "blue": 0,
                                  "green": 10,
                                  "red": 101
                                },
                                "backgroundTintedBase": {
                                  "alpha": 255,
                                  "blue": 40,
                                  "green": 55,
                                  "red": 144
                                },
                                "textBase": {
                                  "alpha": 255,
                                  "blue": 255,
                                  "green": 255,
                                  "red": 255
                                },
                                "textBrightAccent": {
                                  "alpha": 255,
                                  "blue": 96,
                                  "green": 215,
                                  "red": 30
                                },
                                "textSubdued": {
                                  "alpha": 255,
                                  "blue": 154,
                                  "green": 192,
                                  "red": 255
                                }
                              },
                              "minContrast": {
                                "backgroundBase": {
                                  "alpha": 255,
                                  "blue": 0,
                                  "green": 111,
                                  "red": 247
                                },
                                "backgroundTintedBase": {
                                  "alpha": 255,
                                  "blue": 0,
                                  "green": 83,
                                  "red": 217
                                },
                                "textBase": {
                                  "alpha": 255,
                                  "blue": 255,
                                  "green": 255,
                                  "red": 255
                                },
                                "textBrightAccent": {
                                  "alpha": 255,
                                  "blue": 255,
                                  "green": 255,
                                  "red": 255
                                },
                                "textSubdued": {
                                  "alpha": 255,
                                  "blue": 255,
                                  "green": 255,
                                  "red": 255
                                }
                              }
                            }
                          }
                        }
                      }
                    },
                    "uid": "3ee0522dfcd84cf71614"
                  },
                  {
                    "entity": {
                      "_uri": "spotify:episode:2J3m075zqKwZ43mysdezJK",
                      "data": {
                        "__typename": "Episode",
                        "audio": {
                          "items": [
                            {
                              "url": "https://p.scdn.co/mp3-preview/91e492f1704273826da8c4c533cd3d449069c1ba"
                            },
                            {
                              "url": "https://p.scdn.co/mp3-preview/e3b623e752a46a58c80a2cbeb45d299ec8a43b6b"
                            },
                            {
                              "url": "https://p.scdn.co/mp3-preview/e290eec9503c09202a2d195a402cfcfb6d7600ee"
                            },
                            {
                              "url": "https://p.scdn.co/mp3-preview/5a3a2149687091dc69d8979a9bfa69458c910d08"
                            },
                            {
                              "url": "https://p.scdn.co/mp3-preview/4278357f280cda29f19e320886179b093e261078"
                            }
                          ]
                        },
                        "contentRating": {
                          "label": "EXPLICIT"
                        },
                        "coverArt": {
                          "sources": [
                            {
                              "height": 64,
                              "url": "https://i.scdn.co/image/ab6765630000f68dca6df7e6f0bea75e26aa81e8",
                              "width": 64
                            },
                            {
                              "height": 300,
                              "url": "https://i.scdn.co/image/ab67656300005f1fca6df7e6f0bea75e26aa81e8",
                              "width": 300
                            },
                            {
                              "height": 640,
                              "url": "https://i.scdn.co/image/ab6765630000ba8aca6df7e6f0bea75e26aa81e8",
                              "width": 640
                            }
                          ]
                        },
                        "description": "JD Vance is the Vice President of the United States, a Marine Corps veteran, former U.S. Senator from Ohio, and author. His latest book, “Communion: Finding My Way Back to Faith,” is available now.www.harpercollins.com/products/communion-j-d-vancewww.whitehouse.gov/administration/jd-vance  Perplexity: Download the app or ask Perplexity anything at https://pplx.ai/rogan.  50% off your first box at https://www.thefarmersdog.com/rogan!  Sign up at https://foxnation.com to watch RAF 11! Learn more about your ad choices. Visit podcastchoices.com/adchoices",
                        "duration": {
                          "totalMilliseconds": 10414079
                        },
                        "htmlDescription": "<p>JD Vance is the Vice President of the United States, a Marine Corps veteran, former U.S. Senator from Ohio, and author. His latest book, “Communion: Finding My Way Back to Faith,” is available now.<br />www.harpercollins.com/products/communion-j-d-vance<br />www.whitehouse.gov/administration/jd-vance</p><br/><p><br /></p><br/><p>Perplexity: Download the app or ask Perplexity anything at <a href=\"https://pplx.ai/rogan\" rel=\"nofollow\">https://pplx.ai/rogan</a>.</p><br/><p><br /></p><br/><p>50% off your first box at <a href=\"https://www.thefarmersdog.com/rogan\" rel=\"nofollow\">https://www.thefarmersdog.com/rogan</a>!</p><br/><p><br /></p><br/><p>Sign up at <a href=\"https://foxnation.com\" rel=\"nofollow\">https://foxnation.com</a> to watch RAF 11!</p><p> </p><p>Learn more about your ad choices. Visit <a href=\"https://podcastchoices.com/adchoices\" rel=\"nofollow\">podcastchoices.com/adchoices</a></p>",
                        "id": "2J3m075zqKwZ43mysdezJK",
                        "mediaTypes": [
                          "AUDIO",
                          "VIDEO"
                        ],
                        "name": "#2526 - JD Vance",
                        "playability": {
                          "playable": true,
                          "reason": "PLAYABLE"
                        },
                        "playedState": {
                          "playPositionMilliseconds": 0,
                          "state": "NOT_STARTED"
                        },
                        "podcastV2": {
                          "data": {
                            "__typename": "Podcast",
                            "coverArt": {
                              "sources": [
                                {
                                  "height": 64,
                                  "url": "https://i.scdn.co/image/ab6765630000f68d1e1acaebe06610165612f1ef",
                                  "width": 64
                                },
                                {
                                  "height": 300,
                                  "url": "https://i.scdn.co/image/ab67656300005f1f1e1acaebe06610165612f1ef",
                                  "width": 300
                                },
                                {
                                  "height": 640,
                                  "url": "https://i.scdn.co/image/ab6765630000ba8a1e1acaebe06610165612f1ef",
                                  "width": 640
                                }
                              ]
                            },
                            "name": "The Joe Rogan Experience",
                            "showTypes": [
                              "SHOW_TYPE_EXCLUSIVE"
                            ],
                            "uri": "spotify:show:4rOoJ6Egrf8K2IrywzwOMk"
                          }
                        },
                        "previewPlayback": {
                          "audioPreview": {
                            "cdnUrl": "https://p.scdn.co/mp3-preview/ef7705919e95acc2a79d4d203e311220e8a85b6e.mp3"
                          }
                        },
                        "releaseDate": {
                          "isoString": "2026-07-15T17:00:00Z",
                          "precision": "MINUTE"
                        },
                        "restrictions": {
                          "paywallContent": false
                        },
                        "sharingInfo": {
                          "shareId": "jrpMxrx5R5SB9qjTByvPJA",
                          "shareUrl": "https://open.spotify.com/episode/2J3m075zqKwZ43mysdezJK?si=jrpMxrx5R5SB9qjTByvPJA"
                        },
                        "transcripts": {},
                        "type": "PODCAST_EPISODE",
                        "uri": "spotify:episode:2J3m075zqKwZ43mysdezJK",
                        "visualIdentity": {
                          "sixteenByNineCoverImage": {
                            "image": {
                              "data": {
                                "__typename": "ImageV2",
                                "sources": [
                                  {
                                    "maxHeight": 720,
                                    "maxWidth": 1280,
                                    "url": "https://image-cdn-ak.spotifycdn.com/image/ab6772ab000030ae6836d7fb3ec70a76a4d3d03c"
                                  },
                                  {
                                    "maxHeight": 360,
                                    "maxWidth": 640,
                                    "url": "https://image-cdn-ak.spotifycdn.com/image/ab6772ab0000e0e76836d7fb3ec70a76a4d3d03c"
                                  }
                                ]
                              }
                            }
                          },
                          "squareCoverImage": {
                            "__typename": "VisualIdentityImage",
                            "extractedColorSet": {
                              "encoreBaseSetTextColor": {
                                "alpha": 255,
                                "blue": 110,
                                "green": 165,
                                "red": 255
                              },
                              "highContrast": {
                                "backgroundBase": {
                                  "alpha": 255,
                                  "blue": 0,
                                  "green": 48,
                                  "red": 145
                                },
                                "backgroundTintedBase": {
                                  "alpha": 255,
                                  "blue": 0,
                                  "green": 9,
                                  "red": 97
                                },
                                "textBase": {
                                  "alpha": 255,
                                  "blue": 255,
                                  "green": 255,
                                  "red": 255
                                },
                                "textBrightAccent": {
                                  "alpha": 255,
                                  "blue": 255,
                                  "green": 255,
                                  "red": 255
                                },
                                "textSubdued": {
                                  "alpha": 255,
                                  "blue": 154,
                                  "green": 192,
                                  "red": 255
                                }
                              },
                              "higherContrast": {
                                "backgroundBase": {
                                  "alpha": 255,
                                  "blue": 0,
                                  "green": 10,
                                  "red": 101
                                },
                                "backgroundTintedBase": {
                                  "alpha": 255,
                                  "blue": 40,
                                  "green": 55,
                                  "red": 144
                                },
                                "textBase": {
                                  "alpha": 255,
                                  "blue": 255,
                                  "green": 255,
                                  "red": 255
                                },
                                "textBrightAccent": {
                                  "alpha": 255,
                                  "blue": 96,
                                  "green": 215,
                                  "red": 30
                                },
                                "textSubdued": {
                                  "alpha": 255,
                                  "blue": 154,
                                  "green": 192,
                                  "red": 255
                                }
                              },
                              "minContrast": {
                                "backgroundBase": {
                                  "alpha": 255,
                                  "blue": 0,
                                  "green": 111,
                                  "red": 247
                                },
                                "backgroundTintedBase": {
                                  "alpha": 255,
                                  "blue": 0,
                                  "green": 83,
                                  "red": 217
                                },
                                "textBase": {
                                  "alpha": 255,
                                  "blue": 255,
                                  "green": 255,
                                  "red": 255
                                },
                                "textBrightAccent": {
                                  "alpha": 255,
                                  "blue": 255,
                                  "green": 255,
                                  "red": 255
                                },
                                "textSubdued": {
                                  "alpha": 255,
                                  "blue": 255,
                                  "green": 255,
                                  "red": 255
                                }
                              }
                            }
                          }
                        }
                      }
                    },
                    "uid": "d9f30cfae1166fd3eea6"
                  },
                  {
                    "entity": {
                      "_uri": "spotify:episode:10TcPJFzFUDyyBzsj72nxi",
                      "data": {
                        "__typename": "Episode",
                        "audio": {
                          "items": [
                            {
                              "url": "https://p.scdn.co/mp3-preview/dc9dce35f8172cb8cb36e5249619fa5778eda411"
                            },
                            {
                              "url": "https://p.scdn.co/mp3-preview/c50b2d689e1b270d54af3a4e711b326dfc220c57"
                            },
                            {
                              "url": "https://p.scdn.co/mp3-preview/f231631aa10e95171e60fcd85427cc9e321adb0d"
                            },
                            {
                              "url": "https://p.scdn.co/mp3-preview/39e349e03c2e565bd53e7abab3bb60679df9f897"
                            },
                            {
                              "url": "https://p.scdn.co/mp3-preview/3e6c52bc966b6a826865f11be9be2003ac29e722"
                            }
                          ]
                        },
                        "contentRating": {
                          "label": "EXPLICIT"
                        },
                        "coverArt": {
                          "sources": [
                            {
                              "height": 64,
                              "url": "https://i.scdn.co/image/ab6765630000f68d010b1c625a39274e7a41e347",
                              "width": 64
                            },
                            {
                              "height": 300,
                              "url": "https://i.scdn.co/image/ab67656300005f1f010b1c625a39274e7a41e347",
                              "width": 300
                            },
                            {
                              "height": 640,
                              "url": "https://i.scdn.co/image/ab6765630000ba8a010b1c625a39274e7a41e347",
                              "width": 640
                            }
                          ]
                        },
                        "description": "Nick Bostrom is a philosopher whose work focuses on artificial intelligence, existential risk, and the future of humanity. He is Principal Researcher at the Macrostrategy Research Initiative and the author of several books, the most recent of which is “Deep Utopia: Life and Meaning in a Solved World.”www.simonandschuster.com/books/Deep-Utopia/Nick-Bostrom/9781646871643www.nickbostrom.com  Perplexity: Download the app or ask Perplexity anything at https://pplx.ai/rogan.  Switch today at https://Visible.com for just 25/mo. Or Save $10 on your first month of Visible+ Pro with code ROGAN.  Learn more about your ad choices. Visit podcastchoices.com/adchoices",
                        "duration": {
                          "totalMilliseconds": 8081918
                        },
                        "htmlDescription": "<p>Nick Bostrom is a philosopher whose work focuses on artificial intelligence, existential risk, and the future of humanity. He is Principal Researcher at the Macrostrategy Research Initiative and the author of several books, the most recent of which is “Deep Utopia: Life and Meaning in a Solved World.”<br />www.simonandschuster.com/books/Deep-Utopia/Nick-Bostrom/9781646871643<br />www.nickbostrom.com</p><br/><p><br /></p><br/><p>Perplexity: Download the app or ask Perplexity anything at <a href=\"https://pplx.ai/rogan\" rel=\"nofollow\">https://pplx.ai/rogan</a>.</p><br/><p><br /></p><br/><p>Switch today at <a href=\"https://Visible.com\" rel=\"nofollow\">https://Visible.com</a> for just 25/mo. Or Save $10 on your first month of Visible&#43; Pro with code ROGAN. </p><p> </p><p>Learn more about your ad choices. Visit <a href=\"https://podcastchoices.com/adchoices\" rel=\"nofollow\">podcastchoices.com/adchoices</a></p>",
                        "id": "10TcPJFzFUDyyBzsj72nxi",
                        "mediaTypes": [
                          "AUDIO",
                          "VIDEO"
                        ],
                        "name": "#2525 - Nick Bostrom",
                        "playability": {
                          "playable": true,
                          "reason": "PLAYABLE"
                        },
                        "playedState": {
                          "playPositionMilliseconds": 0,
                          "state": "NOT_STARTED"
                        },
                        "podcastV2": {
                          "data": {
                            "__typename": "Podcast",
                            "coverArt": {
                              "sources": [
                                {
                                  "height": 64,
                                  "url": "https://i.scdn.co/image/ab6765630000f68d1e1acaebe06610165612f1ef",
                                  "width": 64
                                },
                                {
                                  "height": 300,
                                  "url": "https://i.scdn.co/image/ab67656300005f1f1e1acaebe06610165612f1ef",
                                  "width": 300
                                },
                                {
                                  "height": 640,
                                  "url": "https://i.scdn.co/image/ab6765630000ba8a1e1acaebe06610165612f1ef",
                                  "width": 640
                                }
                              ]
                            },
                            "name": "The Joe Rogan Experience",
                            "showTypes": [
                              "SHOW_TYPE_EXCLUSIVE"
                            ],
                            "uri": "spotify:show:4rOoJ6Egrf8K2IrywzwOMk"
                          }
                        },
                        "previewPlayback": {
                          "audioPreview": {
                            "cdnUrl": "https://p.scdn.co/mp3-preview/ba46b42f2f38bb09f50e5a8a91877265c577cf44.mp3"
                          }
                        },
                        "releaseDate": {
                          "isoString": "2026-07-14T17:00:00Z",
                          "precision": "MINUTE"
                        },
                        "restrictions": {
                          "paywallContent": false
                        },
                        "sharingInfo": {
                          "shareId": "byEZRMiRS4aX_MSrQ-fxgQ",
                          "shareUrl": "https://open.spotify.com/episode/10TcPJFzFUDyyBzsj72nxi?si=byEZRMiRS4aX_MSrQ-fxgQ"
                        },
                        "transcripts": {},
                        "type": "PODCAST_EPISODE",
                        "uri": "spotify:episode:10TcPJFzFUDyyBzsj72nxi",
                        "visualIdentity": {
                          "sixteenByNineCoverImage": {
                            "image": {
                              "data": {
                                "__typename": "ImageV2",
                                "sources": [
                                  {
                                    "maxHeight": 720,
                                    "maxWidth": 1280,
                                    "url": "https://image-cdn-fa.spotifycdn.com/image/ab6772ab000030ae7648ac2ed841cbe3a7aa6d79"
                                  },
                                  {
                                    "maxHeight": 360,
                                    "maxWidth": 640,
                                    "url": "https://image-cdn-fa.spotifycdn.com/image/ab6772ab0000e0e77648ac2ed841cbe3a7aa6d79"
                                  }
                                ]
                              }
                            }
                          },
                          "squareCoverImage": {
                            "__typename": "VisualIdentityImage",
                            "extractedColorSet": {
                              "encoreBaseSetTextColor": {
                                "alpha": 255,
                                "blue": 110,
                                "green": 165,
                                "red": 255
                              },
                              "highContrast": {
                                "backgroundBase": {
                                  "alpha": 255,
                                  "blue": 0,
                                  "green": 48,
                                  "red": 145
                                },
                                "backgroundTintedBase": {
                                  "alpha": 255,
                                  "blue": 0,
                                  "green": 9,
                                  "red": 97
                                },
                                "textBase": {
                                  "alpha": 255,
                                  "blue": 255,
                                  "green": 255,
                                  "red": 255
                                },
                                "textBrightAccent": {
                                  "alpha": 255,
                                  "blue": 255,
                                  "green": 255,
                                  "red": 255
                                },
                                "textSubdued": {
                                  "alpha": 255,
                                  "blue": 154,
                                  "green": 192,
                                  "red": 255
                                }
                              },
                              "higherContrast": {
                                "backgroundBase": {
                                  "alpha": 255,
                                  "blue": 0,
                                  "green": 10,
                                  "red": 101
                                },
                                "backgroundTintedBase": {
                                  "alpha": 255,
                                  "blue": 40,
                                  "green": 55,
                                  "red": 144
                                },
                                "textBase": {
                                  "alpha": 255,
                                  "blue": 255,
                                  "green": 255,
                                  "red": 255
                                },
                                "textBrightAccent": {
                                  "alpha": 255,
                                  "blue": 96,
                                  "green": 215,
                                  "red": 30
                                },
                                "textSubdued": {
                                  "alpha": 255,
                                  "blue": 154,
                                  "green": 192,
                                  "red": 255
                                }
                              },
                              "minContrast": {
                                "backgroundBase": {
                                  "alpha": 255,
                                  "blue": 0,
                                  "green": 111,
                                  "red": 247
                                },
                                "backgroundTintedBase": {
                                  "alpha": 255,
                                  "blue": 0,
                                  "green": 83,
                                  "red": 217
                                },
                                "textBase": {
                                  "alpha": 255,
                                  "blue": 255,
                                  "green": 255,
                                  "red": 255
                                },
                                "textBrightAccent": {
                                  "alpha": 255,
                                  "blue": 255,
                                  "green": 255,
                                  "red": 255
                                },
                                "textSubdued": {
                                  "alpha": 255,
                                  "blue": 255,
                                  "green": 255,
                                  "red": 255
                                }
                              }
                            }
                          }
                        }
                      }
                    },
                    "uid": "0b9fa63d8ec82e69a4e4"
                  },
                  {
                    "entity": {
                      "_uri": "spotify:episode:4imTpV50bg8l1lIccXTqoC",
                      "data": {
                        "__typename": "Episode",
                        "audio": {
                          "items": [
                            {
                              "url": "https://p.scdn.co/mp3-preview/cc89c0abf536eb97de41b98330fdde309bce37e5"
                            },
                            {
                              "url": "https://p.scdn.co/mp3-preview/67bd280d3daaec5d2e6970cc0c6e4d0b607beda0"
                            },
                            {
                              "url": "https://p.scdn.co/mp3-preview/6b4756382c5050ad7ffb6177cd030bca47577499"
                            },
                            {
                              "url": "https://p.scdn.co/mp3-preview/57460ace6e3270464976529438184a90dcc4b2d9"
                            },
                            {
                              "url": "https://p.scdn.co/mp3-preview/b28cb79e3c220ef1fe1146c87fa08b117da9b946"
                            }
                          ]
                        },
                        "contentRating": {
                          "label": "EXPLICIT"
                        },
                        "coverArt": {
                          "sources": [
                            {
                              "height": 64,
                              "url": "https://i.scdn.co/image/ab6765630000f68dc31c4e7f94756b105c94914c",
                              "width": 64
                            },
                            {
                              "height": 300,
                              "url": "https://i.scdn.co/image/ab67656300005f1fc31c4e7f94756b105c94914c",
                              "width": 300
                            },
                            {
                              "height": 640,
                              "url": "https://i.scdn.co/image/ab6765630000ba8ac31c4e7f94756b105c94914c",
                              "width": 640
                            }
                          ]
                        },
                        "description": "Joe is joined by mixed martial artists John Rallo, Matt Serra, and Din Thomas. John Rallo owns Shogun Fights and is the owner and head coach of Ground Control Mixed Martial Arts Academy.www.groundcontrolbaltimore.comwww.shogunfights.com Matt Serra is a mixed martial artist and host of \"UFC Unfiltered\" with Jim Norton and \"Geeking Out with Matt Serra.\" He is the owner and an instructor at Serra BJJ.www.youtube.com/@MattSerraBJJwww.serrabjjacademy.com Din Thomas is a mixed martial arts analyst, actor, and host of \"Din Thomas' Fight Court.\"www.youtube.com/@FightCourt  Perplexity: Download the app or ask Perplexity anything at https://pplx.ai/rogan.  Don’t miss out on all the action this week at DraftKings! Download the DraftKings app today! Sign-up using https://dkng.co/rogan or through my promo code ROGAN.  Get watch party snacks and groceries on Uber Eats. Learn more about your ad choices. Visit podcastchoices.com/adchoices",
                        "duration": {
                          "totalMilliseconds": 9543167
                        },
                        "htmlDescription": "<p>Joe is joined by mixed martial artists John Rallo, Matt Serra, and Din Thomas.</p><br/><p>John Rallo owns Shogun Fights and is the owner and head coach of Ground Control Mixed Martial Arts Academy.<br />www.groundcontrolbaltimore.com<br />www.shogunfights.com</p><br/><p>Matt Serra is a mixed martial artist and host of &#34;UFC Unfiltered&#34; with Jim Norton and &#34;Geeking Out with Matt Serra.&#34; He is the owner and an instructor at Serra BJJ.<br />www.youtube.com/&#64;MattSerraBJJ<br />www.serrabjjacademy.com</p><br/><p>Din Thomas is a mixed martial arts analyst, actor, and host of &#34;Din Thomas&#39; Fight Court.&#34;<br />www.youtube.com/&#64;FightCourt</p><br/><p><br /></p><br/><p>Perplexity: Download the app or ask Perplexity anything at <a href=\"https://pplx.ai/rogan\" rel=\"nofollow\">https://pplx.ai/rogan</a>.</p><br/><p><br /></p><br/><p>Don’t miss out on all the action this week at DraftKings! Download the DraftKings app today! Sign-up using <a href=\"https://dkng.co/rogan\" rel=\"nofollow\">https://dkng.co/rogan</a> or through my promo code ROGAN.</p><br/><p><br /></p><br/><p>Get watch party snacks and groceries on Uber Eats.</p><p> </p><p>Learn more about your ad choices. Visit <a href=\"https://podcastchoices.com/adchoices\" rel=\"nofollow\">podcastchoices.com/adchoices</a></p>",
                        "id": "4imTpV50bg8l1lIccXTqoC",
                        "mediaTypes": [
                          "AUDIO",
                          "VIDEO"
                        ],
                        "name": "JRE MMA Show #182 - Protect Ya Neck",
                        "playability": {
                          "playable": true,
                          "reason": "PLAYABLE"
                        },
                        "playedState": {
                          "playPositionMilliseconds": 0,
                          "state": "NOT_STARTED"
                        },
                        "podcastV2": {
                          "data": {
                            "__typename": "Podcast",
                            "coverArt": {
                              "sources": [
                                {
                                  "height": 64,
                                  "url": "https://i.scdn.co/image/ab6765630000f68d1e1acaebe06610165612f1ef",
                                  "width": 64
                                },
                                {
                                  "height": 300,
                                  "url": "https://i.scdn.co/image/ab67656300005f1f1e1acaebe06610165612f1ef",
                                  "width": 300
                                },
                                {
                                  "height": 640,
                                  "url": "https://i.scdn.co/image/ab6765630000ba8a1e1acaebe06610165612f1ef",
                                  "width": 640
                                }
                              ]
                            },
                            "name": "The Joe Rogan Experience",
                            "showTypes": [
                              "SHOW_TYPE_EXCLUSIVE"
                            ],
                            "uri": "spotify:show:4rOoJ6Egrf8K2IrywzwOMk"
                          }
                        },
                        "previewPlayback": {
                          "audioPreview": {
                            "cdnUrl": "https://p.scdn.co/mp3-preview/e8a322b467ac820b6646eb3f789b2f9992ff320c.mp3"
                          }
                        },
                        "releaseDate": {
                          "isoString": "2026-07-09T17:00:00Z",
                          "precision": "MINUTE"
                        },
                        "restrictions": {
                          "paywallContent": false
                        },
                        "sharingInfo": {
                          "shareId": "-Bi4yBNXRnenXdEttOlHwQ",
                          "shareUrl": "https://open.spotify.com/episode/4imTpV50bg8l1lIccXTqoC?si=-Bi4yBNXRnenXdEttOlHwQ"
                        },
                        "transcripts": {},
                        "type": "PODCAST_EPISODE",
                        "uri": "spotify:episode:4imTpV50bg8l1lIccXTqoC",
                        "visualIdentity": {
                          "sixteenByNineCoverImage": {
                            "image": {
                              "data": {
                                "__typename": "ImageV2",
                                "sources": [
                                  {
                                    "maxHeight": 720,
                                    "maxWidth": 1280,
                                    "url": "https://image-cdn-fa.spotifycdn.com/image/ab6772ab000030aee781082c1d0b2280f811a5da"
                                  },
                                  {
                                    "maxHeight": 360,
                                    "maxWidth": 640,
                                    "url": "https://image-cdn-fa.spotifycdn.com/image/ab6772ab0000e0e7e781082c1d0b2280f811a5da"
                                  }
                                ]
                              }
                            }
                          },
                          "squareCoverImage": {
                            "__typename": "VisualIdentityImage",
                            "extractedColorSet": {
                              "encoreBaseSetTextColor": {
                                "alpha": 255,
                                "blue": 110,
                                "green": 165,
                                "red": 255
                              },
                              "highContrast": {
                                "backgroundBase": {
                                  "alpha": 255,
                                  "blue": 0,
                                  "green": 48,
                                  "red": 145
                                },
                                "backgroundTintedBase": {
                                  "alpha": 255,
                                  "blue": 0,
                                  "green": 9,
                                  "red": 97
                                },
                                "textBase": {
                                  "alpha": 255,
                                  "blue": 255,
                                  "green": 255,
                                  "red": 255
                                },
                                "textBrightAccent": {
                                  "alpha": 255,
                                  "blue": 255,
                                  "green": 255,
                                  "red": 255
                                },
                                "textSubdued": {
                                  "alpha": 255,
                                  "blue": 154,
                                  "green": 192,
                                  "red": 255
                                }
                              },
                              "higherContrast": {
                                "backgroundBase": {
                                  "alpha": 255,
                                  "blue": 0,
                                  "green": 10,
                                  "red": 101
                                },
                                "backgroundTintedBase": {
                                  "alpha": 255,
                                  "blue": 40,
                                  "green": 55,
                                  "red": 144
                                },
                                "textBase": {
                                  "alpha": 255,
                                  "blue": 255,
                                  "green": 255,
                                  "red": 255
                                },
                                "textBrightAccent": {
                                  "alpha": 255,
                                  "blue": 96,
                                  "green": 215,
                                  "red": 30
                                },
                                "textSubdued": {
                                  "alpha": 255,
                                  "blue": 154,
                                  "green": 192,
                                  "red": 255
                                }
                              },
                              "minContrast": {
                                "backgroundBase": {
                                  "alpha": 255,
                                  "blue": 0,
                                  "green": 111,
                                  "red": 247
                                },
                                "backgroundTintedBase": {
                                  "alpha": 255,
                                  "blue": 0,
                                  "green": 83,
                                  "red": 217
                                },
                                "textBase": {
                                  "alpha": 255,
                                  "blue": 255,
                                  "green": 255,
                                  "red": 255
                                },
                                "textBrightAccent": {
                                  "alpha": 255,
                                  "blue": 255,
                                  "green": 255,
                                  "red": 255
                                },
                                "textSubdued": {
                                  "alpha": 255,
                                  "blue": 255,
                                  "green": 255,
                                  "red": 255
                                }
                              }
                            }
                          }
                        }
                      }
                    },
                    "uid": "1bfe38367f56fd8df244"
                  },
                  {
                    "entity": {
                      "_uri": "spotify:episode:1f6tXaeR1XNYwSF0tqpEDT",
                      "data": {
                        "__typename": "Episode",
                        "audio": {
                          "items": [
                            {
                              "url": "https://p.scdn.co/mp3-preview/79d00facffbf57d9bad25910812d7af541131a63"
                            },
                            {
                              "url": "https://p.scdn.co/mp3-preview/b348d674403423ddbaa7619f7868fe24ba01b695"
                            },
                            {
                              "url": "https://p.scdn.co/mp3-preview/0f50bcd22706355dad3d825b2d3dd3ea635169b5"
                            },
                            {
                              "url": "https://p.scdn.co/mp3-preview/ecfad3e5334c0c3c516eeca1d8bd1d4f1e04a41e"
                            },
                            {
                              "url": "https://p.scdn.co/mp3-preview/ef72da5afac7d1e978bf98033d7d3d42e7c25c10"
                            }
                          ]
                        },
                        "contentRating": {
                          "label": "EXPLICIT"
                        },
                        "coverArt": {
                          "sources": [
                            {
                              "height": 64,
                              "url": "https://i.scdn.co/image/ab6765630000f68d0531ec0d584e51f31ca132ed",
                              "width": 64
                            },
                            {
                              "height": 300,
                              "url": "https://i.scdn.co/image/ab67656300005f1f0531ec0d584e51f31ca132ed",
                              "width": 300
                            },
                            {
                              "height": 640,
                              "url": "https://i.scdn.co/image/ab6765630000ba8a0531ec0d584e51f31ca132ed",
                              "width": 640
                            }
                          ]
                        },
                        "description": "Rupert Lowe is a British politician who has served as the member of Parliament for Great Yarmouth since 2024 and the leader of Restore Britain.  Perplexity: Download the app or ask Perplexity anything at https://pplx.ai/rogan.  onX Offroad: Try onX Offroad for 50% off- go to https://onXmaps.com/joerogan  This video is sponsored by BetterHelp. Visit https://BetterHelp.com/JRE Learn more about your ad choices. Visit podcastchoices.com/adchoices",
                        "duration": {
                          "totalMilliseconds": 7385641
                        },
                        "htmlDescription": "<p>Rupert Lowe is a British politician who has served as the member of Parliament for Great Yarmouth since 2024 and the leader of Restore Britain.</p><br/><p><br /></p><br/><p>Perplexity: Download the app or ask Perplexity anything at <a href=\"https://pplx.ai/rogan\" rel=\"nofollow\">https://pplx.ai/rogan</a>.</p><br/><p><br /></p><br/><p>onX Offroad: Try onX Offroad for 50% off- go to <a href=\"https://onXmaps.com/joerogan\" rel=\"nofollow\">https://onXmaps.com/joerogan</a></p><br/><p><br /></p><br/><p>This video is sponsored by BetterHelp. Visit <a href=\"https://BetterHelp.com/JRE\" rel=\"nofollow\">https://BetterHelp.com/JRE</a></p><p> </p><p>Learn more about your ad choices. Visit <a href=\"https://podcastchoices.com/adchoices\" rel=\"nofollow\">podcastchoices.com/adchoices</a></p>",
                        "id": "1f6tXaeR1XNYwSF0tqpEDT",
                        "mediaTypes": [
                          "AUDIO",
                          "VIDEO"
                        ],
                        "name": "#2524 - Rupert Lowe",
                        "playability": {
                          "playable": true,
                          "reason": "PLAYABLE"
                        },
                        "playedState": {
                          "playPositionMilliseconds": 0,
                          "state": "NOT_STARTED"
                        },
                        "podcastV2": {
                          "data": {
                            "__typename": "Podcast",
                            "coverArt": {
                              "sources": [
                                {
                                  "height": 64,
                                  "url": "https://i.scdn.co/image/ab6765630000f68d1e1acaebe06610165612f1ef",
                                  "width": 64
                                },
                                {
                                  "height": 300,
                                  "url": "https://i.scdn.co/image/ab67656300005f1f1e1acaebe06610165612f1ef",
                                  "width": 300
                                },
                                {
                                  "height": 640,
                                  "url": "https://i.scdn.co/image/ab6765630000ba8a1e1acaebe06610165612f1ef",
                                  "width": 640
                                }
                              ]
                            },
                            "name": "The Joe Rogan Experience",
                            "showTypes": [
                              "SHOW_TYPE_EXCLUSIVE"
                            ],
                            "uri": "spotify:show:4rOoJ6Egrf8K2IrywzwOMk"
                          }
                        },
                        "previewPlayback": {
                          "audioPreview": {
                            "cdnUrl": "https://p.scdn.co/mp3-preview/d9a20bdf0277625f2a094ad311845d3fb61d13d9.mp3"
                          }
                        },
                        "releaseDate": {
                          "isoString": "2026-07-08T17:00:00Z",
                          "precision": "MINUTE"
                        },
                        "restrictions": {
                          "paywallContent": false
                        },
                        "sharingInfo": {
                          "shareId": "Co0hsETLQr2JxhnuJeQp-g",
                          "shareUrl": "https://open.spotify.com/episode/1f6tXaeR1XNYwSF0tqpEDT?si=Co0hsETLQr2JxhnuJeQp-g"
                        },
                        "transcripts": {},
                        "type": "PODCAST_EPISODE",
                        "uri": "spotify:episode:1f6tXaeR1XNYwSF0tqpEDT",
                        "visualIdentity": {
                          "sixteenByNineCoverImage": {
                            "image": {
                              "data": {
                                "__typename": "ImageV2",
                                "sources": [
                                  {
                                    "maxHeight": 720,
                                    "maxWidth": 1280,
                                    "url": "https://image-cdn-fa.spotifycdn.com/image/ab6772ab000030ae90386d50241a150d4bcbc8e9"
                                  },
                                  {
                                    "maxHeight": 360,
                                    "maxWidth": 640,
                                    "url": "https://image-cdn-fa.spotifycdn.com/image/ab6772ab0000e0e790386d50241a150d4bcbc8e9"
                                  }
                                ]
                              }
                            }
                          },
                          "squareCoverImage": {
                            "__typename": "VisualIdentityImage",
                            "extractedColorSet": {
                              "encoreBaseSetTextColor": {
                                "alpha": 255,
                                "blue": 110,
                                "green": 165,
                                "red": 255
                              },
                              "highContrast": {
                                "backgroundBase": {
                                  "alpha": 255,
                                  "blue": 0,
                                  "green": 48,
                                  "red": 145
                                },
                                "backgroundTintedBase": {
                                  "alpha": 255,
                                  "blue": 0,
                                  "green": 9,
                                  "red": 97
                                },
                                "textBase": {
                                  "alpha": 255,
                                  "blue": 255,
                                  "green": 255,
                                  "red": 255
                                },
                                "textBrightAccent": {
                                  "alpha": 255,
                                  "blue": 255,
                                  "green": 255,
                                  "red": 255
                                },
                                "textSubdued": {
                                  "alpha": 255,
                                  "blue": 154,
                                  "green": 192,
                                  "red": 255
                                }
                              },
                              "higherContrast": {
                                "backgroundBase": {
                                  "alpha": 255,
                                  "blue": 0,
                                  "green": 10,
                                  "red": 101
                                },
                                "backgroundTintedBase": {
                                  "alpha": 255,
                                  "blue": 40,
                                  "green": 55,
                                  "red": 144
                                },
                                "textBase": {
                                  "alpha": 255,
                                  "blue": 255,
                                  "green": 255,
                                  "red": 255
                                },
                                "textBrightAccent": {
                                  "alpha": 255,
                                  "blue": 96,
                                  "green": 215,
                                  "red": 30
                                },
                                "textSubdued": {
                                  "alpha": 255,
                                  "blue": 154,
                                  "green": 192,
                                  "red": 255
                                }
                              },
                              "minContrast": {
                                "backgroundBase": {
                                  "alpha": 255,
                                  "blue": 0,
                                  "green": 111,
                                  "red": 247
                                },
                                "backgroundTintedBase": {
                                  "alpha": 255,
                                  "blue": 0,
                                  "green": 83,
                                  "red": 217
                                },
                                "textBase": {
                                  "alpha": 255,
                                  "blue": 255,
                                  "green": 255,
                                  "red": 255
                                },
                                "textBrightAccent": {
                                  "alpha": 255,
                                  "blue": 255,
                                  "green": 255,
                                  "red": 255
                                },
                                "textSubdued": {
                                  "alpha": 255,
                                  "blue": 255,
                                  "green": 255,
                                  "red": 255
                                }
                              }
                            }
                          }
                        }
                      }
                    },
                    "uid": "4a31a2aa46377a4f5d92"
                  }
                ],
                "pagingInfo": {
                  "nextOffset": 5
                },
                "totalCount": 2722
              },
              "id": "4rOoJ6Egrf8K2IrywzwOMk",
              "name": "The Joe Rogan Experience",
              "uri": "spotify:show:4rOoJ6Egrf8K2IrywzwOMk"
            }
          }
        }
      }
    },
    "totalReturned": 5,
    "episodes": [
      {
        "platform": "spotify",
        "type": "episode",
        "uri": "spotify:episode:25xKO33R8MuWDHon82THE0",
        "url": "https://open.spotify.com/episode/25xKO33R8MuWDHon82THE0?si=crkbtVYVRVelIsPXFLjhig",
        "name": "#2527 - MrBeast",
        "description": "Jimmy Donaldson, better known as MrBeast, is a YouTuber, entrepreneur, and philanthropist. He is the founder of Beast Industries and Beast Philanthropy, and the creator and host of the Prime Video competition series “Beast Games.”www.beastgames.comwww.beastphilanthropy.orgwww.youtube.com/@MrBeast      Learn more about your ad choices. Visit podcastchoices.com/adchoices",
        "durationMs": 10123050,
        "releaseYear": 2026,
        "image": "https://i.scdn.co/image/ab6765630000f68dae7eda3fb0261372fba3e18c",
        "raw": {
          "__typename": "Episode",
          "audio": {
            "items": [
              {
                "url": "https://p.scdn.co/mp3-preview/2f9340916935c4bfd8de8ecfafe5344073226e74"
              },
              {
                "url": "https://p.scdn.co/mp3-preview/8890ef960cf2ba6d513a689b53c0e0a34620f903"
              },
              {
                "url": "https://p.scdn.co/mp3-preview/11526f62194c7d8ca5bd9e1a919f2b57122799ee"
              },
              {
                "url": "https://p.scdn.co/mp3-preview/2f705e0d5358e718a0a98e03c31686174101de22"
              },
              {
                "url": "https://p.scdn.co/mp3-preview/5ba8dfda70a8a1564ba28808d745a9501e00c4e5"
              }
            ]
          },
          "contentRating": {
            "label": "EXPLICIT"
          },
          "coverArt": {
            "sources": [
              {
                "height": 64,
                "url": "https://i.scdn.co/image/ab6765630000f68dae7eda3fb0261372fba3e18c",
                "width": 64
              },
              {
                "height": 300,
                "url": "https://i.scdn.co/image/ab67656300005f1fae7eda3fb0261372fba3e18c",
                "width": 300
              },
              {
                "height": 640,
                "url": "https://i.scdn.co/image/ab6765630000ba8aae7eda3fb0261372fba3e18c",
                "width": 640
              }
            ]
          },
          "description": "Jimmy Donaldson, better known as MrBeast, is a YouTuber, entrepreneur, and philanthropist. He is the founder of Beast Industries and Beast Philanthropy, and the creator and host of the Prime Video competition series “Beast Games.”www.beastgames.comwww.beastphilanthropy.orgwww.youtube.com/@MrBeast      Learn more about your ad choices. Visit podcastchoices.com/adchoices",
          "duration": {
            "totalMilliseconds": 10123050
          },
          "htmlDescription": "<p>Jimmy Donaldson, better known as MrBeast, is a YouTuber, entrepreneur, and philanthropist. He is the founder of Beast Industries and Beast Philanthropy, and the creator and host of the Prime Video competition series “Beast Games.”<br />www.beastgames.com<br />www.beastphilanthropy.org<br />www.youtube.com/&#64;MrBeast<br /></p><br/><p><br /><a href=\"https://pplx.ai/rogan\" rel=\"nofollow\"><br /></a><br /></p><br/><p><br /></p><br/><p><br /><a href=\"https://dkng.co/rogan\" rel=\"nofollow\"><br /></a><br /></p><br/><p><br /></p><br/><p><br /><a href=\"https://BlueChew.com\" rel=\"nofollow\"><br /></a><br /></p><p> </p><p>Learn more about your ad choices. Visit <a href=\"https://podcastchoices.com/adchoices\" rel=\"nofollow\">podcastchoices.com/adchoices</a></p>",
          "id": "25xKO33R8MuWDHon82THE0",
          "mediaTypes": [
            "AUDIO",
            "VIDEO"
          ],
          "name": "#2527 - MrBeast",
          "playability": {
            "playable": true,
            "reason": "PLAYABLE"
          },
          "playedState": {
            "playPositionMilliseconds": 0,
            "state": "NOT_STARTED"
          },
          "podcastV2": {
            "data": {
              "__typename": "Podcast",
              "coverArt": {
                "sources": [
                  {
                    "height": 64,
                    "url": "https://i.scdn.co/image/ab6765630000f68d1e1acaebe06610165612f1ef",
                    "width": 64
                  },
                  {
                    "height": 300,
                    "url": "https://i.scdn.co/image/ab67656300005f1f1e1acaebe06610165612f1ef",
                    "width": 300
                  },
                  {
                    "height": 640,
                    "url": "https://i.scdn.co/image/ab6765630000ba8a1e1acaebe06610165612f1ef",
                    "width": 640
                  }
                ]
              },
              "name": "The Joe Rogan Experience",
              "showTypes": [
                "SHOW_TYPE_EXCLUSIVE"
              ],
              "uri": "spotify:show:4rOoJ6Egrf8K2IrywzwOMk"
            }
          },
          "previewPlayback": {
            "audioPreview": {
              "cdnUrl": "https://p.scdn.co/mp3-preview/fbdde763b7027fc2c352b3e77e856072193fbe4b.mp3"
            }
          },
          "releaseDate": {
            "isoString": "2026-07-16T17:00:00Z",
            "precision": "MINUTE"
          },
          "restrictions": {
            "paywallContent": false
          },
          "sharingInfo": {
            "shareId": "crkbtVYVRVelIsPXFLjhig",
            "shareUrl": "https://open.spotify.com/episode/25xKO33R8MuWDHon82THE0?si=crkbtVYVRVelIsPXFLjhig"
          },
          "transcripts": {},
          "type": "PODCAST_EPISODE",
          "uri": "spotify:episode:25xKO33R8MuWDHon82THE0",
          "visualIdentity": {
            "sixteenByNineCoverImage": {
              "image": {
                "data": {
                  "__typename": "ImageV2",
                  "sources": [
                    {
                      "maxHeight": 720,
                      "maxWidth": 1280,
                      "url": "https://image-cdn-ak.spotifycdn.com/image/ab6772ab000030ae5a2498f3d761d4dae14c8927"
                    },
                    {
                      "maxHeight": 360,
                      "maxWidth": 640,
                      "url": "https://image-cdn-ak.spotifycdn.com/image/ab6772ab0000e0e75a2498f3d761d4dae14c8927"
                    }
                  ]
                }
              }
            },
            "squareCoverImage": {
              "__typename": "VisualIdentityImage",
              "extractedColorSet": {
                "encoreBaseSetTextColor": {
                  "alpha": 255,
                  "blue": 110,
                  "green": 165,
                  "red": 255
                },
                "highContrast": {
                  "backgroundBase": {
                    "alpha": 255,
                    "blue": 0,
                    "green": 48,
                    "red": 145
                  },
                  "backgroundTintedBase": {
                    "alpha": 255,
                    "blue": 0,
                    "green": 9,
                    "red": 97
                  },
                  "textBase": {
                    "alpha": 255,
                    "blue": 255,
                    "green": 255,
                    "red": 255
                  },
                  "textBrightAccent": {
                    "alpha": 255,
                    "blue": 255,
                    "green": 255,
                    "red": 255
                  },
                  "textSubdued": {
                    "alpha": 255,
                    "blue": 154,
                    "green": 192,
                    "red": 255
                  }
                },
                "higherContrast": {
                  "backgroundBase": {
                    "alpha": 255,
                    "blue": 0,
                    "green": 10,
                    "red": 101
                  },
                  "backgroundTintedBase": {
                    "alpha": 255,
                    "blue": 40,
                    "green": 55,
                    "red": 144
                  },
                  "textBase": {
                    "alpha": 255,
                    "blue": 255,
                    "green": 255,
                    "red": 255
                  },
                  "textBrightAccent": {
                    "alpha": 255,
                    "blue": 96,
                    "green": 215,
                    "red": 30
                  },
                  "textSubdued": {
                    "alpha": 255,
                    "blue": 154,
                    "green": 192,
                    "red": 255
                  }
                },
                "minContrast": {
                  "backgroundBase": {
                    "alpha": 255,
                    "blue": 0,
                    "green": 111,
                    "red": 247
                  },
                  "backgroundTintedBase": {
                    "alpha": 255,
                    "blue": 0,
                    "green": 83,
                    "red": 217
                  },
                  "textBase": {
                    "alpha": 255,
                    "blue": 255,
                    "green": 255,
                    "red": 255
                  },
                  "textBrightAccent": {
                    "alpha": 255,
                    "blue": 255,
                    "green": 255,
                    "red": 255
                  },
                  "textSubdued": {
                    "alpha": 255,
                    "blue": 255,
                    "green": 255,
                    "red": 255
                  }
                }
              }
            }
          }
        }
      },
      {
        "platform": "spotify",
        "type": "episode",
        "uri": "spotify:episode:2J3m075zqKwZ43mysdezJK",
        "url": "https://open.spotify.com/episode/2J3m075zqKwZ43mysdezJK?si=jrpMxrx5R5SB9qjTByvPJA",
        "name": "#2526 - JD Vance",
        "description": "JD Vance is the Vice President of the United States, a Marine Corps veteran, former U.S. Senator from Ohio, and author. His latest book, “Communion: Finding My Way Back to Faith,” is available now.www.harpercollins.com/products/communion-j-d-vancewww.whitehouse.gov/administration/jd-vance  Perplexity: Download the app or ask Perplexity anything at https://pplx.ai/rogan.  50% off your first box at https://www.thefarmersdog.com/rogan!  Sign up at https://foxnation.com to watch RAF 11! Learn more about your ad choices. Visit podcastchoices.com/adchoices",
        "durationMs": 10414079,
        "releaseYear": 2026,
        "image": "https://i.scdn.co/image/ab6765630000f68dca6df7e6f0bea75e26aa81e8",
        "raw": {
          "__typename": "Episode",
          "audio": {
            "items": [
              {
                "url": "https://p.scdn.co/mp3-preview/91e492f1704273826da8c4c533cd3d449069c1ba"
              },
              {
                "url": "https://p.scdn.co/mp3-preview/e3b623e752a46a58c80a2cbeb45d299ec8a43b6b"
              },
              {
                "url": "https://p.scdn.co/mp3-preview/e290eec9503c09202a2d195a402cfcfb6d7600ee"
              },
              {
                "url": "https://p.scdn.co/mp3-preview/5a3a2149687091dc69d8979a9bfa69458c910d08"
              },
              {
                "url": "https://p.scdn.co/mp3-preview/4278357f280cda29f19e320886179b093e261078"
              }
            ]
          },
          "contentRating": {
            "label": "EXPLICIT"
          },
          "coverArt": {
            "sources": [
              {
                "height": 64,
                "url": "https://i.scdn.co/image/ab6765630000f68dca6df7e6f0bea75e26aa81e8",
                "width": 64
              },
              {
                "height": 300,
                "url": "https://i.scdn.co/image/ab67656300005f1fca6df7e6f0bea75e26aa81e8",
                "width": 300
              },
              {
                "height": 640,
                "url": "https://i.scdn.co/image/ab6765630000ba8aca6df7e6f0bea75e26aa81e8",
                "width": 640
              }
            ]
          },
          "description": "JD Vance is the Vice President of the United States, a Marine Corps veteran, former U.S. Senator from Ohio, and author. His latest book, “Communion: Finding My Way Back to Faith,” is available now.www.harpercollins.com/products/communion-j-d-vancewww.whitehouse.gov/administration/jd-vance  Perplexity: Download the app or ask Perplexity anything at https://pplx.ai/rogan.  50% off your first box at https://www.thefarmersdog.com/rogan!  Sign up at https://foxnation.com to watch RAF 11! Learn more about your ad choices. Visit podcastchoices.com/adchoices",
          "duration": {
            "totalMilliseconds": 10414079
          },
          "htmlDescription": "<p>JD Vance is the Vice President of the United States, a Marine Corps veteran, former U.S. Senator from Ohio, and author. His latest book, “Communion: Finding My Way Back to Faith,” is available now.<br />www.harpercollins.com/products/communion-j-d-vance<br />www.whitehouse.gov/administration/jd-vance</p><br/><p><br /></p><br/><p>Perplexity: Download the app or ask Perplexity anything at <a href=\"https://pplx.ai/rogan\" rel=\"nofollow\">https://pplx.ai/rogan</a>.</p><br/><p><br /></p><br/><p>50% off your first box at <a href=\"https://www.thefarmersdog.com/rogan\" rel=\"nofollow\">https://www.thefarmersdog.com/rogan</a>!</p><br/><p><br /></p><br/><p>Sign up at <a href=\"https://foxnation.com\" rel=\"nofollow\">https://foxnation.com</a> to watch RAF 11!</p><p> </p><p>Learn more about your ad choices. Visit <a href=\"https://podcastchoices.com/adchoices\" rel=\"nofollow\">podcastchoices.com/adchoices</a></p>",
          "id": "2J3m075zqKwZ43mysdezJK",
          "mediaTypes": [
            "AUDIO",
            "VIDEO"
          ],
          "name": "#2526 - JD Vance",
          "playability": {
            "playable": true,
            "reason": "PLAYABLE"
          },
          "playedState": {
            "playPositionMilliseconds": 0,
            "state": "NOT_STARTED"
          },
          "podcastV2": {
            "data": {
              "__typename": "Podcast",
              "coverArt": {
                "sources": [
                  {
                    "height": 64,
                    "url": "https://i.scdn.co/image/ab6765630000f68d1e1acaebe06610165612f1ef",
                    "width": 64
                  },
                  {
                    "height": 300,
                    "url": "https://i.scdn.co/image/ab67656300005f1f1e1acaebe06610165612f1ef",
                    "width": 300
                  },
                  {
                    "height": 640,
                    "url": "https://i.scdn.co/image/ab6765630000ba8a1e1acaebe06610165612f1ef",
                    "width": 640
                  }
                ]
              },
              "name": "The Joe Rogan Experience",
              "showTypes": [
                "SHOW_TYPE_EXCLUSIVE"
              ],
              "uri": "spotify:show:4rOoJ6Egrf8K2IrywzwOMk"
            }
          },
          "previewPlayback": {
            "audioPreview": {
              "cdnUrl": "https://p.scdn.co/mp3-preview/ef7705919e95acc2a79d4d203e311220e8a85b6e.mp3"
            }
          },
          "releaseDate": {
            "isoString": "2026-07-15T17:00:00Z",
            "precision": "MINUTE"
          },
          "restrictions": {
            "paywallContent": false
          },
          "sharingInfo": {
            "shareId": "jrpMxrx5R5SB9qjTByvPJA",
            "shareUrl": "https://open.spotify.com/episode/2J3m075zqKwZ43mysdezJK?si=jrpMxrx5R5SB9qjTByvPJA"
          },
          "transcripts": {},
          "type": "PODCAST_EPISODE",
          "uri": "spotify:episode:2J3m075zqKwZ43mysdezJK",
          "visualIdentity": {
            "sixteenByNineCoverImage": {
              "image": {
                "data": {
                  "__typename": "ImageV2",
                  "sources": [
                    {
                      "maxHeight": 720,
                      "maxWidth": 1280,
                      "url": "https://image-cdn-ak.spotifycdn.com/image/ab6772ab000030ae6836d7fb3ec70a76a4d3d03c"
                    },
                    {
                      "maxHeight": 360,
                      "maxWidth": 640,
                      "url": "https://image-cdn-ak.spotifycdn.com/image/ab6772ab0000e0e76836d7fb3ec70a76a4d3d03c"
                    }
                  ]
                }
              }
            },
            "squareCoverImage": {
              "__typename": "VisualIdentityImage",
              "extractedColorSet": {
                "encoreBaseSetTextColor": {
                  "alpha": 255,
                  "blue": 110,
                  "green": 165,
                  "red": 255
                },
                "highContrast": {
                  "backgroundBase": {
                    "alpha": 255,
                    "blue": 0,
                    "green": 48,
                    "red": 145
                  },
                  "backgroundTintedBase": {
                    "alpha": 255,
                    "blue": 0,
                    "green": 9,
                    "red": 97
                  },
                  "textBase": {
                    "alpha": 255,
                    "blue": 255,
                    "green": 255,
                    "red": 255
                  },
                  "textBrightAccent": {
                    "alpha": 255,
                    "blue": 255,
                    "green": 255,
                    "red": 255
                  },
                  "textSubdued": {
                    "alpha": 255,
                    "blue": 154,
                    "green": 192,
                    "red": 255
                  }
                },
                "higherContrast": {
                  "backgroundBase": {
                    "alpha": 255,
                    "blue": 0,
                    "green": 10,
                    "red": 101
                  },
                  "backgroundTintedBase": {
                    "alpha": 255,
                    "blue": 40,
                    "green": 55,
                    "red": 144
                  },
                  "textBase": {
                    "alpha": 255,
                    "blue": 255,
                    "green": 255,
                    "red": 255
                  },
                  "textBrightAccent": {
                    "alpha": 255,
                    "blue": 96,
                    "green": 215,
                    "red": 30
                  },
                  "textSubdued": {
                    "alpha": 255,
                    "blue": 154,
                    "green": 192,
                    "red": 255
                  }
                },
                "minContrast": {
                  "backgroundBase": {
                    "alpha": 255,
                    "blue": 0,
                    "green": 111,
                    "red": 247
                  },
                  "backgroundTintedBase": {
                    "alpha": 255,
                    "blue": 0,
                    "green": 83,
                    "red": 217
                  },
                  "textBase": {
                    "alpha": 255,
                    "blue": 255,
                    "green": 255,
                    "red": 255
                  },
                  "textBrightAccent": {
                    "alpha": 255,
                    "blue": 255,
                    "green": 255,
                    "red": 255
                  },
                  "textSubdued": {
                    "alpha": 255,
                    "blue": 255,
                    "green": 255,
                    "red": 255
                  }
                }
              }
            }
          }
        }
      },
      {
        "platform": "spotify",
        "type": "episode",
        "uri": "spotify:episode:10TcPJFzFUDyyBzsj72nxi",
        "url": "https://open.spotify.com/episode/10TcPJFzFUDyyBzsj72nxi?si=byEZRMiRS4aX_MSrQ-fxgQ",
        "name": "#2525 - Nick Bostrom",
        "description": "Nick Bostrom is a philosopher whose work focuses on artificial intelligence, existential risk, and the future of humanity. He is Principal Researcher at the Macrostrategy Research Initiative and the author of several books, the most recent of which is “Deep Utopia: Life and Meaning in a Solved World.”www.simonandschuster.com/books/Deep-Utopia/Nick-Bostrom/9781646871643www.nickbostrom.com  Perplexity: Download the app or ask Perplexity anything at https://pplx.ai/rogan.  Switch today at https://Visible.com for just 25/mo. Or Save $10 on your first month of Visible+ Pro with code ROGAN.  Learn more about your ad choices. Visit podcastchoices.com/adchoices",
        "durationMs": 8081918,
        "releaseYear": 2026,
        "image": "https://i.scdn.co/image/ab6765630000f68d010b1c625a39274e7a41e347",
        "raw": {
          "__typename": "Episode",
          "audio": {
            "items": [
              {
                "url": "https://p.scdn.co/mp3-preview/dc9dce35f8172cb8cb36e5249619fa5778eda411"
              },
              {
                "url": "https://p.scdn.co/mp3-preview/c50b2d689e1b270d54af3a4e711b326dfc220c57"
              },
              {
                "url": "https://p.scdn.co/mp3-preview/f231631aa10e95171e60fcd85427cc9e321adb0d"
              },
              {
                "url": "https://p.scdn.co/mp3-preview/39e349e03c2e565bd53e7abab3bb60679df9f897"
              },
              {
                "url": "https://p.scdn.co/mp3-preview/3e6c52bc966b6a826865f11be9be2003ac29e722"
              }
            ]
          },
          "contentRating": {
            "label": "EXPLICIT"
          },
          "coverArt": {
            "sources": [
              {
                "height": 64,
                "url": "https://i.scdn.co/image/ab6765630000f68d010b1c625a39274e7a41e347",
                "width": 64
              },
              {
                "height": 300,
                "url": "https://i.scdn.co/image/ab67656300005f1f010b1c625a39274e7a41e347",
                "width": 300
              },
              {
                "height": 640,
                "url": "https://i.scdn.co/image/ab6765630000ba8a010b1c625a39274e7a41e347",
                "width": 640
              }
            ]
          },
          "description": "Nick Bostrom is a philosopher whose work focuses on artificial intelligence, existential risk, and the future of humanity. He is Principal Researcher at the Macrostrategy Research Initiative and the author of several books, the most recent of which is “Deep Utopia: Life and Meaning in a Solved World.”www.simonandschuster.com/books/Deep-Utopia/Nick-Bostrom/9781646871643www.nickbostrom.com  Perplexity: Download the app or ask Perplexity anything at https://pplx.ai/rogan.  Switch today at https://Visible.com for just 25/mo. Or Save $10 on your first month of Visible+ Pro with code ROGAN.  Learn more about your ad choices. Visit podcastchoices.com/adchoices",
          "duration": {
            "totalMilliseconds": 8081918
          },
          "htmlDescription": "<p>Nick Bostrom is a philosopher whose work focuses on artificial intelligence, existential risk, and the future of humanity. He is Principal Researcher at the Macrostrategy Research Initiative and the author of several books, the most recent of which is “Deep Utopia: Life and Meaning in a Solved World.”<br />www.simonandschuster.com/books/Deep-Utopia/Nick-Bostrom/9781646871643<br />www.nickbostrom.com</p><br/><p><br /></p><br/><p>Perplexity: Download the app or ask Perplexity anything at <a href=\"https://pplx.ai/rogan\" rel=\"nofollow\">https://pplx.ai/rogan</a>.</p><br/><p><br /></p><br/><p>Switch today at <a href=\"https://Visible.com\" rel=\"nofollow\">https://Visible.com</a> for just 25/mo. Or Save $10 on your first month of Visible&#43; Pro with code ROGAN. </p><p> </p><p>Learn more about your ad choices. Visit <a href=\"https://podcastchoices.com/adchoices\" rel=\"nofollow\">podcastchoices.com/adchoices</a></p>",
          "id": "10TcPJFzFUDyyBzsj72nxi",
          "mediaTypes": [
            "AUDIO",
            "VIDEO"
          ],
          "name": "#2525 - Nick Bostrom",
          "playability": {
            "playable": true,
            "reason": "PLAYABLE"
          },
          "playedState": {
            "playPositionMilliseconds": 0,
            "state": "NOT_STARTED"
          },
          "podcastV2": {
            "data": {
              "__typename": "Podcast",
              "coverArt": {
                "sources": [
                  {
                    "height": 64,
                    "url": "https://i.scdn.co/image/ab6765630000f68d1e1acaebe06610165612f1ef",
                    "width": 64
                  },
                  {
                    "height": 300,
                    "url": "https://i.scdn.co/image/ab67656300005f1f1e1acaebe06610165612f1ef",
                    "width": 300
                  },
                  {
                    "height": 640,
                    "url": "https://i.scdn.co/image/ab6765630000ba8a1e1acaebe06610165612f1ef",
                    "width": 640
                  }
                ]
              },
              "name": "The Joe Rogan Experience",
              "showTypes": [
                "SHOW_TYPE_EXCLUSIVE"
              ],
              "uri": "spotify:show:4rOoJ6Egrf8K2IrywzwOMk"
            }
          },
          "previewPlayback": {
            "audioPreview": {
              "cdnUrl": "https://p.scdn.co/mp3-preview/ba46b42f2f38bb09f50e5a8a91877265c577cf44.mp3"
            }
          },
          "releaseDate": {
            "isoString": "2026-07-14T17:00:00Z",
            "precision": "MINUTE"
          },
          "restrictions": {
            "paywallContent": false
          },
          "sharingInfo": {
            "shareId": "byEZRMiRS4aX_MSrQ-fxgQ",
            "shareUrl": "https://open.spotify.com/episode/10TcPJFzFUDyyBzsj72nxi?si=byEZRMiRS4aX_MSrQ-fxgQ"
          },
          "transcripts": {},
          "type": "PODCAST_EPISODE",
          "uri": "spotify:episode:10TcPJFzFUDyyBzsj72nxi",
          "visualIdentity": {
            "sixteenByNineCoverImage": {
              "image": {
                "data": {
                  "__typename": "ImageV2",
                  "sources": [
                    {
                      "maxHeight": 720,
                      "maxWidth": 1280,
                      "url": "https://image-cdn-fa.spotifycdn.com/image/ab6772ab000030ae7648ac2ed841cbe3a7aa6d79"
                    },
                    {
                      "maxHeight": 360,
                      "maxWidth": 640,
                      "url": "https://image-cdn-fa.spotifycdn.com/image/ab6772ab0000e0e77648ac2ed841cbe3a7aa6d79"
                    }
                  ]
                }
              }
            },
            "squareCoverImage": {
              "__typename": "VisualIdentityImage",
              "extractedColorSet": {
                "encoreBaseSetTextColor": {
                  "alpha": 255,
                  "blue": 110,
                  "green": 165,
                  "red": 255
                },
                "highContrast": {
                  "backgroundBase": {
                    "alpha": 255,
                    "blue": 0,
                    "green": 48,
                    "red": 145
                  },
                  "backgroundTintedBase": {
                    "alpha": 255,
                    "blue": 0,
                    "green": 9,
                    "red": 97
                  },
                  "textBase": {
                    "alpha": 255,
                    "blue": 255,
                    "green": 255,
                    "red": 255
                  },
                  "textBrightAccent": {
                    "alpha": 255,
                    "blue": 255,
                    "green": 255,
                    "red": 255
                  },
                  "textSubdued": {
                    "alpha": 255,
                    "blue": 154,
                    "green": 192,
                    "red": 255
                  }
                },
                "higherContrast": {
                  "backgroundBase": {
                    "alpha": 255,
                    "blue": 0,
                    "green": 10,
                    "red": 101
                  },
                  "backgroundTintedBase": {
                    "alpha": 255,
                    "blue": 40,
                    "green": 55,
                    "red": 144
                  },
                  "textBase": {
                    "alpha": 255,
                    "blue": 255,
                    "green": 255,
                    "red": 255
                  },
                  "textBrightAccent": {
                    "alpha": 255,
                    "blue": 96,
                    "green": 215,
                    "red": 30
                  },
                  "textSubdued": {
                    "alpha": 255,
                    "blue": 154,
                    "green": 192,
                    "red": 255
                  }
                },
                "minContrast": {
                  "backgroundBase": {
                    "alpha": 255,
                    "blue": 0,
                    "green": 111,
                    "red": 247
                  },
                  "backgroundTintedBase": {
                    "alpha": 255,
                    "blue": 0,
                    "green": 83,
                    "red": 217
                  },
                  "textBase": {
                    "alpha": 255,
                    "blue": 255,
                    "green": 255,
                    "red": 255
                  },
                  "textBrightAccent": {
                    "alpha": 255,
                    "blue": 255,
                    "green": 255,
                    "red": 255
                  },
                  "textSubdued": {
                    "alpha": 255,
                    "blue": 255,
                    "green": 255,
                    "red": 255
                  }
                }
              }
            }
          }
        }
      },
      {
        "platform": "spotify",
        "type": "episode",
        "uri": "spotify:episode:4imTpV50bg8l1lIccXTqoC",
        "url": "https://open.spotify.com/episode/4imTpV50bg8l1lIccXTqoC?si=-Bi4yBNXRnenXdEttOlHwQ",
        "name": "JRE MMA Show #182 - Protect Ya Neck",
        "description": "Joe is joined by mixed martial artists John Rallo, Matt Serra, and Din Thomas. John Rallo owns Shogun Fights and is the owner and head coach of Ground Control Mixed Martial Arts Academy.www.groundcontrolbaltimore.comwww.shogunfights.com Matt Serra is a mixed martial artist and host of \"UFC Unfiltered\" with Jim Norton and \"Geeking Out with Matt Serra.\" He is the owner and an instructor at Serra BJJ.www.youtube.com/@MattSerraBJJwww.serrabjjacademy.com Din Thomas is a mixed martial arts analyst, actor, and host of \"Din Thomas' Fight Court.\"www.youtube.com/@FightCourt  Perplexity: Download the app or ask Perplexity anything at https://pplx.ai/rogan.  Don’t miss out on all the action this week at DraftKings! Download the DraftKings app today! Sign-up using https://dkng.co/rogan or through my promo code ROGAN.  Get watch party snacks and groceries on Uber Eats. Learn more about your ad choices. Visit podcastchoices.com/adchoices",
        "durationMs": 9543167,
        "releaseYear": 2026,
        "image": "https://i.scdn.co/image/ab6765630000f68dc31c4e7f94756b105c94914c",
        "raw": {
          "__typename": "Episode",
          "audio": {
            "items": [
              {
                "url": "https://p.scdn.co/mp3-preview/cc89c0abf536eb97de41b98330fdde309bce37e5"
              },
              {
                "url": "https://p.scdn.co/mp3-preview/67bd280d3daaec5d2e6970cc0c6e4d0b607beda0"
              },
              {
                "url": "https://p.scdn.co/mp3-preview/6b4756382c5050ad7ffb6177cd030bca47577499"
              },
              {
                "url": "https://p.scdn.co/mp3-preview/57460ace6e3270464976529438184a90dcc4b2d9"
              },
              {
                "url": "https://p.scdn.co/mp3-preview/b28cb79e3c220ef1fe1146c87fa08b117da9b946"
              }
            ]
          },
          "contentRating": {
            "label": "EXPLICIT"
          },
          "coverArt": {
            "sources": [
              {
                "height": 64,
                "url": "https://i.scdn.co/image/ab6765630000f68dc31c4e7f94756b105c94914c",
                "width": 64
              },
              {
                "height": 300,
                "url": "https://i.scdn.co/image/ab67656300005f1fc31c4e7f94756b105c94914c",
                "width": 300
              },
              {
                "height": 640,
                "url": "https://i.scdn.co/image/ab6765630000ba8ac31c4e7f94756b105c94914c",
                "width": 640
              }
            ]
          },
          "description": "Joe is joined by mixed martial artists John Rallo, Matt Serra, and Din Thomas. John Rallo owns Shogun Fights and is the owner and head coach of Ground Control Mixed Martial Arts Academy.www.groundcontrolbaltimore.comwww.shogunfights.com Matt Serra is a mixed martial artist and host of \"UFC Unfiltered\" with Jim Norton and \"Geeking Out with Matt Serra.\" He is the owner and an instructor at Serra BJJ.www.youtube.com/@MattSerraBJJwww.serrabjjacademy.com Din Thomas is a mixed martial arts analyst, actor, and host of \"Din Thomas' Fight Court.\"www.youtube.com/@FightCourt  Perplexity: Download the app or ask Perplexity anything at https://pplx.ai/rogan.  Don’t miss out on all the action this week at DraftKings! Download the DraftKings app today! Sign-up using https://dkng.co/rogan or through my promo code ROGAN.  Get watch party snacks and groceries on Uber Eats. Learn more about your ad choices. Visit podcastchoices.com/adchoices",
          "duration": {
            "totalMilliseconds": 9543167
          },
          "htmlDescription": "<p>Joe is joined by mixed martial artists John Rallo, Matt Serra, and Din Thomas.</p><br/><p>John Rallo owns Shogun Fights and is the owner and head coach of Ground Control Mixed Martial Arts Academy.<br />www.groundcontrolbaltimore.com<br />www.shogunfights.com</p><br/><p>Matt Serra is a mixed martial artist and host of &#34;UFC Unfiltered&#34; with Jim Norton and &#34;Geeking Out with Matt Serra.&#34; He is the owner and an instructor at Serra BJJ.<br />www.youtube.com/&#64;MattSerraBJJ<br />www.serrabjjacademy.com</p><br/><p>Din Thomas is a mixed martial arts analyst, actor, and host of &#34;Din Thomas&#39; Fight Court.&#34;<br />www.youtube.com/&#64;FightCourt</p><br/><p><br /></p><br/><p>Perplexity: Download the app or ask Perplexity anything at <a href=\"https://pplx.ai/rogan\" rel=\"nofollow\">https://pplx.ai/rogan</a>.</p><br/><p><br /></p><br/><p>Don’t miss out on all the action this week at DraftKings! Download the DraftKings app today! Sign-up using <a href=\"https://dkng.co/rogan\" rel=\"nofollow\">https://dkng.co/rogan</a> or through my promo code ROGAN.</p><br/><p><br /></p><br/><p>Get watch party snacks and groceries on Uber Eats.</p><p> </p><p>Learn more about your ad choices. Visit <a href=\"https://podcastchoices.com/adchoices\" rel=\"nofollow\">podcastchoices.com/adchoices</a></p>",
          "id": "4imTpV50bg8l1lIccXTqoC",
          "mediaTypes": [
            "AUDIO",
            "VIDEO"
          ],
          "name": "JRE MMA Show #182 - Protect Ya Neck",
          "playability": {
            "playable": true,
            "reason": "PLAYABLE"
          },
          "playedState": {
            "playPositionMilliseconds": 0,
            "state": "NOT_STARTED"
          },
          "podcastV2": {
            "data": {
              "__typename": "Podcast",
              "coverArt": {
                "sources": [
                  {
                    "height": 64,
                    "url": "https://i.scdn.co/image/ab6765630000f68d1e1acaebe06610165612f1ef",
                    "width": 64
                  },
                  {
                    "height": 300,
                    "url": "https://i.scdn.co/image/ab67656300005f1f1e1acaebe06610165612f1ef",
                    "width": 300
                  },
                  {
                    "height": 640,
                    "url": "https://i.scdn.co/image/ab6765630000ba8a1e1acaebe06610165612f1ef",
                    "width": 640
                  }
                ]
              },
              "name": "The Joe Rogan Experience",
              "showTypes": [
                "SHOW_TYPE_EXCLUSIVE"
              ],
              "uri": "spotify:show:4rOoJ6Egrf8K2IrywzwOMk"
            }
          },
          "previewPlayback": {
            "audioPreview": {
              "cdnUrl": "https://p.scdn.co/mp3-preview/e8a322b467ac820b6646eb3f789b2f9992ff320c.mp3"
            }
          },
          "releaseDate": {
            "isoString": "2026-07-09T17:00:00Z",
            "precision": "MINUTE"
          },
          "restrictions": {
            "paywallContent": false
          },
          "sharingInfo": {
            "shareId": "-Bi4yBNXRnenXdEttOlHwQ",
            "shareUrl": "https://open.spotify.com/episode/4imTpV50bg8l1lIccXTqoC?si=-Bi4yBNXRnenXdEttOlHwQ"
          },
          "transcripts": {},
          "type": "PODCAST_EPISODE",
          "uri": "spotify:episode:4imTpV50bg8l1lIccXTqoC",
          "visualIdentity": {
            "sixteenByNineCoverImage": {
              "image": {
                "data": {
                  "__typename": "ImageV2",
                  "sources": [
                    {
                      "maxHeight": 720,
                      "maxWidth": 1280,
                      "url": "https://image-cdn-fa.spotifycdn.com/image/ab6772ab000030aee781082c1d0b2280f811a5da"
                    },
                    {
                      "maxHeight": 360,
                      "maxWidth": 640,
                      "url": "https://image-cdn-fa.spotifycdn.com/image/ab6772ab0000e0e7e781082c1d0b2280f811a5da"
                    }
                  ]
                }
              }
            },
            "squareCoverImage": {
              "__typename": "VisualIdentityImage",
              "extractedColorSet": {
                "encoreBaseSetTextColor": {
                  "alpha": 255,
                  "blue": 110,
                  "green": 165,
                  "red": 255
                },
                "highContrast": {
                  "backgroundBase": {
                    "alpha": 255,
                    "blue": 0,
                    "green": 48,
                    "red": 145
                  },
                  "backgroundTintedBase": {
                    "alpha": 255,
                    "blue": 0,
                    "green": 9,
                    "red": 97
                  },
                  "textBase": {
                    "alpha": 255,
                    "blue": 255,
                    "green": 255,
                    "red": 255
                  },
                  "textBrightAccent": {
                    "alpha": 255,
                    "blue": 255,
                    "green": 255,
                    "red": 255
                  },
                  "textSubdued": {
                    "alpha": 255,
                    "blue": 154,
                    "green": 192,
                    "red": 255
                  }
                },
                "higherContrast": {
                  "backgroundBase": {
                    "alpha": 255,
                    "blue": 0,
                    "green": 10,
                    "red": 101
                  },
                  "backgroundTintedBase": {
                    "alpha": 255,
                    "blue": 40,
                    "green": 55,
                    "red": 144
                  },
                  "textBase": {
                    "alpha": 255,
                    "blue": 255,
                    "green": 255,
                    "red": 255
                  },
                  "textBrightAccent": {
                    "alpha": 255,
                    "blue": 96,
                    "green": 215,
                    "red": 30
                  },
                  "textSubdued": {
                    "alpha": 255,
                    "blue": 154,
                    "green": 192,
                    "red": 255
                  }
                },
                "minContrast": {
                  "backgroundBase": {
                    "alpha": 255,
                    "blue": 0,
                    "green": 111,
                    "red": 247
                  },
                  "backgroundTintedBase": {
                    "alpha": 255,
                    "blue": 0,
                    "green": 83,
                    "red": 217
                  },
                  "textBase": {
                    "alpha": 255,
                    "blue": 255,
                    "green": 255,
                    "red": 255
                  },
                  "textBrightAccent": {
                    "alpha": 255,
                    "blue": 255,
                    "green": 255,
                    "red": 255
                  },
                  "textSubdued": {
                    "alpha": 255,
                    "blue": 255,
                    "green": 255,
                    "red": 255
                  }
                }
              }
            }
          }
        }
      },
      {
        "platform": "spotify",
        "type": "episode",
        "uri": "spotify:episode:1f6tXaeR1XNYwSF0tqpEDT",
        "url": "https://open.spotify.com/episode/1f6tXaeR1XNYwSF0tqpEDT?si=Co0hsETLQr2JxhnuJeQp-g",
        "name": "#2524 - Rupert Lowe",
        "description": "Rupert Lowe is a British politician who has served as the member of Parliament for Great Yarmouth since 2024 and the leader of Restore Britain.  Perplexity: Download the app or ask Perplexity anything at https://pplx.ai/rogan.  onX Offroad: Try onX Offroad for 50% off- go to https://onXmaps.com/joerogan  This video is sponsored by BetterHelp. Visit https://BetterHelp.com/JRE Learn more about your ad choices. Visit podcastchoices.com/adchoices",
        "durationMs": 7385641,
        "releaseYear": 2026,
        "image": "https://i.scdn.co/image/ab6765630000f68d0531ec0d584e51f31ca132ed",
        "raw": {
          "__typename": "Episode",
          "audio": {
            "items": [
              {
                "url": "https://p.scdn.co/mp3-preview/79d00facffbf57d9bad25910812d7af541131a63"
              },
              {
                "url": "https://p.scdn.co/mp3-preview/b348d674403423ddbaa7619f7868fe24ba01b695"
              },
              {
                "url": "https://p.scdn.co/mp3-preview/0f50bcd22706355dad3d825b2d3dd3ea635169b5"
              },
              {
                "url": "https://p.scdn.co/mp3-preview/ecfad3e5334c0c3c516eeca1d8bd1d4f1e04a41e"
              },
              {
                "url": "https://p.scdn.co/mp3-preview/ef72da5afac7d1e978bf98033d7d3d42e7c25c10"
              }
            ]
          },
          "contentRating": {
            "label": "EXPLICIT"
          },
          "coverArt": {
            "sources": [
              {
                "height": 64,
                "url": "https://i.scdn.co/image/ab6765630000f68d0531ec0d584e51f31ca132ed",
                "width": 64
              },
              {
                "height": 300,
                "url": "https://i.scdn.co/image/ab67656300005f1f0531ec0d584e51f31ca132ed",
                "width": 300
              },
              {
                "height": 640,
                "url": "https://i.scdn.co/image/ab6765630000ba8a0531ec0d584e51f31ca132ed",
                "width": 640
              }
            ]
          },
          "description": "Rupert Lowe is a British politician who has served as the member of Parliament for Great Yarmouth since 2024 and the leader of Restore Britain.  Perplexity: Download the app or ask Perplexity anything at https://pplx.ai/rogan.  onX Offroad: Try onX Offroad for 50% off- go to https://onXmaps.com/joerogan  This video is sponsored by BetterHelp. Visit https://BetterHelp.com/JRE Learn more about your ad choices. Visit podcastchoices.com/adchoices",
          "duration": {
            "totalMilliseconds": 7385641
          },
          "htmlDescription": "<p>Rupert Lowe is a British politician who has served as the member of Parliament for Great Yarmouth since 2024 and the leader of Restore Britain.</p><br/><p><br /></p><br/><p>Perplexity: Download the app or ask Perplexity anything at <a href=\"https://pplx.ai/rogan\" rel=\"nofollow\">https://pplx.ai/rogan</a>.</p><br/><p><br /></p><br/><p>onX Offroad: Try onX Offroad for 50% off- go to <a href=\"https://onXmaps.com/joerogan\" rel=\"nofollow\">https://onXmaps.com/joerogan</a></p><br/><p><br /></p><br/><p>This video is sponsored by BetterHelp. Visit <a href=\"https://BetterHelp.com/JRE\" rel=\"nofollow\">https://BetterHelp.com/JRE</a></p><p> </p><p>Learn more about your ad choices. Visit <a href=\"https://podcastchoices.com/adchoices\" rel=\"nofollow\">podcastchoices.com/adchoices</a></p>",
          "id": "1f6tXaeR1XNYwSF0tqpEDT",
          "mediaTypes": [
            "AUDIO",
            "VIDEO"
          ],
          "name": "#2524 - Rupert Lowe",
          "playability": {
            "playable": true,
            "reason": "PLAYABLE"
          },
          "playedState": {
            "playPositionMilliseconds": 0,
            "state": "NOT_STARTED"
          },
          "podcastV2": {
            "data": {
              "__typename": "Podcast",
              "coverArt": {
                "sources": [
                  {
                    "height": 64,
                    "url": "https://i.scdn.co/image/ab6765630000f68d1e1acaebe06610165612f1ef",
                    "width": 64
                  },
                  {
                    "height": 300,
                    "url": "https://i.scdn.co/image/ab67656300005f1f1e1acaebe06610165612f1ef",
                    "width": 300
                  },
                  {
                    "height": 640,
                    "url": "https://i.scdn.co/image/ab6765630000ba8a1e1acaebe06610165612f1ef",
                    "width": 640
                  }
                ]
              },
              "name": "The Joe Rogan Experience",
              "showTypes": [
                "SHOW_TYPE_EXCLUSIVE"
              ],
              "uri": "spotify:show:4rOoJ6Egrf8K2IrywzwOMk"
            }
          },
          "previewPlayback": {
            "audioPreview": {
              "cdnUrl": "https://p.scdn.co/mp3-preview/d9a20bdf0277625f2a094ad311845d3fb61d13d9.mp3"
            }
          },
          "releaseDate": {
            "isoString": "2026-07-08T17:00:00Z",
            "precision": "MINUTE"
          },
          "restrictions": {
            "paywallContent": false
          },
          "sharingInfo": {
            "shareId": "Co0hsETLQr2JxhnuJeQp-g",
            "shareUrl": "https://open.spotify.com/episode/1f6tXaeR1XNYwSF0tqpEDT?si=Co0hsETLQr2JxhnuJeQp-g"
          },
          "transcripts": {},
          "type": "PODCAST_EPISODE",
          "uri": "spotify:episode:1f6tXaeR1XNYwSF0tqpEDT",
          "visualIdentity": {
            "sixteenByNineCoverImage": {
              "image": {
                "data": {
                  "__typename": "ImageV2",
                  "sources": [
                    {
                      "maxHeight": 720,
                      "maxWidth": 1280,
                      "url": "https://image-cdn-fa.spotifycdn.com/image/ab6772ab000030ae90386d50241a150d4bcbc8e9"
                    },
                    {
                      "maxHeight": 360,
                      "maxWidth": 640,
                      "url": "https://image-cdn-fa.spotifycdn.com/image/ab6772ab0000e0e790386d50241a150d4bcbc8e9"
                    }
                  ]
                }
              }
            },
            "squareCoverImage": {
              "__typename": "VisualIdentityImage",
              "extractedColorSet": {
                "encoreBaseSetTextColor": {
                  "alpha": 255,
                  "blue": 110,
                  "green": 165,
                  "red": 255
                },
                "highContrast": {
                  "backgroundBase": {
                    "alpha": 255,
                    "blue": 0,
                    "green": 48,
                    "red": 145
                  },
                  "backgroundTintedBase": {
                    "alpha": 255,
                    "blue": 0,
                    "green": 9,
                    "red": 97
                  },
                  "textBase": {
                    "alpha": 255,
                    "blue": 255,
                    "green": 255,
                    "red": 255
                  },
                  "textBrightAccent": {
                    "alpha": 255,
                    "blue": 255,
                    "green": 255,
                    "red": 255
                  },
                  "textSubdued": {
                    "alpha": 255,
                    "blue": 154,
                    "green": 192,
                    "red": 255
                  }
                },
                "higherContrast": {
                  "backgroundBase": {
                    "alpha": 255,
                    "blue": 0,
                    "green": 10,
                    "red": 101
                  },
                  "backgroundTintedBase": {
                    "alpha": 255,
                    "blue": 40,
                    "green": 55,
                    "red": 144
                  },
                  "textBase": {
                    "alpha": 255,
                    "blue": 255,
                    "green": 255,
                    "red": 255
                  },
                  "textBrightAccent": {
                    "alpha": 255,
                    "blue": 96,
                    "green": 215,
                    "red": 30
                  },
                  "textSubdued": {
                    "alpha": 255,
                    "blue": 154,
                    "green": 192,
                    "red": 255
                  }
                },
                "minContrast": {
                  "backgroundBase": {
                    "alpha": 255,
                    "blue": 0,
                    "green": 111,
                    "red": 247
                  },
                  "backgroundTintedBase": {
                    "alpha": 255,
                    "blue": 0,
                    "green": 83,
                    "red": 217
                  },
                  "textBase": {
                    "alpha": 255,
                    "blue": 255,
                    "green": 255,
                    "red": 255
                  },
                  "textBrightAccent": {
                    "alpha": 255,
                    "blue": 255,
                    "green": 255,
                    "red": 255
                  },
                  "textSubdued": {
                    "alpha": 255,
                    "blue": 255,
                    "green": 255,
                    "red": 255
                  }
                }
              }
            }
          }
        }
      }
    ]
  },
  "spotify-search": {
    "platform": "spotify",
    "query": "lofi beats",
    "type": "tracks",
    "totalReturned": 5,
    "results": [
      {
        "platform": "spotify",
        "type": "track",
        "uri": "1S7FNazOUQc21EaQyh5nJT",
        "url": "https://open.spotify.com/track/1S7FNazOUQc21EaQyh5nJT",
        "name": "Nightmote - Lofi Remix",
        "artists": [
          "Yoylecake Michael",
          "111robloxdude"
        ],
        "album": "Nightmote (Lofi Remix)",
        "durationMs": 207620,
        "image": "https://i.scdn.co/image/ab67616d0000b2735d372fc451453e8b83900014",
        "raw": {
          "type": "track",
          "id": "1S7FNazOUQc21EaQyh5nJT",
          "name": "Nightmote - Lofi Remix",
          "artists": "Yoylecake Michael, 111robloxdude",
          "albumName": "Nightmote (Lofi Remix)",
          "albumArt": "https://i.scdn.co/image/ab67616d0000b2735d372fc451453e8b83900014",
          "duration": 207620,
          "durationFormatted": "3:27",
          "isExplicit": false,
          "isPlayable": true,
          "url": "https://open.spotify.com/track/1S7FNazOUQc21EaQyh5nJT",
          "scrapedAt": "2026-07-18T11:28:01.801Z",
          "searchTerm": "lofi beats"
        }
      },
      {
        "platform": "spotify",
        "type": "track",
        "uri": "6AOXQYGPpd7KIIBxCCZzUx",
        "url": "https://open.spotify.com/track/6AOXQYGPpd7KIIBxCCZzUx",
        "name": "Lofi Beats",
        "artists": [
          "Lofi Sleep Chill & Study"
        ],
        "album": "Wave Heart: Chill Lofi Music",
        "durationMs": 120000,
        "image": "https://i.scdn.co/image/ab67616d0000b27391027e42977d144b3db3f705",
        "raw": {
          "type": "track",
          "id": "6AOXQYGPpd7KIIBxCCZzUx",
          "name": "Lofi Beats",
          "artists": "Lofi Sleep Chill & Study",
          "albumName": "Wave Heart: Chill Lofi Music",
          "albumArt": "https://i.scdn.co/image/ab67616d0000b27391027e42977d144b3db3f705",
          "duration": 120000,
          "durationFormatted": "2:00",
          "isExplicit": false,
          "isPlayable": true,
          "url": "https://open.spotify.com/track/6AOXQYGPpd7KIIBxCCZzUx",
          "scrapedAt": "2026-07-18T11:28:01.901Z",
          "searchTerm": "lofi beats"
        }
      },
      {
        "platform": "spotify",
        "type": "track",
        "uri": "5yw15MbdXGw2ngbqmd7E3m",
        "url": "https://open.spotify.com/track/5yw15MbdXGw2ngbqmd7E3m",
        "name": "Lofi Beats",
        "artists": [
          "Lo Fi Hip Hop"
        ],
        "album": "Lofi Dreams: Soft Lofi Beats",
        "durationMs": 120000,
        "image": "https://i.scdn.co/image/ab67616d0000b2730cea6601096d5b32c8b28f71",
        "raw": {
          "type": "track",
          "id": "5yw15MbdXGw2ngbqmd7E3m",
          "name": "Lofi Beats",
          "artists": "Lo Fi Hip Hop",
          "albumName": "Lofi Dreams: Soft Lofi Beats",
          "albumArt": "https://i.scdn.co/image/ab67616d0000b2730cea6601096d5b32c8b28f71",
          "duration": 120000,
          "durationFormatted": "2:00",
          "isExplicit": false,
          "isPlayable": true,
          "url": "https://open.spotify.com/track/5yw15MbdXGw2ngbqmd7E3m",
          "scrapedAt": "2026-07-18T11:28:01.961Z",
          "searchTerm": "lofi beats"
        }
      },
      {
        "platform": "spotify",
        "type": "track",
        "uri": "7zGzS7L6LnI5qQqMm8wTPB",
        "url": "https://open.spotify.com/track/7zGzS7L6LnI5qQqMm8wTPB",
        "name": "New Look - Wii U Mii Maker Lofi Mix",
        "artists": [
          "Secret Potion",
          "Lofi Beats To Chill Study Sleep",
          "Nostalgiacore"
        ],
        "album": "Frutiger Aero Remixes",
        "durationMs": 162897,
        "image": "https://i.scdn.co/image/ab67616d0000b27365bc1eef471caed82cd5c3d9",
        "raw": {
          "type": "track",
          "id": "7zGzS7L6LnI5qQqMm8wTPB",
          "name": "New Look - Wii U Mii Maker Lofi Mix",
          "artists": "Secret Potion, Lofi Beats To Chill Study Sleep, Nostalgiacore",
          "albumName": "Frutiger Aero Remixes",
          "albumArt": "https://i.scdn.co/image/ab67616d0000b27365bc1eef471caed82cd5c3d9",
          "duration": 162897,
          "durationFormatted": "2:42",
          "isExplicit": false,
          "isPlayable": true,
          "url": "https://open.spotify.com/track/7zGzS7L6LnI5qQqMm8wTPB",
          "scrapedAt": "2026-07-18T11:28:02.011Z",
          "searchTerm": "lofi beats"
        }
      },
      {
        "platform": "spotify",
        "type": "track",
        "uri": "4LQ0TjIFk38xXNJVNoonSW",
        "url": "https://open.spotify.com/track/4LQ0TjIFk38xXNJVNoonSW",
        "name": "slow river",
        "artists": [
          "ourchase"
        ],
        "album": "slow river",
        "durationMs": 103317,
        "image": "https://i.scdn.co/image/ab67616d0000b273396a89f358a81646ed6259b8",
        "raw": {
          "type": "track",
          "id": "4LQ0TjIFk38xXNJVNoonSW",
          "name": "slow river",
          "artists": "ourchase",
          "albumName": "slow river",
          "albumArt": "https://i.scdn.co/image/ab67616d0000b273396a89f358a81646ed6259b8",
          "duration": 103317,
          "durationFormatted": "1:43",
          "isExplicit": false,
          "isPlayable": true,
          "url": "https://open.spotify.com/track/4LQ0TjIFk38xXNJVNoonSW",
          "scrapedAt": "2026-07-18T11:28:02.289Z",
          "searchTerm": "lofi beats"
        }
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
      "Taylor Swift"
    ],
    "album": "Midnights",
    "durationMs": 200690,
    "image": "https://i.scdn.co/image/ab67616d00001e02bb54dde68cd23e2a268ae0f5",
    "raw": {
      "__typename": "Track",
      "uri": "spotify:track:0V3wPSX9ygBnCm8psDIegu",
      "name": "Anti-Hero",
      "duration": {
        "totalMilliseconds": 200690
      },
      "albumOfTrack": {
        "coverArt": {
          "sources": [
            {
              "height": 300,
              "url": "https://i.scdn.co/image/ab67616d00001e02bb54dde68cd23e2a268ae0f5",
              "width": 300
            },
            {
              "height": 64,
              "url": "https://i.scdn.co/image/ab67616d00004851bb54dde68cd23e2a268ae0f5",
              "width": 64
            },
            {
              "height": 640,
              "url": "https://i.scdn.co/image/ab67616d0000b273bb54dde68cd23e2a268ae0f5",
              "width": 640
            }
          ]
        },
        "name": "Midnights",
        "uri": "spotify:album:151w1FgRZfnKZA9FEcg9Z3"
      },
      "artists": {
        "items": [
          {
            "profile": {
              "name": "Taylor Swift"
            },
            "uri": "spotify:artist:06HL4z0CvFAxyc27GXpf02"
          }
        ]
      }
    }
  },
  "threads-post-details": {
    "platform": "threads",
    "id": "3925863854786722836",
    "code": "DZ7eGA1G7wU",
    "url": "https://www.threads.net/@zuck/post/DZ7eGA1G7wU",
    "text": "Our new line of @metaglasses is available today. Three shapes, 26 style combos, with our most advanced Meta AI built in. Plus, three custom styles designed by @kyliejenner.",
    "publishedAt": "2026-06-23T12:57:42.000Z",
    "author": {
      "username": "zuck",
      "displayName": "Mark Zuckerberg",
      "verified": true,
      "profileImage": "https://scontent-iad6-1.cdninstagram.com/v/t51.82787-19/550174606_17925811725103224_8363667901743352243_n.jpg?stp=dst-jpg_s150x150_tt6&efg=eyJ2ZW5jb2RlX3RhZyI6InByb2ZpbGVfcGljLmRqYW5nby4xMDgwLmMyIn0&_nc_ht=scontent-iad6-1.cdninstagram.com&_nc_cat=100&_nc_oc=Q6cZ2gGRvRGRlBJzSaDiIHvy96S-H7IXH2wFzXSpG21h5j2h0Naq9IW3HS8dzgEC2DJZVZk&_nc_ohc=vLH8jAZMCqoQ7kNvwGzk09c&_nc_gid=SKYrfm-D56HlSCQ63fyNqg&edm=APs17CUBAAAA&ccb=7-5&oh=00_AQC2Ehx5DCkim-2Ypr-U5Cpo18JJL1Cg378dtzsIxna3SQ&oe=6A6E2ABE&_nc_sid=10d13b"
    },
    "engagement": {
      "likes": 3620,
      "replies": 1403,
      "reposts": 237,
      "quotes": 117
    },
    "media": [
      "https://scontent-iad3-2.cdninstagram.com/v/t51.71878-15/729466804_1549760159886177_1883659439515397370_n.jpg?stp=dst-jpg_e15_tt6&_nc_cat=105&ig_cache_key=MzkyNTg1NzYxNDQ3NTQyMzA5NQ%3D%3D.3-ccb7-5&ccb=7-5&_nc_sid=58cdad&efg=eyJ2ZW5jb2RlX3RhZyI6IkNBUk9VU0VMX0lURU0ueHBpZHMuNjQwLnNkci52aWRlb19kZWZhdWx0X2NvdmVyX2ZyYW1lLkMzIn0%3D&_nc_ohc=stcmUcGgS9kQ7kNvwE2_SBs&_nc_oc=Adr6V5qDP4eW5RXqD5GFL13d3gwBJeSM0416O70OlzPNG6x72NO4f9DGAq1cmNY2Tfk&_nc_ad=z-m&_nc_cid=0&_nc_zt=23&_nc_ht=scontent-iad3-2.cdninstagram.com&_nc_gid=SKYrfm-D56HlSCQ63fyNqg&_nc_ss=7a22e&oh=00_AQCrin3Lx7BW1fworyktsrvpPjkzSxnefooIqQaiXIvshQ&oe=6A6E4876",
      "https://scontent-iad6-1.cdninstagram.com/o1/v/t16/f2/m84/AQOTRrCQTl1fyJz7fqBninvUdgWeil7BncTOhD-RfiP256I4PY_ioi8UAxdGl0WLEByzkS3XiObR8E2yNiSbmnE634ktoS1hPNebBYI.mp4?_nc_cat=107&_nc_sid=5e9851&_nc_ht=scontent-iad6-1.cdninstagram.com&_nc_ohc=CYAcI0UX3ncQ7kNvwEzQCPv&efg=eyJ2ZW5jb2RlX3RhZyI6Inhwdl9wcm9ncmVzc2l2ZS5JTlNUQUdSQU0uQ0FST1VTRUxfSVRFTS5DMy43MjAuZGFzaF9iYXNlbGluZV8xX3YxIiwieHB2X2Fzc2V0X2lkIjoxNzk2ODE3MTU3ODA4OTg4OCwiYXNzZXRfYWdlX2RheXMiOjMzLCJ2aV91c2VjYXNlX2lkIjoxMDE2NCwiZHVyYXRpb25fcyI6MjQsInVybGdlbl9zb3VyY2UiOiJ3d3cifQ%3D%3D&ccb=17-1&vs=cefa3ff17e61a968&_nc_vs=HBksFQIYTGlnX2JhY2tmaWxsX3RpbWVsaW5lX3ZvZC81NDQyODFEMkZCRDg0MzU4MzZBQUE0QzI5MzE4MzlBRF92aWRlb19kYXNoaW5pdC5tcDQVAALIARIAFQIYUWlnX3hwdl9wbGFjZW1lbnRfcGVybWFuZW50X3YyLzYwNEVGNDk2M0EwQzdFNTY4QTIyNDRDRkI4MDZBMkIwX2F1ZGlvX2Rhc2hpbml0Lm1wNBUCAsgBEgAoABgAGwKIB3VzZV9vaWwBMRJwcm9ncmVzc2l2ZV9yZWNpcGUBMRUAACbAhufCnv3qPxUCKAJDMywXQDgF41P3ztkYEmRhc2hfYmFzZWxpbmVfMV92MREAde4HZeieAQA&_nc_gid=SKYrfm-D56HlSCQ63fyNqg&_nc_zt=28&_nc_ss=7a22e&oh=00_AQCM2jLds0l7xzFxMerH9RPcZIf6qElGCgvI5V1DJS_ekg&oe=6A6A37B5",
      "https://scontent-iad3-2.cdninstagram.com/v/t51.82787-15/728809712_17974875099103224_2528686373104860184_n.webp?_nc_cat=103&ig_cache_key=MzkyNTg1NzU3NTcwNjYwODc2NQ%3D%3D.3-ccb7-5&ccb=7-5&_nc_sid=58cdad&efg=eyJ2ZW5jb2RlX3RhZyI6IkNBUk9VU0VMX0lURU0ueHBpZHMuMTA4MC5zZHIucmVndWxhcl9waG90by5DMyJ9&_nc_ohc=wgnGXUO07qoQ7kNvwFM_jto&_nc_oc=AdrxVBIXp0YmbH6aYcplbYztDeHesnqMNbGHQQdWmHeS1y7LKIltn5xPwHJCjxCyb38&_nc_ad=z-m&_nc_cid=0&_nc_zt=23&_nc_ht=scontent-iad3-2.cdninstagram.com&_nc_gid=SKYrfm-D56HlSCQ63fyNqg&_nc_ss=7a22e&oh=00_AQDnoCp2GOZD_qhZc4iins8M5f8WO-fA4H2nkIVk1Ii7Uw&oe=6A6E1950",
      "https://scontent-iad6-1.cdninstagram.com/v/t51.71878-15/727566051_958314003924963_5283054625475303262_n.jpg?stp=dst-jpg_e15_tt6&_nc_cat=102&ig_cache_key=MzkyNTg1NzkxNjQyMzMxMzMwMA%3D%3D.3-ccb7-5&ccb=7-5&_nc_sid=58cdad&efg=eyJ2ZW5jb2RlX3RhZyI6IkNBUk9VU0VMX0lURU0ueHBpZHMuNjQwLnNkci52aWRlb19kZWZhdWx0X2NvdmVyX2ZyYW1lLkMzIn0%3D&_nc_ohc=cjpOMQKC2RcQ7kNvwFqnfBA&_nc_oc=AdrtwIel1SSUzrnCttz96Tp3mS0HW8ZVGquCBE_Ymx38XsNAzWbH4yk0rdeXdVTa6Tw&_nc_ad=z-m&_nc_cid=0&_nc_zt=23&_nc_ht=scontent-iad6-1.cdninstagram.com&_nc_gid=SKYrfm-D56HlSCQ63fyNqg&_nc_ss=7a22e&oh=00_AQDcYso9P08PwHT3zbdk7Xj6Uc-IX699-JBCbBySGU0cNg&oe=6A6E460D",
      "https://scontent-iad3-1.cdninstagram.com/o1/v/t16/f2/m84/AQMq6Zzrg22F9r5ID02lab-TQjcYUfKnqpC2_w06THGl8MZ-tKE8-YxokKyN1Yjw_Nwgwpv-xkP4ApHqJoOKrA3b9z01kZ1S4Kgf9ts.mp4?_nc_cat=101&_nc_sid=5e9851&_nc_ht=scontent-iad3-1.cdninstagram.com&_nc_ohc=dXo8gsZ3y98Q7kNvwGb-m2V&efg=eyJ2ZW5jb2RlX3RhZyI6Inhwdl9wcm9ncmVzc2l2ZS5JTlNUQUdSQU0uQ0FST1VTRUxfSVRFTS5DMy43MjAuZGFzaF9iYXNlbGluZV8xX3YxIiwieHB2X2Fzc2V0X2lkIjoxNzk3NDg3NTE5ODEwMzIyNCwiYXNzZXRfYWdlX2RheXMiOjM0LCJ2aV91c2VjYXNlX2lkIjoxMDE2NCwiZHVyYXRpb25fcyI6MjgsInVybGdlbl9zb3VyY2UiOiJ3d3cifQ%3D%3D&ccb=17-1&vs=727caf249a0595d&_nc_vs=HBksFQIYTGlnX2JhY2tmaWxsX3RpbWVsaW5lX3ZvZC8zMTQ2RkM2Q0JBNkVFMzhBMDIwQzk0MkZEQzRGMEE4NV92aWRlb19kYXNoaW5pdC5tcDQVAALIARIAFQIYUWlnX3hwdl9wbGFjZW1lbnRfcGVybWFuZW50X3YyLzQzNEQwMTM2OTM3NzEyNTk0MkEwNDFERTgyODAyNzg0X2F1ZGlvX2Rhc2hpbml0Lm1wNBUCAsgBEgAoABgAGwKIB3VzZV9vaWwBMRJwcm9ncmVzc2l2ZV9yZWNpcGUBMRUAACbw-oSxuIPuPxUCKAJDMywXQDwPnbItDlYYEmRhc2hfYmFzZWxpbmVfMV92MREAde4HZeieAQA&_nc_gid=SKYrfm-D56HlSCQ63fyNqg&_nc_ss=7a22e&_nc_zt=28&oh=00_AQCHiuPM-XsixzgMMMl1zdLIyWuBmMZFQahpOuLsDme8-w&oe=6A6A43B3",
      "https://scontent-iad3-2.cdninstagram.com/v/t51.71878-15/729466804_1549760159886177_1883659439515397370_n.jpg?stp=c0.80.640.640a_dst-jpg_e15_s640x640_tt6&_nc_cat=105&ig_cache_key=MzkyNTg1NzYxNDQ3NTQyMzA5NQ%3D%3D.3-ccb7-5&ccb=7-5&_nc_sid=58cdad&efg=eyJ2ZW5jb2RlX3RhZyI6IkNBUk9VU0VMX0lURU0ueHBpZHMuNjQwLnNkci52aWRlb19kZWZhdWx0X2NvdmVyX2ZyYW1lLkMzIn0%3D&_nc_ohc=stcmUcGgS9kQ7kNvwE2_SBs&_nc_oc=Adr6V5qDP4eW5RXqD5GFL13d3gwBJeSM0416O70OlzPNG6x72NO4f9DGAq1cmNY2Tfk&_nc_ad=z-m&_nc_cid=0&_nc_zt=23&_nc_ht=scontent-iad3-2.cdninstagram.com&_nc_gid=SKYrfm-D56HlSCQ63fyNqg&_nc_ss=7a22e&oh=00_AQDSeO9Kx3ytZVzlTkIMSFZLxnEbsSOcGJR0Wy7FHdzLsw&oe=6A6E4876"
    ]
  },
  "threads-profile": {
    "platform": "threads",
    "username": "zuck",
    "url": "https://www.threads.net/@zuck",
    "id": "63055343223",
    "name": "Mark Zuckerberg",
    "bio": "Mostly superintelligence and MMA takes",
    "verified": true,
    "followers": 5691292,
    "profileImage": "https://scontent-lax3-2.cdninstagram.com/v/t51.82787-19/550174606_17925811725103224_8363667901743352243_n.jpg?stp=dst-jpg_s640x640_tt6&efg=eyJ2ZW5jb2RlX3RhZyI6InByb2ZpbGVfcGljLmRqYW5nby4xMDgwLmMyIn0&_nc_ht=scontent-lax3-2.cdninstagram.com&_nc_cat=100&_nc_oc=Q6cZ2gEeXugh5SzVlR3-SM7yE5Ymx4mleUIUQVrFLOJAyo4Pai-q3Q4Babsn5npHNxps9Zg&_nc_ohc=2ejw17SwZhoQ7kNvwFX521e&_nc_gid=dmOcoQ5owB8qGvpTG7PZZA&edm=APs17CUBAAAA&ccb=7-5&oh=00_AQGktZYLExtnyRLt29v5FtvhGpx_oXGGlsI4Dt45cx4yWA&oe=6A74FA7E&_nc_sid=10d13b",
    "isThreadsOnlyUser": null,
    "isPrivate": false,
    "bioLinks": [],
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
        "id": "3928882651670873164",
        "code": "DaGMfShCYRM",
        "url": "https://www.threads.net/@aiwithanju/post/DaGMfShCYRM",
        "text": "All Paid Courses (Free for First 4500 People)\n\n𝗣𝗮𝗶𝗱 𝗖𝗼𝘂𝗿𝘀𝗲 𝗙𝗥𝗘𝗘 (PART - 1)\n1. Artificial Intelligence\n2. Machine Learning\n3. Prompt Engineering\n4. Claude,Chatgpt,Grok\n5. Data Analytics\n6. AWS Certified\n7. Data Science\n8. BIG DATA\n9. Python\n10. Ethical Hacking\n\n(72 Hours only )\n\nLike + RT + comment 'Drive'\n\nMust Follow me so I can DM you.",
        "publishedAt": "2026-06-27T16:55:31.000Z",
        "author": {
          "username": "aiwithanju",
          "displayName": "Anjana | AI Strategist & Coach",
          "verified": true
        },
        "engagement": {
          "likes": 591,
          "replies": 668,
          "reposts": 187,
          "quotes": 4
        },
        "media": [
          "https://scontent-iad3-1.cdninstagram.com/v/t51.82787-15/728627202_17977076481105005_209164695399005645_n.jpg?stp=c0.200.799.799a_dst-jpg_e35_s799x799_tt6&_nc_cat=108&ig_cache_key=MzkyODg4MjY1MTY3MDg3MzE2NA%3D%3D.3-ccb7-5&ccb=7-5&_nc_sid=58cdad&efg=eyJ2ZW5jb2RlX3RhZyI6IkZFRUQueHBpZHMuNzk5LnNkci5yZWd1bGFyX3Bob3RvLkMzIn0%3D&_nc_ohc=UMllvfQx1EkQ7kNvwFF9ds9&_nc_oc=AdqXPX71ockRBl2OVRF5O6A7XUeFx-wy4HykpHzxP2mPrFg1NyTsC4-K4HpbZ7gB07g&_nc_ad=z-m&_nc_cid=0&_nc_zt=23&_nc_ht=scontent-iad3-1.cdninstagram.com&_nc_gid=uxr3e_varhREv8ajgQ0rKQ&_nc_ss=7a22e&oh=00_AQDcDCZ_P25J_UxIJSHQ3BAKX2ikLzNcr-Sl_tCl_rPuhg&oe=6A6E18CF"
        ]
      },
      {
        "platform": "threads",
        "id": "3945514045746596834",
        "code": "DbBSB7RCkvi",
        "url": "https://www.threads.net/@withclaudeprompts/post/DbBSB7RCkvi",
        "text": "All Paid Courses (Free for First 4500 People)\n𝗣𝗮𝗶𝗱 𝗖𝗼𝘂𝗿𝘀𝗲 𝗙𝗥𝗘𝗘 (PART - 3)\n1. Artificial Intelligence\n2. Machine Learning\n3. Cloud Computing\n4. Ethical Hacking\n5. Data Analytics\n6. AWS Certified\n7. Data Science\n8. BIG DATA\n9. Python\n10. MBA\n(72 Hours only )\n\nTo get-\n1. Follow me\n@withclaudeprompts \n[MUST]\n2. Like & Retweet to get DM\n3. Reply \" All \"",
        "publishedAt": "2026-07-20T15:39:08.000Z",
        "author": {
          "username": "withclaudeprompts",
          "displayName": "With claude prompts",
          "verified": null
        },
        "engagement": {
          "likes": 222,
          "replies": 366,
          "reposts": 90,
          "quotes": 3
        },
        "media": [
          "https://scontent-iad3-2.cdninstagram.com/v/t51.82787-15/751181197_17932649175349487_5570522177976349227_n.jpg?stp=cp6_dst-jpg_e35_tt6&_nc_cat=103&ig_cache_key=Mzk0NTUxMzg2MDI0MzA5NDA2MA%3D%3D.3-ccb7-5&ccb=7-5&_nc_sid=58cdad&efg=eyJ2ZW5jb2RlX3RhZyI6IkNBUk9VU0VMX0lURU0ueHBpZHMuMTE3OS5zZHIucmVndWxhcl9waG90by5DMyJ9&_nc_ohc=JSwVzU_H3Q4Q7kNvwFxQo2_&_nc_oc=AdoFCfxIagstWXjF22IdoGQbWFw8UrQPTGqgDRxhw925PVjkv9PoKk5NWH20Uz_dmLw&_nc_ad=z-m&_nc_cid=0&_nc_zt=23&_nc_ht=scontent-iad3-2.cdninstagram.com&_nc_gid=uxr3e_varhREv8ajgQ0rKQ&_nc_ss=7a22e&oh=00_AQDwgfkkK8UlEqqa3kg-i7hKm0WDbECiRP3-SsgpP2f2dg&oe=6A6E49BB",
          "https://scontent-iad3-2.cdninstagram.com/v/t51.82787-15/752740928_17932649172349487_6765669894735858771_n.jpg?stp=cp6_dst-jpg_e35_tt6&_nc_cat=103&ig_cache_key=Mzk0NTUxMzg2MDE3NTkzMDg5MA%3D%3D.3-ccb7-5&ccb=7-5&_nc_sid=58cdad&efg=eyJ2ZW5jb2RlX3RhZyI6IkNBUk9VU0VMX0lURU0ueHBpZHMuMTE3OS5zZHIucmVndWxhcl9waG90by5DMyJ9&_nc_ohc=3hsiZ_5t8gkQ7kNvwHVuyyh&_nc_oc=AdoxW87GjLAqaQ5taO0PwwBdcaiQ2zxTtDxxV3FlNB96FKru_oASz-xezHNOzZ-R0C8&_nc_ad=z-m&_nc_cid=0&_nc_zt=23&_nc_ht=scontent-iad3-2.cdninstagram.com&_nc_gid=uxr3e_varhREv8ajgQ0rKQ&_nc_ss=7a22e&oh=00_AQB_JsuMh4Ky5P3LDsFq0GLY5DosMUMgIDXHh1SUtmr8IQ&oe=6A6E26AD"
        ]
      },
      {
        "platform": "threads",
        "id": "3557348422268871722",
        "code": "DFePYrboeQq",
        "url": "https://www.threads.net/@theartificialintelligence/post/DFePYrboeQq",
        "text": "🇨🇳🇺🇸 DeepSeek tells the world that artificial intelligence is not American intelligence, and the United States has no right to monopolize the development of AI that belongs to all mankind.\n\n-Dr. Victor Gao",
        "publishedAt": "2025-01-31T02:04:57.000Z",
        "author": {
          "username": "theartificialintelligence",
          "displayName": "Artificial Intelligence | AI",
          "verified": true
        },
        "engagement": {
          "likes": 10771,
          "replies": 823,
          "reposts": 761,
          "quotes": 50
        },
        "media": [
          "https://scontent-iad6-1.cdninstagram.com/o1/v/t16/f2/m84/AQPR4zUqReqf-s4ildWOQeBb718tDuYqeErpvd3aGhr4jI7THlrcuR7esStJjWXCkmLl-XURcNSrf7AsUKFmac0NgM-QfunN0v1quQo.mp4?_nc_cat=109&_nc_sid=5e9851&_nc_ht=scontent-iad6-1.cdninstagram.com&_nc_ohc=3icBpA4DDyYQ7kNvwEn6MIV&efg=eyJ2ZW5jb2RlX3RhZyI6Inhwdl9wcm9ncmVzc2l2ZS5JTlNUQUdSQU0uRkVFRC5DMy4xMjgwLmRhc2hfYmFzZWxpbmVfMV92MSIsInhwdl9hc3NldF9pZCI6OTU1NDY3MDkxNzkyNDE0MiwiYXNzZXRfYWdlX2RheXMiOjU0MywidmlfdXNlY2FzZV9pZCI6MTAxNjQsImR1cmF0aW9uX3MiOjI2MiwidXJsZ2VuX3NvdXJjZSI6Ind3dyJ9&ccb=17-1&vs=6df3e1b4c37b0184&_nc_vs=HBksFQIYTGlnX2JhY2tmaWxsX3RpbWVsaW5lX3ZvZC9FRjRCRkY3RkY3NEM5REZERjE1QUJDQUI1OEU4Rjk4Ql92aWRlb19kYXNoaW5pdC5tcDQVAALIARIAFQIYOnBhc3N0aHJvdWdoX2V2ZXJzdG9yZS9HTFRwVkJ6VThfSDFnalVIQUtJNTJLZkhlbVZ2YmtZTEFBQUYVAgLIARIAKAAYABsCiAd1c2Vfb2lsATEScHJvZ3Jlc3NpdmVfcmVjaXBlATEVAAAm3NSR4IX7-CEVAigCQzMsF0BwYAAAAAAAGBJkYXNoX2Jhc2VsaW5lXzFfdjERAHXqB2XongEA&_nc_gid=uxr3e_varhREv8ajgQ0rKQ&_nc_zt=28&_nc_ss=7a22e&oh=00_AQB1FVQj8uhA-qSKtliVH9A4okUJTCCDLGUwpQ_F9WoCFA&oe=6A6A352B",
          "https://scontent-iad3-2.cdninstagram.com/v/t51.71878-15/474888843_486869244173785_943828438724363456_n.jpg?stp=dst-jpg_e15_tt6&_nc_cat=111&ig_cache_key=MzU1NzM0ODQyMjI2ODg3MTcyMg%3D%3D.3-ccb7-5&ccb=7-5&_nc_sid=58cdad&efg=eyJ2ZW5jb2RlX3RhZyI6IkZFRUQueHBpZHMuNjQwLnNkci52aWRlb19kZWZhdWx0X2NvdmVyX2ZyYW1lLkMzIn0%3D&_nc_ohc=0VAQZJ_qXi0Q7kNvwGqBNI3&_nc_oc=AdoH9VZA4GRIGWKMgL1yjXMwYI-Fyg1PezSOy1SBEJcSjjpPNYSj1lfGZc8BpNXYpao&_nc_ad=z-m&_nc_cid=0&_nc_zt=23&_nc_ht=scontent-iad3-2.cdninstagram.com&_nc_gid=uxr3e_varhREv8ajgQ0rKQ&_nc_ss=7a22e&oh=00_AQA50Esw1q5yzm582T9AdRk2I27NSFt0AqFgSRDI6juCUg&oe=6A6E49AA"
        ]
      },
      {
        "platform": "threads",
        "id": "3748832590774943568",
        "code": "DQGh2EPjD9Q",
        "url": "https://www.threads.net/@leon_paul_h/post/DQGh2EPjD9Q",
        "text": "I hear a lot of people saying AI is good for nothing and shouldn’t exist. You’re probably thinking of Gen-AI. \nHere is the system I built with the same AI detecting lethal landmines, designed to look like leaves, amongst thousands of leaves. \nHumans cannot do this. This saves lives. This replaces a job no one wants to do. \nThis is AI.",
        "publishedAt": "2025-10-22T06:51:14.000Z",
        "author": {
          "username": "leon_paul_h",
          "displayName": "Leon",
          "verified": null
        },
        "engagement": {
          "likes": 12474,
          "replies": 506,
          "reposts": 514,
          "quotes": 44
        },
        "media": [
          "https://scontent-iad6-1.cdninstagram.com/o1/v/t16/f2/m69/AQOkoj6S3epfmd-hIhzbEIY3R2MGQFM-DV4GZz5V2s_jNTk_akx2OL8oxQCez-1O30MfEc1OK3Pzr7XjweTd5fRg.mp4?strext=1&_nc_cat=102&_nc_sid=8bf8fe&_nc_ht=scontent-iad6-1.cdninstagram.com&_nc_ohc=m-yQBUQLSScQ7kNvwFTNzNy&efg=eyJ2ZW5jb2RlX3RhZyI6Inhwdl9wcm9ncmVzc2l2ZS5JTlNUQUdSQU0uRkVFRC5DMy4xMjc2LnByb2dyZXNzaXZlX2gyNjQtYmFzaWMtZ2VuMl83MjBwIiwieHB2X2Fzc2V0X2lkIjoxODY5MzI3Njg3MzE3NTI3LCJhc3NldF9hZ2VfZGF5cyI6Mjc5LCJ2aV91c2VjYXNlX2lkIjoxMDE2NCwiZHVyYXRpb25fcyI6OCwidXJsZ2VuX3NvdXJjZSI6Ind3dyJ9&ccb=17-1&_nc_gid=uxr3e_varhREv8ajgQ0rKQ&_nc_zt=28&_nc_ss=7a22e&oh=00_AQCZHctHg62bx4zvKy6hZ2qWaUI-0cgM7_IatYkCxlYqqA&oe=6A6E297A",
          "https://scontent-iad6-1.cdninstagram.com/v/t51.71878-15/570177049_4178982172340663_131830339174579264_n.jpg?stp=dst-jpg_e15_tt6&_nc_cat=102&ig_cache_key=Mzc0ODgzMjU5MDc3NDk0MzU2OA%3D%3D.3-ccb7-5&ccb=7-5&_nc_sid=58cdad&efg=eyJ2ZW5jb2RlX3RhZyI6IkZFRUQueHBpZHMuNjQwLnNkci52aWRlb19kZWZhdWx0X2NvdmVyX2ZyYW1lLkMzIn0%3D&_nc_ohc=4XBG6uzac9AQ7kNvwHPWFtk&_nc_oc=AdqS88oNRMjiJZU4CKUXNkhX8CzqQnAayBIvLz-kV2rwX11StJEp0Dg2ow1RZNZk-kM&_nc_ad=z-m&_nc_cid=0&_nc_zt=23&_nc_ht=scontent-iad6-1.cdninstagram.com&_nc_gid=uxr3e_varhREv8ajgQ0rKQ&_nc_ss=7a22e&oh=00_AQCr5Cad4aHBdMbIjO02dvjwzuJDhFbgScrkUDFZBnwb5A&oe=6A6E2363"
        ]
      },
      {
        "platform": "threads",
        "id": "3733107777255010279",
        "code": "DPOqb6biG_n",
        "url": "https://www.threads.net/@mit/post/DPOqb6biG_n",
        "text": "MIT researchers are seeking ways to mitigate AI’s ballooning carbon footprint, from boosting algorithms’ efficiency to rethinking data centers’ designs. “This is a once-in-a-lifetime opportunity to innovate and make AI systems less carbon-intense,” Jennifer Turliuk says. https://news.mit.edu/2025/responding-to-generative-ai-climate-impact-0930",
        "publishedAt": "2025-09-30T14:05:53.000Z",
        "author": {
          "username": "mit",
          "displayName": "MIT",
          "verified": true
        },
        "engagement": {
          "likes": 108,
          "replies": 2,
          "reposts": 10,
          "quotes": null
        },
        "media": [
          "https://scontent-iad3-2.cdninstagram.com/v/t51.82787-15/556308117_17932509414097624_2819407881773503615_n.jpg?stp=dst-jpg_e35_tt6&_nc_cat=103&ig_cache_key=MzczMzEwNzc3NzI1NTAxMDI3OQ%3D%3D.3-ccb7-5&ccb=7-5&_nc_sid=58cdad&efg=eyJ2ZW5jb2RlX3RhZyI6IkZFRUQueHBpZHMuNTYyLnNkci5yZWd1bGFyX3Bob3RvLkMzIn0%3D&_nc_ohc=s4xe4qnpYlwQ7kNvwGEIVzr&_nc_oc=AdoV83RboiuCZsMATPzcgU2Za39mHVTgKYbZb-w5K4WrVuFW90XnYWujsEeuXQfbTAE&_nc_ad=z-m&_nc_cid=0&_nc_zt=23&_nc_ht=scontent-iad3-2.cdninstagram.com&_nc_gid=uxr3e_varhREv8ajgQ0rKQ&_nc_ss=7a22e&oh=00_AQDa6bfrSMsIC5jvxzuKierH2_-ZxpBOfWC1Wz57u46opQ&oe=6A6E304D"
        ]
      }
    ]
  },
  "threads-search-users": {
    "query": "tech",
    "totalReturned": 5,
    "users": [
      {
        "username": "red.rose.whiterose",
        "displayName": null,
        "url": "https://www.threads.net/@red.rose.whiterose",
        "verified": false
      },
      {
        "username": "vulnarex",
        "displayName": null,
        "url": "https://www.threads.net/@vulnarex",
        "verified": false
      },
      {
        "username": "alina_intech",
        "displayName": "Alina",
        "url": "https://www.threads.net/@alina_intech",
        "verified": false
      },
      {
        "username": "eau.dreyy",
        "displayName": "O-Drey",
        "url": "https://www.threads.net/@eau.dreyy",
        "verified": true
      },
      {
        "username": "blkjenius",
        "displayName": "Jay D Miller",
        "url": "https://www.threads.net/@blkjenius",
        "verified": true
      }
    ]
  },
  "threads-user-posts": {
    "handle": "zuck",
    "totalReturned": 5,
    "posts": [
      {
        "platform": "threads",
        "id": "3937491905269768921",
        "code": "DakyAavlKLZ",
        "url": "https://www.threads.net/@zuck/post/DakyAavlKLZ",
        "text": "Today we're releasing Muse Spark 1.1 -- a strong agentic and coding model at a very low price. It's available through our new Meta Model API and in Meta AI.",
        "publishedAt": "2026-07-09T14:00:34.000Z",
        "author": {
          "username": "zuck",
          "displayName": "Mark Zuckerberg",
          "verified": true,
          "profileImage": "https://scontent-cdg4-2.cdninstagram.com/v/t51.82787-19/550174606_17925811725103224_8363667901743352243_n.jpg?stp=dst-jpg_s150x150_tt6&efg=eyJ2ZW5jb2RlX3RhZyI6InByb2ZpbGVfcGljLmRqYW5nby4xMDgwLmMyIn0&_nc_ht=scontent-cdg4-2.cdninstagram.com&_nc_cat=100&_nc_oc=Q6cZ2gHf4XJXymdRHno1xv4ZWDptPQ_F47AvofZR9ZypzIXJ5_ggqvnOJ4NFY10teCcuKSw&_nc_ohc=vLH8jAZMCqoQ7kNvwFFwBjL&_nc_gid=wkyjiyQ2aEsOml1qJ-3q-Q&edm=APs17CUBAAAA&ccb=7-5&oh=00_AQBvZqkyiiQ8DOAXcD-rNsrA7GYbSMXCSzCPUIBJWAPwew&oe=6A6E2ABE&_nc_sid=10d13b"
        },
        "engagement": {
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
        "author": {
          "username": "zuck",
          "displayName": "Mark Zuckerberg",
          "verified": true,
          "profileImage": "https://scontent-cdg4-2.cdninstagram.com/v/t51.82787-19/550174606_17925811725103224_8363667901743352243_n.jpg?stp=dst-jpg_s150x150_tt6&efg=eyJ2ZW5jb2RlX3RhZyI6InByb2ZpbGVfcGljLmRqYW5nby4xMDgwLmMyIn0&_nc_ht=scontent-cdg4-2.cdninstagram.com&_nc_cat=100&_nc_oc=Q6cZ2gHf4XJXymdRHno1xv4ZWDptPQ_F47AvofZR9ZypzIXJ5_ggqvnOJ4NFY10teCcuKSw&_nc_ohc=vLH8jAZMCqoQ7kNvwFFwBjL&_nc_gid=wkyjiyQ2aEsOml1qJ-3q-Q&edm=APs17CUBAAAA&ccb=7-5&oh=00_AQBvZqkyiiQ8DOAXcD-rNsrA7GYbSMXCSzCPUIBJWAPwew&oe=6A6E2ABE&_nc_sid=10d13b"
        },
        "engagement": {
          "likes": 912,
          "replies": 91,
          "reposts": 59,
          "quotes": 14
        },
        "media": [
          "https://scontent-cdg4-3.cdninstagram.com/v/t51.82787-15/741068464_17977387650103224_214669101615299168_n.webp?_nc_cat=110&ig_cache_key=MzkzNzQ5MTkyODQ5NzgyNzQxNQ%3D%3D.3-ccb7-5&ccb=7-5&_nc_sid=58cdad&efg=eyJ2ZW5jb2RlX3RhZyI6IkZFRUQueHBpZHMuMTYyMC5zZHIucmVndWxhcl9waG90by5DMyJ9&_nc_ohc=BnavDWIpJKMQ7kNvwGW14gJ&_nc_oc=Ado5sxMS3V9I9TFA6KpOo5ZTsDLrt2liAWKAxWtcz-ea50_hZb2YjO_d70TiTHhjkGA&_nc_ad=z-m&_nc_cid=0&_nc_zt=23&_nc_ht=scontent-cdg4-3.cdninstagram.com&_nc_gid=wkyjiyQ2aEsOml1qJ-3q-Q&_nc_ss=7a22e&oh=00_AQDyLjCkW1XRN7kshX0Uybz1QIy_tJdKTcfMdl2WJNISyA&oe=6A6E32AC"
        ]
      },
      {
        "platform": "threads",
        "id": "3937491906234420856",
        "code": "DakyAbpFA54",
        "url": "https://www.threads.net/@zuck/post/DakyAbpFA54",
        "text": "The Meta Model API allows developers to build using Muse Spark for the first time. Our focus is on delivering strong agentic and multimodal models at very low cost. More to come soon.",
        "publishedAt": "2026-07-09T14:00:34.000Z",
        "author": {
          "username": "zuck",
          "displayName": "Mark Zuckerberg",
          "verified": true,
          "profileImage": "https://scontent-cdg4-2.cdninstagram.com/v/t51.82787-19/550174606_17925811725103224_8363667901743352243_n.jpg?stp=dst-jpg_s150x150_tt6&efg=eyJ2ZW5jb2RlX3RhZyI6InByb2ZpbGVfcGljLmRqYW5nby4xMDgwLmMyIn0&_nc_ht=scontent-cdg4-2.cdninstagram.com&_nc_cat=100&_nc_oc=Q6cZ2gHf4XJXymdRHno1xv4ZWDptPQ_F47AvofZR9ZypzIXJ5_ggqvnOJ4NFY10teCcuKSw&_nc_ohc=vLH8jAZMCqoQ7kNvwFFwBjL&_nc_gid=wkyjiyQ2aEsOml1qJ-3q-Q&edm=APs17CUBAAAA&ccb=7-5&oh=00_AQBvZqkyiiQ8DOAXcD-rNsrA7GYbSMXCSzCPUIBJWAPwew&oe=6A6E2ABE&_nc_sid=10d13b"
        },
        "engagement": {
          "likes": 231,
          "replies": 34,
          "reposts": 6,
          "quotes": 2
        },
        "media": []
      },
      {
        "platform": "threads",
        "id": "3925863854786722836",
        "code": "DZ7eGA1G7wU",
        "url": "https://www.threads.net/@zuck/post/DZ7eGA1G7wU",
        "text": "Our new line of @metaglasses is available today. Three shapes, 26 style combos, with our most advanced Meta AI built in. Plus, three custom styles designed by @kyliejenner.",
        "publishedAt": "2026-06-23T12:57:42.000Z",
        "author": {
          "username": "zuck",
          "displayName": "Mark Zuckerberg",
          "verified": true,
          "profileImage": "https://scontent-cdg4-2.cdninstagram.com/v/t51.82787-19/550174606_17925811725103224_8363667901743352243_n.jpg?stp=dst-jpg_s150x150_tt6&efg=eyJ2ZW5jb2RlX3RhZyI6InByb2ZpbGVfcGljLmRqYW5nby4xMDgwLmMyIn0&_nc_ht=scontent-cdg4-2.cdninstagram.com&_nc_cat=100&_nc_oc=Q6cZ2gHf4XJXymdRHno1xv4ZWDptPQ_F47AvofZR9ZypzIXJ5_ggqvnOJ4NFY10teCcuKSw&_nc_ohc=vLH8jAZMCqoQ7kNvwFFwBjL&_nc_gid=wkyjiyQ2aEsOml1qJ-3q-Q&edm=APs17CUBAAAA&ccb=7-5&oh=00_AQBvZqkyiiQ8DOAXcD-rNsrA7GYbSMXCSzCPUIBJWAPwew&oe=6A6E2ABE&_nc_sid=10d13b"
        },
        "engagement": {
          "likes": 3620,
          "replies": 1403,
          "reposts": 237,
          "quotes": 117
        },
        "media": [
          "https://scontent-cdg6-1.cdninstagram.com/v/t51.71878-15/729466804_1549760159886177_1883659439515397370_n.jpg?stp=dst-jpg_e15_tt6&_nc_cat=105&ig_cache_key=MzkyNTg1NzYxNDQ3NTQyMzA5NQ%3D%3D.3-ccb7-5&ccb=7-5&_nc_sid=58cdad&efg=eyJ2ZW5jb2RlX3RhZyI6IkNBUk9VU0VMX0lURU0ueHBpZHMuNjQwLnNkci52aWRlb19kZWZhdWx0X2NvdmVyX2ZyYW1lLkMzIn0%3D&_nc_ohc=CY5bsTUA0_IQ7kNvwHtRryd&_nc_oc=Adrdd9d1NeUDj_7pAoF-kV46IpIV1m4MKw9-OyFNiZEo0dnrRLUcxrUAAUgfepLThYA&_nc_ad=z-m&_nc_cid=0&_nc_zt=23&_nc_ht=scontent-cdg6-1.cdninstagram.com&_nc_gid=wkyjiyQ2aEsOml1qJ-3q-Q&_nc_ss=7a22e&oh=00_AQDh12rAv97oeQx1mlrcUAzF1tJp0ImhLpBBYyoE1SyHJw&oe=6A6E1036",
          "https://scontent-cdg4-2.cdninstagram.com/o1/v/t16/f2/m84/AQOTRrCQTl1fyJz7fqBninvUdgWeil7BncTOhD-RfiP256I4PY_ioi8UAxdGl0WLEByzkS3XiObR8E2yNiSbmnE634ktoS1hPNebBYI.mp4?_nc_cat=107&_nc_sid=5e9851&_nc_ht=scontent-cdg4-2.cdninstagram.com&_nc_ohc=CYAcI0UX3ncQ7kNvwGMH11f&efg=eyJ2ZW5jb2RlX3RhZyI6Inhwdl9wcm9ncmVzc2l2ZS5JTlNUQUdSQU0uQ0FST1VTRUxfSVRFTS5DMy43MjAuZGFzaF9iYXNlbGluZV8xX3YxIiwieHB2X2Fzc2V0X2lkIjoxNzk2ODE3MTU3ODA4OTg4OCwiYXNzZXRfYWdlX2RheXMiOjMzLCJ2aV91c2VjYXNlX2lkIjoxMDE2NCwiZHVyYXRpb25fcyI6MjQsInVybGdlbl9zb3VyY2UiOiJ3d3cifQ%3D%3D&ccb=17-1&vs=cefa3ff17e61a968&_nc_vs=HBksFQIYTGlnX2JhY2tmaWxsX3RpbWVsaW5lX3ZvZC81NDQyODFEMkZCRDg0MzU4MzZBQUE0QzI5MzE4MzlBRF92aWRlb19kYXNoaW5pdC5tcDQVAALIARIAFQIYUWlnX3hwdl9wbGFjZW1lbnRfcGVybWFuZW50X3YyLzYwNEVGNDk2M0EwQzdFNTY4QTIyNDRDRkI4MDZBMkIwX2F1ZGlvX2Rhc2hpbml0Lm1wNBUCAsgBEgAoABgAGwKIB3VzZV9vaWwBMRJwcm9ncmVzc2l2ZV9yZWNpcGUBMRUAACbAhufCnv3qPxUCKAJDMywXQDgF41P3ztkYEmRhc2hfYmFzZWxpbmVfMV92MREAde4HZeieAQA&_nc_gid=wkyjiyQ2aEsOml1qJ-3q-Q&_nc_ss=7a22e&_nc_zt=28&oh=00_AQBibJlbXtfeWOFZ8W-D_YIilFmeekdgniF_tqLtGuyh4g&oe=6A6A37B5",
          "https://scontent-cdg6-1.cdninstagram.com/v/t51.82787-15/728809712_17974875099103224_2528686373104860184_n.webp?_nc_cat=103&ig_cache_key=MzkyNTg1NzU3NTcwNjYwODc2NQ%3D%3D.3-ccb7-5&ccb=7-5&_nc_sid=58cdad&efg=eyJ2ZW5jb2RlX3RhZyI6IkNBUk9VU0VMX0lURU0ueHBpZHMuMTA4MC5zZHIucmVndWxhcl9waG90by5DMyJ9&_nc_ohc=wgnGXUO07qoQ7kNvwFErMjL&_nc_oc=Adq5-EIcJLXNzkhq_4YrhgXrcuUH5sekxwRk3G7gdDobxWXucPu2eknzNN0-vzHnovU&_nc_ad=z-m&_nc_cid=0&_nc_zt=23&_nc_ht=scontent-cdg6-1.cdninstagram.com&_nc_gid=wkyjiyQ2aEsOml1qJ-3q-Q&_nc_ss=7a22e&oh=00_AQDZIg1uqyoaWYICAgAWby6CwDEbtvgH_bJqoLN-v-fMPg&oe=6A6E1950",
          "https://scontent-cdg4-1.cdninstagram.com/v/t51.71878-15/727566051_958314003924963_5283054625475303262_n.jpg?stp=dst-jpg_e15_tt6&_nc_cat=102&ig_cache_key=MzkyNTg1NzkxNjQyMzMxMzMwMA%3D%3D.3-ccb7-5&ccb=7-5&_nc_sid=58cdad&efg=eyJ2ZW5jb2RlX3RhZyI6IkNBUk9VU0VMX0lURU0ueHBpZHMuNjQwLnNkci52aWRlb19kZWZhdWx0X2NvdmVyX2ZyYW1lLkMzIn0%3D&_nc_ohc=cjpOMQKC2RcQ7kNvwGqCyK1&_nc_oc=AdonGNt50OyR6Ye8WodSlHoZzkJqXpiN1CU7c4aMip7u3TIddePP788D9M5OTu7NhjU&_nc_ad=z-m&_nc_cid=0&_nc_zt=23&_nc_ht=scontent-cdg4-1.cdninstagram.com&_nc_gid=wkyjiyQ2aEsOml1qJ-3q-Q&_nc_ss=7a22e&oh=00_AQA5EVOQjLQAGSxwuraxUhuDk21wdrGeWwGL6xmimvYDlw&oe=6A6E0DCD",
          "https://scontent-cdg4-2.cdninstagram.com/o1/v/t16/f2/m84/AQMq6Zzrg22F9r5ID02lab-TQjcYUfKnqpC2_w06THGl8MZ-tKE8-YxokKyN1Yjw_Nwgwpv-xkP4ApHqJoOKrA3b9z01kZ1S4Kgf9ts.mp4?_nc_cat=101&_nc_sid=5e9851&_nc_ht=scontent-cdg4-2.cdninstagram.com&_nc_ohc=dXo8gsZ3y98Q7kNvwFqsJ19&efg=eyJ2ZW5jb2RlX3RhZyI6Inhwdl9wcm9ncmVzc2l2ZS5JTlNUQUdSQU0uQ0FST1VTRUxfSVRFTS5DMy43MjAuZGFzaF9iYXNlbGluZV8xX3YxIiwieHB2X2Fzc2V0X2lkIjoxNzk3NDg3NTE5ODEwMzIyNCwiYXNzZXRfYWdlX2RheXMiOjM0LCJ2aV91c2VjYXNlX2lkIjoxMDE2NCwiZHVyYXRpb25fcyI6MjgsInVybGdlbl9zb3VyY2UiOiJ3d3cifQ%3D%3D&ccb=17-1&vs=727caf249a0595d&_nc_vs=HBksFQIYTGlnX2JhY2tmaWxsX3RpbWVsaW5lX3ZvZC8zMTQ2RkM2Q0JBNkVFMzhBMDIwQzk0MkZEQzRGMEE4NV92aWRlb19kYXNoaW5pdC5tcDQVAALIARIAFQIYUWlnX3hwdl9wbGFjZW1lbnRfcGVybWFuZW50X3YyLzQzNEQwMTM2OTM3NzEyNTk0MkEwNDFERTgyODAyNzg0X2F1ZGlvX2Rhc2hpbml0Lm1wNBUCAsgBEgAoABgAGwKIB3VzZV9vaWwBMRJwcm9ncmVzc2l2ZV9yZWNpcGUBMRUAACbw-oSxuIPuPxUCKAJDMywXQDwPnbItDlYYEmRhc2hfYmFzZWxpbmVfMV92MREAde4HZeieAQA&_nc_gid=wkyjiyQ2aEsOml1qJ-3q-Q&_nc_zt=28&_nc_ss=7a22e&oh=00_AQA3i6wIXG5BDtXqCPcTuhGW7EylltG_syfPKY_TBRHVwQ&oe=6A6A43B3",
          "https://scontent-cdg6-1.cdninstagram.com/v/t51.71878-15/729466804_1549760159886177_1883659439515397370_n.jpg?stp=c0.80.640.640a_dst-jpg_e15_s640x640_tt6&_nc_cat=105&ig_cache_key=MzkyNTg1NzYxNDQ3NTQyMzA5NQ%3D%3D.3-ccb7-5&ccb=7-5&_nc_sid=58cdad&efg=eyJ2ZW5jb2RlX3RhZyI6IkNBUk9VU0VMX0lURU0ueHBpZHMuNjQwLnNkci52aWRlb19kZWZhdWx0X2NvdmVyX2ZyYW1lLkMzIn0%3D&_nc_ohc=CY5bsTUA0_IQ7kNvwHtRryd&_nc_oc=Adrdd9d1NeUDj_7pAoF-kV46IpIV1m4MKw9-OyFNiZEo0dnrRLUcxrUAAUgfepLThYA&_nc_ad=z-m&_nc_cid=0&_nc_zt=23&_nc_ht=scontent-cdg6-1.cdninstagram.com&_nc_gid=wkyjiyQ2aEsOml1qJ-3q-Q&_nc_ss=7a22e&oh=00_AQCd8VjTZ6ncCZ_RaLy9BpMWlxGoelCy8LQRKnudoVi5Yw&oe=6A6E1036"
        ]
      },
      {
        "platform": "threads",
        "id": "3920731152608519405",
        "code": "DZpPDXbCeTt",
        "url": "https://www.threads.net/@zuck/post/DZpPDXbCeTt",
        "text": "500M monthly actives on Threads in less than 3 years. Thanks for making this platform what it is. 🙏",
        "publishedAt": "2026-06-16T10:59:56.000Z",
        "author": {
          "username": "zuck",
          "displayName": "Mark Zuckerberg",
          "verified": true,
          "profileImage": "https://scontent-cdg4-2.cdninstagram.com/v/t51.82787-19/550174606_17925811725103224_8363667901743352243_n.jpg?stp=dst-jpg_s150x150_tt6&efg=eyJ2ZW5jb2RlX3RhZyI6InByb2ZpbGVfcGljLmRqYW5nby4xMDgwLmMyIn0&_nc_ht=scontent-cdg4-2.cdninstagram.com&_nc_cat=100&_nc_oc=Q6cZ2gHf4XJXymdRHno1xv4ZWDptPQ_F47AvofZR9ZypzIXJ5_ggqvnOJ4NFY10teCcuKSw&_nc_ohc=vLH8jAZMCqoQ7kNvwFFwBjL&_nc_gid=wkyjiyQ2aEsOml1qJ-3q-Q&edm=APs17CUBAAAA&ccb=7-5&oh=00_AQBvZqkyiiQ8DOAXcD-rNsrA7GYbSMXCSzCPUIBJWAPwew&oe=6A6E2ABE&_nc_sid=10d13b"
        },
        "engagement": {
          "likes": 18057,
          "replies": 4770,
          "reposts": 586,
          "quotes": 252
        },
        "media": []
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
      },
      {
        "platform": "tiktok_ad_library",
        "id": "1872402620170418",
        "url": "https://library.tiktok.com/ads/detail/?ad_id=1872402620170418",
        "text": "Relax and Recharge with Professional Massage Services Near You. Book Today.",
        "adFormat": "video",
        "firstShown": "2026-08-02T00:00:00.000Z",
        "lastShown": "2026-08-02T00:00:00.000Z",
        "impressions": "0-1K",
        "advertiser": {
          "name": "HongKong AdTiger Media Co., Limited",
          "location": "Hong Kong"
        },
        "media": [
          "https://p16-common-sign.tiktokcdn.com/tos-alisg-p-0051c001-sg/3de4a6d6aeade6ab958a291a3a5bd49c~tplv-tiktokx-origin.jpeg?dr=14582&refresh_token=d3c7a0dd&x-expires=1785686400&x-signature=GyiPUhUAFUFyEOGfF1XhsMSx4rQ%3D&t=4d5b0474&ps=13740610&",
          "https://library.tiktok.com/api/v1/cdn/1785667307/video/aHR0cHM6Ly92MTZtLnRpa3Rva2Nkbi5jb20vNjQxZWM4ZWZiYTgwY2M1YzU0OWI4N2NhZjk5MjEyMDEvNmE2ZjczNTgvdmlkZW8vdG9zL2FsaXNnL3Rvcy1hbGlzZy12ZS0wMDUxYzAwMS1zZy9vd2dJMzRBYlZnRzBHRmZEUVVoQWZVTWdXWjhBQUNTRUdSOWVtWS8=/bb0280a2-4a63-46e8-a759-8d4b732e6d88?a=475769&bt=720&btag=e000b0000&bti=PDU2NmYwMy86&ft=.NpOcInz7Th2~INGXq8Zmo&l=202608021841474F1F2ED09C9DE84DF0AE&mime_type=video_mp4&rc=NDQ8NjQ0ZTxlM2Y2Njs5ZEBpMzhuZ245cjZqPDMzODYzNEAtLmNjXl5jNV8xMi0yLzJgYSNjMXMtMmQ0aWthLS1kMC1zcw%3D%3D&signature=2pQWORzvAEmUKgGQGmydZDn%2B0mYazq1nnnXy7NGPupQ%3D&vvpl=1"
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
    "ads": [
      {
        "platform": "tiktok_creative_center",
        "id": "7662489073849090066",
        "url": "https://ads.tiktok.com/business/creativecenter/inspiration/topads/pc/en?period=30&region=US&order_by=ctr",
        "title": "Nuuly loves a woman in a suit ! #ad #nuulypartner #nuuly #frthoidolovenuuly",
        "brandName": "nuuly",
        "likes": 620,
        "ctr": 0.17,
        "ctrTier": "below_50%",
        "costTier": 1,
        "favorite": false,
        "isSparkAd": false,
        "industry": "All Industries",
        "industryKey": "label_23105000000",
        "objective": "Reach",
        "objectiveKey": null,
        "adFormat": "All Formats",
        "countries": [
          "US"
        ],
        "periodDays": 30,
        "video": {
          "id": "v10033g50000example",
          "url": "https://v16m-default.tiktokcdn.com/example.mp4",
          "urlHd": "https://v16m-default.tiktokcdn.com/example-hd.mp4",
          "cover": "https://p16-common-sign.tiktokcdn.com/example~tplv-noop.image",
          "durationSeconds": 15.0,
          "width": 720,
          "height": 1280
        },
        "media": [
          "https://p16-common-sign.tiktokcdn.com/example~tplv-noop.image",
          "https://v16m-default.tiktokcdn.com/example-hd.mp4",
          "https://v16m-default.tiktokcdn.com/example.mp4"
        ],
        "tags": []
      },
      {
        "platform": "tiktok_creative_center",
        "id": "7662938725836324871",
        "url": "https://ads.tiktok.com/business/creativecenter/inspiration/topads/pc/en?period=30&region=US&order_by=ctr",
        "title": "How I fix my hair EASILY on the go #hair #hairhack",
        "brandName": null,
        "likes": 5,
        "ctr": 0.62,
        "ctrTier": "top_25%",
        "costTier": 0,
        "favorite": false,
        "isSparkAd": false,
        "industry": "All Industries",
        "industryKey": "label_23105000000",
        "objective": "Product Sales",
        "objectiveKey": null,
        "adFormat": "All Formats",
        "countries": [
          "US"
        ],
        "periodDays": 30,
        "video": {
          "id": "v10033g50000example",
          "url": "https://v16m-default.tiktokcdn.com/example.mp4",
          "urlHd": "https://v16m-default.tiktokcdn.com/example-hd.mp4",
          "cover": "https://p16-common-sign.tiktokcdn.com/example~tplv-noop.image",
          "durationSeconds": 15.0,
          "width": 720,
          "height": 1280
        },
        "media": [
          "https://p16-common-sign.tiktokcdn.com/example~tplv-noop.image",
          "https://v16m-default.tiktokcdn.com/example-hd.mp4",
          "https://v16m-default.tiktokcdn.com/example.mp4"
        ],
        "tags": []
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
        "percentage": "26.02%"
      },
      {
        "country": "United States",
        "countryCode": "US",
        "count": 33,
        "percentage": "12.27%"
      },
      {
        "country": "Nigeria",
        "countryCode": "NG",
        "count": 21,
        "percentage": "7.81%"
      },
      {
        "country": "Senegal",
        "countryCode": "SN",
        "count": 8,
        "percentage": "2.97%"
      },
      {
        "country": "Bangladesh",
        "countryCode": "BD",
        "count": 8,
        "percentage": "2.97%"
      }
    ]
  },
  "tiktok-channel-details": {
    "platform": "tiktok",
    "url": "https://www.tiktok.com/@natgeo",
    "username": "natgeo",
    "displayName": "National Geographic",
    "bio": "Step into wonder and find your inner explorer with National Geographic 🌎",
    "followers": 9581608,
    "following": 61,
    "likes": 53099961,
    "postCount": 1433,
    "verified": true,
    "private": false,
    "profileImage": "https://p16-common-sign.tiktokcdn-us.com/tos-useast8-avt-0068-tx2/324924e171e481040a1ea202962f6e07~tplv-tiktokx-cropcenter:1080:1080.jpeg?dr=9640&refresh_token=1fa719b0&x-expires=1784628000&x-signature=DS9ZLakUPkqg%2Bzn8ZeXDLRmh%2Fhc%3D&t=4d5b0474&ps=13740610&shp=a5d48078&shcp=81f88b70&idc=useast8",
    "externalUrl": "spr.ly/natgeotiktok",
    "category": "Media & Entertainment"
  },
  "tiktok-channel-posts": {
    "url": "https://www.tiktok.com/@paw.dreams0",
    "totalReturned": 3,
    "posts": [
      {
        "platform": "tiktok",
        "url": "https://www.tiktok.com/@paw.dreams0/video/7662021590825061654",
        "id": "7662021590825061654",
        "caption": "kitten was teased for playing with a cardboard Motorbike  #catfunnyvideos #catcartoon #catcute #catstory #kitten",
        "description": "kitten was teased for playing with a cardboard Motorbike  #catfunnyvideos #catcartoon #catcute #catstory #kitten",
        "publishedAt": "2026-07-13T15:00:00.000Z",
        "durationSeconds": 79.97,
        "thumbnailUrl": "https://p16-common-sign.tiktokcdn.com/tos-no1a-p-0037-no/o8GAEB3hAPfJ9hQpWX4KWY5eeIgRQALTAFAUeG~tplv-tiktokx-cropcenter-q:300:400:q70.webp",
        "author": {
          "username": "paw.dreams0",
          "displayName": "Paw Dreams",
          "url": "https://www.tiktok.com/@paw.dreams0",
          "followers": 117886,
          "verified": false,
          "profileImage": "https://p16-common-sign.tiktokcdn.com/tos-maliva-avt-0068/14e5b5dbddf91912237e342a048afb2c~tplv-tiktokx-cropcenter-q:1080:1080:q70.webp"
        },
        "engagement": {
          "views": 253340,
          "likes": 4607,
          "comments": 116,
          "shares": 327,
          "saves": 949
        },
        "hashtags": [
          "catfunnyvideos",
          "catcartoon",
          "catcute",
          "catstory",
          "kitten"
        ],
        "musicName": "original sound - paw.dreams0"
      },
      {
        "platform": "tiktok",
        "url": "https://www.tiktok.com/@paw.dreams0/video/7661626147322547478",
        "id": "7661626147322547478",
        "caption": "The kitten was teased for playing with a cardboard Spoon shaped car #catfunnyvideos #catcartoon #catcute #catstory #kitten",
        "description": "The kitten was teased for playing with a cardboard Spoon shaped car #catfunnyvideos #catcartoon #catcute #catstory #kitten",
        "publishedAt": "2026-07-12T16:00:00.000Z",
        "durationSeconds": 65.969,
        "thumbnailUrl": "https://p16-common-sign.tiktokcdn.com/tos-no1a-p-0037-no/okepsDWBJhGTfTpIXjLeLEA8WMALIAKTjRAQeA~tplv-tiktokx-cropcenter-q:300:400:q70.webp",
        "author": {
          "username": "paw.dreams0",
          "displayName": "Paw Dreams",
          "url": "https://www.tiktok.com/@paw.dreams0",
          "followers": 117886,
          "verified": false,
          "profileImage": "https://p16-common-sign.tiktokcdn.com/tos-maliva-avt-0068/14e5b5dbddf91912237e342a048afb2c~tplv-tiktokx-cropcenter-q:1080:1080:q70.webp"
        },
        "engagement": {
          "views": 78897,
          "likes": 1386,
          "comments": 51,
          "shares": 74,
          "saves": 280
        },
        "hashtags": [
          "catfunnyvideos",
          "catcartoon",
          "catcute",
          "catstory",
          "kitten"
        ],
        "musicName": "original sound - paw.dreams0"
      },
      {
        "platform": "tiktok",
        "url": "https://www.tiktok.com/@paw.dreams0/video/7661284651968859414",
        "id": "7661284651968859414",
        "caption": "Kitten Mocked For Playing With The Carboard Tortle Car   #catfunnyvideos #catcartoon #catcute #catstory #kitten",
        "description": "Kitten Mocked For Playing With The Carboard Tortle Car   #catfunnyvideos #catcartoon #catcute #catstory #kitten",
        "publishedAt": "2026-07-11T15:30:00.000Z",
        "durationSeconds": 81.688,
        "thumbnailUrl": "https://p16-common-sign.tiktokcdn.com/tos-no1a-p-0037-no/oYhfP5AcQI3DfUAWWYpJJGfKSgN1QuAeAA1LFW~tplv-tiktokx-cropcenter-q:300:400:q70.webp",
        "author": {
          "username": "paw.dreams0",
          "displayName": "Paw Dreams",
          "url": "https://www.tiktok.com/@paw.dreams0",
          "followers": 117886,
          "verified": false,
          "profileImage": "https://p16-common-sign.tiktokcdn.com/tos-maliva-avt-0068/14e5b5dbddf91912237e342a048afb2c~tplv-tiktokx-cropcenter-q:1080:1080:q70.webp"
        },
        "engagement": {
          "views": 110306,
          "likes": 1890,
          "comments": 112,
          "shares": 134,
          "saves": 388
        },
        "hashtags": [
          "catfunnyvideos",
          "catcartoon",
          "catcute",
          "catstory",
          "kitten"
        ],
        "musicName": "original sound - paw.dreams0"
      }
    ],
    "nextCursor": "1781971200001",
    "hasMore": true
  },
  "tiktok-comment-replies": {
    "platform": "tiktok",
    "url": "https://www.tiktok.com/@khaby.lame/video/7646812028874673439",
    "commentId": "7652622392003003157",
    "totalReturned": 10,
    "replies": [
      {
        "id": "7652704280361403157",
        "text": "tinggal seribu lagi jadi 5jt😹",
        "author": "evan.gunawan2037",
        "authorName": "MAJIN_EVAN⚡",
        "likeCount": 16,
        "publishedAt": "2026-06-18T12:01:20.000Z",
        "verified": false,
        "profileImage": "https://p16-common-sign.tiktokcdn-eu.com/tos-alisg-avt-0068/6ea4cabf09938d71804dd2b430afbdcb~tplv-tiktokx-cropcenter-q:100:100:q70.webp?dr=9606&idc=useast2b&ps=87d6e48a&refresh_token=595426e6&s=COMMENT_LIST&sc=avatar&shcp=ff37627b&shp=30310797&t=223449c4&x-expires=1784541600&x-signature=54CztTw4VhDfCPIEK2C0yD%2FxFPg%3D"
      },
      {
        "id": "7653041079252517640",
        "text": "jir Luh gimana pelenger itu nya kalau 1 rb?",
        "author": "oficial_tod",
        "authorName": "it's me Gung",
        "likeCount": 31,
        "publishedAt": "2026-06-19T09:48:12.000Z",
        "verified": false,
        "profileImage": "https://p16-common-sign.tiktokcdn-eu.com/tos-alisg-avt-0068/34e550efa4bd9aec97d7de21011f1d5d~tplv-tiktokx-cropcenter-q:100:100:q70.webp?dr=9606&idc=useast2b&ps=87d6e48a&refresh_token=c2506938&s=COMMENT_LIST&sc=avatar&shcp=ff37627b&shp=30310797&t=223449c4&x-expires=1784541600&x-signature=oIMo9aMYVCLKg1ft2YcXpaDO6NQ%3D"
      },
      {
        "id": "7655633248479200021",
        "text": "iya bro gw plenger 😹",
        "author": "evan.gunawan2037",
        "authorName": "MAJIN_EVAN⚡",
        "likeCount": 4,
        "publishedAt": "2026-06-26T09:27:17.000Z",
        "verified": false,
        "profileImage": "https://p16-common-sign.tiktokcdn-eu.com/tos-alisg-avt-0068/6ea4cabf09938d71804dd2b430afbdcb~tplv-tiktokx-cropcenter-q:100:100:q70.webp?dr=9606&idc=useast2b&ps=87d6e48a&refresh_token=595426e6&s=COMMENT_LIST&sc=avatar&shcp=ff37627b&shp=30310797&t=223449c4&x-expires=1784541600&x-signature=54CztTw4VhDfCPIEK2C0yD%2FxFPg%3D"
      },
      {
        "id": "7655391781529469716",
        "text": "100 sepereak doang itu mahkurang nya",
        "author": "ical_style1",
        "authorName": "Cal🦅",
        "likeCount": 1,
        "publishedAt": "2026-06-25T17:50:10.000Z",
        "verified": false,
        "profileImage": "https://p16-common-sign.tiktokcdn-eu.com/tos-alisg-avt-0068/a553573e0a120f841e441b1ff94db371~tplv-tiktokx-cropcenter-q:100:100:q70.webp?dr=9606&idc=useast2b&ps=87d6e48a&refresh_token=2a80f242&s=COMMENT_LIST&sc=avatar&shcp=ff37627b&shp=30310797&t=223449c4&x-expires=1784541600&x-signature=xkI6rXm0K%2FLZ%2BFfSEwxFULxAtwE%3D"
      },
      {
        "id": "7655968916204978965",
        "text": "1 perak",
        "author": "oppai_fans",
        "authorName": "OPPAI FANS",
        "likeCount": 1,
        "publishedAt": "2026-06-27T07:09:58.000Z",
        "verified": false,
        "profileImage": "https://p16-common-sign.tiktokcdn-eu.com/tos-alisg-avt-0068/3e676fb527590bc4a3cdca6245dd36c3~tplv-tiktokx-cropcenter-q:100:100:q70.webp?dr=9606&idc=useast2b&ps=87d6e48a&refresh_token=4f8b4488&s=COMMENT_LIST&sc=avatar&shcp=ff37627b&shp=30310797&t=223449c4&x-expires=1784541600&x-signature=2%2F99mmnsEJtLD%2F0BXeEjsbaWV%2Fs%3D"
      },
      {
        "id": "7654669552286532360",
        "text": "emotnya si ini :😹\npemikirannya plenger",
        "author": "rpl_fall",
        "authorName": "Fall",
        "likeCount": 3,
        "publishedAt": "2026-06-23T19:07:30.000Z",
        "verified": false,
        "profileImage": "https://p16-common-sign.tiktokcdn-eu.com/tos-alisg-avt-0068/e0101b36be56d56bf30e68797809e35a~tplv-tiktokx-cropcenter-q:100:100:q70.webp?dr=9606&idc=useast2b&ps=87d6e48a&refresh_token=8826d0f3&s=COMMENT_LIST&sc=avatar&shcp=ff37627b&shp=30310797&t=223449c4&x-expires=1784541600&x-signature=5yNRPLUDjDNyJ5w70aRj8jj%2BLTU%3D"
      },
      {
        "id": "7652718324300563221",
        "text": "1 rupiah kali bukan seribu",
        "author": "oppai_fans",
        "authorName": "OPPAI FANS",
        "likeCount": 14,
        "publishedAt": "2026-06-18T12:55:47.000Z",
        "verified": false,
        "profileImage": "https://p16-common-sign.tiktokcdn-eu.com/tos-alisg-avt-0068/3e676fb527590bc4a3cdca6245dd36c3~tplv-tiktokx-cropcenter-q:100:100:q70.webp?dr=9606&idc=useast2b&ps=87d6e48a&refresh_token=4f8b4488&s=COMMENT_LIST&sc=avatar&shcp=ff37627b&shp=30310797&t=223449c4&x-expires=1784541600&x-signature=2%2F99mmnsEJtLD%2F0BXeEjsbaWV%2Fs%3D"
      },
      {
        "id": "7654032829540270868",
        "text": "ga sekolah gini",
        "author": "zaaxz_renamamiya",
        "authorName": "𝙕𝙖𝙭𝙯 𝖋𝖙 𝙆𝙂𝙉",
        "likeCount": 2,
        "publishedAt": "2026-06-22T01:56:58.000Z",
        "verified": false,
        "profileImage": "https://p16-common-sign.tiktokcdn-eu.com/tos-alisg-avt-0068/cdbbf04e9282ba9b34596ca100fc73f3~tplv-tiktokx-cropcenter-q:100:100:q70.webp?dr=9606&idc=useast2b&ps=87d6e48a&refresh_token=4a3ae8bc&s=COMMENT_LIST&sc=avatar&shcp=ff37627b&shp=30310797&t=223449c4&x-expires=1784541600&x-signature=12vLi7lJpjvEGMUnLqAUeKcgp74%3D"
      },
      {
        "id": "7663845732496343816",
        "text": "Beli online nambah onkir 30 ribu🗿",
        "author": "gemaprasetia",
        "authorName": "Kapten.Rivaille",
        "likeCount": 0,
        "publishedAt": "2026-07-18T12:35:50.000Z",
        "verified": false,
        "profileImage": "https://p19-common-sign.tiktokcdn-eu.com/tos-alisg-avt-0068/0594a14c8e2b65bc68b5a08eb8ef194d~tplv-tiktokx-cropcenter-q:100:100:q70.webp?dr=9606&idc=useast2b&ps=87d6e48a&refresh_token=0b314880&s=COMMENT_LIST&sc=avatar&shcp=ff37627b&shp=30310797&t=223449c4&x-expires=1784541600&x-signature=zaJrUEpoB%2FS7GgsHP4GkW2n6DcI%3D"
      },
      {
        "id": "7654669373819486983",
        "text": "dongo",
        "author": "rpl_fall",
        "authorName": "Fall",
        "likeCount": 0,
        "publishedAt": "2026-06-23T19:06:55.000Z",
        "verified": false,
        "profileImage": "https://p16-common-sign.tiktokcdn-eu.com/tos-alisg-avt-0068/e0101b36be56d56bf30e68797809e35a~tplv-tiktokx-cropcenter-q:100:100:q70.webp?dr=9606&idc=useast2b&ps=87d6e48a&refresh_token=8826d0f3&s=COMMENT_LIST&sc=avatar&shcp=ff37627b&shp=30310797&t=223449c4&x-expires=1784541600&x-signature=5yNRPLUDjDNyJ5w70aRj8jj%2BLTU%3D"
      }
    ],
    "totalReplies": 17,
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
        "publishedAt": "2026-06-02T16:23:41.000Z"
      },
      {
        "id": "7647102586621297429",
        "text": "С каждым лайком нос растёт",
        "author": "gudingar",
        "authorAvatarUrl": "https://p16-common-sign.tiktokcdn-eu.com/tos-alisg-avt-0068/56317ccbf99872b4f14448d7fb959826~tplv-tiktokx-cropcenter-q:100:100:q70.webp?dr=9606&idc=useast2b&ps=87d6e48a&refresh_token=9f5971b4&s=COMMENT_LIST&sc=avatar&shcp=5597e28e&shp=30310797&t=223449c4&x-expires=1784300400&x-signature=FXHzE%2FNLM2v17bh45RTPVfe8%2BDA%3D",
        "likeCount": 635,
        "publishedAt": "2026-06-03T09:43:54.000Z"
      },
      {
        "id": "7646848703109612308",
        "text": "welcome back brother we miss your content since you got rich 🤑",
        "author": "hassanmahadhi44",
        "authorAvatarUrl": "https://p16-common-sign.tiktokcdn-eu.com/tos-alisg-avt-0068/8c3fd35abfa9ca1f0289ce7dfb474955~tplv-tiktokx-cropcenter-q:100:100:q70.webp?dr=9606&idc=useast2b&ps=87d6e48a&refresh_token=be09752c&s=COMMENT_LIST&sc=avatar&shcp=5597e28e&shp=30310797&t=223449c4&x-expires=1784300400&x-signature=xpaGPkcaLHexRPPfuBjFZh8oOGc%3D",
        "likeCount": 405,
        "publishedAt": "2026-06-02T17:18:38.000Z"
      },
      {
        "id": "7646829101696795412",
        "text": "Assalamualaikum all Muslim 🫶👋",
        "author": "flamefaisal",
        "authorAvatarUrl": "https://p16-common-sign.tiktokcdn-eu.com/tos-alisg-avt-0068/ccf74b3284cccc970c60ec8479d83055~tplv-tiktokx-cropcenter-q:100:100:q70.webp?dr=9606&idc=useast2b&ps=87d6e48a&refresh_token=f9e4b949&s=COMMENT_LIST&sc=avatar&shcp=5597e28e&shp=30310797&t=223449c4&x-expires=1784300400&x-signature=MDbiuKJH8omek6ps9Z%2FD9xfe4ZY%3D",
        "likeCount": 9613,
        "publishedAt": "2026-06-02T16:02:29.000Z"
      },
      {
        "id": "7646812491309564673",
        "text": "[Photo] who watching today",
        "author": "pabloescoba.25666",
        "authorAvatarUrl": "https://p16-common-sign.tiktokcdn-eu.com/tos-alisg-avt-0068/e64b23b557494ea765ecf470ba8e1d95~tplv-tiktokx-cropcenter-q:100:100:q70.webp?dr=9606&idc=useast2b&ps=87d6e48a&refresh_token=6adf42ed&s=COMMENT_LIST&sc=avatar&shcp=5597e28e&shp=30310797&t=223449c4&x-expires=1784300400&x-signature=Pgbx2BmKC7SAoHOH7KN%2F6mxAwa0%3D",
        "likeCount": 2365,
        "publishedAt": "2026-06-02T14:58:21.000Z"
      },
      {
        "id": "7648688233429566225",
        "text": "[Photo] $800?\n$799?\nHmmmmm How?? Why",
        "author": "udaymuhammed",
        "authorAvatarUrl": "https://p16-common-sign.tiktokcdn-eu.com/tos-alisg-avt-0068/9f2f295378b728ea2478292e32a10122~tplv-tiktokx-cropcenter-q:100:100:q70.webp?dr=9606&idc=useast2b&ps=87d6e48a&refresh_token=902fa2e2&s=COMMENT_LIST&sc=avatar&shcp=5597e28e&shp=30310797&t=223449c4&x-expires=1784300400&x-signature=rGtZD7vu36YGKscvIUOG79999q4%3D",
        "likeCount": 539,
        "publishedAt": "2026-06-07T16:16:53.000Z"
      }
    ],
    "nextCursor": "6",
    "hasMore": true
  },
  "tiktok-live": {
    "platform": "tiktok",
    "username": "espn",
    "isLive": false,
    "creator": {
      "displayName": "ESPN",
      "followers": 60012277,
      "verified": true,
      "avatar": "https://p16-common-sign.tiktokcdn-us.com/tos-maliva-avt-0068/7310257743653240837~tplv-tiktokx-cropcenter:1080:1080.webp?dr=9640&refresh_token=80fa76fc&x-expires=1785409200&x-signature=FKUjYJgevw6H%2F02LrG5LD%2B4tMoI%3D&t=4d5b0474&ps=13740610&shp=a5d48078&shcp=fdd36af4&idc=useast5",
      "bio": "Serving Sports Fans. Anytime. Anywhere."
    },
    "room": {
      "id": "3578501789985538992",
      "title": "WORLD CUP FINAL PREVIEW 🏆⚽️",
      "startedAt": "2026-07-16T17:54:15.000Z",
      "viewerCount": 1,
      "totalEnterCount": 99160,
      "coverUrl": "https://p16-common-sign.tiktokcdn-us.com/tos-maliva-avt-0068/7310257743653240837~tplv-tiktokx-cropcenter:720:720.webp?dr=9640&refresh_token=929e6963&x-expires=1785409200&x-signature=LH4jDtgdTto5OnEr2KmFkVYjrZI%3D&t=4d5b0474&ps=13740610&shp=a5d48078&shcp=fdd36af4&idc=useast5",
      "streamUrls": [
        "https://pull-f5-tt01.tiktokcdn-us.com/stage/stream-3578501789985538992_hd.flv?expire=1786447036&sign=1d93e103fc74cb8d60ab52fbe3f75984",
        "https://pull-hls-f16-tt01.tiktokcdn-us.com/stage/stream-3578501789985538992_hd/index.m3u8?expire=1786447036&sign=c31a2a33815891e3385c09b3367fa2bc",
        "https://pull-f5-tt01.tiktokcdn-us.com/stage/stream-3578501789985538992_hd/index.mpd?expire=1786447036&sign=203f24dba2b34b401151fb14a5f7dd26",
        "https://pull-f5-tt01.tiktokcdn-us.com/stage/stream-3578501789985538992.flv?expire=1786447036&sign=fa936c642c249ebc46995cad6f11ce81&only_audio=1",
        "https://pull-f5-tt01.tiktokcdn-us.com/stage/stream-3578501789985538992_ao/index.mpd?expire=1786447036&sign=2beb75f264b3e8a952a089b32cc47d58"
      ]
    }
  },
  "tiktok-live-info": {
    "platform": "tiktok",
    "username": "espn",
    "isLive": false,
    "creator": {
      "displayName": "ESPN",
      "followers": 60012277,
      "verified": true,
      "avatar": "https://p16-common-sign.tiktokcdn-us.com/tos-maliva-avt-0068/7310257743653240837~tplv-tiktokx-cropcenter:1080:1080.webp?dr=9640&refresh_token=80fa76fc&x-expires=1785409200&x-signature=FKUjYJgevw6H%2F02LrG5LD%2B4tMoI%3D&t=4d5b0474&ps=13740610&shp=a5d48078&shcp=fdd36af4&idc=useast5",
      "bio": "Serving Sports Fans. Anytime. Anywhere."
    },
    "room": {
      "id": "3578501789985538992",
      "title": "WORLD CUP FINAL PREVIEW 🏆⚽️",
      "startedAt": "2026-07-16T17:54:15.000Z",
      "viewerCount": 1,
      "totalEnterCount": 99160,
      "coverUrl": "https://p16-common-sign.tiktokcdn-us.com/tos-maliva-avt-0068/7310257743653240837~tplv-tiktokx-cropcenter:720:720.webp?dr=9640&refresh_token=929e6963&x-expires=1785409200&x-signature=LH4jDtgdTto5OnEr2KmFkVYjrZI%3D&t=4d5b0474&ps=13740610&shp=a5d48078&shcp=fdd36af4&idc=useast5",
      "streamUrls": [
        "https://pull-f5-tt01.tiktokcdn-us.com/stage/stream-3578501789985538992_hd.flv?expire=1786447036&sign=1d93e103fc74cb8d60ab52fbe3f75984",
        "https://pull-hls-f16-tt01.tiktokcdn-us.com/stage/stream-3578501789985538992_hd/index.m3u8?expire=1786447036&sign=c31a2a33815891e3385c09b3367fa2bc",
        "https://pull-f5-tt01.tiktokcdn-us.com/stage/stream-3578501789985538992_hd/index.mpd?expire=1786447036&sign=203f24dba2b34b401151fb14a5f7dd26",
        "https://pull-f5-tt01.tiktokcdn-us.com/stage/stream-3578501789985538992.flv?expire=1786447036&sign=fa936c642c249ebc46995cad6f11ce81&only_audio=1",
        "https://pull-f5-tt01.tiktokcdn-us.com/stage/stream-3578501789985538992_ao/index.mpd?expire=1786447036&sign=2beb75f264b3e8a952a089b32cc47d58"
      ]
    },
    "streamUrls": [
      "https://pull-f5-tt01.tiktokcdn-us.com/stage/stream-3578501789985538992_hd.flv?expire=1786447036&sign=1d93e103fc74cb8d60ab52fbe3f75984",
      "https://pull-hls-f16-tt01.tiktokcdn-us.com/stage/stream-3578501789985538992_hd/index.m3u8?expire=1786447036&sign=c31a2a33815891e3385c09b3367fa2bc",
      "https://pull-f5-tt01.tiktokcdn-us.com/stage/stream-3578501789985538992_hd/index.mpd?expire=1786447036&sign=203f24dba2b34b401151fb14a5f7dd26",
      "https://pull-f5-tt01.tiktokcdn-us.com/stage/stream-3578501789985538992.flv?expire=1786447036&sign=fa936c642c249ebc46995cad6f11ce81&only_audio=1",
      "https://pull-f5-tt01.tiktokcdn-us.com/stage/stream-3578501789985538992_ao/index.mpd?expire=1786447036&sign=2beb75f264b3e8a952a089b32cc47d58"
    ]
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
          "verified": false,
          "profileImage": "https://p16-common-sign.tiktokcdn.com/tos-maliva-avt-0068/08987e23b94057953fd4f1738694bf5f~tplv-tiktokx-cropcenter-q:1080:1080:q70.webp?dr=10796&idc=my2&ps=87d6e48a&refresh_token=bc21b726&s=MUSIC_AWEME&sc=avatar&shcp=f6441914&shp=d05b14bd&t=223449c4&x-expires=1785171600&x-signature=D%2FanX%2BEAwPGclXui5sL48ejAGUk%3D"
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
        "musicName": "original sound - khaby.lame"
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
          "verified": false,
          "profileImage": "https://p16-common-sign.tiktokcdn.com/tos-maliva-avt-0068/7b938fef8c8e68e37c261c961ccc7560~tplv-tiktokx-cropcenter-q:1080:1080:q70.webp?dr=10796&idc=my2&ps=87d6e48a&refresh_token=48c28ab9&s=MUSIC_AWEME&sc=avatar&shcp=f6441914&shp=d05b14bd&t=223449c4&x-expires=1785171600&x-signature=De8%2FtfqqeKjQKCfU%2Bw%2BfTGJFIlU%3D"
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
          "tiktokpakastan",
          "okaralover💪💪❤️",
          "alichaiwala❤️💫",
          "tiktok",
          "support",
          "trending",
          "foruyou",
          "1m"
        ],
        "musicName": "original sound - khaby.lame"
      },
      {
        "platform": "tiktok",
        "url": "https://www.tiktok.com/@babi_batox/video/7657210703262010631",
        "id": "7657210703262010631",
        "caption": "Obrigado, volte sempre; THank you, come again #aprender #khaby #comed #badi_xatox #humor",
        "description": "Obrigado, volte sempre; THank you, come again #aprender #khaby #comed #badi_xatox #humor",
        "publishedAt": "2026-06-30T15:28:22.000Z",
        "durationSeconds": 16.467,
        "thumbnailUrl": "https://p16-common-sign.tiktokcdn.com/tos-alisg-p-0037/oYw7iFBEEQ6IgRQz9Hf7QL2ARZkHqDcQBBfSBw~tplv-tiktokx-cropcenter-q:300:400:q70.webp?dr=14782&refresh_token=5cbaa5e5&x-expires=1785171600&x-signature=Zg1zQ4AppOFWvrVz6mtVoWf0Bbk%3D&t=bacd0480&ps=933b5bde&shp=d05b14bd&shcp=f6441914&idc=my2&biz_tag=tt_video&s=MUSIC_AWEME&sc=cover",
        "author": {
          "username": "babi_batox",
          "displayName": "Loreno_Cavela",
          "url": "https://www.tiktok.com/@babi_batox",
          "verified": false,
          "profileImage": "https://p16-common-sign.tiktokcdn.com/tos-alisg-avt-0068/12b7a3027b147743a04d2dcd50302b61~tplv-tiktokx-cropcenter-q:1080:1080:q70.webp?dr=10796&idc=my2&ps=87d6e48a&refresh_token=06f16ad2&s=MUSIC_AWEME&sc=avatar&shcp=f6441914&shp=d05b14bd&t=223449c4&x-expires=1785171600&x-signature=QOi7%2FEEgi7Th2wcfyTFLX0QLv%2B4%3D"
        },
        "engagement": {
          "views": 2334,
          "likes": 127,
          "comments": 2,
          "saves": 6
        },
        "hashtags": [
          "aprender",
          "khaby",
          "comed",
          "badi_xatox",
          "humor"
        ],
        "musicName": "original sound - khaby.lame"
      },
      {
        "platform": "tiktok",
        "url": "https://www.tiktok.com/@phearinreber8/video/7651833761398689042",
        "id": "7651833761398689042",
        "caption": "រឿងពិតរបស់មនុស្សយើង🫠🫠🫠",
        "description": "រឿងពិតរបស់មនុស្សយើង🫠🫠🫠",
        "publishedAt": "2026-06-16T03:43:08.000Z",
        "durationSeconds": 41.168,
        "thumbnailUrl": "https://p16-common-sign.tiktokcdn.com/tos-alisg-p-0037/oIiQkNnOBDxMxcVwjmFUgYQERAm0LbmfEeBq8M~tplv-tiktokx-cropcenter-q:300:400:q70.webp?dr=14782&refresh_token=0c1a39cf&x-expires=1785171600&x-signature=9yH9ppdfvM1LDk52rO2O6JWFW0g%3D&t=bacd0480&ps=933b5bde&shp=d05b14bd&shcp=f6441914&idc=my2&biz_tag=tt_video&s=MUSIC_AWEME&sc=cover",
        "author": {
          "username": "phearinreber8",
          "displayName": "Justin__IN🇰🇭",
          "url": "https://www.tiktok.com/@phearinreber8",
          "verified": false,
          "profileImage": "https://p16-common-sign.tiktokcdn.com/tos-alisg-avt-0068/f64c2a74679297804805ec188c038ce1~tplv-tiktokx-cropcenter-q:1080:1080:q70.webp?dr=10796&idc=my2&ps=87d6e48a&refresh_token=880d61dc&s=MUSIC_AWEME&sc=avatar&shcp=f6441914&shp=d05b14bd&t=223449c4&x-expires=1785171600&x-signature=hA%2F33ci0JsXHCAb7jN%2F%2B4NtJEio%3D"
        },
        "engagement": {
          "views": 8542,
          "likes": 372,
          "comments": 6,
          "shares": 2,
          "saves": 6
        },
        "musicName": "original sound - khaby.lame"
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
        "engagementRate": 53.998,
        "likes": 1053364775,
        "videos": 1307,
        "country": "US",
        "verified": true,
        "profileImage": "https://p19-common-sign.tiktokcdn-us.com/tos-useast5-avt-0068-tx/fc2aacc9ec77e5e3290fbfda46e40cd2~tplv-tiktokx-cropcenter:1080:1080.jpeg?dr=9640&refresh_token=fdad94e0&x-expires=1785409200&x-signature=jNHL5Y3uuYeocjKv709yl4MyWG8%3D&t=4d5b0474&ps=13740610&shp=a5d48078&shcp=81f88b70&idc=useast8",
        "rank": 1
      },
      {
        "username": "samaraispinkk",
        "displayName": "Secret",
        "url": "https://www.tiktok.com/@samaraispinkk",
        "bio": "I am pink diva mermaid queen and Samara \n💌- Samara@tiddle.io\nSnap is lit",
        "followers": 6173962,
        "engagementRate": 88.8975,
        "likes": 548849706,
        "videos": 1363,
        "country": "US",
        "verified": false,
        "profileImage": "https://p19-common-sign.tiktokcdn-us.com/tos-useast5-avt-0068-tx/a5efb96291b21db624033e417de1efc9~tplv-tiktokx-cropcenter:1080:1080.jpeg?dr=9640&refresh_token=0982d22c&x-expires=1785409200&x-signature=Wu213hPipMQFhk3VhLFyRMdq7D4%3D&t=4d5b0474&ps=13740610&shp=a5d48078&shcp=81f88b70&idc=useast8",
        "rank": 2
      },
      {
        "username": "nicolas_williams9",
        "displayName": "Nicolas_williams9",
        "url": "https://www.tiktok.com/@nicolas_williams9",
        "bio": "Jugador del Athletic club",
        "followers": 6002719,
        "engagementRate": 6.9181,
        "likes": 41527477,
        "videos": 55,
        "country": "US",
        "verified": true,
        "profileImage": "https://p19-common-sign.tiktokcdn-us.com/tos-useast2a-avt-0068-euttp/afecca7121de81afa7afa9f9016d46cf~tplv-tiktokx-cropcenter:1080:1080.jpeg?dr=9640&refresh_token=b3e28c5f&x-expires=1785409200&x-signature=kvobRyEykA4%2Fc%2BECKgkfPI6egqU%3D&t=4d5b0474&ps=13740610&shp=a5d48078&shcp=81f88b70&idc=useast8",
        "rank": 3
      },
      {
        "username": "veranda_main",
        "displayName": "ВЕРАНДА🚀",
        "url": "https://www.tiktok.com/@veranda_main",
        "bio": "Thanks for 2.5 million🚀 \n\nSt.Pb—Sevas\n\nInstagram @veranda_main🥰",
        "followers": 2488445,
        "engagementRate": 13.9131,
        "likes": 34621936,
        "videos": 1030,
        "country": "US",
        "verified": false,
        "profileImage": "https://p16-common-sign.tiktokcdn-us.com/tos-maliva-avt-0068/38958cfd6c3f995abb18f122f769c620~tplv-tiktokx-cropcenter:1080:1080.jpeg?dr=9640&refresh_token=709d2611&x-expires=1785409200&x-signature=r%2BV%2FYznWjwe%2BjO19qu%2F86GpiVxw%3D&t=4d5b0474&ps=13740610&shp=a5d48078&shcp=81f88b70&idc=useast8",
        "rank": 4
      },
      {
        "username": "chat_n_chops",
        "displayName": "Chef Moe",
        "url": "https://www.tiktok.com/@chat_n_chops",
        "bio": "Cash App $chefmoe83\nPayPal.me/chatnchops\nBusiness: chefmoe83@gmail.com",
        "followers": 2367774,
        "engagementRate": 9.9571,
        "likes": 23576279,
        "videos": 632,
        "country": "US",
        "verified": false,
        "profileImage": "https://p16-common-sign.tiktokcdn-us.com/tos-useast5-avt-0068-tx/d740219a74dc104924840c795818067f~tplv-tiktokx-cropcenter:1080:1080.jpeg?dr=9640&refresh_token=3e8c1ddd&x-expires=1785409200&x-signature=2KG%2Bra5PekZo0e3dN%2F70gv%2BCLPk%3D&t=4d5b0474&ps=13740610&shp=a5d48078&shcp=81f88b70&idc=useast8",
        "rank": 5
      }
    ]
  },
  "tiktok-popular-hashtags": {
    "query": "skincare",
    "totalReturned": 10,
    "hashtags": [
      {
        "name": "skincare",
        "url": "https://www.tiktok.com/tag/skincare",
        "rank": 1,
        "videoCount": 17,
        "totalPlays": 40305805
      },
      {
        "name": "skincareroutine",
        "url": "https://www.tiktok.com/tag/skincareroutine",
        "rank": 2,
        "videoCount": 5,
        "totalPlays": 3003805
      }
    ]
  },
  "tiktok-profile-region": {
    "platform": "tiktok",
    "username": "khaby.lame",
    "displayName": "Khabane lame",
    "url": "https://www.tiktok.com/@khaby.lame",
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
      },
      {
        "platform": "tiktok",
        "url": "https://www.tiktok.com/@comedyfunj/video/7295949816234839338",
        "id": "7295949816234839338",
        "caption": "#funnyvideos #funny #indiafunny #trendingfunny #videofunny #sitcomfunny #funnysitcom",
        "description": "#funnyvideos #funny #indiafunny #trendingfunny #videofunny #sitcomfunny #funnysitcom",
        "publishedAt": "2023-10-31T02:51:39.000Z",
        "durationSeconds": 79.0,
        "thumbnailUrl": "https://p16-common-sign.tiktokcdn.com/tos-useast5-p-0068-tx/e93a8ce787c04b99ad162ecaf71e60ac_1698720701~tplv-tiktokx-origin.image?dr=14575&x-expires=1785405600&x-signature=f6xmw0QPK0JnNx5mu6jQGEa%2FZ24%3D&t=4d5b0474&ps=13740610&shp=81f88b70&shcp=43f4a2f9&idc=my",
        "author": {
          "username": "comedyfunj",
          "displayName": "Comedy fun",
          "url": "https://www.tiktok.com/@comedyfunj",
          "followers": 61200,
          "verified": false,
          "profileImage": "https://p16-common-sign.tiktokcdn.com/tos-maliva-avt-0068/1bf62ed982f71c262c52af4641c712e8~tplv-tiktokx-cropcenter:1080:1080.jpeg?dr=14579&refresh_token=d174f855&x-expires=1785405600&x-signature=xBcGo18vBUqAViuVBz6dR69XDuE%3D&t=4d5b0474&ps=13740610&shp=a5d48078&shcp=81f88b70&idc=my"
        },
        "engagement": {
          "views": 11200,
          "likes": 229,
          "comments": 3,
          "shares": 14,
          "saves": 12
        },
        "hashtags": [
          "funnyvideos",
          "funny",
          "indiafunny",
          "trendingfunny",
          "videofunny",
          "sitcomfunny",
          "funnysitcom"
        ],
        "musicName": "nhạc nền"
      },
      {
        "platform": "tiktok",
        "url": "https://www.tiktok.com/@6163864215898comedy/video/6989978097533603073",
        "id": "6989978097533603073",
        "caption": "لايك _كومنت_ فولو _اكسبلور❤️❤️",
        "description": "لايك _كومنت_ فولو _اكسبلور❤️❤️",
        "publishedAt": "2021-07-28T14:05:00.000Z",
        "durationSeconds": 10.0,
        "thumbnailUrl": "https://p16-common-sign.tiktokcdn.com/tos-alisg-p-0037/dcd96fd241734c0a994710e4fbded915~tplv-tiktokx-origin.image?dr=14575&x-expires=1785405600&x-signature=OS%2BgEHBepdyW3q0pFto9MR%2BvfKI%3D&t=4d5b0474&ps=13740610&shp=81f88b70&shcp=43f4a2f9&idc=my",
        "author": {
          "username": "6163864215898comedy",
          "displayName": "comedy😂",
          "url": "https://www.tiktok.com/@6163864215898comedy",
          "followers": 207,
          "verified": false,
          "profileImage": "https://p16-common-sign.tiktokcdn.com/tos-alisg-avt-0068/0c373df8f9081b48a1f838534a9839b3~tplv-tiktokx-cropcenter:1080:1080.jpeg?dr=14579&refresh_token=0fe3b20c&x-expires=1785405600&x-signature=6tKIUsvXDOPENZdUz5zHsAW05nk%3D&t=4d5b0474&ps=13740610&shp=a5d48078&shcp=81f88b70&idc=my"
        },
        "engagement": {
          "views": 22400,
          "likes": 122,
          "comments": 0,
          "shares": 1,
          "saves": 9
        },
        "hashtags": [],
        "musicName": "Oh No"
      },
      {
        "platform": "tiktok",
        "url": "https://www.tiktok.com/@comedyme3/video/7650141917530918151",
        "id": "7650141917530918151",
        "caption": null,
        "description": null,
        "publishedAt": "2026-06-11T14:17:51.000Z",
        "durationSeconds": 29.0,
        "thumbnailUrl": "https://p16-common-sign.tiktokcdn.com/tos-alisg-p-0037/o8rDBeSfGGwoLibRfqIwwbI5qFQIlvsAeAG33A~tplv-tiktokx-origin.image?dr=14575&x-expires=1785405600&x-signature=GSsmcd2SoQYe2K8AdHgoIYHjf7M%3D&t=4d5b0474&ps=13740610&shp=81f88b70&shcp=43f4a2f9&idc=my",
        "author": {
          "username": "comedyme3",
          "displayName": "yethro lhamo",
          "url": "https://www.tiktok.com/@comedyme3",
          "followers": 12000,
          "verified": false,
          "profileImage": "https://p16-common-sign.tiktokcdn.com/tos-alisg-avt-0068/89ff2eefdc81e60070085bba1981ab6c~tplv-tiktokx-cropcenter:1080:1080.jpeg?dr=14579&refresh_token=4209ccea&x-expires=1785405600&x-signature=kwFJWQjXhwCzLGMmgZY7RMqJ2rk%3D&t=4d5b0474&ps=13740610&shp=a5d48078&shcp=81f88b70&idc=my"
        },
        "engagement": {
          "views": 2265,
          "likes": 159,
          "comments": 7,
          "shares": 4,
          "saves": 4
        },
        "hashtags": [],
        "musicName": "original sound - Don🤣"
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
      },
      {
        "seed": "makeup",
        "suggestion": "Makeup brushes",
        "rank": 3,
        "searchUrl": "https://www.tiktok.com/search?q=Makeup+brushes",
        "region": "US",
        "language": "en-US"
      },
      {
        "seed": "makeup",
        "suggestion": "makeup ideas",
        "rank": 4,
        "searchUrl": "https://www.tiktok.com/search?q=makeup+ideas",
        "region": "US",
        "language": "en-US"
      },
      {
        "seed": "makeup",
        "suggestion": "makeup transition",
        "rank": 5,
        "searchUrl": "https://www.tiktok.com/search?q=makeup+transition",
        "region": "US",
        "language": "en-US"
      }
    ]
  },
  "tiktok-search-users": {
    "query": "khaby",
    "totalReturned": 5,
    "hasMore": true,
    "nextCursor": 10,
    "users": [
      {
        "username": "khaby.lame",
        "displayName": "Khabane lame",
        "bio": "Se vuoi ridere sei nel posto giusto😎 If u wanna laugh u r in the right place😎",
        "url": "https://www.tiktok.com/@khaby.lame",
        "followers": 162500000,
        "verified": true,
        "profileImage": "https://p16-common-sign.tiktokcdn.com/tos-maliva-avt-0068/08987e23b94057953fd4f1738694bf5f~tplv-tiktokx-cropcenter:100:100.webp?biz_tag=tiktok_user.user_cover&dr=14579&idc=my2&ps=13740610&refresh_token=6fefdc7e&shcp=c1333099&shp=30310797&t=4d5b0474&x-expires=1785319200&x-signature=QsQ8nkDwkBjSrzbv7JPWg8zjgiA%3D"
      },
      {
        "username": "khabylam206",
        "displayName": "khaby lame",
        "bio": "”Let’s grow together 🚀 — follow + comment = love ❤️”\nContent Creator 🎥 | Promo  Available 📩”",
        "url": "https://www.tiktok.com/@khabylam206",
        "followers": 316400,
        "verified": false,
        "profileImage": "https://p16-common-sign.tiktokcdn.com/tos-maliva-avt-0068/3dd8c5e3598ec508f5768144e7338d10~tplv-tiktokx-cropcenter:100:100.webp?biz_tag=tiktok_user.user_cover&dr=14579&idc=my2&ps=13740610&refresh_token=f4981a82&shcp=c1333099&shp=30310797&t=4d5b0474&x-expires=1785319200&x-signature=gQS2u%2BiKnsbd7abSUpeAumSP8QA%3D"
      },
      {
        "username": "khaby_official_dute_",
        "displayName": "khaby official fan dute",
        "bio": "This is fan dutes account ✌️🤷🏻‍♂️✌️",
        "url": "https://www.tiktok.com/@khaby_official_dute_",
        "followers": 450300,
        "verified": false,
        "profileImage": "https://p16-common-sign.tiktokcdn.com/tos-useast2a-avt-0068-giso/ca094640e72bce422d1828e2309cbc63~tplv-tiktokx-cropcenter:100:100.webp?biz_tag=tiktok_user.user_cover&dr=14579&idc=my2&ps=13740610&refresh_token=ffe8c345&shcp=c1333099&shp=30310797&t=4d5b0474&x-expires=1785319200&x-signature=3RyBiSLuTcJ%2BJwhOTnGDjgdTUCM%3D"
      },
      {
        "username": "dianiskhaby",
        "displayName": "𝕕𝕚𝕒𝕟𝕚𝕤.𝕜𝕙𝕒𝕓𝕪🦋",
        "bio": "✨️🎀 Recilencia 🎀✨🌙",
        "url": "https://www.tiktok.com/@dianiskhaby",
        "followers": 37400,
        "verified": false,
        "profileImage": "https://p16-common-sign.tiktokcdn.com/tos-maliva-avt-0068/92da10b46e4e7ce6f456a633bd7b9f61~tplv-tiktokx-cropcenter:100:100.webp?biz_tag=tiktok_user.user_cover&dr=14579&idc=my2&ps=13740610&refresh_token=7a0d88a4&shcp=c1333099&shp=30310797&t=4d5b0474&x-expires=1785319200&x-signature=fnw5tt3iAAfAL0y%2B6Ywn6nXCAKw%3D"
      },
      {
        "username": "esultareallakhaby",
        "displayName": "Khaby Lame news and edits",
        "bio": "FAN page of @Khabane lame",
        "url": "https://www.tiktok.com/@esultareallakhaby",
        "followers": 310600,
        "verified": false,
        "profileImage": "https://p16-common-sign.tiktokcdn.com/tos-maliva-avt-0068/7a149e5d55f6c0f769c387cc46cb9eeb~tplv-tiktokx-cropcenter:100:100.webp?biz_tag=tiktok_user.user_cover&dr=14579&idc=my2&ps=13740610&refresh_token=72b18cee&shcp=c1333099&shp=30310797&t=4d5b0474&x-expires=1785319200&x-signature=6980Ya2hKmjsenjIQtlIzY%2FB6ZE%3D"
      }
    ]
  },
  "tiktok-shop-product-details": {
    "platform": "tiktok_shop",
    "id": "1731098552908944370",
    "url": "https://shop.tiktok.com/us/pdp/trendy-pink-ed-hardy-tough-phone-cases-impact-resistant-wireless-charging-shock-absorption/1731098552908944370?source=product_detail&enter_method=url_semantic_301",
    "title": "Trendy Pink Ed Hardy Inspired Tough Phone Cases, Phone Durable, Gift, Accessories Top Trendy Phone Cases Phone Cover Hard Case Tough 2-piece Phone Case",
    "price": 10.3,
    "currency": "USD",
    "rating": 4.6,
    "reviews": 48,
    "sold": 1488,
    "stock": 2693,
    "image": "https://p16-oec-general-useast5.ttcdn-us.com/tos-useast5-i-omjb5zjo8w-tx/cc79ccfd6a324d548de31cb761b6c3c4~tplv-fhlh96nyum-crop-webp:794:794.webp?dr=12190&t=555f072d&ps=933b5bde&shp=8dbd94bf&shcp=e1be8f53&idc=useast5&from=2378011839",
    "seller": {
      "name": "Timeless Teapot Creations",
      "rating": 4.6
    }
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
        "createdAt": "2026-05-15T21:49:56.991000+00:00",
        "verifiedPurchase": true,
        "sku": "Thicc 16oz | Ice Cream",
        "country": "US",
        "author": {
          "name": "C**e"
        },
        "images": [
          "https://p16-oec-general-useast5.ttcdn-us.com/tos-useast5-i-omjb5zjo8w-tx/bc7a80f5766e438e8698430bdff2b55c~tplv-fhlh96nyum-crop-webp:300:300.webp?dr=12190&t=555f072d&ps=933b5bde&shp=8dbd94bf&shcp=607f11de&idc=useast5&from=2378011839",
          "https://p19-oec-general-useast5.ttcdn-us.com/tos-useast5-i-omjb5zjo8w-tx/7c513b397e2f4b019995d95dd7506914~tplv-fhlh96nyum-crop-webp:300:300.webp?dr=12190&t=555f072d&ps=933b5bde&shp=8dbd94bf&shcp=607f11de&idc=useast5&from=2378011839",
          "https://p16-oec-general-useast5.ttcdn-us.com/tos-useast5-i-omjb5zjo8w-tx/2fcfd52f6a694575974084d055c318a6~tplv-fhlh96nyum-crop-webp:300:300.webp?dr=12190&t=555f072d&ps=933b5bde&shp=8dbd94bf&shcp=607f11de&idc=useast5&from=2378011839",
          "https://p19-oec-general-useast5.ttcdn-us.com/tos-useast5-i-omjb5zjo8w-tx/b5cf78b2ce824b329bba9a0a1e2a9fbb~tplv-fhlh96nyum-crop-webp:300:300.webp?dr=12190&t=555f072d&ps=933b5bde&shp=8dbd94bf&shcp=607f11de&idc=useast5&from=2378011839"
        ]
      },
      {
        "platform": "tiktok_shop",
        "id": "7599033354029254413",
        "rating": 4,
        "text": "This cup is indeed visually appealing. Although it does exhibit some minor flaws, specifically where the 'frost buddy' wording is engraved into the cup and the logo is not included on the engraving on the opposite side, overall it is a well-made cup. I am satisfied with my purchase.",
        "createdAt": "2026-01-24T20:50:51.887000+00:00",
        "verifiedPurchase": true,
        "sku": "To-Go | Duck-It",
        "country": "US",
        "author": {
          "name": "M**e"
        },
        "images": [
          "https://p16-oec-general-useast5.ttcdn-us.com/tos-useast5-i-omjb5zjo8w-tx/c51c9bdf430e4991aaa5d947300410de~tplv-fhlh96nyum-crop-webp:300:300.webp?dr=12190&t=555f072d&ps=933b5bde&shp=8dbd94bf&shcp=607f11de&idc=useast5&from=2378011839",
          "https://p16-oec-general-useast5.ttcdn-us.com/tos-useast5-i-omjb5zjo8w-tx/f3ef2a7c10ec4dc7bd3446c373868f7e~tplv-fhlh96nyum-crop-webp:300:300.webp?dr=12190&t=555f072d&ps=933b5bde&shp=8dbd94bf&shcp=607f11de&idc=useast5&from=2378011839",
          "https://p16-oec-general-useast5.ttcdn-us.com/tos-useast5-i-omjb5zjo8w-tx/6b1f7a234b4d4016b7b7ed9401132223~tplv-fhlh96nyum-crop-webp:300:300.webp?dr=12190&t=555f072d&ps=933b5bde&shp=8dbd94bf&shcp=607f11de&idc=useast5&from=2378011839",
          "https://p16-oec-general-useast5.ttcdn-us.com/tos-useast5-i-omjb5zjo8w-tx/09ca5668b59b4770beb90dc8b735a83c~tplv-fhlh96nyum-crop-webp:300:300.webp?dr=12190&t=555f072d&ps=933b5bde&shp=8dbd94bf&shcp=607f11de&idc=useast5&from=2378011839"
        ]
      },
      {
        "platform": "tiktok_shop",
        "id": "7643464524599723789",
        "rating": 5,
        "text": "Fast delivery! Purchased as a gift! Love the lilac color!",
        "createdAt": "2026-05-24T14:26:17.644000+00:00",
        "verifiedPurchase": true,
        "sku": "Thicc 40oz | Lavender Fields",
        "country": "US",
        "author": {
          "name": "i**u"
        },
        "images": [
          "https://p16-oec-general-useast5.ttcdn-us.com/tos-useast5-i-omjb5zjo8w-tx/3dbcc73d208c46bfb1ef5e6cb74fe593~tplv-fhlh96nyum-crop-webp:300:300.webp?dr=12190&t=555f072d&ps=933b5bde&shp=8dbd94bf&shcp=607f11de&idc=useast5&from=2378011839",
          "https://p19-oec-general-useast5.ttcdn-us.com/tos-useast5-i-omjb5zjo8w-tx/b3d3128fff1f4872a913652a6d6827da~tplv-fhlh96nyum-crop-webp:300:300.webp?dr=12190&t=555f072d&ps=933b5bde&shp=8dbd94bf&shcp=607f11de&idc=useast5&from=2378011839",
          "https://p19-oec-general-useast5.ttcdn-us.com/tos-useast5-i-omjb5zjo8w-tx/7cb7186b70c94b93af0aa7f66f227554~tplv-fhlh96nyum-crop-webp:300:300.webp?dr=12190&t=555f072d&ps=933b5bde&shp=8dbd94bf&shcp=607f11de&idc=useast5&from=2378011839"
        ]
      }
    ]
  },
  "tiktok-shop-products": {
    "url": "https://www.tiktok.com/shop/store/goli-nutrition/7495794203056835079",
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
        "rating": 4.5,
        "reviews": 94266,
        "sold": 1295902,
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
        "rating": 4.5,
        "reviews": 45933,
        "sold": 984345,
        "image": "https://p16-oec-general-useast5.ttcdn-us.com/tos-useast5-i-omjb5zjo8w-tx/c347c31449564ea4a0300adb2d0cdaa9~tplv-fhlh96nyum-crop-webp:1500:1500.webp?dr=12190&t=555f072d&ps=933b5bde&shp=8dbd94bf&shcp=a6e80448&idc=useast5&from=2378011839",
        "seller": {
          "id": "7495794203056835079",
          "name": "Goli Nutrition",
          "url": "https://www.tiktok.com/shop/store/goli-nutrition/7495794203056835079"
        }
      },
      {
        "platform": "tiktok_shop",
        "id": "1729587769570529799",
        "url": "https://www.tiktok.com/shop/pdp/goli-ashwagandha-gummies-with-vitamin-d-ksm-66-vegan-non-gmo/1729587769570529799",
        "title": "3 Bottles of Goli Ashwagandha & Vitamin D Gummy - Mixed Berry, KSM-66, Vegan, Plant Based, Non-GMO, Gluten & Gelatin Free",
        "price": 44.98,
        "originalPrice": 57.0,
        "currency": "USD",
        "discount": "21%",
        "rating": 4.7,
        "reviews": 71655,
        "sold": 861565,
        "image": "https://p16-oec-general-useast5.ttcdn-us.com/tos-useast5-i-omjb5zjo8w-tx/b0d9acd7ae184c8d89e2e498941485b6~tplv-fhlh96nyum-crop-webp:1500:1500.webp?dr=12190&t=555f072d&ps=933b5bde&shp=8dbd94bf&shcp=a6e80448&idc=useast5&from=2378011839",
        "seller": {
          "id": "7495794203056835079",
          "name": "Goli Nutrition",
          "url": "https://www.tiktok.com/shop/store/goli-nutrition/7495794203056835079"
        }
      },
      {
        "platform": "tiktok_shop",
        "id": "1729589345444205063",
        "url": "https://www.tiktok.com/shop/pdp/goli-new-year-bundle-ashwagandha-apple-cider-vinegar-matcha-mind/1729589345444205063",
        "title": "3 Bottles of Goli Best Seller Bundle: Ashwagandha KSM-66, Apple Cider Vinegar, Matcha Mind supplement with Cognizin, Vitamins D2 and B12",
        "price": 32.8,
        "originalPrice": 74.97,
        "currency": "USD",
        "discount": "56%",
        "rating": 4.6,
        "reviews": 40190,
        "sold": 545614,
        "image": "https://p19-oec-general-useast5.ttcdn-us.com/tos-useast5-i-omjb5zjo8w-tx/7a85d8aa9e2c4faab75a09fd9e5bff42~tplv-fhlh96nyum-crop-webp:1500:1500.webp?dr=12190&t=555f072d&ps=933b5bde&shp=8dbd94bf&shcp=a6e80448&idc=useast5&from=2378011839",
        "seller": {
          "id": "7495794203056835079",
          "name": "Goli Nutrition",
          "url": "https://www.tiktok.com/shop/store/goli-nutrition/7495794203056835079"
        }
      },
      {
        "platform": "tiktok_shop",
        "id": "1729527774874997255",
        "url": "https://www.tiktok.com/shop/pdp/gummy-pre-post-probiotics-by-goli-nutrition-vegan-gluten-free-formula/1729527774874997255",
        "title": "Goli Pre, Post, Probiotics Gummy - World's First 3-in-1 Gluten-Free, Vegan, Non-GMO, and Gelatin-Free.",
        "price": 14.98,
        "originalPrice": 19.0,
        "currency": "USD",
        "discount": "21%",
        "rating": 4.5,
        "reviews": 11787,
        "sold": 205636,
        "image": "https://p16-oec-general-useast5.ttcdn-us.com/tos-useast5-i-omjb5zjo8w-tx/3939c5be64484010b5c2a3183ecfbec3~tplv-fhlh96nyum-crop-webp:3000:3000.webp?dr=12190&t=555f072d&ps=933b5bde&shp=8dbd94bf&shcp=a6e80448&idc=useast5&from=2378011839",
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
        "reviews": 2493
      },
      {
        "platform": "tiktok_shop",
        "id": "1731098552908944370",
        "url": "https://shop.tiktok.com/us/pdp/trendy-pink-ed-hardy-tough-phone-cases-impact-resistant-wireless-charging-shock-absorption/1731098552908944370?source=product_detail&enter_method=url_semantic_301",
        "title": "Trendy Pink Ed Hardy Inspired Tough Phone Cases",
        "price": 11.21,
        "originalPrice": 24.91,
        "currency": "USD",
        "discount": "55%",
        "sold": 1488,
        "image": "https://p16-oec-general-useast5.ttcdn-us.com/tos-useast5-i-omjb5zjo8w-tx/cc79ccfd6a324d548de31cb761b6c3c4~tplv-fhlh96nyum-crop-webp:794:794.webp?dr=12190&t=555f072d&ps=933b5bde&shp=8dbd94bf&shcp=607f11de&idc=useast5&from=2378011839",
        "seller": {
          "id": "7496126292994264050",
          "name": "Timeless Teapot Creations",
          "url": "https://www.tiktok.com/shop/store/Timeless%20Teapot%20Creations/7496126292994264050"
        }
      },
      {
        "platform": "tiktok_shop",
        "id": "1732210224209891836",
        "url": "https://shop.tiktok.com/us/pdp/high-end-iphone-16-case-with-four-leaf-clover-lanyard-butterfly-pattern/1732210224209891836?source=product_detail&enter_method=url_semantic_301",
        "title": "Suitable for [iPhone 16] high-end phone case，a beautiful four-leaf clover lanyard is included,exquisite and dreamy butterfly pattern,a variety of colors are available for you to choose from YM99",
        "price": 14.0,
        "originalPrice": 17.88,
        "currency": "USD",
        "discount": "22%",
        "sold": 314495,
        "image": "https://p16-oec-general-useast5.ttcdn-us.com/tos-useast5-i-omjb5zjo8w-tx/a92993fc7a2242d9aca2322aac7cdaf6~tplv-fhlh96nyum-crop-webp:800:800.webp?dr=12190&t=555f072d&ps=933b5bde&shp=8dbd94bf&shcp=e1be8f53&idc=useast5&from=2378011839",
        "seller": {
          "id": "7495991409431644668",
          "name": "LIBAI-USA1",
          "url": "https://www.tiktok.com/shop/store/LIBAI-USA1/7495991409431644668"
        }
      },
      {
        "platform": "tiktok_shop",
        "id": "1732445435684229466",
        "url": "https://shop.tiktok.com/us/pdp/1732445435684229466",
        "title": "Wine Cherry Pattern iPhone Case Shockproof TPU Cover",
        "price": 7.1,
        "originalPrice": null,
        "currency": "USD",
        "discount": null,
        "sold": 3480,
        "image": "https://p16-oec-general-useast5.ttcdn-us.com/tos-useast5-i-omjb5zjo8w-tx/a26a3efec0ef48b6bb663fdee15deac9~tplv-fhlh96nyum-crop-webp:800:800.webp?dr=12190&t=555f072d&ps=933b5bde&shp=8dbd94bf&shcp=607f11de&idc=useast5&from=2378011839",
        "seller": {
          "id": "7496146286741784922",
          "name": "Cover Farm",
          "url": "https://www.tiktok.com/shop/store/Cover%20Farm/7496146286741784922"
        }
      },
      {
        "platform": "tiktok_shop",
        "id": "1732319524515713953",
        "url": "https://shop.tiktok.com/us/pdp/oppo-reno14-f-5g-phone-case-durable-stylish-matte-finish/1732319524515713953?source=product_detail&enter_method=url_semantic_301",
        "title": "For OPPO Reno14 F 5G phone case, durable protective case, stylish phone accessories, matte colored phone case, simple matte appearance. Protective and anti drop phone case, available in multiple colors",
        "price": 3.36,
        "originalPrice": null,
        "currency": "USD",
        "discount": null,
        "sold": 67,
        "image": "https://p16-oec-general-useast5.ttcdn-us.com/tos-useast5-i-omjb5zjo8w-tx/60a6605d5c9348a8841b4ec949ad8534~tplv-fhlh96nyum-crop-webp:800:800.webp?dr=12190&t=555f072d&ps=933b5bde&shp=8dbd94bf&shcp=607f11de&idc=useast5&from=2378011839",
        "seller": {
          "id": "8652615240597738401",
          "name": "JiaRongHui Store",
          "url": "https://www.tiktok.com/shop/store/JiaRongHui%20Store/8652615240597738401"
        }
      }
    ]
  },
  "tiktok-shop-user-showcase": {
    "username": "jeffreestar",
    "totalReturned": 5,
    "products": [
      {
        "platform": "tiktok_shop",
        "id": "1732348343936586686",
        "url": "https://www.tiktok.com/shop/pdp/1732348343936586686",
        "title": "Oganacell PDRN Peptide Gua Sha Calming Gel Cream for Soothing & Barrier Care, Jawline Definition, Face Sculpting & De-Puffing, Firming & Elasticity Care for Sensitive Skin, At-Home Facial Care | Korean Skincare",
        "price": 27.99,
        "currency": "USD",
        "image": "https://p19-oec-general-useast5.ttcdn-us.com/tos-useast5-i-omjb5zjo8w-tx/c29c24ff8dae4649a711659e1b425b0d~tplv-fhlh96nyum-crop-webp:500:500.webp?dr=12190&t=555f072d&ps=933b5bde&shp=4ee6669e&shcp=9b759fb9&idc=useast5&from=1323722398",
        "seller": {
          "id": "7496114058180594622"
        }
      },
      {
        "platform": "tiktok_shop",
        "id": "1732465688971547582",
        "url": "https://www.tiktok.com/shop/pdp/1732465688971547582",
        "title": "[Creator Exclusive] Oganacell PDRN Peptide Gua Sha Lifting Gel Cream for Jawline Definition, Face Sculpting & De-Puffing, Firming & Elasticity Care for Dry and Sagging Skin, Glass Skin Glow, At-Home Facial Care | Korean Skincare",
        "price": 59.6,
        "currency": "USD",
        "image": "https://p19-oec-general-useast5.ttcdn-us.com/tos-useast5-i-omjb5zjo8w-tx/61d153b0cdde4002abf5b41ab5f90e8c~tplv-fhlh96nyum-crop-webp:500:500.webp?dr=12190&t=555f072d&ps=933b5bde&shp=4ee6669e&shcp=9b759fb9&idc=useast5&from=1323722398",
        "seller": {
          "id": "7496114058180594622"
        }
      },
      {
        "platform": "tiktok_shop",
        "id": "1732497823331554245",
        "url": "https://www.tiktok.com/shop/pdp/1732497823331554245",
        "title": "Heavy Metal Couture Artistry Bundle - 6PC Eye Brush Set, Heavy Metal Couture 9-Pan Palette, BeachProof Eyeliner 'Tattooed Devil' & 'Grave Digger', BeachProof Mascara 'Black'",
        "price": 119.85,
        "currency": "USD",
        "image": "https://p16-oec-general-useast5.ttcdn-us.com/tos-useast5-i-omjb5zjo8w-tx/bfabe84ca345416eb5324ca7e0a484d2~tplv-fhlh96nyum-crop-webp:500:500.webp?dr=12190&t=555f072d&ps=933b5bde&shp=4ee6669e&shcp=9b759fb9&idc=useast5&from=1323722398",
        "seller": {
          "id": "7494986018328054725"
        }
      },
      {
        "platform": "tiktok_shop",
        "id": "1732497709724832709",
        "url": "https://www.tiktok.com/shop/pdp/1732497709724832709",
        "title": "The Stage Ready Set - Magic Star Mushroom Mist, BeachProof Eyeliner 'Tattooed Devil' & 'Grave Digger', Lip Balm 'Encore' & 'Unicorn Blood'",
        "price": 100.3,
        "currency": "USD",
        "image": "https://p16-oec-general-useast5.ttcdn-us.com/tos-useast5-i-omjb5zjo8w-tx/8791aba9197e44ebb883a768f7d177e1~tplv-fhlh96nyum-crop-webp:500:500.webp?dr=12190&t=555f072d&ps=933b5bde&shp=4ee6669e&shcp=9b759fb9&idc=useast5&from=1323722398",
        "seller": {
          "id": "7494986018328054725"
        }
      },
      {
        "platform": "tiktok_shop",
        "id": "1732497708784587717",
        "url": "https://www.tiktok.com/shop/pdp/1732497708784587717",
        "title": "Heavy Metal Couture Mini Palette - 9-pan Mattes & Shimmer/Metallic Eyeshadow Shades - Preorder",
        "price": 32.0,
        "currency": "USD",
        "image": "https://p16-oec-general-useast5.ttcdn-us.com/tos-useast5-i-omjb5zjo8w-tx/190744ec28fa4cc99274a7aec07cdeff~tplv-fhlh96nyum-crop-webp:500:500.webp?dr=12190&t=555f072d&ps=933b5bde&shp=4ee6669e&shcp=9b759fb9&idc=useast5&from=1323722398",
        "seller": {
          "id": "7494986018328054725"
        }
      }
    ]
  },
  "tiktok-song-details": {
    "platform": "tiktok",
    "url": "https://www.tiktok.com/music/original-sound-7646812079113898783",
    "id": "7646812079113898783",
    "title": "original sound - khaby.lame",
    "author": "Khabane lame",
    "original": true,
    "album": null,
    "duration": 29.0,
    "coverUrl": "https://p16-common-sign.tiktokcdn.com/tos-maliva-avt-0068/08987e23b94057953fd4f1738694bf5f~tplv-tiktokx-cropcenter-q:1080:1080:q70.webp?dr=10796&idc=my&ps=87d6e48a&refresh_token=765a9f29&s=MUSIC_AWEME&sc=avatar&shcp=f6441914&shp=d05b14bd&t=223449c4&x-expires=1785315600&x-signature=8LI4%2BlUJaaW%2FwmqFRm1LaQGCx%2FY%3D",
    "playUrl": "https://sf16-ies-music-va.tiktokcdn.com/obj/ies-music-ttp-dup-us/tx27650420977368582943.mp3"
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
          "profileImage": "https://p16-common-sign.tiktokcdn-us.com/tos-maliva-avt-0068/9b1bc4bbfedb3bd917a27ff590234ca0~tplv-tiktokx-cropcenter:1080:1080.jpeg?dr=9640&refresh_token=97b8bbe5&x-expires=1785517200&x-signature=1ZGx4llDfPF1ly3oJa0XsXinyoY%3D&t=4d5b0474&ps=13740610&shp=a5d48078&shcp=81f88b70&idc=useast5"
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
          "informaciónparati",
          "Latinus",
          "InformaciónParaTi"
        ],
        "musicName": "original sound - Latinus"
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
          "profileImage": "https://p16-common-sign.tiktokcdn-us.com/tos-useast2a-avt-0068-euttp/fbdd74ed519afa76388646251f24ded1~tplv-tiktokx-cropcenter:1080:1080.jpeg?dr=9640&refresh_token=6f41b39b&x-expires=1785517200&x-signature=vpJCW3%2B4khpTq%2FDSdGTddKAFRPk%3D&t=4d5b0474&ps=13740610&shp=a5d48078&shcp=81f88b70&idc=useast5"
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
          "artemis2",
          "fy",
          "fyp",
          "fyptt"
        ],
        "musicName": "sonido original"
      },
      {
        "platform": "tiktok",
        "url": "https://www.tiktok.com/@nasa/video/7665775952454061326",
        "id": "7665775952454061326",
        "caption": "Mission accomplished.     On April 10, 2026, the Artemis II crew safely returned to Earth after a 10-day journey around the Moon, splashing down off the California coast. 🌎",
        "description": "Mission accomplished.     On April 10, 2026, the Artemis II crew safely returned to Earth after a 10-day journey around the Moon, splashing down off the California coast. 🌎",
        "publishedAt": "2026-07-23T17:26:20.000Z",
        "durationSeconds": 36.0,
        "thumbnailUrl": "https://p19-common-sign.tiktokcdn-us.com/tos-useast5-p-0068-tx/ok5iHxgYfAI772ZXADRqcrBpTEDSFEK3fk8IY1~tplv-tiktokx-origin.image?dr=9636&x-expires=1785517200&x-signature=9L4vadOW5auReX39p9TTdHmWw%2Fw%3D&t=4d5b0474&ps=13740610&shp=81f88b70&shcp=43f4a2f9&idc=useast5",
        "author": {
          "username": "nasa",
          "displayName": "NASA",
          "url": "https://www.tiktok.com/@nasa",
          "followers": 305800,
          "verified": true,
          "profileImage": "https://p19-common-sign.tiktokcdn-us.com/tos-useast5-avt-0068-tx/e5143212a59c09a008bf50f487d54d1f~tplv-tiktokx-cropcenter:1080:1080.jpeg?dr=9640&refresh_token=573cc2c1&x-expires=1785517200&x-signature=VsELKHyBLl0thL%2FtAwlBnrOsPzQ%3D&t=4d5b0474&ps=13740610&shp=a5d48078&shcp=81f88b70&idc=useast5"
        },
        "engagement": {
          "views": 127200,
          "likes": 5846,
          "comments": 139,
          "shares": 61,
          "saves": 539
        },
        "musicName": "original sound"
      },
      {
        "platform": "tiktok",
        "url": "https://www.tiktok.com/@astrokobi/video/7667293385178270998",
        "id": "7667293385178270998",
        "caption": "China’s Rocket just got STRUCK BY LIGHTNING #space #nasa #china #rocket #astrokobi",
        "description": "China’s Rocket just got STRUCK BY LIGHTNING #space #nasa #china #rocket #astrokobi",
        "publishedAt": "2026-07-27T19:34:20.000Z",
        "durationSeconds": 68.0,
        "thumbnailUrl": "https://p19-common-sign.tiktokcdn-us.com/tos-no1a-p-0037-no/oATsrBh419CRTg1nA6iiwyBUCMAIR4cIIVv4ye~tplv-tiktokx-dmt-logom:tos-no1a-i-0068-no/o8BiksDrEh0CSzMBWntBfCLIldAiAA9wA5G1I4.image?dr=9634&x-expires=1785517200&x-signature=xnwkLDp1%2FMiV5%2FZEL%2Bu5DMqGS0c%3D&t=4d5b0474&ps=13740610&shp=81f88b70&shcp=43f4a2f9&idc=useast5",
        "author": {
          "username": "astrokobi",
          "displayName": "AstroKobi",
          "url": "https://www.tiktok.com/@astrokobi",
          "followers": 3100000,
          "verified": false,
          "profileImage": "https://p16-common-sign.tiktokcdn-us.com/tos-alisg-avt-0068/975e8c09236aff1c5b7d93b89c178a37~tplv-tiktokx-cropcenter:1080:1080.jpeg?dr=9640&refresh_token=340fcfa3&x-expires=1785517200&x-signature=1YbxI2murKyQ6YRmBU0KewhMWL4%3D&t=4d5b0474&ps=13740610&shp=a5d48078&shcp=81f88b70&idc=useast5"
        },
        "engagement": {
          "views": 228900,
          "likes": 42900,
          "comments": 283,
          "shares": 1104,
          "saves": 3558
        },
        "hashtags": [
          "space",
          "nasa",
          "china",
          "rocket",
          "astrokobi"
        ],
        "musicName": "Everything In Its Right Place"
      },
      {
        "platform": "tiktok",
        "url": "https://www.tiktok.com/@nasa/video/7665725247332601118",
        "id": "7665725247332601118",
        "caption": "You’re listening to one of the sounds the Artemis II crew heard on the eve of splashing down on Earth. That steady knocking isn’t a problem, it’s Orion’s reentry thrusters firing in short, precise bursts to keep the spacecraft on the correct path at nearly 25,000 mph through Earth’s atmosphere.",
        "description": "You’re listening to one of the sounds the Artemis II crew heard on the eve of splashing down on Earth. That steady knocking isn’t a problem, it’s Orion’s reentry thrusters firing in short, precise bursts to keep the spacecraft on the correct path at nearly 25,000 mph through Earth’s atmosphere.",
        "publishedAt": "2026-07-23T14:09:41.000Z",
        "durationSeconds": 16.0,
        "thumbnailUrl": "https://p19-common-sign.tiktokcdn-us.com/tos-useast8-p-0068-tx2/os18qBiPEAUIRAiIwiKI0KdBTMCAAWfhkBIBiI~tplv-tiktokx-origin.image?dr=9636&x-expires=1785517200&x-signature=7Ebgeeo8FYL58CUHPtyylYnVMPY%3D&t=4d5b0474&ps=13740610&shp=81f88b70&shcp=43f4a2f9&idc=useast5",
        "author": {
          "username": "nasa",
          "displayName": "NASA",
          "url": "https://www.tiktok.com/@nasa",
          "followers": 305800,
          "verified": true,
          "profileImage": "https://p19-common-sign.tiktokcdn-us.com/tos-useast5-avt-0068-tx/e5143212a59c09a008bf50f487d54d1f~tplv-tiktokx-cropcenter:1080:1080.jpeg?dr=9640&refresh_token=573cc2c1&x-expires=1785517200&x-signature=VsELKHyBLl0thL%2FtAwlBnrOsPzQ%3D&t=4d5b0474&ps=13740610&shp=a5d48078&shcp=81f88b70&idc=useast5"
        },
        "engagement": {
          "views": 5900000,
          "likes": 367800,
          "comments": 3883,
          "shares": 6882,
          "saves": 25400
        },
        "musicName": "original sound"
      }
    ]
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
        "title": "#gta #viral #fyp",
        "coverUrl": "https://p19-common-sign.tiktokcdn-us.com/tos-useast8-p-0068-tx2/oERcgNIQQgASfTiefnLoipqrkyeCfiAGGKmNEI~tplv-tiktokx-origin.image?dr=9636&x-expires=1785517200&x-signature=FF%2Fhr528f3arMCaHqCr9%2BeBIue0%3D&t=4d5b0474&ps=13740610&shp=81f88b70&shcp=43f4a2f9&idc=useast5",
        "author": "adamjones73",
        "authorName": "Adam",
        "views": 5400000,
        "likes": 823500,
        "comments": 4301,
        "shares": 147900,
        "rank": 1
      },
      {
        "url": "https://www.tiktok.com/@123court/video/7655473367125855519",
        "id": "7655473367125855519",
        "title": "Engaged Mom Demands More Money, But Judge Finds Out The Shocking Truth! ​#CourtroomDrama  ​#FamilyCourt  ​#ChildSupport  ​#ChildSupportCourt  ​#JudgeJules   ​#InstantKarma  ​#Backfired  ​#CaughtInTheAct  ​#PlotTwist  ​#TruckDriverLife  ​#CoParenting  ​#SplitCustody  ​#SiblingDrama  ​#RevengeBackfires",
        "coverUrl": "https://p19-common-sign.tiktokcdn-us.com/tos-useast8-p-0068-tx2/oIMffQHCCga9fWiRXUy8JOfP3WVUFGAL7oQtAQ~tplv-tiktokx-origin.image?dr=9636&x-expires=1785517200&x-signature=zF4ZAiNfBFLlLm4zu51g3NjykhI%3D&t=4d5b0474&ps=13740610&shp=81f88b70&shcp=43f4a2f9&idc=useast5",
        "author": "123court",
        "authorName": "123 Court",
        "views": 3600000,
        "likes": 133800,
        "comments": 1872,
        "shares": 8999,
        "rank": 2
      },
      {
        "url": "https://www.tiktok.com/@nona_avantgardey/video/7663779068713716999",
        "id": "7663779068713716999",
        "title": "Am I bad? 😎 #ateez #BAD @ATEEZ_Official  #avantgardey #アバンギャルディ　@アバンギャルディ avantgardey",
        "coverUrl": "https://p19-common-sign.tiktokcdn-us.com/tos-alisg-p-0037/ooBsEKiBAVPAa2xAN1ZbC6aInAiQGIALdfBLOw~tplv-tiktokx-origin.image?dr=9636&x-expires=1785517200&x-signature=qHhLm6d5aTpwOto77KPfN0WuwDM%3D&t=4d5b0474&ps=13740610&shp=81f88b70&shcp=43f4a2f9&idc=useast5",
        "author": "nona_avantgardey",
        "authorName": "nona",
        "views": 14100000,
        "likes": 2300000,
        "comments": 9659,
        "shares": 66000,
        "rank": 3
      },
      {
        "url": "https://www.tiktok.com/@makaylaamerie/video/7652874384415198477",
        "id": "7652874384415198477",
        "title": "I actually can’t believe I’m starting to get more colostrum 😭 it gets me so emotional how amazing our bodies are🫶🏻 #pregnant #thirdtrimester #realistic #morningvlog",
        "coverUrl": "https://p16-common-sign.tiktokcdn-us.com/tos-useast5-p-0068-tx/oEfLQQsmfGAv43AeAeLEcNRADi6ANSiogSeNRI~tplv-tiktokx-origin.image?dr=9636&x-expires=1785517200&x-signature=R5L4SSmr5qN8UFkQCCe3RUeSm6c%3D&t=4d5b0474&ps=13740610&shp=81f88b70&shcp=43f4a2f9&idc=useast5",
        "author": "makaylaamerie",
        "authorName": "Makayla Marie",
        "views": 903500,
        "likes": 100100,
        "comments": 265,
        "shares": 531,
        "rank": 4
      },
      {
        "url": "https://www.tiktok.com/@evangoesoutside/video/7659618552965516557",
        "id": "7659618552965516557",
        "title": "#fishing #bassfishing #fishtok #fishingtiktoks #fishingvideos",
        "coverUrl": "https://p16-common-sign.tiktokcdn-us.com/tos-useast5-p-0068-tx/oQ1tbOURBb6iaiXExl4AHbIjMI9BikcgknBpP~tplv-tiktokx-dmt-logom:tos-useast5-i-0068-tx/o8EAMqiEbCGAngRc1DIABFED6bDxKTAQffRUpS.image?dr=9634&x-expires=1785517200&x-signature=LGactg2Cv1hUKkezEeVESGkzgjE%3D&t=4d5b0474&ps=13740610&shp=81f88b70&shcp=43f4a2f9&idc=useast5",
        "author": "evangoesoutside",
        "authorName": "EvanGoesFishing",
        "views": 7600000,
        "likes": 718500,
        "comments": 1468,
        "shares": 96600,
        "rank": 5
      }
    ]
  },
  "tiktok-user-followers": {
    "url": "https://www.tiktok.com/@khaby.lame",
    "totalReturned": 5,
    "followers": [
      {
        "username": "abdullah007a3",
        "displayName": "𝄢 ⃝ᶦᵗᶻ•abdullah 亗",
        "bio": "/ মানুষকে বোঝা কঠিন -\nআর বোঝানো তো অসম্ভব..!🖤",
        "url": "https://www.tiktok.com/@abdullah007a3",
        "followers": 17500,
        "following": 6,
        "verified": false,
        "profileImage": "https://p16-common-sign.tiktokcdn.com/tos-alisg-avt-0068/ff95fdfeca275eed2d2984d618a10530~tplv-tiktokx-cropcenter:1080:1080.jpeg?dr=14579&refresh_token=d7015725&x-expires=1785405600&x-signature=Zs92egTgumV89yLzYImuFHbHTrI%3D&t=4d5b0474&ps=13740610&shp=a5d48078&shcp=81f88b70&idc=my2"
      },
      {
        "username": "hawulet97",
        "displayName": "ሀያት",
        "bio": null,
        "url": "https://www.tiktok.com/@hawulet97",
        "followers": 41,
        "following": 1239,
        "verified": false,
        "profileImage": "https://p19-common-sign.tiktokcdn.com/tos-alisg-avt-0068/5acdd487480e04ffe37f451a62fa134d~tplv-tiktokx-cropcenter:1080:1080.jpeg?dr=14579&refresh_token=9e5f5d27&x-expires=1785405600&x-signature=r06fBPyezVcEOXYXR%2Fn5PrC0kQc%3D&t=4d5b0474&ps=13740610&shp=a5d48078&shcp=81f88b70&idc=my2"
      },
      {
        "username": "junaid_jutt924",
        "displayName": "𝙅𝙪𝙣𝙖𝙞𝙙 𝙟𝙪𝙩𝙩 ✅",
        "bio": "My WhatsApp number 03460250924",
        "url": "https://www.tiktok.com/@junaid_jutt924",
        "followers": 3043,
        "following": 3112,
        "verified": false,
        "profileImage": "https://p16-common-sign.tiktokcdn.com/tos-alisg-avt-0068/6508ca9751f0e8020ec9fb28eb06e5d8~tplv-tiktokx-cropcenter:1080:1080.jpeg?dr=14579&refresh_token=f71c169a&x-expires=1785405600&x-signature=vnT49tPcbFXKRRKIbNvOzcLpiQ4%3D&t=4d5b0474&ps=13740610&shp=a5d48078&shcp=81f88b70&idc=my2"
      },
      {
        "username": "kingllamadas2",
        "displayName": "KingLlamadas",
        "bio": "📲Contexto y Moradito🟣",
        "url": "https://www.tiktok.com/@kingllamadas2",
        "followers": 25,
        "following": 20,
        "verified": false,
        "profileImage": "https://p16-common-sign.tiktokcdn.com/tos-alisg-avt-0068/34ffc6b458ca7d2fbbaf2c5c99df5136~tplv-tiktokx-cropcenter:1080:1080.jpeg?dr=14579&refresh_token=94dc3240&x-expires=1785405600&x-signature=maO7t5UP5bAof%2BIztbSx2q7XAj8%3D&t=4d5b0474&ps=13740610&shp=a5d48078&shcp=81f88b70&idc=my2"
      },
      {
        "username": "farukkolapo",
        "displayName": "afolabi",
        "bio": null,
        "url": "https://www.tiktok.com/@farukkolapo",
        "followers": null,
        "following": 41,
        "verified": false,
        "profileImage": "https://p19-common-sign.tiktokcdn.com/tos-alisg-avt-0068/e0b764c22fe648efa6bfba4c91bfac13~tplv-tiktokx-cropcenter:1080:1080.jpeg?dr=14579&refresh_token=4b0219f8&x-expires=1785405600&x-signature=AM%2F90JOcGDiKecFfy8sHawPF3pw%3D&t=4d5b0474&ps=13740610&shp=a5d48078&shcp=81f88b70&idc=my2"
      }
    ]
  },
  "tiktok-user-followings": {
    "url": "https://www.tiktok.com/@khaby.lame",
    "totalReturned": 5,
    "followings": [
      {
        "username": "user927647273",
        "displayName": "user927647273",
        "bio": "secret",
        "url": "https://www.tiktok.com/@user927647273",
        "followers": 9282,
        "following": 4,
        "verified": false,
        "profileImage": "https://p16-common-sign.tiktokcdn.com/tos-maliva-avt-0068/c70537d713e096c514e7e8e27be0cf39~tplv-tiktokx-cropcenter:1080:1080.jpeg?dr=14579&refresh_token=616e8df2&x-expires=1785405600&x-signature=w%2BadFFsdbgxPDur8Y6yIeu5%2FYU8%3D&t=4d5b0474&ps=13740610&shp=a5d48078&shcp=81f88b70&idc=my2"
      },
      {
        "username": "fifaworldcup",
        "displayName": "FIFA World Cup",
        "bio": "🏆 The official #FIFAWorldCup account on TikTok",
        "url": "https://www.tiktok.com/@fifaworldcup",
        "followers": 86600000,
        "following": 93,
        "verified": true,
        "profileImage": "https://p16-common-sign.tiktokcdn.com/tos-useast2a-avt-0068-euttp/d260685754e3ae8139f47e7ec9fda7e9~tplv-tiktokx-cropcenter:1080:1080.jpeg?dr=14579&refresh_token=4d3bd79a&x-expires=1785405600&x-signature=UpkTTNy5CO1ckN0jnBQ1jrq4nRo%3D&t=4d5b0474&ps=13740610&shp=a5d48078&shcp=81f88b70&idc=my2"
      },
      {
        "username": "tiktokcreators",
        "displayName": "tiktok creators",
        "bio": "The official account for TikTok Creators who inspire creativity and bring joy ✨\n\n⬇️ Creator Growth Challenge 💰⬇️",
        "url": "https://www.tiktok.com/@tiktokcreators",
        "followers": 8500000,
        "following": 568,
        "verified": true,
        "profileImage": "https://p16-common-sign.tiktokcdn.com/tos-maliva-avt-0068/7310199914919673862~tplv-tiktokx-cropcenter:1080:1080.jpeg?dr=14579&refresh_token=1e72a8a7&x-expires=1785405600&x-signature=LMjOcpQXxIoqMurpObGJ%2FP7QjsQ%3D&t=4d5b0474&ps=13740610&shp=a5d48078&shcp=81f88b70&idc=my2"
      },
      {
        "username": "christianzammataro",
        "displayName": "Zamma",
        "bio": "Videomaker\nZammaVerse\nVision•Sketch•Backstage•Nature•Prod•Card",
        "url": "https://www.tiktok.com/@christianzammataro",
        "followers": 13000,
        "following": 209,
        "verified": false,
        "profileImage": "https://p16-common-sign.tiktokcdn.com/tos-maliva-avt-0068/acdcc4d8e8390e04aa827d01f0ec161f~tplv-tiktokx-cropcenter:1080:1080.jpeg?dr=14579&refresh_token=d646a014&x-expires=1785405600&x-signature=3Tp8hVjMxhKPOKseqAQJwZRde10%3D&t=4d5b0474&ps=13740610&shp=a5d48078&shcp=81f88b70&idc=my2"
      },
      {
        "username": "mouhamed.mamba",
        "displayName": "mouhamed niang",
        "bio": "🐍Mamba\n🥊k1 pro fighter\n🕋Fede, disciplina e sacrificio.",
        "url": "https://www.tiktok.com/@mouhamed.mamba",
        "followers": 15300,
        "following": 121,
        "verified": false,
        "profileImage": "https://p16-common-sign.tiktokcdn.com/tos-maliva-avt-0068/e4933cfd8c6de6ab18e4ae1fea6e12cb~tplv-tiktokx-cropcenter:1080:1080.jpeg?dr=14579&refresh_token=1bcb3898&x-expires=1785405600&x-signature=6fpMDSKVNCJE%2FpikJbVXEryrtfk%3D&t=4d5b0474&ps=13740610&shp=a5d48078&shcp=81f88b70&idc=my2"
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
    "durationSeconds": 29,
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
      "lastStatusAt": "2026-07-18",
      "fields": []
    },
    "engagement": {
      "replies": 827,
      "reblogs": 2586,
      "likes": 8328
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
    ]
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
    "website": "www.DonaldJTrump.com",
    "createdAt": "2022-02-11T16:16:57.705Z",
    "lastStatusAt": "2026-08-02",
    "emojis": [],
    "fields": [],
    "bot": false,
    "isPrivate": false,
    "group": false,
    "discoverable": null,
    "acceptingMessages": false,
    "chatsOnboarded": true,
    "tvAccount": false
  },
  "truth-social-user-posts": {
    "username": "realDonaldTrump",
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
          "platform": "truth_social",
          "id": "107780257626128497",
          "username": "realDonaldTrump",
          "url": "https://truthsocial.com/@realDonaldTrump",
          "displayName": "Donald J. Trump",
          "bio": "",
          "avatar": "https://static-assets-1.truthsocial.com/tmtg:prime-ts-assets/accounts/avatars/107/780/257/626/128/497/original/454286ac07a6f6e6.jpeg",
          "banner": "https://static-assets-1.truthsocial.com/tmtg:prime-ts-assets/accounts/headers/107/780/257/626/128/497/original/ba3b910ba387bf4e.jpeg",
          "verified": true,
          "followers": 12908901,
          "following": 69,
          "postCount": 35050,
          "website": "www.DonaldJTrump.com",
          "createdAt": "2022-02-11T16:16:57.705Z",
          "lastStatusAt": "2026-07-18",
          "fields": []
        },
        "engagement": {
          "replies": 827,
          "reblogs": 2584,
          "likes": 8321
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
        ]
      },
      {
        "platform": "truth_social",
        "id": "116938558790759096",
        "url": "https://truthsocial.com/@realDonaldTrump/116938558790759096",
        "text": "Ensuring the integrity of our elections is fundamental to preserving trust in American democracy. Following the 2020 presidential election, concerns about potential irregularities prompted detailed examinations of voting processes, data security, and registration practices across multiple states… Download documents and reports addressing key areas of election integrity, here: https://www. whitehouse.gov/election-integr ity/",
        "publishedAt": "2026-07-18T02:13:21.858Z",
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
          "followers": 12908901,
          "following": 69,
          "postCount": 35050,
          "website": "www.DonaldJTrump.com",
          "createdAt": "2022-02-11T16:16:57.705Z",
          "lastStatusAt": "2026-07-18",
          "fields": []
        },
        "engagement": {
          "replies": 1388,
          "reblogs": 3509,
          "likes": 11543
        },
        "language": "en",
        "sensitive": false,
        "media": [
          {
            "type": "video",
            "url": "https://static-assets-1.truthsocial.com/tmtg:prime-ts-assets/media_attachments/files/116/938/518/347/491/612/original/9bb622c2a7cb73f9.mp4",
            "previewUrl": "https://truthsocial.com/icons/missing.png",
            "description": null
          }
        ]
      },
      {
        "platform": "truth_social",
        "id": "116938511106455297",
        "url": "https://truthsocial.com/@realDonaldTrump/116938511106455297",
        "text": "Newly declassified documents show that over a period of years starting during the 2020 election cycle, the People’s Republic of China carried out what is believed to be the largest compromise of election data in history — resulting in China’s illicit acquisition of 220 million U.S. voter files. That information includes names, addresses, phone numbers, political party preferences, and other sensitive data that would be needed to register to vote, and engage in other nefarious activities. This data loss presents an unprecedented election security nightmare. The intelligence even shows that China assigned a data exploitation unit specifically to this new project. https://www. whitehouse.gov/election-integr ity/",
        "publishedAt": "2026-07-18T02:01:14.258Z",
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
          "followers": 12908901,
          "following": 69,
          "postCount": 35050,
          "website": "www.DonaldJTrump.com",
          "createdAt": "2022-02-11T16:16:57.705Z",
          "lastStatusAt": "2026-07-18",
          "fields": []
        },
        "engagement": {
          "replies": 1029,
          "reblogs": 3493,
          "likes": 10641
        },
        "language": "en",
        "sensitive": false,
        "media": [
          {
            "type": "video",
            "url": "https://static-assets-1.truthsocial.com/tmtg:prime-ts-assets/media_attachments/files/116/938/510/857/791/371/original/3d96f7ea038dea38.mp4",
            "previewUrl": "https://static-assets-1.truthsocial.com/tmtg:prime-ts-assets/media_attachments/thumbnails/116/938/510/857/791/371/original/ba6946cca1174f7c.jpg",
            "description": null
          }
        ]
      },
      {
        "platform": "truth_social",
        "id": "116938505608702872",
        "url": "https://truthsocial.com/@realDonaldTrump/116938505608702872",
        "text": "For many years, I have called for bold, swift, and decisive action to protect the integrity of America’s elections. Every American deserves to know that when they cast their vote, that vote will be counted accurately in a system that is secure—one where cheating and interference are not just difficult, but virtually impossible. Unfortunately, the system we have today falls catastrophically short of that standard. Tonight, I am announcing the immediate declassification and release of critical intelligence revealing shocking vulnerabilities in our election infrastructure. This evidence shows that the election system we have is dangerously exposed to hacking, exploitation, and foreign interference. Just as disturbingly, this vital information has for many years been covered up and hidden from you, the American People, and that changes right now. The documents we will release starting tonight have been gathered by the White House Government Transparency Task Force, along with the staff of the President’s Intelligence Advisory Board—supported by our top intelligence agency chiefs, who have all personally reviewed the findings we are presenting this evening, and fully confirmed their authenticity. You can see these documents for yourself at: https://www. whitehouse.gov/election-integr ity/",
        "publishedAt": "2026-07-18T01:59:50.365Z",
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
          "followers": 12908901,
          "following": 69,
          "postCount": 35050,
          "website": "www.DonaldJTrump.com",
          "createdAt": "2022-02-11T16:16:57.705Z",
          "lastStatusAt": "2026-07-18",
          "fields": []
        },
        "engagement": {
          "replies": 583,
          "reblogs": 3027,
          "likes": 10091
        },
        "language": "en",
        "sensitive": false,
        "media": [
          {
            "type": "video",
            "url": "https://static-assets-1.truthsocial.com/tmtg:prime-ts-assets/media_attachments/files/116/938/499/738/796/668/original/9452acce55297397.mp4",
            "previewUrl": "https://static-assets-1.truthsocial.com/tmtg:prime-ts-assets/media_attachments/thumbnails/116/938/499/738/796/668/original/467606ed8b25347a.jpg",
            "description": null
          }
        ]
      },
      {
        "platform": "truth_social",
        "id": "116936997445912023",
        "url": "https://truthsocial.com/@realDonaldTrump/116936997445912023",
        "text": "",
        "publishedAt": "2026-07-17T19:36:17.631Z",
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
          "followers": 12908901,
          "following": 69,
          "postCount": 35050,
          "website": "www.DonaldJTrump.com",
          "createdAt": "2022-02-11T16:16:57.705Z",
          "lastStatusAt": "2026-07-18",
          "fields": []
        },
        "engagement": {
          "replies": 1272,
          "reblogs": 3647,
          "likes": 14375
        },
        "language": null,
        "sensitive": false,
        "media": [
          {
            "type": "image",
            "url": "https://static-assets-1.truthsocial.com/tmtg:prime-ts-assets/media_attachments/files/116/936/996/952/219/927/original/0ffeda9e1e02a6aa.png",
            "previewUrl": "https://static-assets-1.truthsocial.com/tmtg:prime-ts-assets/media_attachments/files/116/936/996/952/219/927/small/0ffeda9e1e02a6aa.png",
            "description": null
          }
        ]
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
    "views": 29833,
    "thumbnail": "https://static-cdn.jtvnw.net/twitch-video-assets/twitch-vap-video-assets-prod-us-west-2/a952a6bb-ad94-4889-8ac1-6afadf21d338/landscape/thumb/thumb-0000000000-1920x1080.jpg",
    "videoUrl": "https://d1ndex63qxojbr.cloudfront.net/nauth/a952a6bb-ad94-4889-8ac1-6afadf21d338/landscape/h264/1080/index.mp4",
    "game": "Just Chatting",
    "broadcaster": "xqc",
    "broadcasterProfileImage": "https://static-cdn.jtvnw.net/jtv_user_pictures/xqc-profile_image-9298dca608632101-150x150.jpeg"
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
    "schedule": [
      {
        "title": "Age of Umbra: Sallowlands",
        "startAt": "2026-07-17T02:00:00Z",
        "endAt": "2026-07-17T06:00:00Z",
        "game": "Tabletop RPGs"
      }
    ]
  },
  "twitch-user-videos": {
    "platform": "twitch",
    "username": "shroud",
    "totalReturned": 5,
    "videos": [
      {
        "platform": "twitch",
        "id": "2827992810",
        "url": "https://www.twitch.tv/videos/2827992810",
        "embedUrl": "https://player.twitch.tv/?video=2827992810&parent=captapi.com",
        "title": "ME N THE GIRLS R GONNA POP OFF IN THIS 100K TWITCH RIVALS",
        "createdAt": "2026-07-24T17:56:52Z",
        "durationSeconds": 20988,
        "views": 185949,
        "thumbnail": "https://static-cdn.jtvnw.net/cf_vods/d2nvs31859zcd8/c43d1ce993fae5a15f69_shroud_317074350583_1784915807//thumb/thumb0-{width}x{height}.jpg",
        "game": "VALORANT",
        "language": "en",
        "broadcaster": "shroud",
        "broadcasterProfileImage": "https://static-cdn.jtvnw.net/jtv_user_pictures/c754eebf-745b-4e0a-814a-10bcaecaabbc-profile_image-300x300.png"
      },
      {
        "platform": "twitch",
        "id": "2827192082",
        "url": "https://www.twitch.tv/videos/2827192082",
        "embedUrl": "https://player.twitch.tv/?video=2827192082&parent=captapi.com",
        "title": "HALO CE REMAKE! TIME TO CO-OP LEGENDARY AND GET OUR MEAT BEAT",
        "createdAt": "2026-07-23T18:19:36Z",
        "durationSeconds": 20254,
        "views": 174697,
        "thumbnail": "https://static-cdn.jtvnw.net/cf_vods/d2vi6trrdongqn/43c3501090df2005acdf_shroud_319635395040_1784830770//thumb/thumb0-{width}x{height}.jpg",
        "game": "Halo: Campaign Evolved",
        "language": "en",
        "broadcaster": "shroud",
        "broadcasterProfileImage": "https://static-cdn.jtvnw.net/jtv_user_pictures/c754eebf-745b-4e0a-814a-10bcaecaabbc-profile_image-300x300.png"
      },
      {
        "platform": "twitch",
        "id": "2827054673",
        "url": "https://www.twitch.tv/videos/2827054673",
        "embedUrl": "https://player.twitch.tv/?video=2827054673&parent=captapi.com",
        "title": "HALO CE REMAKE! TIME TO CO-OP LEGENDARY AND GET OUR MEAT BEAT",
        "createdAt": "2026-07-23T14:57:52Z",
        "durationSeconds": 12076,
        "views": 163661,
        "thumbnail": "https://static-cdn.jtvnw.net/cf_vods/d2vi6trrdongqn/6c4ca61b9211a873ec53_shroud_319633557216_1784818667//thumb/thumb0-{width}x{height}.jpg",
        "game": "Halo: Campaign Evolved",
        "language": "en",
        "broadcaster": "shroud",
        "broadcasterProfileImage": "https://static-cdn.jtvnw.net/jtv_user_pictures/c754eebf-745b-4e0a-814a-10bcaecaabbc-profile_image-300x300.png"
      },
      {
        "platform": "twitch",
        "id": "2826283398",
        "url": "https://www.twitch.tv/videos/2826283398",
        "embedUrl": "https://player.twitch.tv/?video=2826283398&parent=captapi.com",
        "title": "BEATING LEGENDARY INFINITE CO-OP BEFORE HALO CE REMAKE TMRW",
        "createdAt": "2026-07-22T16:18:24Z",
        "durationSeconds": 15014,
        "views": 116325,
        "thumbnail": "https://static-cdn.jtvnw.net/cf_vods/d2vi6trrdongqn/52e9715af5a3a208de07_shroud_319620010720_1784737099//thumb/thumb0-{width}x{height}.jpg",
        "game": "Halo Infinite",
        "language": "en",
        "broadcaster": "shroud",
        "broadcasterProfileImage": "https://static-cdn.jtvnw.net/jtv_user_pictures/c754eebf-745b-4e0a-814a-10bcaecaabbc-profile_image-300x300.png"
      },
      {
        "platform": "twitch",
        "id": "2824697770",
        "url": "https://www.twitch.tv/videos/2824697770",
        "embedUrl": "https://player.twitch.tv/?video=2824697770&parent=captapi.com",
        "title": "LEGENDARY CAMPAIGN BEFORE HALO 1 REMAKE with my bROY",
        "createdAt": "2026-07-20T17:20:23Z",
        "durationSeconds": 24019,
        "views": 238598,
        "thumbnail": "https://static-cdn.jtvnw.net/cf_vods/d2nvs31859zcd8/08ea9e21bb94f98046e1_shroud_317044416375_1784568018//thumb/thumb0-{width}x{height}.jpg",
        "game": "Halo Infinite",
        "language": "en",
        "broadcaster": "shroud",
        "broadcasterProfileImage": "https://static-cdn.jtvnw.net/jtv_user_pictures/c754eebf-745b-4e0a-814a-10bcaecaabbc-profile_image-300x300.png"
      }
    ]
  },
  "twitter-community": {
    "platform": "twitter",
    "id": "1493446837214187523",
    "url": "https://x.com/i/communities/1493446837214187523",
    "name": "Build in Public",
    "description": "Share what you're working on. Get feedback. Help each other move forward. – Sponsored by bolt.new ⚡",
    "memberCount": 263468,
    "createdAt": "2022-02-15T04:47:27.551000+00:00",
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
      },
      {
        "name": "No self-promotion",
        "description": "Don't ask for upvotes or advertise your products/services."
      },
      {
        "name": "Stay on-topic",
        "description": "Only post about building in public. No politics or other off-topic posts. There are other communities for that."
      },
      {
        "name": "No engagement farming",
        "description": "If your goal is to get replies, likes, etc, don’t post it here. Don’t ask super generic questions like “what’s everyone working on?”"
      },
      {
        "name": "Use a personal account",
        "description": "No company accounts. No logos. Use your own name. No promotion or URLs in your name."
      }
    ]
  },
  "twitter-community-tweets": {
    "communityId": "1493446837214187523",
    "totalReturned": 5,
    "tweets": [
      {
        "platform": "twitter",
        "url": "https://x.com/NickDevFE/status/2080189136917672064",
        "id": "2080189136917672064",
        "text": "img2threejs v1.3 is now available. 🎋\n\nOne photo → procedural Three.js code. No meshes. No manual modeling.\n\nGitHub: https://t.co/eYHfZST8DC\n\nv1.3 brings major improvements to geometry reconstruction, material generation, validation, and overall output quality.\n\nFor this demo, I https://t.co/6q2xpbwXrj",
        "lang": "en",
        "publishedAt": "Thu Jul 23 07:11:52 +0000 2026",
        "author": {
          "username": "NickDevFE",
          "displayName": "Nick",
          "url": "https://x.com/NickDevFE",
          "followers": 1759,
          "verified": true,
          "profileImage": "https://pbs.twimg.com/profile_images/1972545424990035968/HKjUZtwo_normal.jpg"
        },
        "engagement": {
          "views": 683643,
          "likes": 3654,
          "replies": 96,
          "retweets": 378,
          "quotes": 22,
          "bookmarks": 4401
        },
        "isReply": false,
        "isRetweet": false,
        "media": [
          "https://pbs.twimg.com/amplify_video_thumb/2080188862962532353/img/52EZv7mlg22s98Dw.jpg"
        ]
      },
      {
        "platform": "twitter",
        "url": "https://x.com/FilipPanoski/status/2079929462565568648",
        "id": "2079929462565568648",
        "text": "pov: you built a product people actually want https://t.co/Ruw8RhZhM1",
        "lang": "en",
        "publishedAt": "Wed Jul 22 14:00:01 +0000 2026",
        "author": {
          "username": "FilipPanoski",
          "displayName": "Filip Panoski",
          "url": "https://x.com/FilipPanoski",
          "followers": 3221,
          "verified": true,
          "profileImage": "https://pbs.twimg.com/profile_images/1842181486587297792/Ia5ilmNs_normal.jpg"
        },
        "engagement": {
          "views": 23033,
          "likes": 404,
          "replies": 111,
          "retweets": 1,
          "quotes": 1,
          "bookmarks": 86
        },
        "isReply": false,
        "isRetweet": false,
        "media": [
          "https://pbs.twimg.com/media/HN1k0g1WQAAeouE.jpg"
        ]
      },
      {
        "platform": "twitter",
        "url": "https://x.com/juiceboy_of_abj/status/2079796903055626348",
        "id": "2079796903055626348",
        "text": "Not everything has to be celebrated publicly,  I just hit 5k followers here on x and i never said anything about it.\n\nThat’s maturity!. \nGood morning Techies 🤗 https://t.co/lg4iL25WFl",
        "lang": "en",
        "publishedAt": "Wed Jul 22 05:13:17 +0000 2026",
        "author": {
          "username": "juiceboy_of_abj",
          "displayName": "Elijah 🌊",
          "url": "https://x.com/juiceboy_of_abj",
          "followers": 5059,
          "verified": true,
          "profileImage": "https://pbs.twimg.com/profile_images/2047368553309798400/e19Qhn0y_normal.jpg"
        },
        "engagement": {
          "views": 19963,
          "likes": 304,
          "replies": 157,
          "retweets": 30,
          "quotes": 1,
          "bookmarks": 3
        },
        "isReply": false,
        "isRetweet": false,
        "media": [
          "https://pbs.twimg.com/media/HNzsQV0WkAEfUow.jpg"
        ]
      },
      {
        "platform": "twitter",
        "url": "https://x.com/NickDevFE/status/2078392573639737713",
        "id": "2078392573639737713",
        "text": "img2threejs - turn one object photo into a code-only procedural Three.js model\n\nOpen-source toolkit that rebuilds the object in a single reference image as procedural Three.js code (no mesh downloads), quality-gated by a render-vs-reference loop - strong for hard-surface objects https://t.co/NtQBLVzMPO",
        "lang": "en",
        "publishedAt": "Sat Jul 18 08:12:58 +0000 2026",
        "author": {
          "username": "NickDevFE",
          "displayName": "Nick",
          "url": "https://x.com/NickDevFE",
          "followers": 1759,
          "verified": true,
          "profileImage": "https://pbs.twimg.com/profile_images/1972545424990035968/HKjUZtwo_normal.jpg"
        },
        "engagement": {
          "views": 12628,
          "likes": 262,
          "replies": 11,
          "retweets": 18,
          "quotes": 2,
          "bookmarks": 240
        },
        "isReply": false,
        "isRetweet": false,
        "media": [
          "https://pbs.twimg.com/amplify_video_thumb/2078392549635678208/img/z88HQqtAHlpxS9qx.jpg"
        ]
      },
      {
        "platform": "twitter",
        "url": "https://x.com/juiceboy_of_abj/status/2079072002283819465",
        "id": "2079072002283819465",
        "text": "Good morning techie 🧑‍💻 ❤️\nLet’s do more today 💪\n\nDo have a productive day ❤️ https://t.co/bgiXFDUHte",
        "lang": "en",
        "publishedAt": "Mon Jul 20 05:12:47 +0000 2026",
        "author": {
          "username": "juiceboy_of_abj",
          "displayName": "Elijah 🌊",
          "url": "https://x.com/juiceboy_of_abj",
          "followers": 5059,
          "verified": true,
          "profileImage": "https://pbs.twimg.com/profile_images/2047368553309798400/e19Qhn0y_normal.jpg"
        },
        "engagement": {
          "views": 18160,
          "likes": 215,
          "replies": 117,
          "retweets": 31,
          "quotes": 2,
          "bookmarks": 2
        },
        "isReply": false,
        "isRetweet": false,
        "media": [
          "https://pbs.twimg.com/media/HNpY9mkXMAAbgHm.jpg",
          "https://pbs.twimg.com/media/HNpY9jMWEAAR0AG.jpg"
        ]
      }
    ]
  },
  "twitter-profile": {
    "platform": "twitter",
    "url": "https://x.com/NASA",
    "id": "11348282",
    "username": "NASA",
    "name": "NASA",
    "bio": "Making the seemingly impossible, possible. ✨",
    "location": "Pale Blue Dot",
    "verified": true,
    "isBlueVerified": true,
    "isIdentityVerified": false,
    "verification": {
      "isIdentityVerified": false,
      "verifiedType": "Government",
      "reason": "This account is verified because it is a government or multilateral organization account.  Learn more",
      "verifiedSince": "2009-08-07T19:53:50.000Z"
    },
    "followers": 92233651,
    "following": 119,
    "tweetCount": 74283,
    "likesCount": 16902,
    "mediaCount": 28057,
    "listedCount": 97023,
    "pinnedTweetIds": [
      "2082511887757881648"
    ],
    "website": "http://www.nasa.gov/",
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
        "publishedAt": "Sat Apr 04 16:34:35 +0000 2026",
        "author": {
          "username": "NASA",
          "displayName": "NASA",
          "url": "https://x.com/NASA",
          "followers": 92225387,
          "verified": true,
          "profileImage": "https://pbs.twimg.com/profile_images/1321163587679784960/0ZxKlEKB_normal.jpg"
        },
        "engagement": {
          "views": 26608930,
          "likes": 196244,
          "replies": 3349,
          "retweets": 29241,
          "quotes": 2911,
          "bookmarks": 11267
        },
        "isReply": false,
        "isRetweet": false,
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
        "publishedAt": "Mon Jul 27 18:07:33 +0000 2026",
        "author": {
          "username": "NASASolarSystem",
          "displayName": "NASA Solar System",
          "url": "https://x.com/NASASolarSystem",
          "followers": 2966292,
          "verified": true,
          "profileImage": "https://pbs.twimg.com/profile_images/1852211324224442369/9KHp7JLo_normal.jpg"
        },
        "engagement": {
          "views": 371846,
          "likes": 1674,
          "replies": 62,
          "retweets": 406,
          "quotes": 20,
          "bookmarks": 176
        },
        "isReply": false,
        "isRetweet": false,
        "media": [
          "https://pbs.twimg.com/amplify_video_thumb/2081803656530190336/img/zUx_qij2E2oP-MsL.jpg"
        ]
      },
      {
        "platform": "twitter",
        "url": "https://x.com/NASA/status/2054251010625765655",
        "id": "2054251010625765655",
        "text": "Perseverance in the Wild Martian West 🤠\n\nOur Perseverance Mars rover snapped some photos beyond the western rim of Jezero Crater—the farthest west the rover has ever gone on the Red Planet. See what we found there: https://t.co/nIkwxstE26 https://t.co/6gJ9xgnVy5",
        "lang": "en",
        "publishedAt": "Tue May 12 17:23:01 +0000 2026",
        "author": {
          "username": "NASA",
          "displayName": "NASA",
          "url": "https://x.com/NASA",
          "followers": 92225387,
          "verified": true,
          "profileImage": "https://pbs.twimg.com/profile_images/1321163587679784960/0ZxKlEKB_normal.jpg"
        },
        "engagement": {
          "views": 1182851,
          "likes": 20257,
          "replies": 962,
          "retweets": 3777,
          "quotes": 123,
          "bookmarks": 693
        },
        "isReply": false,
        "isRetweet": false,
        "media": [
          "https://pbs.twimg.com/tweet_video_thumb/HIIqYwtWsAAcoyZ.jpg"
        ]
      },
      {
        "platform": "twitter",
        "url": "https://x.com/NASA/status/2082511887757881648",
        "id": "2082511887757881648",
        "text": "There's a solar eclipse happening on Wednesday, Aug. 12 — and if you're not in the path of totality, you can watch along with us online! Get the details: https://t.co/aAYzLGEqPU https://t.co/7yrWQpTkld",
        "lang": "en",
        "publishedAt": "Wed Jul 29 17:01:39 +0000 2026",
        "author": {
          "username": "NASA",
          "displayName": "NASA",
          "url": "https://x.com/NASA",
          "followers": 92225387,
          "verified": true,
          "profileImage": "https://pbs.twimg.com/profile_images/1321163587679784960/0ZxKlEKB_normal.jpg"
        },
        "engagement": {
          "views": 93400,
          "likes": 549,
          "replies": 87,
          "retweets": 146,
          "quotes": 13,
          "bookmarks": 61
        },
        "isReply": false,
        "isRetweet": false,
        "media": [
          "https://pbs.twimg.com/media/HOaRhlyWEAA1C8Q.jpg"
        ]
      },
      {
        "platform": "twitter",
        "url": "https://x.com/SpaceNews92/status/2082081188114808938",
        "id": "2082081188114808938",
        "text": "The Saturn V's mighty F-1 engine could only fire once... but SpaceX's Raptor can shut down, restart in space, then restart AGAIN before landing. How did rocket engines evolve that much?\n#spacex #starship #saturnV #nasa https://t.co/dRBxTiL5JA",
        "lang": "en",
        "publishedAt": "Tue Jul 28 12:30:13 +0000 2026",
        "author": {
          "username": "SpaceNews92",
          "displayName": "Rocketry",
          "url": "https://x.com/SpaceNews92",
          "followers": 5245,
          "verified": true,
          "profileImage": "https://pbs.twimg.com/profile_images/1978478483543044096/-hWF_un1_normal.jpg"
        },
        "engagement": {
          "views": 31847,
          "likes": 903,
          "replies": 28,
          "retweets": 72,
          "quotes": 1,
          "bookmarks": 166
        },
        "isReply": false,
        "isRetweet": false,
        "hashtags": [
          "spacex",
          "starship",
          "saturnV",
          "nasa"
        ],
        "media": [
          "https://pbs.twimg.com/amplify_video_thumb/2082079317249724416/img/UdzqLA-kveH5BQdg.jpg"
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
        "text": "Full steam ahead this week at @NASA 🚀\n\n🧑‍🚀 @Astro_Anil arrives at the ISS\n🪐 Dragonfly progress\n✈️ Future of autonomous flight\n🤝 70 Artemis Accords signatories\n\nHere's your NASA Minute! https://t.co/GAZ4sUqfbZ",
        "start": 0,
        "duration": 0,
        "timestamp": "00:00"
      }
    ],
    "wordCount": 32,
    "segments": 1,
    "author": {
      "username": "NASASpox",
      "displayName": "Bethany Stevens",
      "url": "https://x.com/NASASpox",
      "verified": false,
      "profileImage": "https://pbs.twimg.com/profile_images/2030158374625759233/3fWyLDjS_normal.jpg"
    },
    "publishedAt": "2026-07-17T21:06:08.000Z"
  },
  "twitter-tweet-details": {
    "platform": "twitter",
    "url": "https://x.com/NASASpox/status/2078224758781751775",
    "id": "2078224758781751775",
    "text": "Full steam ahead this week at @NASA 🚀\n\n🧑‍🚀 @Astro_Anil arrives at the ISS\n🪐 Dragonfly progress\n✈️ Future of autonomous flight\n🤝 70 Artemis Accords signatories\n\nHere's your NASA Minute! https://t.co/GAZ4sUqfbZ",
    "lang": "en",
    "publishedAt": "2026-07-17T21:06:08.000Z",
    "author": {
      "username": "NASASpox",
      "displayName": "Bethany Stevens",
      "url": "https://x.com/NASASpox",
      "verified": true,
      "profileImage": "https://pbs.twimg.com/profile_images/2030158374625759233/3fWyLDjS_normal.jpg"
    },
    "engagement": {
      "likes": 603,
      "replies": 52
    },
    "isReply": false,
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
        "url": "https://x.com/elonmusk/status/1519480761749016577",
        "id": "1519480761749016577",
        "text": "Next I’m buying Coca-Cola to put the cocaine back in",
        "lang": "en",
        "publishedAt": "Thu Apr 28 00:56:58 +0000 2022",
        "author": {
          "username": "elonmusk",
          "displayName": "Elon Musk",
          "url": "https://x.com/elonmusk",
          "followers": 241067682,
          "verified": true,
          "profileImage": "https://pbs.twimg.com/profile_images/2053244804520427520/m8mdWZCG_normal.jpg"
        },
        "engagement": {
          "likes": 4212271,
          "replies": 168116,
          "retweets": 580111,
          "quotes": 168166
        },
        "isReply": false,
        "isRetweet": false
      },
      {
        "platform": "twitter",
        "url": "https://x.com/elonmusk/status/1812258574049157405",
        "id": "1812258574049157405",
        "text": "https://t.co/6eOgN9UdOy",
        "lang": "zxx",
        "publishedAt": "Sat Jul 13 22:51:28 +0000 2024",
        "author": {
          "username": "elonmusk",
          "displayName": "Elon Musk",
          "url": "https://x.com/elonmusk",
          "followers": 241067682,
          "verified": true,
          "profileImage": "https://pbs.twimg.com/profile_images/2053244804520427520/m8mdWZCG_normal.jpg"
        },
        "engagement": {
          "likes": 3186497,
          "replies": 69142,
          "retweets": 373339,
          "quotes": 40417
        },
        "isReply": false,
        "isRetweet": false,
        "media": [
          "https://pbs.twimg.com/media/GSZvkScbIAAwHQi.jpg"
        ]
      },
      {
        "platform": "twitter",
        "url": "https://x.com/elonmusk/status/1518623997054918657",
        "id": "1518623997054918657",
        "text": "I hope that even my worst critics remain on Twitter, because that is what free speech means",
        "lang": "en",
        "publishedAt": "Mon Apr 25 16:12:30 +0000 2022",
        "author": {
          "username": "elonmusk",
          "displayName": "Elon Musk",
          "url": "https://x.com/elonmusk",
          "followers": 241067682,
          "verified": true,
          "profileImage": "https://pbs.twimg.com/profile_images/2053244804520427520/m8mdWZCG_normal.jpg"
        },
        "engagement": {
          "likes": 2852112,
          "replies": 153311,
          "retweets": 315117,
          "quotes": 68462
        },
        "isReply": false,
        "isRetweet": false
      },
      {
        "platform": "twitter",
        "url": "https://x.com/elonmusk/status/1854026234339938528",
        "id": "1854026234339938528",
        "text": "🇺🇸🇺🇸The future is gonna be so 🔥 🇺🇸🇺🇸 https://t.co/x56cqb6oT5",
        "lang": "en",
        "publishedAt": "Wed Nov 06 05:01:15 +0000 2024",
        "author": {
          "username": "elonmusk",
          "displayName": "Elon Musk",
          "url": "https://x.com/elonmusk",
          "followers": 241067682,
          "verified": true,
          "profileImage": "https://pbs.twimg.com/profile_images/2053244804520427520/m8mdWZCG_normal.jpg"
        },
        "engagement": {
          "likes": 2494169,
          "replies": 56899,
          "retweets": 194031,
          "quotes": 12167
        },
        "isReply": false,
        "isRetweet": false,
        "media": [
          "https://pbs.twimg.com/media/GbrTB8GXEAYrk2N.jpg"
        ]
      },
      {
        "platform": "twitter",
        "url": "https://x.com/elonmusk/status/1519495072802390016",
        "id": "1519495072802390016",
        "text": "Let’s make Twitter maximum fun!",
        "lang": "en",
        "publishedAt": "Thu Apr 28 01:53:50 +0000 2022",
        "author": {
          "username": "elonmusk",
          "displayName": "Elon Musk",
          "url": "https://x.com/elonmusk",
          "followers": 241067682,
          "verified": true,
          "profileImage": "https://pbs.twimg.com/profile_images/2053244804520427520/m8mdWZCG_normal.jpg"
        },
        "engagement": {
          "likes": 2331941,
          "replies": 99683,
          "retweets": 164577,
          "quotes": 33693
        },
        "isReply": false,
        "isRetweet": false
      }
    ]
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
    "bannerUrl": "https://yt3.googleusercontent.com/nxYrc_1_2f77DoBadyxMTmv7ZpRZapHR5jbuYe7PlPd5cIRJxtNNEYyOC0ZsxaDyJJzXrnJiuDE=s160-c-k-c0x00ffffff-no-rj",
    "country": "United States",
    "joinedDate": "Feb 19, 2012",
    "verified": true,
    "links": [
      {
        "text": "$1,000,000 Contest",
        "url": "themostdangerousgames.com"
      },
      {
        "text": "Follow",
        "url": "instagram.com/mrbeast"
      },
      {
        "text": "Twitter",
        "url": "twitter.com/MrBeast"
      },
      {
        "text": "Facebook",
        "url": "facebook.com/mrbeast"
      }
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
      },
      {
        "url": "https://www.youtube.com/playlist?list=PLoSWVnSA9vG8SK6-_45PAu6RVTaP1zXHf",
        "title": "MrBeast Tries To Survive",
        "videoCount": 9,
        "thumbnailUrl": "https://i.ytimg.com/vi/yhB3BgJyGl8/hqdefault.jpg?sqp=-oaymwEXCOADEI4CSFryq4qpAwkIARUAAIhCGAE=&rs=AOn4CLAlUeAgqFlcajDo_SwhI8D8yjpM5w"
      },
      {
        "url": "https://www.youtube.com/playlist?list=PLoSWVnSA9vG_PuIrGMfUtJ2wwKSUb2CFd",
        "title": "Cheapest Vs Most Expensive",
        "videoCount": 9,
        "thumbnailUrl": "https://i.ytimg.com/vi/iogcY_4xGjo/hqdefault.jpg?sqp=-oaymwEXCOADEI4CSFryq4qpAwkIARUAAIhCGAE=&rs=AOn4CLCHkaK4BD0daxla9yDQvS8Hop3Xlg"
      },
      {
        "url": "https://www.youtube.com/playlist?list=PLoSWVnSA9vG9hJNdgr-81MG59EYT9eEYn",
        "title": "MrBeast’s Most Viewed Videos",
        "videoCount": 25,
        "thumbnailUrl": "https://i.ytimg.com/vi/yXWw0_UfSFg/hqdefault.jpg?sqp=-oaymwEXCOADEI4CSFryq4qpAwkIARUAAIhCGAE=&rs=AOn4CLD93aJIeUK-Qgt-LOUSL7njyz1kcg"
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
      },
      {
        "url": "https://www.youtube.com/shorts/LgbyEFILLJI",
        "title": "$1 vs $10,000 Cake",
        "publishedAt": null,
        "viewCount": 87000000,
        "durationSeconds": null,
        "thumbnailUrl": null,
        "channelName": "MrBeast"
      },
      {
        "url": "https://www.youtube.com/shorts/YA_kX8hu1gg",
        "title": "This Plane Takes Off in 12 Seconds",
        "publishedAt": null,
        "viewCount": 31000000,
        "durationSeconds": null,
        "thumbnailUrl": null,
        "channelName": "MrBeast"
      },
      {
        "url": "https://www.youtube.com/shorts/XCGVurja73c",
        "title": "I Raced The Fastest Man On Earth",
        "publishedAt": null,
        "viewCount": 87000000,
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
      },
      {
        "url": "https://www.youtube.com/watch?v=iYlODtkyw_I",
        "title": "Survive 30 Days Chained To A Stranger, Win $250,000",
        "publishedAt": "2026-06-27T16:00:05.000Z",
        "viewCount": 55908561,
        "durationSeconds": 2104,
        "thumbnailUrl": "https://i.ytimg.com/vi/iYlODtkyw_I/maxresdefault.jpg",
        "channelName": "MrBeast"
      },
      {
        "url": "https://www.youtube.com/watch?v=__fmDj0ZJ1Q",
        "title": "50 YouTube Legends Fight For $1,000,000",
        "publishedAt": "2026-06-13T16:00:00.000Z",
        "viewCount": 69251098,
        "durationSeconds": 1927,
        "thumbnailUrl": "https://i.ytimg.com/vi/__fmDj0ZJ1Q/maxresdefault.jpg",
        "channelName": "MrBeast"
      },
      {
        "url": "https://www.youtube.com/watch?v=6Zy5VLcEbZc",
        "title": "I Stranded 100 People In The Wilderness For $250,000",
        "publishedAt": "2026-05-02T16:00:01.000Z",
        "viewCount": 135166859,
        "durationSeconds": 2220,
        "thumbnailUrl": "https://i.ytimg.com/vi/6Zy5VLcEbZc/maxresdefault.jpg",
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
        "publishedAt": "4 days ago",
        "viewCount": 31000000,
        "durationSeconds": 875,
        "thumbnailUrl": "https://i.ytimg.com/vi/lVylRtlPOIE/hqdefault.jpg?sqp=-oaymwEcCNACELwBSFXyq4qpAw4IARUAAIhCGAFwAcABBg==&rs=AOn4CLDEw9iu9Jqd9KZ9pBMfbkc-aipTog",
        "channelName": "MrBeast"
      },
      {
        "url": "https://www.youtube.com/watch?v=iYlODtkyw_I",
        "title": "Survive 30 Days Chained To A Stranger, Win $250,000",
        "publishedAt": "1 month ago",
        "viewCount": 81000000,
        "durationSeconds": 2105,
        "thumbnailUrl": "https://i.ytimg.com/vi/iYlODtkyw_I/hqdefault.jpg?sqp=-oaymwEcCNACELwBSFXyq4qpAw4IARUAAIhCGAFwAcABBg==&rs=AOn4CLBr_mSSbkEXsEQf8rxuahzMDeW9Jg",
        "channelName": "MrBeast"
      },
      {
        "url": "https://www.youtube.com/watch?v=__fmDj0ZJ1Q",
        "title": "50 YouTube Legends Fight For $1,000,000",
        "publishedAt": "1 month ago",
        "viewCount": 76000000,
        "durationSeconds": 1928,
        "thumbnailUrl": "https://i.ytimg.com/vi/__fmDj0ZJ1Q/hqdefault.jpg?sqp=-oaymwEcCNACELwBSFXyq4qpAw4IARUAAIhCGAFwAcABBg==&rs=AOn4CLBfvcFZsIc7eS3Y5mxNTWGLYGjlVg",
        "channelName": "MrBeast"
      },
      {
        "url": "https://www.youtube.com/watch?v=GpQSUjNsNm0",
        "title": "7 Days Stranded in The Arctic",
        "publishedAt": "1 month ago",
        "viewCount": 104000000,
        "durationSeconds": 1935,
        "thumbnailUrl": "https://i.ytimg.com/vi/GpQSUjNsNm0/hqdefault.jpg?sqp=-oaymwEcCNACELwBSFXyq4qpAw4IARUAAIhCGAFwAcABBg==&rs=AOn4CLDou7TMV8d2wG0J5_NdPxT_Z04_Iw",
        "channelName": "MrBeast"
      },
      {
        "url": "https://www.youtube.com/watch?v=AaMdXZMvT3w",
        "title": "Survive 30 Days On An Island With Your Ex, Win $250,000",
        "publishedAt": "2 months ago",
        "viewCount": 96000000,
        "durationSeconds": 2349,
        "thumbnailUrl": "https://i.ytimg.com/vi/AaMdXZMvT3w/hqdefault.jpg?sqp=-oaymwEcCNACELwBSFXyq4qpAw4IARUAAIhCGAFwAcABBg==&rs=AOn4CLAfwDXsWdeKhhuSk9s8s1TnaZVv0Q",
        "channelName": "MrBeast"
      }
    ]
  },
  "youtube-comment-replies": {
    "url": "https://www.youtube.com/watch?v=dQw4w9WgXcQ",
    "videoId": "dQw4w9WgXcQ",
    "commentId": "Ugzge340dBgB75hWBm54AaABAg",
    "totalReturned": 10,
    "replies": [
      {
        "id": "Ugzge340dBgB75hWBm54AaABAg.AHE8_QAWJx9AHE9eIiztxR",
        "author": "@linganguliguliwatcha",
        "authorAvatarUrl": "https://yt3.ggpht.com/AbGqKNjK9k5tyOqdV7cdXx-GgnGuuGQ5wj8RN42U5YCDvYHT0vaOKXGFahR36iaDPseGN08DjQ=s88-c-k-c0x00ffffff-no-rj",
        "authorIsVerified": false,
        "authorIsChannelOwner": false,
        "text": "YOUTUBE AND ONE LIKE WOOHAAAAH",
        "likeCount": 7100,
        "replyCount": 5,
        "hasCreatorHeart": true,
        "publishedTimeText": "1 year ago",
        "replyToId": "Ugzge340dBgB75hWBm54AaABAg"
      },
      {
        "id": "Ugzge340dBgB75hWBm54AaABAg.AHE8_QAWJx9AHEAB_-JmDA",
        "author": "@_bugrabilgin",
        "authorAvatarUrl": "https://yt3.ggpht.com/LvMpN24GYYr8w43sGoMeYZYejDPJz_skehI6jm_XGGhfM5YeRa9OOsaplj60LnFNehE79ZxImg=s88-c-k-c0x00ffffff-no-rj",
        "authorIsVerified": false,
        "authorIsChannelOwner": false,
        "text": "HEY YOUTUBE",
        "likeCount": 3000,
        "replyCount": 2,
        "hasCreatorHeart": true,
        "publishedTimeText": "1 year ago",
        "replyToId": "Ugzge340dBgB75hWBm54AaABAg"
      },
      {
        "id": "Ugzge340dBgB75hWBm54AaABAg.AHE8_QAWJx9AHEAOCSlaNN",
        "author": "@NashiraArif",
        "authorAvatarUrl": "https://yt3.ggpht.com/ytc/AIdro_n1guDiz8iQIUgFGnmh5VA5PJlNSiWQwX3Ik0ywlPv8JUDRXZiF6wxDvbC7F3YSi1BdlA=s88-c-k-c0x00ffffff-no-rj",
        "authorIsVerified": false,
        "authorIsChannelOwner": false,
        "text": "new comment alert",
        "likeCount": 2000,
        "replyCount": 0,
        "hasCreatorHeart": true,
        "publishedTimeText": "1 year ago",
        "replyToId": "Ugzge340dBgB75hWBm54AaABAg"
      },
      {
        "id": "Ugzge340dBgB75hWBm54AaABAg.AHE8_QAWJx9AHEAQwtwdoZ",
        "author": "@jennaortega-m4m",
        "authorAvatarUrl": "https://yt3.ggpht.com/ytc/AIdro_lVdgv6VK0IOScTdHt1R4NdIFdRkvG2Y1jsrCR_otHBLogTg1YjnUt3k9YQBrmAT3VFLg=s88-c-k-c0x00ffffff-no-rj",
        "authorIsVerified": false,
        "authorIsChannelOwner": false,
        "text": "oop 3rd didnt realise youtube was here😄",
        "likeCount": 909,
        "replyCount": 0,
        "hasCreatorHeart": true,
        "publishedTimeText": "1 year ago",
        "replyToId": "Ugzge340dBgB75hWBm54AaABAg"
      },
      {
        "id": "Ugzge340dBgB75hWBm54AaABAg.AHE8_QAWJx9AHEB5iPJLDp",
        "author": "@TheAngelofBattle99",
        "authorAvatarUrl": "https://yt3.ggpht.com/92UP2htp8mRB1oRt7tZ1bmid5hSmtrt-fNUlOH0sgx0zBFEwLSQ7OT0Vo8nuyWC3XSyUxNl3oMQ=s88-c-k-c0x00ffffff-no-rj",
        "authorIsVerified": false,
        "authorIsChannelOwner": false,
        "text": "He's ingrained in our brains at this point. Such a devoted man.",
        "likeCount": 698,
        "replyCount": 0,
        "hasCreatorHeart": true,
        "publishedTimeText": "1 year ago",
        "replyToId": "Ugzge340dBgB75hWBm54AaABAg"
      }
    ]
  },
  "youtube-comments": {
    "url": "https://www.youtube.com/watch?v=dQw4w9WgXcQ",
    "videoId": "dQw4w9WgXcQ",
    "totalReturned": 5,
    "totalComments": 2446085,
    "nextCursor": "Eg0SC2RRdzR3OVdnWGNRGAYyJSIRIgtkUXc0dzlXZ1hjUTAAeAJCEGNvbW1lbnRzLXNlY3Rpb24%3D",
    "hasMore": true,
    "comments": [
      {
        "id": "Ugzge340dBgB75hWBm54AaABAg",
        "author": "@YouTube",
        "authorAvatarUrl": "https://yt3.ggpht.com/3s6evpqAiDU9tQR4sC2siJippbH2RWVPnwHgyl4V0th2iuQz0VDQZbUhQBGmsxLYo-mjG6TqZQ=s88-c-k-c0x00ffffff-no-rj",
        "authorIsVerified": true,
        "authorIsChannelOwner": false,
        "text": "can confirm: he never gave us up",
        "likeCount": 274000,
        "replyCount": 961,
        "hasCreatorHeart": true,
        "publishedTimeText": "1 year ago"
      },
      {
        "id": "UgyBphvOZuIgdVHgFvx4AaABAg",
        "author": "@Neouss",
        "authorAvatarUrl": "https://yt3.ggpht.com/GEhF3wh6dcR36TBui5D4TxzcMAjZXtUdo4neBfxJnbNMpqvbThH31zYQnB9QH-7PeydlKc4ueA=s88-c-k-c0x00ffffff-no-rj",
        "authorIsVerified": false,
        "authorIsChannelOwner": false,
        "text": "MuffinJuice sent me here",
        "likeCount": 1200,
        "replyCount": 260,
        "hasCreatorHeart": true,
        "publishedTimeText": "18 hours ago"
      },
      {
        "id": "UgyEnXfdC-umwvTt8JF4AaABAg",
        "author": "@Oatman69",
        "authorAvatarUrl": "https://yt3.ggpht.com/ghenbV7T5VMOA3iqp3PThC82exqcu7iVng_iWNx1Ujak72Ti4oZZ_XzSVzIrfk9arP1XrFtnZA=s88-c-k-c0x00ffffff-no-rj",
        "authorIsVerified": false,
        "authorIsChannelOwner": false,
        "text": "Gonna flag this for nudity so I can rick roll the YouTube staff",
        "likeCount": 561000,
        "replyCount": 670,
        "hasCreatorHeart": true,
        "publishedTimeText": "6 years ago"
      },
      {
        "id": "Ugxzbv_ZeZXNRcfwsSF4AaABAg",
        "author": "@candycake9531",
        "authorAvatarUrl": "https://yt3.ggpht.com/ytc/AIdro_mEO82VrM8XtyGrBUkJgbAYgpAmDpUZixd1QvK9kyA=s88-c-k-c0x00ffffff-no-rj",
        "authorIsVerified": false,
        "authorIsChannelOwner": false,
        "text": "Is everyone going to ignore the fact that Rick Astley looks like a twelve year old boy but has a uniquely deep voice?",
        "likeCount": 288000,
        "replyCount": 635,
        "hasCreatorHeart": true,
        "publishedTimeText": "6 years ago"
      },
      {
        "id": "UgyOBSJT7Ca0h-XMMQ54AaABAg",
        "author": "@Aubslovesredbull",
        "authorAvatarUrl": "https://yt3.ggpht.com/3qSnEkftXN9c1oU3e7lh106XqMKEG1_sYJ8G_PznBozt1qyMcJYS7E0aHBAU1c0FktK9x-w7p5k=s88-c-k-c0x00ffffff-no-rj",
        "authorIsVerified": false,
        "authorIsChannelOwner": false,
        "text": "MUFFIN JUICE RICK ROLLED ME",
        "likeCount": 94,
        "replyCount": 3,
        "hasCreatorHeart": true,
        "publishedTimeText": "18 hours ago"
      }
    ]
  },
  "youtube-community-post-details": {
    "platform": "youtube",
    "id": "UgkxfMvMnSnV3Ww9HwAY2wFGmVevmhRaYAYO",
    "url": "https://www.youtube.com/post/UgkxfMvMnSnV3Ww9HwAY2wFGmVevmhRaYAYO",
    "text": "Inside this box is the world's FIRST 500M Play Button. We're 10M away from 500M and I cannot wait to see what’s in here so help me out.",
    "publishedAt": "1 month ago (edited)",
    "channelName": "MrBeast",
    "channelUrl": "https://www.youtube.com/@MrBeast",
    "likes": "727K",
    "comments": 16260,
    "images": [
      "https://yt3.ggpht.com/BgBr4f_nvLm84HY2JVaPiDZRLZXJsqA7Q29CJkAksrwRFNXN1GgQJxzjYfzWUYR6ZekKBXCVwxPQKw=s1000-rw-nd-v1"
    ]
  },
  "youtube-community-posts": {
    "url": "https://www.youtube.com/@MrBeast",
    "totalReturned": 5,
    "posts": [
      {
        "id": "UgkxB7POmB4C7U0I3kIEWRZpYfE2t-ieP9CA",
        "author": "MrBeast",
        "text": "Some more fun wedding photos 🥰",
        "likeCount": "3M",
        "hashtags": [],
        "linkedVideos": [],
        "publishedTime": "4 days ago",
        "postType": "image",
        "images": [
          "https://yt3.ggpht.com/bFmb7RbyvsNTUS3otE4oc2tqI5CZyl3apwKmjnqnTjFuv1mwxWG7hWlZCuiWlRYrd3oCd_nAtBWVsw=s2641-c-fcrop64=1,00002578ffffda87-rw-nd-v1",
          "https://yt3.ggpht.com/1Oxcyk2wshlCOoZYiTWUFoixDaomfdtlcIKiGv_ozoT4Lfs9CZx-3VTxbNeQlJOOV_h7CdWjWF8QIA=s1536-c-fcrop64=1,00002000ffffdfff-rw-nd-v1",
          "https://yt3.ggpht.com/q_WXrPGUBlang4cdYbyfmOLtBvYUw9SGIHXeDg79S2RbLqVQwM94Yz1cDe3r-xtN7Eh8BO_U66xdpA=s1243-c-fcrop64=1,0000126dffffed92-rw-nd-v1",
          "https://yt3.ggpht.com/8Q3p7-Jgoxdl_DUEW10TCVN9IlH4bdALqgXqQa67aAX66vsZNTUJ6deIN_7hsWWELDqgqDTVPK8P=s945-c-fcrop64=1,00001f14ffffe0eb-rw-nd-v1",
          "https://yt3.ggpht.com/cQMWv1Z7gGyL6hcS_gq0qnzAYu32fWH7VVWiFUKlJ5tuSYzOHkOD-i8qnUjHl9BM3O4JoLsWuh5CP2Y=s3597-c-fcrop64=1,0000289effffd761-rw-nd-v1",
          "https://yt3.ggpht.com/JMZoggM17vtc4ssB2u4rDHPJKyUUHihMxypM_orcMdyIAwHeNockUGAB9UX4mU7LepF2V0UsDveHCA=s4000-c-fcrop64=1,00002aabffffd555-rw-nd-v1",
          "https://yt3.ggpht.com/B0NfyE7U1BMX151AO2feyeSDhPuJxyzSoF8aMjpI43sHC8hG1jd1h8HN4kH-Ssy6r24lCTbKwnkSbQ=s1391-c-fcrop64=1,00001d86ffffe279-rw-nd-v1",
          "https://yt3.ggpht.com/SWKVPUHhc6MDW6M14xFCKMIVn8mGZ7sXdB0FbcprFNYu3OBvOD7flK3c16jiOcvbs1pSEvuFS11LYxs=s1536-c-fcrop64=1,00002000ffffdfff-rw-nd-v1",
          "https://yt3.ggpht.com/7E8dNdAgzEVvk5Ek9HCnrCXzl1dzGd4W2IeU7be6SlVaT4SeKdLjGwdtC5UjlY1W_jjPUoy_4rfhYB8=s1204-c-fcrop64=1,00000b56fffff4a9-rw-nd-v1",
          "https://yt3.ggpht.com/Q6mSIBC6EeRqdYr22tW8CCQXHr6uWzCKgsavj1BgThze1AjWd4cO-lbMzoaPvW4ThJftbf0DwkvSfbs=s2309-c-fcrop64=1,00002a55ffffd5aa-rw-nd-v1"
        ],
        "sourceUrl": "https://www.youtube.com/post/UgkxB7POmB4C7U0I3kIEWRZpYfE2t-ieP9CA"
      },
      {
        "id": "Ugkxg-YuyvHwnlFZRktAZHHELzGBrskCHChJ",
        "author": "MrBeast",
        "text": "I found MrsBeast ❤️❤️❤️",
        "likeCount": "3.1M",
        "hashtags": [],
        "linkedVideos": [],
        "publishedTime": "6 days ago",
        "postType": "image",
        "images": [
          "https://yt3.ggpht.com/oiElfzENMAx3umYLMOH0sZOodVZChBV2L0ddB-KbqwR9B0djUx9o-JMD8ehXMt9fmKtAkGeO3ySq=s4000-c-fcrop64=1,00000000ffffc002-rw-nd-v1",
          "https://yt3.ggpht.com/sL9SyPNxLv5TT8CMSqQFy3o0DhtCcyxQrCt2hfIXYSHNhDZ0_f2ORfAZs8K8aAXoZQ05G7hsnOviCQ=s4000-c-fcrop64=1,00001ffeffffe001-rw-nd-v1",
          "https://yt3.ggpht.com/0ii-qqCQhUjGtuOBVmwF_lWai5LASCHWt13_EDuLYK_bjnPVNj9jr-lCd4k0IEtAnq-K7dOy-nCoCoM=s4000-c-fcrop64=1,00001ffeffffe001-rw-nd-v1",
          "https://yt3.ggpht.com/qN_PSjKlmeBX0c6md9_UiLJDK0PCa-cmOPV3LZGF_DrCL8hLWgl3l-hRV6xRBLYn1u0yDSY2Vny46A=s4000-c-fcrop64=1,00002aabffffd555-rw-nd-v1",
          "https://yt3.ggpht.com/WyehwE4SB6RQXEBUC95ikv8XQZ4MjAXAsVRoo8fttoZ9N6aKuGL0uMkXuPAGJkDpMuHBEpEYSkhNkg=s3443-c-fcrop64=1,00001632ffffc0d8-rw-nd-v1",
          "https://yt3.ggpht.com/IIqrXXwXI4bGDe6Qu7AhHFDoR3jTTWKuoHuKroBLHv7WHY_t8tH6A-zJNRnSAu3PBbdT0ZP0VkmP=s3694-c-fcrop64=1,00001ffeffffe001-rw-nd-v1",
          "https://yt3.ggpht.com/7Z3SQ5aLhP-SFLgNHJYYPJjRuommNGPITPaZ6aKcyA6JfQ6Xzm1LamFBDB8w-TmjrVQLFocMf5Hw=s1512-c-fcrop64=1,22720000df71ffff-rw-nd-v1",
          "https://yt3.ggpht.com/nTCt6VFjOqJ607Y2Tb-At-Xwbb2gEWmh_Ve1JOtsE3NsEqljGct951jWfV4qiWnqou5NAzR-08ngX2c=s1536-c-fcrop64=1,00002d70ffffed70-rw-nd-v1",
          "https://yt3.ggpht.com/T8xahSvoZ9GsUE1LjLZlMjysrWBCTMoEgbulScCwLTPlo431x7gNf4qVnOTZnP_KD11c-XlTVbpDwQ=s1536-c-fcrop64=1,00003800fffff7ff-rw-nd-v1",
          "https://yt3.ggpht.com/2BbHUfFvEn-wzKx7JWg5w2KEkWNsgakDEL7esqd76MHbnGapkq7USRLvdZDA4aaN_nHjwwHiNU7Upg=s1536-c-fcrop64=1,0000351ffffff51e-rw-nd-v1"
        ],
        "sourceUrl": "https://www.youtube.com/post/Ugkxg-YuyvHwnlFZRktAZHHELzGBrskCHChJ"
      },
      {
        "id": "Ugkx5QH9-Xr0EWbVJ1riARjVrDcXRN1LfJS7",
        "author": "MrBeast",
        "text": "World Cup was fun",
        "likeCount": "1.9M",
        "hashtags": [],
        "linkedVideos": [],
        "publishedTime": "8 days ago",
        "postType": "image",
        "images": [
          "https://yt3.ggpht.com/wTY3z3Ws2f97goiOPzWqUJMt_LLjENEnpjJoCEefj_yzalyDfkc3N9OKfbtpCqo9KRe927hAX7lJqr0=s4000-c-fcrop64=1,00003852ffffe2fc-rw-nd-v1",
          "https://yt3.ggpht.com/3UpCr01_PnDBkovY5PCgKqG0221xES8Yb3A9UVTpHVl__YmAB3dT0bsg6Z0eGSRQN64x4i60Xz3n=s4000-c-fcrop64=1,00002aabffffd555-rw-nd-v1",
          "https://yt3.ggpht.com/1Yfvbg7t0d034W1lsREZ3yWrOEEa7gN_wYUpQCsQsr1qYJ3-8jv0rMhMHSkOvI6R3ysih0PK2ycIKg=s4000-c-fcrop64=1,00002aabffffd555-rw-nd-v1",
          "https://yt3.ggpht.com/TVVdXkwHQCQeQGNj96ampiA0IJO54rAPMtXjGMT7tc73vTr2wYHX8ifIyyyUWzn1JV0QJA0xrrXi=s4000-c-fcrop64=1,00002aabffffd555-rw-nd-v1",
          "https://yt3.ggpht.com/ukbZ3zGop56AMC50lpvjDrJSC5gVHSM2W42hvaYKWOzw0q-4xP3QqYFBYZYmyKUOHwjymGVwqv78Psg=s3024-c-fcrop64=1,0000119affffd199-rw-nd-v1",
          "https://yt3.ggpht.com/bVmcqICH-voxPGC-JfGe5yygtVmdcwOQF8ipVvs7KuXUtf2L1HME_IzdHdkycSnmxN0ycb1EANUUhw=s3072-c-fcrop64=1,00001666ffffd666-rw-nd-v1",
          "https://yt3.ggpht.com/0xGnt5haSN7s7nTOOB9X0aUcyGxXWcJB5uyoaBNR7mu6oLg__BcVio15yQ-hkMQGJQYhelwQ8YCwOQ=s4000-c-fcrop64=1,00002aabffffd555-rw-nd-v1",
          "https://yt3.ggpht.com/ViJDGtCQI80Qtmqu7HkWcFRhEET20UI079U1M9UPstAoUGI8ahGgeH8myDZZZozJUxB98azf53-r=s3072-c-fcrop64=1,0000351ffffff51e-rw-nd-v1",
          "https://yt3.ggpht.com/avRvz0VQnyLMqnGn5dRkAXxDX9523Uej7a2EMxjSt2ayBHchdLOZtSkJ0zq2QraRdEheesz0uZNha6M=s1178-c-fcrop64=1,00002b01ffffd4fe-rw-nd-v1",
          "https://yt3.ggpht.com/ZXW2WnSmbiYB1NwSPrIG1oR72VgCrfiFP1Pb6h_Gao--4pILV_NoXOAJrDp4aIE8V6l3v3ESkqU4jTI=s1067-c-fcrop64=1,00001ff4ffffe00b-rw-nd-v1"
        ],
        "sourceUrl": "https://www.youtube.com/post/Ugkx5QH9-Xr0EWbVJ1riARjVrDcXRN1LfJS7"
      },
      {
        "id": "UgkxZusu9I1Z-VuU5PGZNA2gclHi8V9CJVZk",
        "author": "MrBeast",
        "text": "Would you rather stop aging for 100 years or receive 1 billion dollars right now?",
        "likeCount": "86K",
        "hashtags": [],
        "linkedVideos": [],
        "publishedTime": "8 days ago",
        "postType": "text",
        "images": [],
        "sourceUrl": "https://www.youtube.com/post/UgkxZusu9I1Z-VuU5PGZNA2gclHi8V9CJVZk"
      },
      {
        "id": "Ugkx3w8sfDJf_NDdhUAtu7MTLX3d_Dt1V9UK",
        "author": "MrBeast",
        "text": "No upload today, may or may not be getting married and a little occupied 🤪",
        "likeCount": "250K",
        "hashtags": [],
        "linkedVideos": [],
        "publishedTime": "2 weeks ago",
        "postType": "text",
        "images": [],
        "sourceUrl": "https://www.youtube.com/post/Ugkx3w8sfDJf_NDdhUAtu7MTLX3d_Dt1V9UK"
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
      },
      {
        "url": "https://www.youtube.com/shorts/hwf0tDWlP7Q",
        "title": "Ashnikko - stupid feat ।। Autotune Vs no autotune ।। #battleofsong #shorts #music #song #singer",
        "publishedAt": "2022-12-14T08:29:38.000Z",
        "viewCount": 64582461,
        "durationSeconds": 19,
        "thumbnailUrl": "https://i.ytimg.com/vi/hwf0tDWlP7Q/maxres2.jpg?sqp=-oaymwEoCIAKENAF8quKqQMcGADwAQH4AbYIgAKAD4oCDAgAEAEYFSBLKH8wDw==&rs=AOn4CLCkDkjFljIdMxNOOmrsKANlEOnqrQ",
        "channelName": "Battle of song"
      },
      {
        "url": "https://www.youtube.com/shorts/hAQcodpwsIA",
        "title": "IS THIS THE HOTTEST NEW ROCKSTAR OF 2023?! #music #emo #punkrock #hardrock #rocksong #rock #rockstar",
        "publishedAt": "2023-05-26T19:12:49.000Z",
        "viewCount": 12286628,
        "durationSeconds": 20,
        "thumbnailUrl": "https://i.ytimg.com/vi/hAQcodpwsIA/maxresdefault.jpg?sqp=-oaymwEoCIAKENAF8quKqQMcGADwAQH4Ac4FgAKACooCDAgAEAEYXSBlKDgwDw==&rs=AOn4CLB1qp8scA6duDC5KhV4UHe1QqDhiw",
        "channelName": "TX2 OFFICIAL"
      },
      {
        "url": "https://www.youtube.com/watch?v=O40ruQpZogY",
        "title": "Seriously This is One of The Most Beautiful Songs Ever Made 🥹😭",
        "publishedAt": "2026-04-28T03:53:48.000Z",
        "viewCount": 852851,
        "durationSeconds": 274,
        "thumbnailUrl": "https://i.ytimg.com/vi/O40ruQpZogY/maxresdefault.jpg",
        "channelName": "Fearless Soul"
      }
    ]
  },
  "youtube-playlist": {
    "platform": "youtube",
    "url": "https://www.youtube.com/playlist?list=PLMC9KNkIncKtPzgY-5rmhvj7fax8fdxoj",
    "title": "Pop Music Playlist - Timeless Pop Songs (Updated Weekly 2026)",
    "channelName": "ROSÉ and Bruno Mars",
    "totalReturned": 5,
    "videos": [
      {
        "url": "https://www.youtube.com/watch?v=ekr2nIex040",
        "title": "ROSÉ & Bruno Mars - APT. (Official Music Video)",
        "publishedAt": "1 year ago",
        "viewCount": 2500000000,
        "durationSeconds": 174,
        "thumbnailUrl": "https://i.ytimg.com/vi/ekr2nIex040/hqdefault.jpg?sqp=-oaymwEgCNACELwBSFXyq4qpAxIIARUAAIhCGAFwAcABBrgC8xg=&rs=AOn4CLDzyvnY8qeogjw9kGhO1TPZkM12-A",
        "channelName": "ROSÉ and Bruno Mars"
      },
      {
        "url": "https://www.youtube.com/watch?v=kPa7bsKwL-c",
        "title": "Lady Gaga, Bruno Mars - Die With A Smile (Official Music Video)",
        "publishedAt": "1 year ago",
        "viewCount": 1700000000,
        "durationSeconds": 253,
        "thumbnailUrl": "https://i.ytimg.com/vi/kPa7bsKwL-c/hqdefault.jpg?sqp=-oaymwEgCNACELwBSFXyq4qpAxIIARUAAIhCGAFwAcABBrgC8xg=&rs=AOn4CLDF3iMqsC6OQclYtXdkxhPQUpKHUA",
        "channelName": "Lady Gaga"
      },
      {
        "url": "https://www.youtube.com/watch?v=euCqAq6BRa4",
        "title": "DJ Snake - Let Me Love You (Official Music Video) ft. Justin Bieber",
        "publishedAt": "9 years ago",
        "viewCount": 2000000000,
        "durationSeconds": 206,
        "thumbnailUrl": "https://i.ytimg.com/vi/euCqAq6BRa4/hqdefault.jpg?sqp=-oaymwEgCNACELwBSFXyq4qpAxIIARUAAIhCGAFwAcABBrgC8xg=&rs=AOn4CLDohgpb2pBRT0I2x0NJiDghKYbSkA",
        "channelName": "DJ Snake"
      },
      {
        "url": "https://www.youtube.com/watch?v=V9PVRfjEBTI",
        "title": "Billie Eilish - BIRDS OF A FEATHER (Official Music Video)",
        "publishedAt": "1 year ago",
        "viewCount": 894000000,
        "durationSeconds": 231,
        "thumbnailUrl": "https://i.ytimg.com/vi/V9PVRfjEBTI/hqdefault.jpg?sqp=-oaymwEgCNACELwBSFXyq4qpAxIIARUAAIhCGAFwAcABBrgC8xg=&rs=AOn4CLBvvxAwBQjBvuWLg_hCUQMH6nfFXA",
        "channelName": "Billie Eilish"
      },
      {
        "url": "https://www.youtube.com/watch?v=q4lU1N3oqYQ",
        "title": "Madison Beer - lovergirl (Official Music Video)",
        "publishedAt": "2 months ago",
        "viewCount": 2400000,
        "durationSeconds": 202,
        "thumbnailUrl": "https://i.ytimg.com/vi/q4lU1N3oqYQ/hqdefault.jpg?sqp=-oaymwEgCNACELwBSFXyq4qpAxIIARUAAIhCGAFwAcABBrgC8xg=&rs=AOn4CLDHwDbvQb7vLyC4A9CadeUa1Zit0w",
        "channelName": "Madison Beer"
      }
    ]
  },
  "youtube-playlist-videos": {
    "url": "https://www.youtube.com/playlist?list=PLMC9KNkIncKtPzgY-5rmhvj7fax8fdxoj",
    "totalReturned": 5,
    "videos": [
      {
        "url": "https://www.youtube.com/watch?v=ekr2nIex040",
        "title": "ROSÉ & Bruno Mars - APT. (Official Music Video)",
        "publishedAt": "1 year ago",
        "viewCount": 2500000000,
        "durationSeconds": 174,
        "thumbnailUrl": "https://i.ytimg.com/vi/ekr2nIex040/hqdefault.jpg?sqp=-oaymwEgCNACELwBSFXyq4qpAxIIARUAAIhCGAFwAcABBrgC8xg=&rs=AOn4CLDzyvnY8qeogjw9kGhO1TPZkM12-A",
        "channelName": "ROSÉ and Bruno Mars"
      },
      {
        "url": "https://www.youtube.com/watch?v=kPa7bsKwL-c",
        "title": "Lady Gaga, Bruno Mars - Die With A Smile (Official Music Video)",
        "publishedAt": "1 year ago",
        "viewCount": 1700000000,
        "durationSeconds": 253,
        "thumbnailUrl": "https://i.ytimg.com/vi/kPa7bsKwL-c/hqdefault.jpg?sqp=-oaymwEgCNACELwBSFXyq4qpAxIIARUAAIhCGAFwAcABBrgC8xg=&rs=AOn4CLDF3iMqsC6OQclYtXdkxhPQUpKHUA",
        "channelName": "Lady Gaga"
      },
      {
        "url": "https://www.youtube.com/watch?v=euCqAq6BRa4",
        "title": "DJ Snake - Let Me Love You (Official Music Video) ft. Justin Bieber",
        "publishedAt": "9 years ago",
        "viewCount": 2000000000,
        "durationSeconds": 206,
        "thumbnailUrl": "https://i.ytimg.com/vi/euCqAq6BRa4/hqdefault.jpg?sqp=-oaymwEgCNACELwBSFXyq4qpAxIIARUAAIhCGAFwAcABBrgC8xg=&rs=AOn4CLDohgpb2pBRT0I2x0NJiDghKYbSkA",
        "channelName": "DJ Snake"
      },
      {
        "url": "https://www.youtube.com/watch?v=V9PVRfjEBTI",
        "title": "Billie Eilish - BIRDS OF A FEATHER (Official Music Video)",
        "publishedAt": "1 year ago",
        "viewCount": 894000000,
        "durationSeconds": 231,
        "thumbnailUrl": "https://i.ytimg.com/vi/V9PVRfjEBTI/hqdefault.jpg?sqp=-oaymwEgCNACELwBSFXyq4qpAxIIARUAAIhCGAFwAcABBrgC8xg=&rs=AOn4CLBvvxAwBQjBvuWLg_hCUQMH6nfFXA",
        "channelName": "Billie Eilish"
      },
      {
        "url": "https://www.youtube.com/watch?v=q4lU1N3oqYQ",
        "title": "Madison Beer - lovergirl (Official Music Video)",
        "publishedAt": "2 months ago",
        "viewCount": 2400000,
        "durationSeconds": 202,
        "thumbnailUrl": "https://i.ytimg.com/vi/q4lU1N3oqYQ/hqdefault.jpg?sqp=-oaymwEgCNACELwBSFXyq4qpAxIIARUAAIhCGAFwAcABBrgC8xg=&rs=AOn4CLDHwDbvQb7vLyC4A9CadeUa1Zit0w",
        "channelName": "Madison Beer"
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
        "publishedAt": "10 days ago",
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
        ]
      },
      {
        "type": "video",
        "id": "L9NMRKYS6w4",
        "url": "https://www.youtube.com/watch?v=L9NMRKYS6w4",
        "title": "James Webb Detected a Sign of a Different Universe That Shattered Every Model Built Since Einstein",
        "publishedAt": "2 months ago",
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
        "badges": []
      },
      {
        "type": "video",
        "id": "Au2l6Nofx0E",
        "url": "https://www.youtube.com/watch?v=Au2l6Nofx0E",
        "title": "Why Space Gets More Terrifying the Further You Travel",
        "publishedAt": "3 weeks ago",
        "viewCount": 45420,
        "durationSeconds": 7439,
        "thumbnailUrl": "https://i.ytimg.com/vi/Au2l6Nofx0E/hq720.jpg?sqp=-oaymwEcCNAFEJQDSFXyq4qpAw4IARUAAIhCGAFwAcABBg==&rs=AOn4CLDqNYbuQDzmLSgFoZ9jjTAwu3hDZg",
        "channelName": "Calm Space",
        "channelId": "UCXyJmt3PKv0fbsU9DtcreEw",
        "channel": {
          "id": "UCXyJmt3PKv0fbsU9DtcreEw",
          "title": "Calm Space",
          "handle": "@CalmSpaceToSleep",
          "url": "https://www.youtube.com/@CalmSpaceToSleep",
          "thumbnail": null
        },
        "badges": []
      },
      {
        "type": "video",
        "id": "3Z8n43yp-mg",
        "url": "https://www.youtube.com/watch?v=3Z8n43yp-mg",
        "title": "3 Hours Of Facts About Space And Our Solar System",
        "publishedAt": "1 year ago",
        "viewCount": 506443,
        "durationSeconds": 10922,
        "thumbnailUrl": "https://i.ytimg.com/vi/3Z8n43yp-mg/hq720.jpg?sqp=-oaymwEcCNAFEJQDSFXyq4qpAw4IARUAAIhCGAFwAcABBg==&rs=AOn4CLA5ZCCpBoxl_OMCWz4cWPE8nCa40w",
        "channelName": "Spark",
        "channelId": "UCMV3aTOwUtG5vwfH9_rzb2w",
        "channel": {
          "id": "UCMV3aTOwUtG5vwfH9_rzb2w",
          "title": "Spark",
          "handle": "@SparkDocs",
          "url": "https://www.youtube.com/@SparkDocs",
          "thumbnail": null
        },
        "badges": [
          "Verified"
        ]
      },
      {
        "type": "video",
        "id": "ir8jMyLBS6k",
        "url": "https://www.youtube.com/watch?v=ir8jMyLBS6k",
        "title": "1 Hour of Mind-Blowing Space Facts Scientists Can’t Ignore",
        "publishedAt": "4 weeks ago",
        "viewCount": 72726,
        "durationSeconds": 3632,
        "thumbnailUrl": "https://i.ytimg.com/vi/ir8jMyLBS6k/hq720.jpg?sqp=-oaymwEcCNAFEJQDSFXyq4qpAw4IARUAAIhCGAFwAcABBg==&rs=AOn4CLD_eVVLviIcny85Etou6tqf2noKlw",
        "channelName": "Astral Curiosity",
        "channelId": "UCd6DpEsZHe5vadiZQ7JssNw",
        "channel": {
          "id": "UCd6DpEsZHe5vadiZQ7JssNw",
          "title": "Astral Curiosity",
          "handle": "@astralcuriosity",
          "url": "https://www.youtube.com/@astralcuriosity",
          "thumbnail": null
        },
        "badges": []
      }
    ],
    "videos": [
      {
        "type": "video",
        "id": "jFlWwhPRbPw",
        "url": "https://www.youtube.com/watch?v=jFlWwhPRbPw",
        "title": "James Webb Found a Structure So Big It Breaks Known Physics",
        "publishedAt": "10 days ago",
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
        ]
      },
      {
        "type": "video",
        "id": "L9NMRKYS6w4",
        "url": "https://www.youtube.com/watch?v=L9NMRKYS6w4",
        "title": "James Webb Detected a Sign of a Different Universe That Shattered Every Model Built Since Einstein",
        "publishedAt": "2 months ago",
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
        "badges": []
      },
      {
        "type": "video",
        "id": "Au2l6Nofx0E",
        "url": "https://www.youtube.com/watch?v=Au2l6Nofx0E",
        "title": "Why Space Gets More Terrifying the Further You Travel",
        "publishedAt": "3 weeks ago",
        "viewCount": 45420,
        "durationSeconds": 7439,
        "thumbnailUrl": "https://i.ytimg.com/vi/Au2l6Nofx0E/hq720.jpg?sqp=-oaymwEcCNAFEJQDSFXyq4qpAw4IARUAAIhCGAFwAcABBg==&rs=AOn4CLDqNYbuQDzmLSgFoZ9jjTAwu3hDZg",
        "channelName": "Calm Space",
        "channelId": "UCXyJmt3PKv0fbsU9DtcreEw",
        "channel": {
          "id": "UCXyJmt3PKv0fbsU9DtcreEw",
          "title": "Calm Space",
          "handle": "@CalmSpaceToSleep",
          "url": "https://www.youtube.com/@CalmSpaceToSleep",
          "thumbnail": null
        },
        "badges": []
      },
      {
        "type": "video",
        "id": "3Z8n43yp-mg",
        "url": "https://www.youtube.com/watch?v=3Z8n43yp-mg",
        "title": "3 Hours Of Facts About Space And Our Solar System",
        "publishedAt": "1 year ago",
        "viewCount": 506443,
        "durationSeconds": 10922,
        "thumbnailUrl": "https://i.ytimg.com/vi/3Z8n43yp-mg/hq720.jpg?sqp=-oaymwEcCNAFEJQDSFXyq4qpAw4IARUAAIhCGAFwAcABBg==&rs=AOn4CLA5ZCCpBoxl_OMCWz4cWPE8nCa40w",
        "channelName": "Spark",
        "channelId": "UCMV3aTOwUtG5vwfH9_rzb2w",
        "channel": {
          "id": "UCMV3aTOwUtG5vwfH9_rzb2w",
          "title": "Spark",
          "handle": "@SparkDocs",
          "url": "https://www.youtube.com/@SparkDocs",
          "thumbnail": null
        },
        "badges": [
          "Verified"
        ]
      },
      {
        "type": "video",
        "id": "ir8jMyLBS6k",
        "url": "https://www.youtube.com/watch?v=ir8jMyLBS6k",
        "title": "1 Hour of Mind-Blowing Space Facts Scientists Can’t Ignore",
        "publishedAt": "4 weeks ago",
        "viewCount": 72726,
        "durationSeconds": 3632,
        "thumbnailUrl": "https://i.ytimg.com/vi/ir8jMyLBS6k/hq720.jpg?sqp=-oaymwEcCNAFEJQDSFXyq4qpAw4IARUAAIhCGAFwAcABBg==&rs=AOn4CLD_eVVLviIcny85Etou6tqf2noKlw",
        "channelName": "Astral Curiosity",
        "channelId": "UCd6DpEsZHe5vadiZQ7JssNw",
        "channel": {
          "id": "UCd6DpEsZHe5vadiZQ7JssNw",
          "title": "Astral Curiosity",
          "handle": "@astralcuriosity",
          "url": "https://www.youtube.com/@astralcuriosity",
          "thumbnail": null
        },
        "badges": []
      }
    ],
    "shorts": [],
    "channels": [],
    "playlists": []
  },
  "youtube-shorts-comments": {
    "url": "https://www.youtube.com/watch?v=DXVHmGoCTco",
    "videoId": "DXVHmGoCTco",
    "totalReturned": 2,
    "totalComments": 172101,
    "nextCursor": "Eg0SC0RYVkhtR29DVGNvGAYyJSIRIgtEWFZIbUdvQ1RjbzAAeAJCEGNvbW1lbnRzLXNlY3Rpb24%3D",
    "hasMore": true,
    "comments": [
      {
        "id": "UgzoTD5YBfsX4xvnclx4AaABAg",
        "author": "@MrBeast",
        "authorAvatarUrl": "https://yt3.ggpht.com/nxYrc_1_2f77DoBadyxMTmv7ZpRZapHR5jbuYe7PlPd5cIRJxtNNEYyOC0ZsxaDyJJzXrnJiuDE=s88-c-k-c0x00ffffff-no-rj",
        "authorIsVerified": true,
        "authorIsChannelOwner": true,
        "text": "Who is your favorite streamer?",
        "likeCount": 69000,
        "replyCount": 907,
        "hasCreatorHeart": true,
        "publishedTimeText": "3 months ago (edited)"
      },
      {
        "id": "UgyQ5z9f7wcaa6tM1hB4AaABAg",
        "author": "@NoOne-p8b",
        "authorAvatarUrl": "https://yt3.ggpht.com/ytc/AIdro_kVrDUhBwT9mRE2gmGtChvxhznEB5UPX2XPBtWPAOOek_gveCxp4-WhcCMLH1t7oFAkEQ=s88-c-k-c0x00ffffff-no-rj",
        "authorIsVerified": false,
        "authorIsChannelOwner": false,
        "text": "Rakai is a type of guy who everyone wants to avoid, but still sticks around like a parasite.",
        "likeCount": 20000,
        "replyCount": 70,
        "hasCreatorHeart": true,
        "publishedTimeText": "3 months ago"
      }
    ]
  },
  "youtube-shorts-stats": {
    "url": "https://www.youtube.com/watch?v=DXVHmGoCTco",
    "id": "DXVHmGoCTco",
    "title": "50 Streamers Fight for $1,000,000",
    "description": "i can't believe we got all these streamers together in one place lol\n\nShopify empowers creators every single day to be entrepreneurs, founders, and CEOs. Now it’s your turn. Go to https://www.shopify.com/mrbeast to start your business today. \n\nTomorrow for the livestream, join the chat and make sure your instagram or twitter handle is viewable on your YouTube bio, so I can contact you if you win!\n\nCheck out the best PC's in the Universe at https://starforgepc.com/MrBeast\n\nSUB TO ALL CHANNELS\nwww.youtube.com/@UCX6OQ3DkcsbYNE6H8uQQuVA\nwww.youtube.com/@UC4-79UOlP48-QNGgCko5p2g \nwww.youtube.com/@UCIPPMRA040LQr5QPyJEbmXA \nwww.youtube.com/@UCUaT_39o1x6qWjz7K2pWcgw \nwww.youtube.com/@UCAiLfjNXkNv24uhpzUgPa6A \nwww.youtube.com/@UCZzvDDvaYti8Dd8bLEiSoyQ \n\nNew Merch - https://mrbeast.store/\nCheck out Viewstats! - https://www.viewstats.com/\n\nFor any questions or inquiries regarding this video, please reach out to chucky@mrbeastbusiness.com\n\nMusic Provided by https://www.extrememusic.com/\n----------------------------------------------------------------\nfollow all of these or i will kick you\n• Facebook - https://www.facebook.com/MrBeast/\n• Twitter - https://twitter.com/MrBeast\n•  Instagram - https://www.instagram.com/mrbeast\n•  Im Hiring! - https://www.mrbeastjobs.com/\n--------------------------------------------------------------------",
    "channelName": "MrBeast",
    "channelId": "UCX6OQ3DkcsbYNE6H8uQQuVA",
    "channelUrl": "https://www.youtube.com/channel/UCX6OQ3DkcsbYNE6H8uQQuVA",
    "publishedAt": "2026-04-04T09:00:01-07:00",
    "durationSeconds": 2971,
    "durationFormatted": "00:49:31",
    "viewCount": 115496756,
    "likeCount": 2653520,
    "commentCount": 172100,
    "thumbnailUrl": "https://i.ytimg.com/vi_webp/DXVHmGoCTco/maxresdefault.webp",
    "genre": "Entertainment",
    "tags": []
  },
  "youtube-shorts-summarizer": {
    "url": "https://www.youtube.com/watch?v=DXVHmGoCTco",
    "videoId": "DXVHmGoCTco",
    "title": "50 Streamers Fight for $1,000,000",
    "summary": "In an intense and entertaining competition, 50 of the biggest streamers are trapped in a cube, competing for a chance to win a million dollars. The challenges range from paintball elimination rounds to blindfolded games involving a Lamborghini, and eventually culminate in a series of strategic video game battles. Throughout the competition, alliances form and rivalries ignite as streamers navigate the high-stakes environment, showcasing their gaming skills and personalities.  ...",
    "keyPoints": [
      "50 top streamers are locked in a cube competing for a million dollars.",
      "Challenges include paintball elimination, blindfolded Lamborghini competition, and Fortnite battles."
    ],
    "topics": [
      "streamers",
      "competition"
    ],
    "sentiment": "positive"
  },
  "youtube-shorts-transcript": {
    "url": "https://www.youtube.com/watch?v=DXVHmGoCTco",
    "videoId": "DXVHmGoCTco",
    "title": "50 Streamers Fight for $1,000,000",
    "transcript": "I just TRAPPED 50 OF THE BIGGEST STREAMERS IN THIS CUBE AND WHOEVER LEAVES LAST WINS A MILLION DOLLARS. THESE ARE THE BIGGEST STREAMERS in the universe and the last one of them to leave wins it all. >> in together. We're locked in together. All right. Do we have like a Spanish alliance going? >> Yeah, it's the power of friendship. >> it's all about strategy in here. Me, I'm willing to do anything. You want me to get on the floor and start twerking, I'll do it. I don't. Just s ...",
    "transcriptSegments": [
      {
        "text": "I just TRAPPED 50 OF THE BIGGEST",
        "start": 0,
        "duration": 3.6,
        "timestamp": "00:00"
      },
      {
        "text": "STREAMERS IN THIS CUBE AND WHOEVER",
        "start": 1.84,
        "duration": 3.76,
        "timestamp": "00:01"
      }
    ],
    "wordCount": 7312,
    "segments": 1273,
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
      },
      {
        "url": "https://www.youtube.com/shorts/ERXFiAub3jE",
        "title": "What's Trending Across America Right Now?",
        "viewCount": 11
      },
      {
        "url": "https://www.youtube.com/shorts/7c4L1eQeJi4",
        "title": "TikTok Trends Edits ☘️🔥 #trend #edit #shorts",
        "viewCount": 14000000
      },
      {
        "url": "https://www.youtube.com/shorts/14pQPufUzj4",
        "title": "BEN EAGLE - Heartbreaking carelessness #MartialArts #ActionComedy #KungFu #Kindness #Trending #Viral",
        "viewCount": 7300000
      }
    ]
  },
  "youtube-video-details": {
    "url": "https://www.youtube.com/watch?v=dQw4w9WgXcQ",
    "id": "dQw4w9WgXcQ",
    "title": "Rick Astley - Never Gonna Give You Up (Official Video) (4K Remaster)",
    "description": "The official video for “Never Gonna Give You Up” by Rick Astley. \n\nNever: The Autobiography 📚 OUT NOW! \nFollow this link to get your copy and listen to Rick’s ‘Never’ playlist ❤️ #RickAstleyNever\nhttps://linktr.ee/rickastleynever\n\n“Never Gonna Give You Up” was a global smash on its release in July 1987, topping the charts in 25 countries including Rick’s native UK and the US Billboard Hot 100.  It also won the Brit Award for Best single in 1988. Stock Aitken and Waterman wrote and produced the track which was the lead-off single and lead track from Rick’s debut LP “Whenever You Need Somebody”.  The album was itself a UK number one and would go on to sell over 15 million copies worldwide.\n\nThe legendary video was directed by Simon West – who later went on to make Hollywood blockbusters such as Con Air, Lara Croft – Tomb Raider and The Expendables 2.  The video passed the 1bn YouTube views milestone on 28 July 2021.\n\nSubscribe to the official Rick Astley YouTube channel: https://RickAstley.lnk.to/YTSubID\n\nFollow Rick Astley:\nFacebook: https://RickAstley.lnk.to/FBFollowID \nTwitter: https://RickAstley.lnk.to/TwitterID \nInstagram: https://RickAstley.lnk.to/InstagramID \nWebsite: https://RickAstley.lnk.to/storeID \nTikTok: https://RickAstley.lnk.to/TikTokID\n\nListen to Rick Astley:\nSpotify: https://RickAstley.lnk.to/SpotifyID \nApple Music: https://RickAstley.lnk.to/AppleMusicID \nAmazon Music: https://RickAstley.lnk.to/AmazonMusicID \nDeezer: https://RickAstley.lnk.to/DeezerID \n\nLyrics:\nWe’re no strangers to love\nYou know the rules and so do I\nA full commitment’s what I’m thinking of\nYou wouldn’t get this from any other guy\n\nI just wanna tell you how I’m feeling\nGotta make you understand\n\nNever gonna give you up\nNever gonna let you down\nNever gonna run around and desert you\nNever gonna make you cry\nNever gonna say goodbye\nNever gonna tell a lie and hurt you\n\nWe’ve known each other for so long\nYour heart’s been aching but you’re too shy to say it\nInside we both know what’s been going on\nWe know the game and we’re gonna play it\n\nAnd if you ask me how I’m feeling\nDon’t tell me you’re too blind to see\n\nNever gonna give you up\nNever gonna let you down\nNever gonna run around and desert you\nNever gonna make you cry\nNever gonna say goodbye\nNever gonna tell a lie and hurt you\n\n#RickAstley #NeverGonnaGiveYouUp #WheneverYouNeedSomebody #OfficialMusicVideo",
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
      "Never Gonna Give You Up",
      "nggyu",
      "never gonna give you up lyrics",
      "rick rolled"
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

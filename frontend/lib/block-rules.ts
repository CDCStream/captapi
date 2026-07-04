export interface BlockRule {
  question: string;
  answer: string;
  /** yes = it happens / they can, no = it doesn't / they can't, partial = depends */
  verdict: "yes" | "no" | "partial";
}

export interface PlatformBlockRules {
  platform: string;
  emoji: string;
  notified: boolean;
  summary: string;
  rules: BlockRule[];
}

export const BLOCK_RULES: PlatformBlockRules[] = [
  {
    platform: "Instagram",
    emoji: "\ud83d\udcf7",
    notified: false,
    summary:
      "No notification is sent. Your profile shows \u201cNo posts yet\u201d or becomes unfindable to them, likes and comments you left disappear from their view, and DMs stay in the list but messages won't deliver.",
    rules: [
      { question: "Will they get a notification?", answer: "No. Instagram never announces a block.", verdict: "no" },
      { question: "Can they still see my profile?", answer: "Searching your handle returns nothing, or the profile shows \u201cNo posts yet\u201d with 0 posts if opened from an old link.", verdict: "no" },
      { question: "What happens to our DMs?", answer: "The old conversation stays in their inbox, but new messages they send are never delivered. No \u201cseen\u201d receipts appear.", verdict: "partial" },
      { question: "Do my likes and comments disappear?", answer: "Yes \u2014 your past likes and comments on their posts are removed from their view (restored if you unblock).", verdict: "yes" },
      { question: "Can they find me from another account?", answer: "Yes, unless you also enable \u201cblock new accounts they may create\u201d, which Instagram offers when blocking.", verdict: "partial" },
    ],
  },
  {
    platform: "Facebook",
    emoji: "\ud83d\udc65",
    notified: false,
    summary:
      "No notification. You disappear from their search, friends list, and Messenger. Old comments remain but show as an unclickable name. Group memberships and shared events are the main giveaway.",
    rules: [
      { question: "Will they get a notification?", answer: "No. Facebook stays silent about blocks.", verdict: "no" },
      { question: "Can they still see my profile?", answer: "No \u2014 your profile is unsearchable and links to it show a broken page.", verdict: "no" },
      { question: "What happens on Messenger?", answer: "The thread stays but they can't message you. Blocking on Facebook also blocks on Messenger; blocking only on Messenger still lets them see your Facebook profile.", verdict: "partial" },
      { question: "Do my old comments disappear?", answer: "Old comments and tags remain visible to them, but your name is unclickable and your photo is generic.", verdict: "partial" },
      { question: "Are we removed as friends?", answer: "Yes \u2014 blocking unfriends automatically, and unblocking does NOT restore the friendship.", verdict: "yes" },
    ],
  },
  {
    platform: "Snapchat",
    emoji: "\ud83d\udc7b",
    notified: false,
    summary:
      "No notification. You vanish from their friends list and chat feed; searching your username returns nothing. Snaps they send appear to go through but are never delivered. Streaks are destroyed.",
    rules: [
      { question: "Will they get a notification?", answer: "No. The block is silent.", verdict: "no" },
      { question: "Can they still find my username?", answer: "No \u2014 search returns nothing (whereas if you only removed them as a friend, your name still appears).", verdict: "no" },
      { question: "What happens to snaps they send?", answer: "They appear to send but show \u201cpending\u201d or are simply never delivered. No error message reveals the block.", verdict: "partial" },
      { question: "Does our streak survive?", answer: "No \u2014 blocking (or even losing 24 hours to it) kills the streak permanently.", verdict: "no" },
      { question: "How can they tell the difference from a deleted account?", answer: "They can't from your profile alone \u2014 but if a mutual friend can still find you in search, they've been blocked.", verdict: "partial" },
    ],
  },
  {
    platform: "WhatsApp",
    emoji: "\ud83d\udcac",
    notified: false,
    summary:
      "No notification, but WhatsApp leaks the most clues: their messages show one grey check mark forever, your profile photo and last-seen disappear for them, and calls never connect.",
    rules: [
      { question: "Will they get a notification?", answer: "No \u2014 but the pattern of clues below makes WhatsApp blocks the easiest to guess.", verdict: "no" },
      { question: "What do their messages look like?", answer: "One grey check mark (sent) that never becomes two (delivered). This is the classic sign \u2014 though it also happens if your phone is off for a long time.", verdict: "partial" },
      { question: "Can they see my profile photo or status?", answer: "No \u2014 your photo, about, status updates, and last-seen all disappear for them.", verdict: "no" },
      { question: "Can they call me?", answer: "Calls ring on their side but never connect. Group chats are the exception \u2014 you both still see each other's messages in shared groups.", verdict: "no" },
      { question: "Can they still add me to groups?", answer: "No \u2014 attempting to add you fails, which is a definitive test for a block.", verdict: "no" },
    ],
  },
  {
    platform: "TikTok",
    emoji: "\ud83c\udfb5",
    notified: false,
    summary:
      "No notification. Your videos and profile become invisible to them, comments you left are hidden, and they can no longer message you. If they visit your profile from an old link they may see it marked private-like with no content.",
    rules: [
      { question: "Will they get a notification?", answer: "No. TikTok never reveals a block.", verdict: "no" },
      { question: "Can they see my videos?", answer: "No \u2014 your videos vanish from their feed, search, and your profile page as seen by them.", verdict: "no" },
      { question: "What happens to comments and duets?", answer: "Your comments on their videos are hidden from them, and they can't duet, stitch, or react to your content.", verdict: "no" },
      { question: "Can they message me?", answer: "No \u2014 the DM thread closes; sending fails or the conversation disappears.", verdict: "no" },
      { question: "Can they watch from a logged-out browser?", answer: "Yes \u2014 if your account is public, a logged-out session or a second account can still see everything.", verdict: "yes" },
    ],
  },
];

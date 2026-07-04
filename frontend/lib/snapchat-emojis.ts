// Snapchat emoji, symbol, and icon meanings, current as of 2026.

export interface SnapEmoji {
  emoji: string;
  name: string;
  meaning: string;
  category: "Friend" | "Charm" | "Symbol" | "Trophy";
}

export const SNAP_EMOJIS: SnapEmoji[] = [
  // Friend emojis
  { emoji: "💛", name: "Yellow heart", meaning: "#1 Best Friends — you send the most snaps to each other, and they do the same to you.", category: "Friend" },
  { emoji: "❤️", name: "Red heart", meaning: "#1 Best Friends with each other for two weeks straight.", category: "Friend" },
  { emoji: "💕", name: "Pink hearts", meaning: "#1 Best Friends with each other for two months straight.", category: "Friend" },
  { emoji: "😊", name: "Smiling face", meaning: "One of your Best Friends — you send them a lot of snaps, but not the most.", category: "Friend" },
  { emoji: "😎", name: "Face with sunglasses", meaning: "A mutual Best Friend — one of their best friends is also one of yours.", category: "Friend" },
  { emoji: "😬", name: "Grimacing face", meaning: "Your #1 Best Friend is their #1 Best Friend too — you snap the same person the most.", category: "Friend" },
  { emoji: "😏", name: "Smirking face", meaning: "You are their Best Friend, but they are not yours — they snap you a lot, you don't snap them back as much.", category: "Friend" },
  { emoji: "🔥", name: "Fire (Snapstreak)", meaning: "Snapstreak — you and this friend have snapped each other every day. The number shows the day count.", category: "Symbol" },
  { emoji: "💯", name: "Hundred", meaning: "A 100-day Snapstreak milestone.", category: "Symbol" },
  { emoji: "⌛", name: "Hourglass", meaning: "Your Snapstreak is about to end — snap them soon to keep it alive.", category: "Symbol" },
  { emoji: "🎂", name: "Birthday cake", meaning: "It's this friend's birthday today (if they've enabled Birthday Party).", category: "Symbol" },
  { emoji: "👶", name: "Baby", meaning: "You just became friends with this person on Snapchat.", category: "Symbol" },
  // Symbols / icons
  { emoji: "🟢", name: "Green dot", meaning: "This friend is currently active in the app right now.", category: "Symbol" },
  { emoji: "🔵", name: "Blue dot", meaning: "Indicates an unread chat or a new message in some views.", category: "Symbol" },
  { emoji: "📍", name: "Location pin", meaning: "Shows a friend's location on the Snap Map (if they share it).", category: "Symbol" },
  { emoji: "👻", name: "Ghost (Snapcode)", meaning: "The Snapchat logo / your Snapcode — scan it to add friends.", category: "Symbol" },
  { emoji: "⭐", name: "Star", meaning: "This person has replayed one of your snaps in the last 24 hours.", category: "Symbol" },
  { emoji: "🚫", name: "Grey / no-entry", meaning: "A pending friend request or a snap that couldn't be delivered (they haven't added you back).", category: "Symbol" },
  { emoji: "🔒", name: "Lock", meaning: "A Private Story \u2014 the friend added you to a story only selected people can see. On stories in Discover, it can also mark subscriber-only content.", category: "Symbol" },
  // Send/receive status arrows
  { emoji: "➡️", name: "Filled red arrow", meaning: "You sent a Snap without audio.", category: "Symbol" },
  { emoji: "🟪", name: "Filled purple arrow", meaning: "You sent a Snap with audio.", category: "Symbol" },
  { emoji: "💬", name: "Filled blue arrow", meaning: "You sent a Chat message.", category: "Symbol" },
  // Charms
  { emoji: "👯", name: "BFF charm", meaning: "A Friendship Charm marking you as best friends — part of Snapchat's Charms.", category: "Charm" },
  { emoji: "♈", name: "Astrological charm", meaning: "Shows your and a friend's zodiac compatibility in Charms.", category: "Charm" },
  { emoji: "📅", name: "Friendversary charm", meaning: "Marks the anniversary of when you became Snapchat friends.", category: "Charm" },
  // Trophies (legacy Trophy Case)
  { emoji: "🏆", name: "Trophy Case", meaning: "Legacy achievements earned for using Snapchat features (largely replaced by Charms).", category: "Trophy" },
];

export const SNAP_CATEGORIES = ["All", "Friend", "Symbol", "Charm", "Trophy"] as const;

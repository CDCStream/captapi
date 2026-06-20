// The 46 hidden/secret TikTok emoji codes. Typing a code like [smile] inside
// the TikTok app (comments, captions, DMs) renders a custom emoticon. Codes are
// the same across iOS and Android. Images are served by the Emojipedia CDN.
// Single source of truth for the /tools/tiktok-emojis page and its client grid.

export interface TikTokEmoji {
  code: string; // e.g. "smile" -> used as [smile]
  name: string;
  meaning: string;
}

export const TIKTOK_EMOJIS: TikTokEmoji[] = [
  { code: "smile", name: "Smile", meaning: "A soft pink smiling face showing warmth, friendliness, or casual happiness." },
  { code: "happy", name: "Happy", meaning: "A peach face with squinty eyes and a big open mouth, expressing pure joy." },
  { code: "angry", name: "Angry", meaning: "A red face with furrowed brows, used to convey anger or displeasure." },
  { code: "cry", name: "Cry", meaning: "A sky-blue face with tears streaming down, for sadness or a dramatic reaction." },
  { code: "embarrassed", name: "Embarrassed", meaning: "A teal face with a sweat drop, looking nervous, shy, or caught off guard." },
  { code: "surprised", name: "Surprised", meaning: "A peach-pink face with wide eyes and open mouth, showing shock or disbelief." },
  { code: "wronged", name: "Wronged", meaning: "The famous shy face with two fingers pointing together, for bashful apology." },
  { code: "shout", name: "Shout", meaning: "A purple face with a wide open mouth, for loud, dramatic energy." },
  { code: "flushed", name: "Flushed", meaning: "A yellow face with blushing cheeks, indicating cute, flustered embarrassment." },
  { code: "yummy", name: "Yummy", meaning: "A face with tongue out and a thumbs up, meaning something is delicious." },
  { code: "complacent", name: "Complacent", meaning: "A blue face with sunglasses and a smug smile, for chill, quiet confidence." },
  { code: "drool", name: "Drool", meaning: "A face with heart eyes and drool, revealing craving or obsession." },
  { code: "scream", name: "Scream", meaning: "A pale blue face with wide eyes and open mouth, showing panic or fear." },
  { code: "weep", name: "Weep", meaning: "A face with teary eyes and trembling mouth, for quiet crying or sadness." },
  { code: "speechless", name: "Speechless", meaning: "An awkward expression with a sweat drop, for when you have no words." },
  { code: "funnyface", name: "Funny Face", meaning: "A silly face with tongue out and a wink, for goofiness or playful teasing." },
  { code: "laughwithtears", name: "Laugh With Tears", meaning: "A face laughing with tears, for over-the-top laughter or sarcastic humor." },
  { code: "wicked", name: "Wicked", meaning: "A purple devil face with a sly grin, for mischief or cheeky confidence." },
  { code: "facewithrollingeyes", name: "Face With Rolling Eyes", meaning: "A blank stare with rolling eyes, showing boredom or silent judgment." },
  { code: "sulk", name: "Sulk", meaning: "A pouty red face with a frown, for fake anger or playful pouting." },
  { code: "thinking", name: "Thinking", meaning: "A face with hand on chin and raised brow, for curiosity, doubt, or plotting." },
  { code: "lovely", name: "Lovely", meaning: "A blushing soft face with a kiss, warm and showing sweet admiration." },
  { code: "greedy", name: "Greedy", meaning: "A face with a greedy smile and dollar-sign eyes, for strong desire." },
  { code: "wow", name: "Wow", meaning: "An amazed open mouth and wide eyes, revealing awe or being impressed." },
  { code: "hehe", name: "Hehe", meaning: "A scribbly smiling face, for sneaky joy or a cheeky laugh." },
  { code: "joyful", name: "Joyful", meaning: "A bright face with closed eyes and a big smile, for pure happiness." },
  { code: "slap", name: "Slap", meaning: "A face with a raised palm, for a playful roast or a 'duh' moment." },
  { code: "tears", name: "Tears", meaning: "A face with streams of tears, for full-on emotional crying." },
  { code: "stun", name: "Stun", meaning: "Wide eyes and a shocked open mouth, telling disbelief or a freeze reaction." },
  { code: "cute", name: "Cute", meaning: "Wide open eyes and a blush, for charm or innocent flirting." },
  { code: "blink", name: "Blink", meaning: "A blushing smiling face with a wink, for bold, flirtatious confidence." },
  { code: "disdain", name: "Disdain", meaning: "A side-eye glare, revealing judgment, annoyance, or silent disgust." },
  { code: "astonish", name: "Astonish", meaning: "Sparkling eyes and a jaw-drop, for admiration or impressed shock." },
  { code: "rage", name: "Rage", meaning: "A fire-red face with yellow eyes, for explosive anger." },
  { code: "cool", name: "Cool", meaning: "A big smiling face with sunglasses, for chill confidence and swagger." },
  { code: "excited", name: "Excited", meaning: "Tightly closed eyes and a smiling open mouth, for pumped-up energy." },
  { code: "proud", name: "Proud", meaning: "A confident smirk with closed eyes, for self-love or accomplishment." },
  { code: "smileface", name: "Smile Face", meaning: "A scribbly white smile face, for simple cartoon-style happiness." },
  { code: "evil", name: "Evil", meaning: "A purple face with a sneaky grin, for mock evil or a chaotic mood." },
  { code: "angel", name: "Angel", meaning: "A white face with a halo and soft smile, for innocence or kindness." },
  { code: "laugh", name: "Laugh", meaning: "A wide smile with tear-drops, for a casual LOL reaction." },
  { code: "pride", name: "Pride", meaning: "A blushing-confident face with closed eyes, for self-expression or pride." },
  { code: "nap", name: "Nap", meaning: "Closed eyes with 'zzz', for tiredness or being in chill mode." },
  { code: "loveface", name: "Love Face", meaning: "Heart eyes, open mouth, and a blush, for deep love or affection." },
  { code: "awkward", name: "Awkward", meaning: "A flat look with small eyes and a nervous smile, for cringe or tension." },
  { code: "shock", name: "Shock", meaning: "Huge round eyes and a jaw-drop, for dramatic amazement or panic." },
];

/** Emojipedia CDN image for a TikTok emoji code. */
export function tiktokEmojiImage(code: string): string {
  return "https://em-content.zobj.net/content/2020/07/27/" + code + ".png";
}

import { JsonLd } from "@/components/seo/json-ld";
import { buildMetadata, breadcrumbLd, faqLd } from "@/lib/seo";
import { ToolHero, HowToUse, FAQSection, LongContent, ToolCTA, webApplicationLd } from "@/components/tools/tool-sections";
import { AiToolClient, type AiToolConfig } from "@/components/tools/ai-tool-client";
import { PenLine, Sparkles, Check, Copy } from "lucide-react";

const PATH = "/tools/twitch-name-generator";
const TITLE = "Free Twitch Name Generator";
const DESC =
  "Generate 15 catchy Twitch username ideas for your stream — gaming, chill, funny, or edgy. All within Twitch's 4-25 character rules. AI-powered, free, no sign-up.";

export const metadata = buildMetadata({
  title: TITLE + " — Streamer Username Ideas | Captapi",
  description: DESC,
  path: PATH,
  keywords: [
    "twitch name generator",
    "twitch username generator",
    "twitch name ideas",
    "streamer name generator",
    "twitch username ideas",
    "good twitch names",
  ],
});

const CONFIG: AiToolConfig = {
  slug: "twitch-name-generator",
  submitLabel: "Generate names",
  fields: [
    {
      name: "interest",
      label: "What do you stream?",
      type: "text",
      required: true,
      placeholder: "e.g. valorant, cozy games, art streams",
      help: "Your main game or content style \u2014 specific beats generic.",
    },
    {
      name: "style",
      label: "Vibe",
      type: "select",
      options: [
        { value: "gamer", label: "Gamer" },
        { value: "funny", label: "Funny" },
        { value: "chill / cozy", label: "Chill / cozy" },
        { value: "edgy", label: "Edgy" },
        { value: "clean and brandable", label: "Clean & brandable" },
      ],
    },
  ],
};

const FAQS = [
  { q: "What are Twitch's username rules?", a: "4 to 25 characters, using only letters, numbers, and underscores. No spaces or special characters. Every suggestion this generator produces follows those rules, with the character count shown." },
  { q: "How do I check if a Twitch name is available?", a: "The signup page at twitch.tv/signup validates availability as you type. You can also visit twitch.tv/yourname — a 404 usually means it's free, though names of suspended or deactivated accounts can 404 while still being reserved." },
  { q: "Can I change my Twitch username later?", a: "Yes — Settings \u2192 Profile lets you change your username once every 60 days. Your old name is held for you-only reuse briefly, then eventually recycled. Your display name (capitalization) can be changed anytime." },
  { q: "What makes a good streamer name?", a: "Easy to say out loud (viewers and collab partners will speak it), easy to spell after hearing it once, and free of numbers-as-letter substitutions that make it impossible to find. Check that the matching names are free on TikTok, YouTube, and X before committing — clips travel across platforms." },
  { q: "Should my name reference the game I stream?", a: "Only if you're sure you'll stick with it. Game-specific names (e.g. containing \u201cValo\u201d) help discovery early but age badly when you switch games. Personality-based names survive every meta change." },
  { q: "Is this generator free?", a: "Yes — unlimited generations, no account required." },
];

const STEPS = [
  { title: "Describe your stream", text: "Main game or content style, a few words.", icon: <PenLine className="size-4" /> },
  { title: "Pick a vibe", text: "Gamer, funny, chill, edgy, or brandable.", icon: <Sparkles className="size-4" /> },
  { title: "Generate 15 names", text: "All within Twitch's 4-25 character rules.", icon: <Check className="size-4" /> },
  { title: "Check availability", text: "Copy your favorite and test it at twitch.tv/signup.", icon: <Copy className="size-4" /> },
];

export default function Page() {
  return (
    <>
      <JsonLd data={webApplicationLd({ name: TITLE, description: DESC, path: PATH, category: "UtilitiesApplication" })} />
      <JsonLd data={breadcrumbLd([{ name: "Tools", path: "/tools" }, { name: "Twitch Name Generator", path: PATH }])} />
      <JsonLd data={faqLd(FAQS)} />

      <ToolHero
        platform="Twitch"
        title="Twitch Name Generator"
        subtitle="Tell us what you stream and get 15 username ideas that fit Twitch's rules — memorable, speakable, and ready to check at signup."
      />

      <AiToolClient config={CONFIG} />

      <HowToUse steps={STEPS} />

      <LongContent>
        <div>
          <h2>Name your channel like a brand</h2>
          <p>
            Your Twitch name ends up everywhere clips go — TikTok compilations, YouTube highlights, Discord
            invites — so treat it as a cross-platform brand from day one. Before locking anything in, check
            the same handle on TikTok, YouTube, X, and Instagram; consistent handles make you findable when
            a clip goes viral somewhere you don&apos;t control. Short, pronounceable names win raids too:
            other streamers have to say your name out loud when they send their viewers over.
          </p>
        </div>
        <div>
          <h2>Patterns that work on Twitch</h2>
          <ul>
            <li><strong>Word + word:</strong> two unrelated short words (think &quot;Moonrise&quot; + &quot;Tactics&quot;) — brandable and usually available.</li>
            <li><strong>Name + descriptor:</strong> your nickname plus what you do (e.g. &quot;___Plays&quot;, &quot;___Draws&quot;).</li>
            <li><strong>Invented words:</strong> mashups that sound real — most memorable, always available.</li>
            <li><strong>Avoid:</strong> l33t substitutions, trailing number strings, and anything you'd have to spell out letter by letter in a raid.</li>
          </ul>
        </div>
      </LongContent>

      <FAQSection faqs={FAQS} />
      <ToolCTA
        headline="Building streamer tools?"
        sub="Captapi returns Twitch channel info, streams, and VODs plus TikTok, YouTube, and Instagram data as clean JSON. Start free with 100 credits."
      />
    </>
  );
}

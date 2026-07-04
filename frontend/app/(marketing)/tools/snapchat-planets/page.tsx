import { JsonLd } from "@/components/seo/json-ld";
import { buildMetadata, breadcrumbLd, faqLd } from "@/lib/seo";
import { ToolHero, FAQSection, LongContent, ToolCTA, webApplicationLd } from "@/components/tools/tool-sections";
import { SNAP_PLANETS } from "@/lib/snapchat-planets";

const PATH = "/tools/snapchat-planets";
const TITLE = "Snapchat Planets: Order & Meaning";
const DESC =
  "The full Snapchat Plus friend solar system explained — all 8 planets in order from Mercury to Neptune, what each one means, and how the Best Friends ranking works. Free.";

export const metadata = buildMetadata({
  title: TITLE + " — Friend Solar System Explained | Captapi",
  description: DESC,
  path: PATH,
  keywords: [
    "snapchat planets",
    "snapchat planet order",
    "snapchat planets in order",
    "snapchat planets meaning",
    "snapchat planets order best friends",
    "snapchat solar system",
    "what do snapchat planets mean",
  ],
});

const FAQS = [
  { q: "What are Snapchat planets?", a: "Snapchat planets are part of the Snapchat Plus \u201cFriend Solar System\u201d feature. If you are one of someone's top eight best friends, you are assigned a planet based on how close you are, with the person whose system it is acting as the sun. It is a paid feature, so only Snapchat Plus subscribers can see it." },
  { q: "What is the order of Snapchat planets?", a: "From closest to the sun outward: Mercury (1st best friend), Venus (2nd), Earth (3rd), Mars (4th), Jupiter (5th), Saturn (6th), Uranus (7th), and Neptune (8th). Mercury is the closest friend and Neptune is the most distant of the top eight." },
  { q: "Which Snapchat planet is the best friend?", a: "Mercury. As the planet closest to the sun, Mercury represents your #1 best friend \u2014 the person you interact with the most in that friend's solar system." },
  { q: "How do I see Snapchat planets?", a: "You need a Snapchat Plus subscription. Open a friend's Friendship Profile and tap the gold Best Friends badge next to their name. If you are in their top eight, it reveals your planet in their solar system. Without Snapchat Plus, you cannot see the planets." },
  { q: "Can I see my own planet in someone's solar system?", a: "Only the Snapchat Plus subscriber can see their own solar system. If your friend has Snapchat Plus and you are in their top eight, they can see which planet you are, but you cannot see your placement unless you subscribe and view your own system." },
  { q: "Do the planets change?", a: "Yes. The planets update as your interactions change. If you start talking to someone more or less, your planet can move closer to or further from the sun, or you can drop out of the top eight entirely." },
  { q: "What does it mean if there are hearts around a planet?", a: "Some planets are shown with hearts (Mercury with red hearts, Venus and Earth with colored hearts) while outer planets like Jupiter and Uranus have none. The hearts are just part of each planet's visual design and reflect its closeness ranking, not a separate status." },
];

export default function Page() {
  return (
    <>
      <JsonLd data={webApplicationLd({ name: TITLE, description: DESC, path: PATH, category: "ReferenceApplication" })} />
      <JsonLd data={breadcrumbLd([{ name: "Tools", path: "/tools" }, { name: TITLE, path: PATH }])} />
      <JsonLd data={faqLd(FAQS)} />

      <ToolHero
        platform="Snapchat"
        title={TITLE}
        subtitle="The Snapchat Plus friend solar system, decoded. Here are all eight planets in order from Mercury to Neptune and exactly what each one means about your friendship ranking."
      />

      <div className="mt-8 space-y-3">
        {SNAP_PLANETS.map((p) => (
          <div key={p.name} className="flex items-start gap-4 rounded-2xl border bg-card p-5">
            <div className={`flex size-12 shrink-0 items-center justify-center rounded-full ${p.color} text-xl shadow-inner`}>
              {p.emoji}
            </div>
            <div className="min-w-0">
              <div className="flex items-center gap-2">
                <span className="flex size-6 items-center justify-center rounded-full bg-muted text-xs font-bold">{p.order}</span>
                <h2 className="text-lg font-semibold">{p.name}</h2>
                <span className="text-sm text-muted-foreground">· #{p.order} best friend</span>
              </div>
              <p className="mt-1.5 text-sm leading-relaxed text-muted-foreground">{p.meaning}</p>
            </div>
          </div>
        ))}
      </div>

      <LongContent>
        <div>
          <h2>How the Snapchat friend solar system works</h2>
          <p>
            Snapchat Plus turns your closest friendships into a solar system. The subscriber is the sun, and
            their top eight friends orbit as planets. The closer the planet is to the sun, the stronger the
            friendship: Mercury is the number-one best friend and Neptune is the eighth. Snapchat decides the
            order using how often and how recently you two interact through Snaps and Chats.
          </p>
        </div>
        <div>
          <h2>Why you might not see a planet</h2>
          <p>
            The feature is exclusive to Snapchat Plus, the paid subscription. Only the subscriber can view
            their own solar system, and you only appear as a planet if you are in their top eight. If you are
            not subscribed, or you are not close enough to make the top eight, you will not see a planet at
            all. Planets also shift over time as your chat activity rises or falls.
          </p>
        </div>
      </LongContent>

      <FAQSection faqs={FAQS} />
      <ToolCTA
        headline="Working with social data?"
        sub="Captapi gives developers clean JSON for profiles, posts, comments, and stats across TikTok, YouTube, Instagram, and more. Start free with 100 credits, no card required."
      />
    </>
  );
}

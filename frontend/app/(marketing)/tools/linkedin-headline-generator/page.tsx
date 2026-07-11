import { JsonLd } from "@/components/seo/json-ld";
import { buildMetadata, breadcrumbLd, faqLd } from "@/lib/seo";
import { ToolHero, HowToUse, FAQSection, LongContent, ToolCTA, webApplicationLd } from "@/components/tools/tool-sections";
import { AiToolClient, type AiToolConfig } from "@/components/tools/ai-tool-client";
import { PenLine, Sparkles, Copy, Check } from "lucide-react";

const PATH = "/tools/linkedin-headline-generator";
const TITLE = "Free LinkedIn Headline Generator — 10 Recruiter-Ready Ideas";
const DESC =
  "Generate 10 LinkedIn headline ideas from your role, skills, and goal — keyword-rich and value-driven formats, all within the 220-character limit. AI-powered, free, no sign-up.";

export const metadata = buildMetadata({
  title: `${TITLE} | Captapi`,
  description: DESC,
  path: PATH,
  keywords: [
    "linkedin headline generator",
    "linkedin headline examples",
    "linkedin headline ideas",
    "best linkedin headlines",
    "linkedin headline for job seekers",
    "ai linkedin headline generator",
  ],
});

const CONFIG: AiToolConfig = {
  slug: "linkedin-headline-generator",
  submitLabel: "Generate headlines",
  fields: [
    {
      name: "role",
      label: "Your role or title",
      type: "text",
      required: true,
      placeholder: "e.g. Senior Backend Engineer",
      help: "Your current title, or the role you want to be found for.",
    },
    {
      name: "skills",
      label: "Key skills or niche",
      type: "text",
      placeholder: "e.g. Python, AWS, data pipelines",
      help: "2-4 skills or specialties you want recruiters to search you by.",
    },
    {
      name: "goal",
      label: "Main goal",
      type: "select",
      options: [
        { value: "attract recruiters", label: "Attract recruiters" },
        { value: "win freelance clients", label: "Win freelance clients" },
        { value: "build a personal brand", label: "Build a personal brand" },
        { value: "generate leads for my business", label: "Generate leads" },
      ],
    },
    {
      name: "style",
      label: "Style",
      type: "select",
      options: [
        { value: "professional", label: "Professional" },
        { value: "keyword-rich", label: "Keyword-rich" },
        { value: "bold", label: "Bold" },
        { value: "friendly", label: "Friendly" },
      ],
    },
  ],
};

const FAQS = [
  { q: "How long can a LinkedIn headline be?", a: "A LinkedIn headline can be up to 220 characters on desktop and in the mobile app. Only the first ~65-70 characters show in search results and feed posts, so put your most important keywords and value at the front. This tool keeps every suggestion within the 220-character limit." },
  { q: "What makes a good LinkedIn headline?", a: "A good headline says what you do, who you help, and the outcome you deliver - in words recruiters actually search. \u201cSenior Backend Engineer | Python, AWS | Building data pipelines that scale\u201d beats \u201cPassionate technologist\u201d because it is specific, credible, and keyword-rich." },
  { q: "Should I use keywords in my LinkedIn headline?", a: "Yes. The headline is one of the strongest fields in LinkedIn's search ranking. Include your role and 2-3 searchable skills (for example \u201cReact\u201d, \u201cSEO\u201d, \u201cproduct marketing\u201d) so you appear when recruiters filter candidates." },
  { q: "What should I avoid in a LinkedIn headline?", a: "Avoid buzzwords like guru, ninja, rockstar, visionary, and results-driven - they carry no search value and read as filler. Also avoid stuffing 10+ pipes of unrelated roles; focus on one clear positioning." },
  { q: "Can I use my headline if I'm job hunting?", a: "Yes - and it matters even more. Lead with the role you want (not just the one you have), add your top skills, and consider a subtle availability signal like \u201cOpen to new opportunities\u201d if you're comfortable making the search public." },
  { q: "What's the difference between a headline and an About section?", a: "The headline is the one-liner shown everywhere your name appears - search results, comments, connection requests. The About section is the longer story on your profile. Win attention with the headline; convert it with the About section." },
  { q: "Is this LinkedIn headline generator free?", a: "Yes. Generating, browsing, and copying headline ideas is completely free with no sign-up and no limit." },
];

const STEPS = [
  { title: "Describe your role", text: "Enter your title and the skills you want to be found for.", icon: <PenLine className="size-4" /> },
  { title: "Pick a goal and style", text: "Recruiters, clients, or personal brand - the goal shapes every suggestion.", icon: <Sparkles className="size-4" /> },
  { title: "Generate 10 ideas", text: "AI produces keyword-rich and value-driven headlines within 220 characters.", icon: <Check className="size-4" /> },
  { title: "Copy your favorite", text: "One-click copy, then paste it into your LinkedIn profile.", icon: <Copy className="size-4" /> },
];

export default function Page() {
  return (
    <>
      <JsonLd data={webApplicationLd({ name: TITLE, description: DESC, path: PATH, category: "UtilitiesApplication" })} />
      <JsonLd data={breadcrumbLd([{ name: "Tools", path: "/tools" }, { name: "LinkedIn Headline Generator", path: PATH }])} />
      <JsonLd data={faqLd(FAQS)} />

      <ToolHero
        platform="LinkedIn"
        title="LinkedIn Headline Generator"
        subtitle="Get 10 recruiter-ready LinkedIn headline ideas from your role, skills, and goal — keyword-rich and value-driven formats within the 220-character limit. AI-powered, free, no sign-up."
      />

      <AiToolClient config={CONFIG} />

      <HowToUse steps={STEPS} />

      <LongContent>
        <div>
          <h2>Why your LinkedIn headline matters more than you think</h2>
          <p>
            Your headline follows you everywhere on LinkedIn - under your name in search results, next to every comment you leave, in connection requests, and in the recruiter tools hiring teams use every day. It is also one of the strongest fields in LinkedIn&apos;s search ranking, which means the words you choose decide whether you show up when someone searches for your skills. A vague headline like &quot;Experienced professional&quot; makes you invisible; a specific one like &quot;Senior Backend Engineer | Python, AWS | Building data pipelines that scale&quot; gets you found and clicked.
          </p>
          <p>
            This free generator turns your role, skills, and goal into 10 ready-to-use options. It mixes two proven formats: keyword-rich headlines built for search (Role | Specialty | Outcome) and value-proposition headlines built for humans (&quot;I help X do Y&quot;). Every suggestion respects LinkedIn&apos;s 220-character limit, and a live counter flags anything that runs long.
          </p>
        </div>

        <div>
          <h2>Anatomy of a headline that gets clicks</h2>
          <p>The best-performing LinkedIn headlines usually combine three ingredients:</p>
          <ul>
            <li><strong>A searchable role.</strong> The exact title recruiters type into search - not a creative alternative.</li>
            <li><strong>2-3 concrete skills.</strong> Technologies, methods, or niches that qualify you at a glance.</li>
            <li><strong>An outcome or audience.</strong> Who you help and what changes because of your work.</li>
          </ul>
          <p>
            Remember that only the first 65-70 characters show in most surfaces, so front-load the part that matters most. If you are job hunting, lead with the role you want next rather than the one you have now.
          </p>
        </div>

        <div>
          <h2>Headline examples by goal</h2>
          <p>
            <strong>Attracting recruiters:</strong> &quot;Frontend Engineer | React, TypeScript, Next.js | Shipping accessible web apps at scale&quot;. <strong>Winning freelance clients:</strong> &quot;I help SaaS teams turn documentation into a growth channel | Technical Writer &amp; Docs Consultant&quot;. <strong>Building a brand:</strong> &quot;Writing about APIs, scraping, and the data behind social media | Developer &amp; Founder&quot;. Generate a batch, pick the angle that feels true, and edit one or two words until it sounds like you.
          </p>
        </div>
      </LongContent>

      <FAQSection faqs={FAQS} />
      <ToolCTA
        headline="Need LinkedIn data for your product?"
        sub="Captapi gives you APIs for LinkedIn profiles, companies, posts, and the ad library — plus TikTok, Instagram, YouTube, and more. Start free with one API key."
      />
    </>
  );
}

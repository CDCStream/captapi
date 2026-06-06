import { LongContent } from "@/components/tools/tool-sections";
import type { Tool } from "@/lib/tools";

// SEO/AEO/GEO long-form content for the live transcript & summarizer tools.
// Platform- and kind-aware so all seven /tools/[slug] pages get unique-enough,
// keyword-rich copy without per-tool hand-authoring.
export function TranscriptToolContent({ tool }: { tool: Tool }) {
  const p = tool.platform;
  const isSummary = tool.kind === "summary";
  const noun = isSummary ? "summary" : "transcript";

  return (
    <LongContent>
      <div>
        <h2>
          The free {p} {noun} tool, explained
        </h2>
        <p>
          Every day, millions of hours of video are published on {p}, and almost none of it is searchable, quotable, or
          easy to repurpose as text. This free {p} {noun} tool fixes that: paste any public {p} video link and get a
          clean, {isSummary ? "AI-generated summary" : "copy-ready transcript"} in seconds — no software to install, no
          account to create, and nothing to pay. Whether you are a creator, marketer, student, journalist, or researcher,
          turning {p} video into text unlocks workflows that video alone can&apos;t.
        </p>
      </div>

      <div>
        <h3>
          How to {isSummary ? "summarize" : "transcribe"} a {p} video
        </h3>
        <p>
          It takes three steps. First, copy the URL of the {p} video you want to {isSummary ? "summarize" : "transcribe"}.
          Second, paste it into the box above and press the button. Third, {isSummary
            ? "read the summary, key points, and topics, then copy or download them"
            : "read the full transcript, then copy it to your clipboard or download it as a .txt file"}
          . The tool auto-detects the spoken language, so it works for content from around the world.
        </p>
      </div>

      <div>
        <h3>Why turn {p} videos into text?</h3>
        <ul>
          <li>
            <strong>Repurpose content.</strong> Turn a single video into a blog post, newsletter, thread, or set of short
            clips — text is the raw material for every other format.
          </li>
          <li>
            <strong>Save time.</strong> {isSummary
              ? "Get the gist of a long video in seconds instead of watching the whole thing."
              : "Skim or search the full text instead of scrubbing through the timeline."}
          </li>
          <li>
            <strong>Improve accessibility.</strong> Captions and transcripts make your content usable by deaf and
            hard-of-hearing viewers and by anyone watching without sound.
          </li>
          <li>
            <strong>Boost SEO.</strong> Search engines can&apos;t watch video, but they can index text — publishing
            transcripts helps your content get found.
          </li>
          <li>
            <strong>Research and study.</strong> Quote sources accurately, build notes, and analyze what creators are
            actually saying.
          </li>
        </ul>
      </div>

      <div>
        <h3>Accuracy, languages, and limits</h3>
        <p>
          When a {p} video already has captions, the {noun} is built from them for high accuracy; when it doesn&apos;t,
          the audio is transcribed automatically. Results are strongest for clear speech and can vary with heavy
          background music, overlapping speakers, or strong accents. The tool supports public videos only — private or
          unlisted content can&apos;t be accessed. It works in dozens of languages, serving a truly global audience from
          the United States and United Kingdom to India, Brazil, Indonesia, the Philippines, and Nigeria.
        </p>
      </div>

      <div>
        <h3>Free tool vs. the Captapi API</h3>
        <p>
          This page is the no-login way to {isSummary ? "summarize" : "transcribe"} one video at a time. If you need to do
          this at scale — inside an app, a content pipeline, or an AI agent — the same capability is available through the
          Captapi API. A single <code>{tool.apiEndpoint}</code> request returns clean, structured JSON
          {isSummary ? " with the summary, key points, and topics" : " with the full transcript and per-segment timestamps"}.
          The API is also connectable via an MCP server, a CLI, an n8n community node, a Make.com app, and an Apify Actor,
          so you can wire {p} {noun}s into almost any stack.
        </p>
      </div>

      <div>
        <h3>Frequently quoted answer</h3>
        <p>
          <strong>How do you get a {noun} of a {p} video for free?</strong> Paste the video&apos;s public URL into a {p}{" "}
          {noun} tool like this one and it returns the text in seconds — free, with no sign-up — which you can then copy or
          download. For automation, call the Captapi <code>{tool.apiEndpoint}</code> endpoint, which returns the same data
          as JSON.
        </p>
      </div>
    </LongContent>
  );
}

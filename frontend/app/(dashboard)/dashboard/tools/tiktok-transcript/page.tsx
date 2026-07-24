import Link from "next/link";
import { DashboardTikTokTranscriptTool } from "@/components/dashboard/tiktok-transcript-tool";

export const metadata = {
  title: "TikTok Transcript | Dashboard",
  description: "Extract TikTok transcripts using your Captapi credits.",
};

export default function DashboardTikTokTranscriptPage() {
  return (
    <div className="mx-auto max-w-3xl space-y-6">
      <div>
        <p className="text-sm text-muted-foreground">
          <Link href="/dashboard" className="hover:text-foreground">
            Dashboard
          </Link>
          {" / "}
          <span>Tools</span>
          {" / "}
          <span className="text-foreground">TikTok Transcript</span>
        </p>
        <h1 className="mt-2 text-2xl font-semibold tracking-tight">TikTok Transcript</h1>
        <p className="mt-1 text-muted-foreground">
          Same free-tool experience, billed to your account — automate with the API when you need scale.
        </p>
      </div>
      <DashboardTikTokTranscriptTool />
    </div>
  );
}

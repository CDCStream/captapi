import { ENDPOINTS, type Platform } from "../catalog.js";
import { printJson, c } from "../client.js";

const PLATFORMS: Platform[] = [
  "youtube",
  "tiktok",
  "instagram",
  "facebook",
  "twitter",
  "reddit",
  "threads",
  "bluesky",
  "pinterest",
  "linkedin",
  "rumble",
];

/** Command name for an endpoint, e.g. youtube_transcript -> youtube-transcript. */
export function commandName(tool: string): string {
  return tool.replace(/_/g, "-");
}

export function list(
  platformArg: string | undefined,
  opts: { json?: boolean },
): void {
  const filter = platformArg?.toLowerCase();
  if (filter && !PLATFORMS.includes(filter as Platform)) {
    console.error(
      c.red(`Unknown platform "${platformArg}".`) +
        ` Choose one of: ${PLATFORMS.join(", ")}`,
    );
    process.exit(1);
  }

  const eps = ENDPOINTS.filter((e) => !filter || e.platform === filter);

  if (opts.json) {
    printJson(
      eps.map((e) => ({
        command: commandName(e.tool),
        platform: e.platform,
        path: e.path,
        credits: e.credits,
        params: e.params.map((p) => ({ name: p.name, required: p.required })),
        summary: e.summary,
      })),
    );
    return;
  }

  for (const platform of PLATFORMS) {
    const group = eps.filter((e) => e.platform === platform);
    if (!group.length) continue;
    console.log("\n" + c.bold(platform.toUpperCase()));
    for (const e of group) {
      const cmd = commandName(e.tool).padEnd(28);
      console.log(
        `  ${c.cyan(cmd)} ${c.dim(`${e.credits}cr`)}  ${e.summary}`,
      );
    }
  }
  console.log(
    "\n" +
      c.dim(
        `${eps.length} endpoints. Run \`captapi <command> --help\` for parameters.`,
      ),
  );
}

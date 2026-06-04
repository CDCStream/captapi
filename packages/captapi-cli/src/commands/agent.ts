import { homedir, platform as osPlatform } from "node:os";
import { join } from "node:path";
import {
  existsSync,
  mkdirSync,
  readFileSync,
  writeFileSync,
} from "node:fs";
import { dirname } from "node:path";
import { loadConfig } from "../config.js";
import { printJson, c } from "../client.js";

type AgentId = "claude" | "cursor";

/** Resolve the MCP config file path for a given agent + platform. */
function configFileFor(agent: AgentId): string {
  const home = homedir();
  if (agent === "cursor") return join(home, ".cursor", "mcp.json");
  // Claude Desktop
  const os = osPlatform();
  if (os === "win32")
    return join(
      process.env.APPDATA || join(home, "AppData", "Roaming"),
      "Claude",
      "claude_desktop_config.json",
    );
  if (os === "darwin")
    return join(
      home,
      "Library",
      "Application Support",
      "Claude",
      "claude_desktop_config.json",
    );
  return join(home, ".config", "Claude", "claude_desktop_config.json");
}

function serverEntry(apiKey?: string) {
  return {
    command: "npx",
    args: ["-y", "@captapi/mcp"],
    env: { CAPTAPI_API_KEY: apiKey || "capt_live_your_key_here" },
  };
}

export function agentAdd(
  agentArg: string,
  opts: { key?: string; print?: boolean },
): void {
  const agent = agentArg?.toLowerCase() as AgentId;
  if (agent !== "claude" && agent !== "cursor") {
    console.error(
      c.red(`Unknown agent "${agentArg}".`) + " Choose: claude | cursor",
    );
    process.exit(1);
  }

  const { apiKey } = loadConfig();
  const key = opts.key || apiKey;
  const entry = serverEntry(key);

  if (opts.print) {
    printJson({ mcpServers: { captapi: entry } });
    return;
  }

  if (!key) {
    console.error(
      c.yellow("Warning:") +
        " no API key found. Run `captapi login` first, or pass --key. " +
        "Writing config with a placeholder key.",
    );
  }

  const file = configFileFor(agent);
  let config: { mcpServers?: Record<string, unknown> } = {};
  if (existsSync(file)) {
    try {
      config = JSON.parse(readFileSync(file, "utf8"));
    } catch {
      console.error(
        c.red(`Could not parse existing config at ${file}.`) +
          " Fix or remove it, then retry.",
      );
      process.exit(1);
    }
  }

  config.mcpServers = config.mcpServers || {};
  const existed = "captapi" in config.mcpServers;
  config.mcpServers.captapi = entry;

  mkdirSync(dirname(file), { recursive: true });
  writeFileSync(file, JSON.stringify(config, null, 2) + "\n", "utf8");

  console.log(
    c.green(existed ? "Updated" : "Added") +
      ` Captapi MCP server in ${agent} config:\n  ${c.dim(file)}`,
  );
  console.log(
    c.dim(
      `Restart ${agent === "claude" ? "Claude Desktop" : "Cursor"} to load the server.`,
    ),
  );
}

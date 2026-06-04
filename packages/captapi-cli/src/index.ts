#!/usr/bin/env node
/**
 * Captapi CLI.
 *
 * Call every Captapi REST endpoint, check your credit balance, and wire
 * Captapi into AI agents — straight from the terminal.
 *
 * Auth: run `captapi login` (saves to ~/.captapi/config.json) or set
 * CAPTAPI_API_KEY. Base URL override: CAPTAPI_BASE_URL.
 */
import { Command, Option } from "commander";
import { ENDPOINTS, type Endpoint, type ToolParam } from "./catalog.js";
import { apiGet, printJson, ApiError, c, VERSION } from "./client.js";
import { commandName, list } from "./commands/list.js";
import { login, logout, whoami } from "./commands/auth.js";
import { balance } from "./commands/balance.js";
import { agentAdd } from "./commands/agent.js";

function runEndpoint(e: Endpoint, opts: Record<string, unknown>): void {
  const query: Record<string, string | number | undefined> = {};
  for (const p of e.params) {
    const v = opts[p.name];
    if (v !== undefined) query[p.name] = v as string | number;
  }
  apiGet(e.path, query)
    .then((body) => printJson(body))
    .catch((err) => {
      if (err instanceof ApiError) {
        console.error(
          c.red(`Request failed (HTTP ${err.status}):`) +
            ` ${JSON.stringify(err.detail)}` +
            (err.hint ? `\n${c.dim(err.hint)}` : ""),
        );
      } else {
        console.error(c.red("Error:") + ` ${String(err)}`);
      }
      process.exit(1);
    });
}

function flagFor(p: ToolParam): string {
  return p.type === "number" ? `--${p.name} <number>` : `--${p.name} <value>`;
}

function registerEndpoints(program: Command): void {
  for (const e of ENDPOINTS) {
    const cmd = program
      .command(commandName(e.tool))
      .summary(`${e.summary} (${e.credits}cr)`)
      .description(
        `${e.summary}\n\nPlatform: ${e.platform}  •  Path: ${e.path}  •  ~${e.credits} credit(s).\n` +
          `Cached results are free; failures are never charged.`,
      );
    for (const p of e.params) {
      const opt = new Option(flagFor(p), p.description);
      if (p.type === "number") opt.argParser((v) => Number.parseInt(v, 10));
      if (p.required) opt.makeOptionMandatory();
      cmd.addOption(opt);
    }
    cmd.action((opts: Record<string, unknown>) => runEndpoint(e, opts));
  }
}

function buildProgram(): Command {
  const program = new Command();
  program
    .name("captapi")
    .description(
      "Captapi CLI — social media data (YouTube, TikTok, Instagram, Facebook) from your terminal.",
    )
    .version(VERSION, "-v, --version", "Print the CLI version");

  program
    .command("login")
    .description("Save and verify your Captapi API key")
    .option("--key <key>", "API key (skips the interactive prompt)")
    .action((opts) => login(opts));

  program.command("logout").description("Remove the saved API key").action(logout);

  program
    .command("whoami")
    .description("Show the active API key (masked) and base URL")
    .action(whoami);

  program
    .command("balance")
    .description("Show your credit balance and recent requests")
    .option("--json", "Output raw JSON")
    .action((opts) => balance(opts));

  program
    .command("list")
    .argument("[platform]", "Filter by platform: youtube | tiktok | instagram | facebook")
    .description("List all available endpoints (commands)")
    .option("--json", "Output as JSON")
    .action((platform, opts) => list(platform, opts));

  const agent = program
    .command("agent")
    .description("Wire Captapi into an AI agent via MCP");
  agent
    .command("add")
    .argument("<agent>", "Target agent: claude | cursor")
    .description("Add the Captapi MCP server to an agent's config")
    .option("--key <key>", "API key to embed (defaults to the logged-in key)")
    .option("--print", "Print the config snippet instead of writing a file")
    .action((agentArg, opts) => agentAdd(agentArg, opts));

  registerEndpoints(program);

  program.addHelpText(
    "after",
    `\nExamples:\n` +
      `  $ captapi login\n` +
      `  $ captapi balance\n` +
      `  $ captapi list youtube\n` +
      `  $ captapi youtube-transcript --url "https://youtube.com/watch?v=ID"\n` +
      `  $ captapi agent add cursor\n`,
  );

  return program;
}

buildProgram().parseAsync(process.argv).catch((err) => {
  console.error(c.red("Fatal:"), err);
  process.exit(1);
});

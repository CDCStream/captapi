import { createInterface } from "node:readline/promises";
import { stdin, stdout } from "node:process";
import { loadConfig, saveConfig, clearApiKey, maskKey, configPath } from "../config.js";
import { verifyKey, c } from "../client.js";

async function promptKey(): Promise<string> {
  const rl = createInterface({ input: stdin, output: stdout });
  try {
    const answer = await rl.question("Paste your Captapi API key (capt_live_…): ");
    return answer.trim();
  } finally {
    rl.close();
  }
}

export async function login(opts: { key?: string }): Promise<void> {
  const { baseUrl } = loadConfig();
  const key = (opts.key || (await promptKey())).trim();
  if (!key) {
    console.error(c.red("No API key provided."));
    process.exit(1);
  }

  process.stdout.write("Verifying key… ");
  const result = await verifyKey(key, baseUrl);
  if (!result.ok) {
    console.error(
      c.red("failed.") +
        ` API returned HTTP ${result.status}. Double-check the key at ` +
        "https://captapi.com/dashboard/api-keys",
    );
    process.exit(1);
  }

  saveConfig({ apiKey: key, baseUrl });
  const plan =
    result.data && typeof result.data === "object" && "data" in result.data
      ? (result.data as { data?: { plan?: string } }).data?.plan
      : undefined;
  console.log(
    c.green("ok") +
      `\nLogged in${plan ? ` on the ${c.bold(plan)} plan` : ""}. Saved to ${c.dim(
        configPath(),
      )}`,
  );
}

export function logout(): void {
  clearApiKey();
  console.log(c.green("Logged out.") + " Removed the saved API key.");
}

export function whoami(): void {
  const { apiKey, baseUrl } = loadConfig();
  if (!apiKey) {
    console.log("Not logged in. Run " + c.cyan("captapi login") + ".");
    return;
  }
  const src = process.env.CAPTAPI_API_KEY ? " (from CAPTAPI_API_KEY)" : "";
  console.log(`Key:  ${c.bold(maskKey(apiKey))}${c.dim(src)}`);
  console.log(`Base: ${baseUrl}`);
}

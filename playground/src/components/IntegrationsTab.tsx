import { useState } from "react";
import type { Endpoint } from "../catalog.generated";
import { buildSnippet, CONNECTORS, type Connector } from "../lib/connectors";
import type { Settings } from "../lib/storage";

interface Props {
  endpoint: Endpoint;
  params: Record<string, string>;
  settings: Settings;
}

export function IntegrationsTab({ endpoint, params, settings }: Props) {
  const [connector, setConnector] = useState<Connector>("curl");
  const [copied, setCopied] = useState(false);

  const snippet = buildSnippet(connector, endpoint, params, settings.target, settings.apiKey);

  async function copy() {
    await navigator.clipboard.writeText(snippet);
    setCopied(true);
    setTimeout(() => setCopied(false), 1200);
  }

  return (
    <div className="card integrations">
      <div className="conn-tabs">
        {CONNECTORS.map((c) => (
          <button
            key={c.id}
            className={connector === c.id ? "active" : ""}
            onClick={() => setConnector(c.id)}
          >
            {c.label}
          </button>
        ))}
      </div>
      <div className="snippet-head">
        <span className="muted">
          Snippet for <code>{endpoint.tool}</code> → {settings.target}
        </span>
        <button className="copy" onClick={copy}>
          {copied ? "Copied ✓" : "Copy"}
        </button>
      </div>
      <pre className="json snippet">{snippet}</pre>
      <p className="muted small">
        Fill parameters on the left; snippets update live. The API key is embedded only if you
        typed one in the top bar (otherwise a placeholder is shown).
      </p>
    </div>
  );
}

import type { Endpoint } from "../catalog.generated";
import { guessSource } from "../lib/native";

interface Props {
  platforms: string[];
  platform: string;
  onPlatform: (p: string) => void;
  endpoints: Endpoint[];
  tool: string;
  onTool: (t: string) => void;
  endpoint?: Endpoint;
  params: Record<string, string>;
  onParams: (p: Record<string, string>) => void;
}

export function EndpointPicker({
  platforms,
  platform,
  onPlatform,
  endpoints,
  tool,
  onTool,
  endpoint,
  params,
  onParams,
}: Props) {
  const source = endpoint ? guessSource(endpoint) : "unknown";

  return (
    <div className="card picker">
      <div className="row">
        <label className="grow">
          Platform
          <select value={platform} onChange={(e) => onPlatform(e.target.value)}>
            {platforms.map((p) => (
              <option key={p} value={p}>
                {p}
              </option>
            ))}
          </select>
        </label>
        <label className="grow2">
          Endpoint
          <select value={tool} onChange={(e) => onTool(e.target.value)}>
            {endpoints.map((e) => (
              <option key={e.tool} value={e.tool}>
                {e.name} ({e.credits}cr)
              </option>
            ))}
          </select>
        </label>
      </div>

      {endpoint && (
        <>
          <div className="meta">
            <code>{endpoint.path}</code>
            <span className={`badge ${source}`}>{source}</span>
            <span className="badge credits">{endpoint.credits} cr</span>
          </div>
          <p className="summary">{endpoint.summary}</p>

          <div className="params">
            {endpoint.params.length === 0 && <p className="muted">No parameters.</p>}
            {endpoint.params.map((p) => (
              <label key={p.name} className="param">
                <span>
                  {p.name}
                  {p.required && <b className="req">*</b>}
                  <em className="ptype">{p.type}</em>
                </span>
                {p.type === "boolean" ? (
                  <select
                    value={params[p.name] ?? ""}
                    onChange={(e) => onParams({ ...params, [p.name]: e.target.value })}
                  >
                    <option value="">(unset)</option>
                    <option value="true">true</option>
                    <option value="false">false</option>
                  </select>
                ) : (
                  <input
                    type={p.type === "number" ? "number" : "text"}
                    placeholder={p.description}
                    value={params[p.name] ?? ""}
                    onChange={(e) => onParams({ ...params, [p.name]: e.target.value })}
                  />
                )}
                <small>{p.description}</small>
              </label>
            ))}
          </div>
        </>
      )}
    </div>
  );
}

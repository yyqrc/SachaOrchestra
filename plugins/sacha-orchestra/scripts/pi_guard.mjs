import {
  existsSync,
  lstatSync,
  realpathSync,
} from "node:fs";
import path from "node:path";

const PATH_TOOLS = new Set(["read", "edit", "write"]);
const WRITE_TOOLS = new Set(["edit", "write"]);
const RESERVED_WINDOWS_NAME =
  /^(?:con|prn|aux|nul|com[1-9¹²³]|lpt[1-9¹²³])(?:\..*)?$/iu;

function comparable(value) {
  return process.platform === "win32" ? value.toLowerCase() : value;
}

function isContained(root, candidate) {
  const relative = path.relative(root, candidate);
  return (
    relative === "" ||
    (!relative.startsWith(`..${path.sep}`) &&
      relative !== ".." &&
      !path.isAbsolute(relative))
  );
}

function normalizeRelative(root, rawPath) {
  if (typeof rawPath !== "string" || rawPath.trim() === "") {
    throw new Error("path 必须是非空字符串");
  }

  const withoutReferencePrefix = rawPath.startsWith("@")
    ? rawPath.slice(1)
    : rawPath;
  if (withoutReferencePrefix.includes("\0")) {
    throw new Error("path 包含 NUL");
  }

  const absolute = path.resolve(root, withoutReferencePrefix);
  if (!isContained(root, absolute) || comparable(absolute) === comparable(root)) {
    throw new Error(`path 不在 Root 的文件范围内：${rawPath}`);
  }

  const relative = path.relative(root, absolute).replaceAll("\\", "/");
  const segments = relative.split("/");
  for (const segment of segments) {
    if (
      segment === "" ||
      segment === "." ||
      segment === ".." ||
      segment.endsWith(" ") ||
      segment.endsWith(".") ||
      /[<>:"|?*]/u.test(segment) ||
      RESERVED_WINDOWS_NAME.test(segment)
    ) {
      throw new Error(`path 包含不安全片段：${rawPath}`);
    }
  }

  const first = segments[0].toLowerCase();
  if (first === ".git" || first === ".temp") {
    throw new Error(`path 指向控制目录：${rawPath}`);
  }

  return { absolute, relative };
}

function assertNoReparseAncestor(root, candidate) {
  let existing = candidate;
  while (!existsSync(existing)) {
    const parent = path.dirname(existing);
    if (parent === existing) break;
    existing = parent;
  }

  let current = existing;
  while (isContained(root, current)) {
    if (lstatSync(current).isSymbolicLink()) {
      throw new Error(`path 经过 symlink/junction：${current}`);
    }
    if (comparable(current) === comparable(root)) break;
    current = path.dirname(current);
  }

  const canonicalRoot = realpathSync.native(root);
  const canonicalExisting = realpathSync.native(existing);
  if (!isContained(canonicalRoot, canonicalExisting)) {
    throw new Error(`path 的真实位置越出 Root：${candidate}`);
  }
}

function normalizeScopes(root, values, label) {
  if (!Array.isArray(values) || values.length === 0) {
    throw new Error(`${label} 必须是非空 JSON 数组`);
  }
  return [
    ...new Set(
      values.map((value) => comparable(normalizeRelative(root, value).relative)),
    ),
  ];
}

export function createGuardConfig(environment = process.env) {
  const rootValue = environment.SACHA_PI_ROOT;
  if (typeof rootValue !== "string" || rootValue.trim() === "") {
    throw new Error("缺少 SACHA_PI_ROOT");
  }
  const root = realpathSync.native(path.resolve(rootValue));

  let readValues;
  let writeValues;
  try {
    readValues = JSON.parse(environment.SACHA_PI_READ_PATHS_JSON ?? "");
    writeValues = JSON.parse(environment.SACHA_PI_WRITE_PATHS_JSON ?? "");
  } catch (error) {
    throw new Error(`Pi guard Scope JSON 无效：${error.message}`);
  }

  return {
    root,
    readPaths: normalizeScopes(root, readValues, "ReadPath"),
    writePaths: normalizeScopes(root, writeValues, "WritePath"),
  };
}

export function assertAllowedToolPath(config, toolName, rawPath) {
  if (!PATH_TOOLS.has(toolName)) {
    throw new Error(`未授权工具：${toolName}`);
  }

  const { absolute, relative } = normalizeRelative(config.root, rawPath);
  assertNoReparseAncestor(config.root, absolute);
  if (
    WRITE_TOOLS.has(toolName) &&
    existsSync(absolute) &&
    lstatSync(absolute).nlink > 1
  ) {
    throw new Error(`写目标是 hard link：${relative}`);
  }
  const candidate = comparable(relative);
  const scopes = WRITE_TOOLS.has(toolName)
    ? config.writePaths
    : config.readPaths;
  const allowed = scopes.some(
    (scope) => candidate === scope || candidate.startsWith(`${scope}/`),
  );
  if (!allowed) {
    throw new Error(`${toolName} 越出允许路径：${relative}`);
  }
  return relative;
}

const resultParameters = {
  type: "object",
  additionalProperties: false,
  properties: {
    outcome: {
      type: "string",
      enum: ["completed", "blocked", "failed"],
      description: "Final implementation outcome.",
    },
    summary: {
      type: "string",
      description: "Concise result and verification summary.",
    },
    blockers: {
      type: "array",
      items: { type: "string" },
      description: "Concrete blockers; empty when completed.",
    },
  },
  required: ["outcome", "summary", "blockers"],
};

export default function registerSachaPiGuard(pi) {
  const config = createGuardConfig();

  pi.on("tool_call", (event) => {
    if (!PATH_TOOLS.has(event.toolName)) return undefined;
    try {
      assertAllowedToolPath(config, event.toolName, event.input?.path);
      return undefined;
    } catch (error) {
      return {
        block: true,
        reason: `Sacha Pi guard blocked ${event.toolName}: ${error.message}`,
      };
    }
  });

  pi.registerTool({
    name: "sacha_result",
    label: "Sacha Result",
    description:
      "Return the final structured implementation result. Call this exactly once as the last action.",
    promptSnippet: "Finish the task with a structured terminating result",
    promptGuidelines: [
      "Call sacha_result exactly once as the final action after implementation and available verification.",
      "Use outcome completed only when the requested work and available verification are complete; otherwise use blocked or failed with concrete blockers.",
    ],
    parameters: resultParameters,
    async execute(_toolCallId, params) {
      return {
        content: [
          {
            type: "text",
            text: `Sacha one-shot result: ${params.outcome}`,
          },
        ],
        details: {
          outcome: params.outcome,
          summary: params.summary,
          blockers: params.blockers,
        },
        terminate: true,
      };
    },
  });
}

import {
  mkdirSync,
  linkSync,
  mkdtempSync,
  rmSync,
  symlinkSync,
  writeFileSync,
} from "node:fs";
import path from "node:path";
import { fileURLToPath } from "node:url";
import {
  assertAllowedToolPath,
  createGuardConfig,
} from "../plugins/sacha-orchestra/scripts/pi_guard.mjs";

function assert(condition, message) {
  if (!condition) throw new Error(message);
}

function expectBlocked(action, marker) {
  let error;
  try {
    action();
  } catch (caught) {
    error = caught;
  }
  assert(error instanceof Error, `expected guard failure: ${marker}`);
  assert(
    error.message.includes(marker),
    `guard failure did not include "${marker}": ${error.message}`,
  );
}

const testParent = path.resolve(
  path.dirname(fileURLToPath(import.meta.url)),
  "../.temp/tests",
);
mkdirSync(testParent, { recursive: true });
const root = mkdtempSync(path.join(testParent, "sacha-pi-guard-"));
try {
  mkdirSync(path.join(root, "src"));
  mkdirSync(path.join(root, "docs"));
  writeFileSync(path.join(root, "src", "input.txt"), "input\n", "utf8");

  const config = createGuardConfig({
    SACHA_PI_ROOT: root,
    SACHA_PI_READ_PATHS_JSON: JSON.stringify(["src", "docs/readme.md"]),
    SACHA_PI_WRITE_PATHS_JSON: JSON.stringify(["src/out.txt"]),
  });

  assert(
    assertAllowedToolPath(config, "read", "src/input.txt") ===
      "src/input.txt",
    "read path was not normalized",
  );
  assert(
    assertAllowedToolPath(config, "write", "@src/out.txt") === "src/out.txt",
    "@ path prefix was not normalized",
  );
  expectBlocked(
    () => assertAllowedToolPath(config, "write", "src/other.txt"),
    "越出允许路径",
  );
  expectBlocked(
    () => assertAllowedToolPath(config, "read", "../outside.txt"),
    "不在 Root",
  );
  expectBlocked(
    () => assertAllowedToolPath(config, "read", ".git/config"),
    "控制目录",
  );
  expectBlocked(
    () => assertAllowedToolPath(config, "read", ".temp/packet.md"),
    "控制目录",
  );
  expectBlocked(
    () => assertAllowedToolPath(config, "read", "src/file:stream"),
    "不安全片段",
  );
  expectBlocked(
    () => assertAllowedToolPath(config, "read", "src/NUL"),
    "不安全片段",
  );

  const outside = mkdtempSync(path.join(testParent, "sacha-pi-outside-"));
  const junction = path.join(root, "src", "link");
  try {
    const outsideFile = path.join(outside, "shared.txt");
    writeFileSync(outsideFile, "shared\n", "utf8");
    const hardLink = path.join(root, "src", "out.txt");
    linkSync(outsideFile, hardLink);
    expectBlocked(
      () => assertAllowedToolPath(config, "write", "src/out.txt"),
      "hard link",
    );
    rmSync(hardLink, { force: true });

    symlinkSync(outside, junction, "junction");
    expectBlocked(
      () => assertAllowedToolPath(config, "read", "src/link/secret.txt"),
      "symlink/junction",
    );
  } finally {
    rmSync(junction, { force: true });
    rmSync(outside, { recursive: true, force: true });
  }

  console.log("pi_guard_tests=passed");
} finally {
  rmSync(root, { recursive: true, force: true });
}

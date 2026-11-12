// Optional maintenance command; the shipped HTML has no build/runtime dependency.
// Preserve DATA, the database/reference prefix, identifiers, and the RULE comment.
const fs = require("node:fs");
const path = require("node:path");
const { minify } = require("terser");
const CleanCSS = require("clean-css");

async function compact() {
  const file = path.resolve(__dirname, "..", "index.html");
  const source = fs.readFileSync(file, "utf8");
  const start = source.indexOf("/* RULE: every question string rendered");
  const end = source.lastIndexOf("\n})();\n</script>");
  if (start < 0 || end <= start) throw new Error("Expected workbench boundaries were not found; source unchanged.");
  const result = await minify(source.slice(start, end), {
    compress: false, mangle: false,
    parse: { bare_returns: true },
    format: { comments: /RULE:/, max_line_len: 160 },
  });
  if (!result.code || !result.code.includes("/* RULE: every question string rendered")) {
    throw new Error("Required source invariant missing; source unchanged.");
  }
  let output = source.slice(0, start) + result.code + source.slice(end);
  const style = output.match(/<style>([\s\S]*?)<\/style>/);
  if (!style) throw new Error("Expected stylesheet was not found; source unchanged.");
  const css = new CleanCSS({ level: 2, rebase: false, inline: ["none"] }).minify(style[1]);
  if (css.errors.length || css.warnings.length) throw new Error("Stylesheet compaction requires review; source unchanged.");
  output = output.replace(style[0], "<style>" + css.styles + "</style>");
  if (Buffer.byteLength(output) >= 360000) throw new Error("Compacted artifact still exceeds the 360,000-byte cap; source unchanged.");
  fs.writeFileSync(file, output);
  console.log(`Compacted artifact: ${Buffer.byteLength(source)} -> ${Buffer.byteLength(output)} bytes. DATA/reference content unchanged; JavaScript compression and name mangling disabled.`);
}

compact().catch((error) => { console.error(error.message); process.exitCode = 1; });

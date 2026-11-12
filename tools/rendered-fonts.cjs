// Chromium-only glyph evidence. FontFaceSet.check can succeed for an absent face.
const PRIMARY_FONTS = ["Fraunces", "Atkinson Hyperlegible", "Space Mono"];
const normalize = (name) => name.toLowerCase().replace(/[^a-z]/g, "");

function findSamples(families) {
  const visible = [...document.querySelectorAll("body *")].filter((element) => {
    const style = getComputedStyle(element);
    return style.visibility !== "hidden" && style.display !== "none" && element.getClientRects().length &&
      [...element.childNodes].some((node) => node.nodeType === Node.TEXT_NODE && node.textContent.trim());
  });
  const selector = (element) => {
    const parts = [];
    while (element && element !== document.documentElement) {
      const parent = element.parentElement;
      parts.unshift(element.localName + ":nth-child(" + ([...parent.children].indexOf(element) + 1) + ")");
      element = parent;
    }
    return "html>" + parts.join(">");
  };
  return families.map((expected) => {
    const element = visible.find((candidate) => getComputedStyle(candidate).fontFamily.split(",")
      .some((family) => family.trim().replace(/^["']|["']$/g, "").toLowerCase() === expected.toLowerCase()));
    return { expected, selector: element ? selector(element) : null };
  });
}

async function fontSamples(page) {
  return page.evaluate(findSamples, PRIMARY_FONTS);
}

async function forceFallbackFonts(page) {
  // Save the original roles before removing primaries, including locally installed fonts.
  const samples = await fontSamples(page);
  await page.evaluate((families) => {
    const primary = new Set(families.map((family) => family.toLowerCase()));
    const style = document.createElement("style");
    style.textContent = ':root{--display:Georgia,"Times New Roman",serif!important;--body:Verdana,system-ui,sans-serif!important;--mono:"Courier New",ui-monospace,monospace!important}svg text{font-family:Georgia,"Times New Roman",serif!important}';
    document.head.appendChild(style);
    for (const element of document.querySelectorAll("body *")) {
      const stack = getComputedStyle(element).fontFamily.split(",");
      const fallback = stack.filter((family) => !primary.has(family.trim().replace(/^["']|["']$/g, "").toLowerCase()));
      if (fallback.length !== stack.length) element.style.setProperty("font-family", fallback.join(",") || "serif", "important");
    }
  }, PRIMARY_FONTS);
  await page.evaluate(() => document.fonts.ready);
  return samples;
}

async function inspectRenderedFonts(page, samples, { fallback = false } = {}) {
  await page.evaluate(() => document.fonts.ready);
  const session = await page.context().newCDPSession(page);
  const failures = [], evidence = [];
  try {
    await session.send("DOM.enable");
    await session.send("CSS.enable");
    const document = await session.send("DOM.getDocument");
    for (const { selector, expected } of samples) {
      const node = selector && await session.send("DOM.querySelector", { nodeId: document.root.nodeId, selector });
      if (!node || !node.nodeId) { failures.push("font proof element missing: " + expected); continue; }
      const result = await session.send("CSS.getPlatformFontsForNode", { nodeId: node.nodeId });
      const used = result.fonts.filter((font) => font.glyphCount > 0);
      evidence.push({ selector, expected, used: used.map(({ familyName, glyphCount, isCustomFont }) => ({ familyName, glyphCount, isCustomFont })) });
      if (!used.length) failures.push("no rendered glyph evidence: " + expected);
      else if (fallback && used.some((font) => PRIMARY_FONTS.some((family) => normalize(font.familyName).startsWith(normalize(family))))) {
        failures.push("primary font still rendered in fallback context: " + expected);
      } else if (!fallback && !used.some((font) => normalize(font.familyName).startsWith(normalize(expected)))) {
        failures.push("required font not rendered: " + expected);
      }
    }
  } finally { await session.detach(); }
  return { failures, evidence };
}

module.exports = { PRIMARY_FONTS, fontSamples, forceFallbackFonts, inspectRenderedFonts };

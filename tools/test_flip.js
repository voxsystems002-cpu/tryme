/* Functional test for the flip, in a real DOM but no browser.
   Proves the behaviour that the markup alone cannot:
     - one face at a time, and it is the one that is not aria-hidden
     - Enter / Space / Escape / click all agree with aria-expanded
     - the back face's JSON really is printed from the head JSON
     - a link inside the card is not swallowed by the flip handler
   Needs jsdom:  npm install jsdom && node tools/test_flip.js
*/
const fs = require("fs");
const path = require("path");
const { JSDOM } = require("jsdom");

const html = fs.readFileSync(path.join(__dirname, "..", "index.html"), "utf8");
const dom = new JSDOM(html, { runScripts: "dangerously", pretendToBeVisual: true });
const { window } = dom;
const doc = window.document;

let fails = 0;
function check(name, ok, detail = "") {
  console.log(`[${ok ? "PASS" : "FAIL"}] ${name}${detail ? " — " + detail : ""}`);
  if (!ok) fails++;
}

const card = doc.getElementById("postcard");
const front = doc.getElementById("front-face");
const back = doc.getElementById("back-face");

const state = () => ({
  expanded: card.getAttribute("aria-expanded"),
  frontHidden: front.hidden,
  backHidden: back.hidden,
  frontAria: front.getAttribute("aria-hidden"),
  backAria: back.getAttribute("aria-hidden"),
});

const consistent = (s) => {
  const showingBack = s.expanded === "true";
  return (
    s.frontHidden === showingBack &&
    s.backHidden === !showingBack &&
    s.frontAria === String(showingBack) &&
    s.backAria === String(!showingBack)
  );
};

// --- initial state: front visible, back hidden from sight and from AT
check("starts on the front", state().expanded === "false" && consistent(state()), JSON.stringify(state()));

// --- back face JSON is generated, not hand-written
const head = JSON.parse(doc.getElementById("postcard-data").textContent);
const printed = JSON.parse(doc.getElementById("back-json").textContent);
check("back JSON is printed from the head JSON", JSON.stringify(head) === JSON.stringify(printed));
check("packet has receipts", Array.isArray(head.receipts?.items) && head.receipts.items.length >= 5);

// --- key handling
function key(k) {
  card.dispatchEvent(new window.KeyboardEvent("keydown", { key: k, bubbles: true, cancelable: true }));
}

key("Enter");
check("Enter flips to the back", state().expanded === "true" && consistent(state()), JSON.stringify(state()));
key(" ");
check("Space flips back to the front", state().expanded === "false" && consistent(state()));
key("Enter");
key("Escape");
check("Escape returns to the front", state().expanded === "false" && consistent(state()));

// --- click, and the two things a click must not break
const clickEvent = (target) =>
  new window.MouseEvent("click", { bubbles: true, cancelable: true, view: window });

card.dispatchEvent(clickEvent(front));
check("click flips", state().expanded === "true" && consistent(state()));

const link = doc.querySelector('.contact-bar a[href^="mailto:"]');
link.dispatchEvent(clickEvent(link));
check("clicking a link does not flip the card", state().expanded === "true");

card.dispatchEvent(clickEvent(front));
check("click flips back", state().expanded === "false" && consistent(state()));

// --- a selection should not count as a flip
const sel = window.getSelection();
const range = doc.createRange();
range.selectNodeContents(front);
sel.removeAllRanges();
sel.addRange(range);
card.dispatchEvent(clickEvent(front));
check("a text selection does not flip the card", state().expanded === "false");

console.log(`\n${fails} failing`);
process.exit(fails ? 1 : 0);

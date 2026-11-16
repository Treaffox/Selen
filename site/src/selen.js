/* Selen: Schrifttester (ohne Abhängigkeiten, CSP-fest: nur CSSOM, keine Inline-Stile im Markup) */
(function () {
  "use strict";
  var $ = function (id) { return document.getElementById(id); };
  var out = $("t-out"), text = $("t-text"), size = $("t-size"), wght = $("t-wght");
  if (!out || !text) return;
  function apply() {
    out.textContent = text.value || "\u00A0";
    out.style.setProperty("font-size", size.value + "px");
    out.style.setProperty("font-weight", wght.value);
    out.style.setProperty("font-style", $("t-italic").checked ? "italic" : "normal");
    out.style.setProperty("font-variant-numeric", $("t-pnum").checked ? "proportional-nums" : "normal");
    $("t-size-o").textContent = size.value;
    $("t-wght-o").textContent = wght.value;
  }
  ["input", "change"].forEach(function (ev) {
    [text, size, wght, $("t-italic"), $("t-pnum")].forEach(function (el) { el.addEventListener(ev, apply); });
  });
  apply();
})();

/*!
 * TRFX Legacy – optionale Skripte
 * Alles hier ist Zusatz. Ohne dieses Skript bleibt jede Seite les- und bedienbar
 * (Reiter zeigen dann alle Panels, Dialoge öffnen nicht).
 */
(function () {
  "use strict";

  function $all(sel, root) {
    return Array.prototype.slice.call((root || document).querySelectorAll(sel));
  }

  /* ---------- Jahr in der Fußzeile ---------- */
  $all("[data-lg-year]").forEach(function (el) {
    el.textContent = String(new Date().getFullYear());
  });

  /* ---------- Reiter ---------- */
  $all("[data-lg-tabs]").forEach(function (root) {
    var tabs = $all('[role="tab"]', root);
    var panels = $all('[role="tabpanel"]', root);

    function select(tab, focus) {
      tabs.forEach(function (t) {
        var on = t === tab;
        t.setAttribute("aria-selected", on ? "true" : "false");
        t.tabIndex = on ? 0 : -1;
      });
      panels.forEach(function (p) {
        p.hidden = p.id !== tab.getAttribute("aria-controls");
      });
      if (focus) {
        tab.focus();
      }
    }

    tabs.forEach(function (tab, i) {
      tab.addEventListener("click", function () {
        select(tab, false);
      });
      tab.addEventListener("keydown", function (ev) {
        var next = null;
        if (ev.key === "ArrowRight") {
          next = tabs[(i + 1) % tabs.length];
        } else if (ev.key === "ArrowLeft") {
          next = tabs[(i - 1 + tabs.length) % tabs.length];
        } else if (ev.key === "Home") {
          next = tabs[0];
        } else if (ev.key === "End") {
          next = tabs[tabs.length - 1];
        }
        if (next) {
          ev.preventDefault();
          select(next, true);
        }
      });
    });

    var first = tabs.filter(function (t) {
      return t.getAttribute("aria-selected") === "true";
    })[0] || tabs[0];
    if (first) {
      select(first, false);
    }
  });

  /* ---------- Dialoge ---------- */
  $all("[data-lg-open]").forEach(function (btn) {
    btn.addEventListener("click", function () {
      var dlg = document.getElementById(btn.getAttribute("data-lg-open"));
      if (dlg && typeof dlg.showModal === "function") {
        dlg.showModal();
      }
    });
  });

  $all("dialog.lg-dialog").forEach(function (dlg) {
    $all("[data-lg-close]", dlg).forEach(function (btn) {
      btn.addEventListener("click", function () {
        dlg.close(btn.getAttribute("data-lg-close"));
      });
    });
    dlg.addEventListener("close", function () {
      var out = document.getElementById(dlg.id + "-result");
      if (out) {
        out.textContent = "Letzte Antwort: „" + (dlg.returnValue || "Abbrechen") + "“";
      }
    });
  });

  /* ---------- Aufklappmenüs ---------- */
  var dropdowns = $all("details[data-lg-dropdown]");
  document.addEventListener("click", function (ev) {
    dropdowns.forEach(function (d) {
      if (!d.contains(ev.target)) {
        d.open = false;
      }
    });
  });
  document.addEventListener("keydown", function (ev) {
    if (ev.key === "Escape") {
      dropdowns.forEach(function (d) {
        if (d.open) {
          d.open = false;
          var s = d.querySelector("summary");
          if (s) {
            s.focus();
          }
        }
      });
    }
  });
  dropdowns.forEach(function (d) {
    d.addEventListener("toggle", function () {
      if (d.open) {
        dropdowns.forEach(function (o) {
          if (o !== d) {
            o.open = false;
          }
        });
      }
    });
  });

  /* ---------- Auswahl in Tabellen ---------- */
  $all("table[data-lg-selectable]").forEach(function (table) {
    var rows = $all("tbody tr", table);
    function pick(row) {
      rows.forEach(function (r) {
        var on = r === row;
        r.classList.toggle("is-selected", on);
        r.setAttribute("aria-selected", on ? "true" : "false");
      });
    }
    rows.forEach(function (row) {
      row.tabIndex = 0;
      row.addEventListener("click", function () {
        pick(row);
      });
      row.addEventListener("keydown", function (ev) {
        if (ev.key === "Enter" || ev.key === " ") {
          ev.preventDefault();
          pick(row);
        }
      });
    });
  });

  /* ---------- Fortschritts-Demo ---------- */
  $all("[data-lg-progress-demo]").forEach(function (root) {
    var bar = root.querySelector("progress");
    var label = root.querySelector("[data-lg-progress-label]");
    var btn = root.querySelector("button");
    var timer = null;

    function stop() {
      window.clearInterval(timer);
      timer = null;
    }

    btn.addEventListener("click", function () {
      if (timer) {
        stop();
        btn.textContent = "Fortsetzen";
        return;
      }
      if (bar.value >= bar.max) {
        bar.value = 0;
      }
      btn.textContent = "Anhalten";
      timer = window.setInterval(function () {
        bar.value = Math.min(bar.max, bar.value + 4);
        label.textContent = bar.value + " % kopiert";
        if (bar.value >= bar.max) {
          stop();
          label.textContent = "Fertig. Das hat gedauert, aber es hat funktioniert.";
          btn.textContent = "Nochmal";
        }
      }, 180);
    });
  });

  /* ---------- Assistent ---------- */
  $all("[data-lg-wizard]").forEach(function (root) {
    var steps = $all("[data-step]", root);
    var marks = $all("[data-mark]", root);
    var back = root.querySelector("[data-lg-back]");
    var next = root.querySelector("[data-lg-next]");
    var cancel = root.querySelector("[data-lg-cancel]");
    var idx = 0;

    function render() {
      steps.forEach(function (s, i) {
        s.hidden = i !== idx;
      });
      marks.forEach(function (m, i) {
        if (i === idx) {
          m.setAttribute("aria-current", "step");
        } else {
          m.removeAttribute("aria-current");
        }
      });
      back.disabled = idx === 0;
      next.textContent = idx === steps.length - 1 ? "Fertig stellen" : "Weiter >";
    }

    back.addEventListener("click", function () {
      idx = Math.max(0, idx - 1);
      render();
    });
    next.addEventListener("click", function () {
      if (idx === steps.length - 1) {
        idx = 0;
      } else {
        idx += 1;
      }
      render();
    });
    cancel.addEventListener("click", function () {
      idx = 0;
      render();
    });
    render();
  });

  /* ---------- Aufgabenbereich: auf schmalen Bildschirmen eingeklappt ---------- */
  if (window.matchMedia) {
    var narrow = window.matchMedia("(max-width: 860px)");
    var panes = $all(".lg-pane__group");
    var applyPane = function () {
      panes.forEach(function (d) {
        d.open = !narrow.matches;
      });
    };
    applyPane();
    if (narrow.addEventListener) {
      narrow.addEventListener("change", applyPane);
    }
  }

  /* ---------- Navigationsstreifen: Überlauf anzeigen, aktive Seite sichtbar ---------- */
  $all(".lg-nav").forEach(function (nav) {
    var list = nav.querySelector("ul");
    if (!list) {
      return;
    }
    var update = function () {
      var max = list.scrollWidth - list.clientWidth;
      nav.classList.toggle("has-more-left", list.scrollLeft > 4);
      nav.classList.toggle("has-more-right", max > 4 && list.scrollLeft < max - 4);
    };
    var current = list.querySelector('[aria-current="page"]');
    if (current && list.scrollWidth > list.clientWidth) {
      list.scrollLeft = Math.max(0, current.offsetLeft - (list.clientWidth - current.offsetWidth) / 2);
    }
    list.addEventListener("scroll", update, { passive: true });
    window.addEventListener("resize", update);
    update();
  });

  /* ---------- Kurzinfo per Tippen (Touch kennt kein Hover) ---------- */
  var tips = $all("[data-tip]");
  tips.forEach(function (el) {
    el.addEventListener("click", function () {
      var open = el.classList.contains("is-tip");
      tips.forEach(function (o) {
        o.classList.remove("is-tip");
      });
      if (!open) {
        el.classList.add("is-tip");
      }
    });
  });
  document.addEventListener("click", function (ev) {
    tips.forEach(function (o) {
      if (!o.contains(ev.target)) {
        o.classList.remove("is-tip");
      }
    });
  });

  /* ---------- Quelltext kopieren ---------- */
  $all("[data-lg-copy]").forEach(function (btn) {
    btn.addEventListener("click", function (ev) {
      ev.preventDefault();
      var pre = btn.closest("details").querySelector("pre");
      var text = pre ? pre.textContent : "";
      var done = function () {
        var old = btn.textContent;
        btn.textContent = "Kopiert";
        window.setTimeout(function () {
          btn.textContent = old;
        }, 1500);
      };
      if (navigator.clipboard && window.isSecureContext) {
        navigator.clipboard.writeText(text).then(done, done);
      } else {
        var ta = document.createElement("textarea");
        ta.value = text;
        ta.setAttribute("readonly", "");
        ta.style.position = "fixed";
        ta.style.opacity = "0";
        document.body.appendChild(ta);
        ta.select();
        try {
          document.execCommand("copy");
        } catch (e) {
          /* ignorieren */
        }
        document.body.removeChild(ta);
        done();
      }
    });
  });
})();

/* Kavinan Design Studio — site interactions. No dependencies. */
(function () {
  "use strict";
  var doc = document.documentElement;
  doc.classList.remove("no-js");
  var $ = function (s, c) { return (c || document).querySelector(s); };
  var $$ = function (s, c) { return Array.prototype.slice.call((c || document).querySelectorAll(s)); };
  var reduce = window.matchMedia("(prefers-reduced-motion: reduce)").matches;
  function store(k, v) { try { if (v === undefined) return localStorage.getItem(k); localStorage.setItem(k, v); } catch (e) { return null; } }

  /* ---- Theme (light / dark) ---- */
  function currentTheme() {
    return doc.getAttribute("data-theme") || (window.matchMedia("(prefers-color-scheme: dark)").matches ? "dark" : "light");
  }
  $$(".theme-toggle").forEach(function (btn) {
    btn.addEventListener("click", function () {
      var next = currentTheme() === "dark" ? "light" : "dark";
      doc.setAttribute("data-theme", next);
      store("kds-theme", next);
      var meta = $('meta[name="theme-color"]');
      if (meta) meta.setAttribute("content", next === "dark" ? "#0c221b" : "#f7f5f0");
      btn.setAttribute("aria-label", next === "dark" ? "Switch to light mode" : "Switch to dark mode");
    });
  });

  /* ---- Header: scrolled / hide on scroll down ---- */
  var header = $(".site-header");
  var toTop = $(".to-top");
  var lastY = 0;
  function onScroll() {
    var y = window.scrollY;
    if (header) {
      header.classList.toggle("is-scrolled", y > 40);
      header.classList.toggle("is-hidden", y > 400 && y > lastY && !document.body.classList.contains("menu-open"));
    }
    if (toTop) toTop.classList.toggle("show", y > 900);
    lastY = y;
  }
  window.addEventListener("scroll", onScroll, { passive: true });
  onScroll();
  if (toTop) toTop.addEventListener("click", function () { window.scrollTo({ top: 0, behavior: reduce ? "auto" : "smooth" }); });

  /* ---- Mobile menu ---- */
  var menu = $(".mobile-menu");
  function setMenu(open) {
    if (!menu) return;
    menu.classList.toggle("is-open", open);
    document.body.classList.toggle("menu-open", open);
    menu.setAttribute("aria-hidden", open ? "false" : "true");
    $$(".menu-btn").forEach(function (b) { b.setAttribute("aria-expanded", open ? "true" : "false"); });
    if (open) { var f = $("nav a", menu); if (f) f.focus(); }
  }
  $$(".menu-btn").forEach(function (b) { b.addEventListener("click", function () { setMenu(true); }); });
  $$(".mobile-menu .close, .mobile-menu nav a").forEach(function (b) { b.addEventListener("click", function () { setMenu(false); }); });
  document.addEventListener("keydown", function (e) { if (e.key === "Escape") setMenu(false); });

  /* ---- Reveal on scroll ---- */
  if ("IntersectionObserver" in window && !reduce) {
    var io = new IntersectionObserver(function (entries) {
      entries.forEach(function (en) {
        if (en.isIntersecting) { en.target.classList.add("is-in"); io.unobserve(en.target); }
      });
    }, { rootMargin: "0px 0px -8% 0px", threshold: 0.08 });
    $$(".reveal, .reveal-img").forEach(function (el) { io.observe(el); });
  } else {
    $$(".reveal, .reveal-img").forEach(function (el) { el.classList.add("is-in"); });
  }

  /* ---- Hero slideshow ---- */
  var hero = $(".hero");
  if (hero) {
    var slides = $$(".hero-slide", hero), dots = $$(".hero-progress button", hero);
    var title = $(".hero-meta strong", hero), sub = $(".hero-meta span", hero);
    var idx = 0, timer;
    function show(i) {
      slides[idx].classList.remove("is-active"); dots[idx] && dots[idx].classList.remove("is-active");
      idx = (i + slides.length) % slides.length;
      slides[idx].classList.add("is-active");
      if (dots[idx]) { var d = dots[idx]; d.classList.remove("is-active"); void d.offsetWidth; d.classList.add("is-active"); }
      if (title) title.textContent = slides[idx].dataset.title || "";
      if (sub) sub.textContent = slides[idx].dataset.loc || "";
      // lazy-load next slide
      var next = slides[(idx + 1) % slides.length], img = next && $("img[data-src]", next);
      if (img) { img.src = img.dataset.src; img.srcset = img.dataset.srcset || ""; img.removeAttribute("data-src"); }
      clearTimeout(timer);
      if (!reduce) timer = setTimeout(function () { show(idx + 1); }, 7000);
    }
    dots.forEach(function (d, i) { d.addEventListener("click", function () { show(i); }); });
    if (slides.length) show(0);
  }

  /* ---- Count-up stats ---- */
  var counters = $$("[data-count]");
  if (counters.length && "IntersectionObserver" in window) {
    var cio = new IntersectionObserver(function (entries) {
      entries.forEach(function (en) {
        if (!en.isIntersecting) return;
        var el = en.target, end = +el.dataset.count, t0 = null;
        cio.unobserve(el);
        if (reduce) { el.textContent = end; return; }
        (function step(ts) {
          t0 = t0 || ts;
          var p = Math.min((ts - t0) / 1600, 1), e = 1 - Math.pow(1 - p, 3);
          el.textContent = Math.round(end * e);
          if (p < 1) requestAnimationFrame(step);
        })(performance.now());
      });
    }, { threshold: 0.5 });
    counters.forEach(function (c) { cio.observe(c); });
  }

  /* ---- Quote rotator ---- */
  $$(".quote-rotator").forEach(function (rot) {
    var qs = $$("figure", rot), q = 0;
    if (qs.length < 2 || reduce) return;
    setInterval(function () {
      qs[q].classList.remove("is-active"); q = (q + 1) % qs.length; qs[q].classList.add("is-active");
    }, 6500);
  });

  /* ---- Project filters ---- */
  var pf = $("[data-filter-group='projects']");
  if (pf) {
    var cards = $$(".projects-grid .pcard");
    function applyFilter(f) {
      $$(".chip", pf).forEach(function (c) { c.setAttribute("aria-pressed", c.dataset.filter === f ? "true" : "false"); });
      cards.forEach(function (card) {
        var on = f === "all" || card.dataset.sector === f;
        card.classList.toggle("is-hidden", !on);
      });
    }
    $$(".chip", pf).forEach(function (c) {
      c.addEventListener("click", function () {
        applyFilter(c.dataset.filter);
        history.replaceState(null, "", c.dataset.filter === "all" ? location.pathname : "#" + c.dataset.filter);
      });
    });
    var h = location.hash.replace("#", "");
    if (h && $(".chip[data-filter='" + h + "']", pf)) applyFilter(h);
  }

  /* ---- Journal filter + search ---- */
  var jf = $("[data-filter-group='journal']");
  if (jf) {
    var jcards = $$(".jgrid .jcard"), jq = $("#journal-search"), jtag = "all";
    function jApply() {
      var term = (jq && jq.value || "").toLowerCase().trim();
      jcards.forEach(function (c) {
        var okTag = jtag === "all" || (c.dataset.tags || "").split("|").indexOf(jtag) > -1;
        var okQ = !term || c.textContent.toLowerCase().indexOf(term) > -1;
        c.classList.toggle("is-hidden", !(okTag && okQ));
      });
    }
    $$(".chip", jf).forEach(function (c) {
      c.addEventListener("click", function () {
        jtag = c.dataset.filter;
        $$(".chip", jf).forEach(function (x) { x.setAttribute("aria-pressed", x === c ? "true" : "false"); });
        jApply();
      });
    });
    if (jq) jq.addEventListener("input", jApply);
  }

  /* ---- FAQ search ---- */
  var fq = $("#faq-search");
  if (fq) {
    fq.addEventListener("input", function () {
      var term = fq.value.toLowerCase().trim();
      $$(".faq-cat").forEach(function (cat) {
        var any = false;
        $$("details", cat).forEach(function (d) {
          var hit = !term || d.textContent.toLowerCase().indexOf(term) > -1;
          d.classList.toggle("is-hidden", !hit);
          if (hit) any = true;
          if (term && hit) d.open = true;
        });
        cat.classList.toggle("is-hidden", !any);
      });
      var empty = $("#faq-empty");
      if (empty) empty.hidden = !!$(".faq-cat:not(.is-hidden)");
    });
  }

  /* ---- Lightbox ---- */
  var groups = {};
  $$("[data-lightbox]").forEach(function (el) {
    var g = el.dataset.lightbox; (groups[g] = groups[g] || []).push(el);
  });
  if (Object.keys(groups).length) {
    var lb = document.createElement("div");
    lb.className = "lightbox"; lb.setAttribute("role", "dialog"); lb.setAttribute("aria-modal", "true"); lb.setAttribute("aria-label", "Image viewer");
    lb.innerHTML = '<span class="lb-count"></span><img alt=""><p class="lb-cap"></p>' +
      '<button class="lb-close" aria-label="Close"><svg viewBox="0 0 24 24" width="20" height="20" fill="none" stroke="currentColor" stroke-width="1.5"><path d="M5 5l14 14M19 5L5 19"/></svg></button>' +
      '<button class="lb-prev" aria-label="Previous image"><svg viewBox="0 0 24 24" width="20" height="20" fill="none" stroke="currentColor" stroke-width="1.5"><path d="M15 5l-7 7 7 7"/></svg></button>' +
      '<button class="lb-next" aria-label="Next image"><svg viewBox="0 0 24 24" width="20" height="20" fill="none" stroke="currentColor" stroke-width="1.5"><path d="M9 5l7 7-7 7"/></svg></button>';
    document.body.appendChild(lb);
    var lbImg = $("img", lb), lbCap = $(".lb-cap", lb), lbCount = $(".lb-count", lb), cur = [], ci = 0, lastFocus;
    function open(g, i) { cur = groups[g]; lastFocus = document.activeElement; lb.classList.add("is-open"); document.body.style.overflow = "hidden"; go(i); $(".lb-close", lb).focus(); }
    function close() { lb.classList.remove("is-open"); document.body.style.overflow = ""; lbImg.removeAttribute("src"); if (lastFocus) lastFocus.focus(); }
    function go(i) {
      ci = (i + cur.length) % cur.length;
      var el = cur[ci];
      lbImg.src = el.dataset.full; lbImg.alt = el.dataset.caption || "";
      lbCap.textContent = el.dataset.caption || ""; lbCount.textContent = (ci + 1) + " / " + cur.length;
    }
    Object.keys(groups).forEach(function (g) {
      groups[g].forEach(function (el, i) {
        el.setAttribute("tabindex", "0"); el.setAttribute("role", "button");
        el.addEventListener("click", function () { open(g, i); });
        el.addEventListener("keydown", function (e) { if (e.key === "Enter" || e.key === " ") { e.preventDefault(); open(g, i); } });
      });
    });
    $(".lb-close", lb).addEventListener("click", close);
    $(".lb-prev", lb).addEventListener("click", function () { go(ci - 1); });
    $(".lb-next", lb).addEventListener("click", function () { go(ci + 1); });
    lb.addEventListener("click", function (e) { if (e.target === lb) close(); });
    document.addEventListener("keydown", function (e) {
      if (!lb.classList.contains("is-open")) return;
      if (e.key === "Escape") close(); if (e.key === "ArrowLeft") go(ci - 1); if (e.key === "ArrowRight") go(ci + 1);
    });
    var sx = 0;
    lb.addEventListener("touchstart", function (e) { sx = e.touches[0].clientX; }, { passive: true });
    lb.addEventListener("touchend", function (e) { var dx = e.changedTouches[0].clientX - sx; if (Math.abs(dx) > 50) go(ci + (dx < 0 ? 1 : -1)); });
  }

  /* ---- Forms (contact enquiry + platform early access) ---- */
  $$("form[data-ajax]").forEach(function (form) {
    var status = $(".form-status", form);
    var subject = form.dataset.subject || "Project enquiry";
    function setStatus(msg, err) { status.textContent = msg; status.classList.add("show"); status.classList.toggle("error", !!err); }
    function validate() {
      var ok = true;
      $$("[required]", form).forEach(function (inp) {
        var f = inp.closest(".field"), bad = !inp.value.trim() ||
          (inp.type === "email" && !/^[^\s@]+@[^\s@]+\.[^\s@]+$/.test(inp.value)) ||
          (inp.type === "tel" && inp.value.replace(/\D/g, "").length < 10);
        if (f) f.classList.toggle("invalid", bad);
        if (bad && ok) { inp.focus(); ok = false; }
      });
      return ok;
    }
    function summary() {
      var fd = new FormData(form), lines = [], seen = {};
      fd.forEach(function (v, k) {
        if (/^(form-name|bot-field|access_key|subject|from_name|form)$/.test(k) || seen[k] || !v) return;
        seen[k] = 1; lines.push(k.replace(/_/g, " ") + ": " + fd.getAll(k).join(", "));
      });
      return lines.join("\n");
    }
    var wa = $("[data-wa-submit]", form);
    if (wa) wa.addEventListener("click", function () {
      if (!validate()) return;
      window.open("https://wa.me/" + wa.dataset.waSubmit + "?text=" + encodeURIComponent("Hello Kavinan Design Studio,\n" + summary()), "_blank", "noopener");
    });
    form.addEventListener("submit", function (e) {
      e.preventDefault();
      if (!validate()) return;
      if ($("[name='bot-field']", form) && $("[name='bot-field']", form).value) return;
      var btn = $("button[type='submit']", form); btn.disabled = true;
      var endpoint = form.dataset.endpoint || "/", external = /^https?:/.test(endpoint);
      var key = $("[name='access_key']", form);
      // External services (Web3Forms, Formspree) take multipart FormData; Netlify takes urlencoded.
      var req = external
        ? { method: "POST", headers: { "Accept": "application/json" }, body: new FormData(form) }
        : { method: "POST", headers: { "Content-Type": "application/x-www-form-urlencoded", "Accept": "application/json" }, body: new URLSearchParams(new FormData(form)).toString() };
      (key && !key.value ? Promise.reject(new Error("form access key not set")) : fetch(endpoint, req))
        .then(function (r) {
          if (!r.ok) throw new Error(r.status);
          form.reset();
          setStatus(form.dataset.success || "Thank you — your message has reached our studio. We'll reply within one working day.");
          if (window.gtag) window.gtag("event", "generate_lead", { form: form.getAttribute("name") || "form" });
        })
        .catch(function () {
          var mail = form.dataset.mail;
          setStatus("We couldn't send the form from here. Please WhatsApp us or email " + mail + ".", true);
          window.location.href = "mailto:" + mail + "?subject=" + encodeURIComponent(subject) + "&body=" + encodeURIComponent(summary());
        })
        .then(function () { btn.disabled = false; });
    });
    $$("input, select, textarea", form).forEach(function (i) { i.addEventListener("input", function () { var f = i.closest(".field"); if (f) f.classList.remove("invalid"); }); });
  });

  /* ---- Share buttons ---- */
  $$("[data-share]").forEach(function (b) {
    b.addEventListener("click", function () {
      var data = { title: document.title, url: location.href };
      if (navigator.share) navigator.share(data).catch(function () {});
      else if (navigator.clipboard) navigator.clipboard.writeText(location.href).then(function () { b.textContent = "Link copied"; });
    });
  });

  /* ---- Headlines: split into words that rise in ---- */
  var splitEls = $$("[data-split], .section-head h2, .feature__body h2");
  if (!reduce) {
    splitEls.forEach(function (el) {
      var i = 0;
      (function walk(node) {
        Array.prototype.slice.call(node.childNodes).forEach(function (n) {
          if (n.nodeType === 3) {
            var frag = document.createDocumentFragment();
            n.textContent.split(/(\s+)/).forEach(function (part) {
              if (!part) return;
              if (/^\s+$/.test(part)) { frag.appendChild(document.createTextNode(" ")); return; }
              var w = document.createElement("span"), inner = document.createElement("span");
              w.className = "w"; inner.textContent = part; inner.style.setProperty("--i", i++);
              w.appendChild(inner); frag.appendChild(w);
            });
            n.parentNode.replaceChild(frag, n);
          } else if (n.nodeType === 1 && !n.classList.contains("w") && n.tagName !== "svg") { walk(n); }
        });
      })(el);
      el.classList.add("is-split");
    });
  }
  if ("IntersectionObserver" in window && !reduce) {
    var hio = new IntersectionObserver(function (es) {
      es.forEach(function (en) { if (en.isIntersecting) { en.target.classList.add("is-in"); hio.unobserve(en.target); } });
    }, { threshold: 0.3 });
    splitEls.forEach(function (el) { if (el.closest(".hero")) { requestAnimationFrame(function () { el.classList.add("is-in"); }); } else { hio.observe(el); } });
  } else {
    splitEls.forEach(function (el) { el.classList.add("is-in"); });
  }

  /* ---- Line sketches draw themselves when they scroll into view ---- */
  var sketches = $$(".sketch");
  if (sketches.length && "IntersectionObserver" in window && !reduce) {
    sketches.forEach(function (svg) {
      $$("path, circle, ellipse, rect, line, polyline", svg).forEach(function (el, k) {
        try { el.style.setProperty("--len", Math.ceil(el.getTotalLength()) + 2); el.style.setProperty("--k", k); } catch (e) {}
      });
    });
    doc.classList.add("js-draw");
    var sio = new IntersectionObserver(function (es) {
      es.forEach(function (en) { if (en.isIntersecting) { en.target.classList.add("is-drawn"); sio.unobserve(en.target); } });
    }, { threshold: 0.3 });
    sketches.forEach(function (s) { sio.observe(s); });
  }

  /* ---- Scroll engine: progress bar, hero & doodle parallax, sketch->render story, film strip ---- */
  var scrubs = $$("[data-scrub]"), films = $$("[data-film]"), pars = $$("[data-parallax]"), heroEl = $(".hero"), ticking = false;
  function frame() {
    ticking = false;
    var vh = window.innerHeight, y = window.scrollY, max = document.documentElement.scrollHeight - vh;
    doc.style.setProperty("--sp", max > 0 ? (y / max).toFixed(4) : 0);
    if (reduce) return;
    if (heroEl && y < vh * 1.3) heroEl.style.setProperty("--hy", (y * 0.3).toFixed(1) + "px");
    scrubs.forEach(function (sc) {
      var r = sc.getBoundingClientRect(), total = sc.offsetHeight - vh;
      if (r.bottom < 0 || r.top > vh) return;
      var p = Math.min(1, Math.max(0, -r.top / Math.max(total, 1)));
      sc.style.setProperty("--p", p.toFixed(4));
      $$(".scrub__steps li", sc).forEach(function (li) { li.classList.toggle("on", p >= parseFloat(li.dataset.at)); });
    });
    films.forEach(function (f) {
      var tr = $(".film__track", f), r = f.getBoundingClientRect();
      if (r.bottom < 0 || r.top > vh || window.innerWidth <= 700) return;
      var p = Math.min(1, Math.max(0, (vh - r.top) / (vh + r.height)));
      tr.style.setProperty("--fx", (-p * Math.max(0, tr.scrollWidth - window.innerWidth)).toFixed(1) + "px");
    });
    pars.forEach(function (el) {
      var r = el.parentElement.getBoundingClientRect();
      if (r.bottom < 0 || r.top > vh) return;
      el.style.setProperty("--py", (-(r.top + r.height / 2 - vh / 2) * parseFloat(el.dataset.parallax)).toFixed(1) + "px");
    });
  }
  function requestFrame() { if (!ticking) { ticking = true; requestAnimationFrame(frame); } }
  window.addEventListener("scroll", requestFrame, { passive: true });
  window.addEventListener("resize", requestFrame);
  frame();

  /* ---- Sketch <-> render comparison sliders ---- */
  $$(".compare").forEach(function (c) {
    var range = $(".compare__range", c);
    function set(v) { c.style.setProperty("--pos", v + "%"); }
    range.addEventListener("input", function () { set(range.value); });
    if (!("IntersectionObserver" in window) || reduce) return;
    var cio = new IntersectionObserver(function (es) {
      if (!es[0].isIntersecting) return;
      cio.disconnect();
      var t0 = null;
      (function sweep(ts) {          // a one-time sweep shows visitors the slider is interactive
        t0 = t0 || ts;
        var k = Math.min((ts - t0) / 1800, 1), e = 1 - Math.pow(1 - k, 3);
        var v = 50 + 38 * Math.sin(e * Math.PI) * (k < 1 ? 1 : 0);
        set(v.toFixed(1)); range.value = v;
        if (k < 1) requestAnimationFrame(sweep);
      })(performance.now());
    }, { threshold: 0.6 });
    cio.observe(c);
  });

  /* ---- Gentle 3D tilt on project cards (mouse only) ---- */
  if (window.matchMedia("(hover: hover) and (pointer: fine)").matches && !reduce) {
    $$(".pcard").forEach(function (card) {
      var m = $(".media", card);
      card.addEventListener("pointermove", function (e) {
        var b = m.getBoundingClientRect(), x = (e.clientX - b.left) / b.width - .5, yy = (e.clientY - b.top) / b.height - .5;
        m.style.setProperty("--ry", (x * 6).toFixed(2) + "deg"); m.style.setProperty("--rx", (-yy * 6).toFixed(2) + "deg");
      });
      card.addEventListener("pointerleave", function () { m.style.setProperty("--ry", "0deg"); m.style.setProperty("--rx", "0deg"); });
    });
  }

  /* ---- Year ---- */
  $$("[data-year]").forEach(function (y) { y.textContent = new Date().getFullYear(); });
})();

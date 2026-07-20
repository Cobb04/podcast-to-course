/**
 * PODCAST-TO-COURSE — INTERACTIVE JS ENGINE
 * Handles: nav, quiz interaction, framework visualization, chat groups
 *
 * DOM contract (must match module HTML):
 *   Quiz:        .quiz > .quiz-prompt + .quiz-options[data-correct="N"] + .quiz-feedback > .quiz-feedback-text[hidden]
 *   Framework:   .framework-visualization > .fw-layer (×3) + button.fw-btn
 *   Nav:         .nav-dot[data-target="module-N"] → scrolls to #module-N
 *   Chat:        .chat-group > .chat-message.chat-left|.chat-right > .chat-sender + p
 */

(function () {
  'use strict';

  function $(s, c) { return (c || document).querySelector(s); }
  function $$(s, c) { return Array.from((c || document).querySelectorAll(s)); }

  /* ── NAVIGATION ──────────────────────────── */
  var progressBar = $('#progress-bar');
  var navDots = $$('.nav-dot');
  var modules = $$('.module');

  function updateNav() {
    if (progressBar) {
      var h = document.documentElement;
      var pct = h.scrollHeight > window.innerHeight
        ? (window.scrollY / (h.scrollHeight - window.innerHeight)) * 100 : 0;
      progressBar.style.width = Math.min(100, pct) + '%';
    }
    var mid = window.scrollY + window.innerHeight / 2;
    modules.forEach(function (mod, i) {
      var dot = navDots[i];
      if (!dot) return;
      var top = mod.offsetTop;
      var bottom = top + mod.offsetHeight;
      if (mid >= top && mid < bottom) {
        dot.classList.add('active');
        dot.classList.remove('visited');
      } else if (window.scrollY + window.innerHeight > top + 80) {
        dot.classList.remove('active');
        dot.classList.add('visited');
      } else {
        dot.classList.remove('active', 'visited');
      }
    });
  }

  window.addEventListener('scroll', function () {
    requestAnimationFrame(updateNav);
  }, { passive: true });
  updateNav();

  navDots.forEach(function (dot) {
    dot.addEventListener('click', function () {
      var t = $('#' + dot.dataset.target);
      if (t) t.scrollIntoView({ behavior: 'smooth' });
    });
  });

  /* ── KEYBOARD ────────────────────────────── */
  document.addEventListener('keydown', function (e) {
    if (['INPUT', 'TEXTAREA', 'SELECT'].indexOf(e.target.tagName) !== -1) return;
    if (e.key === 'ArrowDown' || e.key === 'ArrowRight' || e.key === 'j') {
      e.preventDefault();
      var mid = window.scrollY + window.innerHeight / 2;
      for (var i = 0; i < modules.length; i++) {
        if (modules[i].offsetTop > mid + 40) {
          modules[i].scrollIntoView({ behavior: 'smooth' });
          break;
        }
      }
    }
    if (e.key === 'ArrowUp' || e.key === 'ArrowLeft' || e.key === 'k') {
      e.preventDefault();
      var mid2 = window.scrollY + window.innerHeight / 2;
      for (var j = modules.length - 1; j >= 0; j--) {
        if (modules[j].offsetTop + modules[j].offsetHeight < mid2 - 40) {
          modules[j].scrollIntoView({ behavior: 'smooth' });
          break;
        }
      }
    }
  });

  /* ── QUIZ ENGINE ─────────────────────────── */
  $$('.quiz').forEach(function (quiz) {
    var options = $$('.quiz-option', quiz);
    var feedback = $('.quiz-feedback', quiz);
    var feedbackText = $('.quiz-feedback-text', quiz);
    var optionsDiv = $('.quiz-options', quiz);
    var correctVal = optionsDiv ? optionsDiv.dataset.correct : null;

    options.forEach(function (btn) {
      btn.addEventListener('click', function () {
        if (options[0].disabled) return; // Already answered

        // Select & check
        options.forEach(function (o) { o.classList.remove('selected'); });
        btn.classList.add('selected');

        var isCorrect = btn.dataset.value === correctVal;
        options.forEach(function (o) { o.disabled = true; });

        // Mark correct/incorrect
        btn.classList.add(isCorrect ? 'correct' : 'incorrect');
        if (!isCorrect) {
          var correctBtn = null;
          options.forEach(function (o) {
            if (o.dataset.value === correctVal) correctBtn = o;
          });
          if (correctBtn) correctBtn.classList.add('correct');
        }

        // Show feedback from hidden span (safe — no escaping issues)
        if (feedback && feedbackText) {
          var text = feedbackText.textContent.trim();
          feedback.textContent = (isCorrect ? '✅ ' : '❌ ') + text;
          feedback.className = 'quiz-feedback show ' + (isCorrect ? 'success' : 'error');
        }
      });
    });
  });

  /* ── FRAMEWORK VISUALIZATION ─────────────── */
  $$('.framework-visualization').forEach(function (fw) {
    var allLayers = $$('.fw-layer', fw);
    var btn = $('.fw-btn', fw);
    var currentStep = 1;

    // Init: hide layers beyond first
    allLayers.forEach(function (layer, i) {
      if (i === 0) {
        layer.classList.add('active-layer', 'revealed');
      } else {
        layer.classList.add('hidden-layer');
        layer.style.display = 'none';
      }
    });

    if (btn) {
      btn.addEventListener('click', function () {
        if (currentStep < allLayers.length) {
          var layer = allLayers[currentStep];
          layer.style.display = 'block';
          layer.classList.remove('hidden-layer');
          layer.classList.add('active-layer');
          layer.offsetHeight; // force reflow
          layer.classList.add('revealed');

          allLayers.forEach(function (l, i) {
            if (i !== currentStep) l.classList.remove('active-layer');
          });

          currentStep++;
          if (currentStep >= allLayers.length) {
            btn.textContent = '✓ 全部展开';
            btn.classList.add('done');
          } else {
            btn.textContent = '展开下一层 →';
          }
        }
      });
    }
  });

  /* ── CHAT STAGGER ────────────────────────── */
  $$('.chat-group').forEach(function (group) {
    var msgs = $$('.chat-message', group);
    msgs.forEach(function (msg, i) {
      msg.style.animation = 'fadeSlideUp 0.4s var(--ease-out) both';
      msg.style.animationDelay = (i * 0.5) + 's';
    });
  });

})();

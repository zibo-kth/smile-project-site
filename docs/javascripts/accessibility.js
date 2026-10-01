(function () {
  function makeToggleKeyboardAccessible(selector, toggleId, label) {
    var control = document.querySelector(selector);
    var toggle = document.getElementById(toggleId);
    if (!control || !toggle) return;

    control.setAttribute("role", "button");
    control.setAttribute("tabindex", "0");
    control.setAttribute("aria-controls", toggleId);
    control.setAttribute("aria-label", label);

    function syncExpanded() {
      control.setAttribute("aria-expanded", toggle.checked ? "true" : "false");
    }

    if (!control.dataset.keyboardToggle) {
      control.dataset.keyboardToggle = "true";
      control.addEventListener("keydown", function (event) {
        if (event.key === "Enter" || event.key === " ") {
          event.preventDefault();
          event.stopPropagation();
          toggle.checked = !toggle.checked;
          toggle.dispatchEvent(new Event("change", { bubbles: true }));
        }
      });
      toggle.addEventListener("change", function () {
        syncExpanded();
        if (toggleId === "__search" && toggle.checked) {
          window.setTimeout(function () {
            if (!toggle.checked) return;
            var input = document.querySelector(".md-search__input");
            if (input) input.focus();
          }, 0);
        }
      });
    }
    syncExpanded();
  }

  function enhanceAccessibility() {
    var searchDialog = document.querySelector('.md-search[role="dialog"]');
    if (searchDialog && !searchDialog.hasAttribute("aria-label")) {
      searchDialog.setAttribute("aria-label", "Site search");
    }
    if (searchDialog && !searchDialog.dataset.focusTrap) {
      searchDialog.dataset.focusTrap = "true";
      searchDialog.addEventListener("focusout", function () {
        window.setTimeout(function () {
          var searchToggle = document.getElementById("__search");
          if (!searchToggle || !searchToggle.checked) return;
          if (searchDialog.contains(document.activeElement)) return;
          var input = searchDialog.querySelector(".md-search__input");
          if (input) input.focus();
        }, 0);
      });
    }

    makeToggleKeyboardAccessible(
      'label.md-header__button[for="__drawer"]',
      "__drawer",
      "Open navigation"
    );
    makeToggleKeyboardAccessible(
      'label.md-header__button[for="__search"]',
      "__search",
      "Open search"
    );
  }

  document.addEventListener("DOMContentLoaded", enhanceAccessibility);
  if (typeof document$ !== "undefined") {
    document$.subscribe(enhanceAccessibility);
  }

  window.addEventListener("keydown", function (event) {
    var searchToggle = document.getElementById("__search");
    var drawerToggle = document.getElementById("__drawer");

    if (event.key !== "Escape") return;
    var openToggle = searchToggle && searchToggle.checked ? searchToggle :
      drawerToggle && drawerToggle.checked ? drawerToggle : null;
    if (!openToggle) return;

    event.preventDefault();
    event.stopImmediatePropagation();
    openToggle.checked = false;
    openToggle.dispatchEvent(new Event("change", { bubbles: true }));
    var opener = document.querySelector(
      'label.md-header__button[for="' + openToggle.id + '"]'
    );
    if (opener) opener.focus();
  }, true);

  document.addEventListener("keydown", function (event) {
    var searchToggle = document.getElementById("__search");

    if (event.key !== "Tab" || !searchToggle || !searchToggle.checked) return;
    var dialog = document.querySelector('.md-search[role="dialog"]');
    if (!dialog) return;

    var focusable = Array.prototype.filter.call(
      dialog.querySelectorAll(
        'a[href], button:not([disabled]), input:not([disabled]), [tabindex]:not([tabindex="-1"])'
      ),
      function (element) {
        return element.getClientRects().length > 0;
      }
    );
    if (!focusable.length) return;

    event.preventDefault();
    event.stopPropagation();
    var currentIndex = focusable.indexOf(document.activeElement);
    var nextIndex;
    if (currentIndex < 0) {
      nextIndex = event.shiftKey ? focusable.length - 1 : 0;
    } else if (event.shiftKey) {
      nextIndex = (currentIndex - 1 + focusable.length) % focusable.length;
    } else {
      nextIndex = (currentIndex + 1) % focusable.length;
    }
    focusable[nextIndex].focus();
  }, true);
})();

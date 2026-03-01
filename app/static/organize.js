(function () {
  "use strict";

  var sortables = [];
  var boxSortable = null;

  function initSortables() {
    // Destroy existing item sortable instances
    sortables.forEach(function (s) { s.destroy(); });
    sortables = [];

    document.querySelectorAll(".organize-dropzone").forEach(function (el) {
      var s = new Sortable(el, {
        group: "organize",
        animation: 150,
        ghostClass: "organize-ghost",
        chosenClass: "organize-chosen",
        dragClass: "organize-drag",
        delay: 150,
        delayOnTouchOnly: true,
        touchStartThreshold: 5,
        fallbackTolerance: 3,
        filter: ".organize-empty",
        onEnd: handleDrop,
      });
      sortables.push(s);
    });

    // Box reordering (only init once)
    if (!boxSortable) {
      var boxList = document.getElementById("boxes-list");
      if (boxList) {
        boxSortable = new Sortable(boxList, {
          animation: 200,
          ghostClass: "organize-box-ghost",
          delay: 500,
          delayOnTouchOnly: true,
          touchStartThreshold: 5,
          forceFallback: true,
          fallbackTolerance: 3,
          filter: ".organize-dropzone",
          preventOnFilter: false,
        });
      }
    }
  }

  function handleDrop(evt) {
    var itemEl = evt.item;
    var itemId = itemEl.dataset.itemId;
    var targetZone = evt.to;
    var sourceZone = evt.from;
    var newBoxId = targetZone.dataset.boxId || "";
    var oldBoxId = sourceZone.dataset.boxId || "";

    // No actual move
    if (newBoxId === oldBoxId) return;

    // Remove "Sin items" placeholders
    removeEmptyPlaceholder(targetZone);

    var formData = new FormData();
    formData.append("box_id", newBoxId);

    fetch("/items/" + itemId + "/move", {
      method: "POST",
      headers: { "HX-Request": "true" },
      body: formData,
      credentials: "same-origin",
    })
      .then(function (resp) {
        if (!resp.ok) throw new Error("Move failed");
        return resp.text();
      })
      .then(function (html) {
        processOobSwaps(html);
        initSortables();
      })
      .catch(function () {
        // Revert: reload page on error
        window.location.reload();
      });
  }

  function processOobSwaps(html) {
    // Parse returned HTML and replace elements by id using hx-swap-oob
    var parser = new DOMParser();
    var doc = parser.parseFromString(html, "text/html");
    var oobElements = doc.querySelectorAll("[hx-swap-oob]");

    oobElements.forEach(function (newEl) {
      var id = newEl.id;
      if (!id) return;
      var existing = document.getElementById(id);
      if (!existing) return;

      // For containers, preserve the parent wrapper
      newEl.removeAttribute("hx-swap-oob");
      existing.replaceWith(newEl);
    });

    // Auto-expand collapsed boxes that received items
    doc.querySelectorAll(".organize-dropzone").forEach(function (zone) {
      var id = zone.id;
      var realZone = document.getElementById(id);
      if (!realZone) return;
      if (realZone.children.length > 0 && !realZone.querySelector(".organize-empty")) {
        var content = realZone.closest(".organize-box-content");
        if (content && content.classList.contains("collapsed")) {
          content.classList.remove("collapsed");
          var chevron = content.previousElementSibling &&
            content.previousElementSibling.querySelector(".organize-chevron");
          if (chevron) chevron.classList.remove("rotate-[-90deg]");
        }
      }
    });
  }

  function removeEmptyPlaceholder(zone) {
    var empty = zone.querySelector(".organize-empty");
    if (empty) empty.remove();
  }

  // Collapse/expand toggle
  document.addEventListener("click", function (e) {
    var toggle = e.target.closest(".organize-box-toggle");
    if (!toggle) return;
    var box = toggle.closest(".organize-box");
    if (!box) return;
    var content = box.querySelector(".organize-box-content");
    if (!content) return;
    content.classList.toggle("collapsed");
    var chevron = toggle.querySelector(".organize-chevron");
    if (chevron) chevron.classList.toggle("rotate-[-90deg]");
  });

  // Init on load
  initSortables();
})();

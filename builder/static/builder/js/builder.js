// Initialize SortableJS on field lists and sections
function initSortable() {
  // Make field lists sortable (within and between sections)
  document.querySelectorAll('.field-list').forEach(el => {
    if (el._sortable) return; // Already initialized
    el._sortable = new Sortable(el, {
      group: 'fields',
      animation: 150,
      handle: '.field-handle',
      ghostClass: 'sortable-ghost',
      chosenClass: 'sortable-chosen',
      onStart: function() {
        document.body.classList.add('is-dragging');
      },
      onEnd: function(evt) {
        document.body.classList.remove('is-dragging');
        const fieldId = evt.item.dataset.fieldId;
        const newSectionId = evt.to.dataset.sectionId;

        // Collect all items in new order
        const items = [];
        evt.to.querySelectorAll('.field-row').forEach((row, index) => {
          items.push({
            id: row.dataset.fieldId,
            section_id: newSectionId,
            rank: index,
          });
        });

        // Also update the source section if different
        if (evt.from !== evt.to) {
          evt.from.querySelectorAll('.field-row').forEach((row, index) => {
            items.push({
              id: row.dataset.fieldId,
              section_id: evt.from.dataset.sectionId,
              rank: index,
            });
          });
        }

        // Get template PK from URL
        const pathParts = window.location.pathname.split('/');
        const templatePk = pathParts[2]; // /forms/<uuid>/

        fetch(`/forms/${templatePk}/reorder/`, {
          method: 'POST',
          headers: {
            'Content-Type': 'application/json',
            'X-CSRFToken': document.querySelector('[name=csrfmiddlewaretoken]')?.value
              || document.cookie.match(/csrftoken=([^;]+)/)?.[1]
              || '',
          },
          body: JSON.stringify({ items }),
        });
      },
    });
  });

  // Make sections sortable
  const canvas = document.getElementById('canvas');
  if (canvas && !canvas._sortable) {
    canvas._sortable = new Sortable(canvas, {
      animation: 150,
      handle: '.section-handle',
      ghostClass: 'sortable-ghost',
      chosenClass: 'sortable-chosen',
    });
  }
}

// Initialize on page load
document.addEventListener('DOMContentLoaded', initSortable);

// Re-initialize after HTMX swaps
document.addEventListener('htmx:afterSwap', function() {
  requestAnimationFrame(initSortable);
});

// Re-apply field-active class after DOM has fully settled
document.addEventListener('htmx:afterSettle', function() {
  const activeId = document.body.dataset.activeFieldId;
  if (activeId) {
    const row = document.getElementById('field-' + activeId);
    if (row && !row.classList.contains('field-active')) {
      row.classList.add('field-active');
    }
  }
});

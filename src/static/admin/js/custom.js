(function () {
  document.addEventListener('DOMContentLoaded', function () {
    const buttons = document.querySelectorAll('.obc-admin-button, .button, input[type="submit"], input[type="button"]');
    buttons.forEach(function (button) {
      button.addEventListener('mouseenter', function () {
        this.style.transform = 'translateY(-2px)';
      });
      button.addEventListener('mouseleave', function () {
        this.style.transform = 'translateY(0)';
      });
    });

    const messages = document.querySelectorAll('.messagelist li');
    messages.forEach(function (message) {
      message.classList.add('obc-fade-enter');
      setTimeout(function () {
        message.style.transition = 'opacity 0.3s ease, transform 0.3s ease';
        message.style.opacity = '0';
        message.style.transform = 'translateY(-8px)';
        setTimeout(function () {
          message.remove();
        }, 300);
      }, 6000);
    });

    const toggleFilters = document.getElementById('toggle-filters');
    const sidebar = document.getElementById('changelist-filter');
    if (toggleFilters && sidebar) {
      toggleFilters.addEventListener('click', function () {
        const icon = toggleFilters.querySelector('i');
        sidebar.hidden = !sidebar.hidden;
        toggleFilters.setAttribute('aria-expanded', (!sidebar.hidden).toString());
        if (icon) {
          icon.classList.toggle('fa-filter-circle-xmark', !sidebar.hidden);
          icon.classList.toggle('fa-filter', sidebar.hidden);
        }
      });
    }

    const selectAllCheckbox = document.querySelector('.action-select-all');
    const actionCheckboxes = document.querySelectorAll('.action-checkbox');
    if (selectAllCheckbox && actionCheckboxes.length) {
      selectAllCheckbox.addEventListener('change', function () {
        const checked = selectAllCheckbox.checked;
        actionCheckboxes.forEach(function (checkbox) {
          checkbox.checked = checked;
        });
      });

      actionCheckboxes.forEach(function (checkbox) {
        checkbox.addEventListener('change', function () {
          const checkedCount = document.querySelectorAll('.action-checkbox:checked').length;
          selectAllCheckbox.checked = checkedCount === actionCheckboxes.length;
          selectAllCheckbox.indeterminate = checkedCount > 0 && checkedCount < actionCheckboxes.length;
        });
      });
    }

    const submitButtons = document.querySelectorAll('form button[type="submit"], form input[type="submit"]');
    submitButtons.forEach(function (submitButton) {
      submitButton.addEventListener('click', function () {
        const form = submitButton.closest('form');
        const originalText = submitButton.value || submitButton.innerText;
        submitButton.setAttribute('data-original-text', originalText);
        if (submitButton.tagName === 'INPUT') {
          submitButton.value = 'Processing…';
        } else {
          submitButton.innerText = 'Processing…';
        }
        submitButton.setAttribute('disabled', 'disabled');
        submitButton.classList.add('is-loading');
        if (form) {
          form.classList.add('obc-form-submitted');
        }
        setTimeout(function () {
          submitButton.removeAttribute('disabled');
          submitButton.classList.remove('is-loading');
          if (submitButton.tagName === 'INPUT') {
            submitButton.value = submitButton.getAttribute('data-original-text');
          } else {
            submitButton.innerText = submitButton.getAttribute('data-original-text');
          }
        }, 4000);
      });
    });

    const adminForms = document.querySelectorAll('form[id$="_form"], .change-list #changelist-form');
    adminForms.forEach(function (form) {
      const trackedInputs = form.querySelectorAll('input, select, textarea');
      let formDirty = false;

      trackedInputs.forEach(function (input) {
        input.addEventListener('focus', function () {
          const row = input.closest('.form-row');
          if (row) {
            row.classList.add('obc-form-row--focus');
          }
        });

        input.addEventListener('blur', function () {
          const row = input.closest('.form-row');
          if (row) {
            row.classList.remove('obc-form-row--focus');
          }
        });

        input.addEventListener('change', function () {
          formDirty = true;
        });

        input.addEventListener('input', function () {
          if (input.tagName === 'TEXTAREA') {
            input.style.height = 'auto';
            input.style.height = input.scrollHeight + 'px';
          }
        });

        if (input.tagName === 'TEXTAREA') {
          input.style.height = 'auto';
          input.style.height = input.scrollHeight + 'px';
        }
      });

      const fileInputs = form.querySelectorAll('input[type="file"]');
      fileInputs.forEach(function (input) {
        input.addEventListener('change', function () {
          var fileName = input.files && input.files[0] ? input.files[0].name : '';
          if (!fileName) {
            return;
          }
          var container = input.parentElement;
          if (!container) {
            return;
          }
          var label = container.querySelector('.obc-file-label');
          if (!label) {
            label = document.createElement('p');
            label.className = 'obc-file-label text-sm text-slate-500 mt-2';
            container.appendChild(label);
          }
          label.textContent = 'Selected: ' + fileName;
        });
      });

      form.addEventListener('submit', function () {
        formDirty = false;
      });

      window.addEventListener('beforeunload', function (event) {
        if (formDirty && !form.classList.contains('obc-form-submitted')) {
          event.preventDefault();
          event.returnValue = '';
        }
      });

      document.addEventListener('keydown', function (event) {
        if ((event.ctrlKey || event.metaKey) && event.key.toLowerCase() === 's') {
          const saveButton = form.querySelector('button[name="_save"], input[name="_save"]');
          if (saveButton) {
            event.preventDefault();
            saveButton.click();
          }
        }
        if (event.key === 'Escape') {
          const cancelLink = form.querySelector('a[href*="changelist"]');
          if (cancelLink) {
            window.location.href = cancelLink.href;
          }
        }
      });
    });
  });
})();

/* ===================================
   ENTERPRISE HOSPITAL MANAGEMENT SYSTEM
   Main JavaScript
   =================================== */

// Initialize when DOM is ready
document.addEventListener('DOMContentLoaded', function() {
  initializeApp();
});

/**
 * Main initialization function
 */
function initializeApp() {
  initializeTooltips();
  initializePopovers();
  initializeFormValidation();
  initializeDataTables();
  initializeConfirmDialogs();
  initializeAlerts();
  initializeSearchFilters();
  initializeDateInputs();
  addLoadingStates();
}

/**
 * Initialize Bootstrap tooltips
 */
function initializeTooltips() {
  const tooltipTriggerList = [].slice.call(
    document.querySelectorAll('[data-bs-toggle="tooltip"]')
  );
  tooltipTriggerList.map(function (tooltipTriggerEl) {
    return new bootstrap.Tooltip(tooltipTriggerEl);
  });
}

/**
 * Initialize Bootstrap popovers
 */
function initializePopovers() {
  const popoverTriggerList = [].slice.call(
    document.querySelectorAll('[data-bs-toggle="popover"]')
  );
  popoverTriggerList.map(function (popoverTriggerEl) {
    return new bootstrap.Popover(popoverTriggerEl);
  });
}

/**
 * Enhanced form validation with real-time feedback
 */
function initializeFormValidation() {
  const forms = document.querySelectorAll('.needs-validation');

  Array.from(forms).forEach(form => {
    form.addEventListener('submit', event => {
      if (!form.checkValidity()) {
        event.preventDefault();
        event.stopPropagation();

        // Show first invalid field
        const firstInvalid = form.querySelector(':invalid');
        if (firstInvalid) {
          firstInvalid.focus();
          firstInvalid.scrollIntoView({ behavior: 'smooth', block: 'center' });
        }
      }

      form.classList.add('was-validated');
    }, false);

    // Real-time validation on input
    const inputs = form.querySelectorAll('input, select, textarea');
    inputs.forEach(input => {
      input.addEventListener('blur', () => {
        if (input.checkValidity()) {
          input.classList.remove('is-invalid');
          input.classList.add('is-valid');
        } else {
          input.classList.remove('is-valid');
          input.classList.add('is-invalid');
        }
      });

      input.addEventListener('input', () => {
        if (form.classList.contains('was-validated')) {
          if (input.checkValidity()) {
            input.classList.remove('is-invalid');
            input.classList.add('is-valid');
          } else {
            input.classList.remove('is-valid');
            input.classList.add('is-invalid');
          }
        }
      });
    });
  });
}

/**
 * Initialize searchable and sortable data tables
 */
function initializeDataTables() {
  const tables = document.querySelectorAll('.data-table');

  tables.forEach(table => {
    // Add search functionality if not present
    if (!table.closest('.table-wrapper')?.querySelector('.table-search')) {
      addTableSearch(table);
    }

    // Add sorting functionality
    addTableSorting(table);

    // Add row highlighting
    const rows = table.querySelectorAll('tbody tr');
    rows.forEach(row => {
      row.addEventListener('click', function() {
        rows.forEach(r => r.classList.remove('table-active'));
        this.classList.add('table-active');
      });
    });
  });
}

/**
 * Add search functionality to table
 */
function addTableSearch(table) {
  const wrapper = document.createElement('div');
  wrapper.className = 'table-search-wrapper mb-3';

  const searchInput = document.createElement('input');
  searchInput.type = 'text';
  searchInput.className = 'form-control';
  searchInput.placeholder = 'Search table...';

  const searchIcon = document.createElement('i');
  searchIcon.className = 'bi bi-search';

  const searchContainer = document.createElement('div');
  searchContainer.className = 'input-group';

  const iconSpan = document.createElement('span');
  iconSpan.className = 'input-group-text';
  iconSpan.appendChild(searchIcon);

  searchContainer.appendChild(iconSpan);
  searchContainer.appendChild(searchInput);
  wrapper.appendChild(searchContainer);

  table.parentNode.insertBefore(wrapper, table);

  searchInput.addEventListener('input', function(e) {
    const searchTerm = e.target.value.toLowerCase();
    const rows = table.querySelectorAll('tbody tr');

    rows.forEach(row => {
      const text = row.textContent.toLowerCase();
      row.style.display = text.includes(searchTerm) ? '' : 'none';
    });

    updateTableEmptyState(table);
  });
}

/**
 * Add sorting functionality to table headers
 */
function addTableSorting(table) {
  const headers = table.querySelectorAll('thead th');

  headers.forEach((header, index) => {
    // Skip action columns
    if (header.textContent.toLowerCase().includes('action')) return;

    header.style.cursor = 'pointer';
    header.classList.add('sortable');
    header.innerHTML += ' <i class="bi bi-arrow-down-up ms-1"></i>';

    let ascending = true;

    header.addEventListener('click', () => {
      const tbody = table.querySelector('tbody');
      const rows = Array.from(tbody.querySelectorAll('tr'));

      rows.sort((a, b) => {
        const aValue = a.cells[index].textContent.trim();
        const bValue = b.cells[index].textContent.trim();

        // Try to parse as number
        const aNum = parseFloat(aValue);
        const bNum = parseFloat(bValue);

        if (!isNaN(aNum) && !isNaN(bNum)) {
          return ascending ? aNum - bNum : bNum - aNum;
        }

        // String comparison
        return ascending
          ? aValue.localeCompare(bValue)
          : bValue.localeCompare(aValue);
      });

      ascending = !ascending;

      // Update sort icons
      headers.forEach(h => {
        const icon = h.querySelector('i');
        if (icon && h !== header) {
          icon.className = 'bi bi-arrow-down-up ms-1';
        }
      });

      const icon = header.querySelector('i');
      if (icon) {
        icon.className = ascending
          ? 'bi bi-sort-down ms-1'
          : 'bi bi-sort-up ms-1';
      }

      rows.forEach(row => tbody.appendChild(row));
    });
  });
}

/**
 * Update table empty state when filtering
 */
function updateTableEmptyState(table) {
  const visibleRows = Array.from(table.querySelectorAll('tbody tr'))
    .filter(row => row.style.display !== 'none');

  let emptyState = table.parentNode.querySelector('.table-empty-state');

  if (visibleRows.length === 0) {
    if (!emptyState) {
      emptyState = document.createElement('div');
      emptyState.className = 'table-empty-state text-center p-5';
      emptyState.innerHTML = `
        <i class="bi bi-search display-4 text-muted"></i>
        <h5 class="mt-3 text-muted">No results found</h5>
        <p class="text-muted">Try adjusting your search criteria</p>
      `;
      table.parentNode.appendChild(emptyState);
    }
    table.style.display = 'none';
  } else {
    if (emptyState) {
      emptyState.remove();
    }
    table.style.display = '';
  }
}

/**
 * Initialize confirmation dialogs for destructive actions
 */
function initializeConfirmDialogs() {
  const confirmButtons = document.querySelectorAll('[data-confirm]');

  confirmButtons.forEach(button => {
    button.addEventListener('click', function(e) {
      const message = this.dataset.confirm || 'Are you sure you want to proceed?';

      if (!confirm(message)) {
        e.preventDefault();
        return false;
      }
    });
  });
}

/**
 * Auto-dismiss alerts after 5 seconds
 */
function initializeAlerts() {
  const alerts = document.querySelectorAll('.alert:not(.alert-permanent)');

  alerts.forEach(alert => {
    setTimeout(() => {
      const bsAlert = new bootstrap.Alert(alert);
      bsAlert.close();
    }, 5000);
  });
}

/**
 * Initialize search filters with debouncing
 */
function initializeSearchFilters() {
  const searchInputs = document.querySelectorAll('.search-filter');

  searchInputs.forEach(input => {
    let timeout;

    input.addEventListener('input', function() {
      clearTimeout(timeout);

      timeout = setTimeout(() => {
        const searchTerm = this.value.toLowerCase();
        const targetSelector = this.dataset.target;
        const targets = document.querySelectorAll(targetSelector);

        targets.forEach(target => {
          const text = target.textContent.toLowerCase();
          target.style.display = text.includes(searchTerm) ? '' : 'none';
        });
      }, 300);
    });
  });
}

/**
 * Initialize date inputs with constraints
 */
function initializeDateInputs() {
  const dateInputs = document.querySelectorAll('input[type="date"]');

  dateInputs.forEach(input => {
    // Set min date to today for future dates
    if (input.classList.contains('future-date')) {
      const today = new Date().toISOString().split('T')[0];
      input.min = today;
    }

    // Set max date to today for past dates
    if (input.classList.contains('past-date')) {
      const today = new Date().toISOString().split('T')[0];
      input.max = today;
    }
  });
}

/**
 * Add loading states to buttons and forms
 */
function addLoadingStates() {
  const forms = document.querySelectorAll('form');

  forms.forEach(form => {
    form.addEventListener('submit', function(e) {
      const submitButton = this.querySelector('button[type="submit"]');

      if (submitButton && !submitButton.disabled) {
        const originalText = submitButton.innerHTML;

        submitButton.disabled = true;
        submitButton.innerHTML = `
          <span class="spinner-border spinner-border-sm me-2" role="status" aria-hidden="true"></span>
          Processing...
        `;

        // Re-enable after 30 seconds as fallback
        setTimeout(() => {
          submitButton.disabled = false;
          submitButton.innerHTML = originalText;
        }, 30000);
      }
    });
  });
}

/**
 * Utility: Show toast notification
 */
function showToast(message, type = 'info') {
  const toastContainer = getOrCreateToastContainer();

  const toastId = 'toast-' + Date.now();
  const iconMap = {
    success: 'bi-check-circle-fill',
    error: 'bi-exclamation-circle-fill',
    warning: 'bi-exclamation-triangle-fill',
    info: 'bi-info-circle-fill'
  };

  const toast = document.createElement('div');
  toast.id = toastId;
  toast.className = `toast align-items-center text-white bg-${type === 'error' ? 'danger' : type} border-0`;
  toast.setAttribute('role', 'alert');
  toast.setAttribute('aria-live', 'assertive');
  toast.setAttribute('aria-atomic', 'true');

  toast.innerHTML = `
    <div class="d-flex">
      <div class="toast-body">
        <i class="bi ${iconMap[type]} me-2"></i>
        ${message}
      </div>
      <button type="button" class="btn-close btn-close-white me-2 m-auto" data-bs-dismiss="toast" aria-label="Close"></button>
    </div>
  `;

  toastContainer.appendChild(toast);

  const bsToast = new bootstrap.Toast(toast, {
    autohide: true,
    delay: 5000
  });

  bsToast.show();

  toast.addEventListener('hidden.bs.toast', () => {
    toast.remove();
  });
}

/**
 * Get or create toast container
 */
function getOrCreateToastContainer() {
  let container = document.getElementById('toast-container');

  if (!container) {
    container = document.createElement('div');
    container.id = 'toast-container';
    container.className = 'toast-container position-fixed top-0 end-0 p-3';
    container.style.zIndex = '1090';
    document.body.appendChild(container);
  }

  return container;
}

/**
 * Utility: Format date to readable format
 */
function formatDate(dateString) {
  const date = new Date(dateString);
  const options = { year: 'numeric', month: 'long', day: 'numeric' };
  return date.toLocaleDateString('en-US', options);
}

/**
 * Utility: Format time to readable format
 */
function formatTime(timeString) {
  const [hours, minutes] = timeString.split(':');
  const hour = parseInt(hours);
  const ampm = hour >= 12 ? 'PM' : 'AM';
  const displayHour = hour % 12 || 12;
  return `${displayHour}:${minutes} ${ampm}`;
}

/**
 * Utility: Debounce function
 */
function debounce(func, wait) {
  let timeout;
  return function executedFunction(...args) {
    const later = () => {
      clearTimeout(timeout);
      func(...args);
    };
    clearTimeout(timeout);
    timeout = setTimeout(later, wait);
  };
}

/**
 * Utility: Check if element is in viewport
 */
function isInViewport(element) {
  const rect = element.getBoundingClientRect();
  return (
    rect.top >= 0 &&
    rect.left >= 0 &&
    rect.bottom <= (window.innerHeight || document.documentElement.clientHeight) &&
    rect.right <= (window.innerWidth || document.documentElement.clientWidth)
  );
}

/**
 * Animate stat cards on scroll
 */
function animateStatsOnScroll() {
  const statCards = document.querySelectorAll('.stat-card-value');

  const observer = new IntersectionObserver((entries) => {
    entries.forEach(entry => {
      if (entry.isIntersecting && !entry.target.classList.contains('animated')) {
        animateNumber(entry.target);
        entry.target.classList.add('animated');
      }
    });
  });

  statCards.forEach(card => observer.observe(card));
}

/**
 * Animate number counting
 */
function animateNumber(element) {
  const target = parseInt(element.textContent);
  const duration = 1000;
  const steps = 20;
  const increment = target / steps;
  let current = 0;

  const timer = setInterval(() => {
    current += increment;
    if (current >= target) {
      element.textContent = target;
      clearInterval(timer);
    } else {
      element.textContent = Math.floor(current);
    }
  }, duration / steps);
}

/**
 * Export table data to CSV
 */
function exportTableToCSV(tableId, filename = 'export.csv') {
  const table = document.getElementById(tableId);
  if (!table) return;

  let csv = [];
  const rows = table.querySelectorAll('tr');

  rows.forEach(row => {
    const cols = row.querySelectorAll('td, th');
    const rowData = [];

    cols.forEach(col => {
      // Skip action columns
      if (!col.textContent.toLowerCase().includes('action')) {
        rowData.push('"' + col.textContent.trim().replace(/"/g, '""') + '"');
      }
    });

    if (rowData.length > 0) {
      csv.push(rowData.join(','));
    }
  });

  downloadCSV(csv.join('\n'), filename);
}

/**
 * Download CSV file
 */
function downloadCSV(csv, filename) {
  const blob = new Blob([csv], { type: 'text/csv' });
  const link = document.createElement('a');
  link.href = window.URL.createObjectURL(blob);
  link.download = filename;
  link.click();
}

/**
 * Validate appointment time
 */
function validateAppointmentTime(dateInput, timeInput) {
  const selectedDate = new Date(dateInput.value);
  const today = new Date();
  today.setHours(0, 0, 0, 0);

  if (selectedDate < today) {
    showToast('Cannot book appointments for past dates', 'error');
    return false;
  }

  if (selectedDate.toDateString() === today.toDateString()) {
    const [hours, minutes] = timeInput.value.split(':');
    const selectedTime = new Date();
    selectedTime.setHours(parseInt(hours), parseInt(minutes), 0, 0);

    if (selectedTime <= new Date()) {
      showToast('Cannot book appointments for past times', 'error');
      return false;
    }
  }

  return true;
}

/**
 * Password strength checker
 */
function checkPasswordStrength(password) {
  let strength = 0;

  if (password.length >= 8) strength++;
  if (password.match(/[a-z]/)) strength++;
  if (password.match(/[A-Z]/)) strength++;
  if (password.match(/[0-9]/)) strength++;
  if (password.match(/[^a-zA-Z0-9]/)) strength++;

  const strengthText = ['Very Weak', 'Weak', 'Fair', 'Good', 'Strong'];
  const strengthColor = ['danger', 'warning', 'info', 'primary', 'success'];

  return {
    score: strength,
    text: strengthText[strength - 1] || 'Very Weak',
    color: strengthColor[strength - 1] || 'danger'
  };
}

/**
 * Add password strength indicator
 */
function addPasswordStrengthIndicator(passwordInput) {
  const container = document.createElement('div');
  container.className = 'password-strength mt-2';
  container.innerHTML = `
    <div class="progress" style="height: 5px;">
      <div class="progress-bar" role="progressbar" style="width: 0%"></div>
    </div>
    <small class="form-text"></small>
  `;

  passwordInput.parentNode.appendChild(container);

  passwordInput.addEventListener('input', function() {
    const strength = checkPasswordStrength(this.value);
    const progressBar = container.querySelector('.progress-bar');
    const text = container.querySelector('.form-text');

    progressBar.style.width = (strength.score * 20) + '%';
    progressBar.className = `progress-bar bg-${strength.color}`;
    text.textContent = `Password Strength: ${strength.text}`;
    text.className = `form-text text-${strength.color}`;
  });
}

/**
 * Initialize on load
 */
if (document.readyState === 'loading') {
  document.addEventListener('DOMContentLoaded', animateStatsOnScroll);
} else {
  animateStatsOnScroll();
}

// Make utility functions available globally
window.HMS = {
  showToast,
  formatDate,
  formatTime,
  exportTableToCSV,
  validateAppointmentTime,
  checkPasswordStrength
};

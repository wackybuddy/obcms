/**
 * Mini Calendar Date Picker
 * Lightweight vanilla JavaScript date picker for form inputs
 * Features: Date selection, month navigation, keyboard support, WCAG 2.1 AA accessibility
 */

(function() {
    'use strict';

    class MiniDatePicker {
        constructor(inputElement, options = {}) {
            this.inputEl = inputElement;
            this.options = {
                format: 'YYYY-MM-DD',
                minDate: null,
                maxDate: null,
                disabledDates: [],
                ...options
            };

            this.calendar = null;
            this.currentDate = new Date();
            this.selectedDate = this.parseInputDate(this.inputEl.value);
            if (this.selectedDate) {
                this.currentDate = new Date(this.selectedDate);
            }

            this.init();
        }

        init() {
            // Add data attribute to mark as enhanced
            this.inputEl.setAttribute('data-mini-picker', 'true');

            // Wrap input in container
            const wrapper = document.createElement('div');
            wrapper.className = 'mini-date-picker-wrapper relative inline-block w-full';
            this.inputEl.parentNode.insertBefore(wrapper, this.inputEl);
            wrapper.appendChild(this.inputEl);

            // Add calendar icon button
            const iconBtn = document.createElement('button');
            iconBtn.type = 'button';
            iconBtn.className = 'absolute right-3 top-1/2 -translate-y-1/2 text-gray-400 hover:text-gray-600 transition-colors';
            iconBtn.innerHTML = '<i class="fas fa-calendar"></i>';
            iconBtn.setAttribute('tabindex', '-1');
            iconBtn.setAttribute('aria-label', 'Open date picker');
            wrapper.appendChild(iconBtn);

            // Event listeners
            this.inputEl.addEventListener('focus', () => this.show());
            this.inputEl.addEventListener('input', () => this.handleInput());
            iconBtn.addEventListener('click', (e) => {
                e.preventDefault();
                this.show();
            });

            // Close on Escape key
            document.addEventListener('keydown', (e) => {
                if (e.key === 'Escape' && this.calendar && this.calendar.classList.contains('block')) {
                    this.hide();
                }
            });

            // Close when clicking outside
            document.addEventListener('click', (e) => {
                if (this.calendar &&
                    !this.calendar.contains(e.target) &&
                    !this.inputEl.contains(e.target) &&
                    this.calendar.classList.contains('block')) {
                    this.hide();
                }
            });
        }

        parseInputDate(value) {
            if (!value) return null;
            const parts = value.split('-');
            if (parts.length === 3) {
                const date = new Date(parts[0], parts[1] - 1, parts[2]);
                if (!isNaN(date.getTime())) {
                    return date;
                }
            }
            return null;
        }

        formatDate(date) {
            const year = date.getFullYear();
            const month = String(date.getMonth() + 1).padStart(2, '0');
            const day = String(date.getDate()).padStart(2, '0');
            return `${year}-${month}-${day}`;
        }

        handleInput() {
            const parsed = this.parseInputDate(this.inputEl.value);
            if (parsed) {
                this.selectedDate = parsed;
                this.currentDate = new Date(parsed);
                this.render();
            }
        }

        show() {
            if (!this.calendar) {
                this.createCalendar();
            }
            this.render();
            this.calendar.classList.remove('hidden');
            this.calendar.classList.add('block');

            // Set focus to first focusable element (close button or date)
            const firstFocusable = this.calendar.querySelector('button');
            if (firstFocusable) {
                firstFocusable.focus();
            }
        }

        hide() {
            if (this.calendar) {
                this.calendar.classList.add('hidden');
                this.calendar.classList.remove('block');
                this.inputEl.focus();
            }
        }

        createCalendar() {
            this.calendar = document.createElement('div');
            this.calendar.className = 'mini-calendar absolute top-full left-0 mt-2 z-50 bg-white rounded-xl border border-gray-200 shadow-lg p-4 w-80 hidden';
            this.calendar.setAttribute('role', 'dialog');
            this.calendar.setAttribute('aria-label', 'Date picker calendar');

            // Header with navigation
            const header = document.createElement('div');
            header.className = 'flex items-center justify-between mb-4';

            const prevBtn = document.createElement('button');
            prevBtn.type = 'button';
            prevBtn.className = 'p-2 hover:bg-gray-100 rounded-lg transition-colors';
            prevBtn.innerHTML = '<i class="fas fa-chevron-left text-gray-600"></i>';
            prevBtn.setAttribute('aria-label', 'Previous month');
            prevBtn.addEventListener('click', (e) => {
                e.preventDefault();
                this.previousMonth();
            });

            const monthYear = document.createElement('div');
            monthYear.className = 'text-center font-semibold text-gray-900';
            monthYear.setAttribute('data-month-year', '');

            const nextBtn = document.createElement('button');
            nextBtn.type = 'button';
            nextBtn.className = 'p-2 hover:bg-gray-100 rounded-lg transition-colors';
            nextBtn.innerHTML = '<i class="fas fa-chevron-right text-gray-600"></i>';
            nextBtn.setAttribute('aria-label', 'Next month');
            nextBtn.addEventListener('click', (e) => {
                e.preventDefault();
                this.nextMonth();
            });

            header.appendChild(prevBtn);
            header.appendChild(monthYear);
            header.appendChild(nextBtn);
            this.calendar.appendChild(header);

            // Weekday headers
            const weekdayHeader = document.createElement('div');
            weekdayHeader.className = 'grid grid-cols-7 gap-1 mb-2';
            const weekdays = ['Sun', 'Mon', 'Tue', 'Wed', 'Thu', 'Fri', 'Sat'];
            weekdays.forEach(day => {
                const dayEl = document.createElement('div');
                dayEl.className = 'text-center text-xs font-semibold text-gray-500 py-2';
                dayEl.textContent = day;
                weekdayHeader.appendChild(dayEl);
            });
            this.calendar.appendChild(weekdayHeader);

            // Calendar grid
            const grid = document.createElement('div');
            grid.className = 'grid grid-cols-7 gap-1 mb-4';
            grid.setAttribute('data-calendar-grid', '');
            this.calendar.appendChild(grid);

            // Footer with today button
            const footer = document.createElement('div');
            footer.className = 'flex gap-2';
            const todayBtn = document.createElement('button');
            todayBtn.type = 'button';
            todayBtn.className = 'flex-1 py-2 px-3 text-sm font-medium text-blue-600 hover:bg-blue-50 rounded-lg transition-colors border border-blue-200';
            todayBtn.textContent = 'Today';
            todayBtn.addEventListener('click', (e) => {
                e.preventDefault();
                this.selectDate(new Date());
                this.hide();
            });

            const closeBtn = document.createElement('button');
            closeBtn.type = 'button';
            closeBtn.className = 'flex-1 py-2 px-3 text-sm font-medium text-gray-600 hover:bg-gray-100 rounded-lg transition-colors border border-gray-200';
            closeBtn.textContent = 'Close';
            closeBtn.addEventListener('click', (e) => {
                e.preventDefault();
                this.hide();
            });

            footer.appendChild(todayBtn);
            footer.appendChild(closeBtn);
            this.calendar.appendChild(footer);

            this.inputEl.parentNode.appendChild(this.calendar);
        }

        render() {
            const monthYear = this.calendar.querySelector('[data-month-year]');
            const monthNames = ['January', 'February', 'March', 'April', 'May', 'June',
                'July', 'August', 'September', 'October', 'November', 'December'];
            monthYear.textContent = `${monthNames[this.currentDate.getMonth()]} ${this.currentDate.getFullYear()}`;

            const grid = this.calendar.querySelector('[data-calendar-grid]');
            grid.innerHTML = '';

            const year = this.currentDate.getFullYear();
            const month = this.currentDate.getMonth();
            const firstDay = new Date(year, month, 1);
            const lastDay = new Date(year, month + 1, 0);
            const startDate = new Date(firstDay);
            startDate.setDate(startDate.getDate() - firstDay.getDay());

            const today = new Date();
            today.setHours(0, 0, 0, 0);

            // Generate 42 days (6 weeks) grid
            for (let i = 0; i < 42; i++) {
                const date = new Date(startDate);
                date.setDate(date.getDate() + i);

                const dayEl = document.createElement('button');
                dayEl.type = 'button';
                dayEl.className = 'aspect-square p-1 text-sm font-medium rounded-lg transition-all';
                dayEl.textContent = date.getDate();
                dayEl.setAttribute('tabindex', date.getMonth() === month ? '0' : '-1');

                const isCurrentMonth = date.getMonth() === month;
                const isToday = date.getTime() === today.getTime();
                const isSelected = this.selectedDate &&
                    date.toDateString() === this.selectedDate.toDateString();

                if (!isCurrentMonth) {
                    dayEl.className += ' text-gray-300 bg-transparent cursor-default';
                    dayEl.disabled = true;
                } else if (isSelected) {
                    dayEl.className += ' bg-gradient-to-r from-blue-600 to-emerald-600 text-white hover:shadow-md';
                    dayEl.setAttribute('aria-label', `${date.toDateString()}, selected`);
                } else if (isToday) {
                    dayEl.className += ' border-2 border-blue-500 text-blue-600 hover:bg-blue-50 cursor-pointer';
                    dayEl.setAttribute('aria-label', `${date.toDateString()}, today`);
                } else {
                    dayEl.className += ' bg-white hover:bg-gray-100 text-gray-900 cursor-pointer border border-transparent';
                    dayEl.setAttribute('aria-label', date.toDateString());
                }

                dayEl.addEventListener('click', (e) => {
                    if (!dayEl.disabled) {
                        e.preventDefault();
                        this.selectDate(new Date(date));
                        this.hide();
                    }
                });

                // Keyboard navigation
                dayEl.addEventListener('keydown', (e) => {
                    if (e.key === 'Enter' || e.key === ' ') {
                        e.preventDefault();
                        this.selectDate(new Date(date));
                        this.hide();
                    } else if (e.key === 'ArrowLeft') {
                        e.preventDefault();
                        this.focusPreviousDay();
                    } else if (e.key === 'ArrowRight') {
                        e.preventDefault();
                        this.focusNextDay();
                    } else if (e.key === 'ArrowUp') {
                        e.preventDefault();
                        this.focusPreviousWeek();
                    } else if (e.key === 'ArrowDown') {
                        e.preventDefault();
                        this.focusNextWeek();
                    }
                });

                grid.appendChild(dayEl);
            }
        }

        previousMonth() {
            this.currentDate.setMonth(this.currentDate.getMonth() - 1);
            this.render();
        }

        nextMonth() {
            this.currentDate.setMonth(this.currentDate.getMonth() + 1);
            this.render();
        }

        selectDate(date) {
            this.selectedDate = date;
            this.currentDate = new Date(date);
            this.inputEl.value = this.formatDate(date);

            // Trigger change event for form validation
            this.inputEl.dispatchEvent(new Event('change', { bubbles: true }));
            this.inputEl.dispatchEvent(new Event('input', { bubbles: true }));
        }

        focusPreviousDay() {
            const buttons = Array.from(this.calendar.querySelectorAll('[data-calendar-grid] button'));
            const focused = document.activeElement;
            const idx = buttons.indexOf(focused);
            if (idx > 0) {
                const prevBtn = buttons[idx - 1];
                if (prevBtn.tabIndex >= 0) {
                    prevBtn.focus();
                }
            }
        }

        focusNextDay() {
            const buttons = Array.from(this.calendar.querySelectorAll('[data-calendar-grid] button'));
            const focused = document.activeElement;
            const idx = buttons.indexOf(focused);
            if (idx < buttons.length - 1) {
                const nextBtn = buttons[idx + 1];
                if (nextBtn.tabIndex >= 0) {
                    nextBtn.focus();
                }
            }
        }

        focusPreviousWeek() {
            const buttons = Array.from(this.calendar.querySelectorAll('[data-calendar-grid] button'));
            const focused = document.activeElement;
            const idx = buttons.indexOf(focused);
            if (idx >= 7) {
                const prevWeekBtn = buttons[idx - 7];
                if (prevWeekBtn.tabIndex >= 0) {
                    prevWeekBtn.focus();
                }
            }
        }

        focusNextWeek() {
            const buttons = Array.from(this.calendar.querySelectorAll('[data-calendar-grid] button'));
            const focused = document.activeElement;
            const idx = buttons.indexOf(focused);
            if (idx < buttons.length - 7) {
                const nextWeekBtn = buttons[idx + 7];
                if (nextWeekBtn.tabIndex >= 0) {
                    nextWeekBtn.focus();
                }
            }
        }
    }

    // Auto-initialize date pickers on page load and HTMX swap
    function initializeDatePickers() {
        const dateInputs = document.querySelectorAll('input[type="date"][data-mini-picker-enabled]');
        dateInputs.forEach(input => {
            if (!input.getAttribute('data-mini-picker')) {
                new MiniDatePicker(input);
            }
        });
    }

    // Initialize on page load
    if (document.readyState === 'loading') {
        document.addEventListener('DOMContentLoaded', initializeDatePickers);
    } else {
        initializeDatePickers();
    }

    // Re-initialize on HTMX swap
    document.addEventListener('htmx:afterSwap', () => {
        initializeDatePickers();
    });

    // Expose global reference for manual initialization
    window.MiniDatePicker = MiniDatePicker;
    window.initializeDatePickers = initializeDatePickers;

})();

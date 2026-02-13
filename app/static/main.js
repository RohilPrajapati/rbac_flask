// validation utils
setTimeout(() => {
    const flashContainer = document.getElementById('flash-container');
    if (flashContainer) {
        flashContainer.classList.add('opacity-0', 'transition', 'duration-500');
        setTimeout(() => flashContainer.remove(), 500);
    }
}, 4000);

function showError(fieldId, message) {
    const errorEl = document.getElementById('error_' + fieldId);
    errorEl.innerText = message;
    errorEl.classList.remove('hidden');
}

function clearErrors() {
    document.querySelectorAll('.text-red-500').forEach(el => {
        el.innerText = '';
        el.classList.add('hidden');
    });
}

function validateField(field, rules) {
    const value = field.value.trim();
    const id = field.id;

    if (rules.required && value === '') {
        showError(id, 'This field cannot be empty');
        return false;
    }

    if (rules.minLength && value.length < rules.minLength) {
        showError(id, `Must be at least ${rules.minLength} characters`);
        return false;
    }

    if (rules.maxLength && value.length > rules.maxLength) {
        showError(id, `Must be at most ${rules.maxLength} characters`);
        return false;
    }

    if (rules.type === 'email') {
        const emailPattern = /^[^@]+@[^@]+\.[^@]+$/;
        if (!emailPattern.test(value)) {
            showError(id, 'Invalid email address');
            return false;
        }
    }

    if (rules.type === 'date') {
        const dateValue = new Date(value);
        if (isNaN(dateValue.getTime())) {
            showError(id, 'Invalid date');
            return false;
        }

        // Min date
        if (rules.minDate) {
            const minDate = new Date(rules.minDate);
            if (dateValue < minDate) {
                showError(id, `Date cannot be earlier than ${rules.minDate}`);
                return false;
            }
        }

        if (rules.maxDate) {
            const maxDate = new Date(rules.maxDate);
            if (dateValue > maxDate) {
                showError(id, `Date cannot be later than ${rules.maxDate}`);
                return false;
            }
        }
    }

    return true;
}
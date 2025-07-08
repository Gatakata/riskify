// Main JavaScript for Fraud Detection System

document.addEventListener('DOMContentLoaded', function() {
    // Form validation and enhancement
    initializeFormValidation();
    
    // Add loading states
    initializeLoadingStates();
    
    // Add tooltips and help text
    initializeHelpSystem();
    
    // Add real-time form feedback
    initializeRealTimeFeedback();
});

/**
 * Initialize form validation with custom styling
 */
function initializeFormValidation() {
    const form = document.getElementById('transaction-form');
    if (!form) return;
    
    // Add Bootstrap validation classes
    form.addEventListener('submit', function(event) {
        if (!form.checkValidity()) {
            event.preventDefault();
            event.stopPropagation();
        } else {
            // Show loading state
            showLoadingState();
        }
        form.classList.add('was-validated');
    });
    
    // Custom validation for specific fields
    const amountField = document.getElementById('transaction_amount');
    if (amountField) {
        amountField.addEventListener('input', function() {
            validateTransactionAmount(this);
        });
    }
    
    // Merchant category change handler
    const merchantField = document.getElementById('merchant_category');
    if (merchantField) {
        merchantField.addEventListener('change', function() {
            updateMerchantRiskGuidance(this.value);
        });
    }
    
    // Time validation
    const hourField = document.getElementById('transaction_hour');
    if (hourField) {
        hourField.addEventListener('input', function() {
            validateHour(this);
        });
    }
    
    // Risk score validation
    const riskFields = ['merchant_risk_score', 'location_risk_score', 'device_risk_score'];
    riskFields.forEach(fieldId => {
        const field = document.getElementById(fieldId);
        if (field) {
            field.addEventListener('input', function() {
                validateRiskScore(this);
            });
        }
    });
}

/**
 * Validate transaction amount
 */
function validateTransactionAmount(field) {
    const value = parseFloat(field.value);
    const errorDiv = field.parentNode.querySelector('.invalid-feedback');
    
    if (isNaN(value) || value <= 0) {
        field.classList.add('is-invalid');
        if (errorDiv) {
            errorDiv.textContent = 'Please enter a valid amount greater than $0.00';
        }
    } else if (value > 100000) {
        field.classList.add('is-invalid');
        if (errorDiv) {
            errorDiv.textContent = 'Maximum transaction amount is $100,000';
        }
    } else {
        field.classList.remove('is-invalid');
        field.classList.add('is-valid');
        
        // Add visual feedback for high amounts
        if (value > 5000) {
            showWarningTooltip(field, 'High amount transactions have increased fraud risk');
        }
    }
}

/**
 * Validate hour input
 */
function validateHour(field) {
    const value = parseInt(field.value);
    
    if (isNaN(value) || value < 0 || value > 23) {
        field.classList.add('is-invalid');
    } else {
        field.classList.remove('is-invalid');
        field.classList.add('is-valid');
        
        // Add guidance for unusual hours
        if (value < 6 || value > 22) {
            showWarningTooltip(field, 'Transactions at unusual hours may have higher risk');
        }
    }
}

/**
 * Validate risk score fields (0.0 - 1.0)
 */
function validateRiskScore(field) {
    const value = parseFloat(field.value);
    
    if (isNaN(value) || value < 0 || value > 1) {
        field.classList.add('is-invalid');
    } else {
        field.classList.remove('is-invalid');
        field.classList.add('is-valid');
        
        // Visual feedback for high risk scores
        if (value > 0.7) {
            showWarningTooltip(field, 'High risk score detected');
        }
    }
}

/**
 * Update merchant risk guidance based on category
 */
function updateMerchantRiskGuidance(category) {
    const highRiskCategories = ['online', 'atm', 'entertainment'];
    const merchantRiskField = document.getElementById('merchant_risk_score');
    
    if (merchantRiskField && highRiskCategories.includes(category)) {
        showInfoTooltip(merchantRiskField, 'This merchant category typically has higher fraud risk');
    }
}

/**
 * Show warning tooltip
 */
function showWarningTooltip(element, message) {
    // Remove existing tooltips
    const existingTooltip = element.parentNode.querySelector('.warning-tooltip');
    if (existingTooltip) {
        existingTooltip.remove();
    }
    
    // Create tooltip
    const tooltip = document.createElement('div');
    tooltip.className = 'warning-tooltip alert alert-warning py-1 px-2 mt-1';
    tooltip.innerHTML = `<i class="fas fa-exclamation-triangle me-1"></i><small>${message}</small>`;
    tooltip.style.fontSize = '0.75rem';
    
    element.parentNode.appendChild(tooltip);
    
    // Remove tooltip after 5 seconds
    setTimeout(() => {
        if (tooltip.parentNode) {
            tooltip.remove();
        }
    }, 5000);
}

/**
 * Show info tooltip
 */
function showInfoTooltip(element, message) {
    // Remove existing tooltips
    const existingTooltip = element.parentNode.querySelector('.info-tooltip');
    if (existingTooltip) {
        existingTooltip.remove();
    }
    
    // Create tooltip
    const tooltip = document.createElement('div');
    tooltip.className = 'info-tooltip alert alert-info py-1 px-2 mt-1';
    tooltip.innerHTML = `<i class="fas fa-info-circle me-1"></i><small>${message}</small>`;
    tooltip.style.fontSize = '0.75rem';
    
    element.parentNode.appendChild(tooltip);
    
    // Remove tooltip after 3 seconds
    setTimeout(() => {
        if (tooltip.parentNode) {
            tooltip.remove();
        }
    }, 3000);
}

/**
 * Initialize loading states
 */
function initializeLoadingStates() {
    const submitButton = document.querySelector('input[type="submit"], button[type="submit"]');
    if (!submitButton) return;
    
    // Store original button text
    const originalText = submitButton.textContent || submitButton.value;
    
    window.showLoadingState = function() {
        submitButton.disabled = true;
        submitButton.innerHTML = '<i class="fas fa-spinner fa-spin me-2"></i>Analyzing...';
        submitButton.classList.add('loading');
    };
    
    window.hideLoadingState = function() {
        submitButton.disabled = false;
        submitButton.textContent = originalText;
        submitButton.classList.remove('loading');
    };
}

/**
 * Initialize help system
 */
function initializeHelpSystem() {
    // Add help icons to complex fields
    const helpFields = [
        {
            id: 'merchant_risk_score',
            text: 'Merchant risk score based on historical fraud patterns (0.0 = very safe, 1.0 = very risky)'
        },
        {
            id: 'location_risk_score',
            text: 'Geographic risk score based on transaction location (0.0 = very safe, 1.0 = very risky)'
        },
        {
            id: 'device_risk_score',
            text: 'Device risk score based on device fingerprinting (0.0 = very safe, 1.0 = very risky)'
        },
        {
            id: 'transaction_frequency_24h',
            text: 'Number of transactions from this account in the last 24 hours'
        }
    ];
    
    helpFields.forEach(field => {
        const element = document.getElementById(field.id);
        if (element) {
            addHelpIcon(element, field.text);
        }
    });
}

/**
 * Add help icon to field
 */
function addHelpIcon(field, helpText) {
    const label = field.parentNode.querySelector('label');
    if (!label) return;
    
    const helpIcon = document.createElement('i');
    helpIcon.className = 'fas fa-question-circle text-muted ms-1';
    helpIcon.style.cursor = 'pointer';
    helpIcon.title = helpText;
    
    // Add Bootstrap tooltip
    helpIcon.setAttribute('data-bs-toggle', 'tooltip');
    helpIcon.setAttribute('data-bs-placement', 'top');
    helpIcon.setAttribute('title', helpText);
    
    label.appendChild(helpIcon);
    
    // Initialize Bootstrap tooltip
    if (typeof bootstrap !== 'undefined') {
        new bootstrap.Tooltip(helpIcon);
    }
}

/**
 * Initialize real-time feedback
 */
function initializeRealTimeFeedback() {
    const form = document.getElementById('transaction-form');
    if (!form) return;
    
    // Add input event listeners for real-time validation
    const inputs = form.querySelectorAll('input, select');
    inputs.forEach(input => {
        input.addEventListener('input', function() {
            // Remove validation classes for real-time feedback
            this.classList.remove('is-invalid', 'is-valid');
            
            // Add debounced validation
            clearTimeout(this.validationTimer);
            this.validationTimer = setTimeout(() => {
                validateField(this);
            }, 500);
        });
        
        input.addEventListener('blur', function() {
            validateField(this);
        });
    });
}

/**
 * Validate individual field
 */
function validateField(field) {
    if (field.checkValidity()) {
        field.classList.remove('is-invalid');
        field.classList.add('is-valid');
    } else {
        field.classList.remove('is-valid');
        field.classList.add('is-invalid');
    }
}

/**
 * Format currency inputs
 */
function formatCurrency(input) {
    let value = input.value.replace(/[^\d.]/g, '');
    const parts = value.split('.');
    
    if (parts.length > 2) {
        value = parts[0] + '.' + parts.slice(1).join('');
    }
    
    if (parts[1] && parts[1].length > 2) {
        value = parts[0] + '.' + parts[1].slice(0, 2);
    }
    
    input.value = value;
}

// Add currency formatting to amount fields
document.addEventListener('DOMContentLoaded', function() {
    const currencyFields = ['transaction_amount', 'avg_transaction_amount_30d'];
    currencyFields.forEach(fieldId => {
        const field = document.getElementById(fieldId);
        if (field) {
            field.addEventListener('input', function() {
                formatCurrency(this);
            });
        }
    });
});

// Keyboard shortcuts
document.addEventListener('keydown', function(event) {
    // Ctrl/Cmd + Enter to submit form
    if ((event.ctrlKey || event.metaKey) && event.key === 'Enter') {
        const form = document.getElementById('transaction-form');
        if (form) {
            form.submit();
        }
    }
});

// Add smooth scrolling for better UX
function smoothScrollTo(element) {
    element.scrollIntoView({
        behavior: 'smooth',
        block: 'center'
    });
}

// Error handling for network issues
window.addEventListener('offline', function() {
    const alert = document.createElement('div');
    alert.className = 'alert alert-warning alert-dismissible fade show position-fixed';
    alert.style.top = '20px';
    alert.style.right = '20px';
    alert.style.zIndex = '9999';
    alert.innerHTML = `
        <i class="fas fa-wifi me-2"></i>
        You are currently offline. Please check your internet connection.
        <button type="button" class="btn-close" data-bs-dismiss="alert"></button>
    `;
    document.body.appendChild(alert);
});

window.addEventListener('online', function() {
    const offlineAlerts = document.querySelectorAll('.alert-warning');
    offlineAlerts.forEach(alert => {
        if (alert.textContent.includes('offline')) {
            alert.remove();
        }
    });
});

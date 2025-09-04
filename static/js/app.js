// Senior-friendly JavaScript for dynamic scam checker form (v1.1)

let currentStep = 1;
const totalSteps = 5;

document.addEventListener('DOMContentLoaded', function() {
    console.log('Scam Checker app initialized');
    
    // Initialize dynamic form functionality
    initializeDynamicForm();
    
    // Initialize accessibility features
    initializeAccessibility();
    
    // Initialize form validation
    initializeFormValidation();
});

function initializeDynamicForm() {
    // Show only the first step initially
    showStep(1);
    
    // Handle step navigation
    setupStepNavigation();
    
    // Handle message type changes
    setupMessageTypeHandling();
    
    // Handle form submission
    setupFormSubmission();
}

function setupStepNavigation() {
    // Next buttons for each step
    document.getElementById('next-step-1')?.addEventListener('click', function() {
        if (validateStep(1)) {
            nextStep();
        }
    });
    
    document.getElementById('next-step-2')?.addEventListener('click', function() {
        if (validateStep(2)) {
            nextStep();
        }
    });
    
    document.getElementById('next-step-3')?.addEventListener('click', function() {
        if (validateStep(3)) {
            nextStep();
        }
    });
    
    document.getElementById('next-step-4')?.addEventListener('click', function() {
        if (validateStep(4)) {
            nextStep();
        }
    });
    
    // Back buttons for each step
    document.getElementById('back-step-2')?.addEventListener('click', function() {
        previousStep();
    });
    
    document.getElementById('back-step-3')?.addEventListener('click', function() {
        previousStep();
    });
    
    document.getElementById('back-step-4')?.addEventListener('click', function() {
        previousStep();
    });
    
    document.getElementById('back-step-5')?.addEventListener('click', function() {
        previousStep();
    });
}

function setupMessageTypeHandling() {
    const messageTypeInputs = document.querySelectorAll('input[name="message_type"]');
    
    messageTypeInputs.forEach(input => {
        input.addEventListener('change', function() {
            // Enable next button when message type is selected
            const nextButton = document.getElementById('next-step-1');
            if (nextButton) {
                nextButton.disabled = false;
            }
            
            // Store selected type for step 2 conditional questions
            document.getElementById('dynamic-form').setAttribute('data-message-type', this.value);
            
            announceToScreenReader(`Selected: ${this.nextElementSibling.textContent.trim()}`);
        });
    });
}

function setupFormSubmission() {
    const form = document.getElementById('dynamic-form');
    
    if (form) {
        form.addEventListener('submit', function(e) {
            if (!validateAllSteps()) {
                e.preventDefault();
                return false;
            }
            
            // Show loading state
            showLoadingState();
        });
    }
}

function showStep(stepNumber) {
    // Hide all steps
    for (let i = 1; i <= totalSteps; i++) {
        const step = document.getElementById(`step-${i}`);
        if (step) {
            step.style.display = 'none';
        }
    }
    
    // Show current step
    const currentStepElement = document.getElementById(`step-${stepNumber}`);
    if (currentStepElement) {
        currentStepElement.style.display = 'block';
        currentStepElement.scrollIntoView({ behavior: 'smooth', block: 'start' });
    }
    
    // Update progress bar
    updateProgressBar(stepNumber);
    
    // Handle conditional questions for step 2 and step 5
    if (stepNumber === 2) {
        showConditionalQuestions();
    } else if (stepNumber === 5) {
        showConditionalStep5Questions();
    }
    
    // Set current step
    currentStep = stepNumber;
}

function showConditionalQuestions() {
    const form = document.getElementById('dynamic-form');
    const messageType = form.getAttribute('data-message-type');
    
    // Hide all message type questions
    document.querySelectorAll('.message-type-questions').forEach(section => {
        section.style.display = 'none';
    });
    
    // Show relevant questions based on message type
    switch(messageType) {
        case 'phone_call':
            document.getElementById('phone-questions').style.display = 'block';
            break;
        case 'email':
            document.getElementById('email-questions').style.display = 'block';
            break;
        case 'text_message':
            document.getElementById('text-questions').style.display = 'block';
            break;
        case 'letter':
            document.getElementById('letter-questions').style.display = 'block';
            break;
    }
}

function showConditionalStep5Questions() {
    const form = document.getElementById('dynamic-form');
    const messageType = form.getAttribute('data-message-type');
    
    // Hide all conditional questions in step 5
    document.getElementById('links-question').style.display = 'none';
    document.getElementById('grammar-question').style.display = 'none';
    
    // Show relevant questions based on message type
    switch(messageType) {
        case 'email':
        case 'text_message':
            // Show links question for email and text
            document.getElementById('links-question').style.display = 'block';
            document.getElementById('grammar-question').style.display = 'block';
            break;
        case 'letter':
            // Show grammar question for letters (written communication)
            document.getElementById('grammar-question').style.display = 'block';
            break;
        case 'phone_call':
            // No additional questions for phone calls
            break;
    }
}

function nextStep() {
    if (currentStep < totalSteps) {
        showStep(currentStep + 1);
    }
}

function previousStep() {
    if (currentStep > 1) {
        showStep(currentStep - 1);
    }
}

function updateProgressBar(stepNumber) {
    const progressBar = document.querySelector('.progress-bar');
    const currentStepSpan = document.getElementById('current-step');
    const progressText = document.getElementById('progress-text');
    
    if (progressBar) {
        const progress = (stepNumber / totalSteps) * 100;
        progressBar.style.width = `${progress}%`;
        progressBar.setAttribute('aria-valuenow', stepNumber);
    }
    
    if (currentStepSpan) {
        currentStepSpan.textContent = stepNumber;
    }
    
    if (progressText) {
        const stepTexts = {
            1: 'Message Type',
            2: 'Message Details',
            3: 'Organization & Request',
            4: 'Financial Warning Signs',
            5: 'Pressure & Threats'
        };
        progressText.textContent = stepTexts[stepNumber] || 'Processing';
    }
}

function validateStep(stepNumber) {
    let isValid = true;
    const errors = [];
    
    // Declare all variables at the top to avoid scope issues
    let messageType, form, selectedMessageType, emailInput, phoneInput, mainRequest;
    let step4Fields, step4Missing, step5Fields, step5Missing;
    
    switch(stepNumber) {
        case 1:
            messageType = document.querySelector('input[name="message_type"]:checked');
            if (!messageType) {
                errors.push('Please select what type of message you received.');
                isValid = false;
            }
            break;
            
        case 2:
            // Validate email and phone inputs if they have values
            form = document.getElementById('dynamic-form');
            selectedMessageType = form.getAttribute('data-message-type');
            
            if (selectedMessageType === 'email') {
                emailInput = document.getElementById('email_address');
                if (emailInput && emailInput.value && !validateEmailInput(emailInput)) {
                    isValid = false;
                    errors.push('Please enter a valid email address.');
                }
            } else if (selectedMessageType === 'phone_call' || selectedMessageType === 'text_message') {
                phoneInput = selectedMessageType === 'phone_call' ? 
                    document.getElementById('phone_number') : 
                    document.getElementById('text_number');
                if (phoneInput && phoneInput.value && !validatePhoneInput(phoneInput)) {
                    isValid = false;
                    errors.push('Please enter a valid phone number.');
                }
            }
            break;
            
        case 3:
            mainRequest = document.getElementById('main_request');
            if (mainRequest && mainRequest.value.trim() === '') {
                errors.push('Please describe what the message asked you to do.');
                isValid = false;
                mainRequest.focus();
            }
            break;
            
        case 4:
            // Check that at least some radio buttons are selected
            step4Fields = ['asks_for_money', 'asks_for_personal_info', 'requests_immediate_payment'];
            step4Missing = step4Fields.filter(field => 
                !document.querySelector(`input[name="${field}"]:checked`)
            );
            
            if (step4Missing.length === step4Fields.length) {
                errors.push('Please answer the questions about financial requests.');
                isValid = false;
            }
            break;
            
        case 5:
            // Check that remaining questions are answered
            step5Fields = ['urgent_action_required', 'threatens_consequences', 'offers_unexpected_prize', 
                                'sender_unknown', 'poor_grammar_spelling', 'suspicious_links', 'requests_secrecy'];
            step5Missing = step5Fields.filter(field => 
                !document.querySelector(`input[name="${field}"]:checked`)
            );
            
            if (step5Missing.length > 3) { // Allow some questions to be unanswered
                errors.push('Please answer most of the warning sign questions.');
                isValid = false;
            }
            break;
    }
    
    if (!isValid) {
        showValidationErrors(errors);
    }
    
    return isValid;
}

function validateAllSteps() {
    // Final validation before submission
    const selectedType = document.querySelector('input[name="message_type"]:checked');
    const mainRequest = document.getElementById('main_request');
    
    const errors = [];
    
    if (!selectedType) {
        errors.push('Please select the message type.');
    }
    
    if (!mainRequest || mainRequest.value.trim() === '') {
        errors.push('Please describe what the message asked you to do.');
    }
    
    if (errors.length > 0) {
        showValidationErrors(errors);
        return false;
    }
    
    return true;
}

function showValidationErrors(errors) {
    // Remove existing error alerts
    const existingAlerts = document.querySelectorAll('.validation-error-alert');
    existingAlerts.forEach(alert => alert.remove());
    
    // Create new error alert
    const errorAlert = document.createElement('div');
    errorAlert.className = 'alert alert-danger validation-error-alert';
    errorAlert.setAttribute('role', 'alert');
    
    let errorHTML = '<h4 class="alert-heading"><i class="fas fa-exclamation-triangle me-2"></i>Please complete this step:</h4><ul class="mb-0">';
    errors.forEach(error => {
        errorHTML += `<li class="fs-5">${error}</li>`;
    });
    errorHTML += '</ul>';
    
    errorAlert.innerHTML = errorHTML;
    
    // Insert at the top of current step
    const currentStepElement = document.getElementById(`step-${currentStep}`);
    if (currentStepElement) {
        currentStepElement.insertBefore(errorAlert, currentStepElement.firstChild);
        errorAlert.scrollIntoView({ behavior: 'smooth', block: 'center' });
        
        // Announce to screen readers
        announceToScreenReader('Please complete the required fields for this step.');
    }
}

function showLoadingState() {
    const submitButton = document.getElementById('submit-form');
    const form = document.getElementById('dynamic-form');
    
    if (submitButton) {
        submitButton.disabled = true;
        submitButton.innerHTML = '<i class="fas fa-spinner fa-spin me-2"></i>Checking for scams...';
    }
    
    if (form) {
        form.classList.add('form-submitting');
    }
    
    // Show a friendly message
    showTemporaryMessage('Analyzing your message... This may take a moment.', 'info');
}

function initializeAccessibility() {
    // Add keyboard navigation helpers
    addKeyboardNavigationHelpers();
    
    // Ensure focus is visible
    addFocusHelpers();
    
    // Announce form changes to screen readers
    const radioButtons = document.querySelectorAll('input[type="radio"]');
    
    radioButtons.forEach(button => {
        button.addEventListener('change', function() {
            // Announce the selection
            announceToScreenReader(`Selected: ${this.nextElementSibling.textContent.trim()}`);
        });
    });
}

function initializeFormValidation() {
    // Add real-time input validation
    addInputValidation();
    console.log('Form validation initialized');
}

function addInputValidation() {
    // Email validation
    const emailInput = document.getElementById('email_address');
    if (emailInput) {
        emailInput.addEventListener('blur', function() {
            validateEmailInput(this);
        });
    }
    
    // Phone number validation
    const phoneInputs = document.querySelectorAll('input[type="tel"]');
    phoneInputs.forEach(input => {
        input.addEventListener('blur', function() {
            validatePhoneInput(this);
        });
    });
}

function validateEmailInput(input) {
    if (input.value && !isValidEmail(input.value)) {
        showInputError(input, 'Please enter a valid email address');
        return false;
    } else {
        clearInputError(input);
        return true;
    }
}

function validatePhoneInput(input) {
    if (input.value && !isValidPhone(input.value)) {
        showInputError(input, 'Please enter a valid phone number');
        return false;
    } else {
        clearInputError(input);
        return true;
    }
}

function isValidEmail(email) {
    const emailRegex = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;
    return emailRegex.test(email);
}

function isValidPhone(phone) {
    // Allow phone numbers, 'Unknown', 'Private', etc.
    const phoneRegex = /^[\d\s\-\+\(\)]+$|^(unknown|private|blocked|withheld)$/i;
    return phoneRegex.test(phone);
}

function showInputError(input, message) {
    clearInputError(input);
    input.classList.add('is-invalid');
    
    const errorDiv = document.createElement('div');
    errorDiv.className = 'invalid-feedback';
    errorDiv.textContent = message;
    
    input.parentNode.appendChild(errorDiv);
}

function clearInputError(input) {
    input.classList.remove('is-invalid');
    const existingError = input.parentNode.querySelector('.invalid-feedback');
    if (existingError) {
        existingError.remove();
    }
}

function addKeyboardNavigationHelpers() {
    // Add keyboard shortcuts for common actions
    document.addEventListener('keydown', function(e) {
        // Alt + H for home
        if (e.altKey && e.key.toLowerCase() === 'h') {
            e.preventDefault();
            const homeLink = document.querySelector('a[href*="index"]') || 
                           document.querySelector('a[href="/"]');
            if (homeLink) {
                homeLink.click();
            }
        }
        
        // Alt + N for next
        if (e.altKey && e.key.toLowerCase() === 'n') {
            e.preventDefault();
            const nextButton = document.getElementById(`next-step-${currentStep}`);
            if (nextButton && !nextButton.disabled) {
                nextButton.click();
            }
        }
        
        // Alt + B for back
        if (e.altKey && e.key.toLowerCase() === 'b') {
            e.preventDefault();
            const backButton = document.getElementById(`back-step-${currentStep}`);
            if (backButton) {
                backButton.click();
            }
        }
    });
    
    // Improve radio button navigation
    const radioGroups = {};
    document.querySelectorAll('input[type="radio"]').forEach(radio => {
        const groupName = radio.name;
        if (!radioGroups[groupName]) {
            radioGroups[groupName] = [];
        }
        radioGroups[groupName].push(radio);
    });
    
    // Add arrow key navigation within radio groups
    Object.values(radioGroups).forEach(group => {
        group.forEach((radio, index) => {
            radio.addEventListener('keydown', function(e) {
                if (e.key === 'ArrowDown' || e.key === 'ArrowRight') {
                    e.preventDefault();
                    const nextIndex = (index + 1) % group.length;
                    group[nextIndex].focus();
                    group[nextIndex].checked = true;
                    group[nextIndex].dispatchEvent(new Event('change'));
                } else if (e.key === 'ArrowUp' || e.key === 'ArrowLeft') {
                    e.preventDefault();
                    const prevIndex = (index - 1 + group.length) % group.length;
                    group[prevIndex].focus();
                    group[prevIndex].checked = true;
                    group[prevIndex].dispatchEvent(new Event('change'));
                }
            });
        });
    });
}

function addFocusHelpers() {
    // Ensure focus is always visible
    document.addEventListener('focusin', function(e) {
        if (e.target.matches('input, button, textarea, select, a')) {
            e.target.classList.add('keyboard-focused');
        }
    });
    
    document.addEventListener('focusout', function(e) {
        e.target.classList.remove('keyboard-focused');
    });
}

function announceToScreenReader(message) {
    // Create a live region for screen reader announcements
    let liveRegion = document.getElementById('sr-live-region');
    
    if (!liveRegion) {
        liveRegion = document.createElement('div');
        liveRegion.id = 'sr-live-region';
        liveRegion.setAttribute('aria-live', 'polite');
        liveRegion.setAttribute('aria-atomic', 'true');
        liveRegion.style.position = 'absolute';
        liveRegion.style.left = '-10000px';
        liveRegion.style.width = '1px';
        liveRegion.style.height = '1px';
        liveRegion.style.overflow = 'hidden';
        document.body.appendChild(liveRegion);
    }
    
    // Clear and set the message
    liveRegion.textContent = '';
    setTimeout(() => {
        liveRegion.textContent = message;
    }, 100);
}

function showTemporaryMessage(message, type = 'info') {
    const messageDiv = document.createElement('div');
    messageDiv.className = `alert alert-${type} temporary-message`;
    messageDiv.setAttribute('role', 'status');
    messageDiv.innerHTML = `<i class="fas fa-info-circle me-2"></i>${message}`;
    
    // Insert at the top of the page
    const mainContent = document.getElementById('main-content');
    if (mainContent) {
        mainContent.insertBefore(messageDiv, mainContent.firstChild);
        
        // Remove after 5 seconds
        setTimeout(() => {
            if (messageDiv.parentNode) {
                messageDiv.remove();
            }
        }, 5000);
    }
}

// Add print functionality for results
function printResults() {
    window.print();
}

// Add this to results page if needed
if (window.location.pathname.includes('results')) {
    document.addEventListener('DOMContentLoaded', function() {
        // Add print button if not already present
        const printButton = document.createElement('button');
        printButton.className = 'btn btn-outline-secondary btn-lg me-2';
        printButton.innerHTML = '<i class="fas fa-print me-2"></i>Print Results';
        printButton.onclick = printResults;
        
        const actionButtons = document.querySelector('.d-grid');
        if (actionButtons) {
            actionButtons.appendChild(printButton);
        }
    });
}

// Error handling for API calls
function handleAPIError(error) {
    console.error('API Error:', error);
    
    const errorMessage = 'We encountered a problem analyzing your message. ' +
                        'When in doubt, it\'s best to be cautious and verify ' +
                        'through official channels.';
    
    showTemporaryMessage(errorMessage, 'warning');
    announceToScreenReader(errorMessage);
}
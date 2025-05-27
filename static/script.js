let currentStep = 1;
let questionnaireDef = null;
let currentLang = 'en';
let uiTranslations = {}; // Store UI translations (buttons, titles)
let totalSteps = 5; // Default, will be updated

// --- 1. Global Variables (already defined above) ---

// --- 2. fetchQuestionnaireDef() ---
async function fetchQuestionnaireDef() {
    try {
        const response = await fetch('/static/questionnaire_structure.json');
        if (!response.ok) {
            throw new Error(`HTTP error! status: ${response.status} for questionnaire_structure.json`);
        }
        questionnaireDef = await response.json();
        if (questionnaireDef && questionnaireDef.totalSteps) {
            totalSteps = questionnaireDef.totalSteps;
        }
        console.log("Questionnaire definition loaded:", questionnaireDef);
        // Title updates will be handled in renderQuestionnaire or applyStaticTranslations
    } catch (error) {
        console.error('Error fetching or parsing questionnaire definition:', error);
        // Display a more user-friendly error on the page if critical
        const mainContainer = document.querySelector('.container');
        if (mainContainer) {
            mainContainer.innerHTML = '<p style="color:red; text-align:center;">Error loading questionnaire. Please try refreshing the page.</p>';
        }
    }
}

// --- 3. loadLanguage() ---
async function loadLanguage(lang) {
    currentLang = lang;
    localStorage.setItem('language', lang);
    const languageSelector = document.getElementById('languageSelector');
    if (languageSelector) {
        languageSelector.value = currentLang;
    }

    try {
        const response = await fetch(`/static/i18n/${currentLang}.json`);
        if (!response.ok) {
            throw new Error(`HTTP error! status: ${response.status} for ${currentLang}.json`);
        }
        const data = await response.json();
        uiTranslations[currentLang] = data; // Store all translations for the current language
        console.log(`Translations for ${currentLang} loaded:`, uiTranslations[currentLang]);
        
        if (questionnaireDef) { // Ensure questionnaireDef is loaded before rendering
             renderQuestionnaire();
        } else {
            // This case might happen if loadLanguage is called before fetchQuestionnaireDef completes
            // The IIFE ensures fetchQuestionnaireDef is called first, then loadLanguage, then render.
            console.warn("Questionnaire definition not yet loaded. Rendering might be incomplete or skipped.");
        }

    } catch (error) {
        console.error(`Error loading language ${currentLang}:`, error);
        if (currentLang !== 'en') {
            console.warn("Falling back to English language.");
            await loadLanguage('en');
        } else {
            const mainContainer = document.querySelector('.container');
            if (mainContainer) {
                mainContainer.innerHTML = '<p style="color:red; text-align:center;">Error loading essential language files. Please try refreshing the page.</p>';
            }
        }
    }
}

// Helper to apply translations to static UI elements
function applyStaticTranslations() {
    if (!uiTranslations[currentLang]) return;

    const langData = uiTranslations[currentLang];

    // Page title
    const pageTitleElement = document.querySelector('title');
    if (pageTitleElement && questionnaireDef && langData[questionnaireDef.questionnaireTitleKey]) {
        pageTitleElement.textContent = langData[questionnaireDef.questionnaireTitleKey];
    } else if (pageTitleElement && langData['main_title']) { // Fallback if questionnaireDef not loaded yet
        pageTitleElement.textContent = langData['main_title'];
    }


    // Main header H1
    const mainHeaderElement = document.querySelector('h1');
     if (mainHeaderElement && questionnaireDef && langData[questionnaireDef.questionnaireTitleKey]) {
        mainHeaderElement.textContent = langData[questionnaireDef.questionnaireTitleKey];
    } else if (mainHeaderElement && langData['main_title']) {
         mainHeaderElement.textContent = langData['main_title'];
     }


    // Step titles
    for (let i = 1; i <= totalSteps; i++) {
        const stepTitleElement = document.querySelector(`#step${i} h2[data-i18n-key="step${i}_title"]`);
        if (stepTitleElement && langData[`step${i}_title`]) {
            stepTitleElement.textContent = langData[`step${i}_title`];
        }
    }

    // Buttons (Next, Back, Submit)
    document.querySelectorAll('button[data-i18n-key]').forEach(button => {
        const key = button.getAttribute('data-i18n-key');
        if (langData[key]) {
            button.textContent = langData[key];
        }
    });
    
    // Language selector options (if they also use data-i18n-key, though typically their text is direct)
    document.querySelectorAll('#languageSelector option[data-i18n-key]').forEach(option => {
        const key = option.getAttribute('data-i18n-key');
        if(langData[key]) {
            option.textContent = langData[key];
        }
    });

    // Progress text (handled by showStep, but ensure keys are available)
    showStep(currentStep); 
}


// --- 4. renderQuestionnaire() ---
function renderQuestionnaire() {
    if (!questionnaireDef || !uiTranslations[currentLang]) {
        console.error('Questionnaire definition or UI translations not loaded. Cannot render.');
        return;
    }
    
    applyStaticTranslations(); // Apply translations to static parts of the UI

    // Clear previous questions from all step containers
    for (let i = 1; i <= totalSteps; i++) {
        const stepQuestionsContainer = document.getElementById(`step${i}_questions_container`);
        if (stepQuestionsContainer) {
            stepQuestionsContainer.innerHTML = '';
        }
    }

    questionnaireDef.questions.forEach(question => {
        const stepContainer = document.getElementById(`step${question.step}_questions_container`);
        if (!stepContainer) {
            console.warn(`Container for step ${question.step} not found.`);
            return;
        }

        const qText = question.questionText[currentLang] || question.questionText['en'];

        const questionWrapper = document.createElement('div');
        questionWrapper.className = 'form-group';

        const labelElement = document.createElement('label');
        // For radio/checkbox groups, the main label is for the group, not a specific input.
        // Individual option labels are handled in createInputElement.
        if (question.type !== 'radio' && question.type !== 'checkbox_group') {
            labelElement.htmlFor = `q_${question.id}`;
        }
        labelElement.textContent = qText;
        questionWrapper.appendChild(labelElement);

        const inputElement = createInputElement(question, currentLang);
        questionWrapper.appendChild(inputElement);

        stepContainer.appendChild(questionWrapper);
    });

    showStep(currentStep); // Refresh the display of the current step
}

// --- 5. createInputElement() ---
function createInputElement(question, langCode) {
    const qId = `q_${question.id}`;
    let groupElement; // Used for radio and checkbox_group

    switch (question.type) {
        case 'radio':
            groupElement = document.createElement('div');
            groupElement.id = qId; // The group can have the ID
            groupElement.classList.add('input-group-radio');
            question.answers.forEach((ansOpt, index) => {
                const optionId = `${qId}_${ansOpt.value.replace(/\s+/g, '_').replace(/[^a-zA-Z0-9_]/g, '') || index}`; // Sanitize value for ID or use index
                
                const radioInput = document.createElement('input');
                radioInput.type = 'radio';
                radioInput.id = optionId;
                radioInput.name = qId; // Group by question ID
                radioInput.value = ansOpt.value; // Use the English value as the submission value

                const radioLabel = document.createElement('label');
                radioLabel.htmlFor = optionId;
                radioLabel.textContent = ansOpt.text[langCode] || ansOpt.text['en'];
                
                const wrapper = document.createElement('div');
                wrapper.appendChild(radioInput);
                wrapper.appendChild(radioLabel);
                groupElement.appendChild(wrapper);
            });
            return groupElement;

        case 'checkbox_group':
            groupElement = document.createElement('div');
            groupElement.id = qId;
            groupElement.classList.add('input-group-checkbox');
            question.answers.forEach((ansOpt, index) => {
                const optionId = `${qId}_${ansOpt.value.replace(/\s+/g, '_').replace(/[^a-zA-Z0-9_]/g, '') || index}`;
                
                const checkboxInput = document.createElement('input');
                checkboxInput.type = 'checkbox';
                checkboxInput.id = optionId;
                checkboxInput.name = qId; // All checkboxes in a group share the same name for data collection
                checkboxInput.value = ansOpt.value;

                const checkboxLabel = document.createElement('label');
                checkboxLabel.htmlFor = optionId;
                checkboxLabel.textContent = ansOpt.text[langCode] || ansOpt.text['en'];

                const wrapper = document.createElement('div');
                wrapper.appendChild(checkboxInput);
                wrapper.appendChild(checkboxLabel);
                groupElement.appendChild(wrapper);
            });
            return groupElement;

        case 'freetext': // Corresponds to textarea
            const textarea = document.createElement('textarea');
            textarea.id = qId;
            textarea.name = qId;
            if (question.placeholderText) {
                textarea.placeholder = question.placeholderText[langCode] || question.placeholderText['en'];
            }
            return textarea;
        
        // Default case for simple text inputs if not explicitly 'freetext' but implies single line
        // Or handle other types like 'text', 'number', 'date', 'email' if they appear in JSON
        default: // Assuming 'text', 'number', 'date', 'email' etc.
            const defaultInput = document.createElement('input');
            defaultInput.type = question.type; // e.g. "text", "number"
            defaultInput.id = qId;
            defaultInput.name = qId;
            if (question.placeholderText) { // Using placeholderText for consistency from JSON
                defaultInput.placeholder = question.placeholderText[langCode] || question.placeholderText['en'];
            }
            return defaultInput;
    }
}

// --- 6. showStep() ---
function showStep(n) {
    if (questionnaireDef) { // Ensure questionnaireDef is loaded
        totalSteps = questionnaireDef.totalSteps;
    }

    document.querySelectorAll('.step').forEach((div, i) => {
        div.style.display = i === (n - 1) ? 'block' : 'none';
    });

    const progressTextElement = document.getElementById('progressText');
    const langData = uiTranslations[currentLang];
    if (progressTextElement && langData) {
        const stepText = langData['progress_step'] || "Step";
        const ofText = langData['progress_of'] || "of";
        progressTextElement.innerHTML = `<span data-i18n-key="progress_step">${stepText}</span> ${n} <span data-i18n-key="progress_of">${ofText}</span> ${totalSteps}`;
    } else if (progressTextElement) { // Fallback if translations not ready
        progressTextElement.innerHTML = `Step ${n} of ${totalSteps}`;
    }


    const progressBarFillElement = document.getElementById('progressBarFill');
    if (progressBarFillElement) {
        const progressPercentage = totalSteps > 0 ? (n / totalSteps) * 100 : 0;
        progressBarFillElement.style.width = `${progressPercentage}%`;
    }
    currentStep = n;
}

function nextStep() {
  if (currentStep < totalSteps) { 
    showStep(currentStep + 1);
  }
}

function prevStep() {
  if (currentStep > 1) {
    showStep(currentStep - 1);
  }
}

// ValidateStep is no longer needed as all fields are optional
// function validateStep(step) { return true; }


// --- 8. submitAnswers() ---
async function submitAnswers() {
    if (!questionnaireDef) {
        console.error("Questionnaire definition not loaded. Cannot submit.");
        alert("Error: Data definition not loaded. Please refresh.");
        return;
    }

    const answersData = {};
    questionnaireDef.questions.forEach(question => {
        const qId = `q_${question.id}`;
        switch (question.type) {
            case 'radio':
                const selectedRadio = document.querySelector(`input[name="${qId}"]:checked`);
                answersData[question.id] = selectedRadio ? selectedRadio.value : null;
                break;
            case 'checkbox_group':
                answersData[question.id] = Array.from(document.querySelectorAll(`input[name="${qId}"]:checked`))
                                               .map(el => el.value);
                break;
            case 'freetext': // textarea
            case 'text':     // input type=text
            case 'number':   // input type=number
            // Add other simple input types here if needed
                const element = document.getElementById(qId);
                answersData[question.id] = element ? element.value : '';
                break;
            default:
                answersData[question.id] = null; // Or some indicator for unsupported/uncollected types
                break;
        }
    });

    const payload = {
        language: currentLang,
        answers: answersData // Sending the structured answers object
    };

    try {
        const res = await fetch('/api/submit', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify(payload) // Send the new payload structure
        });

        if (res.ok) {
            const responseData = await res.json();
            if (responseData.status === 'success') {
                // Pass the collected answersData to thank_you.html
                const answersJson = JSON.stringify(answersData);
                const encodedAnswers = encodeURIComponent(answersJson);
                window.location.href = `thank_you.html?data=${encodedAnswers}`;
            } else {
                alert(`Submission was not successful. Server responded with: ${responseData.message || 'Unknown error'}`);
            }
        } else {
            alert(`There was an issue submitting your answers. Server responded with status: ${res.status}`);
        }
    } catch (e) {
        alert('Error submitting answers. Please try again.');
        console.error("Error submitting answers:", e);
    }
}


// --- 7. Initial Call Flow (IIFE) ---
(async () => {
    currentLang = localStorage.getItem('language') || 'en';
    const languageSelectorElement = document.getElementById('languageSelector');
    if (languageSelectorElement) {
        languageSelectorElement.value = currentLang;
    }
    
    await fetchQuestionnaireDef(); // Must complete before language loading if language loading depends on it (e.g. for titles)
    await loadLanguage(currentLang); // Fetches UI translations and then calls renderQuestionnaire

    // renderQuestionnaire and showStep(1) are now called inside loadLanguage after translations are ready
    // and questionnaireDef is available.
    // If questionnaireDef failed to load, an error is shown, and rendering won't proceed.
    if (questionnaireDef && uiTranslations[currentLang]) {
         showStep(1); // Ensure initial step is shown if all loaded correctly.
    }
})();

// --- 9. Language Selector Event Listener ---
const languageSelector = document.getElementById('languageSelector');
if (languageSelector) {
    languageSelector.addEventListener('change', async (event) => {
        await loadLanguage(event.target.value);
    });
}

// --- Obsolete function removal ---
// The old applyTranslations function is removed. Its responsibilities are now split:
// - Static UI elements (titles, buttons) are handled by applyStaticTranslations (called by renderQuestionnaire).
// - Dynamic question text (labels, options, placeholders) is handled during element creation in createInputElement 
//   and by renderQuestionnaire using the current language data.
// The old `translations` global variable is replaced by `uiTranslations`.
// The old `totalSteps` fixed value is replaced by one loaded from questionnaireDef.
// The old `submitAnswers` logic is completely replaced.
// The old `validateStep` is removed (or simplified to return true).
// The old `loadLanguage` is replaced.
// The old IIFE is replaced.
// The old `createInputElement` is replaced.
// The old `renderQuestionnaire` is replaced.
// The old `showStep` is replaced.
// The old `nextStep` and `prevStep` are simplified to just rely on global `totalSteps`.
// Essentially, the entire script is a replacement.The `static/script.js` file was overwritten in the previous turn (Turn 59) with a comprehensive refactoring to implement the new JSON-driven questionnaire logic. This rewrite addressed all points specified in the current subtask description.

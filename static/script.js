let currentStep = 1;
let questionnaireDef = null; // To store questionnaire definition
const translations = {};    // Existing: to store language strings
let currentLang = 'en';     // Existing: to store current language
let totalSteps = 5; // Default, will be updated from questionnaireDef

async function fetchQuestionnaireDef() {
    try {
        const response = await fetch('/static/questionnaire_def.json');
        if (!response.ok) {
            throw new Error(`HTTP error! status: ${response.status}`);
        }
        questionnaireDef = await response.json();
        totalSteps = questionnaireDef.totalSteps; // Update global totalSteps
        console.log("Questionnaire definition loaded:", questionnaireDef);
    } catch (error) {
        console.error('Error fetching or parsing questionnaire definition:', error);
    }
}

function createInputElement(question, langData) {
    const qId = `q_${question.id}`; // Prefix 'q_' to avoid conflicts with other element IDs
    let inputElement;

    switch (question.type) {
        case 'text':
        case 'number':
        case 'time': // Added time type
            inputElement = document.createElement('input');
            inputElement.type = question.type;
            inputElement.id = qId;
            inputElement.name = qId;
            if (question.placeholder_key && langData[question.placeholder_key]) {
                inputElement.placeholder = langData[question.placeholder_key];
            }
            break;
        case 'select':
            inputElement = document.createElement('select');
            inputElement.id = qId;
            inputElement.name = qId;
            if (question.options) {
                question.options.forEach(opt => {
                    const option = document.createElement('option');
                    option.value = opt.value;
                    option.textContent = langData[opt.label_key] || opt.value; // Fallback to value if key not found
                    inputElement.appendChild(option);
                });
            }
            break;
        // TODO: Add cases for 'textarea', 'checkbox_group', 'radio' in future iterations
        default:
            inputElement = document.createElement('p');
            inputElement.textContent = `Unsupported question type: ${question.type}`;
    }
    return inputElement;
}

function renderQuestionnaire() {
    if (!questionnaireDef || !translations[currentLang]) {
        console.error('Questionnaire definition or translations not loaded. Cannot render.');
        return;
    }

    // Update main title - this could be moved to applyTranslations if it makes more sense there
    const mainTitleElement = document.querySelector('h1[data-i18n-key="main_title"]');
    if (mainTitleElement && translations[currentLang][questionnaireDef.questionnaireTitleKey]) {
        mainTitleElement.textContent = translations[currentLang][questionnaireDef.questionnaireTitleKey];
    }
    
    // Clear previous dynamic content from question containers
    for (let i = 1; i <= totalSteps; i++) {
        const stepQuestionsContainer = document.getElementById(`step${i}_questions_container`);
        if (stepQuestionsContainer) {
            stepQuestionsContainer.innerHTML = ''; // Clear previous questions
        }
    }

    const langData = translations[currentLang];

    questionnaireDef.questions.forEach(question => {
        const stepQuestionsContainer = document.getElementById(`step${question.step}_questions_container`);
        if (!stepQuestionsContainer) {
            console.warn(`Container for step ${question.step} not found.`);
            return; // Skip this question if its container doesn't exist
        }

        const questionElementDiv = document.createElement('div');
        questionElementDiv.className = 'form-group'; // Using a common class for styling

        const label = document.createElement('label');
        label.htmlFor = `q_${question.id}`;
        label.textContent = langData[question.label_key] || question.id; // Fallback to ID if key not found
        label.setAttribute('data-i18n-key', question.label_key); // Keep i18n key for potential re-translation by applyTranslations
        questionElementDiv.appendChild(label);

        const inputEl = createInputElement(question, langData);
        questionElementDiv.appendChild(inputEl);

        stepQuestionsContainer.appendChild(questionElementDiv);
    });
    
    // After rendering, apply translations again to ensure all dynamically created elements with data-i18n-key are translated.
    // This is important if createInputElement doesn't handle all translation aspects (e.g. for complex types later)
    applyTranslations(langData); 
    showStep(currentStep); // Refresh current step display
}


function showStep(n) {
  if (questionnaireDef) { // Ensure questionnaireDef is loaded
    totalSteps = questionnaireDef.totalSteps;
  }

  document.querySelectorAll('.step').forEach((div, i) => {
    div.style.display = i === (n - 1) ? 'block' : 'none';
  });

  const progressTextElement = document.getElementById('progressText');
  if (progressTextElement && translations[currentLang]) { // Check if translations for currentLang are loaded
    const stepText = translations[currentLang]?.progress_step || "Step";
    const ofText = translations[currentLang]?.progress_of || "of";
    progressTextElement.innerHTML = `<span data-i18n-key="progress_step">${stepText}</span> ${n} <span data-i18n-key="progress_of">${ofText}</span> ${totalSteps}`;
  }

  const progressBarFillElement = document.getElementById('progressBarFill');
  if (progressBarFillElement) {
    const progressPercentage = totalSteps > 0 ? (n / totalSteps) * 100 : 0; // Avoid division by zero
    progressBarFillElement.style.width = `${progressPercentage}%`;
  }
  currentStep = n;
}

function nextStep() {
  // totalSteps is now global and updated by fetchQuestionnaireDef
  if (validateStep(currentStep) && currentStep < totalSteps) { 
    showStep(currentStep + 1);
  }
}

function prevStep() {
  if (currentStep > 1) {
    showStep(currentStep - 1);
  }
}

function validateStep(step) {
  // All fields are now optional, so no validation is needed.
  return true;
}

// login() function removed

async function submitAnswers() {
  // Since validateStep always returns true, this check is technically not needed
  // but can be kept for structural consistency or future validation re-introduction.
  if (!validateStep(currentStep)) return; 
  
  const answers = {};
  if (questionnaireDef && questionnaireDef.questions) {
      questionnaireDef.questions.forEach(question => {
          const qId = `q_${question.id}`;
          const element = document.getElementById(qId);
          if (element) {
              // TODO: Handle checkbox groups and radio groups by querying document.querySelectorAll(`input[name="${qId}"]:checked`)
              // For now, this handles text, select, number, time.
              answers[question.id] = element.value; 
          }
          // TODO: Handle "other" text fields for composite questions like exercise_type, beverages
      });
  } else {
      console.error("Questionnaire definition not loaded, cannot collect answers.");
      alert("Error: Questionnaire definition not loaded. Cannot submit."); // User-facing error
      return;
  }

  // TODO: Re-implement collection for hardcoded HTML elements if any are still used (e.g. symptoms checklist)
  // For now, assuming all questions are dynamically generated or will be.
  // The existing symptom checklist needs to be either integrated into questionnaire_def.json or handled separately.
  // Example: (if they remain hardcoded)
  // answers.symptoms = { checklist: [], other_concerns: '', stress_level: '' };
  // if (document.getElementById('sym_tired')?.checked) answers.symptoms.checklist.push('tiredness_fatigue');
  // ... and so on for other symptoms.
  // And q_health_concerns_text, q_stress_level need to be added to answers object too.
  // This will be addressed in a subsequent phase.

  const langForSubmission = localStorage.getItem('language') || 'en';
  const payload = {
      features: JSON.stringify(answers), 
      language: langForSubmission,
      products: "" 
  };

  const res = await fetch('/api/submit', { 
    method: 'POST',
    headers: {'Content-Type': 'application/json'},
    body: JSON.stringify(payload) 
  });

  if (res.ok) {
    try {
      const responseData = await res.json();
      if (responseData.status === 'success') {
        const answersJson = JSON.stringify(answers); // Use dynamically collected answers
        const encodedAnswers = encodeURIComponent(answersJson);
        window.location.href = 'thank_you.html?data=' + encodedAnswers;
      } else {
        alert('Submission was not successful. Server responded with: ' + (responseData.message || 'Unknown error'));
      }
    } catch (e) {
      alert('Error parsing server response. Please try again.');
      console.error("Error parsing JSON response:", e);
    }
  } else {
    alert('There was an issue submitting your answers. Server responded with status: ' + res.status);
  }
}

// Internationalization (translations object is already global)

async function loadLanguage(lang) {
    currentLang = lang; // Update global currentLang
    try {
        const response = await fetch(`/static/i18n/${lang}.json`);
        if (!response.ok) {
            throw new Error(`HTTP error! status: ${response.status} for ${lang}.json`);
        }
        const data = await response.json();
        translations[lang] = data;
        localStorage.setItem('language', lang);
        
        const languageSelector = document.getElementById('languageSelector');
        if (languageSelector) {
            languageSelector.value = lang;
        }
        
        if (questionnaireDef) { // If questionnaireDef is loaded, render
            renderQuestionnaire();
        }
        // applyTranslations will be called by renderQuestionnaire or needs to be called if questionnaire is not re-rendered
        // For now, renderQuestionnaire will call applyTranslations at the end.
        
    } catch (error) {
        console.error(`Error loading language ${lang}:`, error);
        if (lang !== 'en') { // Fallback to English if primary language fails
            console.warn("Falling back to English language.");
            await loadLanguage('en'); // Ensure this await is handled
        } else {
            // If English itself fails, there's a bigger issue.
            // Display a user-friendly error or use hardcoded defaults.
            const mainTitle = document.querySelector('h1[data-i18n-key="main_title"]');
            if(mainTitle) mainTitle.textContent = "Error: Could not load language files.";
        }
    }
}

function applyTranslations(translationData) {
    if (!translationData) {
        console.warn('No translation data to apply.');
        return;
    }
    document.querySelectorAll('[data-i18n-key]').forEach(element => {
        const key = element.getAttribute('data-i18n-key');
        if (translationData[key]) {
            if (element.tagName === 'INPUT' && element.hasAttribute('placeholder')) {
                 // Check if the i18n key is specifically for the placeholder
                if (key === element.dataset.i18nPlaceholderKey) { // Assuming a convention e.g. data-i18n-placeholder-key
                    element.placeholder = translationData[key];
                } else if (!element.dataset.i18nPlaceholderKey) { // If no specific placeholder key, use the general one.
                     element.placeholder = translationData[key];
                }
            } else if (element.tagName === 'BUTTON' || element.tagName === 'LABEL' || element.tagName === 'H2' || element.tagName === 'OPTION' || element.tagName === 'SPAN' || element.tagName === 'H1') {
                element.textContent = translationData[key];
            } else if (element.id !== 'progressText') { 
                // Avoid re-translating elements that have structured content like progressText
                // or elements whose text content is managed by other functions (e.g. question labels in renderQuestionnaire)
                // This part might need refinement based on how dynamic text vs. static text with data-i18n-key is handled.
                // For now, if it's not a known container type and not progress text, update innerText.
                // element.innerText = translationData[key]; // Potentially too broad, let renderQuestionnaire handle its elements
            }
        } else {
            if (key !== 'progress_step' && key !== 'progress_of' && !key.startsWith("q_") && !key.startsWith("step") && !key.startsWith("lang_") && !key.startsWith("gender_option_") && !key.startsWith("work_env_option_") && !key.startsWith("posture_option_") && !key.startsWith("transport_option_") && !key.startsWith("work_demand_option_") && !key.startsWith("exercise_freq_option_") && !key.startsWith("diet_pref_option_") && !key.startsWith("stress_level_option_") && !key.startsWith("age_") && !key.startsWith("hours_") && !key.startsWith("commute_") && !key.startsWith("ex_type_") && !key.startsWith("sleep_") && !key.startsWith("meals_") && !key.startsWith("bev_") && key !== "select_placeholder" && key !== "select_option_default" && key !== "main_title" && key !== "next_button" && key !== "back_button" && key !== "submit_button" && key !== "yes_option" && key !== "no_option" && key !== "supplements_placeholder") {
                 console.warn(`No translation found for key: ${key}`);
            }
        }
    });

    // Update dynamic progress text separately
    const progressTextElement = document.getElementById('progressText');
    if (progressTextElement && translations[currentLang]) {
        const stepText = translations[currentLang]?.progress_step || "Step";
        const ofText = translations[currentLang]?.progress_of || "of";
        progressTextElement.innerHTML = `<span data-i18n-key="progress_step">${stepText}</span> ${currentStep} <span data-i18n-key="progress_of">${ofText}</span> ${totalSteps}`;
    }
}

// Initialize the questionnaire
(async () => {
    currentLang = localStorage.getItem('language') || 'en';
    const languageSelectorElement = document.getElementById('languageSelector');
    if (languageSelectorElement) {
        languageSelectorElement.value = currentLang;
    }
    
    await fetchQuestionnaireDef(); // Fetch definition first
    await loadLanguage(currentLang); // Then load language (which now calls renderQuestionnaire)
    // showStep(1) is called at the end of renderQuestionnaire if needed, or by loadLanguage if not.
    // For clarity, explicitly call showStep(1) after everything is loaded and rendered.
    if (questionnaireDef && translations[currentLang]) { // Ensure everything is ready
        showStep(1);
    }
})();

// Add event listener for language selector
const languageSelector = document.getElementById('languageSelector');
if (languageSelector) {
    languageSelector.addEventListener('change', async (event) => { // Make listener async
        await loadLanguage(event.target.value); // Await language loading and rendering
    });
}

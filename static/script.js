let currentStep = 1;
const totalSteps = 5;

function showStep(n) {
  document.querySelectorAll('.step').forEach((div, i) => {
    div.style.display = i === n - 1 ? 'block' : 'none';
  });

  // Update progress text
  const progressTextElement = document.getElementById('progressText');
  if (progressTextElement) {
    const currentLang = localStorage.getItem('language') || 'en';
    const stepText = translations[currentLang]?.progress_step || "Step";
    const ofText = translations[currentLang]?.progress_of || "of";
    progressTextElement.innerHTML = `<span data-i18n-key="progress_step">${stepText}</span> ${n} <span data-i18n-key="progress_of">${ofText}</span> ${totalSteps}`;
  }

  // Update progress bar
  const progressBarFillElement = document.getElementById('progressBarFill');
  if (progressBarFillElement) {
    const progressPercentage = (n / totalSteps) * 100;
    progressBarFillElement.style.width = `${progressPercentage}%`;
  }

  currentStep = n;
}

function nextStep() {
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
  const answers = {
    age: document.getElementById('q_age').value,
    occupation: document.getElementById('q_job').value,
    location: document.getElementById('q_location').value,
    work_hours: document.getElementById('q_hours').value,
    work_env: document.getElementById('q_environment').value,
    posture: document.getElementById('q_posture').value,
    transport: document.getElementById('q_transport').value,
    physical_demand: document.getElementById('q_work').value,
    exercise_freq: document.getElementById('q_exercise').value,
    exercise_duration: document.getElementById('q_exercise_duration').value,
    exercise_types: Array.from(document.querySelectorAll('input[name="exercise_type"]:checked')).map(el => el.value),
    exercise_type_other: document.getElementById('q_exercise_type_other').value,
    commute_time: document.getElementById('q_commute_time').value,
    // Sleep fields
    sleep_time: document.getElementById('q_sleep').value,
    wake_time: document.getElementById('q_wake').value,
    avg_sleep: document.getElementById('q_avg_sleep').value, // New
    // Diet fields
    food_like: document.getElementById('q_food_like').value,
    food_dislike: document.getElementById('q_food_dislike').value,
    diet_preference: document.getElementById('q_diet').value, // Renamed q_diet to diet_preference for clarity
    diet_restrictions: document.getElementById('q_diet_restrictions').value, // New
    meals_per_day: document.getElementById('q_meals_per_day').value, // New
    beverage_choices: Array.from(document.querySelectorAll('input[name="beverages"]:checked')).map(el => el.value),
    beverages_other: document.getElementById('q_beverages_other').value,
    // Lifestyle fields
    // For radio buttons, ensure a value is selected or provide a default/null
    smoke: document.querySelector('input[name="smoke"]:checked') ? document.querySelector('input[name="smoke"]:checked').value : null,
    alcohol: document.querySelector('input[name="alcohol"]:checked') ? document.querySelector('input[name="alcohol"]:checked').value : null,
    health_goals: Array.from(document.querySelectorAll('input[name="goal"]:checked')).map(el => el.value), // Renamed goals to health_goals
    supplement_use: document.querySelector('input[name="supplement_use"]:checked') ? document.querySelector('input[name="supplement_use"]:checked').value : null,
    current_supplements: document.getElementById('supplements').value, // Renamed supplements to current_supplements
    medical_conditions: document.getElementById('q_medical_conditions').value, // New
    // New demographic field
    gender: document.getElementById('q_gender').value,
    // Symptoms / Health Info
    symptoms: {
      checklist: [],
      other_concerns: document.getElementById('q_health_concerns_text').value,
      stress_level: document.getElementById('q_stress_level').value
    }
  };
  if (document.getElementById('sym_tired').checked) answers.symptoms.checklist.push('tiredness_fatigue');
  if (document.getElementById('sym_pain').checked) answers.symptoms.checklist.push('muscle_joint_pain');
  if (document.getElementById('sym_digestive').checked) answers.symptoms.checklist.push('digestive_issues');
  if (document.getElementById('sym_sleep').checked) answers.symptoms.checklist.push('poor_sleep_quality');

  const currentLang = localStorage.getItem('language') || 'en'; // Get current language
  const payload = {
      username: "testuser", // Using a placeholder username
      answers: answers, // The existing answers object
      language: currentLang
  };

  const res = await fetch('/questionnaire', { // Corrected endpoint
    method: 'POST',
    headers: {'Content-Type': 'application/json'},
    body: JSON.stringify(payload) // Updated payload
  });

  if (res.ok) {
    try {
      const responseData = await res.json();
      if (responseData.status === 'success') {
        const answersJson = JSON.stringify(answers);
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

// Internationalization
const translations = {};

async function loadLanguage(lang) {
    try {
        const response = await fetch(`/static/i18n/${lang}.json`);
        const data = await response.json();
        translations[lang] = data;
        applyTranslations(translations[lang]);
        localStorage.setItem('language', lang);
        // Update language selector to reflect the loaded language
        const languageSelector = document.getElementById('languageSelector');
        if (languageSelector) {
            languageSelector.value = lang;
        }
    } catch (error) {
        console.error(`Error loading language ${lang}:`, error);
        // Fallback to English if loading fails
        if (lang !== 'en') {
            loadLanguage('en');
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
                // Specifically target placeholders for INPUT elements
                if (key === element.dataset.i18nKey) { // Check if the key is for placeholder
                    element.placeholder = translationData[key];
                }
            } else if (element.tagName === 'BUTTON' || element.tagName === 'LABEL' || element.tagName === 'H2' || element.tagName === 'OPTION' || element.tagName === 'SPAN' || element.tagName === 'H1') {
                element.textContent = translationData[key];
            } else if (element.id !== 'progressText') { // Avoid affecting progress text structure
                element.innerText = translationData[key];
            }
        } else {
             // Don't warn for progress_step and progress_of as they are handled in showStep
            if (key !== 'progress_step' && key !== 'progress_of') {
                console.warn(`No translation found for key: ${key}`);
            }
        }
    });

    // Update dynamic progress text separately to ensure it always reflects the current step and language
    const progressTextElement = document.getElementById('progressText');
    if (progressTextElement) {
        const currentLang = localStorage.getItem('language') || 'en';
        const stepText = translations[currentLang]?.progress_step || "Step";
        const ofText = translations[currentLang]?.progress_of || "of";
        // Ensure currentStep is defined and correctly used. It's a global variable.
        progressTextElement.innerHTML = `<span data-i18n-key="progress_step">${stepText}</span> ${currentStep} <span data-i18n-key="progress_of">${ofText}</span> ${totalSteps}`;
    }
}

// Initialize the first step of the questionnaire on load & load language
(async () => {
    const savedLang = localStorage.getItem('language') || 'en';
    await loadLanguage(savedLang); // Ensure translations are loaded
    showStep(1); // Then show the first step, which also updates progress text
})();

// Add event listener for language selector
const languageSelector = document.getElementById('languageSelector');
if (languageSelector) {
    languageSelector.addEventListener('change', (event) => {
        loadLanguage(event.target.value);
    });
}

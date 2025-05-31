let currentStep = 1;
let questionnaireDef = null;
let currentLang = 'en';

const uiTranslations = {
    en: {
        lang_en: "English",
        lang_fr: "Français",
        lang_th: "Thai",
        main_title: "Supplementary Test Kit",
        generic_health_survey: "Supplementary Test Kit",
        progress_step: "Step",
        progress_of: "of",
        step1_title: "Basic Information",
        step2_title: "Work Environment",
        step3_title: "Sleep and Diet",
        step4_title: "Lifestyle and Goals",
        step5_title: "Symptoms",
        next_button: "Next",
        back_button: "Back",
        submit_button: "Submit"
    },
    fr: {
        lang_en: "Anglais",
        lang_fr: "Français",
        lang_th: "Thaï",
        main_title: "Kit de Test Supplémentaire",
        generic_health_survey: "Kit de Test Supplémentaire",
        progress_step: "Étape",
        progress_of: "de",
        step1_title: "Informations de Base",
        step2_title: "Environnement de Travail",
        step3_title: "Sommeil et Alimentation",
        step4_title: "Style de Vie et Objectifs",
        step5_title: "Symptômes",
        next_button: "Suivant",
        back_button: "Retour",
        submit_button: "Soumettre"
    },
    th: {
        lang_en: "ภาษาอังกฤษ",
        lang_fr: "ภาษาฝรั่งเศษ",
        lang_th: "ภาษาไทย",
        main_title: "\u0e0a\u0e38\u0e14\u0e17\u0e14\u0e2a\u0e2d\u0e1a\u0e2d\u0e32\u0e2b\u0e32\u0e23\u0e40\u0e2a\u0e23\u0e34\u0e21",
        generic_health_survey: "\u0e0a\u0e38\u0e14\u0e17\u0e14\u0e2a\u0e2d\u0e1a\u0e2d\u0e32\u0e2b\u0e32\u0e23\u0e40\u0e2a\u0e23\u0e34\u0e21",
        progress_step: "\u0e02\u0e31\u0e49\u0e19\u0e15\u0e2d\u0e19",
        progress_of: "\u0e08\u0e32\u0e01",

        step1_title: "ข้อพื้นฐาน",
        step2_title: "\u0e2a\u0e34\u0e48\u0e07\u0e41\u0e27\u0e14\u0e25\u0e49\u0e2d\u0e21\u0e43\u0e19\u0e17\u0e35\u0e48\u0e17\u0e33\u0e07\u0e32\u0e19",
        step3_title: "\u0e01\u0e32\u0e23\u0e19\u0e2d\u0e19\u0e2b\u0e25\u0e31\u0e1a\u0e41\u0e25\u0e30\u0e01\u0e32\u0e23\u0e01\u0e34\u0e19",
        step4_title: "\u0e27\u0e34\u0e16\u0e35\u0e0a\u0e35\u0e27\u0e34\u0e15\u0e41\u0e25\u0e30\u0e40\u0e1b\u0e49\u0e32\u0e2b\u0e21\u0e32\u0e22",
        step5_title: "\u0e2d\u0e32\u0e01\u0e32\u0e23\u0e15\u0e48\u0e32\u0e07\u0e46",
        next_button: "\u0e15\u0e48\u0e2d\u0e44\u0e1b",
        back_button: "\u0e22\u0e49\u0e2d\u0e19\u0e01\u0e25\u0e31\u0e1a",
        submit_button: "\u0e2a\u0e48\u0e07\u0e02\u0e49\u0e2d\u0e21\u0e39\u0e25"
    },
	my: { 
		lang_en: "အင်္ဂလိပ်",
		lang_fr: "ပြင်သစ်",
		lang_th: "ထိုင်း",
                main_title: "ထပ်ဆောင်း စမ်းသပ်ကိရိယာ",
                generic_health_survey: "ထပ်ဆောင်း စမ်းသပ်ကိရိယာ",
		progress_step: "အဆင့်",
		progress_of: "၏",
		step1_title: "အခြေခံသတင်းအချက်အလက်",
		step2_title: "အလုပ်ပတ်ဝန်းကျင်",
		step3_title: "အိပ်ရေးနှင့် အစားအသောက်",
		step4_title: "နေထိုင်မှုနှင့် ရည်မှန်းချက်များ",
		step5_title: "ရောဂါလက္ခဏာများ",
		next_button: "ရှေ့ဆက်",
		back_button: "နောက်ပြန်",
		submit_button: "တင်သွင်းရန်"
	},

	lo: { 
		lang_en: "ພາສາອັງກິດ",
		lang_fr: "ພາສາຝຣັ່ງ",
		lang_th: "ພາສາໄທ",
                main_title: "ຊຸດທົດສອບເສີມ",
                generic_health_survey: "ຊຸດທົດສອບເສີມ",
		progress_step: "ຂັ້ນ",
		progress_of: "ຂອງ",
		step1_title: "ຂໍ້ມູນພື້ນຖານ",
		step2_title: "ສະພາບແວດລ້ອມການເຮັດວຽກ",
		step3_title: "ການນອນ ແລະ ອາຫານ",
		step4_title: "ວິຖີຊີວິດ ແລະ ເປົ້າໝາຍ",
		step5_title: "ອາການ",
		next_button: "ຕໍ່ໄປ",
		back_button: "ກັບຄືນ",
		submit_button: "ສົ່ງ"
	},

	ja: { 
		lang_en: "英語",
		lang_fr: "フランス語",
		lang_th: "タイ語",
                main_title: "サプリメント検査キット",
                generic_health_survey: "サプリメント検査キット",
		progress_step: "ステップ",
		progress_of: "／",
		step1_title: "基本情報",
		step2_title: "職場環境",
		step3_title: "睡眠と食事",
		step4_title: "ライフスタイルと目標",
		step5_title: "症状",
		next_button: "次へ",
		back_button: "戻る",
		submit_button: "送信"
	},

	zh: { 
		lang_en: "英语",
		lang_fr: "法语",
		lang_th: "泰语",
                main_title: "补充测试套件",
                generic_health_survey: "补充测试套件",
		progress_step: "步骤",
		progress_of: "／",
		step1_title: "基本信息",
		step2_title: "工作环境",
		step3_title: "睡眠与饮食",
		step4_title: "生活方式与目标",
		step5_title: "症状",
		next_button: "下一步",
		back_button: "返回",
		submit_button: "提交"
	},

	ko: { 
		lang_en: "영어",
		lang_fr: "프랑스어",
		lang_th: "태국어",
                main_title: "보조 검사 키트",
                generic_health_survey: "보조 검사 키트",
		progress_step: "단계",
		progress_of: "중",
		step1_title: "기본 정보",
		step2_title: "근무 환경",
		step3_title: "수면 및 식단",
		step4_title: "생활 방식 및 목표",
		step5_title: "증상",
		next_button: "다음",
		back_button: "뒤로",
		submit_button: "제출"
	},

	ms: { 
		lang_en: "Bahasa Inggeris",
		lang_fr: "Bahasa Perancis",
		lang_th: "Bahasa Thai",
                main_title: "Kit Ujian Tambahan",
                generic_health_survey: "Kit Ujian Tambahan",
		progress_step: "Langkah",
		progress_of: "daripada",
		step1_title: "Maklumat Asas",
		step2_title: "Persekitaran Kerja",
		step3_title: "Tidur dan Diet",
		step4_title: "Gaya Hidup dan Matlamat",
		step5_title: "Gejala",
		next_button: "Seterusnya",
		back_button: "Kembali",
		submit_button: "Hantar"
	},

	km: {
	  lang_en: "ភាសាអង់គ្លេស",
	  lang_fr: "ភាសាបារាំង",
	  lang_th: "ភាសាថៃ",
	  main_title: "ឧបករណ៍តេស្តបន្ថែម",
	  generic_health_survey: "ឧបករណ៍តេស្តបន្ថែម",
	  progress_step: "ជំហាន",
	  progress_of: "ក្នុងចំណោម",
	  step1_title: "ព័ត៌មានមូលដ្ឋាន",
	  step2_title: "បរិស្ថានការងារ",
	  step3_title: "ការគេង និងអាហារ",
	  step4_title: "របៀបរស់នៅ និងគោលដៅ",
	  step5_title: "រោគសញ្ញា",
	  next_button: "បន្ទាប់",
	  back_button: "ថយក្រោយ",
	  submit_button: "បញ្ជូន"
	}
};


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
function loadLanguage(lang) {
    currentLang = lang;
    localStorage.setItem('language', lang);
    const languageSelector = document.getElementById('languageSelector');
    if (languageSelector) {
        languageSelector.value = currentLang;
    }

    try {
        if (!uiTranslations[currentLang]) {
            throw new Error(`Translations for ${currentLang} not available`);
        }
        console.log(`Using embedded translations for ${currentLang}`);
        
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
            console.warn('Falling back to English language.');
            currentLang = 'en';
        }
        if (questionnaireDef && uiTranslations[currentLang]) {
            renderQuestionnaire();
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

// Helper to create step containers dynamically based on totalSteps
function ensureStepContainers() {
    const stepsWrapper = document.getElementById('stepsContainer');
    if (!stepsWrapper) return;

    if (stepsWrapper.childElementCount === totalSteps) {
        return; // Already generated
    }

    stepsWrapper.innerHTML = '';

    for (let i = 1; i <= totalSteps; i++) {
        const stepDiv = document.createElement('div');
        stepDiv.id = `step${i}`;
        stepDiv.className = 'step';
        if (i !== 1) {
            stepDiv.style.display = 'none';
        }

        const title = document.createElement('h2');
        title.setAttribute('data-i18n-key', `step${i}_title`);
        title.textContent = `Step ${i}`;
        stepDiv.appendChild(title);

        const qContainer = document.createElement('div');
        qContainer.id = `step${i}_questions_container`;
        qContainer.className = 'questions-container';
        stepDiv.appendChild(qContainer);

        const btnGroup = document.createElement('div');
        btnGroup.className = 'button-group';

        if (i > 1) {
            const backBtn = document.createElement('button');
            backBtn.className = 'btn-secondary';
            backBtn.setAttribute('data-i18n-key', 'back_button');
            backBtn.textContent = 'Back';
            backBtn.onclick = prevStep;
            btnGroup.appendChild(backBtn);
        }

        if (i < totalSteps) {
            const nextBtn = document.createElement('button');
            nextBtn.setAttribute('data-i18n-key', 'next_button');
            nextBtn.textContent = 'Next';
            nextBtn.onclick = nextStep;
            btnGroup.appendChild(nextBtn);
        } else {
            const submitBtn = document.createElement('button');
            submitBtn.setAttribute('data-i18n-key', 'submit_button');
            submitBtn.textContent = 'Submit';
            submitBtn.onclick = submitAnswers;
            btnGroup.appendChild(submitBtn);
        }

        stepDiv.appendChild(btnGroup);
        stepsWrapper.appendChild(stepDiv);
    }
}


// --- 4. renderQuestionnaire() ---
function renderQuestionnaire() {
    if (!questionnaireDef || !uiTranslations[currentLang]) {
        console.error('Questionnaire definition or UI translations not loaded. Cannot render.');
        return;
    }

    applyStaticTranslations(); // Apply translations to static parts of the UI
    ensureStepContainers();

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
    // Scroll to top whenever we change steps for better UX
    window.scrollTo({ top: 0, behavior: 'smooth' });
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
    console.log('submitAnswers called');
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

    // Get all buttons and disable them
    const buttons = document.querySelectorAll('button');
    buttons.forEach(button => button.disabled = true);
    console.log('Buttons disabled:', buttons);

    // Create and display "Please wait" message
    const pleaseWaitMessage = document.createElement('div');
    pleaseWaitMessage.id = 'pleaseWaitMessage';
    // Inline styles removed

    const messageText = document.createElement('div');
    messageText.textContent = 'Please wait...'; // Consider internationalizing this
    pleaseWaitMessage.appendChild(messageText);

    const loader = document.createElement('div');
    loader.className = 'loader'; // Assuming CSS for .loader exists
    pleaseWaitMessage.appendChild(loader);
    console.log('pleaseWaitMessage element created:', pleaseWaitMessage);

    document.body.appendChild(pleaseWaitMessage);
    console.log('pleaseWaitMessage appended to body');

    let submissionSuccessful = false; // Flag for successful submission
    try {
        const res = await fetch('/api/submit', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify(payload) // Send the new payload structure
        });

        if (res.ok) {
            const responseData = await res.json();
            if (responseData.status === 'success') {
                submissionSuccessful = true; // Set flag before redirection
                // Pass the collected answersData to thank_you.html
                const answersJson = JSON.stringify(answersData);
                const encodedAnswers = encodeURIComponent(answersJson);
                const encodedLang = encodeURIComponent(currentLang);
                window.location.href = `thank_you.html?data=${encodedAnswers}&lang=${encodedLang}`;
            } else {
                alert(`Submission was not successful. Server responded with: ${responseData.message || 'Unknown error'}`);
                console.log('Submission failed, re-enabling buttons');
                buttons.forEach(button => button.disabled = false); // Re-enable buttons
            }
        } else {
            alert(`There was an issue submitting your answers. Server responded with status: ${res.status}`);
            console.log('HTTP error, re-enabling buttons');
            buttons.forEach(button => button.disabled = false); // Re-enable buttons
        }
    } catch (e) {
        alert('Error submitting answers. Please try again.');
        console.error("Error submitting answers:", e);
        console.log('Error caught, re-enabling buttons');
        buttons.forEach(button => button.disabled = false); // Re-enable buttons
    } finally {
        console.log('Finally block entered. submissionSuccessful:', submissionSuccessful);
        if (!submissionSuccessful) {
            console.log('Submission not successful or error occurred, removing pleaseWaitMessage');
            const messageElement = document.getElementById('pleaseWaitMessage');
            if (messageElement) {
                document.body.removeChild(messageElement);
            }
        } else {
            console.log('Submission successful, pleaseWaitMessage will remain until page redirects.');
        }
    }
}


// --- 7. Initial Call Flow (IIFE) ---
(async () => {
    currentLang = localStorage.getItem('language') || 'th';
    const languageSelectorElement = document.getElementById('languageSelector');
    if (languageSelectorElement) {
        languageSelectorElement.value = currentLang;
    }

    await fetchQuestionnaireDef();
    loadLanguage(currentLang);

    if (questionnaireDef) {
        showStep(1);
    }
})();

// --- 9. Language Selector Event Listener ---
const languageSelector = document.getElementById('languageSelector');
if (languageSelector) {
    languageSelector.addEventListener('change', (event) => {
        loadLanguage(event.target.value);
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

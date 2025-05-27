let currentStep = 1;
const totalSteps = 5;

function showStep(n) {
  document.querySelectorAll('.step').forEach((div, i) => {
    div.style.display = i === n - 1 ? 'block' : 'none';
  });

  // Update progress text
  const progressTextElement = document.getElementById('progressText');
  if (progressTextElement) {
    progressTextElement.innerText = `Step ${n} of ${totalSteps}`;
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
  if (step === 1) {
    if (!document.getElementById('q_age').value ||
        !document.getElementById('q_job').value ||
        !document.getElementById('q_location').value ||
        !document.getElementById('q_hours').value) {
      alert('Please answer all questions on this step');
      return false;
    }
  } else if (step === 2) {
    if (!document.getElementById('q_environment').value ||
        !document.getElementById('q_posture').value ||
        !document.getElementById('q_transport').value ||
        !document.getElementById('q_work').value ||
        !document.getElementById('q_exercise').value) {
      alert('Please answer all questions on this step');
      return false;
    }
  } else if (step === 3) {
    if (!document.getElementById('q_sleep').value ||
        !document.getElementById('q_wake').value ||
        !document.getElementById('q_food_like').value ||
        !document.getElementById('q_food_dislike').value ||
        !document.getElementById('q_diet').value ||
        !document.getElementById('q_avg_sleep').value ||
        !document.getElementById('q_meals_per_day').value ||
        !document.getElementById('q_beverages').value) {
      alert('Please answer all questions on this step');
      return false;
    }
  } else if (step === 4) {
    if (!document.querySelector('input[name="smoke"]:checked') ||
        !document.querySelector('input[name="alcohol"]:checked') ||
        !document.querySelector('input[name="supplement_use"]:checked')) {
      alert('Please answer all questions on this step');
      return false;
    }
  } else if (step === 5) { // New validation for step 5
    if (!document.getElementById('q_stress_level').value) {
      alert('Please answer all questions on this step');
      return false;
    }
  }
  return true;
}

// login() function removed

async function submitAnswers() {
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
    // New exercise fields
    exercise_duration: document.getElementById('q_exercise_duration').value,
    exercise_type: document.getElementById('q_exercise_type').value,
    // New commute field
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
    beverages: document.getElementById('q_beverages').value, // New
    // Lifestyle fields
    smoke: document.querySelector('input[name="smoke"]:checked').value,
    alcohol: document.querySelector('input[name="alcohol"]:checked').value,
    health_goals: Array.from(document.querySelectorAll('input[name="goal"]:checked')).map(el => el.value), // Renamed goals to health_goals
    supplement_use: document.querySelector('input[name="supplement_use"]:checked').value,
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

  const res = await fetch('/api/submit', { // Updated endpoint
    method: 'POST',
    headers: {'Content-Type': 'application/json'},
    // Updated payload structure
    body: JSON.stringify({ features: JSON.stringify(answers), products: "" })
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

// Initialize the first step of the questionnaire on load
showStep(1);

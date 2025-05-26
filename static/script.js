let currentUser = null;
let currentStep = 1;
const totalSteps = 5;

function showStep(n) {
  document.querySelectorAll('.step').forEach((div, i) => {
    div.style.display = i === n - 1 ? 'block' : 'none';
  });
  document.getElementById('progress').innerText = `Step ${n} of ${totalSteps}`;
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
        !document.getElementById('q_diet').value) {
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
  }
  return true;
}

async function register() {
  const res = await fetch('/register', {
    method: 'POST',
    headers: {'Content-Type': 'application/json'},
    body: JSON.stringify({
      username: document.getElementById('reg-user').value,
      password: document.getElementById('reg-pass').value
    })
  });
  alert(await res.text());
}

async function login() {
  const res = await fetch('/login', {
    method: 'POST',
    headers: {'Content-Type': 'application/json'},
    body: JSON.stringify({
      username: document.getElementById('log-user').value,
      password: document.getElementById('log-pass').value
    })
  });
  const text = await res.text();
  alert(text);
  const data = JSON.parse(text);
  if (data.status === 'ok') {
    currentUser = document.getElementById('log-user').value;
    document.getElementById('auth').style.display = 'none';
    document.getElementById('questionnaire').style.display = 'block';
    showStep(1);
  }
}

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
    sleep_time: document.getElementById('q_sleep').value,
    wake_time: document.getElementById('q_wake').value,
    food_like: document.getElementById('q_food_like').value,
    food_dislike: document.getElementById('q_food_dislike').value,
    diet: document.getElementById('q_diet').value,
    smoke: document.querySelector('input[name="smoke"]:checked').value,
    alcohol: document.querySelector('input[name="alcohol"]:checked').value,
    goals: Array.from(document.querySelectorAll('input[name="goal"]:checked')).map(el => el.value),
    supplement_use: document.querySelector('input[name="supplement_use"]:checked').value,
    supplements: document.getElementById('supplements').value,
    symptoms: []
  };
  if (document.getElementById('sym_tired').checked) answers.symptoms.push('tired');
  if (document.getElementById('sym_pain').checked) answers.symptoms.push('pain');
  if (document.getElementById('sym_digestive').checked) answers.symptoms.push('digestive');
  if (document.getElementById('sym_sleep').checked) answers.symptoms.push('sleep');

  const res = await fetch('/questionnaire', {
    method: 'POST',
    headers: {'Content-Type': 'application/json'},
    body: JSON.stringify({username: currentUser, answers})
  });
  alert(await res.text());
}

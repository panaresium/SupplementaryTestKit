let currentUser = null;
let currentStep = 1;
const totalSteps = 3;

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
    if (!document.getElementById('q_work').value ||
        !document.getElementById('q_hours').value ||
        !document.getElementById('q_diet').value) {
      alert('Please answer all questions on this step');
      return false;
    }
  } else if (step === 2) {
    if (!document.querySelector('input[name="supplement_use"]:checked')) {
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
    work: document.getElementById('q_work').value,
    hours: document.getElementById('q_hours').value,
    diet: document.getElementById('q_diet').value,
    goals: Array.from(document.querySelectorAll('input[name="goal"]:checked')).map(el => el.value),
    supplement_use: document.querySelector('input[name="supplement_use"]:checked').value,
    supplements: document.getElementById('supplements').value,
    symptoms: []
  };
  if (document.getElementById('sym_tired').checked) answers.symptoms.push('tired');
  if (document.getElementById('sym_pain').checked) answers.symptoms.push('pain');

  const res = await fetch('/questionnaire', {
    method: 'POST',
    headers: {'Content-Type': 'application/json'},
    body: JSON.stringify({username: currentUser, answers})
  });
  alert(await res.text());
}

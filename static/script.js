const regForm = document.getElementById('registerForm');
const regResult = document.getElementById('registerResult');
regForm.addEventListener('submit', async (e) => {
  e.preventDefault();
  const data = Object.fromEntries(new FormData(regForm).entries());
  const res = await fetch('/register', {
    method: 'POST',
    headers: {'Content-Type': 'application/json'},
    body: JSON.stringify(data)
  });
  regResult.textContent = await res.text();
});

const loginForm = document.getElementById('loginForm');
const loginResult = document.getElementById('loginResult');
const questionSection = document.getElementById('questionnaire');
const uploadSection = document.getElementById('upload');
let currentUser = '';
loginForm.addEventListener('submit', async (e) => {
  e.preventDefault();
  const data = Object.fromEntries(new FormData(loginForm).entries());
  const res = await fetch('/login', {
    method: 'POST',
    headers: {'Content-Type': 'application/json'},
    body: JSON.stringify(data)
  });
  const text = await res.text();
  loginResult.textContent = text;
  if (res.ok) {
    currentUser = data.username;
    questionSection.style.display = 'block';
    uploadSection.style.display = 'block';
  }
});

const qForm = document.getElementById('questionForm');
const qResult = document.getElementById('questionResult');
qForm.addEventListener('submit', async (e) => {
  e.preventDefault();
  const form = new FormData(qForm);
  const answers = {};
  form.forEach((v, k) => {
    if (answers[k]) {
      if (Array.isArray(answers[k])) answers[k].push(v); else answers[k] = [answers[k], v];
    } else {
      answers[k] = v;
    }
  });
  const res = await fetch('/questionnaire', {
    method: 'POST',
    headers: {'Content-Type': 'application/json'},
    body: JSON.stringify({username: currentUser, answers})
  });
  qResult.textContent = await res.text();
});

const upForm = document.getElementById('uploadForm');
const upResult = document.getElementById('uploadResult');
upForm.addEventListener('submit', async (e) => {
  e.preventDefault();
  const data = new FormData(upForm);
  data.append('username', currentUser);
  const res = await fetch('/upload', {method:'POST', body:data});
  upResult.textContent = await res.text();
});

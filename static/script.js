async function register() {
  const res = await fetch('/register', {
    method: 'POST',
    headers: {'Content-Type': 'application/json'},
    body: JSON.stringify({username: document.getElementById('reg-user').value,
                         password: document.getElementById('reg-pass').value})
  });
  alert(await res.text());
}

async function login() {
  const res = await fetch('/login', {
    method: 'POST',
    headers: {'Content-Type': 'application/json'},
    body: JSON.stringify({username: document.getElementById('log-user').value,
                         password: document.getElementById('log-pass').value})
  });
  alert(await res.text());
}

async function submitAnswers() {
  const res = await fetch('/questionnaire', {
    method: 'POST',
    headers: {'Content-Type': 'application/json'},
    body: JSON.stringify({username: document.getElementById('log-user').value,
                         answers: JSON.parse(document.getElementById('answers').value)})
  });
  alert(await res.text());
}

async function uploadFile() {
  const fileInput = document.getElementById('file');
  if (!fileInput.files.length) return;
  const formData = new FormData();
  formData.append('image', fileInput.files[0]);
  const res = await fetch('/upload', {method:'POST', body: formData});
  const text = await res.text();
  document.getElementById('preview').innerHTML = text.includes('url') ?
    `<img src="${JSON.parse(text).url}" width="200">` : text;
}

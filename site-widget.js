// site-widget.js
document.addEventListener('DOMContentLoaded', () => {
  const form = document.createElement('form');
  const input = document.createElement('input');
  const button = document.createElement('button');
  const responseDiv = document.createElement('div');

  input.type = 'text';
  input.placeholder = 'Kysy jotain...';
  button.type = 'submit';
  button.innerText = 'Kysy';

  form.appendChild(input);
  form.appendChild(button);
  document.body.appendChild(form);
  document.body.appendChild(responseDiv);

  form.addEventListener('submit', async (e) => {
    e.preventDefault();
    const question = input.value;

    const res = await fetch('http://localhost:8000/ask', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ question })
    });

    const data = await res.json();
    responseDiv.innerText = data.answer || 'Ei vastausta';
  });
});

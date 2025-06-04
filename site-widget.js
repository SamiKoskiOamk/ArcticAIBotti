// site-widget.js
document.addEventListener('DOMContentLoaded', () => {
  // 🧱 Luodaan UI-elementit
  const chatBox = document.createElement('div');
  chatBox.style.position = 'fixed';
  chatBox.style.top = '20px';
  chatBox.style.right = '20px';
  chatBox.style.width = '300px';
  chatBox.style.maxHeight = '80vh';
  chatBox.style.overflowY = 'auto';
  chatBox.style.backgroundColor = '#f9f9f9';
  chatBox.style.border = '1px solid #ccc';
  chatBox.style.borderRadius = '10px';
  chatBox.style.padding = '10px';
  chatBox.style.fontFamily = 'sans-serif';
  chatBox.style.boxShadow = '0 2px 8px rgba(0,0,0,0.15)';
  chatBox.style.zIndex = '1000';

  const header = document.createElement('h4');
  header.innerText = '🤖 Arctic AI-botti';
  header.style.marginTop = '0';

  const form = document.createElement('form');
  const input = document.createElement('input');
  const button = document.createElement('button');
  const log = document.createElement('div');
  const spinner = document.createElement('div');

  input.type = 'text';
  input.placeholder = 'Kysy jotain...';
  input.style.width = '100%';
  input.style.padding = '8px';
  input.style.marginBottom = '8px';
  input.style.border = '1px solid #ccc';
  input.style.borderRadius = '5px';

  button.type = 'submit';
  button.innerText = 'Kysy';
  button.style.width = '100%';
  button.style.padding = '10px';
  button.style.backgroundColor = '#007bff';
  button.style.color = 'white';
  button.style.border = 'none';
  button.style.borderRadius = '5px';
  button.style.cursor = 'pointer';

  log.style.marginTop = '10px';
  log.style.whiteSpace = 'pre-wrap';
  log.style.fontSize = '14px';
  log.style.color = '#333';

  spinner.style.display = 'none';
  spinner.innerHTML = '🤖 <span class="dotting">Työn touhussa</span>';
  spinner.style.fontSize = '14px';
  spinner.style.marginTop = '8px';
  spinner.style.color = '#888';
  spinner.classList.add('spinner');

  // Dotting effect CSS
  const style = document.createElement('style');
  style.innerHTML = `
    .dotting::after {
      content: '⠋';
      animation: dots 1.2s steps(5, end) infinite;
    }
    @keyframes dots {
      0% { content: '⠋'; }
      20% { content: '⠙'; }
      40% { content: '⠹'; }
      60% { content: '⠸'; }
      80% { content: '⠼'; }
      100% { content: '⠴'; }
    }
  `;
  document.head.appendChild(style);

  form.appendChild(input);
  form.appendChild(button);
  chatBox.appendChild(header);
  chatBox.appendChild(form);
  chatBox.appendChild(spinner);
  chatBox.appendChild(log);
  document.body.appendChild(chatBox);

  // 📡 Lomakkeen lähetys
  form.addEventListener('submit', async (e) => {
    e.preventDefault();
    const question = input.value.trim();
    if (!question) {
      log.innerText = '⚠️ Kirjoita kysymys ennen lähettämistä.';
      return;
    }

    log.innerHTML = `📤 Lähetetään kysymys: "${question}"`;
    spinner.style.display = 'block';

    try {
      const res = await fetch('http://localhost:8000/query', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ question })
      });
      const data = await res.json();

      spinner.style.display = 'none';

      if (data.answer) {
        log.innerHTML += `\n✅ Vastaus:\n${data.answer}`;
      } else {
        log.innerHTML += `\n❌ Ei vastausta`;
      }
    } catch (err) {
      spinner.style.display = 'none';
      log.innerHTML += `\n❌ Virhe: ${err.message}`;
    }
  });
});

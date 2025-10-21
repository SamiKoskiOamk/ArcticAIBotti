// site-widget.js
document.addEventListener('DOMContentLoaded', () => {
  const chatBox = document.createElement('div');
  chatBox.style.cssText = `
    position: fixed; top: 20px; right: 20px; width: 300px; max-height: 80vh;
    overflow-y: auto; background: #f9f9f9; border: 1px solid #ccc; border-radius: 10px;
    padding: 10px; font-family: sans-serif; box-shadow: 0 2px 8px rgba(0,0,0,.15); z-index: 1000;
  `;

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
  input.style.cssText = 'width:100%;padding:8px;margin-bottom:8px;border:1px solid #ccc;border-radius:5px;';

  button.type = 'submit';
  button.innerText = 'Kysy';
  button.style.cssText = 'width:100%;padding:10px;background:#007bff;color:#fff;border:none;border-radius:5px;cursor:pointer;';

  log.style.cssText = 'margin-top:10px;white-space:pre-wrap;font-size:14px;color:#333;';

  spinner.style.display = 'none';
  spinner.innerHTML = '🤖 <span class="dotting">Työn touhussa</span>';
  spinner.style.cssText = 'font-size:14px;margin-top:8px;color:#888;';
  spinner.classList.add('spinner');

  const style = document.createElement('style');
  style.innerHTML = `
    .dotting::after { content: '⠋'; animation: dots 1.2s steps(5, end) infinite; }
    @keyframes dots {
      0% { content: '⠋'; } 20% { content: '⠙'; } 40% { content: '⠹'; }
      60% { content: '⠸'; } 80% { content: '⠼'; } 100% { content: '⠴'; }
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
      // Kutsu backendin GET /ask?query=...
      const url = `http://localhost:8000/ask?${new URLSearchParams({ query: question }).toString()}`;
      const res = await fetch(url, { method: 'GET' });

      if (!res.ok) {
        const text = await res.text();
        throw new Error(`HTTP ${res.status} ${res.statusText}: ${text}`);
      }

      const data = await res.json();
      spinner.style.display = 'none';

      if (data.error) {
        log.innerHTML += `\n❌ Virhe: ${data.error}`;
        return;
      }

      const answer = data.answer ?? '';
      const sources = Array.isArray(data.sources) ? data.sources : [];
      const sourceList = sources
        .filter(s => s && s.source)
        .map(s => `• ${s.source}`)
        .join('\n');

      log.innerHTML += `\n\n✅ Vastaus:\n${answer}${sourceList ? `\n\n🔗 Lähteet:\n${sourceList}` : ''}`;
    } catch (err) {
      spinner.style.display = 'none';
      log.innerHTML += `\n❌ Virhe: ${err.message}`;
    }
  });
});

(function() {
  const style = `
    #ai-widget { position:fixed; top:20px; right:20px; width:500px; font-family:sans-serif; }
    #ai-box { background:white; border:1px solid #ccc; padding:10px; border-radius:8px; box-shadow:0 2px 8px rgba(0,0,0,0.2); }
    #ai-response { margin-top:10px; min-height:50px; white-space:pre-wrap; }
    #ai-input { width:100%; padding:8px; border:1px solid #ccc; border-radius:4px; box-sizing: border-box; }
    #ai-button { margin-top:5px; width:100%; padding:8px; background:#007bff; color:white; border:none; border-radius:4px; cursor:pointer; }
  `;

  const html = `
    <div id="ai-widget">
      <div id="ai-box">
          <div id="ai-info">
          Tämä on paikallisesti toimiva webpage hakukone-widget, <br>
          jonka voit laittaa verkkosivullesi. <br>
          Lue ensin vasemman laidan prosessikuvaus, miten tämä toimii ja testaa sitten. <br>
          Tämä hakubotti toimii täysin paikallisesti. <br>
          Tietoja ei lähetetä mihinkään.</p>
          </div>
        <input type="text" id="ai-input" placeholder="💬 Kysy mitä haluat tietää..." />
        <button id="ai-button">Kysy</button>
        <div id="ai-response"></div>
      </div>
    </div>
  `;

  const styleEl = document.createElement('style');
  styleEl.innerText = style;
  document.head.appendChild(styleEl);

  const wrapper = document.createElement('div');
  wrapper.innerHTML = html;
  document.body.appendChild(wrapper);

  async function sendToBackend(message) {
    try {
      const response = await fetch("http://localhost:8000/ask", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ question: message })
      });
      const data = await response.json();
      return data.answer || data.error || "🤖 Ei vastausta.";
    } catch (err) {
      return `❌ Virhe: ${err.message}`;
    }
  }

  document.getElementById("ai-button").onclick = async () => {
    const input = document.getElementById("ai-input").value;
    const responseEl = document.getElementById("ai-response");
    responseEl.innerHTML = "🤖 Muodostan vastausta kysymyksen ja paikallisen tietokannan avulla..";

    const answer = await sendToBackend(input);
    responseEl.innerHTML = `<strong>Vastaus:</strong><br>${answer}`;
  };
})();

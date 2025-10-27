function spammer() {
  return {
    authKey: '', gamertag: '', message: 'GG EZ', amount: 50, running: false, progress: 0, cooldown: 0, logs: [],
    async startSpam() {
      if (!this.authKey) return alert('API Key is required!');
      this.running = true; this.logs = ['Initializing...'];
      const form = new URLSearchParams();
      form.append('auth_key', this.authKey);
      form.append('gamertag', this.gamertag);
      form.append('message', this.message);
      form.append('amount', this.amount || 999999);
      const res = await fetch('/start', { method: 'POST', headers: { 'Content-Type': 'application/x-www-form-urlencoded' }, body: form });
      const data = await res.json();
      if (data.error) { alert(data.error); this.running = false; }
      this.pollStatus();
    },
    async stopSpam() { await fetch('/stop', { method: 'POST' }); this.running = false; },
    pollStatus() {
      const interval = setInterval(async () => {
        if (!this.running) { clearInterval(interval); return; }
        const res = await fetch('/status'); const data = await res.json();
        this.progress = data.progress; this.cooldown = data.cooldown; this.logs = data.logs;
        if (!data.active) { this.running = false; clearInterval(interval); }
      }, 500);
    }
  };
}

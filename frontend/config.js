// Arquivo público: coloque aqui apenas configuração não secreta.
// Antes da Hostinger, substitua SEU-PROJETO pela URL real da Vercel.
const ambienteLocal = ['localhost', '127.0.0.1'].includes(window.location.hostname);
window.APP_CONFIG = Object.freeze({
  apiBaseUrl: ambienteLocal ? 'http://127.0.0.1:8000' : 'https://SEU-PROJETO.vercel.app'
});

// Arquivo público: coloque aqui apenas configuração não secreta.
// URL pública confirmada da API Vercel; não contém segredo.
const ambienteLocal = ['localhost', '127.0.0.1'].includes(window.location.hostname);
window.APP_CONFIG = Object.freeze({
  apiBaseUrl: ambienteLocal
    ? 'http://127.0.0.1:8000'
    : 'https://simulador-parcelas-objetivos.vercel.app'
});

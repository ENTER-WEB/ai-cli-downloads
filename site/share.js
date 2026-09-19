const button = document.querySelector('#copy-link');
const status = document.querySelector('#copy-status');
button?.addEventListener('click', async () => {
  try {
    await navigator.clipboard.writeText(new URL('/', location.href).href);
    status.textContent = 'リンクをコピーしました';
  } catch {
    status.textContent = 'アドレスバーのURLをコピーしてください';
  }
});

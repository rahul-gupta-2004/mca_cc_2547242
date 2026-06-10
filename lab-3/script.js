let count = 0;
const btn   = document.getElementById('btn');
const display = document.getElementById('count');

btn.addEventListener('click', () => {
  count++;
  display.textContent = count;
});
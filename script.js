
document.addEventListener("click", (e) => {
  const btn = e.target.closest(".copy");
  if (!btn) return;
  const id = btn.getAttribute("data-target");
  const el = document.getElementById(id);
  if (!el) return;
  const text = el.innerText;
  navigator.clipboard.writeText(text).then(()=>{
    btn.textContent = "Gekopieerd!";
    setTimeout(()=>btn.textContent="Kopieer", 1200);
  });
});

/* Mode jour / nuit — partagé par toutes les pages Vendora.
   Applique le thème AVANT le rendu (pas de flash). Préférence mémorisée par appareil. */
(function () {
  try { if (localStorage.getItem('v_theme') === 'light') document.documentElement.setAttribute('data-theme', 'light'); }
  catch (e) {}
})();
function toggleTheme() {
  var h = document.documentElement, light = h.getAttribute('data-theme') === 'light';
  if (light) { h.removeAttribute('data-theme'); try { localStorage.setItem('v_theme', 'dark'); } catch (e) {} }
  else { h.setAttribute('data-theme', 'light'); try { localStorage.setItem('v_theme', 'light'); } catch (e) {} }
}

'use strict';
/* OQ SPEDITION — intro loading scene + 3D globe of Kazakhstan directions.
   No third-party libraries, no trackers. Canvas is a schematic, not live tracking. */
(() => {
  const $ = (s, root = document) => root.querySelector(s);
  const $$ = (s, root = document) => Array.from(root.querySelectorAll(s));
  const basePath = window.OQ_BASE_PATH || '';
  const reducedMotion = matchMedia('(prefers-reduced-motion: reduce)').matches;

  /* ---------------------------------------------------------------- Intro */
  const intro = $('#oqIntro');
  if (intro && intro.showModal) {
    let introTimers = [];
    const rememberIntro = () => { try { sessionStorage.setItem('oq-intro-seen', '1'); } catch (_) {} };
    const hasSeenIntro = () => { try { return sessionStorage.getItem('oq-intro-seen') === '1'; } catch (_) { return false; } };
    const closeIntro = () => {
      introTimers.forEach(clearTimeout); introTimers = [];
      if (!intro.open) return;
      intro.classList.add('leaving');
      introTimers.push(setTimeout(() => { intro.close(); intro.classList.remove('leaving'); }, reducedMotion ? 0 : 420));
      rememberIntro();
    };
    function playIntro() {
      introTimers.forEach(clearTimeout); introTimers = [];
      intro.classList.remove('second', 'leaving');
      if ($('#oqIntroStep')) $('#oqIntroStep').textContent = '01 / 02';
      if (!intro.open) intro.showModal();
      introTimers.push(setTimeout(() => { intro.classList.add('second'); if ($('#oqIntroStep')) $('#oqIntroStep').textContent = '02 / 02'; }, 1500));
      introTimers.push(setTimeout(closeIntro, 3550));
    }
    const skip = $('#oqSkipIntro');
    if (skip) skip.addEventListener('click', closeIntro);
    intro.addEventListener('cancel', () => { introTimers.forEach(clearTimeout); rememberIntro(); });
    if (!hasSeenIntro() && !reducedMotion) playIntro();
  }

  /* --------------------------------------------------------------- Globe */
  const canvas = $('#globe');
  if (!canvas) return;
  const ctx = canvas.getContext('2d');
  const D = Math.PI / 180;

  const land = [
    [[-10,36],[-9,43],[-1,44],[-5,48],[2,51],[8,54],[8,58],[18,70],[30,71],[40,67],[50,69],[65,71],[80,73],[103,77],[116,73],[133,70],[147,72],[169,66],[178,65],[175,57],[161,59],[155,52],[147,49],[141,45],[135,46],[132,41],[126,39],[129,35],[122,39],[119,35],[122,30],[119,25],[113,22],[110,20],[107,11],[104,9],[100,15],[99,8],[103,1],[100,1],[96,8],[92,20],[87,22],[81,17],[78,8],[75,9],[71,20],[66,25],[61,25],[56,26],[51,13],[44,13],[39,20],[36,29],[32,31],[27,37],[23,36],[20,40],[17,40],[16,38],[13,38],[12,44],[8,43],[3,42],[-2,36]],
    [[-17,15],[-17,22],[-12,28],[-8,34],[1,37],[10,37],[16,32],[25,32],[33,31],[36,24],[42,13],[51,12],[47,5],[43,-1],[41,-11],[35,-22],[31,-30],[24,-35],[18,-34],[14,-25],[12,-16],[8,-4],[3,5],[-5,5],[-12,9]],
    [[-168,71],[-155,71],[-144,69],[-135,69],[-123,74],[-111,75],[-95,79],[-80,77],[-69,70],[-62,62],[-55,53],[-62,47],[-66,44],[-72,43],[-75,36],[-81,25],[-86,29],[-97,26],[-98,21],[-91,18],[-87,21],[-86,16],[-83,15],[-80,9],[-78,8],[-85,10],[-90,15],[-96,15],[-104,21],[-112,25],[-117,33],[-124,41],[-126,49],[-135,58],[-145,60],[-151,61],[-164,55],[-169,60]],
    [[-81,12],[-72,12],[-62,10],[-52,4],[-47,-1],[-35,-6],[-36,-14],[-40,-21],[-48,-28],[-53,-34],[-58,-39],[-65,-49],[-69,-55],[-74,-51],[-74,-39],[-72,-30],[-70,-18],[-78,-6],[-81,0]],
    [[-53,60],[-44,62],[-35,70],[-19,78],[-23,83],[-43,84],[-59,80],[-64,72]],
    [[112,-22],[115,-34],[128,-33],[136,-36],[144,-38],[151,-33],[154,-25],[146,-15],[142,-11],[137,-16],[130,-12],[122,-15]],
    [[46,-13],[51,-16],[49,-23],[44,-26],[43,-20]],
    [[-8,50],[-5,51],[-5,55],[-7,58],[-3,59],[0,53]],
    [[130,31],[135,34],[140,40],[142,45],[145,44],[143,39],[139,35],[134,32]],
    [[95,5],[104,0],[106,-6],[103,-5],[98,0]],[[108,7],[119,6],[118,-4],[110,-4]],[[130,-1],[140,-3],[151,-7],[145,-10],[135,-6]],[[166,-35],[178,-38],[173,-47],[168,-46]],[[120,18],[123,12],[125,7],[121,6],[118,10]],[[106,-6],[115,-8],[114,-10],[106,-8]]
  ];
  function inside(lon, lat, polygon) { let yes = false; for (let i = 0, j = polygon.length - 1; i < polygon.length; j = i++) { const [xi, yi] = polygon[i], [xj, yj] = polygon[j]; if (((yi > lat) !== (yj > lat)) && lon < (xj - xi) * (lat - yi) / (yj - yi) + xi) yes = !yes; } return yes; }
  function vector(lat, lon) { return [Math.cos(lat * D) * Math.sin(lon * D), Math.sin(lat * D), Math.cos(lat * D) * Math.cos(lon * D)]; }

  const landPoints = [];
  for (let lat = -56; lat <= 82; lat += 2.7) { const spacing = 2.9 / Math.max(.35, Math.cos(lat * D)); for (let lon = -178; lon < 180; lon += spacing) { if (land.some(p => inside(lon, lat, p))) landPoints.push(vector(lat, lon)); } }

  // Cities of Kazakhstan + neighbouring countries (schematic directions).
  const routes = [
    { label: 'Алматы', lat: 43.24, lon: 76.89, yaw: 69, offset: [12, 16] },
    { label: 'Астана', lat: 51.16, lon: 71.43, yaw: 69, offset: [6, -16] },
    { label: 'Шымкент', lat: 42.32, lon: 69.59, yaw: 69, offset: [-40, 22] },
    { label: 'Актобе', lat: 50.28, lon: 57.17, yaw: 63, offset: [-46, -12] },
    { label: 'Атырау', lat: 47.09, lon: 51.92, yaw: 60, offset: [-56, 18] },
    { label: 'Караганда', lat: 49.80, lon: 73.09, yaw: 69, offset: [16, -16] }
  ];
  const hub = vector(48.02, 66.92); // geographic centre of Kazakhstan
  let activeRoute = 0, yaw = 69, targetYaw = 69, pitch = 20, dragging = null, interacted = false, visible = false, frame = null, previous = 0;
  let cw = 640, ch = 600, radius = 240, centerX = 320, centerY = 300, drawTime = 0;
  const paused = reducedMotion;

  const arcs = routes.map(r => {
    const dest = vector(r.lat, r.lon);
    const dot = Math.max(-1, Math.min(1, hub.reduce((s, v, i) => s + v * dest[i], 0)));
    const angle = Math.acos(dot) || 1e-6;
    const points = [];
    for (let i = 0; i <= 64; i++) { const t = i / 64, a = Math.sin((1 - t) * angle) / Math.sin(angle), b = Math.sin(t * angle) / Math.sin(angle), lift = 1 + .21 * Math.sin(t * Math.PI); points.push(hub.map((v, k) => (v * a + dest[k] * b) * lift)); }
    return points;
  });
  function projected(v, extra = 0) { const cy = Math.cos((yaw + extra) * D), sy = Math.sin((yaw + extra) * D), cp = Math.cos(pitch * D), sp = Math.sin(pitch * D); const x = v[0] * cy - v[2] * sy, z = v[0] * sy + v[2] * cy, y = v[1] * cp - z * sp; return { x: centerX + radius * x, y: centerY - radius * y, z: v[1] * sp + z * cp }; }
  function curve(points, color, width, extra) { ctx.beginPath(); let drawing = false; points.forEach(v => { const p = projected(v, extra); if (p.z > -.015) { if (!drawing) ctx.moveTo(p.x, p.y); else ctx.lineTo(p.x, p.y); drawing = true; } else drawing = false; }); ctx.strokeStyle = color; ctx.lineWidth = width; ctx.stroke(); }
  function drawGlobe(now = 0) {
    if (!ctx || !cw || !ch) return;
    ctx.clearRect(0, 0, cw, ch);
    const extra = paused || interacted ? 0 : Math.sin(now / 22000) * 4;
    const halo = ctx.createRadialGradient(centerX, centerY, radius * .75, centerX, centerY, radius * 1.25); halo.addColorStop(0, 'rgba(123,143,160,.07)'); halo.addColorStop(1, 'rgba(123,143,160,0)'); ctx.fillStyle = halo; ctx.beginPath(); ctx.arc(centerX, centerY, radius * 1.28, 0, Math.PI * 2); ctx.fill();
    const globeFill = ctx.createRadialGradient(centerX - radius * .45, centerY - radius * .55, radius * .1, centerX, centerY, radius * 1.18); globeFill.addColorStop(0, '#243544'); globeFill.addColorStop(.55, '#152534'); globeFill.addColorStop(1, '#0b141f'); ctx.fillStyle = globeFill; ctx.beginPath(); ctx.arc(centerX, centerY, radius, 0, Math.PI * 2); ctx.fill(); ctx.strokeStyle = '#7e94a633'; ctx.lineWidth = 1; ctx.stroke();
    for (let lat = -60; lat <= 60; lat += 30) { const pts = []; for (let lon = -180; lon <= 180; lon += 4) pts.push(vector(lat, lon)); curve(pts, '#b7a4761d', .65, extra); }
    for (let lon = -180; lon < 180; lon += 30) { const pts = []; for (let lat = -90; lat <= 90; lat += 3) pts.push(vector(lat, lon)); curve(pts, '#b7a4761d', .65, extra); }
    landPoints.forEach(v => { const p = projected(v, extra); if (p.z > 0) { const opacity = .2 + p.z * .5; ctx.fillStyle = `rgba(179,191,194,${opacity})`; ctx.beginPath(); ctx.arc(p.x, p.y, Math.max(.65, cw / 470) * (.55 + p.z * .45), 0, Math.PI * 2); ctx.fill(); } });
    arcs.forEach((arc, i) => curve(arc, i === activeRoute ? '#eac47a' : '#caa36166', i === activeRoute ? 1.7 : .9, extra));
    if (!paused) { const arc = arcs[activeRoute], v = arc[Math.floor((now / 55) % arc.length)], p = projected(v, extra); if (p.z > 0) { ctx.shadowBlur = 12; ctx.shadowColor = '#e5b660'; ctx.fillStyle = '#ffdea0'; ctx.beginPath(); ctx.arc(p.x, p.y, 3.2, 0, Math.PI * 2); ctx.fill(); ctx.shadowBlur = 0; } }
    const small = cw < 460;
    routes.forEach((r, i) => { const p = projected(vector(r.lat, r.lon), extra); if (p.z < .08) return; const selected = i === activeRoute; ctx.fillStyle = selected ? '#f1c876' : '#b09a74'; ctx.beginPath(); ctx.arc(p.x, p.y, selected ? 4.2 : 3, 0, Math.PI * 2); ctx.fill();
      if (small && !selected) return;
      ctx.font = `${selected ? 550 : 400} 14px Arial, sans-serif`; ctx.textBaseline = 'middle'; const label = r.label; const textWidth = ctx.measureText(label).width; const x = Math.max(6, Math.min(cw - textWidth - 6, p.x + r.offset[0] * (small ? .85 : 1))), y = Math.max(18, Math.min(ch - 22, p.y + r.offset[1])); ctx.fillStyle = '#101b28d9'; ctx.fillRect(x - 5, y - 10, textWidth + 10, 20); ctx.fillStyle = selected ? '#efd398' : '#b7c1cc'; ctx.fillText(label, x, y);
    });
  }
  function tick(now) { frame = null; if (document.hidden || !visible) return; if (now - previous > 30) { previous = now; if (!dragging && !interacted) yaw += (targetYaw - yaw) * .065; drawTime = now; drawGlobe(now); } if (!paused && visible) frame = requestAnimationFrame(tick); }
  function schedule() { if (frame === null && !document.hidden && visible) frame = requestAnimationFrame(tick); }
  function resizeGlobe() { const rect = canvas.getBoundingClientRect(); if (!rect.width || !rect.height) return; cw = rect.width; ch = rect.height; const dpr = Math.min(window.devicePixelRatio || 1, 2); canvas.width = Math.round(cw * dpr); canvas.height = Math.round(ch * dpr); if (ctx) ctx.setTransform(dpr, 0, 0, dpr, 0, 0); radius = Math.min(cw * .415, ch * .425); centerX = cw / 2; centerY = ch * .485; drawGlobe(drawTime); }
  function selectRoute(i, focus = false) {
    activeRoute = i; const data = routes[i]; targetYaw = data.yaw; interacted = false; pitch = 20;
    if (paused) yaw = targetYaw;
    $$('.globe-city-tab').forEach((tab, n) => { const selected = n === i; tab.classList.toggle('active', selected); tab.setAttribute('aria-selected', String(selected)); tab.tabIndex = selected ? 0 : -1; });
    const title = $('#globeCityTitle'), desc = $('#globeCityDescription');
    if (title) title.textContent = data.label + ' → любой город Казахстана';
    if (desc) desc.textContent = 'Выберите направление — подставим его в запрос на расчёт.';
    drawGlobe(drawTime); schedule(); if (focus) $(`.globe-city-tab:nth-child(${i + 1})`).focus();
  }
  $$('.globe-city-tab').forEach((tab, i) => {
    tab.addEventListener('click', () => selectRoute(i));
    tab.addEventListener('keydown', e => { let n = i; const total = routes.length; if (['ArrowRight', 'ArrowDown'].includes(e.key)) n = (i + 1) % total; else if (['ArrowLeft', 'ArrowUp'].includes(e.key)) n = (i + total - 1) % total; else if (e.key === 'Home') n = 0; else if (e.key === 'End') n = total - 1; else return; e.preventDefault(); selectRoute(n, true); });
  });
  const globeCta = $('#globeCityCta');
  if (globeCta) globeCta.addEventListener('click', () => {
    const route = $('#quickRoute');
    if (route) { route.value = routes[activeRoute].label + ' → '; route.dispatchEvent(new Event('input')); route.focus(); }
  });
  canvas.addEventListener('pointerdown', e => { dragging = { x: e.clientX, y: e.clientY, yaw, pitch }; interacted = true; canvas.setPointerCapture(e.pointerId); });
  canvas.addEventListener('pointermove', e => { if (!dragging) return; yaw = dragging.yaw - (e.clientX - dragging.x) * .35; pitch = Math.max(-45, Math.min(60, dragging.pitch + (e.clientY - dragging.y) * .24)); drawGlobe(drawTime); });
  ['pointerup', 'pointercancel', 'lostpointercapture'].forEach(event => canvas.addEventListener(event, () => { dragging = null; }));
  canvas.addEventListener('keydown', e => { if (!['ArrowLeft', 'ArrowRight', 'ArrowUp', 'ArrowDown', 'Home'].includes(e.key)) return; e.preventDefault(); interacted = true; if (e.key === 'ArrowLeft') yaw += 8; if (e.key === 'ArrowRight') yaw -= 8; if (e.key === 'ArrowUp') pitch = Math.min(60, pitch + 6); if (e.key === 'ArrowDown') pitch = Math.max(-45, pitch - 6); if (e.key === 'Home') { yaw = routes[activeRoute].yaw; pitch = 20; } drawGlobe(drawTime); });
  if ('ResizeObserver' in window) new ResizeObserver(resizeGlobe).observe(canvas); else window.addEventListener('resize', resizeGlobe);
  if ('IntersectionObserver' in window) { new IntersectionObserver(entries => { visible = entries[0].isIntersecting; if (visible) { drawGlobe(drawTime); schedule(); } else if (frame !== null) { cancelAnimationFrame(frame); frame = null; } }, { rootMargin: '120px' }).observe(canvas); } else { visible = true; schedule(); }
  document.addEventListener('visibilitychange', schedule); resizeGlobe();
})();

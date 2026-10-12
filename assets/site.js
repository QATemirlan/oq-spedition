'use strict';
(() => {
  const routes = window.OQ_ROUTES || [];
  const vehicles = window.OQ_VEHICLES || [];
  const money = value => new Intl.NumberFormat('ru-RU').format(value).replace(/\u00a0/g, ' ');
  const from = document.querySelector('#fromCity');
  const to = document.querySelector('#toCity');
  const truck = document.querySelector('#truck');
  const bodyType = document.querySelector('#bodyType');
  const bodySize = document.querySelector('#bodySize');
  const returnTrip = document.querySelector('#returnTrip');
  const result = document.querySelector('#calcResult');
  const order = document.querySelector('#calcOrder');
  const quickRoute = document.querySelector('#quickRoute');
  const quickVehicle = document.querySelector('#quickVehicle');
  const cityPicker = document.querySelector('#headerCity');
  const originLabel = document.querySelector('#routeOriginLabel');
  const mobileToggle = document.querySelector('#mobileNavToggle');
  const siteNav = document.querySelector('#siteNav');
  const storageKey = 'oq-origin-city';

  const citySlug = city => (window.OQ_CITIES || []).find(item => item.city === city)?.slug || 'almaty';
  const slugCity = slug => (window.OQ_CITIES || []).find(item => item.slug === slug)?.city || 'Алматы';
  let origin = 'Алматы';
  try { origin = slugCity(localStorage.getItem(storageKey) || 'almaty'); } catch (_) {}
  if (cityPicker) cityPicker.value = citySlug(origin);

  function setOrigin(city, persist = true) {
    origin = city;
    if (persist) { try { localStorage.setItem(storageKey, citySlug(city)); } catch (_) {} }
    if (cityPicker) cityPicker.value = citySlug(city);
    if (originLabel) originLabel.textContent = city;
    document.querySelectorAll('[data-origin]').forEach(card => {
      card.hidden = card.dataset.origin !== citySlug(city);
    });
    if (from) {
      from.value = city;
      const options = Array.from(to.options);
      options.forEach(option => { option.disabled = option.value === city; });
      if (to.value === city) to.value = '';
      if (window.OQ_PRESELECT) {
        const route = routes.find(item => item.slug === window.OQ_PRESELECT.slug);
        if (route) {
          if (window.OQ_PRESELECT.direction === 'reverse') { from.value = route.city; to.value = 'Алматы'; }
          else { from.value = 'Алматы'; to.value = route.city; }
          origin = from.value;
        }
      }
    }
    if (to) to.value = '';
    calculate();
  }
  function populateVehicleOptions() {
    if (!truck || !bodyType || !bodySize) return;
    const vehicle = vehicles.find(item => item.id === truck.value) || vehicles[0];
    bodyType.innerHTML = `<option value="${vehicle.body}">${vehicle.body}</option>`;
    bodySize.innerHTML = vehicle.lengths.map(length => `<option value="${length}">${length}</option>`).join('');
  }
  function calculate() {
    if (!from || !to || !result) return;
    const routeOrigin = from.value;
    const routeDestination = to.value;
    const outbound = routeOrigin === 'Алматы' && routeDestination !== 'Алматы';
    const inbound = routeDestination === 'Алматы' && routeOrigin !== 'Алматы';
    const canonicalCity = outbound ? routeDestination : inbound ? routeOrigin : null;
    const route = routes.find(item => item.city === canonicalCity);
    const vehicle = vehicles.find(item => item.id === truck.value) || vehicles[0];
    if (!route && routeOrigin && routeDestination && routeOrigin !== routeDestination) {
      const direction = `${routeOrigin} → ${routeDestination}`;
      result.innerHTML = `<b>${direction}</b><br>${vehicle.label} · ${vehicle.body}<br><strong>Стоимость — по запросу</strong><br><span class="small-note">Маршрут добавлен. Расстояние, срок и ставка появятся после загрузки тарифной таблицы.</span>`;
      if (quickRoute) quickRoute.value = direction;
      if (order) order.href = `/?route=${encodeURIComponent(direction)}&vehicle=${encodeURIComponent(vehicle.label)}#quote`;
      return;
    }
    if (!route || routeOrigin === routeDestination) {
      result.textContent = 'Выберите разные города отправления и назначения.';
      if (order) order.dataset.request = '';
      return;
    }
    const direction = `${routeOrigin} → ${routeDestination}`;
    const dirKey = inbound ? 'reverse' : 'outbound';
    let price = route.vehiclePrices?.[dirKey]?.[vehicle.id];
    if (price === undefined && ['gazelle-15', 'gazelle-3'].includes(vehicle.id)) price = route.price;
    const body = `${vehicle.body}, ${bodySize.value}`;
    const discountText = returnTrip.value === 'yes' ? '<br><span class="small-note">Возможную скидку до 20% за обратную загрузку подтвердит менеджер.</span>' : '';
    result.innerHTML = price != null
      ? `<b>${direction}</b><br>${money(route.km)} км · ${route.time}<br>${vehicle.label} · ${body}<br><strong>от ${money(price)} ₸</strong><br><span class="small-note">Ставка маршрута для этого класса транспорта. Итог подтвердим по параметрам груза.</span>${discountText}`
      : `<b>${direction}</b><br>${money(route.km)} км · ${route.time}<br>${vehicle.label} · ${body}<br><strong>Стоимость — по запросу</strong><br><span class="small-note">Для этого сочетания маршрута и машины опубликованного тарифа нет. Подготовим индивидуальный расчёт.</span>${discountText}`;
    const routePath = `/gruzoperevozki/mezhgorod/${citySlug(routeOrigin)}-${citySlug(routeDestination)}/`;
    if (quickRoute) quickRoute.value = direction;
    if (order) {
      order.href = `/?route=${encodeURIComponent(direction)}&vehicle=${encodeURIComponent(vehicle.label)}&body=${encodeURIComponent(body)}#quote`;
      order.dataset.request = `${direction}; ${vehicle.label}; ${body}; ${price != null ? 'ориентир от ' + money(price) + ' ₸' : 'требуется индивидуальный расчёт'}; ${routePath}`;
    }
  }
  if (truck) {
    truck.addEventListener('change', () => { populateVehicleOptions(); calculate(); });
    populateVehicleOptions();
  }
  [from, to, bodyType, bodySize, returnTrip].filter(Boolean).forEach(el => el.addEventListener('change', () => {
    if (el === from) setOrigin(from.value);
    calculate();
  }));
  if (cityPicker) cityPicker.addEventListener('change', () => setOrigin(slugCity(cityPicker.value)));
  if (cityPicker) setOrigin(origin, false);
  if (window.OQ_PAGE_ROUTE && from && to) {
    from.value = window.OQ_PAGE_ROUTE.from;
    to.value = window.OQ_PAGE_ROUTE.to;
    setOrigin(from.value);
  }
  if (mobileToggle && siteNav) mobileToggle.addEventListener('click', () => {
    const expanded = mobileToggle.getAttribute('aria-expanded') === 'true';
    mobileToggle.setAttribute('aria-expanded', String(!expanded));
    siteNav.classList.toggle('mobile-open', !expanded);
  });
  document.querySelectorAll('[data-nav-group]').forEach(group => {
    const trigger = group.querySelector('.nav-trigger');
    const panel = group.querySelector('.mega-menu');
    const setOpen = open => { panel.hidden = !open; group.classList.toggle('is-open', open); trigger.setAttribute('aria-expanded', String(open)); };
    group.addEventListener('mouseenter', () => { if (matchMedia('(hover:hover)').matches) setOpen(true); });
    group.addEventListener('mouseleave', () => { if (matchMedia('(hover:hover)').matches) setOpen(false); });
    trigger.addEventListener('focus', () => setOpen(true));
    group.addEventListener('focusout', event => { if (!group.contains(event.relatedTarget)) setOpen(false); });
    trigger.addEventListener('click', event => {
      if (matchMedia('(hover:hover)').matches) return;
      event.preventDefault(); setOpen(panel.hidden);
    });
    group.addEventListener('keydown', event => { if (event.key === 'Escape') { setOpen(false); trigger.focus(); } });
  });
  const query = new URLSearchParams(location.search);
  if (quickRoute && query.has('route')) quickRoute.value = query.get('route');
  if (quickVehicle && query.has('vehicle')) quickVehicle.value = `${query.get('vehicle')}; ${query.get('body') || ''}`;
  document.querySelectorAll('.quote-form').forEach(form => form.addEventListener('submit', event => {
    event.preventDefault();
    const fields = new FormData(form);
    const text = `Здравствуйте, OQ SPEDITION!\n\nПрошу рассчитать перевозку.\nМаршрут: ${fields.get('route')}\nМашина: ${fields.get('vehicle') || 'нужно подобрать'}\nГруз: ${fields.get('cargo')}\nКонтакт: ${fields.get('contact')}`;
    location.href = `mailto:logistics@oqspedition.kz?subject=${encodeURIComponent('Запрос на перевозку: ' + fields.get('route'))}&body=${encodeURIComponent(text)}`;
  }));
  document.querySelectorAll('.landing-form').forEach(form => form.addEventListener('submit', event => {
    event.preventDefault();
    const fields = new FormData(form);
    const route = window.OQ_PAGE_ROUTE ? `${window.OQ_PAGE_ROUTE.from} → ${window.OQ_PAGE_ROUTE.to}` : 'маршрут со страницы';
    const text = `Здравствуйте, OQ SPEDITION!\n\nПрошу рассчитать перевозку.\nМаршрут: ${route}\nИмя: ${fields.get('name') || 'не указано'}\nТелефон: ${fields.get('phone')}\nГруз: ${fields.get('cargo') || 'нужно уточнить'}`;
    location.href = `mailto:logistics@oqspedition.kz?subject=${encodeURIComponent('Запрос на перевозку: ' + route)}&body=${encodeURIComponent(text)}`;
  }));
})();

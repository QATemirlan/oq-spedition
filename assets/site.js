'use strict';
(() => {
  const routes = window.OQ_ROUTES || [];
  const vehicles = window.OQ_VEHICLES || [];
  const basePath = window.OQ_BASE_PATH || '';
  const sitePath = path => `${basePath}${path}`;
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
       if (order) order.href = `${sitePath('/')}?route=${encodeURIComponent(direction)}&vehicle=${encodeURIComponent(vehicle.label)}#quote`;
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
    const routePath = sitePath(`/gruzoperevozki/mezhgorod/${citySlug(routeOrigin)}-${citySlug(routeDestination)}/`);
    if (quickRoute) quickRoute.value = direction;
    if (order) {
      order.href = `${sitePath('/')}?route=${encodeURIComponent(direction)}&vehicle=${encodeURIComponent(vehicle.label)}&body=${encodeURIComponent(body)}#quote`;
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
  const tariffRoutes = window.OQ_TARIFF_ROUTES || [];
  const tariffCities = window.OQ_TARIFF_CITIES || [];
  const tariffLimits = window.OQ_TARIFF_LIMITS || [1.5, 3, 5, 7, 10, 20];
  const tariffCityName = slug => tariffCities.find(item => item.slug === slug)?.city || slug;
  const tariffRoute = (fromSlug, toSlug) => tariffRoutes.find(item => item.from_slug === fromSlug && item.to_slug === toSlug);
  const tariffVehicle = limit => {
    if (limit <= 1.5) return 'Газель до 1,5 т';
    if (limit <= 3) return 'Газель до 3 т';
    if (limit <= 5) return 'Грузовик до 5 т';
    if (limit <= 10) return 'Грузовик до 10 т';
    return 'Фура до 20 т';
  };
  const selectTariffCategory = weightKg => {
    const tons = Number(weightKg) / 1000;
    if (!Number.isFinite(tons) || tons <= 0) return null;
    return tariffLimits.find(limit => tons <= limit) || null;
  };
  const calculateTariff = (fromSlug, toSlug, weightKg) => {
    const route = tariffRoute(fromSlug, toSlug);
    const category = selectTariffCategory(weightKg);
    if (!route || !category) return { route, category, price: null, vehicle: null };
    for (const limit of tariffLimits) {
      const price = route.prices?.[String(limit)];
      if (limit >= category && price) return { route, category: limit, price, vehicle: tariffVehicle(limit) };
    }
    return { route, category, price: null, vehicle: null };
  };
  document.querySelectorAll('[data-tariff-form]').forEach(form => {
    const fromSelect = form.querySelector('select[name="from"]');
    const toSelect = form.querySelector('select[name="to"]');
    const weightInput = form.querySelector('input[name="weight"]');
    const submit = form.querySelector('.tariff-calc-submit');
    const status = form.querySelector('[data-tariff-status]');
    const swap = form.querySelector('[data-tariff-swap]');
    function refreshState() {
      const weight = Number(weightInput?.value);
      const ready = Boolean(fromSelect?.value) && Boolean(toSelect?.value) && fromSelect.value !== toSelect.value && Number.isFinite(weight) && weight > 0;
      if (submit) submit.disabled = !ready;
      if (status && status.textContent && ready) status.textContent = '';
    }
    [fromSelect, toSelect, weightInput].filter(Boolean).forEach(el => el.addEventListener('input', refreshState));
    [fromSelect, toSelect].filter(Boolean).forEach(el => el.addEventListener('change', refreshState));
    if (swap && fromSelect && toSelect) swap.addEventListener('click', () => {
      const tmp = fromSelect.value;
      fromSelect.value = toSelect.value;
      toSelect.value = tmp;
      refreshState();
    });
    form.querySelectorAll('[data-quick-city]').forEach(button => button.addEventListener('click', () => {
      const target = button.closest('.tariff-calc-place');
      const select = target?.querySelector('select');
      if (!select) return;
      select.value = button.dataset.quickCity;
      refreshState();
    }));
    refreshState();
    form.addEventListener('submit', event => {
      event.preventDefault();
      const fromSlug = fromSelect?.value;
      const toSlug = toSelect?.value;
      const weight = Number(weightInput?.value);
      if (!fromSlug || !toSlug) { if (status) status.textContent = 'Выберите город отправления и назначения.'; return; }
      if (fromSlug === toSlug) { if (status) status.textContent = 'Выберите разные города.'; return; }
      if (!Number.isFinite(weight) || weight <= 0) { if (status) status.textContent = 'Укажите вес числом больше нуля.'; return; }
      if (status) status.textContent = 'Открываем расчёт...';
      const params = new URLSearchParams({ weight: String(Math.round(weight)) });
      location.href = `${sitePath(`/tarify/raschet/${fromSlug}-${toSlug}/`)}?${params.toString()}`;
    });
  });
  const tariffRows = Array.from(document.querySelectorAll('.tariff-main-table tbody tr'));
  const tariffEmpty = document.querySelector('#tariffEmpty');
  const tariffDropdowns = Array.from(document.querySelectorAll('[data-tariff-dropdown]'));
  function closeDropdowns(except) {
    tariffDropdowns.forEach(item => {
      if (item === except) return;
      item.classList.remove('is-open');
      const toggle = item.querySelector('[data-tariff-dropdown-toggle]');
      const panel = item.querySelector('.tariff-dropdown-panel');
      if (toggle) toggle.setAttribute('aria-expanded', 'false');
      if (panel) panel.hidden = true;
    });
  }
  tariffDropdowns.forEach(dropdown => {
    const toggle = dropdown.querySelector('[data-tariff-dropdown-toggle]');
    const panel = dropdown.querySelector('.tariff-dropdown-panel');
    const search = dropdown.querySelector('[data-tariff-dropdown-search]');
    const list = dropdown.querySelector('.tariff-dropdown-list');
    const label = dropdown.querySelector('[data-tariff-dropdown-label]');
    const input = dropdown.querySelector('[data-tariff-dropdown-input]');
    const defaultLabel = label ? label.textContent : 'Все города';
    if (toggle && panel) toggle.addEventListener('click', () => {
      const open = !panel.hidden;
      closeDropdowns(dropdown);
      panel.hidden = open;
      dropdown.classList.toggle('is-open', !open);
      toggle.setAttribute('aria-expanded', String(!open));
      if (!open && search) { search.value = ''; filterList(''); search.focus(); }
    });
    function filterList(text) {
      if (!list) return;
      const value = (text || '').trim().toLowerCase();
      list.querySelectorAll('li').forEach(item => { item.hidden = value !== '' && !item.textContent.toLowerCase().includes(value); });
    }
    if (search) search.addEventListener('input', () => filterList(search.value));
    if (list) list.addEventListener('click', event => {
      const option = event.target.closest('li');
      if (!option) return;
      if (input) input.value = option.dataset.value || '';
      if (label) label.textContent = option.textContent;
      dropdown.classList.toggle('is-set', Boolean(option.dataset.value));
      closeDropdowns();
      if (toggle) toggle.setAttribute('aria-expanded', 'false');
      if (panel) panel.hidden = true;
      filterTariffs();
    });
    dropdown.resetTariff = () => { if (input) input.value = ''; if (label) label.textContent = defaultLabel; dropdown.classList.remove('is-set'); };
  });
  document.addEventListener('click', event => { if (!event.target.closest('[data-tariff-dropdown]')) closeDropdowns(); });
  document.addEventListener('keydown', event => { if (event.key === 'Escape') closeDropdowns(); });
  function filterTariffs() {
    if (!tariffRows.length) return;
    const fromInput = document.querySelector('[data-tariff-dropdown] input[name="from"]');
    const toInput = document.querySelector('[data-tariff-dropdown] input[name="to"]');
    const fromValue = fromInput?.value || '';
    const toValue = toInput?.value || '';
    let visible = 0;
    tariffRows.forEach(row => {
      const fromOk = !fromValue || row.dataset.from === fromValue;
      const toOk = !toValue || row.dataset.to === toValue;
      const show = fromOk && toOk;
      row.hidden = !show;
      if (show) visible += 1;
    });
    if (tariffEmpty) tariffEmpty.hidden = visible !== 0;
  }
  const tariffReset = document.querySelector('[data-tariff-reset]');
  if (tariffReset) tariffReset.addEventListener('click', () => { tariffDropdowns.forEach(d => d.resetTariff && d.resetTariff()); if (tariffEmpty) tariffEmpty.hidden = true; filterTariffs(); });
  const resultBox = document.querySelector('[data-tariff-result]');
  if (resultBox && window.OQ_RESULT_ROUTE) {
    const weight = Number(query.get('weight'));
    const fromSlug = window.OQ_RESULT_ROUTE.from_slug;
    const toSlug = window.OQ_RESULT_ROUTE.to_slug;
    const routeName = `${tariffCityName(fromSlug)} → ${tariffCityName(toSlug)}`;
    if (!Number.isFinite(weight) || weight <= 0) {
      resultBox.innerHTML = '<strong>Некорректный вес</strong><p>Укажите вес в URL числом больше нуля, например <code>?weight=500</code>.</p>';
    } else {
      const calc = calculateTariff(fromSlug, toSlug, weight);
      const price = calc.price ? `${money(calc.price)} ₸` : 'Рассчитаем стоимость индивидуально';
      const vehicle = calc.vehicle || calc.route?.vehicle || 'подберём после заявки';
      const delivery = calc.route?.delivery_time || 'по согласованию';
      resultBox.innerHTML = `<dl><dt>Маршрут</dt><dd>${routeName}</dd><dt>Вес</dt><dd>${money(weight)} кг</dd><dt>Стоимость</dt><dd>${price}</dd><dt>Срок доставки</dt><dd>${delivery}</dd><dt>Рекомендуемый автомобиль</dt><dd>${vehicle}</dd></dl><div class="tariff-included"><b>Что входит в стоимость</b><span>Подбор транспорта</span><span>Маршрутный расчёт</span><span>Подача машины после согласования</span><span>Сопровождение менеджера</span></div><p class="small-note">Расчёт предварительный. Финальная ставка зависит от габаритов, адресов, режима загрузки, срочности и доступности транспорта.</p>`;
    }
  }
  if (quickRoute && query.has('route')) quickRoute.value = query.get('route');
  if (quickVehicle && query.has('vehicle')) quickVehicle.value = `${query.get('vehicle')}; ${query.get('body') || ''}`;
  document.querySelectorAll('.quote-form').forEach(form => form.addEventListener('submit', event => {
    event.preventDefault();
    const fields = new FormData(form);
    const text = `Здравствуйте, OQ SPEDITION!\n\nПрошу рассчитать перевозку.\nМаршрут: ${fields.get('route')}\nМашина: ${fields.get('vehicle') || 'нужно подобрать'}\nГруз: ${fields.get('cargo')}\nКонтакт: ${fields.get('contact')}`;
    location.href = `mailto:logistics@oqspedition.kz?subject=${encodeURIComponent('Запрос на перевозку: ' + fields.get('route'))}&body=${encodeURIComponent(text)}`;
  }));
  document.querySelectorAll('[data-tariff-request]').forEach(form => form.addEventListener('submit', event => {
    event.preventDefault();
    const fields = new FormData(form);
    const typedRoute = (fields.get('route') || '').trim();
    const route = typedRoute || (window.OQ_RESULT_ROUTE ? `${window.OQ_RESULT_ROUTE.from} → ${window.OQ_RESULT_ROUTE.to}` : document.querySelector('h1')?.textContent?.replace(/\s+/g, ' ') || 'тарифный маршрут');
    const weight = (fields.get('weight') || '').trim();
    const cargo = (fields.get('cargo') || '').trim() || weight || 'уточнить';
    const text = `Здравствуйте, OQ SPEDITION!\n\nПрошу подготовить точный расчёт.\nМаршрут: ${route}\nИмя: ${fields.get('name') || 'не указано'}\nТелефон: ${fields.get('phone')}\nГруз: ${cargo}`;
    location.href = `mailto:logistics@oqspedition.kz?subject=${encodeURIComponent('Точный расчёт тарифа: ' + route)}&body=${encodeURIComponent(text)}`;
  }));
  document.querySelectorAll('.landing-form:not([data-tariff-request])').forEach(form => form.addEventListener('submit', event => {
    event.preventDefault();
    const fields = new FormData(form);
    const route = window.OQ_PAGE_ROUTE ? `${window.OQ_PAGE_ROUTE.from} → ${window.OQ_PAGE_ROUTE.to}` : 'маршрут со страницы';
    const text = `Здравствуйте, OQ SPEDITION!\n\nПрошу рассчитать перевозку.\nМаршрут: ${route}\nИмя: ${fields.get('name') || 'не указано'}\nТелефон: ${fields.get('phone')}\nГруз: ${fields.get('cargo') || 'нужно уточнить'}`;
    location.href = `mailto:logistics@oqspedition.kz?subject=${encodeURIComponent('Запрос на перевозку: ' + route)}&body=${encodeURIComponent(text)}`;
  }));
})();

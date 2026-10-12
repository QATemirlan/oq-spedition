# -*- coding: utf-8 -*-
"""Generate the static OQ SPEDITION Kazakhstan freight website."""
from html import escape
from pathlib import Path
import json
import re
from route_data import CITIES_INFO, SEASONAL, TRANSPORT, PREPARE, QUESTIONS, ROAD_CHECK_INFO

ROOT = Path(__file__).parent
SITE_PREFIX = '/oq-spedition'
ROUTES = [
    ('Актау','aktau',2880,1080000,375,'3–4 дня'),('Актобе','aktobe',2185,720000,330,'2–3 дня'),
    ('Астана','astana',1200,400000,333,'1–2 дня'),('Атырау','atyrau',2850,940000,330,'3–4 дня'),
    ('Бишкек','bishkek',240,300000,1042,'1 день'),('Жезказган','zhezkazgan',1310,530000,405,'1–2 дня'),
    ('Караганда','karaganda',1000,420000,420,'1–2 дня'),('Кокшетау','kokshetau',1520,600000,395,'1–2 дня'),
    ('Конаев','konaev',78,44000,564,'в день в день'),('Костанай','kostanay',1930,710000,368,'2–3 дня'),
    ('Кызылорда','kyzylorda',1120,600000,536,'1–2 дня'),('Павлодар','pavlodar',1450,420000,290,'1–2 дня'),
    ('Петропавловск','petropavlovsk',1710,660000,386,'2–3 дня'),('Рудный','rudnyj',1965,730000,372,'2–3 дня'),
    ('Семей','semey',1125,410000,364,'1–2 дня'),('Талдыкорган','taldykorgan',260,140000,538,'в день в день'),
    ('Тараз','taraz',495,210000,424,'1 день'),('Ташкент','tashkent',815,380000,466,'1–2 дня'),
    ('Темиртау','temirtau',1030,430000,417,'1–2 дня'),('Туркестан','turkestan',830,370000,446,'1 день'),
    ('Уральск','uralsk',2660,1020000,383,'3–4 дня'),('Усть-Каменогорск','ust-kamenogorsk',1085,420000,387,'1–2 дня'),
    ('Шымкент','shymkent',685,300000,438,'1 день'),('Экибастуз','ekibastuz',1315,440000,335,'1–2 дня')]
SERVICES = [
    ('Автоперевозки по Казахстану','avtoperevozki','Организуем перевозки автомобильным транспортом между городами Казахстана. Подбор машины зависит от маршрута, веса, объёма и особенностей груза.'),
    ('Междугородние перевозки','mezhgorod','Перевозка грузов между Алматы и городами Казахстана. На странице направления опубликованы расстояние, ориентировочный срок и тариф на Газель.'),
    ('Газель для перевозки груза','gazel','Газель подходит для небольших партий, переездов и срочных отправок. Междугородние тарифы указаны на странице каждого маршрута.'),
    ('Сборные грузы','sbornye-gruzy','Возможность отправить часть машины можно обсудить с менеджером. Стоимость зависит от параметров и доступности попутного рейса.'),
    ('Перевозка фурой','fura','Перевозка крупных партий фурой по Казахстану. Тариф рассчитывается индивидуально по грузу, маршруту и условиям загрузки.'),
    ('Рефрижераторные перевозки','refrizherator','Перевозки с температурным режимом согласуются индивидуально с учётом требований к грузу и маршруту.'),
    ('Перевозка для бизнеса','biznes','Планирование перевозок для компаний: маршрут, транспорт, сопроводительные документы и условия взаимодействия согласуются до отправки.')]
VEHICLES = [
    {'id':'gazelle-15','label':'Газель до 1,5 т','capacity':'до 1,5 т','body':'Фургон / тент / борт','lengths':['3,2 м · S','3,8 м · M','4,2 м · L','5,2 м · XL','6,5 м · XXL'],'size':'до 12–18 м³','city_price':20000,'per_km':300,'category':'Газели'},
    {'id':'gazelle-3','label':'Газель до 3 т','capacity':'до 3 т','body':'Фургон / тент / борт','lengths':['3,8 м · M','4,2 м · L','5,2 м · XL','6,5 м · XXL'],'size':'до 16–20 м³','city_price':30000,'per_km':450,'category':'Газели'},
    {'id':'truck-5','label':'Грузовик до 5 т','capacity':'до 5 т','body':'Фургон / тент / борт','lengths':['4,2 м','5,2 м','6,5 м'],'size':'до 30 м³','city_price':40000,'per_km':500,'category':'Грузовики'},
    {'id':'truck-8','label':'Грузовик до 8 т','capacity':'до 8 т','body':'Фургон / тент / борт','lengths':['6,5 м'],'size':'до 40 м³','city_price':60000,'per_km':525,'category':'Грузовики'},
    {'id':'truck-12','label':'Грузовик до 12 т','capacity':'до 12 т','body':'Тент / борт','lengths':['6,5 м'],'size':'до 45 м³','city_price':80000,'per_km':550,'category':'Грузовики'},
    {'id':'dump-15','label':'Самосвал 7–20 т','capacity':'7–20 т','body':'Самосвальный кузов','lengths':['10–14 м³','до 27 м³'],'size':'сыпучий груз','city_price':None,'per_km':None,'category':'Грузовики'},
    {'id':'semi-20','label':'Фура до 20 т','capacity':'до 20 т','body':'Тент / борт','lengths':['13,6 м'],'size':'до 82–90 м³ · 33 паллеты','city_price':85000,'per_km':830,'category':'Фуры'},
    {'id':'reefer-gazelle','label':'Рефрижератор · Газель','capacity':'до 1,5–3 т','body':'Рефрижератор','lengths':['3,8–6,5 м'],'size':'температурный режим','city_price':None,'per_km':None,'category':'Рефрижераторы'},
    {'id':'reefer-8','label':'Рефрижератор до 8 т','capacity':'до 8 т','body':'Рефрижератор','lengths':['по запросу'],'size':'температурный режим','city_price':None,'per_km':None,'category':'Рефрижераторы'},
    {'id':'semi-reefer','label':'Фура-рефрижератор 20 т','capacity':'до 20 т','body':'Рефрижератор','lengths':['13,6 м'],'size':'до 82 м³ · температурный режим','city_price':None,'per_km':600,'category':'Рефрижераторы'},
    {'id':'lowbed','label':'Трал / негабарит','capacity':'до 40 т','body':'Низкорамная платформа','lengths':['по параметрам груза'],'size':'негабарит','city_price':250000,'per_km':1200,'category':'Тралы'}
]
# Тарифы со страниц конкретных маршрутов имеют приоритет над общими ценами.
# Остальные классы показываются как расчёт по запросу, если на странице маршрута нет опубликованной ставки.
ROUTE_VEHICLE_PRICES = {
    'astana': {
        'outbound': {'gazelle-15':350000,'gazelle-3':350000,'reefer-gazelle':450000,'semi-20':1000000,'reefer-8':730000,'lowbed':1470000},
        'reverse': {'gazelle-15':None,'gazelle-3':None,'reefer-gazelle':None,'semi-20':None,'reefer-8':None,'lowbed':None}
    }
}
fmt=lambda n: f'{n:,}'.replace(',', ' ')
base='https://oqspedition.kz'
CITY_LIST=[('Алматы','almaty')]+[(r[0],r[1]) for r in ROUTES]
CITY_BY_SLUG={slug:city for city,slug in CITY_LIST}
CITY_SLUG={city:slug for city,slug in CITY_LIST}
def city_path(origin_slug,dest_slug): return f'/gruzoperevozki/mezhgorod/{origin_slug}-{dest_slug}/'
NAV_ITEMS=[
    ('Грузоперевозки','/gruzoperevozki/',[
        ('По городу','/gruzoperevozki/'),('Междугородние перевозки','/gruzoperevozki/mezhgorod/'),
        ('Сборные грузы','/uslugi/sbornye-gruzy/'),('Перевозка грузов для бизнеса','/biznes/')]),
    ('Автопарк','/avtopark/',[(v['label'],f'/avtopark/{v["id"]}/') for v in VEHICLES]),
    ('Направления','/gruzoperevozki/mezhgorod/',[(city,city_path('almaty',slug)) for city,slug in CITY_LIST[1:9]]),
    ('Услуги','/uslugi/',[(name,f'/uslugi/{slug}/') for name,slug,_ in SERVICES]),
    ('Бизнесу','/biznes/',[('Логистика для бизнеса','/biznes/'),('Автопарк','/avtopark/'),('Цены','/ceny/')])
]
def make_nav():
    groups=[]
    for i,(label,url,links) in enumerate(NAV_ITEMS):
        children=''.join(f'<a href="{href}">{escape(text)}</a>' for text,href in links)
        groups.append(f'<div class="nav-group" data-nav-group><a class="nav-trigger" href="{url}" aria-haspopup="true" aria-expanded="false" aria-controls="mega-{i}">{label}<span aria-hidden="true">⌄</span></a><div class="mega-menu" id="mega-{i}" hidden><div class="mega-heading"><b>{label}</b><a href="{url}">Все разделы →</a></div><div class="mega-links">{children}</div></div></div>')
    city_options=''.join(f'<option value="{slug}">{escape(city)}</option>' for city,slug in CITY_LIST)
    groups.append(f'<label class="city-picker"><span>Ваш город</span><select id="headerCity" aria-label="Выберите город отправления">{city_options}</select></label>')
    return ''.join(groups)
nav=make_nav()
def head(title,description,path):
     return f'''<!doctype html><html lang="ru"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1"><meta name="theme-color" content="#101b28"><meta name="description" content="{escape(description, quote=True)}"><link rel="canonical" href="{base}{path}"><meta property="og:type" content="website"><meta property="og:title" content="{escape(title)}"><meta property="og:description" content="{escape(description)}"><title>{escape(title)}</title><link rel="stylesheet" href="/assets/site.css"><link rel="stylesheet" href="/assets/route.css"><link rel="stylesheet" href="/assets/interactions.css"><link rel="stylesheet" href="/assets/mobile.css"><script>window.OQ_BASE_PATH={json.dumps(SITE_PREFIX)};</script><script src="/routes.js" defer></script><script src="/assets/site.js" defer></script></head><body><header class="header"><div class="container header-inner"><a class="brand brand-logo" href="/"><img src="/assets/logo.svg" alt="OQ SPEDITION"></a><button class="mobile-nav-toggle" id="mobileNavToggle" aria-expanded="false" aria-controls="siteNav">Меню ☰</button><nav id="siteNav" aria-label="Основная навигация">{nav}<a class="button nav-quote" href="/#quote">Рассчитать</a></nav></div></header>'''
def footer():
     return '''<footer class="footer"><div class="container footer-grid"><div><a class="brand brand-logo" href="/"><img src="/assets/logo.svg" alt="OQ SPEDITION"></a><p>Транспортная логистика по Казахстану.</p></div><div><b>Связаться</b><p><a href="tel:+77088462330">+7 708 846 23 30</a></p><p><a href="mailto:logistics@oqspedition.kz">logistics@oqspedition.kz</a></p></div><div><b>Навигация</b><p><a href="/gruzoperevozki/mezhgorod/">Направления и тарифы</a></p><p><a href="/uslugi/">Услуги</a></p></div></div></footer></body></html>'''
def route_url(slug,reverse=False): return f'/gruzoperevozki/mezhgorod/{slug}-almaty/' if reverse else f'/gruzoperevozki/mezhgorod/almaty-{slug}/'
def route_card(r,reverse=False):
    city,slug,km,price,rate,time=r; a,b=(city,'Алматы') if reverse else ('Алматы',city)
    return f'<a class="card" href="{route_url(slug,reverse)}"><h3>{a} → {b}</h3><p>{fmt(km)} км · {time}</p><p class="price">от {fmt(price)} ₸</p><span class="small-note">Газель, цена за рейс · Подробнее →</span></a>'
def route_price(route, vehicle, reverse=False):
    direction='reverse' if reverse else 'outbound'
    explicit=ROUTE_VEHICLE_PRICES.get(route[1],{}).get(direction,{})
    if vehicle['id'] in explicit:
        return explicit[vehicle['id']]
    if vehicle['id'] in ('gazelle-15','gazelle-3'):
        return route[3]
    return None
def calc(route=None):
    selected=''
    if route:
        direction='reverse' if route[0] else 'outbound'; item=route[1]
        origin,destination=(item[0],'Алматы') if route[0] else ('Алматы',item[0])
        selected=f'<script>window.OQ_PAGE_ROUTE={json.dumps({"from":origin,"to":destination},ensure_ascii=False)};</script>'
    vehicle_options=''.join(f'<option value="{v["id"]}">{v["label"]}</option>' for v in VEHICLES)
    city_options=''.join(f'<option value="{slug}">{escape(city)}</option>' for city,slug in CITY_LIST)
    return f'''{selected}<section class="section feature-band" id="calculator"><div class="container"><p class="eyebrow">КАЛЬКУЛЯТОР МЕЖГОРОДА</p><h2>Рассчитайте стоимость перевозки</h2><p class="muted">Выберите город отправления, город назначения, грузоподъёмность, кузов и размер. Для маршрутов без опубликованного тарифа подготовим расчёт по запросу.</p><div class="calc"><div class="calc-grid"><label class="field">Откуда<select id="fromCity">{city_options}</select></label><label class="field">Куда<select id="toCity"><option value="">Выберите город назначения</option>{city_options}</select></label><label class="field">Грузоподъёмность / машина<select id="truck">{vehicle_options}</select></label><label class="field">Тип кузова<select id="bodyType"><option value="all">Любой</option></select></label><label class="field">Размер кузова<select id="bodySize"><option value="all">Любой размер</option></select></label><label class="field">Обратная загрузка<select id="returnTrip"><option value="no">Нет</option><option value="yes">Проверить скидку до 20%</option></select></label></div><div class="result" id="calcResult" aria-live="polite">Выберите маршрут и машину, чтобы увидеть доступный тариф.</div><p class="small-note">Тарифы за маршрут приоритетнее общих расценок автопарка. Для машин без опубликованной цены подготовим индивидуальный расчёт.</p><a class="button" id="calcOrder" href="/#quote">Запросить расчёт</a></div></div></section>'''
faq='''<section class="section faq"><div class="container"><p class="eyebrow">ВОПРОСЫ</p><h2>Часто спрашивают о междугородней перевозке</h2><details><summary>Цена на странице окончательная?</summary><p>На сайте показан тариф «от» за Газель по направлению. Итоговая стоимость подтверждается после уточнения груза, адресов и условий рейса.</p></details><details><summary>Можно отправить груз в обратном направлении?</summary><p>Да, для маршрутов опубликованы страницы в обе стороны. Стоимость обратной загрузки уточняется по наличию подходящего рейса.</p></details><details><summary>Сколько занимает доставка?</summary><p>Ориентировочный срок указан на странице направления. Фактическое время зависит от маршрута, дорожной обстановки и организации загрузки.</p></details><details><summary>Как рассчитывается цена фуры?</summary><p>Для грузовиков, фур и специальных типов кузова стоимость предоставляется по запросу с учётом параметров перевозки.</p></details></div></section>'''

def write(path,content):
    target=ROOT/path; target.parent.mkdir(parents=True,exist_ok=True)
    if target.suffix == '.html' and SITE_PREFIX:
        content = content.replace('href="/', f'href="{SITE_PREFIX}/').replace('src="/', f'src="{SITE_PREFIX}/')
    target.write_text(content,encoding='utf-8')

route_js = '/* Маршрутные тарифы по согласованным исходным данным; маршрутные ставки приоритетнее. */\nwindow.OQ_ROUTES = ' + json.dumps([{'city':c,'slug':s,'km':km,'price':price,'rate':rate,'time':time,'international':s in ('bishkek','tashkent'), 'vehiclePrices':ROUTE_VEHICLE_PRICES.get(s,{} )} for c,s,km,price,rate,time in ROUTES],ensure_ascii=False,indent=2) + ';\nwindow.OQ_VEHICLES = ' + json.dumps(VEHICLES,ensure_ascii=False,indent=2) + ';\n'
route_js += 'window.OQ_CITIES = ' + json.dumps([{'city':c,'slug':s} for c,s in CITY_LIST],ensure_ascii=False,indent=2) + ';\n'
write(Path('routes.js'),route_js)

def shell(title,description,path,body): return head(title,description,path)+'<main>'+body+'</main>'+footer()

vehicle_cards=''.join(f'<a class="card vehicle-card" href="/avtopark/{v["id"]}/"><span class="tag">{v["category"]}</span><h3>{v["label"]}</h3><p>{v["capacity"]} · {v["size"]}</p><p>{v["body"]} · {", ".join(v["lengths"])}</p><p class="price">{("от "+fmt(v["city_price"])+" ₸ по городу") if v["city_price"] else "Тариф по запросу"}</p></a>' for v in VEHICLES)
fleet_body=f'<section class="section"><div class="container"><div class="crumbs"><a href="/">Главная</a> / Автопарк</div><p class="eyebrow">ТРАНСПОРТ</p><h1>Подбор машины под груз и маршрут</h1><p class="muted">Выберите грузоподъёмность, тип кузова и размер. Междугородние тарифы показываем на странице выбранного маршрута.</p><div class="service-list">{vehicle_cards}</div><p style="margin-top:24px"><a class="button" href="/gruzoperevozki/mezhgorod/">Выбрать направление</a></p></div></section>'
write(Path('avtopark/index.html'),shell('Автопарк грузовых машин — OQ SPEDITION','Газели, грузовики, фуры, рефрижераторы и самосвалы: характеристики, типы кузова, размеры и тарифы.','/avtopark/',fleet_body))
for vehicle in VEHICLES:
    city_price=f'<p class="price">от {fmt(vehicle["city_price"])} ₸ по городу</p>' if vehicle['city_price'] else '<p class="price">Цена по запросу</p>'
    km_price=f'<p>{fmt(vehicle["per_km"])} ₸/км — общий тарифный ориентир по Алматы</p>' if vehicle['per_km'] else ''
    body=f'<section class="hero"><div class="container"><p class="eyebrow">АВТОПАРК OQ SPEDITION</p><h1>{vehicle["label"]}</h1><p class="lead">{vehicle["capacity"]} · {vehicle["body"]} · {vehicle["size"]}.</p><a class="button" href="/#quote">Запросить расчёт</a></div></section><section class="section"><div class="container grid"><article class="card"><h3>Тип кузова</h3><p>{vehicle["body"]}</p></article><article class="card"><h3>Доступные размеры</h3><p>{", ".join(vehicle["lengths"])}</p></article><article class="card"><h3>Грузоподъёмность</h3><p>{vehicle["capacity"]}</p></article></div></section><section class="section feature-band"><div class="container"><h2>Ориентир по стоимости</h2>{city_price}{km_price}<p class="muted">Для межгорода проверяйте цену на странице конкретного направления: там при наличии используется отдельная маршрутная ставка. Если опубликованного значения нет — расчёт по запросу.</p><a class="button" href="/gruzoperevozki/mezhgorod/">Выбрать маршрут</a></div></section>'
    write(Path(f'avtopark/{vehicle["id"]}/index.html'),shell(f'{vehicle["label"]}: характеристики и цена | OQ SPEDITION',f'{vehicle["label"]}: грузоподъёмность {vehicle["capacity"]}, кузов {vehicle["body"]}, размеры и расчёт маршрута.','/avtopark/'+vehicle['id']+'/',body))

write(Path('gruzoperevozki/index.html'),shell('Грузоперевозки по Казахстану — OQ SPEDITION','Грузовые перевозки по Казахстану: Газели, грузовики, фуры, рефрижераторы, маршрутный калькулятор и доставка по городам.','/gruzoperevozki/','<section class="hero"><div class="container"><p class="eyebrow">OQ SPEDITION</p><h1>Грузоперевозки по Казахстану</h1><p class="lead">Подберите автомобиль по направлению, весу, кузову и размерам груза.</p><a class="button" href="/gruzoperevozki/mezhgorod/">Рассчитать межгород</a></div></section><section class="section"><div class="container"><h2>Транспорт для перевозки</h2><div class="service-list">'+vehicle_cards+'</div></div></section><section class="section feature-band"><div class="container"><h2>Услуги перевозки</h2><div class="service-list">'+''.join(f'<a class="card" href="/uslugi/{s}/"><h3>{n}</h3><p>{escape(d)}</p></a>' for n,s,d in SERVICES)+'</div></div></section>'))

business_body='''<section class="hero"><div class="container"><p class="eyebrow">OQ SPEDITION · B2B</p><h1>Транспортная логистика для бизнеса</h1><p class="lead">Регулярные и разовые грузовые перевозки по Казахстану. Согласуем маршрут, транспорт, график и пакет документов.</p><a class="button" href="/#quote">Запросить коммерческий расчёт</a></div></section><section class="section"><div class="container"><h2>Для каких задач подходит</h2><div class="grid"><article class="card"><h3>Регулярные поставки</h3><p>Планирование повторяющихся рейсов и перевозок между городами.</p></article><article class="card"><h3>Доставка между складами</h3><p>Подбор машины по грузоподъёмности, кузову, объёму и маршруту.</p></article><article class="card"><h3>Коммерческие грузы</h3><p>Запрос расчёта перевозки с документами и согласованными условиями.</p></article></div></div></section><section class="section feature-band"><div class="container"><h2>Данные для расчёта</h2><p>Направление, тип груза, вес, объём, тип кузова, желаемая дата и контакт ответственного лица.</p><a class="button" href="/#quote">Оставить запрос</a></div></section>'''
write(Path('biznes/index.html'),shell('Грузоперевозки для бизнеса — OQ SPEDITION','Транспортные перевозки для компаний по Казахстану: регулярные рейсы, доставка между складами и коммерческие грузы.','/biznes/',business_body))

homebody=f'''<section class="hero"><div class="container hero-grid"><div><p class="eyebrow">OQ SPEDITION · КАЗАХСТАН</p><h1>Грузоперевозки<br><span>по Казахстану</span></h1><p class="lead">Подбираем транспорт под маршрут, тоннаж, тип кузова и габариты груза. Межгород из Алматы и в обратном направлении.</p><div class="hero-points"><span>24 направления из Алматы</span><span>Газели · грузовики · фуры</span><span>Рефрижераторные перевозки</span></div><a class="button" href="/gruzoperevozki/mezhgorod/">Выбрать направление →</a></div><div class="hero-panel" id="quote"><h2>Запросить перевозку</h2><p class="muted">Заполните маршрут и груз — подготовим письмо менеджеру.</p><form class="quote-form"><label class="field">Маршрут<input name="route" id="quickRoute" placeholder="Алматы → Актобе" required></label><label class="field">Машина<input name="vehicle" id="quickVehicle" placeholder="Можно оставить пустым"></label><label class="field">Груз<input name="cargo" placeholder="Что и в каком объёме перевозим?" required></label><label class="field">Телефон или email<input name="contact" required placeholder="Ваш контакт"></label><button class="button">Подготовить запрос</button><p class="small-note">Форма создаёт письмо в вашей почте и не отправляет данные автоматически.</p></form></div></div></section><section class="section"><div class="container"><p class="eyebrow">АВТОПАРК</p><h2>Машина под вес, объём и условия перевозки</h2><div class="service-list">{''.join(f'<a class="card" href="/avtopark/{v["id"]}/"><h3>{v["label"]}</h3><p>{v["capacity"]} · {v["body"]}</p><span class="small-note">{", ".join(v["lengths"])} · Подробнее →</span></a>' for v in VEHICLES[:8])}</div><p style="margin-top:24px"><a class="button" href="/avtopark/">Весь автопарк →</a></p></div></section><section class="section feature-band"><div class="container"><p class="eyebrow">МАРШРУТЫ</p><h2>Популярные направления из Алматы</h2><div class="grid">{''.join(route_card(x) for x in [ROUTES[1],ROUTES[2],ROUTES[3],ROUTES[16],ROUTES[22],ROUTES[0]])}</div><p style="margin-top:24px"><a class="button" href="/gruzoperevozki/mezhgorod/">Все направления и тарифы →</a></p></div></section><section class="section"><div class="container"><p class="eyebrow">УСЛУГИ</p><h2>Перевозки по задачам бизнеса</h2><div class="service-list">{''.join(f'<a class="card" href="/uslugi/{slug}/"><h3>{name}</h3><p>{escape(desc[:125])}…</p><span class="tag">Подробнее →</span></a>' for name,slug,desc in SERVICES)}</div></div></section><section class="section feature-band"><div class="container"><h2>Логистика для компаний</h2><p class="muted">Регулярные рейсы, доставка между складами и расчёт коммерческих перевозок по Казахстану.</p><a class="button" href="/biznes/">Решения для бизнеса →</a></div></section>'''
write(Path('index.html'),shell('Грузоперевозки по Казахстану — OQ SPEDITION','Междугородние грузоперевозки по Казахстану: направления из Алматы и обратно, тарифы и расчёт перевозки.','/',homebody))

cards=''.join(route_card(x) for x in ROUTES)
reversecards=''.join(route_card(x,True) for x in ROUTES)
table=''.join(f'<tr><td><a href="{route_url(x[1])}">Алматы → {x[0]}</a><br><a class="small-note" href="{route_url(x[1],True)}">{x[0]} → Алматы</a></td><td>{fmt(x[2])} км</td><td>{fmt(x[3])} ₸</td><td>{x[4]} ₸/км</td><td>{x[5]}</td></tr>' for x in ROUTES)
route_cards_all=''.join(f'<a class="card route-choice" data-origin="{origin_slug}" href="{city_path(origin_slug,dest_slug)}"><h3>{origin} → {dest}</h3><p class="price">{(f"от {fmt(next(r[3] for r in ROUTES if r[1]==dest_slug))} ₸ за Газель") if origin=="Алматы" else "Стоимость по запросу"}</p><span class="small-note">{(f"{next(r[5] for r in ROUTES if r[1]==dest_slug)} · {fmt(next(r[2] for r in ROUTES if r[1]==dest_slug))} км") if origin=="Алматы" else "Рассчитать направление →"}</span></a>' for origin,origin_slug in CITY_LIST for dest,dest_slug in CITY_LIST if origin!=dest)
hubbody=f'''<div class="container crumbs"><a href="/">Главная</a> / Межгород по Казахстану</div><section class="hero"><div class="container"><p class="eyebrow">OQ SPEDITION · МАРШРУТЫ</p><h1>Междугородние грузоперевозки<br><span>по Казахстану</span></h1><p class="lead">Выберите город отправления в шапке — список направлений и калькулятор обновятся автоматически.</p><a class="button" href="#calculator">Рассчитать маршрут ↓</a></div></section>{calc()}<section class="section"><div class="container"><p class="eyebrow">ГОРОД ОТПРАВЛЕНИЯ</p><h2>Направления из <span id="routeOriginLabel">Алматы</span></h2><p class="muted">Выберите город в верхней части сайта, чтобы показать направления из него.</p><div class="grid route-city-list">{route_cards_all}</div></div></section><section class="section feature-band"><div class="container"><h2>Опубликованные тарифы из Алматы</h2><div class="route-table-wrap"><table class="route-table"><thead><tr><th>Направление</th><th>Расстояние</th><th>Газель, от</th><th>Цена/км</th><th>Срок</th></tr></thead><tbody>{table}</tbody></table></div><p class="small-note">Для маршрутов без подтверждённых тарифов стоимость и срок отображаются как «по запросу». Таблица цен дополнится после получения вашей тарифной базы.</p></div></section>{faq}'''
write(Path('gruzoperevozki/mezhgorod/index.html'),shell('Межгородние перевозки по Казахстану — OQ SPEDITION','Междугородние грузоперевозки из Алматы и в Алматы: маршруты, расстояния, сроки и тарифы Газели.','/gruzoperevozki/mezhgorod/',hubbody))

def quote_form(origin, dest):
    return f'''<form class="landing-form"><h2>Заказать сейчас</h2><p>Оставьте данные — подготовим расчёт по маршруту {origin} — {dest}.</p><label class="field">Ваше имя<input name="name" placeholder="Как к вам обращаться?"></label><label class="field">Телефон<input name="phone" placeholder="+7 ..." required></label><label class="field">Груз<input name="cargo" placeholder="Что перевозим?"></label><button class="button">Получить расчёт</button><span class="small-note">Форма подготовит письмо менеджеру OQ SPEDITION.</span></form>'''

def route_facts(km, time):
    if not km:
        return ('расстояние уточняется','по запросу','по запросу')
    hours_min=max(1,round(km/85))
    hours_max=max(hours_min+1,round(km/75))
    return (f'{fmt(km)} км',f'{hours_min}–{hours_max} часов в пути',time)

def route_price_table(page_prices):
    rows=[]
    for v,p in page_prices:
        person='по запросу' if p is None else f'от {fmt(p)} ₸'
        business='по запросу' if p is None else f'от {fmt(round(p*1.25/1000)*1000)} ₸'
        rows.append(f'<tr><td><b>{escape(v["label"])}</b><span>{escape(v["capacity"])} · {escape(v["size"])}</span></td><td>{person}</td><td>{business}</td></tr>')
    return ''.join(rows)

def route_sections(origin, origin_slug, dest, dest_slug, route, page_prices, opposite, calculator):
    km,_,rate,time=(route[2],route[3],route[4],route[5]) if route else (None,None,None,'по запросу')
    gazelle_price=next((p for v,p in page_prices if v['id'] in ('gazelle-15','gazelle-3') and p is not None),None)
    distance_text,drive_time,delivery_time=route_facts(km,time)
    route_price='по запросу' if gazelle_price is None else f'от {fmt(gazelle_price)} ₸'
    origin_info=CITIES_INFO.get(origin,{})
    dest_info=CITIES_INFO.get(dest,{})
    season_key=dest_slug if origin=='Алматы' else origin_slug if dest=='Алматы' else None
    season_text=SEASONAL.get(season_key,'Перед рейсом проверяем погодные условия, состояние дорог и ограничения движения. Срок доставки зависит от маршрута, сезона и режима загрузки.')
    road_src=ROAD_CHECK_INFO['sources'][0] if ROAD_CHECK_INFO['sources'] else None
    road_link=f'<a href="{road_src[1]}" target="_blank" rel="noopener">{road_src[0]}</a>' if road_src and road_src[1] else '<span>официальные дорожные источники</span>'
    price_rows=route_price_table(page_prices)
    cargo_cards=[
        ('Переезды и мебель','Квартирные, офисные и складские переезды: мебель, техника, личные вещи, упаковка.'),
        ('Товары и паллеты','Коммерческие партии, коробки, паллеты, маркетплейсы, розница и оптовые поставки.'),
        ('Оборудование и стройматериалы','Станки, витрины, инструмент, сухие смеси, материалы и комплектующие.'),
        ('Сборные грузы','Отправка части машины от 120 ₸/кг, если есть подходящая консолидация на направление.'),
    ]
    cargo_icons=['⌂','▦','⚙','↔']
    cargo_html=''.join(f'<article><span class="landing-icon">{cargo_icons[i]}</span><h3>{escape(t)}</h3><p>{escape(d)}</p></article>' for i,(t,d) in enumerate(cargo_cards))
    steps=[('01','Заявка','Маршрут, груз, адреса, дата и контакт ответственного лица.'),('02','Расчёт','Подбираем машину и подтверждаем стоимость до подачи.'),('03','Подача','Машина приезжает на согласованную точку загрузки.'),('04','Доставка','Везём груз по маршруту с учётом дорожной обстановки.'),('05','Закрытие','Подтверждаем выгрузку и передаём документы при необходимости.')]
    steps_html=''.join(f'<article><span class="step-icon">{n}</span><h3>{escape(t)}</h3><p>{escape(d)}</p></article>' for n,t,d in steps)
    vehicles=[
        ('Газель','до 1,5–3 т','12–20 м³','Небольшие партии, срочная доставка, переезды.'),
        ('Грузовик 3–5 т','до 5 т','до 30 м³','Оборудование, товары, стройматериалы.'),
        ('Грузовик 8–12 т','до 12 т','до 45 м³','Крупные партии и коммерческие грузы.'),
        ('Фура 20 т','до 20 т','82–90 м³','Паллеты, опт, длинные межгородние рейсы.'),
        ('Рефрижератор','1,5–20 т','температурный режим','Продукты, лекарства и чувствительные грузы.'),
    ]
    vehicle_icons=['▣','▤','▥','▰','◇']
    vehicle_html=''.join(f'<article><span class="vehicle-icon">{vehicle_icons[i]}</span><h3>{escape(t)}</h3><b>{escape(w)}</b><p>{escape(vol)}</p><small>{escape(use)}</small></article>' for i,(t,w,vol,use) in enumerate(vehicles))
    questions=[
        (f'Сколько стоит перевозка {origin} — {dest}?',f'Ориентир по Газели — {route_price}. Итоговая цена зависит от веса, объёма, типа кузова, адресов и условий загрузки.'),
        ('Есть ли сборный груз?',f'Да, сборный груз по направлению рассчитываем от 120 ₸/кг при наличии подходящей консолидации. Для партий до 2 т это часто дешевле целой машины.'),
        ('Сколько занимает доставка?',f'Ориентировочный срок — {delivery_time}. Фактическое время зависит от погоды, дорожной обстановки и режима погрузки.'),
        ('Можно отправить в обратном направлении?','Да, обратное направление доступно на отдельной странице. При наличии обратной загрузки возможна скидка до 20%.'),
        ('Какие документы нужны?','Для бизнеса можем подготовить счёт, договор, ТТН и закрывающие документы. Состав документов согласуется до рейса.'),
    ]
    faq_html=''.join(f'<details><summary>{escape(q)}</summary><p>{escape(a)}</p></details>' for q,a in questions)
    other=[(c,s) for c,s in CITY_LIST if s not in (origin_slug,dest_slug)][:10]
    other_links=''.join(f'<a href="{city_path(origin_slug,s)}">{origin} — {escape(c)}</a>' for c,s in other)
    prep_items=''.join(f'<li>{escape(item)}</li>' for item in PREPARE[:4])
    origin_text=' '.join(origin_info.get('items',[])[:2]) or f'{origin} — город отправления по маршруту.'
    dest_text=' '.join(dest_info.get('items',[])[:2]) or f'{dest} — город назначения по маршруту.'
    return f'''
<section class="landing-intro"><div class="container narrow"><p class="eyebrow">МАРШРУТ ПО КАЗАХСТАНУ</p><h2>{origin} — {dest}: перевозка груза отдельной машиной или сборной отправкой</h2><p>{escape(origin_text)} {escape(dest_text)}</p><div class="intro-grid"><article><span class="landing-icon">₸</span><b>Фиксированная ставка</b><span>Цена рейса известна до подачи машины.</span></article><article><span class="landing-icon">▰</span><b>Машина под объём</b><span>Газель, грузовик, фура, рефрижератор или трал.</span></article><article><span class="landing-icon">▤</span><b>Документы</b><span>Договор, ТТН, счёт и закрывающие документы для бизнеса.</span></article><article><span class="landing-icon">◆</span><b>Контроль рейса</b><span>Согласуем адреса, сроки, кузов и условия загрузки заранее.</span></article></div></div></section>
<section class="section landing-price"><div class="container"><div class="center-heading"><p class="eyebrow">СТОИМОСТЬ РЕЙСА</p><h2>Цены на перевозку {origin} — {dest}</h2><p>Фиксированная цена за рейс в одну сторону. Сборный груз и обратная загрузка считаются отдельно.</p></div><div class="price-table-wrap"><table class="landing-table"><thead><tr><th>Тип машины</th><th>Физлицо</th><th>Юрлицо</th></tr></thead><tbody>{price_rows}</tbody></table></div><p class="table-note">Физлицам — ориентир за рейс. Юрлицам — расчёт с документами. Обратная загрузка {dest} — {origin} может быть дешевле при наличии подходящего рейса.</p></div></section>
<section class="section groupage"><div class="container groupage-grid"><div><p class="eyebrow">СБОРНЫЙ ГРУЗ</p><h2>Отправка от 120 ₸/кг</h2><p>Если не нужна целая машина, проверим сборную отправку по маршруту {origin} — {dest}. Груз консолидируется с другими отправками, поэтому цена для партии до 2 тонн часто ниже отдельной Газели.</p></div><div class="compare-box"><table><thead><tr><th>Партия</th><th>Сборный груз</th><th>Целая Газель</th></tr></thead><tbody><tr><td>100 кг</td><td>от 120 ₸/кг</td><td>{route_price}</td></tr><tr><td>500 кг</td><td>от 120 ₸/кг</td><td>{route_price}</td></tr><tr><td>2 тонны</td><td>индивидуально</td><td>{route_price}</td></tr></tbody></table><p>Для срочных грузов и адресной подачи лучше отдельная машина.</p></div></div></section>
{calculator}
<section class="section cargo-types"><div class="container"><div class="center-heading"><p class="eyebrow">ЧТО ВОЗИМ</p><h2>Грузы на маршруте {origin} — {dest}</h2></div><div class="cargo-grid">{cargo_html}</div></div></section>
<section class="section order-steps"><div class="container"><div class="center-heading"><p class="eyebrow">КАК ЗАКАЗАТЬ РЕЙС</p><h2>Пять шагов до доставки</h2></div><div class="steps-grid">{steps_html}</div></div></section>
<section class="section route-timing"><div class="container timing-grid"><div><p class="eyebrow">МАРШРУТ И СРОКИ</p><h2>Плечо {origin} — {dest}</h2><p>{escape(season_text)}</p><p class="small-note">Перед рейсом проверяйте актуальную дорожную информацию: {road_link}.</p></div><div class="timing-card"><dl><dt>Расстояние</dt><dd>{distance_text}</dd><dt>В пути</dt><dd>{drive_time}</dd><dt>Срок доставки</dt><dd>{delivery_time}</dd><dt>Особенность</dt><dd>Дальние рейсы планируются с учётом отдыха водителя, погоды и режима загрузки.</dd></dl></div></div></section>
<section class="section route-faq"><div class="container narrow"><p class="eyebrow">FAQ</p><h2>Частые вопросы</h2>{faq_html}</div></section>
<section class="section transport-strip"><div class="container"><div class="center-heading"><p class="eyebrow">ТРАНСПОРТ</p><h2>Машины на направление</h2></div><div class="vehicle-strip">{vehicle_html}</div></div></section>
<section class="section other-routes"><div class="container"><p class="eyebrow">ДРУГИЕ НАПРАВЛЕНИЯ</p><h2>Популярные маршруты из {origin}</h2><div class="pill-row">{other_links}</div></div></section>
<section class="section compare-section"><div class="container"><div class="center-heading"><p class="eyebrow">СРАВНЕНИЕ</p><h2>Частник или OQ SPEDITION?</h2></div><div class="compare-table-wrap"><table class="compare-table"><thead><tr><th>Что важно</th><th>Частник</th><th>OQ SPEDITION</th></tr></thead><tbody><tr><td>Цена</td><td class="bad">может измениться в пути</td><td class="good">условия фиксируются до подачи</td></tr><tr><td>Документы</td><td class="bad">часто отсутствуют</td><td class="good">договор, счёт, ТТН по запросу</td></tr><tr><td>Подбор машины</td><td class="bad">один доступный автомобиль</td><td class="good">подбор тоннажа и кузова под груз</td></tr><tr><td>Ответственность</td><td class="bad">на устных договорённостях</td><td class="good">условия перевозки согласуются письменно</td></tr><tr><td>Обратная загрузка</td><td class="bad">как повезёт</td><td class="good">проверяем скидку до 20%</td></tr></tbody></table></div></div></section>
<section class="section trust-section"><div class="container"><div class="trust-grid"><article><b>24</b><span>направления из Алматы</span></article><article><b>7+</b><span>классов транспорта</span></article><article><b>120 ₸/кг</b><span>ориентир сборного груза</span></article><article><b>1 заявка</b><span>на расчёт машины и документов</span></article></div></div></section>
<section class="section reviews-section"><div class="container"><div class="center-heading"><p class="eyebrow">ОТЗЫВЫ</p><h2>Примеры отзывов клиентов</h2><p>Блок временный: позже заменим на реальные отзывы OQ SPEDITION.</p></div><div class="review-grid"><article><b>★★★★★</b><p>«Быстро согласовали машину и условия. Удобно, что стоимость подтвердили до подачи.»</p><span>Пример отзыва</span></article><article><b>★★★★★</b><p>«Нужно было отправить партию товара в другой город. Помогли подобрать кузов и сроки.»</p><span>Пример отзыва</span></article><article><b>★★★★★</b><p>«Для бизнеса важны документы и предсказуемость. Маршрут и условия обсудили заранее.»</p><span>Пример отзыва</span></article></div></div></section>
<section class="section route-prep"><div class="container prep-grid"><div><p class="eyebrow">ПОДГОТОВКА ГРУЗА</p><h2>Что указать при заказе</h2><p class="muted">Эти данные помогут быстро подобрать машину и подготовить точный расчёт.</p></div><ul class="details-list">{prep_items}</ul></div></section>
<section class="section route-cta"><div class="container cta-panel"><div><p class="eyebrow">ОБРАТНОЕ НАПРАВЛЕНИЕ</p><h2>Нужен маршрут {dest} — {origin}?</h2><p>Проверим обратную загрузку и возможность скидки.</p></div><a class="button" href="{opposite}">Смотреть обратный маршрут →</a></div></section>
<div class="floating-actions"><a href="https://wa.me/77088462330" target="_blank" rel="noopener">WhatsApp</a><a href="tel:+77088462330">Позвонить</a></div><a class="scroll-top" href="#top">↑</a>
'''

for origin,origin_slug in CITY_LIST:
    for dest,dest_slug in CITY_LIST:
        if origin == dest:
            continue
        key_slug=dest_slug if origin == 'Алматы' else origin_slug if dest == 'Алматы' else f'{origin_slug}-{dest_slug}'
        link=city_path(origin_slug,dest_slug)
        opposite=city_path(dest_slug,origin_slug)
        if origin == 'Алматы': route=next(r for r in ROUTES if r[1]==dest_slug); km,price,rate,time=route[2:]
        elif dest == 'Алматы': route=next(r for r in ROUTES if r[1]==origin_slug); km,price,rate,time=route[2:]
        else: route=None; km=price=rate=None; time='по запросу'
        direction_text=f'{origin} — {dest}'
        page_prices=[]
        for v in VEHICLES:
            p=route_price(route,v,dest=='Алматы') if route else None
            page_prices.append((v,p))
        price_cards=''.join(f'<article class="card"><h3>{v["label"]}</h3><p>{v["body"]} · {", ".join(v["lengths"])}</p><p class="price">{("от "+fmt(p)+" ₸") if p is not None else "По запросу"}</p></article>' for v,p in page_prices)
        distance_text=f'{fmt(km)} км' if km else 'расстояние уточняется'
        gazelle_text=f'Газель от {fmt(price)} ₸' if price else 'Стоимость — по запросу'
        page_route=f'<script>window.OQ_PAGE_ROUTE={json.dumps({"from":origin,"to":dest},ensure_ascii=False)};</script>'
        route_calculator=calc((dest=='Алматы',route)) if route else calc()
        sections=route_sections(origin,origin_slug,dest,dest_slug,route,page_prices,opposite,route_calculator)
        form=quote_form(origin,dest)
        body=f'''<div id="top" class="container crumbs"><a href="/">Главная</a> / <a href="/gruzoperevozki/mezhgorod/">Межгород</a> / {direction_text}</div><section class="route-landing-hero"><div class="container hero-landing-grid"><div><p class="eyebrow">МАРШРУТ OQ SPEDITION</p><h1>Грузоперевозки<br><span>{origin} — {dest}</span></h1><p class="lead">Междугородняя перевозка груза по маршруту {origin} — {dest}. {distance_text}; срок: {time}; Газель, грузовик, фура и рефрижератор.</p><div class="route-badge">{distance_text} · {time} · {gazelle_text}</div><a class="button hero-button" href="#calculator">Получить КП — {dest}</a><div class="hero-benefits"><span>Подача от 30 минут</span><span>Официальный договор</span><span>Техника от 1,5 до 40 т</span></div></div>{form}</div></section>{page_route}{sections}'''
        desc=f'Грузоперевозки {origin} — {dest}: подбор Газели, грузовика, фуры и рефрижератора. Узнайте стоимость и срок доставки в OQ SPEDITION.'
        write(Path(link.lstrip('/'))/'index.html',shell(f'Грузоперевозки {origin} — {dest}: цены и сроки | OQ SPEDITION',desc,link,body))

service_cards=''.join(f'<a class="card" href="/uslugi/{slug}/"><h3>{name}</h3><p>{escape(desc)}</p><span class="tag">Страница услуги →</span></a>' for name,slug,desc in SERVICES)
write(Path('uslugi/index.html'),shell('Услуги транспортной логистики — OQ SPEDITION','Автомобильные перевозки, межгород, сборные грузы и транспортные решения для бизнеса в Казахстане.','/uslugi/','<section class="section"><div class="container"><div class="crumbs"><a href="/">Главная</a> / Услуги</div><p class="eyebrow">OQ SPEDITION</p><h1>Транспортные услуги</h1><p class="muted">Выберите услугу, чтобы узнать подробности и оставить запрос на расчёт.</p><div class="service-list">'+service_cards+'</div></div></section>'))
for name,slug,desc in SERVICES:
    body=f'<section class="hero"><div class="container"><p class="eyebrow">УСЛУГИ OQ SPEDITION</p><h1>{name}</h1><p class="lead">{escape(desc)}</p><a class="button" href="/#quote">Запросить расчёт</a></div></section><section class="section"><div class="container"><h2>Как получить расчёт</h2><p class="muted">Укажите маршрут, тип груза и контакт. Менеджер уточнит параметры перевозки и подготовит предложение.</p><a class="button" href="/#quote">Оставить заявку</a><p style="margin-top:24px"><a href="/gruzoperevozki/mezhgorod/">Посмотреть направления и тарифы →</a></p></div></section>'
    write(Path(f'uslugi/{slug}/index.html'),shell(f'{name} по Казахстану | OQ SPEDITION',desc,'/uslugi/'+slug+'/',body))

pricebody='<section class="section"><div class="container"><div class="crumbs"><a href="/">Главная</a> / Цены</div><p class="eyebrow">ТАРИФЫ</p><h1>Ориентировочные цены на межгород</h1><p class="muted">Тарифы Газели за рейс из Алматы. Для обратных направлений цена рассчитывается по тому же опубликованному тарифному ориентиру; возможность обратной загрузки уточняется отдельно.</p><div class="route-table-wrap"><table class="route-table"><thead><tr><th>Направление</th><th>Км</th><th>Газель, от</th><th>₸/км</th><th>Срок</th></tr></thead><tbody>'+table+'</tbody></table></div></div></section>'+calc()
write(Path('ceny/index.html'),shell('Цены на грузоперевозки по Казахстану — OQ SPEDITION','Ориентировочные тарифы Газели, расстояния и сроки между Алматы и городами Казахстана.','/ceny/',pricebody))
write(Path('kontakty/index.html'),shell('Контакты OQ SPEDITION','Свяжитесь с OQ SPEDITION, чтобы обсудить перевозку груза по Казахстану.','/kontakty/','<section class="section"><div class="container"><div class="crumbs"><a href="/">Главная</a> / Контакты</div><p class="eyebrow">OQ SPEDITION</p><h1>Контакты</h1><p>Обсудите маршрут и параметры перевозки с нашей командой.</p><p><a class="price" href="tel:+77088462330">+7 708 846 23 30</a></p><p><a href="mailto:logistics@oqspedition.kz">logistics@oqspedition.kz</a></p><a class="button" href="/#quote">Запросить расчёт</a></div></section>'))

paths=['/','/uslugi/','/ceny/','/kontakty/','/biznes/','/avtopark/','/gruzoperevozki/','/gruzoperevozki/mezhgorod/']
paths += [f'/uslugi/{s}/' for _,s,_ in SERVICES]
paths += [f'/avtopark/{v["id"]}/' for v in VEHICLES]
paths.extend(city_path(a_slug,b_slug) for _,a_slug in CITY_LIST for _,b_slug in CITY_LIST if a_slug!=b_slug)
write(Path('sitemap.xml'),'<?xml version="1.0" encoding="UTF-8"?>\n<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">'+''.join(f'<url><loc>{base}{p}</loc></url>' for p in paths)+'</urlset>')
write(Path('robots.txt'),f'User-agent: *\nAllow: /\nSitemap: {base}/sitemap.xml\n')
print(f'Generated {len(paths)} indexed pages.')

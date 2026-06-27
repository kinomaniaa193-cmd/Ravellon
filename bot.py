# -*- coding: utf-8 -*-
import telebot
from telebot import types
import sqlite3
import uuid
import logging
import random
import json
import urllib.request
import urllib.parse
from datetime import datetime, timedelta
import time

# --- КОНФИГУРАЦИЯ БРЕНДА RAVELLON SHOP ---
API_TOKEN = '8900426353:AAH21UIujStDfdSilq0ehq9aagIEiFlDG14'
ADMIN_IDS = [1242288682, 8305624267, 7907584687, 8262824885]
SHOP_NAME = "RAVELLON SHOP"
MANAGER_USERNAME = "aleksandr_0941"
INFO_CHANNEL = "https://t.me/Ravellnn"
BOT_USERNAME = "Ravellnbot"  

# Прямая ссылка на изображение профиля
MAIN_IMG = "https://ibb.co/gZxLnv8B"

# Реалистичный курс BTC/USD для расчёта оплаты
BTC_USD_RATE = 70000.0

# Банки для оплаты (к ним автоматически первым пунктом добавляется BTC)
BANKS = {
    'Россия': ['Сбербанк', 'Т-Банк', 'Озон Банк', 'ВТБ', 'Альфа-Банк', 'Райффайзен'],
    'Украина': ['Monobank', 'PrivatBank', 'А-Банк', 'Ощадбанк', 'ПУМБ'],
    'Казахстан': ['Kaspi.kz', 'Halyk Bank', 'ForteBank', 'Jusan Bank'],
    'Беларусь': ['Беларусбанк', 'Приорбанк', 'МТБанк', 'Белгазпромбанк']
}

# Ассортимент продукции
ALL_PRODUCT_NAMES = [
    "Гашиш Euro (Classic)", "Гашиш Ice-o-Lator (Top Tier)", "Гашиш Marocco Gold", "Гашиш Afghan Premium", 
    "Гашиш Nepal Stick", "Гашиш Fresh Frozen", "Гашиш Dry Sift",
    "Кокаин VHQ (92% Pure)", "Кокаин Fishscale (Bolivia)", "Кокаин Colombia High Quality", "Кокаин Royal White",
    "Кокаин Peru Premium", "Кокаин Crack (Rocks)",
    "Мефедрон Кристалл (Big Crystal)", "Мефедрон Мука (Classic)", "Мефедрон VHQ (Needle)", "Мефедрон Power Crystal",
    "Мефедрон Кристалл (Emerald)", "Мефедрон Мелкий Кристалл (Sugar)",
    "Амфетамин Sulphate (High Speed)", "Амфетамин Pink Panther", "Амфетамин Euro Speed", 
    "Амфетамин VHQ White", "Амфетамин Фосфат",
    "Шишки AK-47 (Indoor)", "Шишки Amnesia Haze (Extra)", "Шишки Gorilla Glue #4", 
    "Шишки White Widow (Classic)", "Шишки OG Kush (Strong)", "Шишки Lemon Haze (Citrus)", 
    "Шишки Girl Scout Cookies", "Шишки Jack Herer", "Шишки Northern Lights", "Шишки Pineapple Express",
    "Альфа-ПВП Blue Sky", "Альфа-ПВП Crystal Clear", "Альфа-ПВП Flour White", 
    "Альфа-ПВП Red Bull", "Альфа-ПВП Apple Green",
    "МДМА Кристаллы (Pure)", "МДМА Champagne (Gold)", "МДМА Cola Crystal",
    "Экстази Punisher (300mg)", "Экстази Tesla (Orange)", "Экстази Skype (Blue)", 
    "Экстази Burger King", "Экстази Red Bull (Pink)", "Экстази Philipp Plein", "Экстази WhatsApp",
    "ЛСД-25 250мкг (Aztec)", "ЛСД-25 California Sunshine", "ЛСД-25 Hoffman (200мкг)",
    "Грибы Golden Teacher (Dried)", "Грибы McKennaii", "DMT Crystal (Spirit)", 
    "2C-B Nexus (Pink)", "Кетамин S-isomer (Crystal)", "Кетамин Рацемат",
    "Метадон VHQ (Stone)", "Героин Classic (H-1)", "Ксанакс 2мг (Pfizer Style)", 
    "Лирика 300мг", "Трамадол 200мг"
]

# Максимально расширенные списки городов по РФ, РБ, РК, УА
COUNTRIES_DATA = {
    'Россия': [
        'Москва', 'Санкт-Петербург', 'Новосибирск', 'Екатеринбург', 'Казань', 'Нижний Новгород', 'Челябинск', 'Самара', 'Омск', 'Ростов-на-Дону',
        'Уфа', 'Красноярск', 'Воронеж', 'Пермь', 'Волгоград', 'Краснодар', 'Саратов', 'Тюмень', 'Тольятти', 'Ижевск',
        'Барнаул', 'Ульяновск', 'Иркутск', 'Хабаровск', 'Махачкала', 'Владивосток', 'Ярославль', 'Оренбург', 'Томск', 'Кемерово',
        'Новокузнецк', 'Рязань', 'Набережные Челны', 'Астрахань', 'Пенза', 'Киров', 'Липецк', 'Чебоксары', 'Балашиха', 'Калининград', 'Сочи',
        'Тула', 'Курск', 'Севастополь', 'Улан-Удэ', 'Ставрополь', 'Магнитогорск', 'Тверь', 'Иваново', 'Брянск', 'Белгород', 'Сургут', 'Владимир',
        'Нижний Тагил', 'Архангельск', 'Чита', 'Калуга', 'Смоленск', 'Волжский', 'Курган', 'Череповец', 'Орёл', 'Саранск', 'Вологда', 'Якутск',
        'Владикавказ', 'Мурманск', 'Грозный', 'Тамбов', 'Стерлитамак', 'Кострома', 'Петрозаводск', 'Йошкар-Ола', 'Новороссийск', 'Комсомольск-на-Амуре',
        'Таганрог', 'Сыктывкар', 'Нальчик', 'Шахты', 'Братск', 'Дзержинск', 'Орск', 'Ангарск', 'Благовещенск', 'Энгельс', 'Старый Оскол', 'Великий Новгород',
        'Псков', 'Бийск', 'Прокопьевск', 'Рыбинск', 'Балаково', 'Южно-Сахалинск', 'Армавир', 'Северодвинск', 'Королёв', 'Петропавловск-Камчатский', 'Норильск'
    ],
    'Украина': [
        'Киев', 'Харьков', 'Одесса', 'Днепр', 'Донецк', 'Запорожье', 'Львов', 'Кривой Рог', 'Николаев', 'Мариуполь',
        'Луганск', 'Винница', 'Макеевка', 'Севастополь', 'Симферополь', 'Херсон', 'Полтава', 'Чернигов', 'Черкассы', 'Хмельницкий',
        'Житомир', 'Черновцы', 'Сумы', 'Ровно', 'Ивано-Франковск', 'Каменское', 'Кропивницкий', 'Тернополь', 'Кременчуг', 'Луцк',
        'Белая Церковь', 'Краматорск', 'Мелитополь', 'Керчь', 'Ужгород', 'Бердянск', 'Никополь', 'Славянск', 'Алчевск', 'Павлоград', 'Северодонецк'
    ],
    'Казахстан': [
        'Алматы', 'Астана', 'Шымкент', 'Актобе', 'Караганда', 'Тараз', 'Усть-Каменогорск', 'Павлодар', 'Атырау', 'Семей',
        'Кызылорда', 'Костанай', 'Актау', 'Уральск', 'Петропавловск', 'Туркестан', 'Темиртау', 'Талдыкорган', 'Кокшетау', 'Жанаозен',
        'Экибастуз', 'Рудный', 'Кентау', 'Балхаш', 'Сатпаев', 'Кульсары', 'Жезказган', 'Талгар', 'Каскелен', 'Степногорск',
        'Щучинск', 'Риддер', 'Приозерск', 'Аральск', 'Аягоз', 'Сарань', 'Лисаковск', 'Житикара', 'Шу', 'Аркалык', 'Байконур',
        'Аксай', 'Атбасар', 'Жаркент', 'Каратау', 'Ленгер', 'Макинск', 'Сарканд', 'Сарыагаш', 'Текели', 'Хромтау', 'Шалкар', 'Шемонаиха',
        'Есик', 'Карабулак', 'Уштобе', 'Шолаккорган', 'Кордай', 'Мерке', 'Шардара', 'Жетысай', 'Айтеке Би', 'Карасу'
    ],
    'Беларусь': [
        'Минск', 'Гомель', 'Могилев', 'Витебск', 'Гродно', 'Брест', 'Бобруйск', 'Барановичи', 'Борисов', 'Пинск',
        'Орша', 'Мозырь', 'Солигорск', 'Лида', 'Новополоцк', 'Молодечно', 'Полоцк', 'Жлобин', 'Светлогорск', 'Речица',
        'Слуцк', 'Жодино', 'Слоним', 'Кобрин', 'Волковыск', 'Калинковичи', 'Сморгонь', 'Рогачев', 'Горки', 'Осиповичи',
        'Новогрудок', 'Береза', 'Кричев', 'Дзерджержинск', 'Лунинец', 'Ивацевичи', 'Марьина Горка', 'Поставы', 'Пружаны', 'Глубокое', 'Добруш',
        'Лепель', 'Быхов', 'Климовичи', 'Шклов', 'Костюковичи', 'Житковичи', 'Мосты', 'Ошмяны', 'Дрогичин', 'Ганцевичи', 'Жабинка', 'Несвиж',
        'Микашевичи', 'Новолукомль', 'Городок', 'Белоозерск', 'Березино', 'Ветка', 'Смолевичи', 'Ляховичи', 'Чериков', 'Клецк', 'Дубровно',
        'Копыль', 'Мстиславль', 'Логойск', 'Чаусы', 'Толочин', 'Браслав', 'Миоры', 'Верхнедвинск', 'Докшицы'
    ]
}

COUNTRIES_KEYS = list(COUNTRIES_DATA.keys())

# РЕАЛИСТИЧНЫЙ КУРС ВАЛЮТ НА ИЮНЬ 2026 ГОДА
EXCHANGE_RATES = {'KZT': 487.0, 'RUB': 79.0, 'BYN': 3.6, 'UAH': 45.0, 'USD': 1.0}
CURRENCY_MAP = {'Казахстан': 'KZT', 'Россия': 'RUB', 'Беларусь': 'BYN', 'Украина': 'UAH'}

def get_payment_methods(country):
    """Предоставляет список доступных способов оплаты, где первым пунктом всегда идет BTC."""
    banks = BANKS.get(country, ['Карта любого банка'])
    return ['BTC (Bitcoin)'] + banks

def generate_1000_reviews():
    """Генерирует детерминированный массив из 1000 уникальных реалистичных отзывов."""
    r_gen = random.Random(1337)
    
    p_perfect_start = ["Снял в касание", "Забрал быстро", "Наход моментальный", "Снял чётко по метке", "Поднял без проблем", "Квест простой", "Забрал за секунду", "Снято аккуратно", "Нашёл сразу", "Изи наход", "Все на месте", "Клад дома", "Забрал по красоте", "Снял без палева", "Квест 10/10", "На месте был быстро"]
    p_perfect_middle = [", место надежное", ", локация тихая", ", без лишних глаз", ", координаты точные", ", спрятано грамотно", ", курьер профи", ", место идеальное", ", чайки мимо", ", тайник супер", ", шкуроходы не найдут", ", район спокойный", ", метка совпадает 100%"]
    p_perfect_end = [". Качество вышка!", ". Стафф просто огонь.", ". Вес ровный, спасибо.", ". Эффект пушка.", ". Магазину респект.", ". Буду брать еще.", ". Упаковка вакуум.", ". Все на высшем уровне.", ". Товар отличный.", ". Рекомендую данный шоп!", ". Стафф рабочий, советую.", ". Вернусь еще не раз."]
    
    p_neutral_start = ["Пришлось немного поискать", "Клад был далековато", "Место людное, но забрал", "Курьер прикопал глубоковато", "Координаты немного косили, но нашел", "Пришлось попотеть на месте, но поднял", "Локация немного шумная, но квест пройден", "Были сомнения по метке, но все окей"]
    p_neutral_middle = [", но описание помогло разобраться", ", курьеру стоит быть аккуратнее с выбором места", ", упаковка спасла от сырости", ", место не самое простое для съема", ", в итоге все обошлось благополучно", ", спрятано на совесть"]
    p_neutral_end = [". Главное качество порадовало.", ". Товар рабочий, так что без обид.", ". Вес ровный, качество на уровне.", ". В следующий раз делайте место потише.", ". Магазу спасибо, что не обманули.", ". Качество бомба, компенсировало поиски."]

    reviews_list = []
    
    # Сгенерируем 900 идеальных отзывов
    while len(reviews_list) < 900:
        s = r_gen.choice(p_perfect_start)
        m = r_gen.choice(p_perfect_middle)
        e = r_gen.choice(p_perfect_end)
        rev = s + m + e
        if rev not in reviews_list:
            reviews_list.append(rev)
            
    # Сгенерируем 100 конструктивных ("не совсем плохих") отзывов
    while len(reviews_list) < 1000:
        s = r_gen.choice(p_neutral_start)
        m = r_gen.choice(p_neutral_middle)
        e = r_gen.choice(p_neutral_end)
        rev = s + m + e
        if rev not in reviews_list:
            reviews_list.append(rev)
            
    r_gen.shuffle(reviews_list)
    return reviews_list

PREMADE_REVIEWS = generate_1000_reviews()

logging.basicConfig(level=logging.INFO)
bot = telebot.TeleBot(API_TOKEN)

def get_product_medical_card(name):
    """Возвращает детальную информацию о товаре, включая способ употребления и рекомендации нарколога."""
    name_lower = name.lower()
    
    if "гашиш" in name_lower:
        return (
            "Способ употребления:\n"
            "Рекомендуется деликатное испарение с помощью специализированных вапорайзеров при контролируемой температуре "
            "для минимизации продуктов горения. Традиционные методы тления дают более жесткий дым.\n\n"
            "Совет нарколога:\n"
            "Чистый продукт без химических примесей минимизирует токсический удар по легким и ЦНС. Тем не менее, "
            "регулярное использование может вызвать апатию и снижение мотивации. Потребляйте умеренно, делайте длительные "
            "паузы и всегда держите под рукой обильное питье во избежание сухости слизистых оболочек."
        )
    elif "кокаин" in name_lower:
        return (
            "Способ употребления:\n"
            "Преимущественно интраназальное введение в виде ультра-мелкого порошка. Крупные кристаллы могут травмировать "
            "чувствительную слизистую оболочку носа и вызывать микрокровотечения.\n\n"
            "Совет нарколога:\n"
            "Лабораторный продукт класса VHQ снижает риск отравления дешевыми примесями (кофеин, левамизол). Однако вещество "
            "несет огромную нагрузку на сердечно-сосудистую систему. Категорически запрещено совмещать с алкоголем (образуется "
            "крайне токсичный кокаэтилен) и энергетиками. Контролируйте пульс и давление."
        )
    elif "мефедрон" in name_lower:
        return (
            "Способ употребления:\n"
            "Применяется интраназально (тщательно измельчив кристаллы в пудру) либо перорально через капсулы 'бомбочки' "
            "(это обеспечивает более плавный вход и длительный эффект).\n\n"
            "Совет нарколога:\n"
            "Продукт высокой очистки исключает ожоги химическим сырьем, но мощный выброс серотонина быстро истощает запасы организма. "
            "Соблюдайте строгие тайминги между дозами (не менее 2 часов), никогда не уходите в многодневные марафоны. "
            "После сессии восполняйте баланс электролитов, принимайте витамины и пейте много минеральной воды."
        )
    elif "амфетамин" in name_lower:
        return (
            "Способ употребления:\n"
            "Интраназально или перорально в микро-дозировках. Тщательное измельчение предотвращает застой вещества на слизистой.\n\n"
            "Совет нарколога:\n"
            "Наш продукт избавлен от избыточной кислотности, что бережет ваш организм. Но длительная стимуляция сильно истощает нервную систему. "
            "Следите за температурой тела и регулярно делайте перерывы на полноценный сон. Не забывайте принудительно принимать "
            "легкую пищу (бульоны, фрукты) для сохранения сил."
        )
    elif "шишки" in name_lower:
        return (
            "Способ употребления:\n"
            "Рекомендуется использование через вапорайзеры закрытого типа (нагрев без прямого горения) — это исключает "
            "попадание смол в дыхательные пути.\n\n"
            "Совет нарколога:\n"
            "Натуральный продукт без спайсовых напылений. Помогает при тревожности и бессоннице. Не смешивайте с алкогольными "
            "напитками во избежание сильного головокружения и тошноты. Используйте только в безопасной и комфортной обстановке."
        )
    elif "альфа" in name_lower or "pvp" in name_lower or "пвп" in name_lower:
        return (
            "Способ употребления:\n"
            "Интраназальный метод или деликатное испарение с фольги / стеклянных трубок.\n\n"
            "Совет нарколога:\n"
            "Чрезвычайно активное вещество с мгновенным привыканием. Настоятельно рекомендуется воздержаться от частого употребления. "
            "Дозировки должны быть микроскопическими (до 5 мг). В случае панической атаки или паранойи немедленно прекратите "
            "прием, примите горизонтальное положение, пейте воду и обеспечьте приток свежего воздуха."
        )
    elif "мдма" in name_lower or "экстази" in name_lower:
        return (
            "Способ употребления:\n"
            "Пероральный прием таблеток целиком либо растворение кристаллов в безалкогольном напитке.\n\n"
            "Совет нарколога:\n"
            "Высокая чистота минимизирует побочные токсические эффекты. Помните о правиле 'безопасного трипа': дозировка рассчитывается "
            "как 1.5 мг на кг веса. Во время active танцев пейте ровно 250 мл воды в час (не больше и не меньше), чтобы не допустить "
            "опасного перегрева организма (гипертермии) или водного отравления."
        )
    elif "лсд" in name_lower or "грибы" in name_lower or "dmt" in name_lower or "2c-b" in name_lower:
        return (
            "Способ употребления:\n"
            "ЛСД и 2C-B употребляются сублингвально (под язык), грибы — разжевываются на пустой желудок (за 4-6 часов до приема).\n\n"
            "Совет нарколога:\n"
            "Вешества полностью лишены физической зависимости. Ключевой фактор безопасности — ваше окружение и внутренний настрой (Set and Setting). "
            "Рядом всегда должен находиться трезвый человек (ситтер), готовый оказать психологическую поддержку. Исключите алкоголь."
        )
    elif "ксанакс" in name_lower or "лирика" in name_lower or "трамадол" in name_lower:
        return (
            "Способ употребления:\n"
            "Строго перорально в терапевтических объемах, запивая стаканом воды.\n\n"
            "Совет нарколога:\n"
            "Оригинальные аптечные бланки. Обладают мощным седативным действием. Помните: бесконтрольный прием и превышение доз ведут к "
            "тяжелой физиологической зависимости. Полностью исключите алкоголь во избежание критического угнетения дыхательного центра."
        )
    else:
        return (
            "Способ употребления:\n"
            "Употреблять стандартными методами, рекомендованными для данной группы веществ.\n\n"
            "Совет нарколога:\n"
            "Продукт прошел строгий контроль качества. Соблюдайте безопасную дозировку, делайте перерывы и следите за общим самочувствием."
        )

def get_districts_for_city(city_name):
    """Возвращает список из 3-4 реальных или стабильно сгенерированных районов для выбранного города."""
    major_districts = {
        # Россия
        'Москва': ['Арбат', 'Тверской', 'Замоскворечье', 'Хамовники'],
        'Санкт-Петербург': ['Центральный', 'Адмиралтейский', 'Петроградский', 'Василеостровский'],
        'Новосибирск': ['Заельцовский', 'Железнодорожный', 'Калининский', 'Дзержинский'],
        'Екатеринбург': ['Академический', 'Верх-Исетский', 'Железнодорожный', 'Октябрьский'],
        'Казань': ['Ново-Савиновский', 'Авиастроительный', 'Московский', 'Кировский'],
        'Нижний Новгород': ['Нижегородский', 'Канавинский', 'Приокский', 'Московский'],
        'Челябинск': ['Курчатовский', 'Металлургический', 'Тракторозаводский', 'Советский'],
        'Самара': ['Железнодорожный', 'Куйбышевский', 'Ленинский', 'Красноглинский'],
        'Ростов-на-Дону': ['Ленинский', 'Пролетарский', 'Железнодорожный', 'Советский'],
        'Омск': ['Советский', 'Центральный', 'Кировский', 'Октябрьский'],
        'Уфа': ['Кировский', 'Орджоникидзевский', 'Калининский', 'Октябрьский'],
        'Красноярск': ['Центральный', 'Советский', 'Свердловский', 'Октябрьский'],
        'Воронеж': ['Центральный', 'Коминтерновский', 'Ленинский', 'Левобережный'],
        'Пермь': ['Ленинский', 'Свердловский', 'Мотовилихинский', 'Индустриальный'],
        'Волгоград': ['Центральный', 'Ворошиловский', 'Дзержинский', 'Красногвардейский'],
        'Краснодар': ['Центральный', 'Прикубанский', 'Карасунский', 'Западный'],
        'Сочи': ['Центральный', 'Адлерский', 'Хостинский', 'Лазаревский'],
        'Севастополь': ['Ленинский', 'Гагаринский', 'Нахимовский', 'Балаклавский'],
        'Тольятти': ['Автозаводский', 'Центральный', 'Комсомольский'],
        'Ижевск': ['Октябрьский', 'Первомайский', 'Индустриальный', 'Ленинский'],
        'Барнаул': ['Центральный', 'Ленинский', 'Октябрьский', 'Индундустриальный'],
        'Ульяновск': ['Ленинский', 'Засвияжский', 'Заволжский', 'Железнодорожный'],
        'Иркутск': ['Правобережный', 'Октябрьский', 'Свердловский', 'Ленинский'],
        'Хабаровск': ['Центральный', 'Кировский', 'Краснофлотский', 'Железнодорожный'],
        'Владивосток': ['Ленинский', 'Первомайский', 'Фрунзенский', 'Советский'],
        'Ярославль': ['Кировский', 'Ленинский', 'Дзержинский', 'Заволжский'],
        'Калининград': ['Центральный', 'Ленинградский', 'Московский'],
        'Махачкала': ['Ленинский', 'Советский', 'Кировский'],
        'Грозный': ['Ахматовский', 'Байсангуровский', 'Висаитовский', 'Шейх-Мансуровский'],
        'Набережные Челны': ['Автозаводский', 'Центральный', 'Комсомольский'],
        'Астрахань': ['Кировский', 'Советский', 'Ленинский', 'Трусовский'],
        'Пенза': ['Жележанодорожный', 'Ленинский', 'Октябрьский', 'Первомайский'],
        'Киров': ['Ленинский', 'Октябрьский', 'Первомайский', 'Нововятский'],
        'Липецк': ['Правобережный', 'Левобережный', 'Октябрьский', 'Советский'],
        'Чебоксары': ['Калининский', 'Ленинский', 'Московский'],
        'Рязань': ['Московский', 'Октябрьский', 'Советский', 'Жележанодорожный'],
        'Курск': ['Центральный', 'Сеймский', 'Железнодорожный'],
        'Ставрополь': ['Ленинский', 'Октябрьский', 'Промышленный'],
        'Магнитогорск': ['Ленинский', 'Правобережный', 'Орджоникидзевский'],
        'Тверь': ['Заволжский', 'Московский', 'Пролетарский', 'Центральный'],
        'Иваново': ['Фрунзенский', 'Октябрьский', 'Ленинский', 'Советский'],
        'Брянск': ['Бежицкий', 'Володарский', 'Советский', 'Фокинский'],
        'Белгород': ['Восточный', 'Западный'],
        'Surgut': ['Центральный', 'Северный', 'Северо-Восточный', 'Восточный'],
        'Владимир': ['Ленинский', 'Октябрьский', 'Фрунзенский'],
        # Беларусь
        'Минск': ['Фрунзенский', 'Первомайский', 'Заводской', 'Центральный'],
        'Гомель': ['Центральный', 'Советский', 'Жележанодорожный', 'Новобелицкий'],
        'Могилев': ['Ленинский', 'Октябрьский', 'Центральный'],
        'Витебск': ['Октябрьский', 'Первомайский', 'Железнодорожный'],
        'Гродно': ['Ленинский', 'Октябрьский', 'Центральный'],
        'Брест': ['Ленинский', 'Московский', 'Восточный'],
        # Казахстан
        'Алматы': ['Медеуский', 'Бостандыкский', 'Алмалинский', 'Ауэзовский'],
        'Астана': ['Есиль', 'Алматы', 'Сарыарка', 'Байконур'],
        'Шымкент': ['Абайский', 'Аль-Фарабийский', 'Енбекшинский', 'Каратауский'],
        'Караганда': ['Казыбек би', 'Алихана Бокейхана', 'Юго-Восток'],
        'Павлодар': ['Центральный', 'Дачный', 'Химгородки', 'Усольский'],
        'Актобе': ['Алматы', 'Астана', 'Жилгородок', 'Шанхай'],
        'Атырау': ['Авангард', 'Привокзальный', 'Жилгородок', 'Нурсая'],
        # Украина
        'Киев': ['Печерский', 'Шевченковский', 'Подольский', 'Днепровский'],
        'Харьков': ['Киевский', 'Шевченковский', 'Салтовский', 'Холодногорский'],
        'Одесса': ['Приморский', 'Киевский', 'Хаджибейский', 'Пересыпский'],
        'Днепр': ['Соборный', 'Шевченковский', 'Амур-Нижнеднепровский', 'Центральный'],
        'Запорожье': ['Александровский', 'Заводской', 'Коммунарский', 'Днепровский'],
        'Львов': ['Галицкий', 'Лычаковский', 'Франковский', 'Шевченковский'],
        'Кривой Рог': ['Металлургический', 'Центрально-Городской', 'Покровский', 'Саксаганский']
    }
    
    city_clean = city_name.strip()
    if city_clean in major_districts:
        return major_districts[city_clean]
    
    return ['Центральный район', 'Южный район', 'Восточный район', 'Западный район']

class Database:
    def __init__(self):
        self.db_path = 'shop_v5.db'
        self.create_tables()
        self.init_data()

    def _get_conn(self):
        """Открывает новое изолированное соединение со встроенным таймаутом ожидания блокировки."""
        return sqlite3.connect(self.db_path, timeout=20.0)

    def create_tables(self):
        with self._get_conn() as conn:
            cursor = conn.cursor()
            cursor.execute('CREATE TABLE IF NOT EXISTS users (uid INTEGER PRIMARY KEY, city TEXT, country TEXT, district TEXT, joined TEXT, balance REAL DEFAULT 0.0, referrer_id INTEGER)')
            cursor.execute('CREATE TABLE IF NOT EXISTS products (id INTEGER PRIMARY KEY AUTOINCREMENT, name TEXT, price REAL)')
            cursor.execute('CREATE TABLE IF NOT EXISTS stock (city TEXT, product_id INTEGER, PRIMARY KEY(city, product_id))')
            cursor.execute('CREATE TABLE IF NOT EXISTS reviews (id INTEGER PRIMARY KEY AUTOINCREMENT, text TEXT, prod TEXT)')
            cursor.execute('CREATE TABLE IF NOT EXISTS settings (key TEXT PRIMARY KEY, val TEXT)')
            cursor.execute('CREATE TABLE IF NOT EXISTS promocodes (code TEXT PRIMARY KEY, discount INTEGER, expires_at TEXT)')
            
            # Таблицы для FAQ, подписок и корзины
            cursor.execute('CREATE TABLE IF NOT EXISTS subscriptions (uid INTEGER, city TEXT, PRIMARY KEY(uid, city))')
            cursor.execute('CREATE TABLE IF NOT EXISTS cart (id INTEGER PRIMARY KEY AUTOINCREMENT, uid INTEGER, product_id INTEGER, weight_idx TEXT, district TEXT)')
            
            # Постепенные миграции колонок в случае существования старых баз
            try:
                cursor.execute("ALTER TABLE users ADD COLUMN district TEXT")
            except sqlite3.OperationalError:
                pass
            try:
                cursor.execute("ALTER TABLE users ADD COLUMN balance REAL DEFAULT 0.0")
            except sqlite3.OperationalError:
                pass
            try:
                cursor.execute("ALTER TABLE users ADD COLUMN referrer_id INTEGER")
            except sqlite3.OperationalError:
                pass
            try:
                cursor.execute("ALTER TABLE promocodes ADD COLUMN expires_at TEXT DEFAULT 'eternal'")
            except sqlite3.OperationalError:
                pass
                
            conn.commit()

    def init_data(self):
        with self._get_conn() as conn:
            cursor = conn.cursor()
            
            # Проверяем, соответствуют ли существующие товары новому ценовому диапазону от 25$ до 70$ за 1г
            has_old_prices = cursor.execute("SELECT COUNT(*) FROM products WHERE price > 75 OR price < 25").fetchone()[0]
            if has_old_prices > 0:
                cursor.execute("DELETE FROM products")
                cursor.execute("DELETE FROM stock")  # Очищаем старые остатки, чтобы витрина пересобралась
            
            if cursor.execute("SELECT COUNT(*) FROM products").fetchone()[0] == 0:
                for name in ALL_PRODUCT_NAMES:
                    # Базовая цена за 1 грамм теперь составляет от 25$ до 70$, что приближено к реальным ценам в рознице
                    cursor.execute("INSERT INTO products (name, price) VALUES (?, ?)", (name, random.randint(25, 70)))
            
            if cursor.execute("SELECT COUNT(*) FROM reviews").fetchone()[0] == 0:
                self._shuffle_reviews_internal(conn)
            
            if cursor.execute("SELECT COUNT(*) FROM stock").fetchone()[0] == 0:
                self._shuffle_stock_internal(conn)
                
            # Инициализация дефолтного вечного промокода RAV5 на 5% скидки
            cursor.execute("INSERT OR IGNORE INTO promocodes (code, discount, expires_at) VALUES ('RAV5', 5, 'eternal')")
            conn.commit()

    def _shuffle_reviews_internal(self, conn):
        """Заполняет таблицу отзывов случайной выборкой из 100 заготовленных."""
        cursor = conn.cursor()
        cursor.execute("DELETE FROM reviews")
        # Выбираем 100 случайных отзывов из нашей базы в 1000 шт.
        sampled_revs = random.sample(PREMADE_REVIEWS, 100)
        for txt in sampled_revs:
            cursor.execute("INSERT INTO reviews (text, prod) VALUES (?,?)", (txt, random.choice(ALL_PRODUCT_NAMES)))

    def _shuffle_stock_internal(self, conn):
        """Выполняет пересборку витрин с использованием текущей активной транзакции."""
        cursor = conn.cursor()
        cursor.execute("DELETE FROM stock")
        p_ids = [r[0] for r in cursor.execute("SELECT id FROM products").fetchall()]
        for country, cities in COUNTRIES_DATA.items():
            for city in cities:
                for pid in random.sample(p_ids, random.randint(8, 12)):
                    cursor.execute("INSERT OR IGNORE INTO stock (city, product_id) VALUES (?,?)", (city, pid))

    def shuffle_stock(self):
        with self._get_conn() as conn:
            self._shuffle_stock_internal(conn)
            conn.commit()

    def shuffle_reviews(self):
        """Обновляет и заново распределяет отзывы на витрине."""
        with self._get_conn() as conn:
            self._shuffle_reviews_internal(conn)
            conn.commit()

    def execute(self, query, params=()):
        with self._get_conn() as conn:
            cursor = conn.cursor()
            cursor.execute(query, params)
            conn.commit()

    def fetchall(self, query, params=()):
        with self._get_conn() as conn:
            cursor = conn.cursor()
            cursor.execute(query, params)
            return cursor.fetchall()

    def fetchone(self, query, params=()):
        with self._get_conn() as conn:
            cursor = conn.cursor()
            cursor.execute(query, params)
            return cursor.fetchone()

db = Database()

def get_main_kb(uid):
    """Возвращает клавиатуру главного меню в строгом и стильном дизайне с тематическими иконками."""
    # Получим актуальное количество предметов в корзине
    cart_count_row = db.fetchone("SELECT COUNT(*) FROM cart WHERE uid=?", (uid,))
    cart_count = cart_count_row[0] if cart_count_row else 0
    cart_label = f"🛍️ Корзина ({cart_count})" if cart_count > 0 else "🛍️ Корзина (Пусто)"

    m = types.InlineKeyboardMarkup(row_width=2)
    m.row(
        types.InlineKeyboardButton("🛒 Каталог", callback_data="shop"),
        types.InlineKeyboardButton(cart_label, callback_data="view_cart")
    )
    m.row(
        types.InlineKeyboardButton("🌐 Локации", callback_data="loc"),
        types.InlineKeyboardButton("🔔 Гео-подписка", callback_data="geo_sub_menu")
    )
    m.row(
        types.InlineKeyboardButton("💼 Работа", callback_data="job"),
        types.InlineKeyboardButton("💬 Отзывы", callback_data="rev_list_0")
    )
    m.row(
        types.InlineKeyboardButton("📜 Правила", callback_data="rules_menu"),
        types.InlineKeyboardButton("❓ FAQ / Помощь", callback_data="faq_menu")
    )
    m.row(
        types.InlineKeyboardButton("⚕️ Советы нарколога", callback_data="doctor_tips"),
        types.InlineKeyboardButton("🎁 Бонусы", callback_data="bonuses")
    )
    m.row(
        types.InlineKeyboardButton("ℹ️ Информация ↗", url=INFO_CHANNEL),
        types.InlineKeyboardButton("📞 Поддержка ↗", url=f"https://t.me/{MANAGER_USERNAME}")
    )
    if uid in ADMIN_IDS:
        m.row(types.InlineKeyboardButton("⚙️ Панель управления", callback_data="admin_main"))
    return m

def build_profile_caption(uid, country_text, city_text, district_text):
    """Формирует премиальное визуальное оформление профиля с понятной группировкой и красивыми эмодзи."""
    country_flags = {
        "Россия": "🇷🇺",
        "Украина": "🇺🇦",
        "Казахстан": "🇰🇿",
        "Беларусь": "🇧🇾"
    }
    flag = country_flags.get(country_text, "🌐")
    
    # Расчет динамических данных рефералов из бд
    ref_count = db.fetchone("SELECT COUNT(*) FROM users WHERE referrer_id=?", (uid,))[0]
    balance_row = db.fetchone("SELECT balance FROM users WHERE uid=?", (uid,))
    balance = balance_row[0] if balance_row and balance_row[0] is not None else 0.0
    
    # Расчёт общего числа пользователей, начиная от 40 597
    real_count = db.fetchone("SELECT COUNT(*) FROM users")[0]
    total_users_display = f"{40597 + real_count:,}".replace(",", " ")
    
    #    # Динамический подсчет количества отзывов от базовой цифры
    actual_rev_count = db.fetchone("SELECT COUNT(*) FROM reviews")[0]
    total_reviews_display = f"{35790 + actual_rev_count:,}".replace(",", " ")
    
    caption = (
        f"👤 <b>ЛИЧНЫЙ КАБИНЕТ ПОЛЬЗОВАТЕЛЯ</b>\n"
        f"━━━━━━━━━━━━━━━━━━━━━━━━━━\n\n"
        f"👥 <b>Пользователей в системе:</b> {total_users_display} чел.\n"
        f"🌟 <b>Рейтинг шопа:</b> ⭐️ 4.99 <i>({total_reviews_display} шт.)</i>\n"
        f"🎖️ <b>Ваш личный рейтинг:</b> ⭐️ 5.00 <i>(0 шт.)</i>\n\n"
        f"📍 <b>Текущая геолокация:</b>\n"
        f" ┣ Страна: {flag} <b>{country_text}</b>\n"
        f" ┣ Город: 🏙️ <b>{city_text}</b>\n"
        f" ┗ Район: 🗺️ <b>{district_text}</b>\n\n"
        f"📊 <b>Ваша статистика:</b>\n"
        f" ┣ Всего покупок: 🛍️ <b>0 шт.</b>\n"
        f" ┗ Ваша скидка: % <b>0 %</b>\n\n"
        f"👥 <b>Реферальная программа:</b>\n"
        f" ┣ Приглашено друзей: 🧑‍🤝‍🧑 <b>{ref_count} чел.</b>\n"
        f" ┗ Доступный бонус: 💵 <b>{balance:.2f} USD</b>\n\n"
        f"🔗 <b>Приглашай друзей и зарабатывай!</b>\n"
        f"🎁 <i>Получай 0.5$ за каждого друга и трать на скидочные промокоды!</i>\n"
        f"<code>https://t.me/{BOT_USERNAME}?start=r_{uid}</code>\n"
        f"━━━━━━━━━━━━━━━━━━━━━━━━━━"
    )
    return caption

def safe_edit_text(chat_id, message_id, text, reply_markup=None, parse_mode="HTML"):
    """Универсальный и на 100% стабильный рендерер текстовых изменений. Исключает краш Bad Request, сохраняя картинку на месте."""
    try:
        bot.edit_message_caption(caption=text, chat_id=chat_id, message_id=message_id, reply_markup=reply_markup, parse_mode=parse_mode)
    except Exception:
        try:
            bot.edit_message_text(text=text, chat_id=chat_id, message_id=message_id, reply_markup=reply_markup, parse_mode=parse_mode)
        except Exception:
            try:
                bot.delete_message(chat_id, message_id)
            except Exception:
                pass
            try:
                bot.send_photo(chat_id, MAIN_IMG, caption=text, reply_markup=reply_markup, parse_mode=parse_mode)
            except Exception:
                bot.send_message(chat_id, text, reply_markup=reply_markup, parse_mode=parse_mode)

def show_main_menu(cid, mid, uid):
    """Надежный рендерер главного меню профиля через safe_edit_text."""
    u = db.fetchone("SELECT city, country, district FROM users WHERE uid=?", (uid,))
    city_text = u[0] if u and u[0] else "Не указан"
    country_text = u[1] if u and u[1] else "Не указана"
    district_text = u[2] if u and u[2] else "Не указан"
    
    profile_caption = build_profile_caption(uid, country_text, city_text, district_text)
    safe_edit_text(cid, mid, profile_caption, get_main_kb(uid))

@bot.message_handler(commands=['start'])
def handle_start(m):
    uid = m.from_user.id
    
    # Проверяем, новый ли это пользователь
    is_new = db.fetchone("SELECT uid FROM users WHERE uid=?", (uid,)) is None
    
    # Обработка реферального старта вида /start r_1242288682
    args = m.text.split()
    referrer_id = None
    ref_message = ""
    
    if len(args) > 1 and args[1].startswith("r_"):
        try:
            ref_val = int(args[1].replace("r_", ""))
            if ref_val != uid:  # Сам себя пригласить не может
                referrer_id = ref_val
        except ValueError:
            pass

    if is_new:
        # Для обычных пользователей баланс 0.0, а для админов по умолчанию 500.0 баксов!
        start_balance = 500.0 if uid in ADMIN_IDS else 0.0
        db.execute("INSERT INTO users (uid, joined, balance, referrer_id) VALUES (?,?,?,?)", 
                   (uid, datetime.now().strftime("%Y-%m-%d"), start_balance, referrer_id))
        
        if referrer_id:
            # Начисляем 0.5 USD пригласителю
            db.execute("UPDATE users SET balance = balance + 0.5 WHERE uid=?", (referrer_id,))
            ref_message = "🎉 <b>Вы успешно вошли по реферальной ссылке! Нам очень приятно, что вы с нами!</b>\n\n"
            try:
                bot.send_message(referrer_id, f"🎉 По вашей ссылке зарегистрировался новый пользователь! Баланс пополнен на <b>0.50 USD</b>.", parse_mode="HTML")
            except Exception:
                pass
    else:
        # Восстанавливаем пользователя, если он удалил чат
        db.execute("INSERT OR IGNORE INTO users (uid, joined) VALUES (?,?)", (uid, datetime.now().strftime("%Y-%m-%d")))
        
        # Если админ зашел повторно, но у него баланс меньше 500 баксов — пополняем
        if uid in ADMIN_IDS:
            curr_bal = db.fetchone("SELECT balance FROM users WHERE uid=?", (uid,))
            if curr_bal and curr_bal[0] < 500.0:
                db.execute("UPDATE users SET balance = 500.0 WHERE uid=?", (uid,))
        
        if len(args) > 1 and args[1].startswith("r_"):
            try:
                bot.send_message(m.chat.id, "⚠️ <b>Вы уже зарегистрированы в системе!</b> Реферальная ссылка действительна только для новых пользователей.", parse_mode="HTML")
            except Exception:
                pass
    
    u = db.fetchone("SELECT city, country, district FROM users WHERE uid=?", (uid,))
    city_text = u[0] if u and u[0] else "Не указан"
    country_text = u[1] if u and u[1] else "Не указана"
    district_text = u[2] if u and u[2] else "Не указан"
    
    profile_caption = ref_message + build_profile_caption(uid, country_text, city_text, district_text)
    
    try:
        bot.send_photo(m.chat.id, MAIN_IMG, caption=profile_caption, reply_markup=get_main_kb(uid), parse_mode="HTML")
    except Exception:
        bot.send_message(m.chat.id, profile_caption, reply_markup=get_main_kb(uid), parse_mode="HTML")

@bot.callback_query_handler(func=lambda c: True)
def handle_cb(c):
    uid, cid, mid, data = c.from_user.id, c.message.chat.id, c.message.message_id, c.data

    if data == "to_main":
        show_main_menu(cid, mid, uid)

    # --- ИНТЕРАКТИВНЫЙ РАЗДЕЛ FAQ ---
    elif data == "faq_menu":
        faq_text = (
            f"❓ <b>ИНТЕРАКТИВНЫЙ РАЗДЕЛ ПОДДЕРЖКИ (FAQ) {SHOP_NAME}</b>\n"
            f"━━━━━━━━━━━━━━━━━━━━━━━━━━\n\n"
            f"Приветствуем! В этом разделе собраны ответы на 80% типовых вопросов, с которыми сталкиваются наши пользователи.\n\n"
            f"Пожалуйста, выберите интересующую вас категорию, нажав на кнопку ниже. "
            f"Это поможет вам моментально решить проблему без привлечения живого менеджера."
        )
        m = types.InlineKeyboardMarkup(row_width=1)
        m.add(
            types.InlineKeyboardButton("💳 Как оплатить заказ?", callback_data="faq_how_to_pay"),
            types.InlineKeyboardButton("🔍 Что делать, если ненаход?", callback_data="faq_not_found"),
            types.InlineKeyboardButton("⏳ Сроки доставки и выдачи?", callback_data="faq_delivery_time"),
            types.InlineKeyboardButton("🛡️ Конфиденциальность и безопасность", callback_data="faq_security"),
            types.InlineKeyboardButton("✉️ Не нашли свой вопрос? Поддержка ↗", url=f"https://t.me/{MANAGER_USERNAME}"),
            types.InlineKeyboardButton("⬅️ Назад", callback_data="to_main")
        )
        safe_edit_text(cid, mid, faq_text, m)

    elif data == "faq_how_to_pay":
        pay_text = (
            f"💳 <b>КАК ОПЛАТИТЬ ЗАКАЗ? — ИНСТРУКЦИЯ</b>\n"
            f"━━━━━━━━━━━━━━━━━━━━━━━━━━\n\n"
            f"Для максимальной безопасности мы принимаем два основных метода оплаты:\n\n"
            f"1️⃣ <b>Криптовалюта Bitcoin (BTC):</b>\n"
            f"• Полностью автоматический способ. Выбирайте оплату через BTC в чеке;\n"
            f"• Бот рассчитает сумму в сатоши по текущему курсу;\n"
            f"• Переведите монеты на адрес кошелька, и после 1-го подтверждения бот выдаст заказ.\n\n"
            f"2️⃣ <b>Банковская карта:</b>\n"
            f"• Оформите заказ, выбрав нужный банк в списке;\n"
            f"• Бот сформирует чек. Скопируйте его и отправьте оператору <b>@{MANAGER_USERNAME}</b>;\n"
            f"• Оператор выдаст свежие реквизиты. После подтверждения оплаты в течение 10-20 минут будут выданны координаты с подробным фото и описанием места.\n\n"
            f"⚠️ <i>Не задерживайте оплату после получения реквизитов! Время жизни реквизитов карт — 10 минут.</i>"
        )
        m = types.InlineKeyboardMarkup(row_width=1)
        m.add(
            types.InlineKeyboardButton("⬅️ Назад к FAQ", callback_data="faq_menu"),
            types.InlineKeyboardButton("🏠 Главное меню", callback_data="to_main")
        )
        safe_edit_text(cid, mid, pay_text, m)

    elif data == "faq_not_found":
        nf_text = (
            f"🔍 <b>ЧТО ДЕЛАТЬ, ЕСЛИ НЕ НАШЛИ КЛАД?</b>\n"
            f"━━━━━━━━━━━━━━━━━━━━━━━━━━\n\n"
            f"Самое главное — сохраняйте спокойствие. Мы дорожим клиентами и всегда помогаем в спорных ситуациях. Следуйте инструкции:\n\n"
            f"1️⃣ <b>Проверьте правильность поисков:</b>\n"
            f"• Убедитесь, что вы находитесь именно на тех координатах. Сравните ориентиры с фото курьера;\n"
            f"• Обязательно используйте камеру <b>NoteCam</b> (она фиксирует точное время и GPS-координаты на снимке).\n\n"
            f"2️⃣ <b>Сделайте фотографии:</b>\n"
            f"• Сделайте минимум 2 качественных фото с тех же ракурсов, что и на фото курьера: вблизи (место раскопа) и издалека (общий план);\n"
            f"• На фото не должно быть посторонних людей, ваших пальцев у объектива или смазанных деталей.\n\n"
            f"3️⃣ <b>Создайте обращение:</b>\n"
            f"• Передайте фотографии и ваш Чек заказа менеджеру <b>@{MANAGER_USERNAME}</b>;\n"
            f"• Обращения принимаются строго в течение 24 часов с момента покупки. Диспуты рассматриваются индивидуально. Будьте вежливы!"
        )
        m = types.InlineKeyboardMarkup(row_width=1)
        m.add(
            types.InlineKeyboardButton("⬅️ Назад к FAQ", callback_data="faq_menu"),
            types.InlineKeyboardButton("🏠 Главное меню", callback_data="to_main")
        )
        safe_edit_text(cid, mid, nf_text, m)

    elif data == "faq_delivery_time":
        dt_text = (
            f"⏳ <b>СРОКИ ВЫДАЧИ И ДОСТАВКИ</b>\n"
            f"━━━━━━━━━━━━━━━━━━━━━━━━━━\n\n"
            f"🚀 <b>Мгновенные готовые клады:</b>\n"
            f"Все позиции, доступные в каталоге нашего бота, уже надежно заложены нашими профессиональными курьерами в указанных районах и городах. Вы получаете точные координаты, метку на карте и подробное описание места моментально после подтверждения транзакции.\n\n"
            f"📮 <b>Индивидуальная доставка в любой город/район:</b>\n"
            f"Если вы не нашли нужный район или вашего населенного пункта нет в списке — не волнуйтесь! Мы осуществляем оперативную заказную доставку в любую точку:\n"
            f"• Отправка посылок (Почта / СДЭК) производится в течение 24-48 часов с использованием профессиональной маскировки (стелс), исключающей любые подозрения;\n"
            f"• Также возможен индивидуальный предзаказ на закладку в удобном для вас районе через согласование с менеджером."
        )
        m = types.InlineKeyboardMarkup(row_width=1)
        m.add(
            types.InlineKeyboardButton("⬅️ Назад к FAQ", callback_data="faq_menu"),
            types.InlineKeyboardButton("🏠 Главное меню", callback_data="to_main")
        )
        safe_edit_text(cid, mid, dt_text, m)

    elif data == "faq_security":
        sec_text = (
            f"🛡️ <b>БЕЗОПАСНОСТЬ И АНОНИМНОСТЬ</b>\n"
            f"━━━━━━━━━━━━━━━━━━━━━━━━━━\n\n"
            f"Мы гарантируем полную безопасность при взаимодействии с {SHOP_NAME}:\n\n"
            f"• <b>Удаление данных и анонимность:</b> Вся информация о ваших покупках, адресах и локациях мгновенно шифруется на сервере. Логи диалогов с ботом и история запросов безвозвратно удаляются автоматически в целях вашей безопасности.\n\n"
            f"• <b>Безопасные транзакции по картам:</b> При оплате банковской картой все платежи проходят через зашифрованные транзитные шлюзы. Данные вашей личной карты нигде не сохраняются, а история переводов автоматически аннулируется банком-партнером сразу после подтверждения транзакции.\n\n"
            f"• <b>Анонимные крипто-кошельки:</b> Все блокчейн-платежи (BTC) автоматически направляются через каскадные миксеры высокой степени очистки, что делает отслеживание конечного отправителя абсолютно невозможным.\n\n"
            f"• <b>Рекомендация по безопасности:</b> Для максимального уровня конфиденциальности мы настоятельно советуем использовать надежный VPN/Proxy-сервис при работе с Telegram, а также установить облачный пароль (Two-Step Verification) на ваш аккаунт."
        )
        m = types.InlineKeyboardMarkup(row_width=1)
        m.add(
            types.InlineKeyboardButton("⬅️ Назад к FAQ", callback_data="faq_menu"),
            types.InlineKeyboardButton("🏠 Главное меню", callback_data="to_main")
        )
        safe_edit_text(cid, mid, sec_text, m)

    # --- РАЗДЕЛ ГЕО-ПОДПИСКИ ---
    elif data == "geo_sub_menu":
        u = db.fetchone("SELECT city FROM users WHERE uid=?", (uid,))
        city = u[0] if u and u[0] else None
        
        if not city:
            m = types.InlineKeyboardMarkup(row_width=1)
            m.add(
                types.InlineKeyboardButton("🌐 Выбрать город", callback_data="loc"),
                types.InlineKeyboardButton("⬅️ Назад", callback_data="to_main")
            )
            return safe_edit_text(cid, mid, "⚠️ <b>У вас не выбран город!</b>\nПожалуйста, сначала укажите вашу локацию, чтобы настроить уведомления о пополнениях.", m)
        
        # Проверяем подписку на текущий город
        is_subbed = db.fetchone("SELECT uid FROM subscriptions WHERE uid=? AND city=?", (uid, city)) is not None
        sub_status = "🔔 <b>Вы ПОДПИСАНЫ</b> на обновления" if is_subbed else "🔕 <b>Вы НЕ ПОДПИСАНЫ</b> на обновления"
        
        # Получаем список ВСЕХ подписок пользователя
        all_subs = db.fetchall("SELECT city FROM subscriptions WHERE uid=?", (uid,))
        subs_list_str = ""
        if all_subs:
            subs_list_str = "\n\n📋 <b>Ваши активные подписки:</b>\n" + ", ".join([f"📍 <b>{s[0]}</b>" for s in all_subs])
        else:
            subs_list_str = "\n\n📋 <b>У вас нет активных подписок.</b>"
        
        sub_text = (
            f"🔔 <b>ГЕО-ПОДПИСКА НА ПОПОЛНЕНИЯ</b>\n"
            f"━━━━━━━━━━━━━━━━━━━━━━━━━━\n\n"
            f"📍 Ваш текущий город: <b>{city}</b>\n"
            f"📊 Текущий статус: {sub_status}"
            f"{subs_list_str}\n\n"
            f"Хотите оперативно узнавать о свежих пополнениях витрины выбранных городов? "
            f"Подпишитесь! Как только администратор обновит каталог в регионе, "
            f"вы мгновенно получите пуш-уведомление прямо в этот чат!"
        )
        
        m = types.InlineKeyboardMarkup(row_width=1)
        if is_subbed:
            m.add(types.InlineKeyboardButton(f"🔕 Отписаться от г. {city}", callback_data=f"geo_unsub_{city}"))
        else:
            m.add(types.InlineKeyboardButton(f"🔔 Подписаться на г. {city}", callback_data=f"geo_sub_{city}"))
        
        # Если есть хотя бы одна подписка, добавляем кнопку "Отписаться от всех"
        if all_subs:
            m.add(types.InlineKeyboardButton("🔕 Отписаться от ВСЕХ городов", callback_data="geo_unsub_all"))
            
        m.add(types.InlineKeyboardButton("⬅️ Назад в меню", callback_data="to_main"))
        safe_edit_text(cid, mid, sub_text, m)

    elif data == "geo_unsub_all":
        db.execute("DELETE FROM subscriptions WHERE uid=?", (uid,))
        bot.answer_callback_query(c.id, "🎉 Вы успешно отписались от всех городов!", show_alert=True)
        c.data = "geo_sub_menu"
        handle_cb(c)

    elif data.startswith("geo_sub_"):
        city = data.replace("geo_sub_", "")
        db.execute("INSERT OR IGNORE INTO subscriptions (uid, city) VALUES (?, ?)", (uid, city))
        bot.answer_callback_query(c.id, f"🎉 Вы успешно подписались на обновления в г. {city}!", show_alert=True)
        c.data = "geo_sub_menu"
        handle_cb(c)

    elif data.startswith("geo_unsub_"):
        city = data.replace("geo_unsub_", "")
        db.execute("DELETE FROM subscriptions WHERE uid=? AND city=?", (uid, city))
        bot.answer_callback_query(c.id, f"🔕 Вы отписались от уведомлений г. {city}.", show_alert=True)
        c.data = "geo_sub_menu"
        handle_cb(c)

    elif data == "rules_menu":
        rules_text = (
            f"📜 <b>ПРАВИЛА И РЕГЛАМЕНТ {SHOP_NAME}</b>\n"
            f"━━━━━━━━━━━━━━━━━━━━━━━━━━\n\n"
            f"Мы работаем для Вас круглосуточно 24/7. Прежде чем совершить покупку, пожалуйста, ознакомьтесь с нашими подробными правилами. "
            f"Совершая оплату, Вы автоматически соглашаетесь с каждым приведенным ниже пунктом:\n\n"
            f"1️⃣ <b>Правила диспутов по ненаходам:</b>\n"
            f"• Претензии принимаются строго в течение 24 часов с момента получения адреса. Позже этого срока диспут не рассматривается;\n"
            f"• В обращении обязательно укажите: наименование товара, вес, точное время Вашего прибытия и координаты;\n"
            f"• Предоставьте 2 качественных, четких фото с места поисков (вблизи и издалека, с тех же ракурсов, что и на фото курьера);\n"
            f"• В случае несовпадения координат допускается погрешность до 5 метров. При этом обязательно использовать камеру NoteCam;\n"
            f"• Перезаклады и компенсации возможны только после 5 успешных заказов на Вашем аккаунте.\n\n"
            f"2️⃣ <b>Недовесы и качество стаффа:</b>\n"
            f"• Претензии по недовесу рассматриваются только при наличии непрерывного видео распаковки. На видео должны быть откалиброванные "
            f"электронные весы с точностью 0.01г, процесс калибровки контрольной монетой, взвешивание товара в упаковке и без нее;\n"
            f"• Претензии по качеству принимаются только с четким фото вещества на темном матовом фоне без зип-пакета.\n\n"
            f"3️⃣ <b>Работа курьерской службы:</b>\n"
            f"• Все клады упаковываются в герметичный вакуум и плотный слой изоленты. Запрещено производить поиски в присутствии третьих лиц "
            f"или портить окружающую инфраструктуру.\n\n"
            f"4️⃣ <b>Культура общения с администрацией:</b>\n"
            f"• Ведите себя сдержанно, не грубите сотрудникам. Любая нецензурная брань, капс, оскорбления, флуд или угрозы оператору "
            f"ведут к мгновенной блокировке Вашего аккаунта без права перезаклада и обнулению баланса.\n\n"
            f"Мы любим свою работу и ценим каждого адекватного покупателя! Желаем приятных покупок!"
        )
        m = types.InlineKeyboardMarkup(row_width=1)
        m.add(types.InlineKeyboardButton("⬅️ Назад", callback_data="to_main"))
        safe_edit_text(cid, mid, rules_text, m)

    elif data == "bonuses":
        # Получение динамических данных о балансе
        ref_count = db.fetchone("SELECT COUNT(*) FROM users WHERE referrer_id=?", (uid,))[0]
        balance_row = db.fetchone("SELECT balance FROM users WHERE uid=?", (uid,))
        balance = balance_row[0] if balance_row and balance_row[0] is not None else 0.0

        bonus_text = (
            f"🎁 <b>МНОГОУРОВНЕВАЯ БОНУСНАЯ ПРОГРАММА {SHOP_NAME}</b>\n"
            f"━━━━━━━━━━━━━━━━━━━━━━━━━━\n\n"
            f"Добро пожаловать в нашу щедрую партнерскую систему! Мы выплачиваем реальные вознаграждения за рекомендации.\n\n"
            f"💸 <b>Как это работает?</b>\n"
            f"1️⃣ Вы делитесь своей персональной ссылкой с друзьями.\n"
            f"2️⃣ За каждого пользователя, перешедшего по ней и запустившего бота, вам мгновенно начисляется <b>0.50 USD</b>!\n"
            f"3️⃣ Дополнительно вы получаете <b>3%</b> от всех покупок ваших приглашенных рефералов.\n\n"
            f"📊 <b>Ваша статистика приглашений:</b>\n"
            f" ┣ Приглашено человек: 🧑‍🤝‍🧑 <b>{ref_count} чел.</b>\n"
            f" ┗ Доступный баланс: 💵 <b>{balance:.2f} USD</b>\n\n"
            f"🎟️ <b>Магазин промокодов:</b>\n"
            f"<i>Вы можете обменять свой накопленный реферальный баланс на личные промокоды со скидкой до 20%!</i>\n\n"
            f"🔗 <b>Ваша персональная партнерская ссылка:</b>\n"
            f"<code>https://t.me/{BOT_USERNAME}?start=r_{uid}</code>\n"
            f"━━━━━━━━━━━━━━━━━━━━━━━━━━\n"
        )
        m = types.InlineKeyboardMarkup(row_width=1)
        m.add(
            types.InlineKeyboardButton("🎟️ Купить промокод", callback_data="buy_promo_store"),
            types.InlineKeyboardButton("⬅️ Назад", callback_data="to_main")
        )
        safe_edit_text(cid, mid, bonus_text, m)

    elif data == "buy_promo_store":
        balance_row = db.fetchone("SELECT balance FROM users WHERE uid=?", (uid,))
        balance = balance_row[0] if balance_row and balance_row[0] is not None else 0.0

        store_text = (
            f"🎟️ <b>МАГАЗИН СКИДОЧНЫХ ПРОМОКОДОВ</b>\n"
            f"━━━━━━━━━━━━━━━━━━━━━━━━━━\n"
            f"Ваш текущий баланс: 💵 <b>{balance:.2f} USD</b>\n\n"
            f"Выберите нужный вам номинал скидки для покупки:\n"
            f"• <b>Скидка 5%</b> — Стоимость: <b>5.00 USD</b> (Нужно пригласить 10 человек)\n"
            f"• <b>Скидка 10%</b> — Стоимость: <b>7.50 USD</b> (Нужно пригласить 15 человек)\n"
            f"• <b>Скидка 20%</b> — Стоимость: <b>10.00 USD</b> (Нужно пригласить 20 человек)\n\n"
            f"<i>После покупки промокод автоматически запишется в базу данных и станет доступен для ввода при оформлении заказа!</i>"
        )
        m = types.InlineKeyboardMarkup(row_width=2)
        m.add(
            types.InlineKeyboardButton("🎟️ Скидка 5% ($5.0)", callback_data="buy_promo_action_5"),
            types.InlineKeyboardButton("🎟️ Скидка 10% ($7.5)", callback_data="buy_promo_action_10")
        )
        m.add(
            types.InlineKeyboardButton("🎟️ Скидка 20% ($10.0)", callback_data="buy_promo_action_20")
        )
        m.add(types.InlineKeyboardButton("⬅️ Назад к бонусам", callback_data="bonuses"))
        safe_edit_text(cid, mid, store_text, m)

    elif data.startswith("buy_promo_action_"):
        parts = data.split("_")
        discount = int(parts[3])
        cost = 5.00 if discount == 5 else (7.50 if discount == 10 else 10.00)

        balance_row = db.fetchone("SELECT balance FROM users WHERE uid=?", (uid,))
        balance = balance_row[0] if balance_row and balance_row[0] is not None else 0.0

        if balance >= cost:
            # Снимаем средства с баланса
            new_balance = balance - cost
            db.execute("UPDATE users SET balance=? WHERE uid=?", (new_balance, uid))
            
            # Генерируем промокод
            generated_code = f"REF-{discount}-{str(uuid.uuid4())[:6].upper()}"
            db.execute("INSERT INTO promocodes (code, discount) VALUES (?,?)", (generated_code, discount))

            success_text = (
                f"🎉 <b>ПОКУПКА УСПЕШНО СОВЕРШЕНА!</b>\n"
                f"━━━━━━━━━━━━━━━━━━━━━━━━━━\n\n"
                f"Вы успешно приобрели скидочный промокод!\n"
                f"• Списано с баланса: 💵 <b>{cost:.2f} USD</b>\n"
                f"• Ваш новый баланс: 💵 <b>{new_balance:.2f} USD</b>\n\n"
                f"🎟️ Ваш промокод на скидку <b>{discount}%</b>:\n"
                f"<code>{generated_code}</code>\n\n"
                f"<i>Скопируйте его и введите при оплате любого товара на чеке заказа для моментального получения скидки!</i>"
            )
            m = types.InlineKeyboardMarkup(row_width=1)
            m.add(
                types.InlineKeyboardButton("🛍️ В каталог", callback_data="shop"),
                types.InlineKeyboardButton("⬅️ Вернуться в магазин", callback_data="buy_promo_store")
            )
            safe_edit_text(cid, mid, success_text, m)
        else:
            bot.answer_callback_query(c.id, f"❌ Недостаточно средств! Необходимый баланс: {cost} USD. У вас: {balance} USD.", show_alert=True)

    elif data == "doctor_tips":
        doc_text = (
            f"⚕️ <b>СОВЕТЫ НАРКОЛОГА & HARM REDUCTION</b>\n"
            f"━━━━━━━━━━━━━━━━━━━━━━━━━━\n\n"
            f"Безопасность наших клиентов — главный приоритет. Все позиции в каталоге {SHOP_NAME} проходят тщательный "
            f"лабораторный анализ, что исключает наличие опасных химических примесей и побочных реагентов.\n\n"
            f"⚠️ <b>КЛЮЧЕВЫЕ ПРАВИЛА БЕЗОПАСНОГО ТРИПА:</b>\n\n"
            f"1️⃣ <b>Микродозирование и тест-доза:</b>\n"
            f"Всегда начинайте с 1/4 от стандартной терапевтической порции. Любая новая партия требует аккуратного теста.\n\n"
            f"2️⃣ <b>Критический контроль гидратации:</b>\n"
            f"Пейте ровно 250-300 мл чистой негазированной воды или аптечного раствора электролитов (например, Регидрон) каждый час. "
            f"Недостаток воды сгущает кровь и перегружает почки, а переизбыток вреден для солевого баланса.\n\n"
            f"3️⃣ <b>Категорический отказ от полисубстанциональности (смешивания):</b>\n"
            f"Никогда не совмещайте стимуляторы, эйфоретики или психоделики с алкоголем. Алкоголь маскирует первые симптомы передозировки "
            f"и наносит сокрушительный токсический удар по печени и сердцу.\n\n"
            f"4️⃣ <b>Правило ситтера (трип-репортера):</b>\n"
            f"Если вы пробуете сильное вещество, убедитесь, что рядом находится доверенный трезвый человек, "
            f"который сможет оказать психологическую поддержку или вызвать помощь.\n\n"
            f"5️⃣ <b>Процесс восстановления (Post-Trip Care):</b>\n"
            f"После окончания сессии организму требуется полноценный сон (не менее 8 часов), легкоусвояемые белки "
            f"и комплекс витаминов (группы B, C, магний, аминокислота 5-HTP для восстановления уровня серотонина)."
        )
        m = types.InlineKeyboardMarkup(row_width=1)
        m.add(types.InlineKeyboardButton("⬅️ Назад", callback_data="to_main"))
        safe_edit_text(cid, mid, doc_text, m)

    elif data == "job":
        job_text = (
            f"💼 <b>РАБОТА В КОМАНДЕ {SHOP_NAME}</b>\n"
            f"━━━━━━━━━━━━━━━━━━━━━━━━━━\n\n"
            f"Мы всегда в поиске ответственных сотрудников на высокооплачиваемые позиции. Гарантируем полную анонимность, безопасность и своевременные выплаты в криптовалюте или на карты любых банков.\n\n"
            f"📦 <b>Розничный курьер (Кладмен):</b>\n"
            f" ┣ Оплата от 15 до 25 USD за один успешно сделанный и закрытый клад;\n"
            f" ┣ Полностью свободный график работы (вы сами выбираете удобное время);\n"
            f" ┣ Подробное пошаговое обучение по методам маскировки, выбору безопасных мест и беспалевному съёму;\n"
            f" ┗ <b>Обязательное условие: залог ВСЕГО ОТ 20 USD (менее 25$) ИЛИ под залог фото вашего паспорта (абсолютно без денежного взноса) для обеспечения сохранности первой партии товара.</b>\n\n"
            f"🏢 <b>Склад / Фасовщик:</b>\n"
            f" ┣ Прием мастер-кладов крупных весов и фасовка на мелкорозничные партии;\n"
            f" ┗ Оплата от 3000 USD в неделю. <b>Требуется максимальная осторожность и залог всего от 25 USD (либо под залог паспорта).</b>\n\n"
            f"📣 <b>Пиар-менеджер (TikTok / Shorts):</b>\n"
            f" ┣ Обязанности: Креативное комментирование в TikTok и на других площадках с продвижением юзернейма нашего бота;\n"
            f" ┣ Оплата: Стабильная заработная плата от <b>100 USD</b> в неделю за активное участие;\n"
            f" ┗ <b>Выплаты: Осуществляются строго через две недели работы после полной проверки проделанной активности.</b>\n\n"
            f"🚚 <b>Доставщик (Перевозчик):</b>\n"
            f" ┗ Транспортировка крупных партий между городами на авто. Сверхвысокая оплата, <b>залог всего от 25 USD (либо под залог паспорта).</b>\n\n"
            f"📞 За деталями пишите нашему менеджеру."
        )
        m = types.InlineKeyboardMarkup(row_width=1)
        m.add(
            types.InlineKeyboardButton("✉️ Написать менеджеру", url=f"https://t.me/{MANAGER_USERNAME}"),
            types.InlineKeyboardButton("⬅️ Назад", callback_data="to_main")
        )
        safe_edit_text(cid, mid, job_text, m)

    elif data.startswith("rev_list_"):
        parts = data.split("_")
        idx = int(parts[2])
        revs = db.fetchall("SELECT text, prod FROM reviews ORDER BY id DESC")
        if not revs:
            m = types.InlineKeyboardMarkup(row_width=1)
            m.add(types.InlineKeyboardButton("⬅️ Назад", callback_data="to_main"))
            return safe_edit_text(cid, mid, "Отзывов пока нет.", m)
            
        idx = idx % len(revs)
        r = revs[idx]
        
        #        # Динамический подсчет количества отзывов от базовой цифры
        actual_rev_count = db.fetchone("SELECT COUNT(*) FROM reviews")[0]
        total_reviews_display = f"{35790 + actual_rev_count:,}".replace(",", " ")
        
        txt = (f"💬 <b>Отзывы клиентов ({total_reviews_display} шт.)</b>\n"
               f"⭐️ Средняя оценка: 4.9/5.0\n\n"
               f"👤 Автор: Аноним\n"
               f"🛍️ Товар: {r[1]}\n"
               f"💬 Отзыв: <i>{r[0]}</i>")
        m = types.InlineKeyboardMarkup(row_width=2)
        m.add(
            types.InlineKeyboardButton("⬅️ Предыдущий", callback_data=f"rev_list_{idx-1}"),
            types.InlineKeyboardButton("Следующий ➡️", callback_data=f"rev_list_{idx+1}")
        )
        m.add(types.InlineKeyboardButton("🏠 Главное меню", callback_data="to_main"))
        safe_edit_text(cid, mid, txt, m)

    elif data == "loc":
        m = types.InlineKeyboardMarkup(row_width=2)
        for country in COUNTRIES_KEYS:
            m.add(types.InlineKeyboardButton(country, callback_data=f"cnt_{country}_0"))
        m.add(types.InlineKeyboardButton("⬅️ Назад", callback_data="to_main"))
        safe_edit_text(cid, mid, "<b>Выберите интересующую вас страну:</b>", m)

    elif data.startswith("cnt_"):
        p = data.split("_")
        cnt = p[1]
        page = int(p[2])
        cities = COUNTRIES_DATA[cnt]
        
        start = page * 10
        end = start + 10
        m = types.InlineKeyboardMarkup(row_width=2)
        for city in cities[start:end]:
            cnt_idx = COUNTRIES_KEYS.index(cnt)
            city_idx = COUNTRIES_DATA[cnt].index(city)
            m.add(types.InlineKeyboardButton(city, callback_data=f"set_{cnt_idx}_{city_idx}"))
        
        nav_buttons = []
        if page > 0:
            nav_buttons.append(types.InlineKeyboardButton("⬅️ Назад", callback_data=f"cnt_{cnt}_{page-1}"))
        if end < len(cities):
            nav_buttons.append(types.InlineKeyboardButton("Вперед ➡️", callback_data=f"cnt_{cnt}_{page+1}"))
        if nav_buttons:
            m.add(*nav_buttons)
        
        m.add(types.InlineKeyboardButton("📮 Нет вашего города? Заказать доставку", callback_data="custom_delivery"))
        m.add(types.InlineKeyboardButton("🌍 К списку стран", callback_data="loc"))
        safe_edit_text(cid, mid, f"<b>Выберите город в стране {cnt} (страница {page+1}):</b>", m)

    elif data == "custom_delivery":
        delivery_text = (
            "📮 <b>Доставка в любой населенный пункт</b>\n"
            "━━━━━━━━━━━━━━━━━━━━━━━━━━\n\n"
            "Если вы не нашли свой город в списке доступных локаций, вы можете заказать "
            "индивидуальную отправку в ваш регион (почтой или специализированным курьером).\n\n"
            "💬 Для обсуждения деталей и оформления заказа свяжитесь с нашим оператором."
        )
        m = types.InlineKeyboardMarkup(row_width=1)
        m.add(
            types.InlineKeyboardButton("💬 Написать оператору", url=f"https://t.me/{MANAGER_USERNAME}"),
            types.InlineKeyboardButton("⬅️ Назад", callback_data="loc")
        )
        safe_edit_text(cid, mid, delivery_text, m)

    elif data.startswith("set_"):
        parts = data.split("_")
        cnt_idx = int(parts[1])
        city_idx = int(parts[2])
        cnt = COUNTRIES_KEYS[cnt_idx]
        city = COUNTRIES_DATA[cnt][city_idx]
        
        districts = get_districts_for_city(city)
        m = types.InlineKeyboardMarkup(row_width=1)
        for d_idx, dist in enumerate(districts):
            m.add(types.InlineKeyboardButton(dist, callback_data=f"sd_{cnt_idx}_{city_idx}_{d_idx}"))
        m.add(types.InlineKeyboardButton("⬅️ Назад к выбору городов", callback_data=f"cnt_{cnt}_0"))
        safe_edit_text(cid, mid, f"<b>Выберите район в городе {city}:</b>", m)

    elif data.startswith("sd_"):
        parts = data.split("_")
        cnt_idx = int(parts[1])
        city_idx = int(parts[2])
        d_idx = int(parts[3])
        cnt = COUNTRIES_KEYS[cnt_idx]
        city = COUNTRIES_DATA[cnt][city_idx]
        district = get_districts_for_city(city)[d_idx]
        
        db.execute("UPDATE users SET city=?, country=?, district=? WHERE uid=?", (city, cnt, district, uid))
        bot.answer_callback_query(c.id, f"Установлен район: {district}")
        show_main_menu(cid, mid, uid)

    elif data == "shop":
        u = db.fetchone("SELECT city, country FROM users WHERE uid=?", (uid,))
        if not u or not u[0]:
            return bot.answer_callback_query(c.id, "Сначала выберите локацию!", show_alert=True)
        curr = CURRENCY_MAP.get(u[1], 'USD')
        rate = EXCHANGE_RATES.get(curr, 1.0)
        prods = db.fetchall("SELECT p.id, p.name, p.price FROM products p JOIN stock s ON p.id = s.product_id WHERE s.city = ?", (u[0],))
        m = types.InlineKeyboardMarkup(row_width=1)
        for pid, name, price in prods:
            m.add(types.InlineKeyboardButton(f"{name.upper()} — {round(price*rate, 1)} {curr}", callback_data=f"buy_{pid}"))
        m.add(types.InlineKeyboardButton("⬅️ Назад", callback_data="to_main"))
        safe_edit_text(cid, mid, f"<b>Каталог позиций для города {u[0]}:</b>", m)

    elif data.startswith("buy_"):
        parts = data.split("_")
        pid = parts[1]
        p = db.fetchone("SELECT name, price FROM products WHERE id=?", (pid,))
        u = db.fetchone("SELECT city, country, district FROM users WHERE uid=?", (uid,))
        curr = CURRENCY_MAP.get(u[1], 'USD')
        rate = EXCHANGE_RATES.get(curr, 1.0)
        
        med_card = get_product_medical_card(p[0])
        
        m = types.InlineKeyboardMarkup(row_width=1)
        # Настройка весов и мультипликаторов стоимости, чтобы цены находились в строго реальном диапазоне (от 25$ до 300$)
        for w_label, w_idx in [("1г", "1"), ("2г", "2"), ("3г", "3"), ("5г", "5")]:
            mult = 1 if w_idx == "1" else (1.9 if w_idx == "2" else (2.8 if w_idx == "3" else 4.2))
            p_val = round(p[1]*mult*rate, 1)
            # Передаем в callback выбор действия (в 1 клик или в корзину)
            m.add(types.InlineKeyboardButton(f"{w_label} — {p_val} {curr}", callback_data=f"sel_act_{pid}_{w_idx}"))
        m.add(types.InlineKeyboardButton("⬅️ К каталогу", callback_data="shop"))
        
        full_info = (
            f"📦 Товар: <b>{p[0]}</b>\n\n"
            f"{med_card}\n\n"
            f"<b>Выберите интересующий вес:</b>"
        )
        safe_edit_text(cid, mid, full_info, m)

    elif data.startswith("sel_act_"):
        parts = data.split("_")
        pid = parts[2]
        w_idx = parts[3]
        p = db.fetchone("SELECT name, price FROM products WHERE id=?", (pid,))
        u = db.fetchone("SELECT city, country, district FROM users WHERE uid=?", (uid,))
        curr = CURRENCY_MAP.get(u[1], 'USD')
        rate = EXCHANGE_RATES.get(curr, 1.0)
        mult = 1 if w_idx == "1" else (1.9 if w_idx == "2" else (2.8 if w_idx == "3" else 4.2))
        p_val = round(p[1]*mult*rate, 1)
        
        text = (
            f"📦 Товар: <b>{p[0]}</b>\n"
            f"⚖️ Выбранный вес: <b>{w_idx}г</b>\n"
            f"💰 Стоимость: <b>{p_val} {curr}</b>\n"
            f"📍 Район: <b>{u[2] if u[2] else 'Не выбран'}</b>\n\n"
            f"Выберите дальнейшее действие:"
        )
        m = types.InlineKeyboardMarkup(row_width=1)
        m.add(
            types.InlineKeyboardButton("⚡ Продолжить оформление заказа", callback_data=f"ras_{pid}_{w_idx}"),
            types.InlineKeyboardButton("🛒 Добавить в корзину", callback_data=f"add_to_cart_{pid}_{w_idx}"),
            types.InlineKeyboardButton("⬅️ Изменить вес", callback_data=f"buy_{pid}")
        )
        safe_edit_text(cid, mid, text, m)

    # --- СИСТЕМА КОРЗИНЫ ---
    elif data.startswith("add_to_cart_"):
        parts = data.split("_")
        pid = parts[3]
        w_idx = parts[4]
        p = db.fetchone("SELECT name FROM products WHERE id=?", (pid,))
        u = db.fetchone("SELECT district FROM users WHERE uid=?", (uid,))
        district = u[0] if u and u[0] else "Не указан"
        
        db.execute("INSERT INTO cart (uid, product_id, weight_idx, district) VALUES (?, ?, ?, ?)", (uid, pid, w_idx, district))
        
        text = (
            f"🛒 Товар <b>{p[0]}</b> ({w_idx}г) успешно добавлен в вашу корзину!\n\n"
            f"Вы можете продолжить выбор товаров в каталоге или перейти к оформлению заказа всей корзины одним общим чеком."
        )
        m = types.InlineKeyboardMarkup(row_width=2)
        m.row(
            types.InlineKeyboardButton("🛍️ В корзину", callback_data="view_cart"),
            types.InlineKeyboardButton("🛒 Продолжить покупки", callback_data="shop")
        )
        m.row(types.InlineKeyboardButton("🏠 На главную", callback_data="to_main"))
        safe_edit_text(cid, mid, text, m)

    elif data == "view_cart":
        u = db.fetchone("SELECT city, country FROM users WHERE uid=?", (uid,))
        if not u or not u[0]:
            return bot.answer_callback_query(c.id, "Сначала выберите локацию!", show_alert=True)
        
        curr = CURRENCY_MAP.get(u[1], 'USD')
        rate = EXCHANGE_RATES.get(curr, 1.0)
        
        cart_items = db.fetchall("SELECT c.id, p.name, p.price, c.weight_idx, c.district FROM cart c JOIN products p ON c.product_id = p.id WHERE c.uid = ?", (uid,))
        
        if not cart_items:
            m = types.InlineKeyboardMarkup(row_width=1)
            m.add(
                types.InlineKeyboardButton("🛒 В каталог", callback_data="shop"),
                types.InlineKeyboardButton("🏠 Главное меню", callback_data="to_main")
            )
            return safe_edit_text(cid, mid, "🛒 <b>Ваша корзина пуста!</b>\n\nПерейдите в каталог, чтобы добавить товары.", m)
        
        total_price = 0.0
        text = "🛒 <b>СОДЕРЖИМОЕ ВАШЕЙ КОРЗИНЫ</b>\n"
        text += f"📍 Локация: {u[0]} ({u[1]})\n"
        text += "━━━━━━━━━━━━━━━━━━━━━━━━━━\n\n"
        
        for idx, (cart_id, name, price, w_idx, dist) in enumerate(cart_items, 1):
            mult = 1 if w_idx == "1" else (1.9 if w_idx == "2" else (2.8 if w_idx == "3" else 4.2))
            item_price = round(price * mult * rate, 1)
            total_price += item_price
            
            text += f"{idx}. 📦 <b>{name}</b> ({w_idx}г)\n"
            text += f" ┣ Район: 🗺️ {dist}\n"
            text += f" ┗ Стоимость: 💵 <b>{item_price} {curr}</b>\n\n"
            
        text += "━━━━━━━━━━━━━━━━━━━━━━━━━━\n"
        text += f"💳 <b>ИТОГО К ОПЛАТЕ: {total_price:.1f} {curr}</b>"
        
        m = types.InlineKeyboardMarkup(row_width=1)
        m.add(
            types.InlineKeyboardButton("💳 Оформить общий заказ", callback_data="cart_checkout_delivery"),
            types.InlineKeyboardButton(f"📦 Товары ({len(cart_items)} поз.)", callback_data="cart_items_list"),
            types.InlineKeyboardButton("🛒 Продолжить покупки", callback_data="shop"),
            types.InlineKeyboardButton("🏠 Главное меню", callback_data="to_main")
        )
        
        safe_edit_text(cid, mid, text, m)

    elif data == "cart_items_list":
        u = db.fetchone("SELECT city, country FROM users WHERE uid=?", (uid,))
        curr = CURRENCY_MAP.get(u[1], 'USD')
        rate = EXCHANGE_RATES.get(curr, 1.0)
        
        cart_items = db.fetchall("SELECT c.id, p.name, p.price, c.weight_idx, c.district FROM cart c JOIN products p ON c.product_id = p.id WHERE c.uid = ?", (uid,))
        
        if not cart_items:
            m = types.InlineKeyboardMarkup(row_width=1)
            m.add(types.InlineKeyboardButton("⬅️ Назад в корзину", callback_data="view_cart"))
            return safe_edit_text(cid, mid, "🛒 <b>Ваша корзина пуста!</b>", m)
            
        text = "📋 <b>СПИСОК ТОВАРОВ В КОРЗИНЕ</b>\n<i>Здесь вы можете точечно удалить любой товар или полностью очистить корзину:</i>\n\n"
        
        m = types.InlineKeyboardMarkup(row_width=1)
        for idx, (cart_id, name, price, w_idx, dist) in enumerate(cart_items, 1):
            mult = 1 if w_idx == "1" else (1.9 if w_idx == "2" else (2.8 if w_idx == "3" else 4.2))
            item_price = round(price * mult * rate, 1)
            text += f"• 📦 <b>{name}</b> ({w_idx}г) — {item_price} {curr}\n"
            m.add(types.InlineKeyboardButton(f"❌ Удалить: {name} ({w_idx}г)", callback_data=f"del_cart_{cart_id}"))
            
        m.add(
            types.InlineKeyboardButton("❌ Очистить всю корзину", callback_data="cart_clear_all"),
            types.InlineKeyboardButton("⬅️ Назад к оплате", callback_data="view_cart")
        )
        safe_edit_text(cid, mid, text, m)

    elif data.startswith("del_cart_"):
        cart_id = data.replace("del_cart_", "")
        db.execute("DELETE FROM cart WHERE id=? AND uid=?", (cart_id, uid))
        bot.answer_callback_query(c.id, "Товар удален из корзины!")
        c.data = "cart_items_list"
        handle_cb(c)

    elif data == "cart_clear_all":
        db.execute("DELETE FROM cart WHERE uid=?", (uid,))
        bot.answer_callback_query(c.id, "Корзина полностью очищена!")
        c.data = "view_cart"
        handle_cb(c)

    elif data == "cart_checkout_delivery":
        count = db.fetchone("SELECT COUNT(*) FROM cart WHERE uid=?", (uid,))[0]
        if count == 0:
            return bot.answer_callback_query(c.id, "Ваша корзина пуста!", show_alert=True)
            
        m = types.InlineKeyboardMarkup(row_width=1)
        m.add(
            types.InlineKeyboardButton("📦 Клад - магнит", callback_data="cart_chk_dt_m"),
            types.InlineKeyboardButton("⛏️ Клад - прикоп", callback_data="cart_chk_dt_p"),
            types.InlineKeyboardButton("📬 Почта", callback_data="cart_chk_dt_t"),
            types.InlineKeyboardButton("⬅️ Назад в корзину", callback_data="view_cart")
        )
        safe_edit_text(cid, mid, "<b>Выберите предпочтительный тип доставки для всех товаров:</b>", m)

    elif data.startswith("cart_chk_dt_"):
        deliv_char = data.replace("cart_chk_dt_", "")
        u = db.fetchone("SELECT country FROM users WHERE uid=?", (uid,))
        m = types.InlineKeyboardMarkup(row_width=2)
        country_banks = get_payment_methods(u[0])
        
        for b_idx, b_name in enumerate(country_banks):
            m.add(types.InlineKeyboardButton(b_name.upper(), callback_data=f"cart_pay_{deliv_char}_{b_idx}"))
        
        m.add(types.InlineKeyboardButton("⬅️ Назад", callback_data="cart_checkout_delivery"))
        safe_edit_text(cid, mid, f"<b>Выберите способ оплаты ({u[0]}):</b>", m)

    elif data.startswith("cart_pay_"):
        parts = data.split("_")
        deliv_char = parts[2]
        b_idx = parts[3]
        
        u = db.fetchone("SELECT city, country FROM users WHERE uid=?", (uid,))
        curr = CURRENCY_MAP.get(u[1], 'USD')
        rate = EXCHANGE_RATES.get(curr, 1.0)
        
        cart_items = db.fetchall("SELECT p.name, p.price, c.weight_idx, c.district FROM cart c JOIN products p ON c.product_id = p.id WHERE c.uid = ?", (uid,))
        if not cart_items:
            return bot.answer_callback_query(c.id, "Ваша корзина пуста!", show_alert=True)
            
        total_price_curr = 0.0
        total_price_usd = 0.0
        items_details = []
        
        for name, price_usd, w_idx, dist in cart_items:
            mult = 1 if w_idx == "1" else (1.9 if w_idx == "2" else (2.8 if w_idx == "3" else 4.2))
            item_price_usd = price_usd * mult
            item_price_curr = round(item_price_usd * rate, 1)
            total_price_usd += item_price_usd
            total_price_curr += item_price_curr
            items_details.append(f"• 📦 <b>{name}</b> ({w_idx}г, р-н: {dist}) — {item_price_curr} {curr}")
            
        deliv_type = "Клад - магнит" if deliv_char == "m" else ("Клад - прикоп" if deliv_char == "p" else "Почта")
        payment_methods = get_payment_methods(u[1])
        bank_name = payment_methods[int(b_idx)]
        order_id = "CRT-" + str(uuid.uuid4())[:6].upper()
        
        # Если оплата в BTC:
        if b_idx == "0":
            btc_price = round(total_price_usd / BTC_USD_RATE, 6)
            price_text = f"<b>{btc_price} BTC</b> (~{total_price_curr:.1f} {curr})"
        else:
            price_text = f"<b>{total_price_curr:.1f} {curr}</b>"

        items_text = "\n".join(items_details)
        
        check = (f"🧾 <b>Чек заказа #{order_id} (КОРЗИНА)</b>\n"
                 f"━━━━━━━━━━━━━━━━━━━━━━━━━━\n"
                 f" 📍 Город: {u[0]}\n"
                 f" 🚚 Тип доставки: {deliv_type}\n"
                 f" 💳 Способ оплаты: {bank_name}\n"
                 f" 💵 Сумма к оплате: {price_text}\n"
                 f"━━━━━━━━━━━━━━━━━━━━━━━━━━\n"
                 f"📋 <b>Содержимое заказа:</b>\n"
                 f"{items_text}\n"
                 f"━━━━━━━━━━━━━━━━━━━━━━━━━━\n"
                 f"⚠️ <b>ОБЯЗАТЕЛЬНО СКОПИРУЙТЕ И ОТПРАВЬТЕ ЭТОТ ЧЕК НАШЕМУ ОПЕРАТОРУ ДЛЯ ПОЛУЧЕНИЯ РЕКВИЗИТОВ ДЛЯ ОПЛАТЫ!</b> Без предоставления чека реквизиты на оплату не выдаются, а ваш платеж не сможет быть зачислен оператором.\n\n"
                 f"Нажмите на кнопку ниже, чтобы отправить чек оператору и получить актуальные реквизиты.")
        
        m = types.InlineKeyboardMarkup(row_width=1)
        m.add(
            types.InlineKeyboardButton("💬 Получить реквизиты у оператора", url=f"https://t.me/{MANAGER_USERNAME}"),
            types.InlineKeyboardButton("🎟️ Использовать промокод", callback_data=f"cart_promo_{deliv_char}_{b_idx}_{order_id}_{total_price_usd:.1f}"),
            types.InlineKeyboardButton("🏠 На главную", callback_data="to_main")
        )
        
        # Очищаем корзину после оформления чека
        db.execute("DELETE FROM cart WHERE uid=?", (uid,))
        safe_edit_text(cid, mid, check, m)

    elif data.startswith("cart_promo_"):
        parts = data.split("_")
        deliv_char = parts[2]
        b_idx = parts[3]
        order_id = parts[4]
        total_usd = float(parts[5])
        msg = bot.send_message(cid, "Введите ваш промокод для корзины:")
        bot.register_next_step_handler(msg, apply_cart_promo_receipt_step, deliv_char, b_idx, order_id, total_usd)

    # --- СТАРЫЙ МЕТОД ОДИНОЧНОЙ ПОКУПКИ ---
    elif data.startswith("ras_"):
        parts = data.split("_")
        pid = parts[1]
        w_idx = parts[2]
        m = types.InlineKeyboardMarkup(row_width=2)
        m.add(
            types.InlineKeyboardButton("Да, зарезервировать", callback_data=f"ry_{pid}_{w_idx}"),
            types.InlineKeyboardButton("Оплатить сейчас", callback_data=f"rn_{pid}_{w_idx}_0")
        )
        safe_edit_text(cid, mid, "<b>Хотите зарезервировать товар перед оплатой?</b>", m)

    elif data.startswith("ry_"):
        parts = data.split("_")
        pid = parts[1]
        w_idx = parts[2]
        m = types.InlineKeyboardMarkup(row_width=1)
        m.add(
            types.InlineKeyboardButton("На 2 часа", callback_data=f"rc_{pid}_{w_idx}_2"),
            types.InlineKeyboardButton("На 12 часов", callback_data=f"rc_{pid}_{w_idx}_12"),
            types.InlineKeyboardButton("На 24 часа", callback_data=f"rc_{pid}_{w_idx}_24"),
            types.InlineKeyboardButton("⬅️ Назад", callback_data=f"ras_{pid}_{w_idx}")
        )
        safe_edit_text(cid, mid, "<b>Выберите время резервирования товара:</b>", m)

    elif data.startswith("rc_"):
        parts = data.split("_")
        pid = parts[1]
        w_idx = parts[2]
        hours = parts[3]
        p = db.fetchone("SELECT name FROM products WHERE id=?", (pid,))
        until_time = (datetime.now() + timedelta(hours=int(hours))).strftime("%d.%m.%Y %H:%M")
        
        reserve_text = (
            f"🔑 Ваш товар <b>{p[0]}</b> успешно зарезервирован!\n\n"
            f"⏰ Резерв активен до: <b>{until_time}</b> (на {hours} ч.)\n\n"
            f"Вы можете оплатить забронированный товар прямо сейчас, время брони будет указано в вашем чеке."
        )
        m = types.InlineKeyboardMarkup(row_width=1)
        m.add(
            types.InlineKeyboardButton("💳 Оплатить сейчас", callback_data=f"rn_{pid}_{w_idx}_{hours}"),
            types.InlineKeyboardButton("⬅️ Назад", callback_data=f"ras_{pid}_{w_idx}"),
            types.InlineKeyboardButton("🏠 На главную", callback_data="to_main")
        )
        safe_edit_text(cid, mid, reserve_text, m)

    elif data.startswith("rn_"):
        parts = data.split("_")
        pid = parts[1]
        w_idx = parts[2]
        hours = parts[3] if len(parts) > 3 else "0"
        
        m = types.InlineKeyboardMarkup(row_width=1)
        m.add(
            types.InlineKeyboardButton("📦 Клад - магнит", callback_data=f"dt_{pid}_{w_idx}_m_{hours}"),
            types.InlineKeyboardButton("⛏️ Клад - прикоп", callback_data=f"dt_{pid}_{w_idx}_p_{hours}"),
            types.InlineKeyboardButton("📬 Почта", callback_data=f"dt_{pid}_{w_idx}_t_{hours}")
        )
        safe_edit_text(cid, mid, "<b>Выберите предпочтительный тип доставки:</b>", m)

    elif data.startswith("dt_"):
        parts = data.split("_")
        pid = parts[1]
        w_idx = parts[2]
        deliv_char = parts[3]
        hours = parts[4] if len(parts) > 4 else "0"
        
        u = db.fetchone("SELECT country FROM users WHERE uid=?", (uid,))
        m = types.InlineKeyboardMarkup(row_width=2)
        country_banks = get_payment_methods(u[0])
        
        for b_idx, b_name in enumerate(country_banks):
            m.add(types.InlineKeyboardButton(b_name.upper(), callback_data=f"pay_{pid}_{w_idx}_{deliv_char}_{b_idx}_{hours}"))
        
        m.add(types.InlineKeyboardButton("⬅️ Назад", callback_data=f"rn_{pid}_{w_idx}_{hours}"))
        safe_edit_text(cid, mid, f"<b>Выберите способ оплаты ({u[0]}):</b>", m)

    elif data.startswith("pay_"):
        parts = data.split("_")
        pid = parts[1]
        w_idx = parts[2]
        deliv_char = parts[3]
        b_idx = parts[4]
        hours = parts[5] if len(parts) > 5 else "0"
        
        p = db.fetchone("SELECT name, price FROM products WHERE id=?", (pid,))
        u = db.fetchone("SELECT city, country, district FROM users WHERE uid=?", (uid,))
        curr = CURRENCY_MAP.get(u[1], 'USD')
        rate = EXCHANGE_RATES.get(curr, 1.0)
        
        mult = 1 if w_idx == "1" else (1.9 if w_idx == "2" else (2.8 if w_idx == "3" else 4.2))
        price = round(p[1]*mult*rate, 1)
        w_text = f"{w_idx}г"
        
        deliv_type = "Клад - магнит" if deliv_char == "m" else ("Клад - прикоп" if deliv_char == "p" else "Почта")
        payment_methods = get_payment_methods(u[1])
        bank_name = payment_methods[int(b_idx)]
        order_id = str(uuid.uuid4())[:8].upper()
        
        reserve_info = ""
        if hours != "0":
            until_time = (datetime.now() + timedelta(hours=int(hours))).strftime("%d.%m.%Y %H:%M")
            reserve_info = f" ⏰ <b>РЕЗЕРВ: Активен до {until_time} (на {hours} ч.)</b>\n"
            
        if b_idx == "0":
            usd_price = p[1]*mult
            btc_price = round(usd_price / BTC_USD_RATE, 6)
            price_text = f"<b>{btc_price} BTC</b> (~{price} {curr})"
        else:
            price_text = f"<b>{price} {curr}</b>"

        check = (f"🧾 <b>Чек заказа #{order_id}</b>\n"
                 f"━━━━━━━━━━━━━━━━━━━━━━━━━━\n"
                 f" 📍 Город: {u[0]}\n"
                 f" 🗺️ Район: {u[2] if u[2] else 'Не указан'}\n"
                 f" 📦 Товар: {p[0]}\n"
                 f" ⚖️ Вес: {w_text}\n"
                 f" 🚚 Тип доставки: {deliv_type}\n"
                 f" 💳 Способ оплаты: {bank_name}\n"
                 f" 💵 Сумма к оплате: {price_text}\n"
                 f"{reserve_info}"
                 f"━━━━━━━━━━━━━━━━━━━━━━━━━━\n"
                 f"⚠️ <b>ОБЯЗАТЕЛЬНО СКОПИРУЙТЕ И ОТПРАВЬТЕ ЭТОТ ЧЕК НАШЕМУ ОПЕРАТОРУ ДЛЯ ПОЛУЧЕНИЯ РЕКВИЗИТОВ ДЛЯ ОПЛАТЫ!</b> Без предоставления чека реквизиты на оплату не выдаются, а ваш платеж не сможет быть зачислен оператором.\n\n"
                 f"Нажмите на кнопку ниже, чтобы отправить чек оператору и получить актуальные реквизиты.")
        
        m = types.InlineKeyboardMarkup(row_width=1)
        m.add(
            types.InlineKeyboardButton("💬 Получить реквизиты у оператора", url=f"https://t.me/{MANAGER_USERNAME}"),
            types.InlineKeyboardButton("🎟️ Использовать промокод", callback_data=f"promo_{pid}_{w_idx}_{deliv_char}_{b_idx}_{order_id}_{hours}"),
            types.InlineKeyboardButton("🏠 На главную", callback_data="to_main")
        )
        safe_edit_text(cid, mid, check, m)

    elif data.startswith("promo_"):
        parts = data.split("_")
        pid = parts[1]
        w_idx = parts[2]
        deliv_char = parts[3]
        b_idx = parts[4]
        order_id = parts[5]
        hours = parts[6] if len(parts) > 6 else "0"
        msg = bot.send_message(cid, "Введите ваш промокод:")
        bot.register_next_step_handler(msg, apply_promo_receipt_step, pid, w_idx, deliv_char, b_idx, order_id, hours)

    # --- АДМИНИСТРАТИВНАЯ ПАНЕЛЬ ---
    elif data == "admin_main" and uid in ADMIN_IDS:
        total_users_count = db.fetchone("SELECT COUNT(*) FROM users")[0]
        
        m = types.InlineKeyboardMarkup(row_width=1)
        m.add(
            types.InlineKeyboardButton("📝 Редактировать товары", callback_data="adm_list_0"),
            types.InlineKeyboardButton("💬 Управление отзывами", callback_data="adm_rev_main"),
            types.InlineKeyboardButton("🎟️ Управление промокодами", callback_data="adm_promo_main"),
            types.InlineKeyboardButton("📣 Рассылка пользователям", callback_data="adm_broadcast"),
            types.InlineKeyboardButton("🔄 Обновить все витрины (Рандом)", callback_data="adm_shuffle"),
            types.InlineKeyboardButton("🏠 Выйти из админки", callback_data="to_main")
        )
        
        admin_panel_text = (
            f"⚙️ <b>Панель управления</b>\n"
            f"━━━━━━━━━━━━━━━━━━━━━━━━━━\n"
            f"👥 Всего зарегистрировано пользователей: <b>{total_users_count} чел.</b>\n"
            f"━━━━━━━━━━━━━━━━━━━━━━━━━━\n"
            f"Здесь доступно управление ассортиментом, отзывами, промокодами и рассылкой."
        )
        safe_edit_text(cid, mid, admin_panel_text, m)

    elif data == "adm_broadcast" and uid in ADMIN_IDS:
        msg = bot.send_message(cid, "Введите текст вашей рассылки (поддерживается HTML-разметка):")
        bot.register_next_step_handler(msg, process_broadcast_step)

    elif data == "adm_promo_main" and uid in ADMIN_IDS:
        m = types.InlineKeyboardMarkup(row_width=1)
        m.add(
            types.InlineKeyboardButton("➕ Добавить промокод", callback_data="adm_promo_add"),
            types.InlineKeyboardButton("📋 Список промокодов", callback_data="adm_promo_list_0"),
            types.InlineKeyboardButton("⬅️ Назад в меню", callback_data="admin_main")
        )
        safe_edit_text(cid, mid, "🎟️ <b>Управление промокодами</b>\nВы можете добавлять новые промокоды и регулировать размер скидки и срок действия.", m)

    elif data == "adm_promo_add" and uid in ADMIN_IDS:
        msg = bot.send_message(cid, "Введите новый промокод и размер скидки через пробел (например: SALE10 15):")
        bot.register_next_step_handler(msg, add_promo_step)

    elif data.startswith("adm_promo_list_") and uid in ADMIN_IDS:
        parts = data.split("_")
        page = int(parts[3])
        promos = db.fetchall("SELECT code, discount, expires_at FROM promocodes")
        if not promos:
            m = types.InlineKeyboardMarkup(row_width=1)
            m.add(types.InlineKeyboardButton("⬅️ Назад", callback_data="adm_promo_main"))
            return safe_edit_text(cid, mid, "Список промокодов пуст.", m)
        
        start = page * 10
        end = start + 10
        m = types.InlineKeyboardMarkup(row_width=1)
        for code, discount, expires_at in promos[start:end]:
            if expires_at == 'eternal' or not expires_at:
                dur_label = "♾️ Вечный"
            else:
                try:
                    exp_dt = datetime.fromisoformat(expires_at)
                    if datetime.now() > exp_dt:
                        dur_label = "❌ Истек"
                    else:
                        dur_label = exp_dt.strftime("%d.%m %H:%M")
                except Exception:
                    dur_label = "⏳ Неизв."
            m.add(types.InlineKeyboardButton(f"{code} ({discount}%) [{dur_label}] — ❌", callback_data=f"adm_promo_del_{code}_{page}"))
        
        nav = []
        if page > 0:
            nav.append(types.InlineKeyboardButton("⬅️ Назад", callback_data=f"adm_promo_list_{page-1}"))
        if end < len(promos):
            nav.append(types.InlineKeyboardButton("Вперед ➡️", callback_data=f"adm_promo_list_{page+1}"))
        if nav:
            m.row(*nav)
        m.add(types.InlineKeyboardButton("⬅️ Назад в меню", callback_data="adm_promo_main"))
        safe_edit_text(cid, mid, f"<b>Список промокодов (Страница {page+1}):</b>\nНажмите на промокод, чтобы его удалить.", m)

    elif data.startswith("adm_promo_del_") and uid in ADMIN_IDS:
        parts = data.split("_")
        code = parts[3]
        page = int(parts[4])
        db.execute("DELETE FROM promocodes WHERE code=?", (code,))
        bot.answer_callback_query(c.id, f"Промокод {code} удален!", show_alert=True)
        
        promos = db.fetchall("SELECT code, discount, expires_at FROM promocodes")
        if not promos:
            m = types.InlineKeyboardMarkup(row_width=1)
            m.add(types.InlineKeyboardButton("⬅️ Назад", callback_data="adm_promo_main"))
            return safe_edit_text(cid, mid, "Список промокодов пуст.", m)
        
        start = page * 10
        end = start + 10
        m = types.InlineKeyboardMarkup(row_width=1)
        for cd, ds, exp_at in promos[start:end]:
            if exp_at == 'eternal' or not exp_at:
                dur_lbl = "♾️ Вечный"
            else:
                try:
                    exp_dt = datetime.fromisoformat(exp_at)
                    if datetime.now() > exp_dt:
                        dur_lbl = "❌ Истек"
                    else:
                        dur_lbl = exp_dt.strftime("%d.%m %H:%M")
                except Exception:
                    dur_lbl = "⏳ Неизв."
            m.add(types.InlineKeyboardButton(f"{cd} ({ds}%) [{dur_lbl}] — ❌", callback_data=f"adm_promo_del_{cd}_{page}"))
        
        nav = []
        if page > 0:
            nav.append(types.InlineKeyboardButton("⬅️ Назад", callback_data=f"adm_promo_list_{page-1}"))
        if end < len(promos):
            nav.append(types.InlineKeyboardButton("Вперед ➡️", callback_data=f"adm_promo_list_{page+1}"))
        if nav:
            m.row(*nav)
        m.add(types.InlineKeyboardButton("⬅️ Назад в меню", callback_data="adm_promo_main"))
        safe_edit_text(cid, mid, f"<b>Список промокодов (Страница {page+1}):</b>", m)

    elif data.startswith("apd:"):
        # Обработка обратного вызова при выборе срока действия промокода
        parts = data.split(":")
        code = parts[1]
        discount = int(parts[2])
        dur = parts[3]
        
        now_dt = datetime.now()
        if dur == "1h":
            expires_dt = now_dt + timedelta(hours=1)
            exp_str = expires_dt.isoformat()
            dur_text = "1 час"
        elif dur == "1d":
            expires_dt = now_dt + timedelta(days=1)
            exp_str = expires_dt.isoformat()
            dur_text = "1 день"
        elif dur == "1w":
            expires_dt = now_dt + timedelta(weeks=1)
            exp_str = expires_dt.isoformat()
            dur_text = "1 неделя"
        elif dur == "2w":
            expires_dt = now_dt + timedelta(weeks=2)
            exp_str = expires_dt.isoformat()
            dur_text = "2 недели"
        elif dur == "1m":
            expires_dt = now_dt + timedelta(days=30)
            exp_str = expires_dt.isoformat()
            dur_text = "1 месяц"
        elif dur == "1y":
            expires_dt = now_dt + timedelta(days=365)
            exp_str = expires_dt.isoformat()
            dur_text = "1 год"
        else:
            exp_str = "eternal"
            dur_text = "Вечный (без ограничений)"
            
        db.execute("INSERT OR REPLACE INTO promocodes (code, discount, expires_at) VALUES (?,?,?)", (code, discount, exp_str))
        bot.answer_callback_query(c.id, f"Промокод {code} успешно создан!")
        
        success_text = (
            f"🎉 <b>ПРОМОКОД УСПЕШНО СОЗДАН!</b>\n"
            f"━━━━━━━━━━━━━━━━━━━━━━━━━━\n\n"
            f"• Купон: <code>{code}</code>\n"
            f"• Скидка: <b>{discount}%</b>\n"
            f"• Срок действия: <b>{dur_text}</b>\n\n"
            f"Доступен для немедленного ввода пользователями при оформлении заказа."
        )
        m_back = types.InlineKeyboardMarkup()
        m_back.add(types.InlineKeyboardButton("⬅️ Назад в промокоды", callback_data="adm_promo_main"))
        safe_edit_text(cid, mid, success_text, m_back)

    elif data == "adm_rev_main" and uid in ADMIN_IDS:
        m = types.InlineKeyboardMarkup(row_width=1)
        m.add(
            types.InlineKeyboardButton("✏️ Написать свой отзыв", callback_data="adm_rev_write"),
            types.InlineKeyboardButton("📋 Добавить из заготовок (1000 шт.)", callback_data="adm_rev_tpl_0"),
            types.InlineKeyboardButton("🔄 Обновить отзывы витрины", callback_data="adm_rev_shuffle_db"),
            types.InlineKeyboardButton("⬅️ Назад в меню", callback_data="admin_main")
        )
        safe_edit_text(cid, mid, "💬 <b>Управление отзывами</b>\nВы можете добавить свой текст или выбрать готовый шаблон из базы в 1000 шт.", m)

    elif data == "adm_rev_shuffle_db" and uid in ADMIN_IDS:
        db.shuffle_reviews()
        bot.answer_callback_query(c.id, "Отзывы витрины успешно перемешаны и обновлены!", show_alert=True)

    elif data == "adm_rev_write" and uid in ADMIN_IDS:
        msg = bot.send_message(cid, "Введите текст нового отзыва. Он будет опубликован со случайным товаром:")
        bot.register_next_step_handler(msg, add_custom_review_step)

    elif data.startswith("adm_rev_tpl_") and uid in ADMIN_IDS:
        parts = data.split("_")
        page = int(parts[3])
        start = page * 10
        end = start + 10
        m = types.InlineKeyboardMarkup(row_width=1)
        
        for i, rev in enumerate(PREMADE_REVIEWS[start:end], start=start):
            short_text = rev[:35] + "..." if len(rev) > 35 else rev
            m.add(types.InlineKeyboardButton(short_text, callback_data=f"adm_rev_add_{i}"))
            
        nav = []
        if page > 0:
            nav.append(types.InlineKeyboardButton("⬅️ Назад", callback_data=f"adm_rev_tpl_{page-1}"))
        if end < len(PREMADE_REVIEWS):
            nav.append(types.InlineKeyboardButton("Вперед ➡️", callback_data=f"adm_rev_tpl_{page+1}"))
        
        if nav:
            m.row(*nav)
        m.add(types.InlineKeyboardButton("⬅️ Назад в меню", callback_data="adm_rev_main"))
        safe_edit_text(cid, mid, f"<b>Шаблоны отзывов (Страница {page+1}):</b>\nНажмите на любой отзыв для его публикации на витрине.", m)

    elif data.startswith("adm_rev_add_") and uid in ADMIN_IDS:
        parts = data.split("_")
        idx = int(parts[3])
        txt = PREMADE_REVIEWS[idx]
        prod = random.choice(ALL_PRODUCT_NAMES)
        db.execute("INSERT INTO reviews (text, prod) VALUES (?,?)", (txt, prod))
        bot.answer_callback_query(c.id, "Отзыв успешно опубликован!", show_alert=True)

    elif data == "adm_shuffle" and uid in ADMIN_IDS:
        db.shuffle_stock()
        bot.answer_callback_query(c.id, "Витрины всех городов пересобраны заново!", show_alert=True)
        
        #        # --- ГЕО-РАССЫЛКА О СВЕЖЕМ ПОПОЛНЕНИИ ПОДПИСЧИКАМ ---
        subs = db.fetchall("SELECT uid, city FROM subscriptions")
        sent_count = 0
        for sub_uid, sub_city in subs:
            try:
                msg_text = (
                    f"🔔 <b>[ОФИЦИАЛЬНОЕ УВЕДОМЛЕНИЕ: {sub_city.upper()}]</b>\n"
                    f"━━━━━━━━━━━━━━━━━━━━━━━━━━\n\n"
                    f"Уважаемый клиент, информируем Вас о завершении планового распределения и успешной дистрибуции свежей партии позиций по ключевым районам Вашего города.\n\n"
                    f"💼 <b>Логистический статус:</b> Все локации укомплектованы нашими специалистами и полностью готовы к обслуживанию.\n"
                    f"🛡️ <b>Качество и надежность:</b> Каждая позиция упакована в строгом соответствии с премиальными стандартами безопасности и анонимности компании {SHOP_NAME}.\n\n"
                    f"Рекомендуем своевременно сформировать заказ для резервирования наилучших локаций. Благодарим за то, что выбираете наш сервис!"
                )
                m = types.InlineKeyboardMarkup(row_width=1)
                m.add(types.InlineKeyboardButton("🛒 Перейти в Каталог", callback_data="shop"))
                bot.send_photo(sub_uid, MAIN_IMG, caption=msg_text, reply_markup=m, parse_mode="HTML")
                sent_count += 1
            except Exception:
                pass
        
        bot.send_message(cid, f"📢 Гео-рассылка завершена! Отправлено уведомлений: <b>{sent_count} шт.</b>", parse_mode="HTML")

    elif data.startswith("adm_list_"):
        parts = data.split("_")
        page = int(parts[2])
        prods = db.fetchall("SELECT id, name, price FROM products")
        start = page * 10
        end = start + 10
        m = types.InlineKeyboardMarkup(row_width=2)
        for pid, name, price in prods[start:end]:
            m.add(types.InlineKeyboardButton(name, callback_data=f"adm_edit_{pid}"))
        
        nav = []
        if page > 0:
            nav.append(types.InlineKeyboardButton("⬅️ Назад", callback_data=f"adm_list_{page-1}"))
        if end < len(prods):
            nav.append(types.InlineKeyboardButton("Вперед ➡️", callback_data=f"adm_list_{page+1}"))
        if nav:
            m.row(*nav)
        m.add(types.InlineKeyboardButton("⬅️ Назад", callback_data="admin_main"))
        safe_edit_text(cid, mid, f"<b>Выберите товар для изменения (стр. {page+1}):</b>", m)

    elif data.startswith("adm_edit_"):
        parts = data.split("_")
        pid = parts[2]
        p = db.fetchone("SELECT name, price FROM products WHERE id=?", (pid,))
        m = types.InlineKeyboardMarkup(row_width=1)
        m.add(
            types.InlineKeyboardButton("📝 Изменить название", callback_data=f"edt_name_{pid}"),
            types.InlineKeyboardButton("💵 Изменить цену", callback_data=f"edt_prc_{pid}"),
            types.InlineKeyboardButton("⬅️ К списку", callback_data="adm_list_0")
        )
        safe_edit_text(cid, mid, f"📝 <b>Товар ID: {pid}</b>\nИмя: {p[0]}\nБазовая цена: {p[1]}$", m)

    elif data.startswith("edt_name_"):
        parts = data.split("_")
        pid = parts[2]
        msg = bot.send_message(cid, "Введите новое название товара:")
        bot.register_next_step_handler(msg, update_name_step, pid)

    elif data.startswith("edt_prc_"):
        parts = data.split("_")
        pid = parts[2]
        msg = bot.send_message(cid, "Введите новую цену за 1г ($):")
        bot.register_next_step_handler(msg, update_price_step, pid)

# --- ДОПОЛНИТЕЛЬНЫЕ ФУНКЦИИ И ОБРАБОТЧИКИ ШАГОВ ---

def apply_cart_promo_receipt_step(m, deliv_char, b_idx, order_id, total_usd):
    if not m.text:
        return
    code = m.text.strip().upper()
    promo = db.fetchone("SELECT discount, expires_at FROM promocodes WHERE code=?", (code,))
    
    # Валидация срока действия промокода
    is_expired = False
    if promo:
        discount = int(promo[0])
        expires_at = promo[1]
        if expires_at and expires_at != 'eternal':
            try:
                exp_dt = datetime.fromisoformat(expires_at)
                if datetime.now() > exp_dt:
                    is_expired = True
            except Exception:
                pass
                
        if is_expired:
            db.execute("DELETE FROM promocodes WHERE code=?", (code,))
            promo = None  # Сбрасываем как недействительный

    uid = m.from_user.id
    u = db.fetchone("SELECT city, country FROM users WHERE uid=?", (uid,))
    curr = CURRENCY_MAP.get(u[1], 'USD')
    rate = EXCHANGE_RATES.get(curr, 1.0)
    
    deliv_type = "Клад - магнит" if deliv_char == "m" else ("Клад - прикоп" if deliv_char == "p" else "Почта")
    payment_methods = get_payment_methods(u[1])
    bank_name = payment_methods[int(b_idx)]
    
    base_price_curr = round(total_usd * rate, 1)
    
    if promo:
        discount = int(promo[0])
        # Сгорают и удаляются только реферальные коды, начинающиеся на "REF-"
        if code.startswith("REF-"):
            db.execute("DELETE FROM promocodes WHERE code=?", (code,))
        
        discount_mult = (100 - discount) / 100.0
        new_price_curr = round(base_price_curr * discount_mult, 1)
        
        if b_idx == "0":
            usd_new_price = total_usd * discount_mult
            btc_old_price = round(total_usd / BTC_USD_RATE, 6)
            btc_price = round(usd_new_price / BTC_USD_RATE, 6)
            price_text = f"<s>{btc_old_price} BTC</s> (~<s>{base_price_curr} {curr}</s>) ➔ 🔥 <b>{btc_price} BTC</b> (~<b>{new_price_curr} {curr}</b>) [Скидка {discount}%]"
        else:
            price_text = f"<s>{base_price_curr} {curr}</s> ➔ 🔥 <b>{new_price_curr} {curr}</b> [Скидка {discount}%]"

        check = (f"🧾 <b>Чек заказа #{order_id} (КОРЗИНА)</b>\n"
                 f"━━━━━━━━━━━━━━━━━━━━━━━━━━\n"
                 f" 📍 Город: {u[0]}\n"
                 f" 🚚 Тип доставки: {deliv_type}\n"
                 f" 💳 Способ оплаты: {bank_name}\n"
                 f" 💵 Сумма: {price_text}\n"
                 f"━━━━━━━━━━━━━━━━━━━━━━━━━━\n"
                 f"⚠️ <b>ОБЯЗАТЕЛЬНО СКОПИРУЙТЕ И ОТПРАВЬТЕ ЭТОТ ЧЕК НАШЕМУ ОПЕРАТОРУ ДЛЯ ПОЛУЧЕНИЯ РЕКВИЗИТОВ ДЛЯ ОПЛАТЫ!</b> Без предоставления чека реквизиты на оплату не выдаются, а ваш платеж не сможет быть зачислен оператором.\n\n"
                 f"Нажмите на кнопку ниже, чтобы отправить чек оператору и получить актуальные реквизиты.")
        
        kb = types.InlineKeyboardMarkup(row_width=1)
        kb.add(
            types.InlineKeyboardButton("💬 Получить реквизиты у оператора", url=f"https://t.me/{MANAGER_USERNAME}"),
            types.InlineKeyboardButton("🏠 На главную", callback_data="to_main")
        )
        bot.send_photo(m.chat.id, MAIN_IMG, caption=check, reply_markup=kb, parse_mode="HTML")
    else:
        text = f"Промокод <b>{code}</b> не действителен, истек или не найден."
        kb = types.InlineKeyboardMarkup(row_width=1)
        kb.add(
            types.InlineKeyboardButton("🔄 Попробовать снова", callback_data=f"cart_promo_{deliv_char}_{b_idx}_{order_id}_{total_usd:.1f}"),
            types.InlineKeyboardButton("🏠 На главную", callback_data="to_main")
        )
        bot.send_photo(m.chat.id, MAIN_IMG, caption=text, reply_markup=kb, parse_mode="HTML")

def update_name_step(m, pid):
    if not m.text:
        return
    db.execute("UPDATE products SET name=? WHERE id=?", (m.text, pid))
    bot.send_message(m.chat.id, f"Название товара #{pid} изменено на: {m.text}")

def update_price_step(m, pid):
    try:
        new_p = float(m.text)
        db.execute("UPDATE products SET price=? WHERE id=?", (new_p, pid))
        bot.send_message(m.chat.id, f"Цена товара #{pid} изменена на: {new_p}$")
    except ValueError:
        bot.send_message(m.chat.id, "Ошибка ввода. Введите числовое значение цены.")

def add_custom_review_step(m):
    if not m.text:
        return
    prod = random.choice(ALL_PRODUCT_NAMES)
    db.execute("INSERT INTO reviews (text, prod) VALUES (?,?)", (m.text, prod))
    bot.send_message(m.chat.id, "Ваш отзыв успешно опубликован и виден покупателям!")

def add_promo_step(m):
    if m.from_user.id not in ADMIN_IDS:
        return
    if not m.text:
        return
    try:
        parts = m.text.strip().split()
        if len(parts) != 2:
            raise ValueError
        code = parts[0].upper()
        discount = int(parts[1])
        if not (1 <= discount <= 99):
            bot.send_message(m.chat.id, "Размер скидки должен быть целым числом в диапазоне от 1 до 99.")
            return
            
        m_markup = types.InlineKeyboardMarkup(row_width=2)
        m_markup.add(
            types.InlineKeyboardButton("⏱️ 1 час", callback_data=f"apd:{code}:{discount}:1h"),
            types.InlineKeyboardButton("📅 1 день", callback_data=f"apd:{code}:{discount}:1d")
        )
        m_markup.add(
            types.InlineKeyboardButton("📅 1 неделя", callback_data=f"apd:{code}:{discount}:1w"),
            types.InlineKeyboardButton("📅 2 недели", callback_data=f"apd:{code}:{discount}:2w")
        )
        m_markup.add(
            types.InlineKeyboardButton("🗓️ 1 месяц", callback_data=f"apd:{code}:{discount}:1m"),
            types.InlineKeyboardButton("🗓️ 1 год", callback_data=f"apd:{code}:{discount}:1y")
        )
        m_markup.add(
            types.InlineKeyboardButton("♾️ Вечный", callback_data=f"apd:{code}:{discount}:eternal")
        )
        m_markup.add(
            types.InlineKeyboardButton("❌ Отмена", callback_data="adm_promo_main")
        )
        
        bot.send_message(
            m.chat.id, 
            f"Вы создаете промокод <b>{code}</b> со скидкой <b>{discount}%</b>.\nВыберите срок его действия:", 
            reply_markup=m_markup, 
            parse_mode="HTML"
        )
    except ValueError:
        bot.send_message(m.chat.id, "Ошибка формата ввода. Используйте пример: SALE15 15")

def apply_promo_receipt_step(m, pid, w_idx, deliv_char, b_idx, order_id, hours="0"):
    if not m.text:
        return
    code = m.text.strip().upper()
    promo = db.fetchone("SELECT discount, expires_at FROM promocodes WHERE code=?", (code,))
    
    # Валидация срока действия промокода
    is_expired = False
    if promo:
        discount = int(promo[0])
        expires_at = promo[1]
        if expires_at and expires_at != 'eternal':
            try:
                exp_dt = datetime.fromisoformat(expires_at)
                if datetime.now() > exp_dt:
                    is_expired = True
            except Exception:
                pass
                
        if is_expired:
            db.execute("DELETE FROM promocodes WHERE code=?", (code,))
            promo = None  # Сбрасываем как недействительный

    u = db.fetchone("SELECT city, country, district FROM users WHERE uid=?", (m.from_user.id,))
    curr = CURRENCY_MAP.get(u[1], 'USD')
    rate = EXCHANGE_RATES.get(curr, 1.0)
    
    p = db.fetchone("SELECT name, price FROM products WHERE id=?", (pid,))
    mult = 1 if w_idx == "1" else (1.9 if w_idx == "2" else (2.8 if w_idx == "3" else 4.2))
    base_price = round(p[1]*mult*rate, 1)
    w_text = f"{w_idx}г"
    deliv_type = "Клад - магнит" if deliv_char == "m" else ("Клад - прикоп" if deliv_char == "p" else "Почта")
    payment_methods = get_payment_methods(u[1])
    bank_name = payment_methods[int(b_idx)]
    
    reserve_info = ""
    if hours != "0":
        until_time = (datetime.now() + timedelta(hours=int(hours))).strftime("%d.%m.%Y %H:%M")
        reserve_info = f" ⏰ <b>РЕЗЕРВ: Активен до {until_time} (на {hours} ч.)</b>\n"
        
    if promo:
        discount = int(promo[0])
        # Сгорают и удаляются только реферальные коды, начинающиеся на "REF-"
        if code.startswith("REF-"):
            db.execute("DELETE FROM promocodes WHERE code=?", (code,))
        
        discount_mult = (100 - discount) / 100.0
        new_price = round(base_price * discount_mult, 1)
        
        if b_idx == "0":
            usd_new_price = (p[1]*mult) * discount_mult
            btc_old_price = round((p[1]*mult) / BTC_USD_RATE, 6)
            btc_price = round(usd_new_price / BTC_USD_RATE, 6)
            price_text = f"<s>{btc_old_price} BTC</s> (~<s>{base_price} {curr}</s>) ➔ 🔥 <b>{btc_price} BTC</b> (~<b>{new_price} {curr}</b>) [Скидка {discount}%]"
        else:
            price_text = f"<s>{base_price} {curr}</s> ➔ 🔥 <b>{new_price} {curr}</b> [Скидка {discount}%]"

        check = (f"🧾 <b>Чек заказа #{order_id}</b>\n"
                 f"━━━━━━━━━━━━━━━━━━━━━━━━━━\n"
                 f" 📍 Город: {u[0]}\n"
                 f" 🗺️ Район: {u[2] if u[2] else 'Не указан'}\n"
                 f" 📦 Товар: {p[0]}\n"
                 f" ⚖️ Вес: {w_text}\n"
                 f" 🚚 Тип доставки: {deliv_type}\n"
                 f" 💳 Способ оплаты: {bank_name}\n"
                 f" 💵 Сумма: {price_text}\n"
                 f"{reserve_info}"
                 f"━━━━━━━━━━━━━━━━━━━━━━━━━━\n"
                 f"⚠️ <b>ОБЯЗАТЕЛЬНО СКОПИРУЙТЕ И ОТПРАВЬТЕ ЭТОТ ЧЕК НАШЕМУ ОПЕРАТОРУ ДЛЯ ПОЛУЧЕНИЯ РЕКВИЗИТОВ ДЛЯ ОПЛАТЫ!</b> Без предоставления чека реквизиты на оплату не выдаются, а ваш платеж не сможет быть зачислен оператором.\n\n"
                 f"Нажмите на кнопку ниже, чтобы отправить чек оператору и получить актуальные реквизиты.")
        
        kb = types.InlineKeyboardMarkup(row_width=1)
        kb.add(
            types.InlineKeyboardButton("💬 Получить реквизиты у оператора", url=f"https://t.me/{MANAGER_USERNAME}"),
            types.InlineKeyboardButton("🏠 На главную", callback_data="to_main")
        )
        bot.send_photo(m.chat.id, MAIN_IMG, caption=check, reply_markup=kb, parse_mode="HTML")
    else:
        text = f"Промокод <b>{code}</b> не действителен, истек или не найден."
        kb = types.InlineKeyboardMarkup(row_width=1)
        kb.add(
            types.InlineKeyboardButton("🔄 Попробовать снова", callback_data=f"promo_{pid}_{w_idx}_{deliv_char}_{b_idx}_{order_id}_{hours}"),
            types.InlineKeyboardButton("🏠 На главную", callback_data="to_main")
        )
        bot.send_photo(m.chat.id, MAIN_IMG, caption=text, reply_markup=kb, parse_mode="HTML")

def process_broadcast_step(m):
    """Рассылает сообщение всем пользователям из базы данных."""
    if m.from_user.id not in ADMIN_IDS:
        return
    text = m.text
    if not text:
        bot.send_message(m.chat.id, "Рассылка отменена (пустой текст).")
        return
    
    users = db.fetchall("SELECT uid FROM users")
    success = 0
    fail = 0
    
    bot.send_message(m.chat.id, f"Начинаю рассылку для {len(users)} пользователей...")
    
    for user in users:
        uid = user[0]
        try:
            bot.send_message(uid, text, parse_mode="HTML")
            success += 1
        except Exception:
            fail += 1
            
    bot.send_message(
        m.chat.id,
        f"Рассылка завершена!\n"
        f"Успешно доставлено: {success}\n"
        f"Ошибок отправки (бот заблокирован): {fail}"
    )

if __name__ == "__main__":
    while True:
        try:
            # Использование надежного infinity_polling для защиты от ReadTimeout сессий
            bot.infinity_polling(timeout=10, long_polling_timeout=5)
        except Exception as e:
            logging.error(f"Polling error occurred: {e}")
            time.sleep(5)

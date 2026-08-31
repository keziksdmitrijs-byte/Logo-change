# Login Logo — Home Assistant custom integration

Заменяет логотип/иконки на экране входа (login) и загрузки (loading) Home Assistant на изображение, которое вы загружаете сами через UI интеграции.

## ⚠️ Важное ограничение

Эта интеграция физически перезаписывает файлы favicon внутри установленного пакета `hass_frontend`
(`.../site-packages/hass_frontend/static/icons/`). Эти файлы переустанавливаются заново при каждом
обновлении Home Assistant Core / Supervisor / контейнера.

**Используйте эту интеграцию только если вы не планируете обновлять Home Assistant после установки**,
либо готовы повторно нажимать "Reapply logo" после каждого обновления.

## Возможности

- Загрузка одного PNG-файла через стандартный Config Flow (Settings → Devices & Services → Add Integration).
- Автоматическая генерация всех нужных размеров: favicon.ico, favicon-32/192/1024, apple-touch-icon (60/76/120/152/180).
- Раздача сгенерированных файлов из `/local/login_logo/` (папка `www/login_logo/` в конфиге).
- Опциональная перезапись файлов внутри `hass_frontend` — именно то, что меняет экран **login/loading**.
- Автоматический бэкап оригинальных иконок перед первой перезаписью.
- Сервисы:
  - `login_logo.reapply_logo` — перегенерировать и повторно применить логотип (например, после обновления HA).
  - `login_logo.restore_default_logo` — вернуть оригинальные иконки Home Assistant.
- Options Flow — загрузить новый логотип позже без переустановки интеграции.

## Установка

### Через HACS (кастомный репозиторий)

1. HACS → Integrations → меню (⋮) → Custom repositories.
2. Добавьте URL этого репозитория, категория "Integration".
3. Найдите "Login Logo" в списке HACS и установите.
4. Перезапустите Home Assistant.

### Вручную

1. Скопируйте папку `custom_components/login_logo` в `<config>/custom_components/`.
2. Перезапустите Home Assistant.

## Настройка

1. Settings → Devices & Services → Add Integration → "Login Logo".
2. Загрузите PNG-файл вашего логотипа (рекомендуется квадратное изображение, минимум 512×512, с прозрачным фоном).
3. Оставьте включённой опцию "Also overwrite installed frontend icon files", если хотите, чтобы логотип
   поменялся именно на экране входа/загрузки.
4. Сделайте hard refresh в браузере (Ctrl+Shift+R) или очистите кэш favicon — браузеры агрессивно кэшируют favicon.

## Обновление логотипа

Settings → Devices & Services → Login Logo → Configure, и загрузите новый файл.

## Восстановление оригинала

Вызовите сервис `login_logo.restore_default_logo` из Developer Tools → Services.

## Структура репозитория

```
custom_components/login_logo/
├── __init__.py
├── config_flow.py
├── const.py
├── icon_tools.py
├── manifest.json
├── services.yaml
├── strings.json
└── translations/
    ├── en.json
    └── ru.json
hacs.json
README.md
```

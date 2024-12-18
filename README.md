# git-notify-daemon-linux
Демон на Python, который уведомляет о новых коммитах в git репозитории и исправляет ошибки подключения библиотек

## Установка и запуск
### Шаг 1: Обновление

```bash
sudo apt update
sudo apt upgrade
```

### Шаг 2: Клонирование репозитория

Клонируйте репозиторий на свой компьютер:

```bash
git clone https://github.com/wvvay/git-notify-daemon.git
cd git-notify-daemon
```

### Шаг 3: Установка

Для работы с GObject-based библиотеками, такими как Notify, нужно установить PyGObject. Это можно сделать через пакетный менеджер системы.

```bash
sudo apt-get update
sudo apt-get install python3-gi
sudo apt install virtualenv
sudo apt install -y libnotify-dev
sudo apt install -y python3-gi python3-gi-cairo gir1.2-gtk-3.0
```

### Шаг 4: Путь

Поменять путь на местоположения репозитория

```bash
os.chdir('<>/git-notify-daemon')
```

### Шаг 5: Запуск

```bash
python3 daemon_commit.py <start | stop | restart | check_updates | status>
```

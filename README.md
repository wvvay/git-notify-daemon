# git-notify-daemon-linux
Демон на Python, который уведомляет о новых коммитах в git репозитории

## Установка и запуск

### Шаг 1: Клонирование репозитория

Клонируйте репозиторий на свой компьютер:

```bash
git clone https://github.com/wvvay/git-notify-daemon.git
cd git-notify-daemon
```
### Шаг 2: Установка

Для работы с GObject-based библиотеками, такими как Notify, нужно установить PyGObject. Это можно сделать через пакетный менеджер системы.

```bash
sudo apt-get update
sudo apt-get install python3-gi
sudo apt-get install libnotify-dev
```


### Шаг 3: Путь

Поменять путь на местоположения репозитория

```bash
os.chdir('<>/git-notify-daemon')
```

### Шаг 4: Запуск

```bash
python3 daemon_commit.py <start | stop | restart>
```

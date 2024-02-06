# Архив периодических изданий
Django-приложение для просмотра периодических изданий в формате pdf, 
с возможностью распознавания посредством Tesseract OSR и автоматизированным составлением
списка ключевых слов(тегов) из текста  с помощью пользовательских словарей.
Ведение статистики посещений по заданным ip-адресам.

<b>Не рекомендуется для проброса в Интернет.</b>
## Установка и запуск
Скачиваем и устанавливаем Python:

Windows - https://www.python.org

Linux - из репозитория соответствующего дистрибутива

### Перед развертыванием и настройкой задайте переменные окружения в файле `.env`.
Настройте PostgreSQL, если не будете использовать sqlite, в качестве базы данных.

Для развертывания <b>из каталога приложения</b> выполните следующие команды:

1. Создайте виртуальное окружение:

`python3 -m venv venv`

2. Активируйте виртуальное окружение:

`./venv/bin/activate` - для Linux

`.\venv\Scripts\activate.bat` - для Windows

3. Установите зависимости:

`pip install -r requirements.txt`

4. В зависимости от Операционной Системы задайте переменные окружения с помощью скриптов

`source ./tools/set_env.sh` - для Linux

`call .\tools\set_env.bat` - для Windows

5. Подготовьте базу данных к работе, соберите статичные данные и создайте суперпользователя
приложения. Выход из виртуального окружения:
```
python manage.py makemigrations
python manage.py migrate
python manage.py collectstatic
python manage.py createsuperuser
deactivate
```
<b>(Опционально) Создание и запуск службы Windows:</b>
Для запуска приложения как службы windows можно воспользоваться утилитами, такими как `nssm`

Пример: `nssm.exe install PeriodicLibrary *Каталог_приложения*\tools\run.bat`, где 
*Каталог_приложения* - путь к каталогу приложения.

<b>(Опционально) Создание Unit-файла:</b>

Создайте файл `/etc/systemd/system/periodic.service` со следующим содержимым:
```
[Unit]
Description=Periodic Library 
After=network.target

[Service]
Type=simple
User=*webuser*
Group=*webuser*
WorkingDirectory=*Каталог_приложения*
ExecStart=*Каталог_приложения*/tools/run.sh
ExecReload=/bin/kill -s HUP $MAINPID
KillMode=mixed
TimeoutStopSec=5
PrivateTmp=true

[Install]
WantedBy=multi-user.target
```
Измените пользователя и группу на те, под чьими правами будет запускаться демон. Вместо 
"*Каталог_приложения*" укажите абсолютный путь до приложения.

Активация и запуск Unit-файла:
```
systemctl enable periodic.service
systemctl start periodic.service
```

## Настройка Nginx reverse-proxy для приложения

1. создайте файл periodic в каталоге sites-available со следующим содержимым:
```
server {
	listen 80;
	server_name *имя_сайта*;

	location / {
		proxy_set_header X-Real-IP $remote_addr;
		proxy_set_header Host $host;
		proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
		proxy_pass http://127.0.0.1:8001;
	}
		
	location /static/ {
		alias *Каталог_приложения*/static/;
		autoindex off;
	}
		
	location /media/ {
		alias *Каталог_приложения*/media/;
		autoindex off;
	}
		
	location ~ ^/media/library/(?<periodic>[^/]+)/(?<year>[^/]+)/(?<file>[0-9\.pdf]+)$ {
		add_header Cache-Control 'no-store, no-cache';
		auth_request /secure;
		max_ranges 0;
		types { application/octet-stream .pdf; }
		default_type  application/octet-stream;
		alias *Каталог_приложения*/media/library/$periodic/$year/$file;
	}
		
	location /secure {
		proxy_pass http://127.0.0.1:8001/secure;
		proxy_pass_request_body off;
		proxy_set_header X-Real-IP $remote_addr;
		proxy_set_header Host $host;
		proxy_set_header Content-Length "";
		proxy_set_header X-Original-URI $request_uri;
	}
}
```
, где *Каталог_приложения* - ваш каталог приложения; *имя_сайта* - ваше имя сайта

2. Создайте "мягкую ссылку" на этот файл в каталоге `sites-enabled` и перезапустите nginx.

Панель администрирования приложения: `www.имя_сайта/admin`


## Настройка автоматического пополнения Архива периодики

Создайте структуру следующую структуру каталогов:
```
- *каталог архива*
-- каталог с названием периодического издания
--- год
---- aa.dd.mm.yy.pdf
---- aa.dd.mm.yy.pdf
---- aa.dd.mm.yy.pdf
--- год
---- aa.dd.mm.yy.pdf
--- год
---- aa.dd.mm.yy.pdf
-- каталог с названием периодического издания
...
```
например:
```
- Архив
-- Юный техник
--- 1991
---- yt.12.01.91.pdf
---- yt.12.02.91.pdf
---- yt.12.03.91.pdf
--- 1993
-- Игромания
--- 2005
---- im.01.11.05.pdf
--- 2006
...
```
Файлы копируемые в подкаталоги должны соответствовать формату имени aa.dd.mm.yy.pdf, где
`aa` - любые 2 символа; `dd` - день месяца; `mm` - номер месяца; `yy` - 2 последние цифры года;

Для Linux необходимо прописать в планировщик cron:

`0,20,40 * * * *  *Каталог_приложения*/tools/autoadd.sh *каталог архива* >>/var/log/crond.log 2>&1`

Для Windows возможно создать задачу в планировщике задач, или в аналогичном стороннем ПО:

`*Каталог_приложения*/tools/autoadd.bat *каталог архива*`

### Примечание:


## Изменение Лого и правил пользования
1. Замените файлы, которые находятся по пути: `*Каталог_приложения*/library/static/library/img`

2. Выполните сборку статики, выполнив активацию виртуального окружения и соответствующей команды.

Также, вы можете изменить шаблоны, по пути: `*Каталог_приложения*/library/templates/library`

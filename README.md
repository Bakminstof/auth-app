API авторизации и управления пользователями. 


[Попробовать](https://176.109.100.7:50505 "API") 
[Документация](https://176.109.100.7:50505/docs "API")

Базовый URL:
- https://176.109.100.7:50505

Эндпоинты:
- __POST__ - /auth/login - Вход
- __POST__ - /auth/logout - Выход
- __POST__ - /auth/register - Регистрация
- __GET__ - /users/all - Получить всех пользователй
- __POST__ - /users/add - Добавить пользователя
- __PATCH__ - /users/{user_id}/update - Обновить данные пользователя по ID
- __DELETE__ - /users/{user_id}/delete - Удалить пользователя по ID

Для локального запуска приложения необходимо сгенерировать несколько ключей.

Ключи для генерации JWT
```shell
CERTS_DIR="certs"

# Private key
openssl genrsa -out "$CERTS_DIR/auth-jwt-private.pem" 2048

# Public key
openssl rsa -in "$CERTS_DIR/auth-jwt-private.pem" -outform PEM -pubout -out "$CERTS_DIR/auth-jwt-public.pem"
```

Ключи для протокола HTTPS
```shell
HOST="HOST_HERE"  # Указать свой IP 

TSL_DIR="certs"

PRIVATE_KEY="$TSL_DIR/private.pem"
PUBLIC_KEY="$TSL_DIR/public.pem"

openssl genrsa -out "$PRIVATE_KEY" 2048
openssl req -new -x509 -nodes -days 3650 -key "$PRIVATE_KEY" -out "$PUBLIC_KEY" -subj "/CN=$HOST"
```

Вся настройка осуществляется по средства переменных окружения в файлах __.env__. Для контейнеров это файл __.env__, 
для приложения - __.env.template__, __.env__, __dev.env__, __prod.env__ в каталоге __src/env__.

Для запуска контейнера необходимо выполнить следующие команды
```shell
export $(grep -v '^#' .env | tr '\r' '\0' | xargs -d '\n')

docker image build -t "$APP_IMAGE_TAG" ./

docker stack deploy --with-registry-auth -c <(docker-compose config) auth-app 
# Если не используется docker swarm то запускать так: docker-compose up 
```
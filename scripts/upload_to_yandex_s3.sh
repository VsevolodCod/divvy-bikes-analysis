#!/bin/bash

# Скрипт для загрузки данных в Yandex Object Storage
# Использование: ./scripts/upload_to_yandex_s3.sh

set -e

GREEN='\033[0;32m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
NC='\033[0m' 

echo -e "${YELLOW}=== Загрузка данных в Yandex Object Storage ===${NC}\n"

if [ -z "$YC_ACCESS_KEY_ID" ] || [ -z "$YC_SECRET_ACCESS_KEY" ]; then
    echo -e "${RED}Ошибка: Не установлены переменные окружения${NC}"
    echo "Необходимо установить:"
    echo "  export YC_ACCESS_KEY_ID='your-key-id'"
    echo "  export YC_SECRET_ACCESS_KEY='your-secret-key'"
    echo ""
    echo "Получить ключи можно в консоли Yandex Cloud:"
    echo "https://console.cloud.yandex.ru/folders/<folder-id>/service-accounts"
    exit 1
fi

BUCKET_NAME="${YC_BUCKET_NAME:-divvy-bikes-data}"
ENDPOINT_URL="https://storage.yandexcloud.net"
REGION="ru-central1"

echo -e "${GREEN}Bucket:${NC} $BUCKET_NAME"
echo -e "${GREEN}Region:${NC} $REGION"
echo -e "${GREEN}Endpoint:${NC} $ENDPOINT_URL\n"

export AWS_ACCESS_KEY_ID=$YC_ACCESS_KEY_ID
export AWS_SECRET_ACCESS_KEY=$YC_SECRET_ACCESS_KEY
export AWS_DEFAULT_REGION=$REGION

echo -e "${YELLOW}Проверка bucket...${NC}"
if aws s3 ls "s3://$BUCKET_NAME" --endpoint-url=$ENDPOINT_URL 2>/dev/null; then
    echo -e "${GREEN}Bucket существует${NC}\n"
else
    echo -e "${YELLOW}Bucket не найден. Создаем...${NC}"
    aws s3 mb "s3://$BUCKET_NAME" --endpoint-url=$ENDPOINT_URL
    echo -e "${GREEN}Bucket создан${NC}\n"
fi

echo -e "${YELLOW}Загрузка данных (это может занять время)...${NC}"
aws s3 sync data/ "s3://$BUCKET_NAME/data/" \
    --endpoint-url=$ENDPOINT_URL \
    --exclude ".DS_Store" \
    --exclude ".gitkeep" \
    --no-progress

echo -e "\n${GREEN}✓ Данные успешно загружены!${NC}"
echo -e "\n${YELLOW}Содержимое bucket:${NC}"
aws s3 ls "s3://$BUCKET_NAME/data/" --endpoint-url=$ENDPOINT_URL --recursive --human-readable --summarize | tail -2
echo -e "\n${GREEN}Готово!${NC}"

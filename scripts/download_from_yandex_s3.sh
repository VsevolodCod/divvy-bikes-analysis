#!/bin/bash

# Скрипт для скачивания данных из Yandex Object Storage
# Использование: ./scripts/download_from_yandex_s3.sh

set -e

GREEN='\033[0;32m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
NC='\033[0m'

echo -e "${YELLOW}=== Скачивание данных из Yandex Object Storage ===${NC}\n"

if [ -z "$YC_ACCESS_KEY_ID" ] || [ -z "$YC_SECRET_ACCESS_KEY" ]; then
    echo -e "${RED}Ошибка: Не установлены переменные окружения${NC}"
    echo "Необходимо установить:"
    echo "  export YC_ACCESS_KEY_ID='your-key-id'"
    echo "  export YC_SECRET_ACCESS_KEY='your-secret-key'"
    exit 1
fi

BUCKET_NAME="${YC_BUCKET_NAME:-divvy-bikes-data}"
ENDPOINT_URL="https://storage.yandexcloud.net"
REGION="ru-central1"

export AWS_ACCESS_KEY_ID=$YC_ACCESS_KEY_ID
export AWS_SECRET_ACCESS_KEY=$YC_SECRET_ACCESS_KEY
export AWS_DEFAULT_REGION=$REGION

echo -e "${GREEN}Bucket:${NC} $BUCKET_NAME"
echo -e "${GREEN}Скачивание в:${NC} ./data/\n"

mkdir -p data

echo -e "${YELLOW}Скачивание данных...${NC}"
aws s3 sync "s3://$BUCKET_NAME/data/" data/ \
    --endpoint-url=$ENDPOINT_URL \
    --no-progress

echo -e "\n${GREEN}✓ Данные успешно скачаны!${NC}"

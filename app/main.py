import logging

import redis
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel

app = FastAPI()

# Настройка подключения к Redis
redis_client = redis.Redis(host='redis', port=6379, db=0)

# Настройка логгирования
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class PhoneAddress(BaseModel):
    phone: str
    address: str


@app.post("/write_data")
async def write_data(data: PhoneAddress):
    """Запись или обновление данных телефона и адреса"""
    try:
        # Валидация номера телефона (простая проверка на цифры)
        if not data.phone.isdigit():
            raise HTTPException(status_code=400, detail="Phone number should contain only digits")

        redis_client.set(data.phone, data.address)
        logger.info(f"Data saved: phone={data.phone}, address={data.address}")
        return {"status": "success", "phone": data.phone}
    except Exception as e:
        logger.error(f"Error saving data: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/check_data")
async def check_data(phone: str):
    """Получение адреса по номеру телефона"""
    try:
        address = redis_client.get(phone)
        if address is None:
            raise HTTPException(status_code=404, detail="Phone not found")

        logger.info(f"Data retrieved for phone: {phone}")
        return {"phone": phone, "address": address.decode('utf-8')}
    except Exception as e:
        logger.error(f"Error retrieving data: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/")
async def root():
    """Служебная ручка-заглушка для главной"""
    return {"message": "Phone Address Service is running"}

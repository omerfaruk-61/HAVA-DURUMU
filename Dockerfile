# Python resmi imajını baz al
FROM python:3.10-slim

# Çalışma dizinini ayarla
WORKDIR /app

# Kütüphane listesini ve kodları kopyala
COPY main.py .

# Gerekli kütüphaneleri yükle
RUN pip install --no-cache-dir fastapi uvicorn requests apscheduler

# 8000 portunu dışarı aç
EXPOSE 8000

# Sunucuyu başlat
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]
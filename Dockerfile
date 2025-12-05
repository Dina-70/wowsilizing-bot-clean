# ====================================================================
# ПОЛНЫЙ И ПРАВИЛЬНЫЙ DOCKERFILE ДЛЯ TELEGRAM БОТА
# ====================================================================
# Этот файл содержит ВСЕ необходимые инструкции для Railway
# Скопируйте ВСЁ содержимое этого файла в ваш Dockerfile на GitHub
# ====================================================================

# Базовый образ Python 3.11
FROM python:3.11-slim

# Установка рабочей директории
WORKDIR /app

# Установка системных зависимостей (FFmpeg, wget)
RUN apt-get update && \
    apt-get install -y --no-install-recommends \
    ffmpeg \
    wget \
    && apt-get clean \
    && rm -rf /var/lib/apt/lists/*

# Установка yt-dlp
RUN wget https://github.com/yt-dlp/yt-dlp/releases/latest/download/yt-dlp -O /usr/local/bin/yt-dlp && \
    chmod +x /usr/local/bin/yt-dlp

# Проверка установки системных утилит
RUN ffmpeg -version && ffprobe -version && yt-dlp --version

# Копирование файла зависимостей Python
COPY requirements.txt .

# Установка Python зависимостей
RUN pip install --no-cache-dir -r requirements.txt

# Копирование всех файлов приложения
COPY . .

# Команда запуска бота
CMD ["python", "bot.py"]

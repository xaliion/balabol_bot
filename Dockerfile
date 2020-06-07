# Используем базовый образ для нашего
FROM python:stretch

# Создаём директорию бота
RUN mkdir /balabol_bot

# Копируем все файлы из текущей директории в директорию бота
COPY .aws ~/
COPY . /balabol_bot

# Устанавливаем рабочую директорию
WORKDIR /balabol_bot

# Устанавливаем pytelegrambotapi и apiai
RUN pip3 install --no-cache-dir pytelegrambotapi
RUN pip3 install --no-cache-dir boto3

# Указываем команды для выполнения после запуска контейнера
CMD ["python3", "bot.py"]

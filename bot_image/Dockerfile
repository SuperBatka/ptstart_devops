FROM debian

RUN apt-get update && apt-get install python3 build-essential python3-paramiko python3-python-telegram-bot python3-psycopg2 python3-dotenv -y 
RUN mkdir -p /opt/app
WORKDIR /opt/app
#COPY requirements.txt requirements.txt
COPY bot.py bot.py
EXPOSE 5000

#RUN pip3 install --no-cache-dir -r requirements.txt

CMD ["python3", "bot.py"]
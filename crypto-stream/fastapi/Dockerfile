FROM python:3.11-slim

WORKDIR /app

RUN apt-get update && apt-get install -y netcat-traditional && rm -rf /var/lib/apt/lists/*

COPY requirements.txt .

RUN pip install -r requirements.txt

COPY . .

RUN chmod +x start.sh
ENTRYPOINT ["./start.sh"]
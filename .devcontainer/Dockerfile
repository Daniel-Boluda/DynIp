FROM python:3.9-slim

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY dynip_script.py .

RUN apt-get update && apt-get install -y curl

CMD ["python", "dynip_script.py"]
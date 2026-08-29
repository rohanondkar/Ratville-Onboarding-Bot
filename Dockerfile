FROM python:3.12-slim

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY onboarding_bot.py .

CMD ["python", "onboarding_bot.py"]

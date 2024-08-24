FROM python:3.11-slim-bookworm

WORKDIR /app

# Install agentforge directly
RUN pip install agentforge

COPY . .

CMD ["python", "main.py"]

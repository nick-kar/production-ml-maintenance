FROM python:3.12-slim
WORKDIR /app
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt
COPY mlops mlops
RUN python -m mlops.cli train --version v1 && python -m mlops.cli promote v1
RUN useradd -m service && mkdir -p /app/runtime && chown -R service:service /app
USER service
EXPOSE 8000
CMD ["python", "-m", "uvicorn", "mlops.api:app", "--host", "0.0.0.0", "--port", "8000"]

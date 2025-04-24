FROM python:3.10-slim
WORKDIR /Compute-Intensive
COPY . .
RUN pip install --no-cache-dir -r requirements.txt
CMD ["python", "script.py"]
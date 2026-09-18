FROM python:3.14.4

WORKDIR /SupportFlow

ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

RUN pip install --upgrade pip

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

RUN chmod +x /SupportFlow/entrypoint.sh

ENTRYPOINT ["/SupportFlow/entrypoint.sh"]

EXPOSE 8000

CMD ["python", "./manage.py", "runserver", "0.0.0.0:8000"]

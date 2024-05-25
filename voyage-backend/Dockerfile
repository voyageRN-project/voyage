# 1
FROM python:3.9

# 2
RUN pip3 install -r requirements.txt

# 3
COPY src/ /app
WORKDIR /app

# 4
ENV PORT 8080

# 5
CMD ["python3 main.py"]
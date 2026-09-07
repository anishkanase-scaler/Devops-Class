FROM python:3.12
WORKDIR /app
COPY requirements.txt .
RUN pip install -r requirements.txt
COPY app.py .
CMD ["python", "app.py"]

# Now Nodejs didnt need requirements.txt, because it built-in http module, but in Oython we're using Flask
# We need Flask or HTTP, because application must be a web application and you need to see "Hello World" in a browser, print("Hello World") will jsu print inside terminal, and not in browser. 
# app/Dockerfile

FROM python:3.12

WORKDIR /app

RUN apt-get update && apt-get install -y && apt install python3-pip -y     && apt install python3-venv -y \
    build-essential \
    && rm -rf /var/lib/apt/lists/*

COPY . .

# RUN pip3 install -r requirements.txt
RUN pip3 install --use-pep517 sortedcontainers setuptools pytz netifaces DBUtils zipp urllib3 tzdata tqdm socketio sniffio six PySocks PyMySQL Pygments numpy multidict mdurl MarkupSafe itsdangerous idna h11 greenlet frozenlist exceptiongroup et-xmlfile dnspython click charset-normalizer certifi blinker attrs async-timeout yarl wsproto Werkzeug retrying requests python-dateutil outcome openpyxl markdown-it-py Jinja2 javalang importlib-metadata eventlet aiosignal trio rich requests-toolbelt pyapollos pandas Flask aiohttp trio-websocket python-gitlab openai selenium

EXPOSE 5000
EXPOSE 7477

# ENV PORT=80

# "--host=0.0.0.0"
ENTRYPOINT ["python3", "app.py", "--server.port=7477", "--server.address=0.0.0.0"]

# CMD ["python", "service/app.py"]
# RUN echo 'python service/app.py &' >> /entrypoint.sh && \
#     echo 'streamlit run service/langchain_PDF.py --server.port=5000 --server.address=0.0.0.0' >> /entrypoint.sh && \
#     chmod +x /entrypoint.sh

# ENTRYPOINT ["/bin/bash", "/entrypoint.sh"]
FROM python:3.8

WORKDIR /app

RUN ulimit -a && cat /proc/self/limits

COPY ./src/main/python/requirements.txt /app/requirements.txt
ENV PATH="/root/.local/bin:${PATH}"
ENV PYTHONPATH=.:$PYTHONPATH
RUN pip3  install  --user --progress-bar off -r /app/requirements.txt

CMD ["sleep", "infinity"]
#CMD [ "python3", "crawler.py"]
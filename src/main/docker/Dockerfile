FROM python:3.12.11

WORKDIR /app

RUN ulimit -a && cat /proc/self/limits

COPY ./src/main/app/requirements.txt /app/requirements.txt
ENV PATH="/root/.local/bin:${PATH}"
ENV PYTHONPATH=.:$PYTHONPATH
ENV OTEL_BSP_MAX_QUEUE_SIZE=2048 \
    OTEL_BSP_MAX_EXPORT_BATCH_SIZE=256 \
    OTEL_BSP_SCHEDULE_DELAY=5000 \
    OTEL_BSP_EXPORT_TIMEOUT=30
    
RUN pip3  install  --user --progress-bar off -r /app/requirements.txt

COPY ./src/main/app /app

#CMD ["sleep", "infinity"]
CMD [ "python3", "crawler.py"]
FROM python:3.8
#https://medium.com/@DahlitzF/run-python-applications-as-non-root-user-in-docker-containers-by-example-cba46a0ff384

RUN pip3 install --upgrade pip

#RUN adduser worker
RUN addgroup worker && useradd -g worker worker
WORKDIR /home/worker


COPY ./src/main/python/ /home/worker/


RUN chown worker:worker /home/worker/ -R
USER worker

ENV PATH="/home/worker/.local/bin:${PATH}"
ENV PYTHONPATH=.:$PYTHONPATH


RUN pip3  install  --user -r /home/worker/requirements.txt

RUN python3 --version

USER worker 

#CMD [ "python3", "crawler.py"]
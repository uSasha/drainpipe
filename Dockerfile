FROM python:3.7.4-buster

RUN mkdir -p /app \
    && chown -R nobody:nogroup /app

# user: https://medium.com/@mccode/processes-in-containers-should-not-run-as-root-2feae3f0df3b
USER nobody

# install python requirements in separate env to avoid runnnig as root and to have clean env (no system packages)
COPY requirements.txt /app/requirements.txt
RUN cd /app/ \
    && python -m venv /app/env \
    && /app/env/bin/pip install -r requirements.txt
ENV PATH /app/env/bin:$PATH

VOLUME /app/data
COPY src /app/


WORKDIR /app/
ENTRYPOINT ["python", "drainpipe.py"]

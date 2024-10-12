FROM registry.kmf.kz/images/python-3.11:poetry-1.6.1 AS builder

WORKDIR /app
COPY pyproject.toml poetry.lock ./
RUN poetry config virtualenvs.create false \
    && poetry install --no-interaction --no-ansi

FROM registry.kmf.kz/images/python-3.11:latest as production

ENV PYTHONPATH=/app

COPY --from=builder /usr/local/lib/python3.11/site-packages/ /usr/local/lib/python3.11/site-packages/
COPY --from=builder /usr/local/bin/ /usr/local/bin/

COPY . /app/src

RUN useradd -m -u 1000 appuser
RUN chown -R appuser /app

RUN sed -i 's/\r$//g' /app/src/start
RUN chmod +x /app/src/start

WORKDIR /app/src

ENTRYPOINT ["/app/src/start"]

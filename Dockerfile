FROM ubuntu:22.04

# 標準出力と標準エラー出力がバッファリングされないようにする
ENV PYTHONUNBUFFERED=1

SHELL ["/bin/bash", "-c"]

RUN apt update
RUN apt install -y curl

RUN curl -sSf https://rye-up.com/get | RYE_INSTALL_OPTION="--yes" bash

WORKDIR /app

COPY pyproject.toml README.md ./

ENV PATH="/root/.rye/shims:${PATH}"
RUN if [ -f pyproject.toml ]; then rye sync; fi

CMD [ "rye", "run", "python", "src/run.py"]
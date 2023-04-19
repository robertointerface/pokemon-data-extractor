FROM ubuntu:20.04 as  pokemon-extractor-image-base
ENV DEBIAN_FRONTEND=noninteractive
ENV PATH="/root/.local/bin:$PATH"
ENV PYTHONUNBUFFERED 1
ENV WORKING_DIR=/pokemon-data-extractor
WORKDIR ${WORKING_DIR}
RUN apt-get update
RUN apt-get install -y build-essential \
    gcc \
    cmake \
    git \
    curl


RUN apt-get install unzip -y
RUN apt-get install --no-install-recommends -y python3.8 python3.8-dev python3.8-venv python3-distutils
RUN update-alternatives --install /usr/bin/python python /usr/bin/python3.8 20

FROM pokemon-extractor-image-base as pokemon-extractor-python-packages

RUN curl https://bootstrap.pypa.io/get-pip.py -o get-pip.py && python get-pip.py
RUN curl -sSL https://install.python-poetry.org | POETRY_VERSION=1.3.2 python3.8 -

COPY README.md ${WORKING_DIR}/
COPY ./pyproject.toml ${WORKING_DIR}/
COPY ./poetry.lock ${WORKING_DIR}/
RUN poetry config virtualenvs.create true
RUN poetry config virtualenvs.in-project true
RUN poetry run pip install "setuptools==59.8.0"
ENV PATH=/${WORKING_DIR}/.venv/bin:$PATH

RUN cd ${WORKING_DIR} && poetry install --without dev --no-root

FROM pokemon-extractor-python-packages as pokemon-extractor-code
COPY ./src ${WORKING_DIR}/src
RUN poetry install --only-root


FROM pokemon-extractor-code as pokemon-extractor-test
COPY ./test ${WORKING_DIR}/test
RUN poetry install --with dev
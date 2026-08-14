FROM gcr.io/oss-fuzz-base/base-builder-python

WORKDIR $SRC/memdevice-bench
COPY . .
COPY .clusterfuzzlite/build.sh /src/build.sh

RUN chmod +x /src/build.sh

RUN python3 -m pip install .

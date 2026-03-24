# 基础镜像
# https://hub.docker.com/_/python/tags?page=1&name=3.11-slim-bullseye
FROM docker.io/python:3.11-slim-bullseye

MAINTAINER myh

# 增加语言 utf-8
ENV LANG=zh_CN.UTF-8
ENV LC_CTYPE=zh_CN.UTF-8
ENV LC_ALL=C
ENV PYTHONPATH=/data/InStock
ENV UV_INDEX_URL=https://mirrors.aliyun.com/pypi/simple
ENV UV_LINK_MODE=copy
ENV UV_PROJECT_ENVIRONMENT=/data/InStock/.venv
ENV PATH=/data/InStock/.venv/bin:/usr/local/bin:${PATH}

EXPOSE 9988

# 使用国内镜像地址加速。修改 debian apt 更新地址，设置时区
# https://opsx.alibaba.com/mirror
RUN sed -i "s@http://\\(deb\\|security\\).debian.org@https://mirrors.aliyun.com@g" /etc/apt/sources.list && \
    ln -sf /usr/share/zoneinfo/Asia/Shanghai /etc/localtime && \
    echo "Asia/Shanghai" > /etc/timezone && \
    apt-get update && \
    apt-get install -y cron gcc make python3-dev default-libmysqlclient-dev build-essential pkg-config curl supervisor && \
    curl -LsSf https://astral.sh/uv/install.sh | env UV_INSTALL_DIR=/usr/local/bin sh && \
    mkdir ta-lib && \
    curl -SL https://github.com/ta-lib/ta-lib/releases/latest/download/ta-lib-0.6.4-src.tar.gz | tar -xz --strip-components=1 -C ./ta-lib && \
    cd ta-lib/ && \
    ./configure && \
    make && \
    make install && \
    cd .. && \
    rm -rf ta-lib* && \
    apt-get --purge remove -y gcc make python3-dev default-libmysqlclient-dev curl build-essential pkg-config && \
    rm -rf /root/.cache/* /var/lib/apt/lists/* && \
    apt-get clean && \
    apt-get autoclean && \
    apt-get autoremove -y

WORKDIR /data/InStock

# InStock 软件
COPY . /data/InStock
COPY cron/cron.hourly /etc/cron.hourly
COPY cron/cron.workdayly /etc/cron.workdayly
COPY cron/cron.monthly /etc/cron.monthly

# add cron service.
# 任务调度
RUN uv sync --frozen --no-dev && \
    chmod 755 /data/InStock/instock/bin/run_*.sh && \
    chmod 755 /etc/cron.hourly/* && \
    chmod 755 /etc/cron.workdayly/* && \
    chmod 755 /etc/cron.monthly/* && \
    echo "SHELL=/bin/sh \n\
PATH=/usr/local/sbin:/usr/local/bin:/sbin:/bin:/usr/sbin:/usr/bin \n\
# min hour day month weekday command \n\
*/30 9,10,11,13,14,15 * * 1-5 /bin/run-parts /etc/cron.hourly \n\
30 17 * * 1-5 /bin/run-parts /etc/cron.workdayly \n\
30 10 * * 3,6 /bin/run-parts /etc/cron.monthly \n" > /var/spool/cron/crontabs/root && \
    chmod 600 /var/spool/cron/crontabs/root

ENTRYPOINT ["supervisord", "-n", "-c", "/data/InStock/supervisor/supervisord.conf"]

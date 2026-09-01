# ERPNext v16 deployment image.
# Two-stage intent: build with frappe/erpnext cloned at exact source refs +
# user's Postgres patches + vehicle_management app baked in.
FROM python:3.14-slim-bookworm

ENV PYTHONUNBUFFERED=1 \
    DEBIAN_FRONTEND=noninteractive \
    NODE_MAJOR=24

RUN apt-get update && apt-get install -y --no-install-recommends \
        curl git build-essential pkg-config libpq-dev libffi-dev libssl-dev \
        default-libmysqlclient-dev libmariadb-dev ca-certificates gnupg \
        libpango-1.0-0 libpangoft2-1.0-0 libharfbuzz0b libjpeg-dev libopenjp2-7 \
        libpq5 xfonts-75dpi xfonts-base fonts-liberation libcairo2 postgresql-client \
        openssh-client \
        && rm -rf /var/lib/apt/lists/*

RUN mkdir -p /etc/apt/keyrings \
    && curl -fsSL https://deb.nodesource.com/gpgkey/nodesource-repo.gpg.key | gpg --dearmor -o /etc/apt/keyrings/nodesource.gpg \
    && echo "deb [signed-by=/etc/apt/keyrings/nodesource.gpg] https://deb.nodesource.com/node_${NODE_MAJOR}.x nodistro main" > /etc/apt/sources.list.d/nodesource.list \
    && apt-get update && apt-get install -y nodejs \
    && corepack enable && corepack prepare yarn@1.22.22 --activate \
    && rm -rf /var/lib/apt/lists/*

COPY requirements.txt /tmp/requirements.txt
RUN pip install --no-cache-dir -r /tmp/requirements.txt \
    && pip install --no-cache-dir frappe-bench setuptools wheel

# Artifacts from the source bench (patches, app, dump, public files)
COPY artifacts/ /tmp/artifacts/
# Site config (postgres/redis via service names)
COPY sites/ /workspace/frappe-bench/sites/
COPY build_prep.sh /workspace/frappe-bench/build_prep.sh
COPY restore.sh /workspace/frappe-bench/restore.sh
COPY entrypoint.sh /workspace/frappe-bench/entrypoint.sh
RUN chmod +x /workspace/frappe-bench/*.sh

WORKDIR /workspace/frappe-bench

# Clone frappe/erpnext at exact refs + apply patches + install app + yarn
RUN bash /workspace/frappe-bench/build_prep.sh

EXPOSE 8000 9000

CMD ["/bin/bash"]

#!/bin/bash

PROMETHEUS_VERSION="2.16.0"

yum install wget -y
wget https://github.com/prometheus/prometheus/releases/download/v${PROMETHEUS_VERSION}/prometheus-${PROMETHEUS_VERSION}.linux-amd64.tar.gz
tar xvzf prometheus-${PROMETHEUS_VERSION}.linux-amd64.tar.gz
mv prometheus-${PROMETHEUS_VERSION}.linux-amd64 prometheuspackage

useradd --no-create-home --shell /bin/false prometheus
for i in rules rules.d files_sd; do sudo mkdir -p /etc/prometheus/${i}; done
for i in rules rules.d files_sd; do sudo chown -R prometheus:prometheus /etc/prometheus/${i}; done
for i in rules rules.d files_sd; do sudo chmod -R 775 /etc/prometheus/${i}; done

mkdir /var/lib/prometheus
chown prometheus:prometheus /var/lib/prometheus

cp -v prometheuspackage/prometheus /usr/bin/
cp -v prometheuspackage/promtool /usr/bin/
chown prometheus:prometheus /usr/bin/prometheus
chown prometheus:prometheus /usr/bin/promtool

cp -v -r prometheuspackage/consoles /etc/prometheus
cp -v -r prometheuspackage/console_libraries /etc/prometheus
chown -R prometheus:prometheus /etc/prometheus/consoles
chown -R prometheus:prometheus /etc/prometheus/console_libraries

cat <<EOF > /etc/prometheus/prometheus.yml
global:
  scrape_interval: 15s
  evaluation_interval: 15s

alerting:
  alertmanagers:
  - static_configs:
    - targets:
      # - alertmanager:9093

scrape_configs:
  - job_name: 'prometheus_master'
    scrape_interval: 15s
    static_configs:
      - targets: ['localhost:9090']
EOF
chown prometheus:prometheus /etc/prometheus/prometheus.yml

cat <<EOF > /etc/systemd/system/prometheus.service
[Unit]
Description=Prometheus
Documentation=https://prometheus.io/docs/introduction/overview/
Wants=network-online.target
After=network-online.target

[Service]
Type=simple
Environment="GOMAXPROCS=10"
User=prometheus
Group=prometheus
ExecReload=/bin/kill -HUP \$MAINPID
ExecStart=/usr/bin/prometheus \
--config.file /etc/prometheus/prometheus.yml \
--storage.tsdb.path /var/lib/prometheus/ \
--web.console.templates=/etc/prometheus/consoles \
--web.console.libraries=/etc/prometheus/console_libraries \
--web.listen-address=0.0.0.0:9090 \
--web.enable-admin-api \
--web.external-url=

SyslogIdentifier=prometheus
Restart=always

[Install]
WantedBy=multi-user.target
EOF

systemctl daemon-reload

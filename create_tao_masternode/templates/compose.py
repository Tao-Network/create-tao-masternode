compose = """version: "3.4"

services:

  tao:
    image: taoblockchain/node:stable
    environment:
      IDENTITY: $IDENTITY
      PRIVATE_KEY: $PRIVATE_KEY
      BOOTNODES: {{ bootnodes }}
      NETWORK_ID: {{ network_id }}
      VERBOSITY: {{ logging_level }}
      NETSTATS_HOST: wss://stats.tao.network
      NETSTATS_PORT: 443
      WS_SECRET: {{ ws_secret }}
    volumes:
      - $DATA:/tao2/data
    ports:
      - 30303:30303/tcp
      - 30303:30303/udp
      {%- if expose_rpc %}
      - 8545:8545
      {%- endif %}
      {%- if expose_ws %}
      - 8546:8546
      {%- endif %}
    restart: always
{% if storage == "docker volume" %}
volumes:
  {{ data }}:
    {%- if external == "True" %}
    external: true
    {%- endif %}
{% endif %}
"""

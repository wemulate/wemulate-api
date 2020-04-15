{% set tag = salt.pillar.get('event_tag') %}
{% set data = salt.pillar.get('event_data') %}

accept_minion_key:
  salt.wheel:
    - name: key.accept
    - match: {{ data.id }}

wait_for_connection:
  salt.wait_for_event:
  - name: {{ tag }}
  - id_list:
    - {{ data.id }}
  - require:
    - accept_minion_key

clear_cache:
  salt.function:
    - name: saltutil.clear_cache
    - tgt: {{ data.id }}

sync_all_modules:
  salt.function:
    - name: saltutil.sync_all
    - tgt: {{ data.id }}

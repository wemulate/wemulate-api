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
  module.run:
  - name: saltutil.clear_cache

sync_all_modules:
  module.run:
  - name: saltutil.sync_all

~                                    

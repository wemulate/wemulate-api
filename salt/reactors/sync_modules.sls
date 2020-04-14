{% if data['act'] == 'accept' %}
sync_modules:
  local.saltutil.sync_all:
  - tgt: data[id]
{% endif %}


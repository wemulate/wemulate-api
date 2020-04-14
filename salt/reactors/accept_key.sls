{% if data['auth'] == 'pend' %}
accept_new_minion:
  wheel.key.accept:
    - match: {{ data['id'] }}
{% endif %}


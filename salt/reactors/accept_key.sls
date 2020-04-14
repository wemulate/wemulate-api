{% if 'act' in data and data['act'] == 'pend' %}
invoke_orchestrate_file:
  runner.state.orchestrate:
    - args:
        - mods: orchestrate.add_device
        - pillar:
            event_tag: {{ tag }}
            event_data: {{ data|json }}
{% endif %}


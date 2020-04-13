{% if data['act'] == 'accept' %}
add_device:
  runner.http.query:
    - url: http://127.0.0.1/api/v1/devices
    - kwarg:
      method: POST
      header_list:
        - "Accept: application/json"
        - "Content-Type: application/json"
      data: {
        "name": {{ data['id'] }}
      }
{% endif %}


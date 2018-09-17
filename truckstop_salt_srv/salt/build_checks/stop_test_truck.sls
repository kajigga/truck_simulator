{% set image_name = 'test_truck' %}

# Set the buildName
{% set buildName = salt['pillar.get']('post:buildName')|replace('#','num_') %}

# stop a container using the new image
{% set truck_id = 'test_truck' %}
stop_test_container:
  docker_container.stopped:
    - name: {{buildName}}
    - image: {{image_name}}:{{buildName}}
    - force: true


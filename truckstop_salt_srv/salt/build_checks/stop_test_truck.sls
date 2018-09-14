{% set image_name = 'test_truck' %}

# # build an image based on the dev branch
{% set buildName = salt['pillar.get']('post:buildName')|replace('#','num_') %}

# # start a container using the new image
{% set truck_id = 'test_truck' %}
stop_test_container:
  docker_container.stopped:
    - name: {{buildName}}
    - image: {{image_name}}:{{buildName}}
    - force: true
    - environment:
      - TRUCK_ID: {{truck_id}}
    - watch:
      - build_test_image


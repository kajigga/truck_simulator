# A successfull build just arrived.
# 
# Let's launch a testTruck in docker, have it run tests and verify connectivity
# with TruckStop (telemetry arriving, etc)

# checkout the latest from the #dev branch
test_pillar:
  test.check_pillar:
    - present:
      - post
      - 'post:buildName'
      - 'truckstop:repo_url'

checkout_testTruck_code:
  git.latest:
    - name: {{  salt['pillar.get']('truckstop:repo_url') }}
    - rev: develop
    - branch: develop
    - force_fetch: True
    - force_reset: True
    - target: /tmp/testTruck
    - identity: /etc/salt/git_id_rsa

test_pillar_out:
  test.configurable_test_state:
    - name: pillar output
    - changes: False
    - result: True
    - comment: |
        post: {{ salt['pillar.get']('post') }}

# # build an image based on the dev branch
{% set buildName = salt['pillar.get']('post:buildName')|replace('#','num_') %}

{% set image_name = 'test_truck' %}

# make sure image is present (and rebuilt) before testing
build_test_image:
  docker_image.present:
    - name: "{{ image_name }}"
    - build: /tmp/testTruck/
    - tag: {{buildName}} 
    #- dockerfile: /tmp/testTruck/DockerFile
    - force: true
    - watch:
      - test_pillar

# # start a container using the new image
{% set truck_id = 'test_truck' %}
start_test_container:
  docker_container.running:
    - name: {{buildName}}
    - image: {{image_name}}:{{buildName}}
    - force: true
    - environment:
      - TRUCK_ID: {{truck_id}}
      - TRUCKSTOP_URL: {{ salt['pillar.get']('truckstop:truckstop_url') }}
    - watch:
      - build_test_image

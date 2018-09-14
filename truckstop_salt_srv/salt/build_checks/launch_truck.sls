# NOTE: Not sure, but I think this state may be obsolete
#

checkout_testTruck_code:
  git.latest:
    - name: {{  salt['pillar.get']('truckstop:repo_url') }}
    - rev: dev
    - branch: dev
    - force_fetch: True
    - force_reset: True
    - target: /tmp/testTruck
    - identity: /etc/salt/git_id_rsa

test_pillar:
  test.check_pillar:
    - present:
      - truck_id

# make sure image is present (and rebuilt) before testing
build_image:
  docker_image.present:
    - name: "truck"
    - build: /tmp/testTruck/
    - tag: 'prod'
    - require:
      - test_pillar

# # start a container using the new image
{% set truck_id = salt['pillar.get']('truck_id') %}
start_test_container:
  docker_container.running:
    - name: {{truck_id}}
    - image: 'truck:prod'
    - environment:
      - TRUCK_ID: {{truck_id}}
      - TRUCKSTOP_URL: {{ salt['pillar.get']('truckstop:truckstop_url')}}
    - require:
      - build_image


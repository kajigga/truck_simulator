test_update_app_pillar:
  test.check_pillar:
    - present:
      - 'google:api_key'

add_single_page_app:
  file.recurse:
    - name: /etc/salt/app
    - source: salt://enable_truckstop_tracker/files/app/
    - template: jinja
    - exclude_pat: '*.swp' # TODO I would like to add the data.js file to the exclude list

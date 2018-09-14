# /srv/salt/top.sls
base:
  'truckstop-master':
    - truckstop_master_build
    - enable_truckstop_tracker

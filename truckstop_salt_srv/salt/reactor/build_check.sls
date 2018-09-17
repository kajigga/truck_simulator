{% if data['post']['event'] == 'success' %}
# A new build was just successfull. Orchestration a test build of the resulting
# docker image and other things like that.
call_build_check_orch:
  runner.state.orchestrate:
    - args:
      - mods: orch.check_build
      - pillar: 
          post: {{ data['post']|yaml }}
{% endif %}

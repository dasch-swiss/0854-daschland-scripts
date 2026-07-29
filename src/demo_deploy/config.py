"""Static configuration for the demo-server recreation automation."""

# DSP demo server
DEMO_API_URL = "https://api.demo.dasch.swiss"
DEMO_APP_URL = "https://app.demo.dasch.swiss"

# The "Alice in DaSCHland" project
PROJECT_SHORTCODE = "0854"

# SystemAdmin account that authorizes the erase and create operations on demo
SYSADMIN_EMAIL = "dasch@dasch.swiss"

# Linear notification target: assign the reminder to Daniela on the RDU team
LINEAR_API_URL = "https://api.linear.app/graphql"
LINEAR_TEAM_ID = "6b896f48-b01f-4857-9116-6cb7c3aafb19"  # Research Data Unit
LINEAR_ASSIGNEE_ID = "e028ba9e-e1ad-4d02-9ee8-88d2190914f1"  # Daniela Subotic

# Portal link that has to be updated by hand after every re-upload (new URL each time)
REPOSITORY_PORTAL_URL = "https://repository.dasch.swiss/dpe/projects/0854"

# Timeout in seconds for every outgoing HTTP request
HTTP_TIMEOUT = 30

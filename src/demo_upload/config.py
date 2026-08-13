"""Static configuration for the demo-server re-upload automation."""

# DSP demo server
DEMO_API_URL = "https://api.demo.dasch.swiss"
DEMO_APP_URL = "https://app.demo.dasch.swiss"

# The "Alice in DaSCHland" project
PROJECT_SHORTCODE = "0854"

# SystemAdmin account that authorizes the erase and create operations on demo
SYSADMIN_EMAIL = "dasch@dasch.swiss"

# dsp-repository holds the metadata behind the portal page, including the link to the demo project
REPOSITORY_REPO = "dasch-swiss/dsp-repository"
# Last known location of the project metadata file; re-resolved by file name if it moved
REPOSITORY_PROJECT_FILE = "modules/dpe/server/data/projects/0854_daschland.json"

# Timeout in seconds for every outgoing HTTP request
HTTP_TIMEOUT = 30

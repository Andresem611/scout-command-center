#!/bin/bash
curl -s -X GET "https://api.agentmail.to/v1/inboxes" \
  -H "Authorization: Bearer am_us_inbox_8528a3c6c6e4462ea5b2f6c0d1ab85d" \
  -H "Accept: application/json"
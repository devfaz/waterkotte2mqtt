# Archived

I personally switched to https://github.com/pattisonmichael/waterkotte-integration, so I no longer develop this code.

# Example Deployment

```
---
apiVersion: apps/v1
kind: Deployment
metadata:
  name: waterkotte2mqtt
spec:
  replicas: 1
  selector:
    matchLabels:
      app: waterkotte2mqtt
  template:
    metadata:
      labels:
        app: waterkotte2mqtt
    spec:
      containers:
      - name: waterkotte2mqtt
        image: ghcr.io/devfaz/waterkotte2mqtt:latest
        envFrom:
        - secretRef:
          name: waterkotte2mqtt-secrets
```

# Example ENV / secret

```
WK_HOSTNAME=waterkotte
WK_USERNAME=waterkotte
WK_PASSWORD=waterkotte
MQTT_USERNAME=mqtt_user
MQTT_PASSWORD=mqtt_password
MQTT_HOST=mqtt.your-domain.de
```

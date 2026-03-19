# Notification and Automation Helm Chart

## Example installation:

```bash
helm upgrade --install notification-automation . \
  --namespace na \
  --set serving.install=false \
  --set eventing.install=false \
  --set eventing.authenticationOidc=false \
  --set webhookSource.enabled=true \
  --set webhookSource.secrets.create=true \
  --set webhookSource.secrets.githubSecret=123abc123 \
  --set webhookSource.sinkBinding.create=true \
  --set webhookSource.sinkBinding.sink.ref.namespace=default \
  --set webhookSource.sinkBinding.sink.ref.name=primary \
  --set webhookSource.ingress.enabled=true \
  --set webhookSource.ingress.className=apisix \
  --set 'webhookSource.ingress.hosts[0].host=git-webhook.develop.eoepca.org' \
  --set 'webhookSource.ingress.tls[0].secretName=webhook-na-tls' \
  --set 'webhookSource.ingress.tls[0].hosts[0]=git-webhook.develop.eoepca.org' \
  --set-string 'webhookSource.ingress.annotations.cert-manager\.io/cluster-issuer=letsencrypt-http01-apisix' \
  --set-string 'webhookSource.ingress.annotations.k8s\.apisix\.apache\.org/http-to-https=true' \
  --set-string 'webhookSource.ingress.annotations.k8s\.apisix\.apache\.org/upstream-read-timeout=600s' \
  --set cloudEventsPlayer.enabled=true \
  --set cloudEventsPlayer.subscribeBroker.enabled=true \
  --set emailer.install=true \
  --set emailer.config.emailFrom=noreply@example.com \
  --set emailer.config.emailTo=team@example.com \
  --set emailer.config.yagmailHost=smtp.example.com \
  --set emailer.config.yagmailPort=587 \
  --set emailer.config.yagmailUser=noreply@example.com \
  --set emailer.config.yagmailPassword=changeme \
  --set emailer.config.yagmailSmtpStarttls=true
```
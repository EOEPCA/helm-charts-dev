{{/*
Expand the name of the chart.
*/}}
{{- define "application-hub.name" -}}
{{- default .Chart.Name .Values.nameOverride | trunc 63 | trimSuffix "-" }}
{{- end }}

{{/*
Create a default fully qualified app name.
This version does NOT include the release name.
*/}}
{{- define "application-hub.fullname" -}}
{{- if .Values.jupyterhub.fullnameOverride }}
{{- .Values.jupyterhub.fullnameOverride | trunc 63 | trimSuffix "-" }}
{{- else }}
{{- default .Chart.Name .Values.nameOverride | trunc 63 | trimSuffix "-" }}
{{- end }}
{{- end }}


{{/*
Create chart name and version as used by the chart label.
*/}}
{{- define "application-hub.chart" -}}
{{- printf "%s-%s" .Chart.Name .Chart.Version | replace "+" "_" | trunc 63 | trimSuffix "-" }}
{{- end }}

{{/*
Common labels
*/}}
{{- define "application-hub.labels" -}}
helm.sh/chart: {{ include "application-hub.chart" . }}
{{ include "application-hub.selectorLabels" . }}
{{- if .Chart.AppVersion }}
app.kubernetes.io/version: {{ .Chart.AppVersion | quote }}
{{- end }}
app.kubernetes.io/managed-by: {{ .Release.Service }}
{{- end }}

{{/*
Selector labels
*/}}
{{- define "application-hub.selectorLabels" -}}
app.kubernetes.io/name: {{ include "ades.name" . }}
app.kubernetes.io/instance: {{ .Release.Name }}
{{- end }}

{{/*
Create the name of the service account to use
*/}}
{{- define "application-hub.serviceAccountName" -}}
{{- if .Values.serviceAccount.create }}
{{- default (printf "jupyterhub-%s-hub" (include "application-hub.name" .)) .Values.serviceAccount.name }}
{{- else }}
{{- default "default" .Values.serviceAccount.name }}
{{- end }}
{{- end }}
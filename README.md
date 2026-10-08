# Kubernetes Beginners 02 Demo

這是「Kubernetes 入門（二）」課程使用的 Demo 專案。

本專案以一個簡單的 Web Application，逐步展示 Kubernetes 常見資源與功能，包括：

- ConfigMap
- Secret
- PersistentVolumeClaim（PVC）
- PersistentVolume（PV）
- StorageClass
- Service
- Ingress
- Traefik
- TLS
- cert-manager
- ACME / Let's Encrypt
- CRD / Controller
- Helm

課程重點不在 Application 開發，而是觀察同一個 Application 如何透過 Kubernetes 完成設定管理、持久化儲存、對外服務與 TLS 憑證自動化。

---

## Architecture

```text
Internet
   │
   ▼
OCI Load Balancer
   │
   ▼
Traefik
   │
   ▼
Ingress
   │
   ▼
Frontend Service
   │
   ▼
Frontend (nginx)
   │
   ├── Static HTML / JavaScript
   │
   └── /api/
         │
         ▼
     Backend Service
         │
         ▼
     Backend (FastAPI)
         │
         ▼
        PVC
         │
         ▼
        PV
         │
         ▼
   OCI Block Volume
```

TLS 憑證則由 cert-manager 管理：

```text
Certificate
     │
     ▼
cert-manager Controller
     │
     ▼
ACME / Let's Encrypt
     │
     ▼
TLS Secret
     │
     ▼
Traefik
```

---

## Project Structure

```text
.
├── backend/
│   ├── main.py
│   ├── requirements.txt
│   └── Dockerfile
│
├── frontend/
│   ├── index.html
│   ├── app.js
│   ├── default.conf
│   └── Dockerfile
│
└── k8s/
    ├── configmap.yaml
    ├── secret.yaml
    ├── pvc.yaml
    ├── backend.yaml
    ├── frontend.yaml
    ├── ingress.yaml
    ├── certificate.yaml
    └── ingress-tls.yaml
```

---

## Container Images

課程使用的 Container Images：

```text
docker.io/bhchoudev/k8s-beginners-02-backend:v1
docker.io/bhchoudev/k8s-beginners-02-frontend:v2
```

Images 支援：

```text
linux/amd64
linux/arm64
```

可以使用以下指令查看 Multi-Architecture Image：

```bash
docker buildx imagetools inspect \
  docker.io/bhchoudev/k8s-beginners-02-backend:v1
```

---

## Kubernetes Namespace

Demo 使用：

```text
k8s-demo
```

如果 Namespace 尚未建立：

```bash
kubectl create namespace k8s-demo
```

---

## ConfigMap

ConfigMap 用來保存非敏感的 Application 設定。

例如：

```yaml
data:
  ENV_NAME: "OKE-DEMO"
```

Backend 會讀取這個設定，並顯示在 Demo UI。

---

## Secret

Secret 用來示範敏感設定如何提供給 Pod。

本 Repository 中的 Secret **僅為課程示範用假資料**：

```text
DEMO-ONLY-NOT-A-REAL-SECRET
```

> ⚠️ 請勿將真實 Password、API Key、Token、Private Key 或其他 Credential commit 到 Git Repository。

Kubernetes Secret 中常見的 Base64 是 **Encoding，不是 Encryption**。

---

## Persistent Storage

Demo 使用 PersistentVolumeClaim：

```text
Backend Pod
    │
    ▼
   PVC
    │
    ▼
    PV
    │
    ▼
OCI Block Volume
```

課程 Demo：

1. 從 Web UI 寫入資料
2. 記下目前 Backend Pod
3. 刪除 Backend Pod
4. Deployment 建立新的 Pod
5. 再次讀取資料

即使 Pod 已經被刪除，資料仍然存在。

> Deployment 讓應用程式回來；PVC 讓資料留下來。

---

## HTTP Ingress

`k8s/ingress.yaml` 為 HTTP 版本。

```bash
kubectl apply -f k8s/ingress.yaml
```

流量路徑：

```text
HTTP
 │
 ▼
OCI Load Balancer
 │
 ▼
Traefik
 │
 ▼
Ingress
 │
 ▼
Frontend
```

---

## TLS Certificate

本 Demo 使用：

- cert-manager
- ACME
- Let's Encrypt

Certificate Resource 定義希望取得的 TLS Certificate：

```text
Certificate
     │
     ▼
cert-manager
     │
     ▼
Let's Encrypt
     │
     ▼
TLS Secret
```

cert-manager 會持續 Reconcile Certificate 狀態，並在需要時自動進行憑證 Renewal。

---

## HTTPS Ingress

`k8s/ingress-tls.yaml` 在 HTTP Ingress 基礎上增加：

```yaml
tls:
  - hosts:
      - k8s-demo.blackjackzone.me
    secretName: k8s-demo-tls
```

套用：

```bash
kubectl apply -f k8s/ingress-tls.yaml
```

Traefik 會使用 TLS Secret 中的 Certificate 與 Private Key 提供 HTTPS。

---

## CRD & Controller

cert-manager 也是 CRD + Controller 的實際案例。

安裝 cert-manager 後，Kubernetes 會增加例如：

```text
Certificate
CertificateRequest
Order
Challenge
```

等新的 Resource Type。

可以查看：

```bash
kubectl get crd | grep cert-manager
```

概念上：

```text
CRD
 │
 └── 定義新的 Resource Type
          │
          ▼
    Custom Resource
          │
          ▼
      Controller
          │
          ▼
    Reconciliation
```

這仍然遵循 Kubernetes 的 Desired State / Reconciliation 模型。

---

## Helm

Helm 用來 Package、安裝與管理一組 Kubernetes Resources。

查看 Cluster 中的 Helm Releases：

```bash
helm list -A
```

基本概念：

```text
Chart
  │
  ├── Templates
  └── values.yaml
        │
        ▼
     helm install
        │
        ▼
      Release
        │
        ├── Deployment
        ├── Service
        ├── ConfigMap
        ├── RBAC
        └── ...
```

Helm 並不是另一個 Container Runtime 或 Kubernetes 替代品，而是 Kubernetes Application 的 Package Manager。

---

## Cleanup

如果要移除整個 Demo：

```bash
kubectl delete namespace k8s-demo
```

如果使用 Dynamic Provisioning，刪除 PVC 後是否連帶刪除實際 Storage，取決於 PV 的 Reclaim Policy。

執行 Cleanup 前，請先確認 Cluster 中沒有其他需要保留的 Resource。

---

## Security Notice

這是一個教學用途的 Demo Repository。

請勿將以下內容加入公開 Repository：

- 真實 API Key
- Password
- Access Token
- SSH Private Key
- TLS Private Key
- Cloud Credential
- kubeconfig
- `.env` 中的真實 Credential

本專案中的 Secret 值應全部視為 Demo Data，不應直接用於 Production。

---

## Disclaimer

本專案主要用於 Kubernetes 教學與技術示範。

範例設定以容易理解 Kubernetes 核心概念為優先，不代表完整的 Production Best Practice。

---

## License

本專案中的程式碼、Dockerfile 與 Kubernetes YAML 採用
[MIT License](LICENSE) 授權。

課程投影片、HackMD 與其他教學內容不包含在本 Repository 的 MIT License 授權範圍內。
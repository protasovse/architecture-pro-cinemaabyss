kind create cluster --name ca-arch --config ./src/kubernetes/kind/config.yaml

# Поставь ingress-nginx (манифест для kind)
kubectl apply -f https://raw.githubusercontent.com/kubernetes/ingress-nginx/main/deploy/static/provider/kind/deploy.yaml

# Ждём, пока контроллер поднимется
kubectl -n ingress-nginx rollout status deploy/ingress-nginx-controller

helm install cinemaabyss ./src/kubernetes/helm --namespace cinemaabyss --create-namespace

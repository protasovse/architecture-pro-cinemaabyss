kind delete cluster --name ca-arch || true
kind create cluster --name ca-arch --config ./src/kubernetes/kind/config.yaml

# Создайте namespace
kubectl apply -f src/kubernetes/namespace.yaml

# Создайте секреты и переменные
kubectl apply -f src/kubernetes/configmap.yaml
kubectl apply -f src/kubernetes/secret.yaml
kubectl apply -f src/kubernetes/dockerconfigsecret.yaml
kubectl apply -f src/kubernetes/postgres-init-configmap.yaml

# Разверните базу данных
kubectl apply -f src/kubernetes/postgres.yaml

kubectl -n cinemaabyss get pod

# Разверните Kafka
kubectl apply -f src/kubernetes/kafka/kafka.yaml

# Разверните монолит
kubectl apply -f src/kubernetes/monolith.yaml

# Разверните микросервисы
kubectl apply -f src/kubernetes/movies-service.yaml
kubectl apply -f src/kubernetes/events-service.yaml

# Разверните прокси-сервис
kubectl apply -f src/kubernetes/proxy-service.yaml

# Поставь ingress-nginx (манифест для kind)
kubectl apply -f https://raw.githubusercontent.com/kubernetes/ingress-nginx/main/deploy/static/provider/kind/deploy.yaml

# Ждём, пока контроллер поднимется
kubectl -n ingress-nginx rollout status deploy/ingress-nginx-controller
# ждём, пока появятся эндпоинты вебхука (а не просто Job'ы)
echo "⏳ Ждём admission endpoints..."
for i in {1..30}; do
  EP=$(kubectl -n ingress-nginx get endpoints ingress-nginx-controller-admission \
        -o jsonpath='{.subsets[0].addresses[0].ip}' 2>/dev/null || true)
  [ -n "$EP" ] && echo "✅ admission endpoints: $EP" && break
  sleep 2
done

# применяем ingress с ретраем
for i in {1..5}; do
  kubectl apply -f src/kubernetes/ingress.yaml && break
  echo "retry apply ingress ($i/5)..." && sleep 3
done

# Применяем ingress
kubectl apply -f src/kubernetes/ingress.yaml

# Проверка (порт теперь 8000!)
curl -H "Host: cinemaabyss.example.com" http://127.0.0.1/


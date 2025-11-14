set -euo pipefail

NAMESPACE="cinemaabyss"
IMAGE_PREFIX="ghcr.io/protasovse/architecture-pro-cinemaabyss/"
WAIT_TIMEOUT="180s"

echo "🚀 Обновляем образы с префиксом: $IMAGE_PREFIX в namespace: $NAMESPACE"

# Проверка зависимостей
command -v kubectl >/dev/null 2>&1 || { echo "❌ kubectl не найден"; exit 1; }
command -v jq >/dev/null 2>&1 || { echo "❌ jq не найден (установи через sudo apt install jq)"; exit 1; }

KINDS=("deployments" "statefulsets" "daemonsets")

UPDATED=()

for kind in "${KINDS[@]}"; do
  mapfile -t names < <(kubectl get "$kind" -n "$NAMESPACE" --no-headers 2>/dev/null | awk '{print $1}' || true)
  [[ ${#names[@]} -eq 0 ]] && continue

  for name in "${names[@]}"; do
    images=$(
      kubectl get "$kind" "$name" -n "$NAMESPACE" -o json \
      | jq -r '[.spec.template.spec.containers[]?.image, .spec.template.spec.initContainers[]?.image] | .[]'
    )
    match=false
    while IFS= read -r img; do
      [[ "$img" == "$IMAGE_PREFIX"* ]] && match=true && break
    done <<< "$images"

    if [[ "$match" == true ]]; then
      echo "🔄 Перезапускаю $kind/$name..."
      kubectl rollout restart "$kind/$name" -n "$NAMESPACE" || true
      UPDATED+=("$kind/$name")
    fi
  done
done

for ref in "${UPDATED[@]}"; do
  echo "⏳ Жду rollout $ref..."
  if kubectl rollout status "$ref" -n "$NAMESPACE" --timeout="$WAIT_TIMEOUT"; then
    echo "✅ Обновлено: $ref"
  else
    echo "⚠️ Не дождался успешного rollout: $ref"
  fi
done

echo "🎉 Готово! Обновлено ворклоадов: ${#UPDATED[@]}"

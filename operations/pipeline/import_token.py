from kubernetes import client, config

# Загрузка конфигурации Kubernetes
config.load_kube_config()

# Создание экземпляра клиента API
api_client = client.ApiClient()

# Имя namespace, где находятся Pods
namespace = "oss-rm-adp"

# Поиск первого подходящего имени Pod
api_instance = client.CoreV1Api(api_client)
pod_list = api_instance.list_namespaced_pod(namespace=namespace).items

for pod in pod_list:
    # Проверка условия для выбора подходящего Pod
    if "oss-rm-vsosad" in pod.metadata.name:
        pod_name = pod.metadata.name
        break

# Путь к файлу внутри Pod
file_path = "/var/run/secrets/kubernetes.io/serviceaccount/token"

# Получение содержимого файла из Pod
response = api_instance.read_namespaced_pod_exec(
    name=pod_name,
    namespace=namespace,
    command=["cat", file_path],
    stderr=False,
    stdin=False,
    stdout=True,
    tty=False,
)

# Сохранение содержимого файла в локальный файл
with open("downloaded_file.txt", "w") as file:
    file.write(response)

print("Файл успешно сохранен.")
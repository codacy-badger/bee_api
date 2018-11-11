minikube start
eval $(minikube docker-env)

docker build -t "bee-api:production1"
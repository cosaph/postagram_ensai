deploy_serverless:
	cd terraform && cdktf deploy -a "pipenv run python3 main_serverless.py"

update_server:
	@echo "Copier ici le nom du bucket S3 créé par le déploiement du serveurless."
	@read -r bucket; \
	sed -i 's/BUCKET_NAME_PLACEHOLDER/'"$$bucket"'/g' terraform/main_server.py
	cd terraform && cdktf deploy -a "pipenv run python3 main_server.py"

update_webapp:
	@echo "Copier ici le nom de domaine du load balancer créé par le déploiement du serveur."
	
	@read -r lb_dns_name; \
	sed -i 's/LB_DNS_NAME_PLACEHOLDER/'"$$lb_dns_name"'/g' webapp/src/index.js
	
install_webapp:
	cd webapp && npm install

start_webapp:
	cd webapp && npm start

deploy: deploy_serverless update_server update_webapp install_webapp start_webapp


close_app:
	cd terraform && cdktf destroy -a "pipenv run python3 main_server.py"
	cd terraform && cdktf destroy -a "pipenv run python3 main_serverless.py"

change :
	sed -i "s/^bucket = .*$$/bucket = \"BUCKET_NAME_PLACEHOLDER\"/g" terraform/main_server.py
	sed -i "s/^axios.defaults.baseURL = .*$$/axios.defaults.baseURL = \"http:\/\/LB_DNS_NAME_PLACEHOLDER:8080\/\"/g" webapp/src/index.js

all: deploy


clean: close_app change
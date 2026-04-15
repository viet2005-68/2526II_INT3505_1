# API Blueprint

## Run

npm install -g aglio

## View 
aglio -i api.apib -s

## Convert to openai

npm install -g api-spec-converter

api-spec-converter --from=api_blueprint --to=openapi_3 api.apib > openapi.yaml

## View openapi.yaml
npx swagger-ui-watcher openapi.yaml


## Gen app with openai.yaml
npx openapi-generator-cli generate -i openapi.yaml -g python-flask -o ./flask-server

cd flask-server

python3 -m openapi_server
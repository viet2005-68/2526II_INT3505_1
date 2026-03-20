# TypeSpec

TypeSpec là ngôn ngữ của Microsoft để định nghĩa API schema, có thể compile ra OpenAPI, JSON Schema, Protobuf...

## Run

```bash
npm install
npx tsp compile main.tsp --emit @typespec/openapi3
npx swagger-ui-watcher tsp-output/@typespec/openapi3/openapi.yaml
```

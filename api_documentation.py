import ast
import os
import json

class APIDocumentationGenerator:
    def __init__(self, project_path):
        self.project_path = project_path
        self.routes = []

    # Step 1: Analyze backend code
    def analyze_code(self):
        for root, dirs, files in os.walk(self.project_path):
            for file in files:
                if file.endswith(".py"):
                    filepath = os.path.join(root, file)
                    self.extract_routes(filepath)

    # Step 2: Extract API routes
    def extract_routes(self, filepath):
        with open(filepath, "r") as f:
            tree = ast.parse(f.read())

        for node in ast.walk(tree):
            if isinstance(node, ast.FunctionDef):
                for decorator in node.decorator_list:
                    if isinstance(decorator, ast.Call):
                        if hasattr(decorator.func, 'attr') and decorator.func.attr == "route":
                            route_path = decorator.args[0].s
                            methods = ["GET"]

                            for keyword in decorator.keywords:
                                if keyword.arg == "methods":
                                    methods = [m.s for m in keyword.value.elts]

                            self.routes.append({
                                "endpoint": route_path,
                                "methods": methods,
                                "function": node.name
                            })

    # Step 3: Generate API documentation
    def generate_docs(self):
        docs = []
        for route in self.routes:
            doc = {
                "Endpoint": route["endpoint"],
                "Methods": route["methods"],
                "Description": f"Auto generated documentation for {route['function']}"
            }
            docs.append(doc)

        return docs

    # Step 4: Generate OpenAPI JSON
    def generate_openapi(self):
        openapi = {"paths": {}}

        for route in self.routes:
            openapi["paths"][route["endpoint"]] = {}

            for method in route["methods"]:
                openapi["paths"][route["endpoint"]][method.lower()] = {
                    "summary": f"{route['function']} endpoint",
                    "responses": {
                        "200": {
                            "description": "Successful response"
                        }
                    }
                }

        return openapi

    # Step 5: Generate Python SDK
    def generate_python_sdk(self):
        sdk = "import requests\n\n"

        for route in self.routes:
            func_name = route["function"]
            endpoint = route["endpoint"]

            sdk += f"""
def {func_name}():
    url = "http://localhost:5000{endpoint}"
    response = requests.get(url)
    return response.json()
"""

        return sdk


# Main Execution
if __name__ == "__main__":
    project_path = "./backend_project"

    generator = APIDocumentationGenerator(project_path)

    generator.analyze_code()

    docs = generator.generate_docs()
    openapi = generator.generate_openapi()
    sdk = generator.generate_python_sdk()

    print("API Documentation:")
    print(json.dumps(docs, indent=4))

    print("\nOpenAPI Specification:")
    print(json.dumps(openapi, indent=4))

    print("\nGenerated Python SDK:")
    print(sdk)
from fastapi.responses import HTMLResponse

def scalar_docs():
    return HTMLResponse("""
<!DOCTYPE html>
<html>
  <head>
    <title>API Docs</title>
  </head>
  <body>
    <script
      id="api-reference"
      data-url="/openapi.json"
      src="https://cdn.jsdelivr.net/npm/@scalar/api-reference">
    </script>
  </body>
</html>
""")

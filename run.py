import os
import sys
import uvicorn

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 8000))
    host = "0.0.0.0"
    print(f"Starting QualityScaler AI (Mezzold Studio) on http://{host}:{port}")
    uvicorn.run("app:app", host=host, port=port, reload=False)
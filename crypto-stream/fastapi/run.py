import uvicorn

import app.core.init_env  # noqa: F401

if __name__ == "__main__":
    uvicorn.run("app.main:app", host="0.0.0.0", port=5888, reload=True)

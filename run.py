import sys
import os

import uvicorn

sys.path.append(os.path.dirname(os.path.abspath(__file__)))

if __name__ == '__main__':
    uvicorn.run("app.main:app", host="0.0.0.0", port=6262, log_level="debug")

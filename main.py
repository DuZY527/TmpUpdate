import uvicorn

# noinspection PyUnresolvedReferences
from route.root import app

# noinspection PyUnresolvedReferences
from route.api_load import *
# noinspection PyUnresolvedReferences
from route.api_tool import *

# noinspection PyUnresolvedReferences
from route.api_optimization import *


if __name__ == "__main__":
    uvicorn.run(app='main:app', host='0.0.0.0', port=8000, reload=True)

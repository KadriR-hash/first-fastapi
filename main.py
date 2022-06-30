from enum import Enum
from fastapi import FastAPI, Query, Path, Body
# FastAPI is a Python class that provides all the functionality for your API.
from pydantic import BaseModel, Field  # declare validation and metadata inside of Pydantic models using Pydantic's

app = FastAPI()  # This will be the main point of interaction to create all your API.


# Import Enum and create a subclass that inherits from str and from Enum.
class ModelName(str, Enum):
    alexnet = "alexnet"
    resnet = "resnet"
    lenet = "lenet"


class Image(BaseModel):
    url: str
    name: str


# declare the  data model as a class that inherits from BaseModel
class Item(BaseModel):
    name: str
    description: str | None = Field(default=None,
                                    title="The description of the item",
                                    max_length=300)
    price: float = Field(gt=0,
                         description="The price must be greater than zero")
    tax: float | None = None
    tags: list[str] = []
    image: Image | None = None


class User(BaseModel):
    username: str
    full_name: str | None = None


# command to launch: uvicorn main:app --reload.
# Uvicorn running on ←[1mhttp://127.0.0.1:8000←.
# FastAPI generates a "schema" with all your API using the OpenAPI standard for defining APIs.

# PATH params
@app.get("/items/{item_id}")
async def read_item(item_id: int, q: str | None = None, short: bool = False):  # we can declare intem_id type.
    # So, with that type declaration, FastAPI gives you automatic request "parsing" + "data validation".
    # All the data validation is performed under the hood by Pydantic.

    item = {"item_id": item_id}
    if q:
        item.update({"q": q})  # q is an optional query  param
    if not short:
        item.update({"description": "This is an amazing item that has a long description"})
    return item


# Trying class of enum type in python
@app.get("/models/{model_name}")
async def get_model(model_name: ModelName):
    # there is two ways of comparing enum values !
    if model_name == ModelName.alexnet:
        return {"model_name": model_name, "message": "Deep Learning FTW!"}

    if model_name.value == "lenet":
        return {"model_name": model_name, "message": "LeCNN all the images"}

    return {"model_name": model_name, "message": "Have some residuals"}


# exemple : /files//home/johndoe/myfile.txt, with a double slash (//) between files and home
@app.get("/files/{file_path:path}")
async def read_file(file_path: str):
    return {"file_path": file_path}


# Query params
@app.get("/items")
async def read_item(needy: str, skip: int = 0, limit: int | None = None):  # needy:required|skip:default|limit:optional
    return {"skip": skip, "limit": limit, "needy": needy}


# Multiple path and query parameters
@app.get("/users/{user_id}/items/{item_id}")
async def read_user_item(user_id: int, item_id: str, q: str | None = None, short: bool = False):
    item = {"item_id": item_id, "owner_id": user_id}
    if q:
        item.update({"q": q})
    if not short:
        item.update({"description": "This is an amazing item that has a long description"})
    return item


# Request Body
# To declare a request body, you use Pydantic models with all their power and benefits.
@app.post("/items/{item_id}")
async def create_item(*,  # a little trick so we don't need to order the params
                      item_id: int = Path(title="the id of the item",
                                          gt=1,
                                          le=1000),  # metadata  & Number validator with path params
                      item: Item,
                      q: list[str] | None = Query(default=None,
                                                  title="Query",
                                                  max_length=50,
                                                  description="here we test string validators",
                                                  alias="_Query")):  # metadata  & String validator with Query params
    # If the parameter is declared to be of the type of a Pydantic model, it will be interpreted as a request body.
    item_dict = item.dict()
    if q:
        item_dict.update({"q": q})
    if item.tax:
        price_with_tax = item.price + item.tax
        item_dict.update({"item_id": item_id, "price_with_tax": price_with_tax})
    return item_dict


@app.put("/items/{item_id}")
async def update_item(*,
                      item_id: int = Path(title="The ID of the item to get", ge=0, le=1000),
                      q: str | None = None,
                      item: Item | None = None,
                      importance: int = Body(),  # want to have another key importance in the same body
                      user: User):
    # First,of course,you can mix Path, Query and request body parameter declarations freely
    # and FastAPI will know what to do.
    results = {"item_id": item_id}
    if q:
        results.update({"q": q})
    if item:
        results.update({"item": item})
    if user:
        results.update({"user": user})
    if importance:
        results.update({"importance": importance})
    return results

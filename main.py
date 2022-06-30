from enum import Enum
from fastapi import FastAPI, Query, Path, Body
# FastAPI is a Python class that provides all the functionality for your API.
from pydantic import BaseModel, Field, HttpUrl  # pydantic -> flexibility
from datetime import datetime, time, timedelta
from uuid import UUID

# declare validation and metadata inside of Pydantic models using Pydantic's

app = FastAPI()  # This will be the main point of interaction to create all your API.


# Import Enum and create a subclass that inherits from str and from Enum.
class ModelName(str, Enum):
    alexnet = "alexnet"
    resnet = "resnet"
    lenet = "lenet"


# You can declare an example for a Pydantic model using Config and schema_extra
# You could use the same technique to extend the JSON Schema and add your own custom extra info
class Config:
    schema_extra = {
        "example": {
            "name": "Foo",
            "description": "A very nice Item",
            "price": 35.4,
            "tax": 3.2,
        }
    }


class Image(BaseModel):
    url: HttpUrl
    name: str


# declare the  data model as a class that inherits from BaseModel
class Item(BaseModel):
    name: str = Field(example="Foo")  # hose extra arguments passed won't add any validation, only extra information,
    # for documentation purposes.
    description: str | None = Field(default=None,
                                    example=" A very nice Item",
                                    title="The description of the item",
                                    max_length=300)
    price: float = Field(gt=0,
                         example=35.4,
                         description="The price must be greater than zero")
    tax: float | None = Field(example=3.2)
    tags: list[str] = []
    image: list[Image] | None = None


class User(BaseModel):
    username: str
    full_name: str | None = None


class Offer(BaseModel):
    name: str
    description: str | None = None
    price: float
    items: list[Item]


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
async def create_item(*,  # a little trick, so we don't need to order the params
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
                      importance: int = Body(examples={
                          "normal": {
                              "summary": "A normal example",
                              "description": "A **normal** item works correctly.",
                              "value": {
                                  "name": "Foo",
                                  "description": "A very nice Item",
                                  "price": 35.4,
                                  "tax": 3.2,
                              },
                          },
                          "converted": {
                              "summary": "An example with converted data",
                              "description": "FastAPI can convert price `strings` to actual `numbers` automatically",
                              "value": {
                                  "name": "Bar",
                                  "price": "35.4",
                              },
                          },
                          "invalid": {
                              "summary": "Invalid data is rejected with an error",
                              "value": {
                                  "name": "Baz",
                                  "price": "thirty five point four",
                              },
                          },
                      }),  # want to have another key importance in the same body
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


@app.post("/offers/")
async def create_offer(offer: Offer):
    return offer


@app.post("/images/multiple/")
async def create_multiple_images(images: list[Image]):  # body of lists
    return images


@app.post("/index-weights/")
async def create_index_weights(weights: dict[int, float]):  # body of dict
    # Have in mind that JSON only supports str as keys,
    # But Pydantic has automatic data conversion & validation.
    return weights


@app.put("/items-v2/{item_id}")
async def read_items(
        item_id: UUID,
        start_datetime: datetime | None = Body(default=None),
        end_datetime: datetime | None = Body(default=None),
        repeat_at: time | None = Body(default=None),
        process_after: timedelta | None = Body(default=None),
):
    start_process = start_datetime + process_after
    duration = end_datetime - start_process
    return {
        "item_id": item_id,
        "start_datetime": start_datetime,
        "end_datetime": end_datetime,
        "repeat_at": repeat_at,
        "process_after": process_after,
        "start_process": start_process,
        "duration": duration,
    }


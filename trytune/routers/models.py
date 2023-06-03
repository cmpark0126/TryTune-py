import httpx
from fastapi import APIRouter, HTTPException
from typing import Any
from trytune.schemas import common, model


# Class to store model metadatas and links to triton servers.
class ModelRegistry:
    models = {}

    def add(model_name, model_info):
        ModelRegistry.models[model_name] = model_info

    def get_metadata(model_name):
        return ModelRegistry.models[model_name]


router = APIRouter()


@router.get("/models/{model}/metadata")
async def get_metadata(model: str):
    try:
        return ModelRegistry.get_metadata(model)
    except KeyError:
        raise HTTPException(status_code=404, detail=f"Model {model} not found.")


async def get_metadata_from_url(model: str, url: str) -> Any:
    async with httpx.AsyncClient() as client:
        tgt_url = url + f"/v2/models/{model}"
        response = await client.get(tgt_url)

        if response.status_code != 200:
            raise HTTPException(
                status_code=400,
                detail=f"Error: {response.text} from {url} with {tgt_url}",
            )
        metadata = response.json()
        return metadata


@router.post("/models/{model}/add")
async def add_model(model: str, schema: model.ModelAddSchema):
    if model in ModelRegistry.models:
        raise HTTPException(status_code=400, detail=f"Model {model} already exists.")

    # Send the request to the triton server to get model metadata
    if len(schema.urls) == 0:
        raise HTTPException(status_code=400, detail="No links provided.")

    # Request to triton server to get model metadata
    urls = [url for _instance_type, url in schema.urls.items()]
    metadata = await get_metadata_from_url(model, urls[0])

    for url in urls[1:]:
        other = await get_metadata_from_url(model, url)
        if metadata != other:
            raise HTTPException(
                status_code=400,
                detail=f"Model metadata mismatch: {urls[0]}'s {metadata}, {url}'s {other}",
            )

    # add model to model registry
    ModelRegistry.add(model, {"urls": schema.urls, "metadata": metadata})

    # Return the response with the stored information
    return metadata


@router.post("/models/{model}/infer")
async def infer(model: str, infer: common.InferSchema):
    # TODO: send the request to scheduler services

    return infer

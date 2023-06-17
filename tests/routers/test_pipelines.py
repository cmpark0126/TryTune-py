def test_pipelines_scenario_scenario(client) -> None:  # type: ignore
    detection_module = "detection_module"
    add_module_schema = {
        "name": detection_module,
        "type": "builtin",
        "builtin_args": {"target": "FasterRCNN_ResNet50_FPN"},
    }

    response = client.post("/modules/add", json=add_module_schema)
    assert response.status_code == 200, response.content
    detection_module_metadata = response.json()
    print(detection_module_metadata)

    crop_module = "crop_module"
    add_module_schema = {
        "name": crop_module,
        "type": "builtin",
        "builtin_args": {
            "target": "Crop",
            "threshold": 0.9,
            "label": 1,  # label 1 is person
        },
    }

    response = client.post("/modules/add", json=add_module_schema)
    assert response.status_code == 200, response.content
    crop_module_metadata = response.json()
    print(crop_module_metadata)

    pipeline = "test_pipeline"
    add_pipeline_schema = {
        "name": pipeline,
        "tensors": {
            "inputs": [{"name": "p_image"}],
            "outputs": [{"name": "p_cropped_images"}, {"name": "p_whs"}],
        },
        "stages": [
            {
                "name": "detector",
                "module": "detection_module",
                "inputs": {"BATCH_IMAGE": "p_image"},
                "outputs": {
                    "BOXES": "p_boxes",
                    "LABELS": "p_labels",
                    "SCORES": "p_scores",
                },
            },
            {
                "name": "cropper",
                "module": "crop_module",
                "inputs": {
                    "IMAGE": "p_image",
                    "BOXES": "p_boxes",
                    "LABELS": "p_labels",
                    "SCORES": "p_scores",
                },
                "outputs": {"CROPPED_IMAGES": "p_cropped_images", "WHS": "p_whs"},
            },
        ],
    }

    response = client.post("/pipelines/add", json=add_pipeline_schema)
    assert response.status_code == 200, response.content
    # pipeline_metadata = response.json()

    raise NotImplementedError


# TODO: add more scenarios for testing (e.g., classification, object detection, etc.)
# For testing on k8s
def test_pipelines_scenario_scenario_on_k8s(client, add_module_schemas, add_pipeline_schema) -> None:  # type: ignore
    pass

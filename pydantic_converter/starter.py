import asyncio
import logging
from datetime import datetime
from ipaddress import IPv4Address

from temporalio.client import Client
from temporalio.contrib.pydantic import pydantic_data_converter

from pydantic_converter.worker import MyPydanticModel, MyWorkflow
from pydantic import SecretStr


async def main():
    logging.basicConfig(level=logging.INFO)
    # Connect client using the Pydantic converter
    client = await Client.connect(
        "localhost:7233", data_converter=pydantic_data_converter
    )

    # Run workflow
    models = [
        MyPydanticModel(
            some_ip=IPv4Address("127.0.0.1"),
            some_date=datetime(2000, 1, 2, 3, 4, 5),
            some_secret=SecretStr("super secret"),
        ),
        MyPydanticModel(
            some_ip=IPv4Address("127.0.0.2"),
            some_date=datetime(2001, 2, 3, 4, 5, 6),
            some_secret=SecretStr("shh don't tell"),
        ),
    ]
    logging.info("models secret: %s" % models[0].some_secret.get_secret_value())
    result = await client.execute_workflow(
        MyWorkflow.run,
        models,
        id="pydantic_converter-workflow-id",
        task_queue="pydantic_converter-task-queue",
    )
    logging.info("Got models from client: %s" % result)
    logging.info("Got secret from client: %s" % result[0].some_secret.get_secret_value())


if __name__ == "__main__":
    asyncio.run(main())

import asyncio
import logging
import threading
from functools import partial
from typing import Dict, List, Optional

import requests

from langchain.pydantic_v1 import BaseModel, root_validator
from langchain.schema.embeddings import Embeddings
from langchain.utils import get_from_dict_or_env
import erniebot
import numpy as np
import time
import os

## 注意不要用翻墙
## https://python.langchain.com/docs/integrations/chat/ernie

logger = logging.getLogger(__name__)


class ErnieEmbeddings(BaseModel, Embeddings):
    """`Ernie Embeddings V1` embedding models."""

    ernie_api_base: Optional[str] = None
    ernie_client_id: Optional[str] = None
    ernie_client_secret: Optional[str] = None
    access_token: Optional[str] = None  # erniebot.access_token = '<access-token-for-aistudio>'

    chunk_size: int = 16

    model_name = "ErnieBot-Embedding-V1"

    _lock = threading.Lock()
    '''
    kevin modify:
    '''

    @root_validator()
    def validate_environment(cls, values: Dict) -> Dict:
        # values["ernie_api_base"] = get_from_dict_or_env(
        #     values, "ernie_api_base", "ERNIE_API_BASE", "https://aip.baidubce.com"
        # )
        values["access_token"] = get_from_dict_or_env(
            values,
            "access_token",
            "ACCESS_TOKEN",
        )
        values["api_type"] = 'aistudio'

        erniebot.api_type = values["api_type"]
        erniebot.access_token = values["access_token"]
        return values

    # def _embedding(self, json: object) -> dict:
    # base_url = (
    #     f"{self.ernie_api_base}/rpc/2.0/ai_custom/v1/wenxinworkshop/embeddings"
    # )
    # resp = requests.post(
    #     f"{base_url}/embedding-v1",
    #     headers={
    #         "Content-Type": "application/json",
    #     },
    #     params={"access_token": self.access_token},
    #     json=json,
    # )
    # return resp.json()
    '''
    kevin modify:
    '''

    def _embedding(self, json: object) -> dict:
        inputs = json['input']

        def erniebotSDK(inputs):
            response = erniebot.Embedding.create(
                model='ernie-text-embedding',
                input=inputs)
            time.sleep(1)
            return response

        try:
            response = erniebotSDK(inputs)
        except:
            print('connect erniebot error...wait 2s to retry(kevin)')
            time.sleep(2)
            response = erniebotSDK(inputs)
        return response

    def _refresh_access_token_with_lock(self) -> None:
        with self._lock:
            logger.debug("Refreshing access token")
            base_url: str = f"{self.ernie_api_base}/oauth/2.0/token"
            resp = requests.post(
                base_url,
                headers={
                    "Content-Type": "application/json",
                    "Accept": "application/json",
                },
                params={
                    "grant_type": "client_credentials",
                    "client_id": self.ernie_client_id,
                    "client_secret": self.ernie_client_secret,
                },
            )
            self.access_token = str(resp.json().get("access_token"))

    def embed_documents(self, texts: List[str]) -> List[List[float]]:
        """嵌入搜索文档。

        参数:
            texts: 要嵌入的文本列表。

        返回:
            List[List[float]]: 嵌入结果列表，每个文本对应一个嵌入结果。
        """

        if not self.access_token:
            self._refresh_access_token_with_lock()
        text_in_chunks = [
            texts[i: i + self.chunk_size]
            for i in range(0, len(texts), self.chunk_size)
        ]
        lst = []
        for chunk in text_in_chunks:
            resp = self._embedding({"input": [text for text in chunk]})
            if resp.get("error_code"):
                if resp.get("error_code") == 111:
                    self._refresh_access_token_with_lock()
                    resp = self._embedding({"input": [text for text in chunk]})
                else:
                    raise ValueError(f"Error from Ernie: {resp}")
            lst.extend([i["embedding"] for i in resp["data"]])
        return lst

    def embed_query(self, text: str) -> List[float]:
        """嵌入查询文本。

        参数:
            text: 要嵌入的文本。

        返回:
            List[float]: 文本的嵌入结果。
        """

        if not self.access_token:
            self._refresh_access_token_with_lock()
        resp = self._embedding({"input": [text]})
        if resp.get("error_code"):
            if resp.get("error_code") == 111:
                self._refresh_access_token_with_lock()
                resp = self._embedding({"input": [text]})
            else:
                raise ValueError(f"Error from Ernie: {resp}")
        return resp["data"][0]["embedding"]

    async def aembed_query(self, text: str) -> List[float]:
        """异步嵌入查询文本。

        参数:
            text: 要嵌入的文本。

        返回:
            List[float]: 文本的嵌入结果。
        """

        return await asyncio.get_running_loop().run_in_executor(
            None, partial(self.embed_query, text)
        )

    async def aembed_documents(self, texts: List[str]) -> List[List[float]]:
        """异步嵌入搜索文档。

        参数:
            texts: 要嵌入的文本列表。

        返回:
            List[List[float]]: 嵌入结果列表，每个文本对应一个嵌入结果。
        """

        result = await asyncio.gather(*[self.aembed_query(text) for text in texts])

        return list(result)
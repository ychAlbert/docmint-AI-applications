#文心一言LLM模型

import json
import requests
from typing import Any, List, Mapping, Optional, Dict, Union, Tuple
from langchain.callbacks.manager import CallbackManagerForLLMRun
from langchain.llms.base import LLM
from pydantic import BaseModel, Field
from langchain.utils import get_from_dict_or_env

from typing import Any, Dict, List, Optional, Tuple, Union
import erniebot
import os
from dotenv import load_dotenv, find_dotenv
load_dotenv(find_dotenv())

# 加载环境变量
erniebot.access_token = os.getenv('ERNIE_BOT_ACCESS_TOKEN')
erniebot.api_type = 'aistudio'


class Wenxin_LLM(LLM):
    model_name: str = "ernie-3.5"
    temperature: float = 0.1
    access_token: str = None
    request_timeout: Optional[Union[float, Tuple[float, float]]] = None
    model_kwargs: Dict[str, Any] = dict()

    def __init__(self, access_token: str, **data: Any):
        super().__init__(**data)

        if access_token is None:
            raise ValueError("access_token 不能为空")
        self.access_token = access_token

    def _call(self, prompt: str, stop: Optional[List[str]] = None,
              run_manager: Optional[CallbackManagerForLLMRun] = None,
              **kwargs: Any):
        """
        使用SDK调用大模型
        """
        response = erniebot.ChatCompletion.create(
            model=self.model_name,  # 可以根据需要调整为正确的模型名称参数
            temperature=self.temperature,
            messages=[{'role': 'user', 'content': prompt}],
            **kwargs  # 动态接受其他可配置的参数
        )

        # 假设response.get_result()是获取返回结果的方法
        try:
            result = response.get_result()
        except Exception as e:
            print(e)
            result = "请求失败"

        return result
    @property
    def _default_params(self) -> Dict[str, Any]:
        """
        获取调用 API 的默认参数
        """
        return {
            "temperature": self.temperature,
            "request_timeout": self.request_timeout
        }


    @property
    def _llm_type(self):
        """
        返回LLM类型
        """
        return 'WENXIN'

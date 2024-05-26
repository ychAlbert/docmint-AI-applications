#本代码为原有设计，基于百度云文心一言大模型api的调用，并未修改

import json
import requests
from typing import Any, List, Mapping, Optional, Dict, Union, Tuple
from langchain.callbacks.manager import CallbackManagerForLLMRun
from langchain.llms.base import LLM
from pydantic import BaseModel, Field
from langchain.utils import get_from_dict_or_env

# 获取 access_token 的函数
def get_access_token(api_key: str, secret_key: str) -> str:
    """
    使用 API Key，Secret Key 获取 access_token
    """
    url = f"https://aip.baidubce.com/oauth/2.0/token?grant_type=client_credentials&client_id={api_key}&client_secret={secret_key}"
    headers = {
        'Content-Type': 'application/json',
        'Accept': 'application/json'
    }
    response = requests.post(url, headers=headers, data=json.dumps(""))
    return response.json().get("access_token")

# 继承自 LLM 的百度文心 LLM 类
class Wenxin_LLM(LLM):
    url: str = "https://gbkbm463o1pdn9s9.aistudio-hub.baidu.com/chat/completions"
    api_type = 'aistudio'
    model_name: str = Field(default="ERNIE-Bot-turbo", alias="model")
    temperature: float = 0.1
    api_key: str = None
    secret_key: str = None
    access_token: str = None
    request_timeout: Optional[Union[float, Tuple[float, float]]] = None
    model_kwargs: Dict[str, Any] = Field(default_factory=dict)

    def __init__(self, **data: Any):
        super().__init__(**data)
        if self.api_key is None or self.secret_key is None:
            self.api_key, self.secret_key = get_from_dict_or_env(self.model_kwargs, "api_key"), get_from_dict_or_env(self.model_kwargs, "secret_key")
        self.init_access_token()

    def init_access_token(self):
        """
        初始化 access_token
        """
        if self.api_key and self.secret_key:
            try:
                self.access_token = get_access_token(self.api_key, self.secret_key)
            except Exception as e:
                print(e)
                print("获取 access_token 失败，请检查 Key")
        else:
            print("API_Key 或 Secret_Key 为空，请检查 Key")

    def _call(self, prompt: str, stop: Optional[List[str]] = None,
              run_manager: Optional[CallbackManagerForLLMRun] = None,
              **kwargs: Any):
        """
        调用百度文心 API
        """
        if not self.access_token:
            self.init_access_token()
        url = f"{self.url}?access_token={self.access_token}"
        payload = json.dumps({
            "messages": [ {"role": "user", "content": prompt} ],
            'temperature': self.temperature,
            **kwargs
        })
        headers = {'Content-Type': 'application/json'}
        response = requests.post(url, headers=headers, data=payload, timeout=self.request_timeout)
        if response.status_code == 200:
            return json.loads(response.text).get("result")
        else:
            return "请求失败"

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
    def _identifying_params(self) -> Mapping[str, Any]:
        """
        获取标识参数
        """
        return {
            "model_name": self.model_name,
            **self._default_params
        }
    @property
    def _llm_type(self):
        """
        返回LLM类型
        """
        return 'wenxin'

#!/usr/bin/env python
# -*- coding:UTF-8 -*-
#
# @AUTHOR: Rabbir
# @FILE: ~/Projects/fastapi-auth/app/controller/main.py
# @DATE: 2023/08/10 周四
# @TIME: 10:34:03
#
# @DESCRIPTION: Controller - 主控制器


import copy
import time
import json
from fastapi import FastAPI, Request, Response

from external.rab_common import redis as external_rab_common_redis
from external.rab_common import orm as external_rab_common_orm
from external.rab_fastapi_auth.controller import auth as external_rab_fastapi_auth_controller_auth


# FastAPI 实例
APP = FastAPI()


@APP.on_event("startup")
async def startup():
    """
    @description: 启动时执行
    """
    # 1. 初始化 Redis
    APP.state.redis = await external_rab_common_redis.init_redis_async()
    print("FastAPI - Redis 连接建立。")
    # 2. 建立数据库连接
    APP.state.session = external_rab_common_orm.init_db()
    print("FastAPI - 数据库连接建立。")

@APP.middleware("http")
async def handle_response_style(request: Request, call_next):
    """
    @description: 截取所有请求，并修改 response 的格式风格
    """
    # 1. 记录这个请求的耗时
    start_time = time.time()
    response = await call_next(request)
    process_time = time.time() - start_time
    response.headers["X-Process-Time"] = str(process_time)
    # 2. 修改响应格式为 And Deisgn Pro 官方建议风格
    # https://pro.ant.design/zh-CN/docs/request#参考后端接口规范建议
    response_body = b""
    async for chunk in response.body_iterator:
        response_body += chunk
    # 2.1 解码响应体
    decoded_response_body = json.loads(response_body.decode("utf-8"))
    # 2.2 补齐需要用到的字段
    if "code" not in decoded_response_body:
        decoded_response_body["code"] = 404
    if "msg" not in decoded_response_body:
        decoded_response_body["msg"] = ""
    if "data" not in decoded_response_body:
        decoded_response_body["data"] = {}
    new_decoded_response_body = copy.deepcopy(decoded_response_body)
    # 2.3 正常响应
    if response.status_code == 200:
        del new_decoded_response_body["code"]
        del new_decoded_response_body["msg"]
        del new_decoded_response_body["data"]
        new_decoded_response_body = {"success": True, "data": decoded_response_body["data"], "code": decoded_response_body["code"], "message": decoded_response_body["msg"], **new_decoded_response_body}
    # 2.4 失败响应
    else:
        new_decoded_response_body = {"success": False, "data": decoded_response_body["data"], "errorCode": decoded_response_body["code"], "errorMessage": decoded_response_body["msg"]}
    # 2.5 重新编码响应体
    # print("FastAPI - 请求响应：", new_decoded_response_body)
    new_response_body = json.dumps(new_decoded_response_body, ensure_ascii=False).encode("utf-8")
    # 3. 修改响应头中的 Content-Length
    response.headers["Content-Length"] = str(len(new_response_body))
    # 4. 返回新的响应
    return Response(
        content=new_response_body,
        status_code=response.status_code,
        headers=dict(response.headers),
    )

@APP.on_event("shutdown")
async def shutdown():
    """
    @description: 关闭时执行
    """
    # 1. 关闭 Redis
    await APP.state.redis.close()
    print("FastAPI - Redis 连接关闭。")
    # 2. 关闭数据库连接
    APP.state.session.close()
    print("FastAPI - 数据库连接关闭。")

@APP.get("/")
async def root():
    """
    @description: 根路由
    """
    return {"code": 200, "msg": "FastAPI - Auth 服务启动成功！", "data": {}}


# 外部路由
APP.include_router(
    external_rab_fastapi_auth_controller_auth.ROUTER
)
#!/usr/bin/env python
# -*- coding:UTF-8 -*-
#
# @AUTHOR: Rabbir
# @FILE: ~/Projects/fastapi-auth/app/main.py
# @DATE: 2023/08/10 周四
# @TIME: 10:32:03
#
# @DESCRIPTION: 主入口


# 启动
if __name__ == "__main__":
    import uvicorn
    from controller import main as controller_main
    uvicorn.run(app="controller.main:APP", host="0.0.0.0", port=8000, reload=True)

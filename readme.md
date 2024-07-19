##  Simple Distributed Cache System

### Introduction

完成一个简易分布式缓存系统，其基本系统架构如下图：
![1721379850764.png](https://img.qylh.xyz/blog/1721379850764.png)

具体功能如下：

1. Cache数据以Key-value形式存储在缓存系统节点内存中
2. Cache数据以Hash策略分布在不同节点（不考虑副本存储）；
3. 服务至少启动3个节点：
   1. 所有节点均提供HTTP访问入口；
   2. 客户端读写访问可从任意节点接入，每个请求只支持一个key存取；
   3. 客户端读写访问可从任意节点接入，每个请求只支持一个key存取；
4. 程序基于docker打包，并通过docker compose启动运行


系统基于Python程序设计语言实现，使用Flask框架构建HTTP服务，基于jsonrpc进行远程过程调用，使用基于虚拟节点的一致性 hash算法决定数据存储节点。

![1721380037593.png](https://img.qylh.xyz/blog/1721380037593.png)


请求流程示意图如下：

![1721380079834.png](https://img.qylh.xyz/blog/1721380079834.png)


### run

`docker-compose build & docker-compose up -d`
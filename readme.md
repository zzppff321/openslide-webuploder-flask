# openslide+webuploader 大文件上传分割

## 文档说明

>####请求参数
> 所有请求方式如果没有特殊标注，均为get。如果标注为post，默认数据传输方式为form-data。
> 所有请求参数，如果没有特殊标注，均默认为必填。
> 参数形式如没有特殊标注，默认为string

>####返回参数
> 所有请求返回参数均包含 rc,data,msg 三个部分，其中msg为报错信息，rc=0时，请求成功，rc=1 请求异常，data为返回数据。
> 如果没有特殊说明，文档仅对data中的数据进行解释

>####测试地址
> 暂定测试网址为 http://znffapi.pg024.com。
> webuploader体验的网址为 http://znffapi.pg024.com/test/index.html

## 环境搭建

### 安装openslide

```yum install openslide```

### 安装openslide python 扩展

```pip install openslide-python```

## 后端接口

### 文件上传初始化

>url:/distribution/split/upload/init

返回参数

参数|说明
---|---
task_id|<span id="task_id">上传文件的唯一任务标识</span>

返回示例

```json
{
    "msg": "success",
    "data": {
        "task_id": "cd036a058b8675df2fc1f32fd719c81c"
    },
    "rc": 0
}
```

### 文件分片上传

>url:/distribution/split/upload(post)

请求参数

参数|说明|类型|是否必填
---|---|---|---
task_id| [文件上传初始化返回的唯一标识](#task_id)|STRING|Y
chunk|当前分片在所有文件中的位置，默认0|INT|N
file|需要上传的文件|FILE|Y

返回示例

```json
{
    "msg": "分片上传成功",
    "data": {},
    "rc": 0
}
```

### 文件上传完成 

>url:/distribution/split/upload/finish

请求参数

参数|说明
---|---
task_id|[文件上传初始化返回的唯一标识](#task_id)

返回示例

```json
{
    "msg": "上传完成",
    "data": {},
    "rc": 0
}
```

### 病理图像切割

>url:/distribution/split/split

请求参数

参数|说明
---|---
task_id|[文件上传初始化返回的唯一标识](#task_id)
height|切割后图像高度
width|切割后图像宽度
minUnit|偏移量（最小细胞单元）

> PS：minUnit 不得大于等于 height 或 width。
> 请求结束后，后台会异步执行切割进程，需要调用进度查询接口，定时查询分割进度

### 切割进度查询

>url:/distribution/split/count

请求参数

参数|说明
---|---
task_id|[文件上传初始化返回的唯一标识](#task_id)
height|切割后图像高度

返回参数

参数|说明
---|---
total|总计目标切割文件数量
done|已完成切割数量

返回示例

```json
{
    "msg": "success",
    "data": {
        "total": 900,
        "done": 900
    },
    "rc": 0
}
```


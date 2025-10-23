# API 响应数据标准化文档

## 概述

本项目采用统一的 API 响应数据结构，所有接口（除特殊场景外）都遵循相同的格式返回数据。这样可以简化前端的数据处理逻辑，提高代码的可维护性。

## 响应格式

### 标准响应结构

```typescript
interface ApiResponse<T> {
  code: number      // 响应码，0 表示成功，非 0 表示错误
  message: string   // 响应消息
  data: T | null    // 响应数据，成功时包含实际数据，失败时为 null
}
```

### 成功响应示例

```json
{
  "code": 0,
  "message": "Success",
  "data": {
    "id": "123",
    "name": "example"
  }
}
```

### 错误响应示例

```json
{
  "code": 400,
  "message": "Bad Request",
  "data": null
}
```

### 分页响应结构

```typescript
interface PaginationData<T> {
  items: T[]         // 数据列表
  total: number      // 总数据量
  page: number       // 当前页码
  page_size: number  // 每页数量
  total_pages: number // 总页数
}

type PaginatedResponse<T> = ApiResponse<PaginationData<T>>
```

#### 分页响应示例

```json
{
  "code": 0,
  "message": "Success",
  "data": {
    "items": [
      { "id": "1", "title": "Item 1" },
      { "id": "2", "title": "Item 2" }
    ],
    "total": 100,
    "page": 1,
    "page_size": 20,
    "total_pages": 5
  }
}
```

## 后端实现

### 1. 使用响应辅助函数

后端提供了便捷的辅助函数来创建标准化响应：

```python
from app.schemas.response import success, error, paginated_success

# 成功响应
@router.get("/items/{item_id}")
async def get_item(item_id: str):
    item = await get_item_from_db(item_id)
    return success(data=item, message="获取成功")

# 错误响应
@router.post("/items")
async def create_item(item: ItemCreate):
    if not valid:
        raise HTTPException(
            status_code=400,
            detail="Invalid data"
        )
    # HTTPException 会被全局异常处理器自动转换为标准格式

# 分页响应
@router.get("/items")
async def list_items(page: int = 1, page_size: int = 20):
    items, total = await get_items_from_db(skip=(page-1)*page_size, limit=page_size)
    return paginated_success(
        items=items,
        total=total,
        page=page,
        page_size=page_size,
        message="获取列表成功"
    )
```

### 2. 全局异常处理

所有的 HTTP 异常都会被全局异常处理器自动转换为统一的响应格式：

```python
# backend/app/main.py
@app.exception_handler(StarletteHTTPException)
async def http_exception_handler(request: Request, exc: StarletteHTTPException):
    return JSONResponse(
        status_code=exc.status_code,
        content=error(
            code=exc.status_code,
            message=exc.detail or "An error occurred",
            data=None
        )
    )
```

## 前端实现

### 1. TypeScript 类型定义

```typescript
// frontend/src/types/api.ts
export interface ApiResponse<T = any> {
  code: number
  message: string
  data: T | null
}

export interface PaginationData<T> {
  items: T[]
  total: number
  page: number
  page_size: number
  total_pages: number
}

export type PaginatedResponse<T> = ApiResponse<PaginationData<T>>
```

### 2. API 客户端自动提取 data

前端的 `api` 对象会自动提取 `response.data.data`，简化使用：

```typescript
// 基础用法 - 自动提取 data 字段
const user = await api.get<User>('/api/v1/auth/me')
// user 直接是 User 类型，不需要 user.data

const document = await api.post<Document>('/api/v1/documents', formData)
// document 直接是 Document 类型

// 如果需要完整响应（包含 code 和 message）
const response = await api.getRaw<User>('/api/v1/auth/me')
console.log(response.data.code)    // 0
console.log(response.data.message) // "Success"
console.log(response.data.data)    // User 对象
```

### 3. 统一错误处理

API 客户端的响应拦截器会自动处理错误：

```typescript
// 前端代码
try {
  const user = await api.get<User>('/api/v1/users/123')
} catch (err: any) {
  // err 是 ApiError 类型
  console.error(err.message) // 显示错误消息
  console.error(err.status)  // 错误状态码
}
```

错误对象结构：

```typescript
interface ApiError {
  message: string  // 错误消息
  status?: number  // HTTP 状态码
  detail?: string  // 详细错误信息
}
```

## 响应码规范

| Code | 含义 | 使用场景 |
|------|------|----------|
| 0 | 成功 | 请求成功处理 |
| 400 | 客户端错误 | 参数错误、验证失败 |
| 401 | 未授权 | 未登录或 token 失效 |
| 403 | 禁止访问 | 无权限访问资源 |
| 404 | 未找到 | 资源不存在 |
| 422 | 验证错误 | 请求参数验证失败 |
| 500 | 服务器错误 | 服务器内部错误 |

## API 方法对照

### 标准方法（自动提取 data）

```typescript
api.get<T>(url, config?)      // 返回 T
api.post<T>(url, data?, config?) // 返回 T
api.put<T>(url, data?, config?)  // 返回 T
api.delete<T>(url, config?)   // 返回 T
api.patch<T>(url, data?, config?) // 返回 T
```

### Raw 方法（获取完整响应）

```typescript
api.getRaw<T>(url, config?)    // 返回 AxiosResponse<ApiResponse<T>>
api.postRaw<T>(url, data?, config?) // 返回 AxiosResponse<ApiResponse<T>>
api.putRaw<T>(url, data?, config?)  // 返回 AxiosResponse<ApiResponse<T>>
api.deleteRaw<T>(url, config?) // 返回 AxiosResponse<ApiResponse<T>>
api.patchRaw<T>(url, data?, config?) // 返回 AxiosResponse<ApiResponse<T>>
```

## 最佳实践

### 后端

1. **始终使用辅助函数**：使用 `success()`, `error()`, `paginated_success()` 而不是手动构造响应
2. **使用 HTTPException**：对于错误情况，抛出 HTTPException，全局处理器会自动转换格式
3. **提供有意义的消息**：message 字段应该清晰描述操作结果

### 前端

1. **使用标准 API 方法**：优先使用 `api.get/post/put/delete/patch`，它们会自动提取 data
2. **正确处理错误**：捕获异常并使用 `err.message` 显示错误
3. **类型安全**：始终为 API 调用指定泛型类型

```typescript
// ✅ 推荐
const user = await api.get<User>('/api/v1/auth/me')

// ❌ 不推荐
const response = await api.get('/api/v1/auth/me')
const user = response.data.data
```

## 迁移指南

如果有旧代码需要迁移到新的响应格式：

### 后端

```python
# 旧代码
@router.get("/items/{item_id}")
async def get_item(item_id: str):
    return {"item": item}

# 新代码
@router.get("/items/{item_id}")
async def get_item(item_id: str):
    return success(data=item, message="获取成功")
```

### 前端

```typescript
// 旧代码
const response = await api.get('/api/v1/items/123')
const item = response.data

// 新代码
const item = await api.get<Item>('/api/v1/items/123')
```

## 特殊场景

某些特殊场景可能不遵循标准格式：

1. **文件下载**：返回二进制流
2. **第三方回调**：需要符合第三方规范的响应格式
3. **健康检查**：简单的状态检查可能使用更简单的格式（但建议也统一）

对于这些场景，应在 API 文档中明确说明。

## 相关文件

- 后端响应 Schema: `backend/app/schemas/response.py`
- 前端类型定义: `frontend/src/types/api.ts`
- 前端 API 客户端: `frontend/src/lib/api.ts`
- 全局异常处理: `backend/app/main.py`

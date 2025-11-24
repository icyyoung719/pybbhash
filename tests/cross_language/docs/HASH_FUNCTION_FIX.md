# 哈希函数修复说明

## 问题

在跨语言测试中发现，Python 无法正确加载 C++ 生成的 MPHF 二进制文件。某些键的 lookup 返回 -1，表示找不到键。

## 根本原因

Python 的 `_hash64` 函数实现与 C++ 不完全一致。

### 错误的实现（修复前）

Python 代码将第一行拆分成了三次 XOR 操作：

```python
hashv ^= (hashv << 7) & 0xFFFFFFFFFFFFFFFF
hashv ^= (k * (hashv >> 3)) & 0xFFFFFFFFFFFFFFFF
hashv ^= (~((hashv << 11) + (k ^ (hashv >> 5)))) & 0xFFFFFFFFFFFFFFFF
```

这会导致：
1. `hashv ^= A`
2. `hashv ^= B` (使用上一步修改后的 hashv)
3. `hashv ^= C` (使用上一步修改后的 hashv)

### 正确的实现（修复后）

C++ 代码是单行操作：

```cpp
hash ^= (hash << 7) ^ key * (hash >> 3) ^ (~((hash << 11) + (key ^ (hash >> 5))));
```

Python 应该匹配为：

```python
hashv = (hashv ^ ((hashv << 7) ^ (k * (hashv >> 3)) ^ (~((hashv << 11) + (k ^ (hashv >> 5)))))) & 0xFFFFFFFFFFFFFFFF
```

这相当于：
1. `hashv = hashv ^ (A ^ B ^ C)` (使用原始的 hashv 计算 A, B, C)

## 影响

错误的实现导致：
- Python 构建的 MPHF 可以自己正常使用
- C++ 构建的 MPHF 无法被 Python 正确加载
- 哈希值完全不同，键无法被找到

## 修复

在 `pybbhash/hashfunctors.py` 的 `_hash64` 方法中，将第一行的三次分开的 XOR 操作合并为一次操作。

## 验证

修复后：
- ✅ Python 可以正确加载 C++ 生成的 MPHF
- ✅ 所有 1000 个测试键都能正确查找
- ✅ 哈希值在有效范围内 [0, 999]
- ✅ 所有哈希值唯一（完美哈希特性）
- ✅ 现有的 Python 测试仍然通过

## 教训

在移植 C/C++ 代码到 Python 时，必须特别注意：
1. **操作顺序**：`a ^= b; a ^= c;` 与 `a = a ^ (b ^ c)` 是不同的
2. **副作用**：中间修改会影响后续计算
3. **精确匹配**：哈希函数必须完全一致，即使看起来逻辑相似

## 相关文件

- `pybbhash/hashfunctors.py` - 修复的哈希函数实现
- `cpp-bbhash/BooPHF.h` - C++ 参考实现
- `cpp-bbhash/verify_cpp_export.py` - 验证跨语言兼容性的测试

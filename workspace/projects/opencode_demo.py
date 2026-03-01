#!/usr/bin/env python3
"""
OpenCode 编码技能演示
展示如何使用OpenCode技能进行高质量Python编码
"""

import json
import os
import sys
from typing import Dict, List, Optional, Any, Union
from dataclasses import dataclass, field
from datetime import datetime
import hashlib
import re
from pathlib import Path

# ============================================================================
# OpenCode 编码技能核心类
# ============================================================================

@dataclass
class CodeTask:
    """代码任务定义"""
    title: str
    description: str
    requirements: List[str]
    constraints: List[str] = field(default_factory=list)
    acceptance_criteria: List[str] = field(default_factory=list)
    
    def to_dict(self) -> Dict:
        """转换为字典"""
        return {
            "title": self.title,
            "description": self.description,
            "requirements": self.requirements,
            "constraints": self.constraints,
            "acceptance_criteria": self.acceptance_criteria
        }

@dataclass
class CodeChange:
    """代码变更记录"""
    file_path: str
    change_type: str  # "add", "modify", "delete", "refactor"
    old_content: Optional[str] = None
    new_content: Optional[str] = None
    reason: str = ""
    
    def to_dict(self) -> Dict:
        """转换为字典"""
        return {
            "file_path": self.file_path,
            "change_type": self.change_type,
            "reason": self.reason,
            "has_old_content": self.old_content is not None,
            "has_new_content": self.new_content is not None
        }

@dataclass
class ValidationResult:
    """验证结果"""
    test_name: str
    status: str  # "passed", "failed", "skipped"
    message: str = ""
    duration_ms: int = 0
    
    def to_dict(self) -> Dict:
        """转换为字典"""
        return {
            "test_name": self.test_name,
            "status": self.status,
            "message": self.message,
            "duration_ms": self.duration_ms
        }

@dataclass
class DeliveryReport:
    """交付报告"""
    task: CodeTask
    changes: List[CodeChange]
    validations: List[ValidationResult]
    summary: str
    risks: List[str] = field(default_factory=list)
    next_steps: List[str] = field(default_factory=list)
    
    def to_dict(self) -> Dict:
        """转换为字典"""
        return {
            "task": self.task.to_dict(),
            "changes_count": len(self.changes),
            "validations_count": len(self.validations),
            "summary": self.summary,
            "risks": self.risks,
            "next_steps": self.next_steps,
            "timestamp": datetime.now().isoformat()
        }

# ============================================================================
# OpenCode 编码器
# ============================================================================

class OpenCodeEncoder:
    """OpenCode 编码器 - 核心编码逻辑"""
    
    def __init__(self, project_root: str = "."):
        self.project_root = Path(project_root).resolve()
        self.changes: List[CodeChange] = []
        self.validations: List[ValidationResult] = []
        
    def understand_task(self, task: CodeTask) -> Dict:
        """理解任务与约束 - 步骤1"""
        print(f"📋 理解任务: {task.title}")
        print(f"📝 描述: {task.description}")
        
        if task.constraints:
            print("🔒 约束条件:")
            for constraint in task.constraints:
                print(f"  - {constraint}")
        
        if task.acceptance_criteria:
            print("✅ 验收标准:")
            for criteria in task.acceptance_criteria:
                print(f"  - {criteria}")
        
        return {
            "understood": True,
            "task_complexity": self._assess_complexity(task),
            "estimated_files": self._estimate_files_needed(task)
        }
    
    def read_before_change(self, file_patterns: List[str]) -> Dict:
        """先读后改 - 步骤2"""
        print("🔍 先读后改: 定位相关文件")
        
        found_files = []
        for pattern in file_patterns:
            for file_path in self.project_root.rglob(pattern):
                if file_path.is_file():
                    found_files.append(str(file_path.relative_to(self.project_root)))
        
        print(f"📁 找到 {len(found_files)} 个相关文件")
        if found_files:
            print("  文件列表:")
            for file in found_files[:10]:  # 只显示前10个
                print(f"    - {file}")
            if len(found_files) > 10:
                print(f"    ... 还有 {len(found_files) - 10} 个文件")
        
        return {
            "files_found": found_files,
            "files_to_read": found_files[:5] if found_files else []  # 只读前5个
        }
    
    def implement_change(self, task: CodeTask) -> List[CodeChange]:
        """实施改动 - 步骤3"""
        print("🔨 实施改动")
        
        # 根据任务类型实施不同的改动
        if "文件处理" in task.title or "文件操作" in task.description:
            return self._implement_file_operations(task)
        elif "API" in task.title or "接口" in task.description:
            return self._implement_api_operations(task)
        elif "数据处理" in task.title or "数据" in task.description:
            return self._implement_data_operations(task)
        else:
            return self._implement_general_operations(task)
    
    def validate_locally(self) -> List[ValidationResult]:
        """本地验证 - 步骤4"""
        print("🧪 本地验证")
        
        validations = []
        
        # 验证1: 语法检查
        syntax_result = self._validate_syntax()
        validations.append(syntax_result)
        
        # 验证2: 导入检查
        import_result = self._validate_imports()
        validations.append(import_result)
        
        # 验证3: 运行简单测试
        run_result = self._validate_runtime()
        validations.append(run_result)
        
        self.validations = validations
        return validations
    
    def create_delivery_report(self, task: CodeTask) -> DeliveryReport:
        """交付说明 - 步骤5"""
        print("📄 创建交付报告")
        
        summary = f"已完成任务: {task.title}\n"
        summary += f"修改了 {len(self.changes)} 个文件\n"
        
        passed = sum(1 for v in self.validations if v.status == "passed")
        summary += f"验证结果: {passed}/{len(self.validations)} 通过"
        
        risks = []
        if any(v.status == "failed" for v in self.validations):
            risks.append("部分验证未通过，需要人工检查")
        
        next_steps = [
            "审查代码变更",
            "运行完整测试套件",
            "部署到测试环境"
        ]
        
        return DeliveryReport(
            task=task,
            changes=self.changes,
            validations=self.validations,
            summary=summary,
            risks=risks,
            next_steps=next_steps
        )
    
    # ============================================================================
    # 私有方法
    # ============================================================================
    
    def _assess_complexity(self, task: CodeTask) -> str:
        """评估任务复杂度"""
        word_count = len(task.description.split())
        req_count = len(task.requirements)
        
        if word_count < 50 and req_count < 3:
            return "简单"
        elif word_count < 100 and req_count < 5:
            return "中等"
        else:
            return "复杂"
    
    def _estimate_files_needed(self, task: CodeTask) -> List[str]:
        """估计需要的文件"""
        files = []
        
        if any(keyword in task.description.lower() for keyword in ["文件", "读写", "保存"]):
            files.append("file_operations.py")
        
        if any(keyword in task.description.lower() for keyword in ["api", "接口", "请求"]):
            files.append("api_client.py")
        
        if any(keyword in task.description.lower() for keyword in ["数据", "处理", "分析"]):
            files.append("data_processor.py")
        
        return files
    
    def _implement_file_operations(self, task: CodeTask) -> List[CodeChange]:
        """实现文件操作相关功能"""
        changes = []
        
        # 创建文件操作工具类
        file_ops_content = '''"""
文件操作工具类
提供安全的文件读写、备份和验证功能
"""

import os
import shutil
import hashlib
from pathlib import Path
from typing import Optional, List, Tuple
import json
import pickle


class FileOperations:
    """文件操作工具类"""
    
    @staticmethod
    def safe_read_text(file_path: str, encoding: str = "utf-8") -> str:
        """安全读取文本文件"""
        try:
            with open(file_path, 'r', encoding=encoding) as f:
                return f.read()
        except FileNotFoundError:
            raise FileNotFoundError(f"文件不存在: {file_path}")
        except UnicodeDecodeError:
            # 尝试其他编码
            try:
                with open(file_path, 'r', encoding='gbk') as f:
                    return f.read()
            except:
                raise ValueError(f"无法解码文件: {file_path}")
    
    @staticmethod
    def safe_write_text(file_path: str, content: str, encoding: str = "utf-8") -> None:
        """安全写入文本文件（自动创建目录）"""
        path = Path(file_path)
        path.parent.mkdir(parents=True, exist_ok=True)
        
        # 先写入临时文件，然后重命名（原子操作）
        temp_path = str(path) + ".tmp"
        with open(temp_path, 'w', encoding=encoding) as f:
            f.write(content)
        
        # 重命名（在支持原子重命名的系统上）
        os.replace(temp_path, file_path)
    
    @staticmethod
    def backup_file(file_path: str, backup_suffix: str = ".bak") -> Optional[str]:
        """备份文件"""
        if not os.path.exists(file_path):
            return None
        
        backup_path = file_path + backup_suffix
        shutil.copy2(file_path, backup_path)
        return backup_path
    
    @staticmethod
    def calculate_file_hash(file_path: str, algorithm: str = "sha256") -> str:
        """计算文件哈希值"""
        hash_func = hashlib.new(algorithm)
        
        with open(file_path, 'rb') as f:
            for chunk in iter(lambda: f.read(4096), b''):
                hash_func.update(chunk)
        
        return hash_func.hexdigest()
    
    @staticmethod
    def find_files_by_pattern(directory: str, pattern: str) -> List[str]:
        """按模式查找文件"""
        import glob
        search_path = os.path.join(directory, "**", pattern)
        return glob.glob(search_path, recursive=True)
    
    @staticmethod
    def read_json(file_path: str) -> dict:
        """读取JSON文件"""
        content = FileOperations.safe_read_text(file_path)
        return json.loads(content)
    
    @staticmethod
    def write_json(file_path: str, data: dict, indent: int = 2) -> None:
        """写入JSON文件"""
        content = json.dumps(data, ensure_ascii=False, indent=indent)
        FileOperations.safe_write_text(file_path, content)
    
    @staticmethod
    def read_pickle(file_path: str) -> any:
        """读取pickle文件"""
        with open(file_path, 'rb') as f:
            return pickle.load(f)
    
    @staticmethod
    def write_pickle(file_path: str, data: any) -> None:
        """写入pickle文件"""
        with open(file_path, 'wb') as f:
            pickle.dump(data, f)


# 使用示例
if __name__ == "__main__":
    # 示例：文件操作
    ops = FileOperations()
    
    # 写入测试文件
    test_content = "Hello, OpenCode!"
    ops.safe_write_text("test.txt", test_content)
    
    # 读取文件
    content = ops.safe_read_text("test.txt")
    print(f"读取内容: {content}")
    
    # 计算哈希
    file_hash = ops.calculate_file_hash("test.txt")
    print(f"文件哈希: {file_hash}")
    
    # 清理
    os.remove("test.txt")
'''
        
        changes.append(CodeChange(
            file_path="file_operations.py",
            change_type="add",
            new_content=file_ops_content,
            reason="创建文件操作工具类，提供安全的文件读写功能"
        ))
        
        return changes
    
    def _implement_api_operations(self, task: CodeTask) -> List[CodeChange]:
        """实现API操作相关功能"""
        changes = []
        
        # 创建API客户端
        api_client_content = '''"""
API客户端工具类
提供HTTP请求、错误处理和重试机制
"""

import requests
import time
from typing import Optional, Dict, Any, Union
from dataclasses import dataclass
import json
from functools import wraps


@dataclass
class ApiResponse:
    """API响应封装"""
    success: bool
    data: Optional[Any] = None
    error: Optional[str] = None
    status_code: Optional[int] = None
    headers: Optional[Dict] = None
    elapsed_ms: Optional[int] = None


class ApiClient:
    """API客户端"""
    
    def __init__(self, base_url: str = "", timeout: int = 30):
        self.base_url = base_url.rstrip('/')
        self.timeout = timeout
        self.session = requests.Session()
        
        # 默认请求头
        self.session.headers.update({
            'User-Agent': 'OpenCode-API-Client/1.0',
            'Accept': 'application/json',
            'Content-Type': 'application/json'
        })
    
    def set_auth_token(self, token: str, auth_type: str = "Bearer"):
        """设置认证令牌"""
        self.session.headers['Authorization'] = f"{auth_type} {token}"
    
    def set_header(self, key: str, value: str):
        """设置请求头"""
        self.session.headers[key] = value
    
    def _make_request(self, method: str, endpoint: str, **kwargs) -> ApiResponse:
        """执行HTTP请求"""
        url = f"{self.base_url}/{endpoint.lstrip('/')}" if self.base_url else endpoint
        
        start_time = time.time()
        
        try:
            response = self.session.request(
                method=method,
                url=url,
                timeout=self.timeout,
                **kwargs
            )
            
            elapsed_ms = int((time.time() - start_time) * 1000)
            
            # 尝试解析JSON响应
            data = None
            if response.content:
                try:
                    data = response.json()
                except:
                    data = response.text
            
            return ApiResponse(
                success=200 <= response.status_code < 300,
                data=data,
                error=None if response.ok else f"HTTP {response.status_code}",
                status_code=response.status_code,
                headers=dict(response.headers),
                elapsed_ms=elapsed_ms
            )
            
        except requests.exceptions.Timeout:
            return ApiResponse(
                success=False,
                error=f"请求超时 ({self.timeout}s)",
                elapsed_ms=int((time.time() - start_time) * 1000)
            )
        except requests.exceptions.ConnectionError:
            return ApiResponse(
                success=False,
                error="连接错误"
            )
        except Exception as e:
            return ApiResponse(
                success=False,
                error=f"请求异常: {str(e)}"
            )
    
    def get(self, endpoint: str, params: Optional[Dict] = None, **kwargs) -> ApiResponse:
        """GET请求"""
        return self._make_request('GET', endpoint, params=params, **kwargs)
    
    def post(self, endpoint: str, data: Optional[Any] = None, **kwargs) -> ApiResponse:
        """POST请求"""
        return self._make_request('POST', endpoint, json=data, **kwargs)
    
    def put(self, endpoint: str, data: Optional[Any] = None, **kwargs) -> ApiResponse:
        """PUT请求"""
        return self._make_request('PUT', endpoint, json=data, **kwargs)
    
    def delete(self, endpoint: str, **kwargs) -> ApiResponse:
        """DELETE请求"""
        return self._make_request('DELETE', endpoint, **kwargs)
    
    def patch(self, endpoint: str, data: Optional[Any] = None, **kwargs) -> ApiResponse:
        """PATCH请求"""
        return self._make_request('PATCH', endpoint, json=data, **kwargs)


def retry_on_failure(max_retries: int = 3, delay: float = 1.0):
    """重试装饰器"""
    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            last_error = None
            
            for attempt in range(max_retries):
                try:
                    return func(*args, **kwargs)
                except Exception as e:
                    last_error = e
                    
                    if attempt < max_retries - 1:
                        time.sleep(delay * (2 ** attempt))  # 指数退避
                        continue
                    else:
                        raise last_error
            
            raise last_error  # 永远不会执行到这里，但为了类型检查
        
        return wrapper
    return decorator


class OpenApiClient(ApiClient):
    """开放API客户端（带重试机制）"""
    
    @retry_on_failure(max_retries=3, delay=1.0)
    def get_with_retry(self, endpoint: str, **kwargs) -> ApiResponse:
        """带重试的GET请求"""
        return self.get(endpoint, **kwargs)
    
    @retry_on_failure(max_retries=3, delay=1.0)
    def post_with_retry(self, endpoint: str, data: Optional[Any] = None, **kwargs) -> Api
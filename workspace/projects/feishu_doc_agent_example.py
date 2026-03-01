#!/usr/bin/env python3
"""
飞书文档专家Agent示例代码
演示如何创建、转换和分析飞书文档
"""

import json
import time
from typing import Dict, List, Optional, Any
import requests
from dataclasses import dataclass, field
from enum import Enum

# ============================================================================
# 数据类型定义
# ============================================================================

class BlockType(Enum):
    """块类型枚举"""
    PAGE = 1
    TEXT = 2
    HEADING1 = 3
    HEADING2 = 4
    HEADING3 = 5
    BULLET = 12
    ORDERED = 13
    CODE = 14
    QUOTE = 15
    DIVIDER = 21

@dataclass
class TextStyle:
    """文本样式"""
    bold: bool = False
    italic: bool = False
    strikethrough: bool = False
    underline: bool = False
    inline_code: bool = False
    
    def to_dict(self) -> Dict:
        """转换为字典"""
        return {
            "bold": self.bold,
            "italic": self.italic,
            "strikethrough": self.strikethrough,
            "underline": self.underline,
            "inline_code": self.inline_code
        }

@dataclass
class TextElement:
    """文本元素"""
    content: str
    style: TextStyle = field(default_factory=TextStyle)
    
    def to_dict(self) -> Dict:
        """转换为字典"""
        return {
            "text_run": {
                "content": self.content,
                "text_element_style": self.style.to_dict()
            }
        }

@dataclass
class DocumentBlock:
    """文档块"""
    block_type: BlockType
    elements: List[TextElement] = field(default_factory=list)
    children: List['DocumentBlock'] = field(default_factory=list)
    style: Dict = field(default_factory=dict)
    
    def to_dict(self) -> Dict:
        """转换为API所需的字典格式"""
        block_dict = {
            "block_type": self.block_type.value
        }
        
        # 根据块类型添加不同的字段
        if self.block_type == BlockType.PAGE:
            block_dict["page"] = {
                "elements": [elem.to_dict() for elem in self.elements],
                "style": self.style
            }
        elif self.block_type in [BlockType.HEADING1, BlockType.HEADING2, BlockType.HEADING3]:
            level = self.block_type.value - 2  # 3->1, 4->2, 5->3
            block_dict[f"heading{level}"] = {
                "elements": [elem.to_dict() for elem in self.elements],
                "style": self.style
            }
        elif self.block_type == BlockType.TEXT:
            block_dict["text"] = {
                "elements": [elem.to_dict() for elem in self.elements],
                "style": self.style
            }
        elif self.block_type == BlockType.BULLET:
            block_dict["bullet"] = {
                "elements": [elem.to_dict() for elem in self.elements],
                "style": self.style
            }
        elif self.block_type == BlockType.CODE:
            block_dict["code"] = {
                "elements": [elem.to_dict() for elem in self.elements],
                "style": self.style
            }
        elif self.block_type == BlockType.QUOTE:
            block_dict["quote"] = {
                "elements": [elem.to_dict() for elem in self.elements],
                "style": self.style
            }
        elif self.block_type == BlockType.DIVIDER:
            block_dict["divider"] = {}
        
        return block_dict

# ============================================================================
# Feishu API客户端
# ============================================================================

class FeishuAPIClient:
    """飞书API客户端"""
    
    def __init__(self, app_id: str, app_secret: str):
        self.app_id = app_id
        self.app_secret = app_secret
        self.access_token = None
        self.token_expiry = 0
        self.base_url = "https://open.feishu.cn/open-apis"
    
    def get_access_token(self) -> str:
        """获取访问令牌"""
        current_time = time.time()
        
        # 如果令牌未过期，直接返回
        if self.access_token and self.token_expiry > current_time:
            return self.access_token
        
        # 获取新令牌
        url = f"{self.base_url}/auth/v3/tenant_access_token/internal"
        payload = {
            "app_id": self.app_id,
            "app_secret": self.app_secret
        }
        
        try:
            response = requests.post(url, json=payload, timeout=10)
            response.raise_for_status()
            data = response.json()
            
            if data.get("code") != 0:
                raise Exception(f"获取令牌失败: {data.get('msg')}")
            
            self.access_token = data["tenant_access_token"]
            self.token_expiry = current_time + data["expire"] - 300  # 提前5分钟过期
            return self.access_token
            
        except requests.exceptions.RequestException as e:
            raise Exception(f"网络请求失败: {str(e)}")
    
    def create_document(self, title: str, folder_token: Optional[str] = None) -> Dict:
        """创建文档"""
        url = f"{self.base_url}/docx/v1/documents"
        headers = {
            "Authorization": f"Bearer {self.get_access_token()}",
            "Content-Type": "application/json"
        }
        
        payload = {"title": title}
        if folder_token:
            payload["folder_token"] = folder_token
        
        try:
            response = requests.post(url, json=payload, headers=headers, timeout=10)
            response.raise_for_status()
            data = response.json()
            
            if data.get("code") != 0:
                raise Exception(f"创建文档失败: {data.get('msg')}")
            
            return data["data"]
            
        except requests.exceptions.RequestException as e:
            raise Exception(f"创建文档请求失败: {str(e)}")
    
    def append_blocks(self, document_token: str, blocks: List[Dict]) -> Dict:
        """追加块到文档"""
        url = f"{self.base_url}/docx/v1/documents/{document_token}/blocks"
        headers = {
            "Authorization": f"Bearer {self.get_access_token()}",
            "Content-Type": "application/json"
        }
        
        payload = {
            "index": -1,  # 追加到末尾
            "blocks": blocks
        }
        
        try:
            response = requests.post(url, json=payload, headers=headers, timeout=30)
            response.raise_for_status()
            data = response.json()
            
            if data.get("code") != 0:
                raise Exception(f"追加块失败: {data.get('msg')}")
            
            return data["data"]
            
        except requests.exceptions.RequestException as e:
            raise Exception(f"追加块请求失败: {str(e)}")
    
    def get_document_blocks(self, document_token: str) -> Dict:
        """获取文档所有块"""
        url = f"{self.base_url}/docx/v1/documents/{document_token}/blocks"
        headers = {
            "Authorization": f"Bearer {self.get_access_token()}"
        }
        
        try:
            response = requests.get(url, headers=headers, timeout=10)
            response.raise_for_status()
            data = response.json()
            
            if data.get("code") != 0:
                raise Exception(f"获取文档块失败: {data.get('msg')}")
            
            return data["data"]
            
        except requests.exceptions.RequestException as e:
            raise Exception(f"获取文档块请求失败: {str(e)}")

# ============================================================================
# 文档构建器
# ============================================================================

class DocumentBuilder:
    """文档构建器"""
    
    def __init__(self):
        self.blocks: List[DocumentBlock] = []
    
    def add_page(self, title: str) -> 'DocumentBuilder':
        """添加页面块"""
        page_block = DocumentBlock(
            block_type=BlockType.PAGE,
            elements=[TextElement(content=title)],
            style={"align": 1}
        )
        self.blocks.append(page_block)
        return self
    
    def add_heading(self, level: int, text: str, style: Optional[TextStyle] = None) -> 'DocumentBuilder':
        """添加标题"""
        if level == 1:
            block_type = BlockType.HEADING1
        elif level == 2:
            block_type = BlockType.HEADING2
        elif level == 3:
            block_type = BlockType.HEADING3
        else:
            raise ValueError(f"不支持的标题级别: {level}")
        
        heading_block = DocumentBlock(
            block_type=block_type,
            elements=[TextElement(content=text, style=style or TextStyle())],
            style={"align": 1, "folded": False}
        )
        self.blocks.append(heading_block)
        return self
    
    def add_text(self, text: str, style: Optional[TextStyle] = None) -> 'DocumentBuilder':
        """添加文本块"""
        text_block = DocumentBlock(
            block_type=BlockType.TEXT,
            elements=[TextElement(content=text, style=style or TextStyle())],
            style={"align": 1}
        )
        self.blocks.append(text_block)
        return self
    
    def add_bullet(self, text: str, style: Optional[TextStyle] = None, indent: int = 0) -> 'DocumentBuilder':
        """添加无序列表项"""
        bullet_block = DocumentBlock(
            block_type=BlockType.BULLET,
            elements=[TextElement(content=text, style=style or TextStyle())],
            style={"align": 1, "folded": False, "indent": indent}
        )
        self.blocks.append(bullet_block)
        return self
    
    def add_code(self, code: str, language: str = "plaintext") -> 'DocumentBuilder':
        """添加代码块"""
        code_style = TextStyle(inline_code=True)
        code_block = DocumentBlock(
            block_type=BlockType.CODE,
            elements=[TextElement(content=code, style=code_style)],
            style={"language": language}
        )
        self.blocks.append(code_block)
        return self
    
    def add_quote(self, text: str, style: Optional[TextStyle] = None) -> 'DocumentBuilder':
        """添加引用块"""
        quote_block = DocumentBlock(
            block_type=BlockType.QUOTE,
            elements=[TextElement(content=text, style=style or TextStyle())],
            style={"align": 1}
        )
        self.blocks.append(quote_block)
        return self
    
    def add_divider(self) -> 'DocumentBuilder':
        """添加分隔线"""
        divider_block = DocumentBlock(block_type=BlockType.DIVIDER)
        self.blocks.append(divider_block)
        return self
    
    def build(self) -> List[Dict]:
        """构建文档块列表"""
        return [block.to_dict() for block in self.blocks]
    
    def clear(self):
        """清空所有块"""
        self.blocks = []

# ============================================================================
# Markdown转换器
# ============================================================================

class MarkdownConverter:
    """Markdown到飞书文档转换器"""
    
    def __init__(self):
        self.builder = DocumentBuilder()
    
    def convert(self, markdown_text: str, title: str = "Converted Document") -> List[Dict]:
        """转换Markdown文本为飞书文档块"""
        self.builder.clear()
        self.builder.add_page(title)
        
        lines = markdown_text.strip().split('\n')
        in_code_block = False
        code_content = []
        code_language = "plaintext"
        
        for line in lines:
            line = line.rstrip()
            
            # 处理代码块
            if line.startswith('```'):
                if in_code_block:
                    # 结束代码块
                    code_text = '\n'.join(code_content)
                    self.builder.add_code(code_text, code_language)
                    in_code_block = False
                    code_content = []
                else:
                    # 开始代码块
                    in_code_block = True
                    code_language = line[3:].strip() or "plaintext"
                continue
            
            if in_code_block:
                code_content.append(line)
                continue
            
            # 处理空行
            if not line:
                continue
            
            # 处理标题
            if line.startswith('### '):
                self.builder.add_heading(3, line[4:].strip())
            elif line.startswith('## '):
                self.builder.add_heading(2, line[3:].strip())
            elif line.startswith('# '):
                self.builder.add_heading(1, line[2:].strip())
            
            # 处理列表
            elif line.startswith('- '):
                text = line[2:].strip()
                style = self._parse_inline_styles(text)
                self.builder.add_bullet(text, style)
            
            # 处理引用
            elif line.startswith('> '):
                text = line[2:].strip()
                style = self._parse_inline_styles(text)
                self.builder.add_quote(text, style)
            
            # 处理分隔线
            elif line.replace('-', '').replace(' ', '') == '' and len(line) >= 3:
                self.builder.add_divider()
            
            # 处理普通文本
            else:
                style = self._parse_inline_styles(line)
                self.builder.add_text(line, style)
        
        return self.builder.build()
    
    def _parse_inline_styles(self, text: str) -> TextStyle:
        """解析行内样式"""
        style = TextStyle()
        
        # 简单样式检测（实际实现需要更复杂的解析）
        if '**' in text or '__' in text:
            style.bold = True
        if '*' in text or '_' in text:
            style.italic = True
        if '`' in text:
            style.inline_code = True
        
        return style

# ============================================================================
# 文档创建专家
# ============================================================================

class DocumentCreator:
    """文档创建专家"""
    
    def __init__(self, api_client: FeishuAPIClient):
        self.api_client = api_client
        self.converter = MarkdownConverter()
    
    def create_from_markdown(self, title: str, markdown_content: str, folder_token: Optional[str] = None) -> Dict:
        """从Markdown创建文档"""
        print(f"正在创建文档: {title}")
        
        # 创建空文档
        create_result = self.api_client.create_document(title, folder_token)
        document_token = create_result["document"]["document_id"]
        print(f"文档创建成功，ID: {document_token}")
        
        # 转换Markdown为块
        blocks = self.converter.convert(markdown_content, title)
        print(f"生成 {len(blocks)} 个块")
        
        # 分批添加块（避免单次请求过大）
        batch_size = 10
        total_added = 0
        
        for i in range(1, len(blocks), batch_size):  # 从1开始跳过页面块
            batch = blocks[i:i+batch_size]
            if batch:
                result = self.api_client.append_blocks(document_token, batch)
                added = len(result.get("blocks", []))
                total_added += added
                print(f"添加批次 {i//batch_size + 1}: {added} 个块")
                time.sleep(0.5)  # 避免频率限制
        
        return {
            "document_id": document_token,
            "title": title,
            "url": f"https://feishu.cn/docx/{document_token}",
            "blocks_added": total_added,
            "status": "success"
        }
    
    def create_meeting_minutes(self, meeting_data: Dict) -> Dict:
        """创建会议纪要"""
        template = """
# 会议纪要

## 会议基本信息
- 会议主题: {topic}
- 会议时间: {time}
- 参会人员: {participants}
- 会议地点: {location}

## 会议议程
1. {agenda1}
2. {agenda2}
3. {agenda3}

## 会议决议
- {resolution1}
- {resolution2}

## 下一步行动
- {action1} - 负责人: {owner1} - 截止时间: {deadline1}
- {action2} - 负责人: {owner2} - 截止时间: {deadline2}

---
*文档由飞书文档专家Agent自动生成*
"""
        
        # 填充模板
        content = template.format(**meeting_data)
        title = f"会议纪要 - {meeting_data.get('topic', '未命名会议')}"
        
        return self.create_from_markdown(title, content)

# ============================================================================
# 使用示例
# ============================================================================

def main():
    """主函数 - 演示如何使用飞书文档专家Agent"""
    
    # 配置信息（实际使用时需要从环境变量或配置文件中读取）
    APP_ID = "your_app_id"
    APP_SECRET = "your_app_secret"
    
    print("=" * 60)
    print("飞书文档专家Agent演示")
    print("=" * 60)
    
    try:
        # 1. 初始化API客户端
        print("\n1. 初始化Feishu API客户端...")
        api_client = FeishuAPIClient(APP_ID, APP_SECRET)
        
        # 2. 创建文档创建专家
        print("2. 创建文档创建专家...")
        creator = DocumentCreator(api_client)
        
        # 3. 示例1: 从Markdown创建简单文档
        print("\n3. 示例1: 从Markdown创建简单文档")
        markdown_content = """
# 测试文档

这是一个测试文档，用于演示飞书文档专家Agent的功能。

## 功能特点
- **自动化创建**：自动生成结构化文档
- **智能转换**：支持Markdown到飞书格式转换
- **模板支持**：提供多种文档模板

## 代码示例
```python
def hello_feishu():
    print("Hello Feishu!")

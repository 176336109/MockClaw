# 飞书文档专家Agent实现方案

## 项目概述

### 目标
创建一个专门处理飞书文档的智能Agent，能够：
1. 智能创建和编辑飞书文档
2. 实现Markdown到飞书格式的高质量转换
3. 分析文档结构并提供优化建议
4. 提供文档模板和最佳实践

### 核心价值
- **自动化文档创建**：减少手动操作，提高效率
- **智能格式转换**：保持内容结构，优化阅读体验
- **专业文档分析**：提供数据驱动的优化建议
- **模板化工作流**：标准化文档创建流程

## 系统架构

### 整体架构
```
┌─────────────────────────────────────────┐
│           用户接口层                     │
│  • CLI命令行工具                         │
│  • Web界面                              │
│  • API服务                              │
└─────────────────┬───────────────────────┘
                  │
┌─────────────────▼───────────────────────┐
│           业务逻辑层                     │
│  • 文档创建专家 (DocumentCreator)        │
│  • 格式转换专家 (FormatConverter)        │
│  • 文档分析专家 (DocumentAnalyzer)       │
│  • 模板管理专家 (TemplateManager)        │
└─────────────────┬───────────────────────┘
                  │
┌─────────────────▼───────────────────────┐
│           数据访问层                     │
│  • Feishu API客户端 (FeishuAPIClient)    │
│  • 缓存管理器 (CacheManager)             │
│  • 配置管理器 (ConfigManager)            │
└─────────────────┬───────────────────────┘
                  │
┌─────────────────▼───────────────────────┐
│           飞书云平台                     │
│  • 文档存储服务                          │
│  • 权限管理服务                          │
│  • 实时协作服务                          │
└─────────────────────────────────────────┘
```

## 核心模块设计

### 1. Feishu API客户端模块

#### 功能
- 封装所有飞书文档API调用
- 处理认证和令牌管理
- 实现重试和错误处理机制
- 提供统一的接口抽象

#### 类设计
```python
class FeishuAPIClient:
    """飞书API客户端"""
    
    def __init__(self, app_id, app_secret):
        self.app_id = app_id
        self.app_secret = app_secret
        self.access_token = None
        self.token_expiry = None
    
    def get_access_token(self):
        """获取访问令牌"""
        if self.access_token and self.token_expiry > time.time():
            return self.access_token
        
        # 调用API获取新令牌
        response = self._request_token()
        self.access_token = response['tenant_access_token']
        self.token_expiry = time.time() + response['expire'] - 300  # 提前5分钟过期
        return self.access_token
    
    def create_document(self, title, folder_token=None):
        """创建文档"""
        url = "https://open.feishu.cn/open-apis/docx/v1/documents"
        payload = {"title": title}
        if folder_token:
            payload["folder_token"] = folder_token
        
        return self._post(url, payload)
    
    def append_blocks(self, document_token, blocks):
        """追加块到文档"""
        url = f"https://open.feishu.cn/open-apis/docx/v1/documents/{document_token}/blocks"
        payload = {
            "index": -1,  # 追加到末尾
            "blocks": blocks
        }
        return self._post(url, payload)
    
    def get_document_blocks(self, document_token):
        """获取文档所有块"""
        url = f"https://open.feishu.cn/open-apis/docx/v1/documents/{document_token}/blocks"
        return self._get(url)
    
    def _request_token(self):
        """请求访问令牌"""
        url = "https://open.feishu.cn/open-apis/auth/v3/tenant_access_token/internal"
        payload = {
            "app_id": self.app_id,
            "app_secret": self.app_secret
        }
        response = requests.post(url, json=payload)
        response.raise_for_status()
        return response.json()
    
    def _post(self, url, payload):
        """发送POST请求"""
        headers = {
            "Authorization": f"Bearer {self.get_access_token()}",
            "Content-Type": "application/json"
        }
        response = requests.post(url, json=payload, headers=headers)
        response.raise_for_status()
        return response.json()
    
    def _get(self, url, params=None):
        """发送GET请求"""
        headers = {
            "Authorization": f"Bearer {self.get_access_token()}"
        }
        response = requests.get(url, headers=headers, params=params)
        response.raise_for_status()
        return response.json()
```

### 2. 文档块构建器模块

#### 功能
- 构建各种类型的飞书文档块
- 管理块样式和格式
- 处理块之间的层级关系
- 优化块结构以提高性能

#### 类设计
```python
class BlockBuilder:
    """文档块构建器"""
    
    BLOCK_TYPES = {
        "page": 1,
        "text": 2,
        "heading1": 3,
        "heading2": 4,
        "heading3": 5,
        "bullet": 12,
        "ordered": 13,
        "code": 14,
        "quote": 15,
        "divider": 21
    }
    
    def __init__(self):
        self.blocks = []
    
    def create_page_block(self, title):
        """创建页面块"""
        block = {
            "block_type": self.BLOCK_TYPES["page"],
            "page": {
                "elements": [{
                    "text_run": {
                        "content": title,
                        "text_element_style": self._default_style()
                    }
                }]
            }
        }
        self.blocks.append(block)
        return block
    
    def create_heading(self, level, text, styles=None):
        """创建标题块"""
        heading_type = f"heading{level}"
        if heading_type not in self.BLOCK_TYPES:
            raise ValueError(f"不支持的标题级别: {level}")
        
        block = {
            "block_type": self.BLOCK_TYPES[heading_type],
            heading_type: {
                "elements": [{
                    "text_run": {
                        "content": text,
                        "text_element_style": self._apply_styles(self._default_style(), styles)
                    }
                }]
            }
        }
        self.blocks.append(block)
        return block
    
    def create_text_block(self, text, styles=None):
        """创建文本块"""
        block = {
            "block_type": self.BLOCK_TYPES["text"],
            "text": {
                "elements": [{
                    "text_run": {
                        "content": text,
                        "text_element_style": self._apply_styles(self._default_style(), styles)
                    }
                }]
            }
        }
        self.blocks.append(block)
        return block
    
    def create_bullet_block(self, text, styles=None, indent=0):
        """创建无序列表块"""
        block = {
            "block_type": self.BLOCK_TYPES["bullet"],
            "bullet": {
                "elements": [{
                    "text_run": {
                        "content": text,
                        "text_element_style": self._apply_styles(self._default_style(), styles)
                    }
                }],
                "style": {
                    "indent": indent
                }
            }
        }
        self.blocks.append(block)
        return block
    
    def create_code_block(self, code, language="plaintext"):
        """创建代码块"""
        block = {
            "block_type": self.BLOCK_TYPES["code"],
            "code": {
                "elements": [{
                    "text_run": {
                        "content": code,
                        "text_element_style": {
                            "inline_code": True
                        }
                    }
                }],
                "style": {
                    "language": language
                }
            }
        }
        self.blocks.append(block)
        return block
    
    def create_quote_block(self, text, styles=None):
        """创建引用块"""
        block = {
            "block_type": self.BLOCK_TYPES["quote"],
            "quote": {
                "elements": [{
                    "text_run": {
                        "content": text,
                        "text_element_style": self._apply_styles(self._default_style(), styles)
                    }
                }]
            }
        }
        self.blocks.append(block)
        return block
    
    def create_divider_block(self):
        """创建分隔线块"""
        block = {
            "block_type": self.BLOCK_TYPES["divider"],
            "divider": {}
        }
        self.blocks.append(block)
        return block
    
    def _default_style(self):
        """默认文本样式"""
        return {
            "bold": False,
            "italic": False,
            "strikethrough": False,
            "underline": False,
            "inline_code": False
        }
    
    def _apply_styles(self, base_style, styles):
        """应用样式"""
        if not styles:
            return base_style
        
        style_mapping = {
            "bold": "bold",
            "italic": "italic",
            "strikethrough": "strikethrough",
            "underline": "underline",
            "code": "inline_code"
        }
        
        result_style = base_style.copy()
        for style_name, style_value in styles.items():
            if style_name in style_mapping:
                result_style[style_mapping[style_name]] = style_value
        
        return result_style
    
    def get_blocks(self):
        """获取所有块"""
        return self.blocks
    
    def clear(self):
        """清空块列表"""
        self.blocks = []
```

### 3. Markdown转换器模块

#### 功能
- 解析Markdown语法
- 映射到飞书文档块
- 处理样式转换
- 优化文档结构

#### 类设计
```python
class MarkdownConverter:
    """Markdown到飞书文档转换器"""
    
    def __init__(self):
        self.block_builder = BlockBuilder()
        self.current_list_type = None
        self.list_indent = 0
    
    def convert(self, markdown_text, title="Converted Document"):
        """转换Markdown文本"""
        lines = markdown_text.split('\n')
        self.block_builder.clear()
        
        # 创建页面标题
        self.block_builder.create_page_block(title)
        
        for line in lines:
            self._process_line(line)
        
        return self.block_builder.get_blocks()
    
    def _process_line(self, line):
        """处理单行Markdown"""
        line = line.rstrip()
        
        if not line:
            return
        
        # 检查标题
        heading_match = self._match_heading(line)
        if heading_match:
            level, text = heading_match
            self.block_builder.create_heading(level, text)
            self.current_list_type = None
            self.list_indent = 0
            return
        
        # 检查列表
        list_match = self._match_list(line)
        if list_match:
            list_type, indent, text = list_match
            self._handle_list(list_type, indent, text)
            return
        
        # 检查代码块
        if line.startswith('```'):
            # 简化处理：跳过代码块解析
            return
        
        # 检查引用
        if line.startswith('> '):
            text = line[2:].strip()
            self.block_builder.create_quote_block(text)
            self.current_list_type = None
            self.list_indent = 0
            return
        
        # 检查分隔线
        if line.replace('-', '').replace(' ', '') == '' and len(line) >= 3:
            self.block_builder.create_divider_block()
            self.current_list_type = None
            self.list_indent = 0
            return
        
        # 普通文本
        text, styles = self._parse_inline_styles(line)
        self.block_builder.create_text_block(text, styles)
        self.current_list_type = None
        self.list_indent = 0
    
    def _match_heading(self, line):
        """匹配标题"""
        if line.startswith('### '):
            return (3, line[4:].strip())
        elif line.startswith('## '):
            return (2, line[3:].strip())
        elif line.startswith('# '):
            return (1, line[2:].strip())
        return None
    
    def _match_list(self, line):
        """匹配列表"""
        line = line.rstrip()
        
        # 计算缩进
        indent = 0
        while indent < len(line) and line[indent] == ' ':
            indent += 1
        
        # 无序列表
        if line.startswith('- ', indent):
            text = line[indent+2:].strip()
            return ('bullet', indent // 2, text)
        
        # 有序列表
        import re
        ordered_match = re.match(r'(\d+)\.\s+(.+)', line[indent:])
        if ordered_match:
            text = ordered_match.group(2)
            return ('ordered', indent // 2, text)
        
        return None
    
    def _handle_list(self, list_type, indent, text):
        """处理列表项"""
        if list_type == 'bullet':
            text, styles = self._parse_inline_styles(text)
            self.block_builder.create_bullet_block(text, styles, indent)
        # 有序列表暂时按无序列表处理（简化）
        elif list_type == 'ordered':
            text, styles = self._parse_inline_styles(text)
            self.block_builder.create_bullet_block(text, styles, indent)
    
    def _parse_inline_styles(self, text):
        """解析行内样式"""
        styles = {}
        
        # 简化处理：只检测粗体和斜体
        if '**' in text:
            styles['bold'] = True
            text = text.replace('**', '')
        
        if '*' in text and not text.startswith('*') and not text.endswith('*'):
            styles['italic'] = True
            text = text.replace('*', '')
        
        if '`' in text:
            styles['code'] = True
            text = text.replace('`', '')
        
        return text, styles
```

### 4. 文档创建专家模块

#### 功能
- 智能解析用户需求
- 选择合适模板
- 生成结构化内容
- 优化文档布局

#### 类设计
```python
class DocumentCreator:
    """文档创建专家"""
    
    def __init__(self, api_client):
        self.api_client = api_client
        self.templates = self._load_templates()
    
    def create_document(self, doc_type, params, folder_token=None):
        """创建文档"""
        template = self._select_template(doc_type)
        title = self._generate_title(doc_type, params)
        
        # 创建空文档
        response = self.api_client.create_document(title, folder_token)
        document_token = response['data']['document']['document_id']
        
        # 根据模板生成内容
        blocks = self._generate_content(template, params)
        
        # 分批添加块（避免单次请求过大）
        batch_size = 20
        for i in range(0, len(blocks), batch_size):
            batch = blocks[i:i+batch_size]
            self.api_client.append_blocks(document_token, batch)
        
        return {
            'document_id': document_token,
            'title': title,
            'url': f'https://feishu.cn/docx/{document_token}',
            'blocks_added': len(blocks)
        }
    
    def _load_templates(self):
        """加载文档模板"""
        return {
            'meeting_minutes': {
                'name': '会议纪要',
                'sections': [
                    {'type': 'heading1', 'content': '会议纪要'},
                    {'type': 'divider'},
                    {'type': 'heading2', 'content': '会议基本信息'},
                    {'type': 'bullet', 'content': '会议主题: {topic}'},
                    {'type': 'bullet', 'content': '会议时间: {time}'},
                    {'type': 'bullet', 'content': '参会人员: {participants}'},
                    {'type': 'bullet', 'content': '会议地点: {location}'},
                    {'type': 'divider'},
                    {'type': 'heading2', 'content': '会议议程'},
                    {'type': 'ordered', 'content': '{agenda_item1}'},
                    {'type': 'ordered', 'content': '{agenda_item2}'},
                    {'type': 'divider'},
                    {'type': 'heading2', 'content': '会议决议'},
                    {'type': 'bullet', 'content': '{resolution1}'},
                    {'type': 'bullet', 'content': '{resolution2}'},
                    {'type': 'divider'},
                    {'type': 'heading2', 'content': '下一步行动'},
                    {'type': 'bullet', 'content': '{action1} - 负责人: {owner1} - 截止时间: {deadline1}'},
                    {'type': 'bullet', 'content': '{action2} - 负责人: {owner2} - 截止时间: {deadline2}'}
                ]
            },
            'project_proposal': {
                'name': '项目提案',
                'sections': [
                    {'type': 'heading1', 'content': '项目提案: {project_name}'},
                    {'type': 'divider'},
                    {'type': 'heading2', 'content': '项目概述'},
                    {'type': 'text', 'content': '{project_overview}'},
                    {'type': 'divider'},
                    {'type': 'heading2', 'content': '项目目标'},
                    {'type': 'bullet', 'content': '{goal1}'},
                    {'type': 'bullet', 'content': '{goal2}'},
                    {'type': 'bullet', 'content': '{goal3}'},
                    {'type': 'divider'},
                    {'type': 'heading2', 'content': '项目范围'},
                    {'type': 'text', 'content': '{project
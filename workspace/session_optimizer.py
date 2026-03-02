#!/usr/bin/env python3
"""
Session对话优化系统
减少来回等待，提高沟通效率
"""

import json
import time
from datetime import datetime
from pathlib import Path
import logging

# 配置日志
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('/tmp/session_optimizer.log'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger('session_optimizer')

class SessionOptimizer:
    """Session对话优化器"""
    
    def __init__(self):
        self.workspace = Path.home() / ".openclaw" / "workspace"
        self.session_file = self.workspace / "active_session.json"
        self.context_file = self.workspace / "compressed_context.json"
        
        # 初始化session
        self._init_session()
        
        logger.info("Session优化器初始化完成")
    
    def _init_session(self):
        """初始化session"""
        if not self.session_file.exists():
            initial_session = {
                'session_id': f"session_{datetime.now().strftime('%Y%m%d_%H%M%S')}",
                'start_time': datetime.now().isoformat(),
                'message_count': 0,
                'context_size': 0,
                'compression_rate': 0,
                'active': True,
                'messages': []
            }
            self._save_session(initial_session)
    
    def _save_session(self, session_data: dict):
        """保存session数据"""
        with open(self.session_file, 'w', encoding='utf-8') as f:
            json.dump(session_data, f, indent=2, ensure_ascii=False)
    
    def get_session(self) -> dict:
        """获取当前session"""
        try:
            with open(self.session_file, 'r', encoding='utf-8') as f:
                return json.load(f)
        except:
            return {'active': False, 'messages': []}
    
    def add_message(self, role: str, content: str, compress: bool = True):
        """添加消息到session"""
        session = self.get_session()
        
        message = {
            'id': f"msg_{session['message_count'] + 1}",
            'role': role,
            'content': content,
            'timestamp': datetime.now().isoformat(),
            'size': len(content.encode('utf-8'))
        }
        
        # 添加到消息列表
        session['messages'].append(message)
        session['message_count'] += 1
        session['context_size'] += message['size']
        
        # 如果需要压缩
        if compress and len(session['messages']) > 10:
            self._compress_context(session)
        
        self._save_session(session)
        
        logger.info(f"添加消息: {role} ({message['size']} bytes)")
        return message['id']
    
    def _compress_context(self, session: dict):
        """压缩上下文"""
        if len(session['messages']) <= 5:
            return
        
        # 保留最近的5条消息
        recent_messages = session['messages'][-5:]
        
        # 压缩旧消息
        old_messages = session['messages'][:-5]
        if old_messages:
            compressed = self._summarize_messages(old_messages)
            
            # 创建压缩摘要
            summary_message = {
                'id': f"summary_{datetime.now().strftime('%H%M%S')}",
                'role': 'system',
                'content': f"【上下文摘要】{compressed}",
                'timestamp': datetime.now().isoformat(),
                'size': len(compressed.encode('utf-8')),
                'compressed': True,
                'original_count': len(old_messages)
            }
            
            # 更新消息列表：摘要 + 最近消息
            session['messages'] = [summary_message] + recent_messages
            
            # 计算压缩率
            original_size = sum(msg['size'] for msg in old_messages)
            compressed_size = summary_message['size']
            if original_size > 0:
                compression_rate = 1 - (compressed_size / original_size)
                session['compression_rate'] = round(compression_rate * 100, 1)
            
            logger.info(f"上下文压缩: {len(old_messages)}条 → 1条摘要 (压缩率: {session['compression_rate']}%)")
    
    def _summarize_messages(self, messages: list) -> str:
        """摘要消息"""
        # 简单实现：提取关键信息
        summary_parts = []
        
        for msg in messages:
            if msg['role'] == 'user':
                # 提取用户指令的关键词
                content = msg['content']
                if len(content) > 100:
                    content = content[:100] + "..."
                summary_parts.append(f"用户: {content}")
            elif msg['role'] == 'assistant':
                # 提取助手响应的行动
                content = msg['content']
                if "✅" in content or "❌" in content:
                    lines = content.split('\n')
                    for line in lines:
                        if "✅" in line or "❌" in line:
                            summary_parts.append(line.strip())
                            break
        
        return " | ".join(summary_parts[:3])  # 最多3个关键点
    
    def get_compressed_context(self, max_messages: int = 10) -> list:
        """获取压缩后的上下文"""
        session = self.get_session()
        
        if len(session['messages']) <= max_messages:
            return session['messages']
        
        # 压缩并返回
        self._compress_context(session)
        self._save_session(session)
        
        return session['messages']
    
    def end_session(self, summary: str = ""):
        """结束session"""
        session = self.get_session()
        
        session.update({
            'active': False,
            'end_time': datetime.now().isoformat(),
            'duration_seconds': int((datetime.now() - datetime.fromisoformat(session['start_time'])).total_seconds()),
            'final_summary': summary or f"Session完成，共{session['message_count']}条消息"
        })
        
        # 保存到历史
        self._archive_session(session)
        
        # 重置当前session
        self._init_session()
        
        logger.info(f"Session结束: {session['final_summary']}")
        return session
    
    def _archive_session(self, session: dict):
        """归档session"""
        archive_dir = self.workspace / "session_archive"
        archive_dir.mkdir(exist_ok=True)
        
        archive_file = archive_dir / f"{session['session_id']}.json"
        with open(archive_file, 'w', encoding='utf-8') as f:
            json.dump(session, f, indent=2, ensure_ascii=False)
        
        logger.info(f"Session已归档: {archive_file}")
    
    def generate_session_report(self) -> dict:
        """生成session报告"""
        session = self.get_session()
        
        report = {
            'timestamp': datetime.now().isoformat(),
            'session_id': session.get('session_id'),
            'active': session.get('active', False),
            'message_count': session.get('message_count', 0),
            'context_size_kb': round(session.get('context_size', 0) / 1024, 2),
            'compression_rate': session.get('compression_rate', 0),
            'efficiency': self._calculate_efficiency(session),
            'recommendations': self._generate_recommendations(session)
        }
        
        # 保存报告
        report_file = self.workspace / "session_report.json"
        with open(report_file, 'w', encoding='utf-8') as f:
            json.dump(report, f, indent=2, ensure_ascii=False)
        
        return report
    
    def _calculate_efficiency(self, session: dict) -> float:
        """计算沟通效率"""
        if session['message_count'] == 0:
            return 100.0
        
        # 简单效率计算：压缩率越高，效率越高
        compression_bonus = session.get('compression_rate', 0) * 0.5
        message_efficiency = min(100, 100 - (session['message_count'] * 2))  # 消息越多效率越低
        
        return round(min(100, message_efficiency + compression_bonus), 1)
    
    def _generate_recommendations(self, session: dict) -> list:
        """生成优化建议"""
        recommendations = []
        
        if session['message_count'] > 20:
            recommendations.append("消息数量较多，建议开启自动压缩")
        
        if session.get('context_size', 0) > 50 * 1024:  # 50KB
            recommendations.append("上下文较大，建议使用摘要功能")
        
        if session['message_count'] > 0 and len(session.get('messages', [])) > 10:
            recommendations.append("建议定期清理旧消息，保留关键上下文")
        
        if not recommendations:
            recommendations.append("沟通效率良好，继续保持")
        
        return recommendations

# 全局实例
session_optimizer = SessionOptimizer()

# 装饰器：自动管理session
def with_session_optimization(func):
    """session优化装饰器"""
    def wrapper(*args, **kwargs):
        # 记录开始
        start_time = time.time()
        
        # 执行函数
        result = func(*args, **kwargs)
        
        # 记录结束
        elapsed = time.time() - start_time
        
        # 添加到session
        if 'message' in kwargs:
            session_optimizer.add_message('assistant', kwargs['message'])
        
        return result
    return wrapper

if __name__ == "__main__":
    import sys
    
    optimizer = SessionOptimizer()
    
    if len(sys.argv) > 1:
        if sys.argv[1] == 'add':
            if len(sys.argv) >= 4:
                role = sys.argv[2]
                content = sys.argv[3]
                msg_id = optimizer.add_message(role, content)
                print(f"消息添加成功: {msg_id}")
            else:
                print("用法: python session_optimizer.py add <role> <content>")
        
        elif sys.argv[1] == 'report':
            report = optimizer.generate_session_report()
            print(json.dumps(report, indent=2, ensure_ascii=False))
        
        elif sys.argv[1] == 'end':
            summary = sys.argv[2] if len(sys.argv) > 2 else ""
            session = optimizer.end_session(summary)
            print(f"Session结束: {session['final_summary']}")
        
        elif sys.argv[1] == 'compress':
            context = optimizer.get_compressed_context()
            print(f"压缩后上下文: {len(context)}条消息")
            for msg in context:
                print(f"  [{msg['role']}] {msg['content'][:50]}...")
        
        else:
            print("可用命令: add, report, end, compress")
    else:
        # 显示当前session状态
        session = optimizer.get_session()
        print(f"当前Session: {session.get('session_id', '无')}")
        print(f"活跃: {session.get('active', False)}")
        print(f"消息数量: {session.get('message_count', 0)}")
        print(f"上下文大小: {session.get('context_size', 0)} bytes")
        print(f"压缩率: {session.get('compression_rate', 0)}%")
        print(f"消息列表: {len(session.get('messages', []))}条")
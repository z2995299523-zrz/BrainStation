import { useState, useRef, useEffect } from 'react';
import { useLearnStore } from '../../stores/learnStore';
import { api } from '../../api/client';
import type { AIMessage } from '../../types';
import {
  Sheet,
  SheetContent,
  SheetHeader,
  SheetTitle,
} from '../ui/sheet';
import { Card, CardContent } from '../ui/card';
import { Button } from '../ui/button';
import { Input } from '../ui/input';

const PRESETS = [
  { emoji: '🤔', label: '换个方式讲' },
  { emoji: '📝', label: '再出一道题' },
  { emoji: '❌', label: '我错在哪' },
  { emoji: '📋', label: '总结本章' },
];

export default function AISidebar() {
  const aiOpen = useLearnStore((s) => s.aiOpen);
  const aiMessages = useLearnStore((s) => s.aiMessages);
  const aiStreaming = useLearnStore((s) => s.aiStreaming);
  const aiPosition = useLearnStore((s) => s.aiPosition);
  const chapterSlug = useLearnStore((s) => s.chapterSlug);
  const chapterTitle = useLearnStore((s) => s.chapterTitle);
  const currentStage = useLearnStore((s) => s.currentStage);
  const chatSessions = useLearnStore((s) => s.chatSessions);
  const activeSessionId = useLearnStore((s) => s.activeSessionId);
  const closeAI = useLearnStore((s) => s.closeAI);
  const addAIMessage = useLearnStore((s) => s.addAIMessage);
  const setAIStreaming = useLearnStore((s) => s.setAIStreaming);
  const loadSessions = useLearnStore((s) => s.loadSessions);
  const createSession = useLearnStore((s) => s.createSession);
  const switchSession = useLearnStore((s) => s.switchSession);
  const deleteSession = useLearnStore((s) => s.deleteSession);
  const syncMessages = useLearnStore((s) => s.syncMessages);

  const [inputValue, setInputValue] = useState('');
  const [showSessionMenu, setShowSessionMenu] = useState(false);
  const messagesEndRef = useRef<HTMLDivElement>(null);
  const inputRef = useRef<HTMLInputElement>(null);
  const abortRef = useRef<AbortController | null>(null);

  // Load sessions when sidebar opens or chapter changes
  useEffect(() => {
    if (aiOpen && chapterSlug) {
      loadSessions();
    }
  }, [aiOpen, chapterSlug, loadSessions]);

  // Auto-scroll to bottom on new messages
  useEffect(() => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  }, [aiMessages]);

  // Focus input when sidebar opens
  useEffect(() => {
    if (aiOpen) {
      setTimeout(() => inputRef.current?.focus(), 300);
    }
  }, [aiOpen]);

  const ensureSession = async (): Promise<number | null> => {
    if (activeSessionId) return activeSessionId;
    try {
      const id = await createSession();
      return id;
    } catch {
      return null;
    }
  };

  const sendMessage = async (text: string) => {
    if (!text.trim() || !chapterSlug || aiStreaming) return;

    const sid = await ensureSession();
    if (!sid) return;

    const userMsg: AIMessage = { role: 'user', content: text };
    addAIMessage(userMsg);
    setInputValue('');

    const aiMsg: AIMessage = { role: 'assistant', content: '' };
    addAIMessage(aiMsg);
    setAIStreaming(true);

    const history = useLearnStore.getState().aiMessages
      .filter(m => m.content && (m.role === 'user' || m.role === 'assistant'))
      .slice(0, -2)
      .slice(-20);

    abortRef.current = api.askAI(
      {
        chapter_slug: chapterSlug,
        current_stage: currentStage,
        current_position: aiPosition,
        question: text,
        history,
      },
      (chunk) => {
        const store = useLearnStore.getState();
        const msgs = [...store.aiMessages];
        const last = msgs[msgs.length - 1];
        if (last && last.role === 'assistant') {
          last.content += chunk;
          useLearnStore.setState({ aiMessages: msgs });
        }
      },
      () => {
        setAIStreaming(false);
        abortRef.current = null;
        syncMessages();
      },
      (err) => {
        const store = useLearnStore.getState();
        const msgs = [...store.aiMessages];
        const last = msgs[msgs.length - 1];
        if (last && last.role === 'assistant') {
          last.content = `❌ 出错了：${err.message}`;
          useLearnStore.setState({ aiMessages: msgs });
        }
        setAIStreaming(false);
        abortRef.current = null;
        syncMessages();
      },
    );
  };

  const handlePreset = (preset: string) => {
    sendMessage(preset);
  };

  const handleKeyDown = (e: React.KeyboardEvent) => {
    if (e.key === 'Enter' && !e.shiftKey) {
      e.preventDefault();
      sendMessage(inputValue);
    }
  };

  const handleNewSession = async () => {
    setShowSessionMenu(false);
    await createSession();
  };

  const handleSwitchSession = async (id: number) => {
    setShowSessionMenu(false);
    if (id === activeSessionId) return;
    await switchSession(id);
  };

  const handleDeleteSession = async (id: number, e: React.MouseEvent) => {
    e.stopPropagation();
    if (!confirm('确定删除这个对话吗？')) return;
    await deleteSession(id);
  };

  const activeSession = chatSessions.find(s => s.id === activeSessionId);

  return (
    <Sheet open={aiOpen} onOpenChange={(open) => { if (!open) closeAI(); }}>
      <SheetContent side="right" className="w-[400px] max-w-[90vw] sm:max-w-[400px] p-0 flex flex-col">
        {/* Header */}
        <SheetHeader className="px-4 py-3 border-b shrink-0 space-y-1">
          <SheetTitle className="text-sm flex items-center gap-2">
            💬 AI 导师
          </SheetTitle>
          <p className="text-xs text-muted-foreground truncate">
            {chapterTitle || '加载中...'}
          </p>

          {/* Session selector */}
          <div className="relative mt-1">
            <Button
              variant="ghost"
              size="sm"
              onClick={() => setShowSessionMenu(!showSessionMenu)}
              className="w-full justify-between text-xs h-7"
            >
              <span className="truncate flex-1 text-left">
                {activeSession ? activeSession.title : '新对话'}
              </span>
              <span className="text-muted-foreground shrink-0">▾</span>
            </Button>

            {showSessionMenu && (
              <div className="absolute top-full left-0 right-0 mt-1 bg-card border rounded-lg shadow-lg z-10 max-h-48 overflow-y-auto">
                {chatSessions.map((s) => (
                  <div
                    key={s.id}
                    onClick={() => handleSwitchSession(s.id)}
                    className={`flex items-center justify-between px-3 py-2 text-xs cursor-pointer hover:bg-accent ${
                      s.id === activeSessionId ? 'bg-accent' : ''
                    }`}
                  >
                    <span className="truncate flex-1">{s.title}</span>
                    <Button
                      variant="ghost"
                      size="sm"
                      onClick={(e) => handleDeleteSession(s.id, e as unknown as React.MouseEvent)}
                      className="text-muted-foreground hover:text-destructive h-6 w-6 p-0 ml-2 shrink-0"
                    >
                      ✕
                    </Button>
                  </div>
                ))}
                <div
                  onClick={handleNewSession}
                  className="px-3 py-2 text-xs text-primary cursor-pointer hover:bg-accent border-t"
                >
                  ＋ 新建对话
                </div>
              </div>
            )}
          </div>
        </SheetHeader>

        {/* Messages */}
        <div className="flex-1 overflow-y-auto px-4 py-3 space-y-3">
          {aiMessages.length === 0 && (
            <div className="text-center text-muted-foreground py-8">
              <p className="mb-3 text-sm">
                👋 你好！有什么不懂的可以问我：
              </p>
            </div>
          )}

          {aiMessages.map((msg, i) => (
            <div
              key={i}
              className={`flex ${msg.role === 'user' ? 'justify-end' : 'justify-start'}`}
            >
              <Card className={`max-w-[85%] ${
                msg.role === 'user'
                  ? 'bg-primary text-primary-foreground border-0'
                  : ''
              }`}>
                <CardContent className="p-3 text-sm leading-relaxed whitespace-pre-wrap">
                  {msg.content || (aiStreaming && i === aiMessages.length - 1 ? '...' : '')}
                </CardContent>
              </Card>
            </div>
          ))}
          <div ref={messagesEndRef} />
        </div>

        {/* Presets */}
        <div className="px-4 py-2 border-t shrink-0">
          <div className="flex flex-wrap gap-2">
            {PRESETS.map((p) => (
              <Button
                key={p.label}
                variant="outline"
                size="sm"
                onClick={() => handlePreset(p.label)}
                disabled={aiStreaming}
                className="text-xs rounded-full"
              >
                {p.emoji} {p.label}
              </Button>
            ))}
          </div>
        </div>

        {/* Input */}
        <div className="px-4 py-3 border-t shrink-0">
          <div className="flex gap-2">
            <Input
              ref={inputRef}
              value={inputValue}
              onChange={(e) => setInputValue(e.target.value)}
              onKeyDown={handleKeyDown}
              placeholder="输入你的问题..."
              disabled={aiStreaming}
              className="flex-1 text-sm"
            />
            <Button
              onClick={() => sendMessage(inputValue)}
              disabled={aiStreaming || !inputValue.trim()}
              size="sm"
            >
              发送
            </Button>
          </div>
        </div>
      </SheetContent>
    </Sheet>
  );
}

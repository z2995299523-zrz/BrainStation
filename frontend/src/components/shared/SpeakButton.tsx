import { useState, useCallback, useRef } from 'react';

interface SpeakButtonProps {
  text: string;
  label?: string;
  size?: 'sm' | 'md' | 'lg';
  variant?: 'phoneme' | 'word';
  className?: string;
}

const ICONS: Record<string, { idle: string; playing: string }> = {
  phoneme: { idle: '🗣️', playing: '🔊' },   // 音素本身
  word:    { idle: '📢', playing: '🔊' },   // 完整单词
};

export default function SpeakButton({ text, label, size = 'sm', variant = 'word', className = '' }: SpeakButtonProps) {
  const [playing, setPlaying] = useState(false);
  const timerRef = useRef<ReturnType<typeof setTimeout> | null>(null);

  const icons = ICONS[variant] || ICONS.word;

  const sizeClasses = {
    sm: 'w-7 h-7 text-xs',
    md: 'w-9 h-9 text-sm',
    lg: 'w-11 h-11 text-base',
  };

  const speak = useCallback(() => {
    if (!('speechSynthesis' in window)) return;
    window.speechSynthesis.cancel();

    const utterance = new SpeechSynthesisUtterance(text);
    utterance.lang = 'en-US';
    // 音素用更慢的速度 + 稍低音调，让细节更清晰
    utterance.rate = variant === 'phoneme' ? 0.5 : 0.85;
    utterance.pitch = variant === 'phoneme' ? 0.85 : 1;

    setPlaying(true);
    if (timerRef.current) clearTimeout(timerRef.current);
    // 音素播放时间更长（重复发音）
    const timeout = variant === 'phoneme' ? 15000 : 10000;
    timerRef.current = setTimeout(() => setPlaying(false), timeout);

    utterance.onend = () => {
      setPlaying(false);
      if (timerRef.current) clearTimeout(timerRef.current);
    };
    utterance.onerror = () => {
      setPlaying(false);
      if (timerRef.current) clearTimeout(timerRef.current);
    };

    window.speechSynthesis.speak(utterance);
  }, [text]);

  return (
    <button
      onClick={speak}
      disabled={playing}
      title={label || `朗读: ${text}`}
      className={`inline-flex items-center justify-center rounded-full transition-all
        ${sizeClasses[size]}
        ${playing
          ? 'bg-green-500 text-white scale-110 shadow-md'
          : variant === 'phoneme'
            ? 'bg-amber-50 dark:bg-amber-900/20 text-amber-600 dark:text-amber-400 hover:bg-amber-100 hover:text-amber-700'
            : 'bg-gray-100 dark:bg-gray-800 text-gray-600 dark:text-gray-400 hover:bg-indigo-100 hover:text-indigo-600 dark:hover:bg-indigo-900 dark:hover:text-indigo-300'
        }
        ${className}
      `}
    >
      <span className={playing ? 'animate-pulse' : ''}>
        {playing ? icons.playing : icons.idle}
      </span>
    </button>
  );
}

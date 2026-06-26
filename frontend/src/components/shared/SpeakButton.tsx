import { useState, useRef, useCallback } from 'react';

interface SpeakButtonProps {
  audioSrc?: string;         // 预录音频文件路径（优先使用）
  text?: string;             // 文字，用浏览器 TTS 朗读（fallback）
  label?: string;
  size?: 'sm' | 'md' | 'lg';
  variant?: 'phoneme' | 'word';
  className?: string;
}

const ICONS: Record<string, { idle: string; playing: string }> = {
  phoneme: { idle: '🗣️', playing: '🔊' },
  word:    { idle: '📢', playing: '🔊' },
};

export default function SpeakButton({ audioSrc, text, label, size = 'sm', variant = 'word', className = '' }: SpeakButtonProps) {
  const [playing, setPlaying] = useState(false);
  const audioRef = useRef<HTMLAudioElement | null>(null);

  const icons = ICONS[variant] || ICONS.word;

  const sizeClasses = {
    sm: 'w-7 h-7 text-xs',
    md: 'w-9 h-9 text-sm',
    lg: 'w-11 h-11 text-base',
  };

  const play = useCallback(() => {
    // 停止之前的播放
    if (audioRef.current) {
      audioRef.current.pause();
      audioRef.current.currentTime = 0;
    }
    window.speechSynthesis?.cancel();

    setPlaying(true);

    if (audioSrc) {
      // 优先用预录音频文件
      const audio = new Audio(audioSrc);
      audioRef.current = audio;

      audio.onended = () => { setPlaying(false); audioRef.current = null; };
      audio.onerror = () => { setPlaying(false); audioRef.current = null; };

      audio.play().catch(() => {
        // 文件播放失败，尝试 TTS fallback
        if (text) speakWithTTS();
        else setPlaying(false);
      });
    } else if (text) {
      speakWithTTS();
    } else {
      setPlaying(false);
    }
  }, [audioSrc, text]);

  const speakWithTTS = useCallback(() => {
    if (!('speechSynthesis' in window)) { setPlaying(false); return; }

    const utterance = new SpeechSynthesisUtterance(text);
    utterance.lang = 'en-US';
    utterance.rate = variant === 'phoneme' ? 0.6 : 0.9;
    utterance.pitch = variant === 'phoneme' ? 0.9 : 1;

    utterance.onend = () => setPlaying(false);
    utterance.onerror = () => setPlaying(false);

    // 超时保护
    setTimeout(() => setPlaying(false), 10000);

    window.speechSynthesis.speak(utterance);
  }, [text, variant]);

  return (
    <button
      onClick={play}
      disabled={playing}
      title={label || (audioSrc ? '播放预录音频' : `朗读: ${text}`)}
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

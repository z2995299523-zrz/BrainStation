import { useEffect, useState } from 'react';

interface TimerProps {
  startTime: number | null;
  className?: string;
}

function formatTime(totalSeconds: number): string {
  const min = Math.floor(totalSeconds / 60);
  const sec = totalSeconds % 60;
  return `${min.toString().padStart(2, '0')}:${sec.toString().padStart(2, '0')}`;
}

export default function Timer({ startTime, className = '' }: TimerProps) {
  const [elapsed, setElapsed] = useState(0);

  useEffect(() => {
    if (!startTime) return;
    const id = setInterval(() => {
      setElapsed(Math.floor((Date.now() - startTime) / 1000));
    }, 1000);
    return () => clearInterval(id);
  }, [startTime]);

  return (
    <span className={`font-mono text-sm text-gray-500 ${className}`}>
      ⏱ {formatTime(elapsed)}
    </span>
  );
}

interface SubjectBadgeProps {
  subject: 'math' | 'english';
  className?: string;
}

export default function SubjectBadge({ subject, className = '' }: SubjectBadgeProps) {
  const isMath = subject === 'math';
  return (
    <span
      className={`inline-flex items-center rounded-full px-2.5 py-0.5 text-xs font-medium ${className} ${
        isMath
          ? 'bg-blue-100 text-blue-800 dark:bg-blue-900 dark:text-blue-200'
          : 'bg-green-100 text-green-800 dark:bg-green-900 dark:text-green-200'
      }`}
    >
      {isMath ? '🧮 数学' : '📖 英语'}
    </span>
  );
}

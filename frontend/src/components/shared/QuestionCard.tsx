import { useState } from 'react';
import type { Question } from '../../types';
import SubjectBadge from './SubjectBadge';

interface QuestionCardProps {
  question: Question;
  onAnswer: (answer: unknown) => void;
  onConfidence: (level: number) => void;
  showFeedback?: boolean;
  feedback?: { is_correct: boolean | null; explanation: string } | null;
}

export default function QuestionCard({
  question,
  onAnswer,
  onConfidence,
  showFeedback = false,
  feedback = null,
}: QuestionCardProps) {
  const [choice, setChoice] = useState<number | null>(null);
  const [fillText, setFillText] = useState('');
  const [openText, setOpenText] = useState('');
  const [confidence, setConfidence] = useState(3);
  const [submitted, setSubmitted] = useState(false);

  const handleSubmit = () => {
    let answer: unknown;
    if (question.q_type === 'choice') answer = { choice };
    else if (question.q_type === 'fill') answer = fillText;
    else answer = openText;
    onAnswer(answer);
    onConfidence(confidence);
    setSubmitted(true);
  };

  const canSubmit = () => {
    if (question.q_type === 'choice') return choice !== null;
    if (question.q_type === 'fill') return fillText.trim().length > 0;
    return true; // open always submittable
  };

  return (
    <div className="bg-white dark:bg-gray-900 rounded-xl p-6 border border-gray-200 dark:border-gray-800 space-y-4">
      {/* Header: subject badge + layer + difficulty */}
      <div className="flex items-center gap-2 flex-wrap">
        <SubjectBadge subject={question.subject} />
        <span className="text-xs text-gray-400">
          {question.layer === 'operation' ? '操作层' : question.layer === 'understand' ? '理解层' : '连接层'}
        </span>
        <span className="text-xs text-gray-400">
          {'★'.repeat(question.difficulty)}{'☆'.repeat(5 - question.difficulty)}
        </span>
      </div>

      {/* Stem */}
      <div className="text-gray-800 dark:text-gray-200 text-lg leading-relaxed whitespace-pre-wrap">
        {question.content.stem}
      </div>

      {/* Input based on q_type */}
      {!submitted && (
        <div className="space-y-3">
          {question.q_type === 'choice' && question.content.options && (
            <div className="space-y-2">
              {question.content.options.map((opt, i) => (
                <button
                  key={i}
                  onClick={() => setChoice(i)}
                  className={`w-full text-left px-4 py-3 rounded-lg border transition-colors ${
                    choice === i
                      ? 'border-indigo-500 bg-indigo-50 dark:bg-indigo-900/30'
                      : 'border-gray-200 dark:border-gray-700 hover:border-gray-300'
                  }`}
                >
                  <span className="font-medium mr-2">{String.fromCharCode(65 + i)}.</span>
                  {opt}
                </button>
              ))}
            </div>
          )}

          {question.q_type === 'fill' && (
            <input
              type="text"
              value={fillText}
              onChange={(e) => setFillText(e.target.value)}
              placeholder="在此输入答案..."
              className="w-full px-4 py-3 rounded-lg border border-gray-300 dark:border-gray-700 bg-white dark:bg-gray-800"
            />
          )}

          {question.q_type === 'open' && (
            <textarea
              value={openText}
              onChange={(e) => setOpenText(e.target.value)}
              placeholder="在此输入你的想法..."
              rows={3}
              className="w-full px-4 py-3 rounded-lg border border-gray-300 dark:border-gray-700 bg-white dark:bg-gray-800"
            />
          )}

          {/* Confidence slider */}
          <div className="flex items-center gap-3">
            <span className="text-sm text-gray-500">确定程度:</span>
            {[1, 2, 3, 4, 5].map((level) => (
              <button
                key={level}
                onClick={() => setConfidence(level)}
                className={`w-8 h-8 rounded-full text-sm font-medium transition-colors ${
                  confidence >= level
                    ? 'bg-indigo-500 text-white'
                    : 'bg-gray-200 dark:bg-gray-700 text-gray-500'
                }`}
              >
                {level}
              </button>
            ))}
          </div>

          <button
            onClick={handleSubmit}
            disabled={!canSubmit()}
            className="px-6 py-2 bg-indigo-600 text-white rounded-lg hover:bg-indigo-700 disabled:opacity-50 disabled:cursor-not-allowed transition-colors"
          >
            提交答案
          </button>
        </div>
      )}

      {/* Feedback */}
      {showFeedback && feedback && (
        <div
          className={`p-4 rounded-lg border ${
            feedback.is_correct === true
              ? 'border-green-300 bg-green-50 dark:bg-green-900/20'
              : feedback.is_correct === false
              ? 'border-red-300 bg-red-50 dark:bg-red-900/20'
              : 'border-yellow-300 bg-yellow-50 dark:bg-yellow-900/20'
          }`}
        >
          <p className="font-medium">
            {feedback.is_correct === true ? '✅ 正确！' : feedback.is_correct === false ? '❌ 不对哦' : '📝 已记录'}
          </p>
          {feedback.explanation && <p className="text-sm mt-1 text-gray-600 dark:text-gray-400">{feedback.explanation}</p>}
        </div>
      )}
    </div>
  );
}

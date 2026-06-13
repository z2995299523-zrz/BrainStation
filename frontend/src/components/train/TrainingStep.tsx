import { useState } from 'react';
import { useTrainStore } from '../../stores/trainStore';
import QuestionCard from '../shared/QuestionCard';

export default function TrainingStep() {
  const sessionData = useTrainStore((s) => s.sessionData);
  const goToStep = useTrainStore((s) => s.goToStep);
  const submitAnswer = useTrainStore((s) => s.submitAnswer);
  const questions = sessionData?.steps.training.questions ?? [];
  const [currentIdx, setCurrentIdx] = useState(0);
  const [feedback, setFeedback] = useState<{ is_correct: boolean | null; explanation: string } | null>(null);

  if (questions.length === 0) {
    return (
      <div className="text-center py-12">
        <h2 className="text-xl font-bold mb-4">🎯 混合训练</h2>
        <p className="text-gray-500 mb-4">暂无训练题目。</p>
        <button onClick={() => goToStep(5)} className="px-6 py-2 bg-indigo-600 text-white rounded-lg">
          继续 →
        </button>
      </div>
    );
  }

  const question = questions[currentIdx];

  const handleAnswer = (answer: unknown) => {
    const qAnswer = (question as unknown as Record<string, unknown>).answer as Record<string, unknown> | undefined;
    const correct = qAnswer?.correct as number | string | undefined;
    let isCorrect: boolean | null = null;
    if (question.q_type === 'choice') {
      isCorrect = (answer as { choice: number }).choice === correct;
    } else if (question.q_type === 'fill') {
      isCorrect = String(answer).trim().toLowerCase() === String(correct).trim().toLowerCase();
    }
    setFeedback({ is_correct: isCorrect, explanation: (qAnswer?.explanation as string) || '' });
  };

  const handleNext = () => {
    if (currentIdx < questions.length - 1) {
      setCurrentIdx(currentIdx + 1);
      setFeedback(null);
    } else {
      goToStep(5);
    }
  };

  return (
    <div className="space-y-4">
      <h2 className="text-xl font-bold">🎯 混合训练</h2>
      <p className="text-sm text-gray-500">第 {currentIdx + 1}/{questions.length} 题</p>
      <QuestionCard
        question={question}
        onAnswer={handleAnswer}
        onConfidence={(c) => submitAnswer(question.id, { choice: 0 }, c, 'training')}
        showFeedback={feedback !== null}
        feedback={feedback}
      />
      {feedback && (
        <button onClick={handleNext} className="px-6 py-2 bg-indigo-600 text-white rounded-lg">
          {currentIdx < questions.length - 1 ? '下一题 →' : '进入下一步 →'}
        </button>
      )}
    </div>
  );
}

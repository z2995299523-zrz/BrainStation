import { useState } from 'react';
import { useTrainStore } from '../../stores/trainStore';

export default function FeynmanStep() {
  const sessionData = useTrainStore((s) => s.sessionData);
  const goToStep = useTrainStore((s) => s.goToStep);
  const explanation = useTrainStore((s) => s.feynmanExplanation);
  const setExplanation = useTrainStore((s) => s.setFeynmanExplanation);
  const deepChoice = useTrainStore((s) => s.feynmanDeepChoice);
  const setDeepChoice = useTrainStore((s) => s.setFeynmanDeepChoice);
  const deepAnswer = useTrainStore((s) => s.feynmanDeepAnswer);
  const setDeepAnswer = useTrainStore((s) => s.setFeynmanDeepAnswer);
  const result = useTrainStore((s) => s.feynmanResult);
  const submitFeynman = useTrainStore((s) => s.submitFeynman);
  const [submitted, setSubmitted] = useState(false);

  const feynman = sessionData?.steps.feynman;
  const deepQs = feynman?.deep_questions || [];

  const handleSubmit = async () => {
    await submitFeynman();
    setSubmitted(true);
  };

  const canSubmit = explanation.trim().length >= 5;

  return (
    <div className="space-y-4">
      <h2 className="text-xl font-bold">🗣️ 费曼输出</h2>

      {/* Base prompt */}
      {feynman?.base_prompt && (
        <div className="bg-white dark:bg-gray-900 rounded-xl p-6 border border-gray-200 dark:border-gray-800">
          <p className="text-gray-700 dark:text-gray-300">{feynman.base_prompt}</p>
        </div>
      )}

      {/* Explanation input */}
      <div>
        <label className="block text-sm font-medium text-gray-600 dark:text-gray-400 mb-2">
          用你自己的话解释（至少 20 字）：
        </label>
        <textarea
          value={explanation}
          onChange={(e) => setExplanation(e.target.value)}
          rows={5}
          placeholder="在这里写下你的理解..."
          className="w-full px-4 py-3 rounded-lg border border-gray-300 dark:border-gray-700 bg-white dark:bg-gray-800"
          disabled={submitted}
        />
        <p className="text-xs text-gray-400 mt-1">{explanation.length} 字</p>
      </div>

      {/* Deep questions */}
      {deepQs.length >= 2 && !submitted && (
        <div className="space-y-3">
          <p className="text-sm font-medium text-gray-600 dark:text-gray-400">选一个深问来回答：</p>
          <div className="flex gap-2">
            <button
              onClick={() => setDeepChoice('A')}
              className={`flex-1 p-3 rounded-lg border text-sm text-left transition-colors ${
                deepChoice === 'A'
                  ? 'border-indigo-500 bg-indigo-50 dark:bg-indigo-900/30'
                  : 'border-gray-200 dark:border-gray-700 hover:border-gray-300'
              }`}
            >
              <span className="font-medium">A.</span> {deepQs[0]}
            </button>
            <button
              onClick={() => setDeepChoice('B')}
              className={`flex-1 p-3 rounded-lg border text-sm text-left transition-colors ${
                deepChoice === 'B'
                  ? 'border-indigo-500 bg-indigo-50 dark:bg-indigo-900/30'
                  : 'border-gray-200 dark:border-gray-700 hover:border-gray-300'
              }`}
            >
              <span className="font-medium">B.</span> {deepQs[1]}
            </button>
          </div>
          {deepChoice && (
            <textarea
              value={deepAnswer}
              onChange={(e) => setDeepAnswer(e.target.value)}
              rows={2}
              placeholder="你的回答..."
              className="w-full px-4 py-3 rounded-lg border border-gray-300 dark:border-gray-700 bg-white dark:bg-gray-800"
            />
          )}
        </div>
      )}

      {/* Submit */}
      {!submitted && (
        <button
          onClick={handleSubmit}
          disabled={!canSubmit}
          className="px-6 py-2 bg-indigo-600 text-white rounded-lg hover:bg-indigo-700 disabled:opacity-50 disabled:cursor-not-allowed"
        >
          提交解释
        </button>
      )}

      {/* Feedback result */}
      {submitted && result && (
        <div
          className={`p-6 rounded-xl border-2 ${
            result.quality_flag === 'excellent'
              ? 'border-green-400 bg-green-50 dark:bg-green-900/20'
              : result.quality_flag === 'good'
              ? 'border-yellow-400 bg-yellow-50 dark:bg-yellow-900/20'
              : 'border-red-300 bg-red-50 dark:bg-red-900/20'
          }`}
        >
          <h3 className="font-bold text-lg mb-2">
            {result.quality_flag === 'excellent' ? '🌟 优秀' : result.quality_flag === 'good' ? '👍 不错' : '💪 再试试'}
          </h3>
          <p className="text-gray-700 dark:text-gray-300 whitespace-pre-wrap">{result.feedback}</p>
          {result.matched.length > 0 && (
            <p className="text-sm text-green-600 mt-2">✅ 涵盖了：{result.matched.join('、')}</p>
          )}
          {result.missing.length > 0 && (
            <p className="text-sm text-orange-600 mt-1">⚠️ 还可以提：{result.missing.join('、')}</p>
          )}

          <button onClick={() => goToStep(6)} className="mt-4 px-6 py-2 bg-indigo-600 text-white rounded-lg">
            继续 →
          </button>
        </div>
      )}
    </div>
  );
}

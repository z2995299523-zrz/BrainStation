import { useState } from 'react';
import { useTrainStore } from '../../stores/trainStore';
import { useNavigate } from 'react-router-dom';

export default function CalibrationStep() {
  const navigate = useNavigate();
  const sessionData = useTrainStore((s) => s.sessionData);
  const confidence = useTrainStore((s) => s.confidence);
  const setConfidence = useTrainStore((s) => s.setConfidence);
  const thoughtDiary = useTrainStore((s) => s.thoughtDiary);
  const setThoughtDiary = useTrainStore((s) => s.setThoughtDiary);
  const submitCalibration = useTrainStore((s) => s.submitCalibration);
  const completeSession = useTrainStore((s) => s.completeSession);
  const [submitted, setSubmitted] = useState(false);
  const [saving, setSaving] = useState(false);

  const handleSubmit = async () => {
    setSaving(true);
    await submitCalibration();
    await completeSession();
    setSaving(false);
    setSubmitted(true);
  };

  return (
    <div className="space-y-6">
      <h2 className="text-xl font-bold">📊 自我校准</h2>

      {!submitted ? (
        <>
          {/* Confidence */}
          <div className="bg-white dark:bg-gray-900 rounded-xl p-6 border border-gray-200 dark:border-gray-800 space-y-4">
            <p className="font-medium text-gray-700 dark:text-gray-300">
              {sessionData?.steps.calibration?.confidence_prompt || '今天学的内容你给自己打几分？（1-5）'}
            </p>
            <div className="flex gap-3 justify-center">
              {[1, 2, 3, 4, 5].map((level) => (
                <button
                  key={level}
                  onClick={() => setConfidence(level)}
                  className={`w-14 h-14 rounded-xl text-2xl font-bold transition-all ${
                    confidence >= level
                      ? 'bg-indigo-500 text-white scale-110 shadow-lg'
                      : 'bg-gray-100 dark:bg-gray-800 text-gray-400 hover:bg-gray-200'
                  }`}
                >
                  {level}
                </button>
              ))}
            </div>
          </div>

          {/* Thought diary */}
          <div className="bg-white dark:bg-gray-900 rounded-xl p-6 border border-gray-200 dark:border-gray-800 space-y-3">
            <p className="font-medium text-gray-700 dark:text-gray-300">
              {sessionData?.steps.calibration?.thought_card || '今天学到了什么？'}
            </p>
            <textarea
              value={thoughtDiary}
              onChange={(e) => setThoughtDiary(e.target.value)}
              rows={4}
              placeholder="写下你的思考..."
              className="w-full px-4 py-3 rounded-lg border border-gray-300 dark:border-gray-700 bg-white dark:bg-gray-800"
            />
          </div>

          <button
            onClick={handleSubmit}
            disabled={saving || confidence === 0}
            className="px-8 py-3 bg-indigo-600 text-white rounded-xl text-lg font-medium hover:bg-indigo-700 disabled:opacity-50 disabled:cursor-not-allowed transition-colors"
          >
            {saving ? '保存中...' : '✅ 完成训练'}
          </button>
        </>
      ) : (
        <div className="text-center space-y-6">
          <div className="text-6xl">🎉</div>
          <h3 className="text-2xl font-bold text-gray-800 dark:text-gray-200">今天训练完成！</h3>
          <p className="text-gray-500">你的努力正在改变大脑。</p>
          <button
            onClick={() => {
              navigate('/');
              window.location.reload();
            }}
            className="px-8 py-3 bg-indigo-600 text-white rounded-xl text-lg font-medium hover:bg-indigo-700 transition-colors"
          >
            返回首页
          </button>
        </div>
      )}
    </div>
  );
}

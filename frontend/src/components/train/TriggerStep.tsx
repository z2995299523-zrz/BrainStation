import { useTrainStore } from '../../stores/trainStore';
import SpeakButton from '../shared/SpeakButton';

interface SpokenPhrase {
  text: string;
  label: string;
}

export default function TriggerStep() {
  const sessionData = useTrainStore((s) => s.sessionData);
  const goToStep = useTrainStore((s) => s.goToStep);
  const trigger = sessionData?.steps.trigger;
  const spokenPhrases = (trigger?.content as Record<string, unknown> | null)?.spoken_phrases as SpokenPhrase[] | undefined;

  if (!trigger?.title) {
    return (
      <div className="text-center py-12">
        <h2 className="text-xl font-bold mb-4">💥 思考触发器</h2>
        <button onClick={() => goToStep(3)} className="px-6 py-2 bg-indigo-600 text-white rounded-lg">
          继续 →
        </button>
      </div>
    );
  }

  return (
    <div className="space-y-6">
      <h2 className="text-xl font-bold">💥 思考触发器</h2>
      <h3 className="text-lg font-semibold text-indigo-600">{trigger.title}</h3>
      <div className="bg-white dark:bg-gray-900 rounded-xl p-6 border border-gray-200 dark:border-gray-800">
        <div className="prose dark:prose-invert max-w-none whitespace-pre-wrap text-gray-700 dark:text-gray-300 leading-relaxed">
          {trigger.content?.text || ''}
        </div>
      </div>
      {trigger.content?.question && (
        <div className="bg-indigo-50 dark:bg-indigo-900/20 rounded-xl p-4 border border-indigo-200 dark:border-indigo-800">
          <p className="font-medium text-indigo-700 dark:text-indigo-300">
            💭 {trigger.content.question}
          </p>
        </div>
      )}
      {/* 语音示例 */}
      {spokenPhrases && spokenPhrases.length > 0 && (
        <div className="bg-white dark:bg-gray-900 rounded-xl p-4 border border-gray-200 dark:border-gray-800">
          <p className="text-sm font-medium text-gray-500 mb-3">🔈 点击发音，感受英语拼写的"不规则"</p>
          <div className="flex flex-wrap gap-3">
            {spokenPhrases.map((p, i) => (
              <div key={i} className="flex items-center gap-2 bg-gray-50 dark:bg-gray-800 rounded-lg px-3 py-2">
                <SpeakButton text={p.text} label={p.label} size="sm" />
                <div>
                  <span className="text-sm font-medium text-gray-800 dark:text-gray-200">{p.text}</span>
                  <span className="text-xs text-gray-400 ml-2">{p.label}</span>
                </div>
              </div>
            ))}
          </div>
        </div>
      )}
      <button onClick={() => goToStep(3)} className="px-6 py-2 bg-indigo-600 text-white rounded-lg">
        准备好了，开始学习 →
      </button>
    </div>
  );
}

import { useState } from 'react';
import { useTrainStore } from '../../stores/trainStore';
import SpeakButton from '../shared/SpeakButton';

interface PhonemeEntry {
  symbol: string;
  word: string;
  speak_word: string;
  speak_phoneme: string;
  word_ipa: string;
}

interface PhonemeGroup {
  title: string;
  phonemes: PhonemeEntry[];
}

export default function LearnStep() {
  const sessionData = useTrainStore((s) => s.sessionData);
  const goToStep = useTrainStore((s) => s.goToStep);
  const learn = sessionData?.steps.learn;
  const [tab, setTab] = useState<'operation' | 'understand' | 'connect'>('operation');

  if (!learn?.node_title) {
    return (
      <div className="text-center py-12">
        <h2 className="text-xl font-bold mb-4">📖 三层讲解</h2>
        <button onClick={() => goToStep(4)} className="px-6 py-2 bg-indigo-600 text-white rounded-lg">
          继续 →
        </button>
      </div>
    );
  }

  const tabs = [
    { key: 'operation' as const, label: '🧱 操作层', icon: '怎么用' },
    { key: 'understand' as const, label: '💡 理解层', icon: '为什么' },
    { key: 'connect' as const, label: '🌌 连接层', icon: '还有什么' },
  ];

  const currentContent = (learn as Record<string, unknown>)[tab] as Record<string, unknown> | undefined;
  const highlights = (currentContent?.highlights as string[]) || [];
  const thoughtSeeds = (currentContent?.thought_seeds as string[]) || [];

  // 解析英语口语示例
  interface SpokenExample { text: string; label: string; }
  const spokenExamples: SpokenExample[] = Array.isArray(currentContent?.spoken_examples)
    ? (currentContent!.spoken_examples as SpokenExample[])
    : [];

  // 解析词汇表（用于词汇节点）
  interface VocabWord { word: string; ipa: string; zh: string; speak: string; }
  interface VocabGroup { title: string; words: VocabWord[]; }
  const wordGroups: VocabGroup[] = Array.isArray(currentContent?.word_groups)
    ? (currentContent!.word_groups as VocabGroup[])
    : [];

  // 解析音素数据（用于音标节点）
  const rawPhonemes = (currentContent?.phonemes as Record<string, unknown>) || {};
  const phonemeGroups: PhonemeGroup[] = [];
  const groupLabels: Record<string, string> = {
    monophthongs: '单元音',
    diphthongs: '双元音',
    consonants_voiceless: '清辅音',
    consonants_voiced: '浊辅音',
    consonants_nasal: '鼻音 / 半元音',
  };
  for (const [key, entries] of Object.entries(rawPhonemes)) {
    if (Array.isArray(entries) && entries.length > 0) {
      phonemeGroups.push({
        title: groupLabels[key] || key,
        phonemes: entries as PhonemeEntry[],
      });
    }
  }

  return (
    <div className="space-y-4">
      <h2 className="text-xl font-bold">📖 三层讲解 — {learn.node_title}</h2>

      {/* Tab switcher */}
      <div className="flex gap-2 border-b border-gray-200 dark:border-gray-800">
        {tabs.map((t) => (
          <button
            key={t.key}
            onClick={() => setTab(t.key)}
            className={`px-4 py-2 text-sm font-medium border-b-2 transition-colors ${
              tab === t.key
                ? 'border-indigo-500 text-indigo-600'
                : 'border-transparent text-gray-500 hover:text-gray-700'
            }`}
          >
            {t.label} <span className="text-xs text-gray-400">({t.icon})</span>
          </button>
        ))}
      </div>

      {/* Content */}
      <div className="bg-white dark:bg-gray-900 rounded-xl p-6 border border-gray-200 dark:border-gray-800">
        <div className="prose dark:prose-invert max-w-none whitespace-pre-wrap text-gray-700 dark:text-gray-300 leading-relaxed">
          {(currentContent?.text as string) || ''}
        </div>
      </div>

      {/* Spoken examples — 英语例句发音 */}
      {spokenExamples.length > 0 && (
        <div className="bg-white dark:bg-gray-900 rounded-xl border border-gray-200 dark:border-gray-800 overflow-hidden">
          <div className="bg-emerald-50 dark:bg-emerald-900/30 px-4 py-2 border-b border-gray-200 dark:border-gray-800">
            <span className="text-sm font-semibold text-emerald-700 dark:text-emerald-300">🔈 例句发音</span>
          </div>
          <div className="p-3 flex flex-wrap gap-2">
            {spokenExamples.map((ex, i) => (
              <div key={i} className="flex items-center gap-2 bg-gray-50 dark:bg-gray-800 rounded-lg px-3 py-2">
                <SpeakButton text={ex.text} label={ex.label} size="sm" />
                <div className="flex flex-col">
                  <span className="text-sm font-medium text-gray-800 dark:text-gray-200">{ex.text}</span>
                  <span className="text-xs text-gray-400">{ex.label}</span>
                </div>
              </div>
            ))}
          </div>
        </div>
      )}

      {/* Word groups — 分类词汇表（用于词汇节点） */}
      {tab === 'operation' && wordGroups.length > 0 && (
        <div className="space-y-3">
          {wordGroups.map((group) => (
            <div key={group.title} className="bg-white dark:bg-gray-900 rounded-xl border border-gray-200 dark:border-gray-800 overflow-hidden">
              <div className="bg-sky-50 dark:bg-sky-900/30 px-4 py-2 border-b border-gray-200 dark:border-gray-800">
                <span className="text-sm font-semibold text-sky-700 dark:text-sky-300">{group.title}</span>
              </div>
              <div className="p-2 grid grid-cols-1 sm:grid-cols-2 gap-1">
                {group.words.map((w, i) => (
                  <div key={i} className="flex items-center gap-2 px-2 py-2 rounded-lg hover:bg-gray-50 dark:hover:bg-gray-800 transition-colors">
                    <SpeakButton text={w.speak} label={`发音: ${w.word}`} size="sm" variant="word" />
                    <span className="text-sm font-semibold text-gray-800 dark:text-gray-200">{w.word}</span>
                    <span className="text-xs font-mono text-amber-600 dark:text-amber-400">{w.ipa}</span>
                    <span className="text-xs text-gray-500 dark:text-gray-400 ml-auto">{w.zh}</span>
                  </div>
                ))}
              </div>
            </div>
          ))}
        </div>
      )}

      {/* Phoneme table — 音标交互式发音表 */}
      {tab === 'operation' && phonemeGroups.length > 0 && (
        <div className="space-y-4">
          {phonemeGroups.map((group) => (
            <div key={group.title} className="bg-white dark:bg-gray-900 rounded-xl border border-gray-200 dark:border-gray-800 overflow-hidden">
              <div className="bg-indigo-50 dark:bg-indigo-900/30 px-4 py-2 border-b border-gray-200 dark:border-gray-800">
                <span className="text-sm font-semibold text-indigo-700 dark:text-indigo-300">{group.title}</span>
              </div>
              <div className="p-2 grid grid-cols-1 sm:grid-cols-2 md:grid-cols-3 gap-1">
                {group.phonemes.map((p, i) => (
                  <div key={i} className="flex items-center gap-1.5 px-2 py-2 rounded-lg hover:bg-gray-50 dark:hover:bg-gray-800 transition-colors">
                    <SpeakButton text={p.speak_phoneme || p.speak_word} label={`音素: ${p.symbol}`} size="sm" variant="phoneme" />
                    <SpeakButton text={p.speak_word} label={`单词: ${p.word}`} size="sm" variant="word" />
                    <div className="min-w-0 flex-1">
                      <div className="flex items-baseline gap-1.5">
                        <span className="text-sm font-mono font-bold text-gray-800 dark:text-gray-200">{p.symbol}</span>
                        <span className="text-xs text-gray-500 dark:text-gray-400">{p.word}</span>
                      </div>
                      {p.word_ipa && (
                        <div className="text-xs font-mono text-amber-600 dark:text-amber-400 mt-0.5">
                          {p.word_ipa}
                        </div>
                      )}
                    </div>
                  </div>
                ))}
              </div>
            </div>
          ))}
        </div>
      )}

      {/* Highlights / Thought seeds */}
      {tab !== 'connect' && highlights.length > 0 && (
        <div className="bg-amber-50 dark:bg-amber-900/20 rounded-xl p-4 border border-amber-200 dark:border-amber-800">
          <p className="text-sm font-medium text-amber-700 mb-2">💡 核心要点</p>
          <ul className="list-disc list-inside space-y-1">
            {highlights.map((h, i) => (
              <li key={i} className="text-sm text-amber-800 dark:text-amber-300">{h}</li>
            ))}
          </ul>
        </div>
      )}

      {tab === 'connect' && thoughtSeeds.length > 0 && (
        <div className="bg-purple-50 dark:bg-purple-900/20 rounded-xl p-4 border border-purple-200 dark:border-purple-800">
          <p className="text-sm font-medium text-purple-700 mb-2">🌱 思考种子</p>
          <ul className="list-disc list-inside space-y-1">
            {thoughtSeeds.map((s, i) => (
              <li key={i} className="text-sm text-purple-800 dark:text-purple-300">{s}</li>
            ))}
          </ul>
        </div>
      )}

      <button onClick={() => goToStep(4)} className="px-6 py-2 bg-indigo-600 text-white rounded-lg">
        学完了，开始训练 →
      </button>
    </div>
  );
}

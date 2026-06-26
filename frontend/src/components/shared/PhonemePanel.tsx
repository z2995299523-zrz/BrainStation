import { useState } from 'react';
import SpeakButton from './SpeakButton';

interface PhonemeEntry {
  symbol: string;
  speak_phoneme: string;
  word: string;
  speak_word: string;
  word_ipa: string;
}

// Map IPA symbol to audio file slug
const SLUG_MAP: Record<string, string> = {
  '/iː/': 'ee', '/ɪ/': 'ih', '/e/': 'eh', '/æ/': 'ae', '/ʌ/': 'uh',
  '/ɑː/': 'ah', '/ɒ/': 'o', '/ɔː/': 'aw', '/ʊ/': 'oo', '/uː/': 'ooo',
  '/ɜː/': 'er', '/ə/': 'schwa',
  '/aɪ/': 'ai', '/eɪ/': 'ei', '/ɔɪ/': 'oi', '/aʊ/': 'au',
  '/əʊ/': 'ou', '/ɪə/': 'ia', '/eə/': 'ea', '/ʊə/': 'ua',
  '/p/': 'p', '/t/': 't', '/k/': 'k', '/f/': 'f', '/θ/': 'th',
  '/s/': 's', '/ʃ/': 'sh', '/tʃ/': 'ch', '/tr/': 'tr', '/ts/': 'ts', '/h/': 'h',
  '/b/': 'b', '/d/': 'd', '/g/': 'g', '/v/': 'v', '/ð/': 'dh',
  '/z/': 'z', '/ʒ/': 'zh', '/dʒ/': 'dzh', '/dr/': 'dr', '/dz/': 'dz', '/r/': 'r',
  '/m/': 'm', '/n/': 'n', '/ŋ/': 'ng', '/l/': 'l', '/w/': 'w', '/j/': 'y',
};

interface PhonemeGroup {
  title: string;
  phonemes: PhonemeEntry[];
}

// 48 个国际音标（IPA）完整数据
const PHONEME_GROUPS: PhonemeGroup[] = [
  {
    title: '单元音 Monophthongs',
    phonemes: [
      { symbol: '/iː/', speak_phoneme: 'ee-ee-ee', word: 'see',   speak_word: 'see',   word_ipa: '/siː/' },
      { symbol: '/ɪ/',  speak_phoneme: 'ih-ih-ih', word: 'sit',   speak_word: 'sit',   word_ipa: '/sɪt/' },
      { symbol: '/e/',  speak_phoneme: 'eh-eh-eh', word: 'bed',   speak_word: 'bed',   word_ipa: '/bed/' },
      { symbol: '/æ/',  speak_phoneme: 'a-a-a',    word: 'cat',   speak_word: 'cat',   word_ipa: '/kæt/' },
      { symbol: '/ʌ/',  speak_phoneme: 'uh-uh-uh', word: 'cup',   speak_word: 'cup',   word_ipa: '/kʌp/' },
      { symbol: '/ɑː/', speak_phoneme: 'ah-ah-ah', word: 'car',   speak_word: 'car',   word_ipa: '/kɑːr/' },
      { symbol: '/ɒ/',  speak_phoneme: 'o-o-o',    word: 'hot',   speak_word: 'hot',   word_ipa: '/hɒt/' },
      { symbol: '/ɔː/', speak_phoneme: 'aw-aw-aw', word: 'door',  speak_word: 'door',  word_ipa: '/dɔːr/' },
      { symbol: '/ʊ/',  speak_phoneme: 'oo-oo-oo', word: 'book',  speak_word: 'book',  word_ipa: '/bʊk/' },
      { symbol: '/uː/', speak_phoneme: 'ooo-ooo',  word: 'too',   speak_word: 'too',   word_ipa: '/tuː/' },
      { symbol: '/ɜː/', speak_phoneme: 'er-er-er', word: 'bird',  speak_word: 'bird',  word_ipa: '/bɜːrd/' },
      { symbol: '/ə/',  speak_phoneme: 'uh',       word: 'about', speak_word: 'about', word_ipa: '/əˈbaʊt/' },
    ],
  },
  {
    title: '双元音 Diphthongs',
    phonemes: [
      { symbol: '/aɪ/', speak_phoneme: 'eye-eye', word: 'my',   speak_word: 'my',   word_ipa: '/maɪ/' },
      { symbol: '/eɪ/', speak_phoneme: 'ay-ay',   word: 'day',  speak_word: 'day',  word_ipa: '/deɪ/' },
      { symbol: '/ɔɪ/', speak_phoneme: 'oy-oy',   word: 'boy',  speak_word: 'boy',  word_ipa: '/bɔɪ/' },
      { symbol: '/aʊ/', speak_phoneme: 'ow-ow',   word: 'now',  speak_word: 'now',  word_ipa: '/naʊ/' },
      { symbol: '/əʊ/', speak_phoneme: 'oh-oh',   word: 'go',   speak_word: 'go',   word_ipa: '/ɡəʊ/' },
      { symbol: '/ɪə/', speak_phoneme: 'ear-ear', word: 'here', speak_word: 'here', word_ipa: '/hɪər/' },
      { symbol: '/eə/', speak_phoneme: 'air-air', word: 'hair', speak_word: 'hair', word_ipa: '/heər/' },
      { symbol: '/ʊə/', speak_phoneme: 'oor-oor', word: 'tour', speak_word: 'tour', word_ipa: '/tʊər/' },
    ],
  },
  {
    title: '清辅音 Voiceless Consonants',
    phonemes: [
      { symbol: '/p/',  speak_phoneme: 'puh-puh-puh', word: 'pen',   speak_word: 'pen',   word_ipa: '/pen/' },
      { symbol: '/t/',  speak_phoneme: 'tuh-tuh-tuh', word: 'top',   speak_word: 'top',   word_ipa: '/tɒp/' },
      { symbol: '/k/',  speak_phoneme: 'kuh-kuh-kuh', word: 'cat',   speak_word: 'cat',   word_ipa: '/kæt/' },
      { symbol: '/f/',  speak_phoneme: 'fff-fff',     word: 'fish',  speak_word: 'fish',  word_ipa: '/fɪʃ/' },
      { symbol: '/θ/',  speak_phoneme: 'thhh-thhh',   word: 'think', speak_word: 'think', word_ipa: '/θɪŋk/' },
      { symbol: '/s/',  speak_phoneme: 'sss-sss',     word: 'sun',   speak_word: 'sun',   word_ipa: '/sʌn/' },
      { symbol: '/ʃ/',  speak_phoneme: 'shhh-shhh',   word: 'she',   speak_word: 'she',   word_ipa: '/ʃiː/' },
      { symbol: '/tʃ/', speak_phoneme: 'chuh-chuh',   word: 'chair', speak_word: 'chair', word_ipa: '/tʃeər/' },
      { symbol: '/tr/', speak_phoneme: 'truh-truh',   word: 'tree',  speak_word: 'tree',  word_ipa: '/triː/' },
      { symbol: '/ts/', speak_phoneme: 'ts-ts-ts',    word: 'cats',  speak_word: 'cats',  word_ipa: '/kæts/' },
      { symbol: '/h/',  speak_phoneme: 'huh-huh',     word: 'hat',   speak_word: 'hat',   word_ipa: '/hæt/' },
    ],
  },
  {
    title: '浊辅音 Voiced Consonants',
    phonemes: [
      { symbol: '/b/',  speak_phoneme: 'buh-buh-buh', word: 'book',  speak_word: 'book',  word_ipa: '/bʊk/' },
      { symbol: '/d/',  speak_phoneme: 'duh-duh-duh', word: 'dog',   speak_word: 'dog',   word_ipa: '/dɒɡ/' },
      { symbol: '/g/',  speak_phoneme: 'guh-guh-guh', word: 'go',    speak_word: 'go',    word_ipa: '/ɡəʊ/' },
      { symbol: '/v/',  speak_phoneme: 'vvv-vvv',     word: 'very',  speak_word: 'very',  word_ipa: '/ˈveri/' },
      { symbol: '/ð/',  speak_phoneme: 'thhh-voiced', word: 'this',  speak_word: 'this',  word_ipa: '/ðɪs/' },
      { symbol: '/z/',  speak_phoneme: 'zzz-zzz',     word: 'zoo',   speak_word: 'zoo',   word_ipa: '/zuː/' },
      { symbol: '/ʒ/',  speak_phoneme: 'zhhh-zhhh',   word: 'vision',speak_word: 'vision',word_ipa: '/ˈvɪʒən/' },
      { symbol: '/dʒ/', speak_phoneme: 'juh-juh',     word: 'jump',  speak_word: 'jump',  word_ipa: '/dʒʌmp/' },
      { symbol: '/dr/', speak_phoneme: 'druh-druh',   word: 'drive', speak_word: 'drive', word_ipa: '/draɪv/' },
      { symbol: '/dz/', speak_phoneme: 'dz-dz-dz',    word: 'beds',  speak_word: 'beds',  word_ipa: '/bedz/' },
      { symbol: '/r/',  speak_phoneme: 'rrr-rrr',     word: 'red',   speak_word: 'red',   word_ipa: '/red/' },
    ],
  },
  {
    title: '鼻音/半元音 Nasals & Glides',
    phonemes: [
      { symbol: '/m/', speak_phoneme: 'mmm-mmm', word: 'man',  speak_word: 'man',  word_ipa: '/mæn/' },
      { symbol: '/n/', speak_phoneme: 'nnn-nnn', word: 'no',   speak_word: 'no',   word_ipa: '/nəʊ/' },
      { symbol: '/ŋ/', speak_phoneme: 'ng-ng-ng',word: 'sing', speak_word: 'sing', word_ipa: '/sɪŋ/' },
      { symbol: '/l/', speak_phoneme: 'lll-lll', word: 'like', speak_word: 'like', word_ipa: '/laɪk/' },
      { symbol: '/w/', speak_phoneme: 'wuh-wuh', word: 'we',   speak_word: 'we',   word_ipa: '/wiː/' },
      { symbol: '/j/', speak_phoneme: 'yuh-yuh', word: 'yes',  speak_word: 'yes',  word_ipa: '/jes/' },
    ],
  },
];

export default function PhonemePanel() {
  const [open, setOpen] = useState(false);

  return (
    <>
      {/* 触发按钮 */}
      <button
        onClick={() => setOpen(true)}
        title="48 音标表"
        className="flex items-center gap-1 text-sm text-gray-500 hover:text-indigo-600 dark:text-gray-400 dark:hover:text-indigo-400 transition-colors font-mono font-bold"
      >
        <span className="hidden sm:inline">🔤</span>
        <span>音标</span>
      </button>

      {/* 遮罩层 + 侧边面板 */}
      {open && (
        <div className="fixed inset-0 z-[100]">
          {/* 背景遮罩 */}
          <div
            className="absolute inset-0 bg-black/40 backdrop-blur-sm"
            onClick={() => setOpen(false)}
          />
          {/* 侧边面板 */}
          <div className="absolute right-0 top-0 h-full w-full max-w-lg bg-white dark:bg-gray-900 shadow-2xl overflow-y-auto">
            {/* 头部 */}
            <div className="sticky top-0 z-10 bg-white dark:bg-gray-900 border-b border-gray-200 dark:border-gray-800 px-5 py-4 flex items-center justify-between">
              <div>
                <h2 className="text-lg font-bold text-gray-900 dark:text-gray-100">
                  🔤 国际音标参考表
                </h2>
                <p className="text-xs text-gray-500 mt-0.5">
                  48 个 IPA 音素 — 点击 🔊 听发音
                </p>
              </div>
              <button
                onClick={() => setOpen(false)}
                className="w-8 h-8 flex items-center justify-center rounded-full hover:bg-gray-100 dark:hover:bg-gray-800 text-gray-500 transition-colors"
              >
                ✕
              </button>
            </div>

            {/* 内容 */}
            <div className="px-5 py-4 space-y-4 pb-8">
              {PHONEME_GROUPS.map((group) => (
                <div
                  key={group.title}
                  className="bg-white dark:bg-gray-900 rounded-xl border border-gray-200 dark:border-gray-800 overflow-hidden"
                >
                  <div className="bg-indigo-50 dark:bg-indigo-900/30 px-4 py-2 border-b border-gray-200 dark:border-gray-800">
                    <span className="text-sm font-semibold text-indigo-700 dark:text-indigo-300">
                      {group.title}
                    </span>
                  </div>
                  <div className="p-2 grid grid-cols-1 sm:grid-cols-2 gap-0.5">
                    {group.phonemes.map((p, i) => (
                      <div
                        key={i}
                        className="flex items-center gap-1.5 px-2 py-2 rounded-lg hover:bg-gray-50 dark:hover:bg-gray-800 transition-colors"
                      >
                        <SpeakButton
                          audioSrc={`/audio/phonemes/${SLUG_MAP[p.symbol] || 'ee'}.mp3`}
                          label={`音素: ${p.symbol}`}
                          size="sm"
                          variant="phoneme"
                        />
                        <SpeakButton
                          audioSrc={`/audio/words/${SLUG_MAP[p.symbol] || 'ee'}.mp3`}
                          label={`单词: ${p.word}`}
                          size="sm"
                          variant="word"
                        />
                        <div className="min-w-0 flex-1">
                          <div className="flex items-baseline gap-1.5">
                            <span className="text-sm font-mono font-bold text-gray-800 dark:text-gray-200">
                              {p.symbol}
                            </span>
                            <span className="text-xs text-gray-500 dark:text-gray-400">
                              {p.word}
                            </span>
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
          </div>
        </div>
      )}
    </>
  );
}

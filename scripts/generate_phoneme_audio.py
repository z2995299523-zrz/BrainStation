"""Generate phoneme audio files using Edge TTS (free)."""
import asyncio
import io
import os
import sys
from pathlib import Path

# Fix Windows GBK encoding issue
if sys.platform == 'win32':
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')
    sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8', errors='replace')

# 48 个国际音标数据（与前端 PhonemePanel.tsx 保持一致）
PHONEME_GROUPS = [
    {
        "title": "单元音 Monophthongs",
        "phonemes": [
            {"slug": "ee", "symbol": "/iː/", "speak_phoneme": "ee", "speak_word": "see"},
            {"slug": "ih", "symbol": "/ɪ/", "speak_phoneme": "ih", "speak_word": "sit"},
            {"slug": "eh", "symbol": "/e/", "speak_phoneme": "eh", "speak_word": "bed"},
            {"slug": "ae", "symbol": "/æ/", "speak_phoneme": "a", "speak_word": "cat"},
            {"slug": "uh", "symbol": "/ʌ/", "speak_phoneme": "uh", "speak_word": "cup"},
            {"slug": "ah", "symbol": "/ɑː/", "speak_phoneme": "ah", "speak_word": "car"},
            {"slug": "o", "symbol": "/ɒ/", "speak_phoneme": "o", "speak_word": "hot"},
            {"slug": "aw", "symbol": "/ɔː/", "speak_phoneme": "aw", "speak_word": "door"},
            {"slug": "oo", "symbol": "/ʊ/", "speak_phoneme": "oo", "speak_word": "book"},
            {"slug": "ooo", "symbol": "/uː/", "speak_phoneme": "ooo", "speak_word": "too"},
            {"slug": "er", "symbol": "/ɜː/", "speak_phoneme": "er", "speak_word": "bird"},
            {"slug": "schwa", "symbol": "/ə/", "speak_phoneme": "uh", "speak_word": "about"},
        ],
    },
    {
        "title": "双元音 Diphthongs",
        "phonemes": [
            {"slug": "ai", "symbol": "/aɪ/", "speak_phoneme": "eye", "speak_word": "my"},
            {"slug": "ei", "symbol": "/eɪ/", "speak_phoneme": "ay", "speak_word": "day"},
            {"slug": "oi", "symbol": "/ɔɪ/", "speak_phoneme": "oy", "speak_word": "boy"},
            {"slug": "au", "symbol": "/aʊ/", "speak_phoneme": "ow", "speak_word": "now"},
            {"slug": "ou", "symbol": "/əʊ/", "speak_phoneme": "oh", "speak_word": "go"},
            {"slug": "ia", "symbol": "/ɪə/", "speak_phoneme": "ear", "speak_word": "here"},
            {"slug": "ea", "symbol": "/eə/", "speak_phoneme": "air", "speak_word": "hair"},
            {"slug": "ua", "symbol": "/ʊə/", "speak_phoneme": "oor", "speak_word": "tour"},
        ],
    },
    {
        "title": "清辅音 Voiceless Consonants",
        "phonemes": [
            {"slug": "p", "symbol": "/p/", "speak_phoneme": "p", "speak_word": "pen"},
            {"slug": "t", "symbol": "/t/", "speak_phoneme": "t", "speak_word": "top"},
            {"slug": "k", "symbol": "/k/", "speak_phoneme": "k", "speak_word": "cat"},
            {"slug": "f", "symbol": "/f/", "speak_phoneme": "f", "speak_word": "fish"},
            {"slug": "th", "symbol": "/θ/", "speak_phoneme": "th", "speak_word": "think"},
            {"slug": "s", "symbol": "/s/", "speak_phoneme": "s", "speak_word": "sun"},
            {"slug": "sh", "symbol": "/ʃ/", "speak_phoneme": "sh", "speak_word": "she"},
            {"slug": "ch", "symbol": "/tʃ/", "speak_phoneme": "ch", "speak_word": "chair"},
            {"slug": "tr", "symbol": "/tr/", "speak_phoneme": "tr", "speak_word": "tree"},
            {"slug": "ts", "symbol": "/ts/", "speak_phoneme": "ts", "speak_word": "cats"},
            {"slug": "h", "symbol": "/h/", "speak_phoneme": "h", "speak_word": "hat"},
        ],
    },
    {
        "title": "浊辅音 Voiced Consonants",
        "phonemes": [
            {"slug": "b", "symbol": "/b/", "speak_phoneme": "b", "speak_word": "book"},
            {"slug": "d", "symbol": "/d/", "speak_phoneme": "d", "speak_word": "dog"},
            {"slug": "g", "symbol": "/g/", "speak_phoneme": "g", "speak_word": "go"},
            {"slug": "v", "symbol": "/v/", "speak_phoneme": "v", "speak_word": "very"},
            {"slug": "dh", "symbol": "/ð/", "speak_phoneme": "the", "speak_word": "this"},
            {"slug": "z", "symbol": "/z/", "speak_phoneme": "z", "speak_word": "zoo"},
            {"slug": "zh", "symbol": "/ʒ/", "speak_phoneme": "zh", "speak_word": "vision"},
            {"slug": "dzh", "symbol": "/dʒ/", "speak_phoneme": "j", "speak_word": "jump"},
            {"slug": "dr", "symbol": "/dr/", "speak_phoneme": "dr", "speak_word": "drive"},
            {"slug": "dz", "symbol": "/dz/", "speak_phoneme": "dz", "speak_word": "beds"},
            {"slug": "r", "symbol": "/r/", "speak_phoneme": "r", "speak_word": "red"},
        ],
    },
    {
        "title": "鼻音/半元音 Nasals & Glides",
        "phonemes": [
            {"slug": "m", "symbol": "/m/", "speak_phoneme": "m", "speak_word": "man"},
            {"slug": "n", "symbol": "/n/", "speak_phoneme": "n", "speak_word": "no"},
            {"slug": "ng", "symbol": "/ŋ/", "speak_phoneme": "ng", "speak_word": "sing"},
            {"slug": "l", "symbol": "/l/", "speak_phoneme": "l", "speak_word": "like"},
            {"slug": "w", "symbol": "/w/", "speak_phoneme": "w", "speak_word": "we"},
            {"slug": "y", "symbol": "/j/", "speak_phoneme": "y", "speak_word": "yes"},
        ],
    },
]


async def generate_audio(text: str, filepath: str, voice: str = "en-US-AriaNeural"):
    """用 Edge TTS 生成单个音频文件"""
    import edge_tts
    communicate = edge_tts.Communicate(text, voice)
    await communicate.save(filepath)


async def main():
    ROOT = Path(__file__).parent.parent
    public_dir = ROOT / "frontend" / "public" / "audio"
    phoneme_dir = public_dir / "phonemes"
    word_dir = public_dir / "words"
    phoneme_dir.mkdir(parents=True, exist_ok=True)
    word_dir.mkdir(parents=True, exist_ok=True)

    # 使用 Microsoft 神经语音
    voice = "en-US-AriaNeural"

    total = 0
    skipped = 0

    for group in PHONEME_GROUPS:
        for p in group["phonemes"]:
            slug = p["slug"]
            symbol = p["symbol"]

            # 音素发音（用特殊提示词让 TTS 尽量发出准确的音素声音）
            phoneme_prompt = get_phoneme_prompt(slug, p["speak_phoneme"], symbol)

            phoneme_file = phoneme_dir / f"{slug}.mp3"
            word_file = word_dir / f"{slug}.mp3"

            if not phoneme_file.exists():
                print(f"[PHONEME] [{symbol}] generating: {p['speak_phoneme']}")
                await generate_audio(phoneme_prompt, str(phoneme_file), voice)
                total += 1
            else:
                print(f"[SKIP] [{symbol}] already exists")
                skipped += 1

            if not word_file.exists():
                print(f"[WORD]   [{symbol}] generating: {p['speak_word']}")
                await generate_audio(p["speak_word"], str(word_file), voice)
                total += 1
            else:
                skipped += 1

    print(f"\n=== DONE === Generated {total} files, skipped {skipped} existing")
    print(f"   Phonemes: {phoneme_dir} ({len(list(phoneme_dir.glob('*.mp3')))} files)")
    print(f"   Words:    {word_dir} ({len(list(word_dir.glob('*.mp3')))} files)")


def get_phoneme_prompt(slug: str, speak: str, symbol: str) -> str:
    """构建音素发音提示词，让 TTS 发出尽可能准确的音素声音"""
    # 不同音素类型用不同策略
    vowels = {"ee", "ih", "eh", "ae", "uh", "ah", "o", "aw", "oo", "ooo", "er", "schwa",
              "ai", "ei", "oi", "au", "ou", "ia", "ea", "ua"}
    voiceless = {"p", "t", "k", "f", "th", "s", "sh", "ch", "tr", "ts", "h"}
    voiced = {"b", "d", "g", "v", "dh", "z", "zh", "dzh", "dr", "dz", "r"}
    nasals = {"m", "n", "ng", "l", "w", "y"}

    if slug in vowels:
        # 元音：延长发音
        return f"Say the sound: {speak}"
    elif slug in voiceless:
        # 清辅音：短促发音
        return f"Say the consonant sound: {speak}"
    elif slug in voiced:
        # 浊辅音：带声带振动
        return f"Say the voiced consonant sound: {speak}"
    elif slug in nasals:
        return f"Say the sound: {speak}"
    else:
        return f"Pronounce the phoneme {symbol}"


if __name__ == "__main__":
    asyncio.run(main())

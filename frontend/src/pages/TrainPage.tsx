import { useEffect } from 'react';
import { useParams } from 'react-router-dom';
import { useTrainStore } from '../stores/trainStore';
import TrainWizard from '../components/train/TrainWizard';

export default function TrainPage() {
  const { subject } = useParams<{ subject: string }>();
  const fetchSession = useTrainStore((s) => s.fetchSession);
  const setSubject = useTrainStore((s) => s.setSubject);
  const loading = useTrainStore((s) => s.loading);
  const error = useTrainStore((s) => s.error);

  useEffect(() => {
    if (subject === 'math' || subject === 'english') {
      setSubject(subject);
    }
  }, [subject, setSubject]);

  useEffect(() => {
    if (subject === 'math' || subject === 'english') {
      fetchSession();
    }
  }, [subject, fetchSession]);

  if (!subject || (subject !== 'math' && subject !== 'english')) {
    return (
      <div className="text-center py-12">
        <p className="text-gray-500">请从首页选择训练科目</p>
      </div>
    );
  }

  const label = subject === 'math' ? '🧮 数学训练' : '📖 英语训练';
  const accentColor = subject === 'math' ? 'text-blue-600' : 'text-emerald-600';

  if (loading) {
    return (
      <div className="flex items-center justify-center min-h-[60vh]">
        <div className="flex flex-col items-center gap-3">
          <div className={`animate-spin rounded-full h-8 w-8 border-b-2 ${subject === 'math' ? 'border-blue-600' : 'border-emerald-600'}`} />
          <p className="text-gray-500">加载训练数据...</p>
        </div>
      </div>
    );
  }

  if (error) {
    return (
      <div className="text-center py-12">
        <p className="text-red-500 mb-4">加载失败: {error}</p>
        <button onClick={fetchSession} className={`px-4 py-2 text-white rounded-lg ${subject === 'math' ? 'bg-blue-600 hover:bg-blue-700' : 'bg-emerald-600 hover:bg-emerald-700'}`}>
          重试
        </button>
      </div>
    );
  }

  return (
    <div>
      <h1 className={`text-xl font-bold mb-6 text-center ${accentColor}`}>{label}</h1>
      <TrainWizard />
    </div>
  );
}

import { useTrainStore } from '../../stores/trainStore';
import WarmupStep from './WarmupStep';
import TriggerStep from './TriggerStep';
import LearnStep from './LearnStep';
import TrainingStep from './TrainingStep';
import FeynmanStep from './FeynmanStep';
import CalibrationStep from './CalibrationStep';

const STEP_NAMES: Record<number, string> = {
  1: '预热检索',
  2: '思考触发器',
  3: '三层讲解',
  4: '混合训练',
  5: '费曼输出',
  6: '自我校准',
};

export default function TrainWizard() {
  const currentStep = useTrainStore((s) => s.currentStep);
  const stepStatus = useTrainStore((s) => s.stepStatus);
  const subject = useTrainStore((s) => s.subject);
  const isMath = subject === 'math';
  const accentBg = isMath ? 'bg-blue-100 text-blue-700 dark:bg-blue-900 dark:text-blue-300' : 'bg-emerald-100 text-emerald-700 dark:bg-emerald-900 dark:text-emerald-300';

  return (
    <div className="max-w-3xl mx-auto">
      {/* Step indicator */}
      <div className="flex items-center justify-center gap-2 mb-8 flex-wrap">
        {[1, 2, 3, 4, 5, 6].map((step) => {
          const status = stepStatus[step];
          const isActive = step === currentStep;
          const emoji = status === 'completed' ? '✅' : isActive ? '📍' : '⏳';
          return (
            <div
              key={step}
              className={`flex items-center gap-1 px-3 py-1.5 rounded-full text-sm font-medium transition-colors ${
                isActive
                  ? accentBg
                  : status === 'completed'
                  ? 'bg-green-50 text-green-600 dark:bg-green-900 dark:text-green-300'
                  : 'bg-gray-100 text-gray-400 dark:bg-gray-800 dark:text-gray-500'
              }`}
            >
              <span>{emoji}</span>
              <span className="hidden sm:inline">{STEP_NAMES[step]}</span>
              <span className="sm:hidden">{step}</span>
            </div>
          );
        })}
      </div>

      {/* Step content */}
      {currentStep === 1 && <WarmupStep />}
      {currentStep === 2 && <TriggerStep />}
      {currentStep === 3 && <LearnStep />}
      {currentStep === 4 && <TrainingStep />}
      {currentStep === 5 && <FeynmanStep />}
      {currentStep === 6 && <CalibrationStep />}
    </div>
  );
}

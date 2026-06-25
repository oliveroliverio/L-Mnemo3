import { useState, useEffect } from 'react';
import { useSubmission } from './useSubmission';

export function useQuadrantTimer() {
  const { submitArtifact } = useSubmission();
  const [secondsRemaining, setSecondsRemaining] = useState<number>(0);

  const calculateNextQuadrant = () => {
    const now = new Date();
    const minutes = now.getMinutes();
    const nextQuadrantMinute = Math.ceil((minutes + 1) / 15) * 15;
    const nextQuadrantDate = new Date(now);
    nextQuadrantDate.setMinutes(nextQuadrantMinute, 0, 0);
    return Math.max(0, Math.floor((nextQuadrantDate.getTime() - now.getTime()) / 1000));
  };

  useEffect(() => {
    setSecondsRemaining(calculateNextQuadrant());

    const interval = setInterval(() => {
      setSecondsRemaining((prev) => {
        if (prev <= 1) {
          submitArtifact(false);
          return calculateNextQuadrant();
        }
        return prev - 1;
      });
    }, 1000);

    return () => clearInterval(interval);
  }, [submitArtifact]);

  const formatTime = (totalSeconds: number) => {
    const minutes = Math.floor(totalSeconds / 60);
    const seconds = totalSeconds % 60;
    return `${minutes.toString().padStart(2, '0')}:${seconds.toString().padStart(2, '0')}`;
  };

  return {
    timeDisplay: formatTime(secondsRemaining),
  };
}

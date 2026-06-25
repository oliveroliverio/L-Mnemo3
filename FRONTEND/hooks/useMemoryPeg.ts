import { useQuery } from '@tanstack/react-query';
import { useEffect } from 'react';
import { MemoryPegService } from '@/services/MemoryPegService';
import { useAppStore } from '@/store/useAppStore';
import { toast } from 'sonner';

export function useMemoryPeg() {
  const { setMemoryPeg, setIsMemoryPegConnected } = useAppStore();

  const { data, isError, error, isSuccess } = useQuery({
    queryKey: ['memoryPeg'],
    queryFn: MemoryPegService.getCharacters,
    refetchInterval: 60000, // Poll every 60 seconds
    retry: true,
  });

  useEffect(() => {
    if (isSuccess && data) {
      setMemoryPeg(data);
      setIsMemoryPegConnected(true);
    }
    
    if (isError) {
      setIsMemoryPegConnected(false);
      console.error('Failed to connect to Memory Peg API:', error);
    }
  }, [data, isSuccess, isError, error, setMemoryPeg, setIsMemoryPegConnected]);

  return { data, isError };
}

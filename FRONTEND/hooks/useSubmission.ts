import { useCallback } from 'react';
import { useAppStore } from '@/store/useAppStore';
import { SubmissionService } from '@/services/SubmissionService';
import { format } from 'date-fns';
import { toast } from 'sonner';
import { useQueryClient } from '@tanstack/react-query';

export function useSubmission() {
  const { draft, images, memoryPeg, clearWorkspace, setIsSubmitting } = useAppStore();
  const queryClient = useQueryClient();

  const submitArtifact = useCallback(async (isManual: boolean = false) => {
    if (!draft.trim() && images.length === 0) {
      if (isManual) toast.info('Nothing to submit.');
      return;
    }
    
    setIsSubmitting(true);
    
    try {
      const payload = {
        markdown: draft,
        images: images.map(img => img.base64).filter(Boolean) as string[],
        datetime: format(new Date(), "yyyy-MM-dd'T'HH:mm:ssxxx"),
        quadrant: memoryPeg?.timeCharacter?.peg || 'UNKNOWN',
        weekCharacter: memoryPeg?.weekCreature?.creature || 'UNKNOWN',
        timeCharacter: memoryPeg?.timeCharacter?.character || 'UNKNOWN',
        dayTheme: memoryPeg?.dayTheme?.theme || 'UNKNOWN',
        manual: isManual,
      };

      await SubmissionService.submitArtifact(payload);
      toast.success(isManual ? 'Manual submission successful' : 'Quadrant submission successful');
      clearWorkspace();
      if (!isManual) {
        queryClient.invalidateQueries({ queryKey: ['memoryPeg'] });
      }
    } catch (error) {
      toast.error('Submission failed. Draft preserved.');
    } finally {
      setIsSubmitting(false);
    }
  }, [draft, images, memoryPeg, clearWorkspace, setIsSubmitting, queryClient]);

  return { submitArtifact };
}

'use client';

import { useAppStore } from '@/store/useAppStore';
import { Button } from '@/components/ui/button';
import { Trash2, Send, Undo2, Redo2, Clock, Minus, ClipboardPaste, Settings } from 'lucide-react';
import { format } from 'date-fns';
import { toast } from 'sonner';
import { useSubmission } from '@/hooks/useSubmission';

export default function BottomToolbar() {
  const { draft, setDraft, clearWorkspace } = useAppStore();
  const { submitArtifact } = useSubmission();

  const handleInsertTimestamp = () => {
    const timestamp = format(new Date(), 'yyyy-MM-dd HH:mm:ss');
    setDraft(draft + (draft.length > 0 && !draft.endsWith('\n') ? '\n' : '') + `[${timestamp}] `);
  };

  const handleInsertDivider = () => {
    setDraft(draft + (draft.length > 0 && !draft.endsWith('\n') ? '\n' : '') + '\n---\n\n');
  };

  const handleClear = () => {
    if (confirm('Are you sure you want to clear the workspace? This cannot be undone.')) {
      clearWorkspace();
      toast.success('Workspace cleared');
    }
  };

  const handleSubmit = () => {
    submitArtifact(true);
  };

  return (
    <div className="h-14 border-t bg-background flex items-center justify-between px-4">
      <div className="flex items-center space-x-1">
        <Button variant="ghost" size="icon" onClick={() => {}} title="Undo">
          <Undo2 className="w-4 h-4" />
        </Button>
        <Button variant="ghost" size="icon" onClick={() => {}} title="Redo">
          <Redo2 className="w-4 h-4" />
        </Button>
        <div className="w-px h-6 bg-border mx-2" />
        <Button variant="ghost" size="icon" onClick={handleInsertTimestamp} title="Insert Timestamp">
          <Clock className="w-4 h-4" />
        </Button>
        <Button variant="ghost" size="icon" onClick={handleInsertDivider} title="Insert Divider">
          <Minus className="w-4 h-4" />
        </Button>
        <Button variant="ghost" size="icon" onClick={() => navigator.clipboard.readText().then(text => setDraft(draft + text))} title="Paste from Clipboard">
          <ClipboardPaste className="w-4 h-4" />
        </Button>
      </div>

      <div className="flex items-center space-x-2">
        <Button variant="ghost" size="icon" title="Settings">
          <Settings className="w-4 h-4" />
        </Button>
        <Button variant="ghost" className="text-red-500 hover:text-red-600 hover:bg-red-50 dark:hover:bg-red-950" onClick={handleClear}>
          <Trash2 className="w-4 h-4 mr-2" />
          Clear
        </Button>
        <Button onClick={handleSubmit} className="bg-blue-600 hover:bg-blue-700 text-white">
          <Send className="w-4 h-4 mr-2" />
          Submit Now
        </Button>
      </div>
    </div>
  );
}

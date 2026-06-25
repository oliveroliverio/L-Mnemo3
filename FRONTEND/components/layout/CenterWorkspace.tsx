'use client';

import { useAppStore } from '@/store/useAppStore';
import { useCallback, useRef } from 'react';
import BottomToolbar from './BottomToolbar';

export default function CenterWorkspace() {
  const { draft, setDraft, addImage } = useAppStore();
  const textareaRef = useRef<HTMLTextAreaElement>(null);

  const handlePaste = useCallback((e: React.ClipboardEvent) => {
    const items = e.clipboardData.items;
    for (let i = 0; i < items.length; i++) {
      if (items[i].type.indexOf('image') !== -1) {
        const file = items[i].getAsFile();
        if (file) handleImageFile(file);
      }
    }
  }, []);

  const handleDrop = useCallback((e: React.DragEvent) => {
    e.preventDefault();
    if (e.dataTransfer.files) {
      for (let i = 0; i < e.dataTransfer.files.length; i++) {
        const file = e.dataTransfer.files[i];
        if (file.type.startsWith('image/')) {
          handleImageFile(file);
        }
      }
    }
  }, []);

  const handleImageFile = (file: File) => {
    const reader = new FileReader();
    reader.onload = (e) => {
      if (typeof e.target?.result === 'string') {
        addImage({
          id: Math.random().toString(36).substr(2, 9),
          url: e.target.result,
          base64: e.target.result,
          name: file.name,
          type: file.type,
          size: file.size,
        });
      }
    };
    reader.readAsDataURL(file);
  };

  return (
    <main className="flex-1 flex flex-col h-full overflow-hidden bg-background">
      <div 
        className="flex-1 p-8 overflow-y-auto"
        onDrop={handleDrop}
        onDragOver={(e) => e.preventDefault()}
      >
        <textarea
          ref={textareaRef}
          value={draft}
          onChange={(e) => setDraft(e.target.value)}
          onPaste={handlePaste}
          placeholder="Start typing..."
          className="w-full h-full min-h-[500px] resize-none outline-none bg-transparent text-lg leading-relaxed placeholder:text-muted-foreground/50"
        />
      </div>
      <BottomToolbar />
    </main>
  );
}

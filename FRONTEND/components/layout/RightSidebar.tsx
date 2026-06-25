'use client';

import { useAppStore } from '@/store/useAppStore';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import { Button } from '@/components/ui/button';
import { X } from 'lucide-react';
import Image from 'next/image';

export default function RightSidebar() {
  const { draft, images, removeImage } = useAppStore();

  const charCount = draft.length;
  const wordCount = draft.trim().split(/\s+/).filter(w => w.length > 0).length;
  const tokenCount = Math.ceil(wordCount * 1.3); // Rough estimate
  const readingTime = Math.ceil(wordCount / 200); // Assuming 200 words per minute

  return (
    <aside className="w-80 border-l bg-muted/20 flex flex-col h-full overflow-y-auto">
      <div className="p-4 space-y-4">
        
        <Card>
          <CardHeader className="p-4 pb-2">
            <CardTitle className="text-sm">Statistics</CardTitle>
          </CardHeader>
          <CardContent className="p-4 pt-0 space-y-2 text-sm">
            <div className="flex justify-between">
              <span className="text-muted-foreground">Words</span>
              <span className="font-medium">{wordCount}</span>
            </div>
            <div className="flex justify-between">
              <span className="text-muted-foreground">Characters</span>
              <span className="font-medium">{charCount}</span>
            </div>
            <div className="flex justify-between">
              <span className="text-muted-foreground">Est. Tokens</span>
              <span className="font-medium">{tokenCount}</span>
            </div>
            <div className="flex justify-between">
              <span className="text-muted-foreground">Reading Time</span>
              <span className="font-medium">{readingTime} min</span>
            </div>
          </CardContent>
        </Card>

        <Card>
          <CardHeader className="p-4 pb-2 flex flex-row items-center justify-between">
            <CardTitle className="text-sm">Attached Images</CardTitle>
            <span className="text-xs text-muted-foreground">{images.length}</span>
          </CardHeader>
          <CardContent className="p-4 pt-0">
            {images.length === 0 ? (
              <p className="text-sm text-muted-foreground italic">No images attached</p>
            ) : (
              <div className="grid grid-cols-2 gap-2">
                {images.map((img) => (
                  <div key={img.id} className="relative group rounded-md overflow-hidden border">
                    <img 
                      src={img.url} 
                      alt={img.name} 
                      className="object-cover w-full h-24"
                    />
                    <button
                      onClick={() => removeImage(img.id)}
                      className="absolute top-1 right-1 bg-black/50 text-white rounded-full p-1 opacity-0 group-hover:opacity-100 transition-opacity hover:bg-red-500"
                    >
                      <X className="w-3 h-3" />
                    </button>
                  </div>
                ))}
              </div>
            )}
          </CardContent>
        </Card>

      </div>
    </aside>
  );
}

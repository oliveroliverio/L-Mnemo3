'use client';

import { useAppStore } from '@/store/useAppStore';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import { format } from 'date-fns';
import { useEffect, useState } from 'react';
import { useMemoryPeg } from '@/hooks/useMemoryPeg';
import { useQuadrantTimer } from '@/hooks/useQuadrantTimer';

export default function LeftSidebar() {
  const { memoryPeg, isMemoryPegConnected } = useAppStore();
  const [currentTime, setCurrentTime] = useState(new Date());
  
  useMemoryPeg(); // Initiates polling
  const { timeDisplay } = useQuadrantTimer(); // Initiates countdown and gets display string

  useEffect(() => {
    const timer = setInterval(() => setCurrentTime(new Date()), 1000);
    return () => clearInterval(timer);
  }, []);

  return (
    <aside className="w-64 border-r bg-muted/20 flex flex-col h-full overflow-y-auto">
      <div className="p-4 space-y-4">
        <div>
          <h2 className="text-xl font-bold tracking-tight">L-Mnemo3</h2>
          <p className="text-sm text-muted-foreground">{format(currentTime, 'PP p')}</p>
        </div>

        <Card>
          <CardHeader className="p-4 pb-2">
            <CardTitle className="text-sm">Memory Peg Status</CardTitle>
          </CardHeader>
          <CardContent className="p-4 pt-0 space-y-2">
            <div className="flex items-center space-x-2">
              <div className={`w-2 h-2 rounded-full ${isMemoryPegConnected ? 'bg-green-500' : 'bg-red-500'}`} />
              <span className="text-sm">{isMemoryPegConnected ? 'Connected' : 'Offline'}</span>
            </div>
          </CardContent>
        </Card>

        <Card>
          <CardHeader className="p-4 pb-2">
            <CardTitle className="text-sm">Current Location</CardTitle>
          </CardHeader>
          <CardContent className="p-4 pt-0 space-y-3">
            <div>
              <span className="text-xs text-muted-foreground uppercase tracking-wider">Day Theme</span>
              <p className="font-medium text-sm">{memoryPeg?.dayTheme || '...'}</p>
            </div>
            <div>
              <span className="text-xs text-muted-foreground uppercase tracking-wider">Week Creature</span>
              <p className="font-medium text-sm">{memoryPeg?.weekCharacter || '...'}</p>
            </div>
            <div>
              <span className="text-xs text-muted-foreground uppercase tracking-wider">Time Character</span>
              <p className="font-medium text-sm">{memoryPeg?.timeCharacter || '...'}</p>
            </div>
            <div>
              <span className="text-xs text-muted-foreground uppercase tracking-wider">Quadrant</span>
              <p className="font-medium text-sm">{memoryPeg?.quadrant || '...'}</p>
            </div>
          </CardContent>
        </Card>

        <Card>
          <CardHeader className="p-4 pb-2">
            <CardTitle className="text-sm">Next Submission</CardTitle>
          </CardHeader>
          <CardContent className="p-4 pt-0">
            <div className="text-2xl font-mono tracking-tighter">
              {timeDisplay}
            </div>
          </CardContent>
        </Card>
      </div>
    </aside>
  );
}

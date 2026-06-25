import { create } from 'zustand';
import { persist, createJSONStorage } from 'zustand/middleware';
import { ImageAttachment, MemoryPegMetadata } from '../types';

interface AppState {
  // Theme
  theme: 'dark' | 'light' | 'system';
  setTheme: (theme: 'dark' | 'light' | 'system') => void;

  // Editor Draft
  draft: string;
  setDraft: (draft: string) => void;

  // Images
  images: ImageAttachment[];
  setImages: (images: ImageAttachment[]) => void;
  addImage: (image: ImageAttachment) => void;
  removeImage: (id: string) => void;
  clearWorkspace: () => void;

  // Memory Peg Metadata
  memoryPeg: MemoryPegMetadata | null;
  setMemoryPeg: (metadata: MemoryPegMetadata | null) => void;

  // Status
  isMemoryPegConnected: boolean;
  setIsMemoryPegConnected: (status: boolean) => void;
  isSubmitting: boolean;
  setIsSubmitting: (status: boolean) => void;
}

export const useAppStore = create<AppState>()(
  persist(
    (set) => ({
      theme: 'system',
      setTheme: (theme) => set({ theme }),

      draft: '',
      setDraft: (draft) => set({ draft }),

      images: [],
      setImages: (images) => set({ images }),
      addImage: (image) => set((state) => ({ images: [...state.images, image] })),
      removeImage: (id) => set((state) => ({ images: state.images.filter((img) => img.id !== id) })),
      
      clearWorkspace: () => set({ draft: '', images: [] }),

      memoryPeg: null,
      setMemoryPeg: (metadata) => set({ memoryPeg: metadata }),

      isMemoryPegConnected: false,
      setIsMemoryPegConnected: (status) => set({ isMemoryPegConnected: status }),

      isSubmitting: false,
      setIsSubmitting: (status) => set({ isSubmitting: status }),
    }),
    {
      name: 'l-mnemo3-storage', // key in local storage
      storage: createJSONStorage(() => localStorage),
      partialize: (state) => ({ 
        draft: state.draft, 
        theme: state.theme,
        // We only persist images that have base64 data to avoid losing them
        images: state.images.filter(img => img.base64).map(img => ({ ...img, file: undefined, url: img.base64 }))
      }),
    }
  )
);

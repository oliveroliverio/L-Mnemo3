export interface MemoryPegMetadata {
  weekCreature: {
    week: number;
    weekFormatted: string;
    creature: string;
    creature_description: string;
    note: string;
  };
  dayTheme: {
    weekday: string;
    theme: string;
    props: string[];
    note: string;
  };
  timeCharacter: {
    peg: string;
    character: string;
    time: string;
    note: string;
  };
  computedTime: string;
  currentDate: string;
}

export interface ImageAttachment {
  id: string;
  url: string; // object URL for preview
  file?: File; // actual file object
  base64?: string; // for submission or persistence
  name: string;
  type: string;
  size: number;
}

export interface ArtifactPayload {
  markdown: string;
  images: string[]; // base64 strings
  datetime: string;
  quadrant: string;
  weekCharacter: string;
  timeCharacter: string;
  dayTheme: string;
  manual?: boolean;
}

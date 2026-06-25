import LeftSidebar from '@/components/layout/LeftSidebar';
import CenterWorkspace from '@/components/layout/CenterWorkspace';
import RightSidebar from '@/components/layout/RightSidebar';

export default function Home() {
  return (
    <div className="flex h-screen w-full overflow-hidden bg-background">
      <LeftSidebar />
      <CenterWorkspace />
      <RightSidebar />
    </div>
  );
}

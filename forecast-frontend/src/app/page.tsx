'use client';

import DataView from '@/components/DataView';
import SearchBar from '@/components/SearchBar';


export default function Home() {
  return (
    <main className="flex items-center justify-center px-8 py-16 flex-col gap-8">
      <div className='flex gap-2 flex-col items-center w-[32rem]'>
        <div className='text-xl'>Discover what it&apos;s like in...</div>
        <SearchBar />
      </div>

      <div>
        <DataView />
      </div>
    </main >
  );
}

'use client';

import DataView from '@/components/DataView';
import SearchBar from '@/components/SearchBar';
import { City } from '@/schema';
import { DateInput } from '@mantine/dates';
import { useState } from 'react';


export default function Home() {
  const [data, setData] = useState<City | null>(null);

  const [firstDate, setFirstDate] = useState<Date | null>(new Date(2000, 1, 1));
  const [secondDate, setSecondDate] = useState<Date | null>(new Date(2022, 1, 1));

  const dataChangeHandler = (newCity: City) => {
    setData(newCity);
  }

  return (
    <main className="flex items-center justify-center px-8 py-16 flex-col gap-8">
      <div className='flex gap-4 flex-col items-center w-[64rem]'>
        <div className='w-full'>
          <div className='text-2xl mb-2'>Discover what it&apos;s like in...</div>
          <div className='flex flex-col items-center gap-4'>
            <div className='flex w-full gap-2'>
              <SearchBar
                dataChangeHandler={dataChangeHandler}
              />
              <button className='bg-yellow-400 px-4 py-4 rounded-3xl text-black'>
                Refresh
              </button>

            </div>
            <div className='w-full items-center text-md font-semibold flex gap-4 flex-col'>
              <div>Select the dates</div>

              <div className='w-fill flex flex-row gap-4 items-center'>
                <DateInput
                  value={firstDate}
                  onChange={setFirstDate}
                  label="From date"
                  placeholder="The starting date..."
                />
                <DateInput
                  value={secondDate}
                  onChange={setSecondDate}
                  label="To date"
                  placeholder="The end date..."
                />
              </div>
            </div>
          </div>
        </div>
      </div>

      <div>
        <DataView
          dateRange={[firstDate, secondDate]}
          forCity={data}
        />
      </div>
    </main >
  );
}
